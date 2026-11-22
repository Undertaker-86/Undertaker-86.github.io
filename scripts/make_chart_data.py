"""Turn small raw-data samples into compact JSON series for theme-aware SVG charts on the site.

Usage: python3 -I make_chart_data.py <repo_root> <out_dir>
Only reads two explicit inputs (one stethoscope SD log, the Stoeber valve output CSVs). No raw data is copied.
"""
import csv
import json
import struct
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, find_peaks, sosfiltfilt, welch

repo, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)


def r(x, n=4):
    return [round(float(v), n) for v in x]


# ---------------------------------------------------------------- stethoscope
def decode_log(path):
    """Same format as the SimPL post-processing notebook: 1024-byte blocks = 510 uint16 + uint32 ms timestamp."""
    data = path.read_bytes()
    ts, vals = [], []
    for i in range(0, len(data) - 1023, 1024):
        b = data[i : i + 1024]
        ts.append(struct.unpack_from("<I", b, 1020)[0])
        vals.extend(struct.unpack_from("<510H", b, 0))
    ts = np.array(ts, float) / 1000
    vals = np.asarray(vals, float)
    if ts[0] > ts[1]:  # the logger counts down; the notebook reverses the record in that case
        vals = vals[::-1]
    fs = 510 / abs(np.median(np.diff(ts)))
    return vals, fs


log = repo / "portfolio/Stethoscope_Capstone_2025/Sample_Data/Log1"
if log.is_file():
    x, fs = decode_log(log)
    x = x - x.mean()
    sos = butter(5, [20, 150], "bandpass", fs=fs, output="sos")  # notebook: 5 poles, 20-150 Hz, zero-phase
    y = sosfiltfilt(sos, x)
    a, b = int(5 * fs), int(11 * fs)  # skip the start-up transient, show 6 s
    seg_x, seg_y = x[a:b], y[a:b]
    step = max(1, len(seg_x) // 900)
    t = np.arange(len(seg_x)) / fs
    # envelope peaks for beat markers (display only)
    env = np.abs(seg_y)
    env = np.convolve(env, np.ones(int(0.05 * fs)) / int(0.05 * fs), "same")
    pk, _ = find_peaks(env, distance=int(0.3 * fs), prominence=env.std())
    f, p_raw = welch(x[a:], fs, nperseg=4096)
    _, p_flt = welch(y[a:], fs, nperseg=4096)
    keep = f <= 400
    json.dump(
        {
            "fs": round(fs, 1),
            "t": r(t[::step], 3),
            "raw": r(seg_x[::step] / np.abs(seg_x).max(), 3),
            "filtered": r(seg_y[::step] / np.abs(seg_y).max(), 3),
            "peaks": r(t[pk], 3),
            "psd_f": r(f[keep], 1),
            "psd_raw_db": r(10 * np.log10(p_raw[keep] + 1e-12), 2),
            "psd_filtered_db": r(10 * np.log10(p_flt[keep] + 1e-12), 2),
        },
        open(out / "stethoscope.json", "w"),
    )
    print(f"stethoscope.json  fs={fs:.0f} Hz  samples={len(x)}")
else:
    print("MISSING", log)

# ---------------------------------------------------------------- Stoeber valve
mo = repo / "portfolio/porous_material/mems_exp/output"
res = mo / "resistance_vs_strain.csv"
if res.is_file():
    rows = list(csv.DictReader(open(res)))
    strain = [float(r_["strain"]) for r_ in rows]
    R = [float(r_["hydraulic_resistance (Pa s/m^3)"]) for r_ in rows]
    curves = {}
    for mm in ["0.50", "2.00", "4.00", "6.00", "8.00"]:
        fpath = mo / f"{mm}mm-strain_d-sample_averaged_by_target_pressure.csv"
        if not fpath.is_file():
            continue
        pts = [
            (float(q["pressure_diff_mbar"]), float(q["FlowSensor(Read)[µl/min]"]))
            for q in csv.DictReader(open(fpath))
            if float(q["target_pressure"]) > 0
        ]
        pts.sort()
        curves[mm] = {"p_mbar": r([p for p, _ in pts], 3), "q_ul_min": r([q for _, q in pts], 2)}
    json.dump(
        {"strain": r(strain, 4), "resistance_GPa_s_per_m3": r(np.array(R) / 1e9, 3), "curves": curves},
        open(out / "stoeber.json", "w"),
    )
    print(f"stoeber.json  {len(strain)} strain points, {len(curves)} flow curves")
else:
    print("MISSING", res)
