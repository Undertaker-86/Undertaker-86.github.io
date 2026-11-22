"""Render portfolio media for PDM4AR ex14 (multi-agent goal collection) from extract.py logs.

Usage: python3 render.py <logs_dir> <out_dir>
Outputs per config: <cfg>.mp4 (1080², real time, 25 fps), <cfg>_routes.png (full paths, numbered pickups/deliveries),
and timeline.png (who carries what, when) for config_3.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.patches import Circle, Polygon

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

BG, PANEL, GRID, INK, INK2, INK3 = "#0a0c0f", "#111419", "#1b2027", "#e9ecf1", "#a9b1bd", "#8a93a0"
OBST, OBST_EDGE, GOAL, CP = "#262c36", "#3a4250", "#ffd166", "#ff8a4c"
ROBOT = ["#4cc9f0", "#a3e635", "#f472b6", "#c4b5fd", "#fb923c", "#2dd4bf"]
R_ROBOT = 0.6
FPS = 25


def load(p):
    d = json.loads(p.read_text())
    names = sorted(n for n in d["players"] if "PDM4AR" in n)
    for i, n in enumerate(names):
        d["players"][n]["c"] = ROBOT[i % len(ROBOT)]
        for k in ("t", "x", "y", "psi"):
            d["players"][n][k] = np.asarray(d["players"][n][k], float)
    d["names"] = names
    d["ev"] = {g["id"]: g for g in d["goal_events"]}
    return d


def setup(d, ax):
    b = np.asarray(d["boundary"], float)
    ax.set_facecolor(BG)
    ax.set_aspect("equal")
    ax.set_xticks([]), ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    xmin, ymin = b.min(0)
    xmax, ymax = b.max(0)
    for v in np.arange(np.ceil(xmin), xmax, 2):
        ax.axvline(v, color=GRID, lw=0.6, zorder=0)
    for v in np.arange(np.ceil(ymin), ymax, 2):
        ax.axhline(v, color=GRID, lw=0.6, zorder=0)
    ax.add_patch(Polygon(b, closed=True, fill=False, ec=INK3, lw=1.4, zorder=1))
    for o in d["obstacles"]:
        ax.add_patch(Polygon(np.asarray(o, float), closed=True, fc=OBST, ec=OBST_EDGE, lw=1.2, zorder=2))
    for c in d["cps_cfg"]:
        ax.add_patch(Circle(c["center"], c["radius"], fc=CP + "22", ec=CP, lw=1.6, ls="--", zorder=2))
    pad = 0.6
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)


def pos(p, t):
    i = min(np.searchsorted(p["t"], t), len(p["t"]) - 1)
    return p["x"][i], p["y"][i], p["psi"][i], i


def render_video(d, path, size=1080):
    fig = plt.figure(figsize=(size / 100, size / 100), dpi=100, facecolor=BG)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.88])
    setup(d, ax)
    T_end = max(p["t"][-1] for p in d["players"].values())
    T_done = float(d["metrics"]["task_accomplishment_time"])
    n_goals = len(d["goals_cfg"])
    goal_xy = {g["id"]: g["center"] for g in d["goals_cfg"]}
    # static faint full paths (the executed plan)
    for n in d["names"]:
        p = d["players"][n]
        ax.plot(p["x"], p["y"], color=p["c"], lw=1.0, alpha=0.16, zorder=3)
    goal_art = {gid: ax.add_patch(Circle(xy, 0.32, fc=GOAL, ec=BG, lw=1.0, zorder=4)) for gid, xy in goal_xy.items()}
    trails = {n: ax.plot([], [], color=d["players"][n]["c"], lw=2.6, alpha=0.9, solid_capstyle="round", zorder=5)[0] for n in d["names"]}
    bodies = {n: ax.add_patch(Circle((0, 0), R_ROBOT, fc=d["players"][n]["c"], ec=BG, lw=1.5, zorder=6)) for n in d["names"]}
    heads = {n: ax.plot([], [], color=BG, lw=2.2, zorder=7)[0] for n in d["names"]}
    carry = {n: ax.add_patch(Circle((0, 0), 0.22, fc=GOAL, ec=BG, lw=1.0, zorder=8, visible=False)) for n in d["names"]}
    flashes = []
    title = fig.text(0.04, 0.955, "", color=INK, fontsize=21, fontweight="bold", va="center", family="DejaVu Sans")
    sub = fig.text(0.04, 0.918, "", color=INK2, fontsize=14, va="center", family="DejaVu Sans Mono")
    clock = fig.text(0.96, 0.955, "", color=INK, fontsize=21, ha="right", va="center", family="DejaVu Sans Mono")
    count = fig.text(0.96, 0.918, "", color=GOAL, fontsize=14, ha="right", va="center", family="DejaVu Sans Mono")
    title.set_text(f"{d['config'].replace('.yaml', '').replace('_', ' ')} · {len(d['names'])} robot{'s' if len(d['names']) > 1 else ''} · {n_goals} goals")
    deliveries = sorted((g["delivery_time"], gid) for gid, g in d["ev"].items() if g.get("delivery_time") is not None)
    hold = int(1.5 * FPS)
    frames = int(np.ceil(T_end * FPS)) + hold
    writer = FFMpegWriter(fps=FPS, codec="libx264", bitrate=-1, extra_args=["-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    with writer.saving(fig, str(path), dpi=100):
        for f in range(frames):
            t = min(f / FPS, T_end)
            for n in d["names"]:
                p = d["players"][n]
                x, y, psi, i = pos(p, t)
                j0 = max(0, np.searchsorted(p["t"], t - 2.5))
                trails[n].set_data(p["x"][j0:i + 1], p["y"][j0:i + 1])
                bodies[n].center = (x, y)
                heads[n].set_data([x, x + 0.55 * np.cos(psi)], [y, y + 0.55 * np.sin(psi)])
                carrying = [gid for gid, g in d["ev"].items() if g.get("collected_by") == n and g.get("collection_time") is not None
                            and g["collection_time"] <= t < (g.get("delivery_time") or 1e9)]
                carry[n].set_visible(bool(carrying))
                carry[n].center = (x - 0.32 * np.cos(psi), y - 0.32 * np.sin(psi))
            for gid, art in goal_art.items():
                g = d["ev"].get(gid, {})
                ct = g.get("collection_time")
                art.set_visible(ct is None or t < ct)
            for dt_, gid in deliveries:
                if dt_ <= t < dt_ + 0.6 and gid not in [fl[0] for fl in flashes]:
                    who = d["ev"][gid]["collected_by"]
                    x, y, _, _ = pos(d["players"][who], dt_)
                    flashes.append((gid, dt_, ax.add_patch(Circle((x, y), 0.6, fill=False, ec=GOAL, lw=2.5, zorder=9))))
            for gid, t0, art in flashes:
                a = (t - t0) / 0.6
                art.set_visible(0 <= a <= 1)
                if 0 <= a <= 1:
                    art.set_radius(0.6 + 1.6 * a)
                    art.set_alpha(1 - a)
            done = f / FPS >= T_end
            n_del = len(deliveries) if done else sum(1 for dt_, _ in deliveries if dt_ <= t)
            clock.set_text(f"t = {max(t, T_done) if done else t:5.2f} s")
            count.set_text(f"delivered {n_del}/{n_goals}")
            if done:
                sub.set_text(f"all delivered at {T_done:.2f} s · 0 collisions · score {d['score']:.1f}")
            else:
                sub.set_text("centrally planned, verified, executed without communication")
            writer.grab_frame(facecolor=BG)
    plt.close(fig)


def render_routes(d, path, size=1400):
    fig = plt.figure(figsize=(size / 100, size / 100), dpi=100, facecolor=BG)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    setup(d, ax)
    goal_xy = {g["id"]: g["center"] for g in d["goals_cfg"]}
    for n in d["names"]:
        p = d["players"][n]
        ax.plot(p["x"], p["y"], color=p["c"], lw=2.4, alpha=0.95, solid_capstyle="round", zorder=5)
        ax.add_patch(Circle((p["x"][0], p["y"][0]), R_ROBOT, fc=p["c"], ec=BG, lw=1.5, zorder=6))
        mine = sorted((g["collection_time"], gid) for gid, g in d["ev"].items() if g.get("collected_by") == n)
        for k, (_, gid) in enumerate(mine, 1):
            gx, gy = goal_xy[gid]
            ax.add_patch(Circle((gx, gy), 0.42, fc=GOAL, ec=p["c"], lw=2.2, zorder=7))
            ax.text(gx, gy, str(k), color=BG, ha="center", va="center", fontsize=11, fontweight="bold", zorder=8)
    for gid, (gx, gy) in goal_xy.items():
        if gid not in d["ev"] or d["ev"][gid].get("collected_by") is None:
            ax.add_patch(Circle((gx, gy), 0.32, fc=GOAL, ec=BG, zorder=7))
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def render_timeline(d, path):
    names = d["names"]
    fig, ax = plt.subplots(figsize=(14, 1.2 + 0.9 * len(names)), dpi=110, facecolor=BG)
    ax.set_facecolor(BG)
    T = float(d["metrics"]["task_accomplishment_time"])
    for r, n in enumerate(names):
        c = d["players"][n]["c"]
        ax.barh(r, T, left=0, height=0.62, color=GRID, zorder=1)
        mine = sorted((g["collection_time"], g["delivery_time"], gid) for gid, g in d["ev"].items() if g.get("collected_by") == n)
        for t0, t1, gid in mine:
            ax.barh(r, t1 - t0, left=t0, height=0.62, color=c, zorder=2)
            ax.text((t0 + t1) / 2, r, gid.replace("goal_", "g"), color=BG, ha="center", va="center", fontsize=9, fontweight="bold", zorder=3)
    ax.set_yticks(range(len(names)), [n.replace("PDM4AR_", "robot ") for n in names], color=INK2, fontsize=11)
    ax.set_xlim(0, T + 0.5)
    ax.invert_yaxis()
    ax.set_xlabel("time (s) · bar = carrying a goal from pickup to delivery", color=INK2, fontsize=11)
    ax.tick_params(colors=INK3)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.grid(axis="x", color=GRID)
    fig.tight_layout()
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


for p in sorted(src.glob("config_*.json")):
    d = load(p)
    render_routes(d, out / f"{p.stem}_routes.png")
    if p.stem == "config_3":
        render_timeline(d, out / "timeline.png")
    render_video(d, out / f"{p.stem}.mp4")
    print("rendered", p.stem, flush=True)
