"""Render card/hero covers for projects without photos, from the same chart data the pages plot.

Usage: python3 -I make_covers.py <site_root>
Writes src/assets/{stethoscope,stoeber-porous-valve,ecs-haptic-wheel}/cover.png and src/data/charts/ecs.json.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

site = Path(sys.argv[1])
charts = site / "src/data/charts"
BG, GRID, MUTED, ACC, INK = "#0a0c0f", "#1b2027", "#5c6672", "#ff8a4c", "#e9ecf1"


def fig():
    f, ax = plt.subplots(figsize=(16, 10), dpi=100)
    f.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=15, length=0)
    ax.grid(color=GRID, lw=1)
    return f, ax


def save(f, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    f.tight_layout(pad=2.2)
    f.savefig(out, facecolor=BG)
    plt.close(f)
    print("cover", out.relative_to(site))


# ---- stethoscope: raw vs filtered heart sound
d = json.load(open(charts / "stethoscope.json"))
f, ax = fig()
t = np.array(d["t"])
ax.plot(t, np.array(d["raw"]) * 0.9 + 1.25, color=MUTED, lw=1.2)
ax.plot(t, np.array(d["filtered"]) * 0.9 - 0.9, color=ACC, lw=2)
ax.text(0.05, 2.25, "raw microphone", color=MUTED, fontsize=20, family="monospace")
ax.text(0.05, 0.12, "20–150 Hz band-pass", color=ACC, fontsize=20, family="monospace")
ax.set_xlim(0, 6)
ax.set_ylim(-2, 2.5)
ax.set_yticks([])
ax.set_xlabel("time (s)", color=MUTED, fontsize=16)
save(f, site / "src/assets/stethoscope/cover.png")

# ---- Stoeber: flow vs pressure at increasing compression
d = json.load(open(charts / "stoeber.json"))
f, ax = fig()
keys = list(d["curves"].keys())
for i, k in enumerate(keys):
    c = d["curves"][k]
    a = 0.35 + 0.65 * (i / max(1, len(keys) - 1))
    col = ACC if i == len(keys) - 1 else MUTED
    ax.plot(c["p_mbar"], c["q_ul_min"], color=ACC, alpha=a, lw=2.4, marker="o", ms=7)
    ax.text(c["p_mbar"][-1] + 0.25, c["q_ul_min"][-1], f"{float(k):.1f} mm", color=INK, alpha=a, fontsize=15, va="center")
ax.set_xlabel("pressure drop (mbar)", color=MUTED, fontsize=16)
ax.set_ylabel("flow rate (µl/min)", color=MUTED, fontsize=16)
save(f, site / "src/assets/stoeber-porous-valve/cover.png")

# ---- ECS: torque–angle laws of the virtual worlds (constants from src/lib/worlds.c, src/lab6/lab6.c)
ang = np.linspace(-90, 90, 721)
spring = -50.0 * ang  # virtualSpring, k = 50
wall = np.where(ang < 0, -500.0 * ang, 0.0)  # virtualWall, k = 500 at 0°
rel = np.mod(ang, 45.0)
rel = np.where(rel > 22.5, rel - 45.0, rel)
detent = -250.0 * np.sin(rel / 45.0 * np.pi)  # virtualKnobDetents: 45° spacing, 250 peak
json.dump(
    {"angle": [round(float(v), 2) for v in ang[::4]],
     "spring": [round(float(v), 1) for v in spring[::4]],
     "wall": [round(float(v), 1) for v in wall[::4]],
     "detent": [round(float(v), 1) for v in detent[::4]]},
    open(charts / "ecs.json", "w"),
)
f, ax = fig()
ax.plot(ang, np.clip(wall, -4600, 4600), color=MUTED, lw=2)
ax.plot(ang, spring, color=MUTED, lw=2, ls="--")
ax.plot(ang, detent * 8, color=ACC, lw=3)
ax.text(-88, 4200, "virtual wall", color=MUTED, fontsize=18, family="monospace")
ax.text(40, -3200, "spring", color=MUTED, fontsize=18, family="monospace")
ax.text(-88, -2400, "45° detents", color=ACC, fontsize=18, family="monospace")
ax.set_ylim(-4800, 4800)
ax.set_yticks([])
ax.set_xlabel("wheel angle (°)", color=MUTED, fontsize=16)
save(f, site / "src/assets/ecs-haptic-wheel/cover.png")
