"""Run PDM4AR ex14 configs with the official simulator and dump everything needed for custom renders.

Run inside the course image (code mounted read-only at /repo, output dir at /out):
  docker run --rm -v <exercise repo>:/repo:ro -v <this dir>:/tools:ro -v <out>:/out idscfrazz/pdm4ar2026:3.11-bullseye \
    bash -c 'PYTHONPATH=/repo/src python /tools/extract.py /repo/src/pdm4ar/exercises_def/ex14/config_1.yaml ...'
"""
import json
import logging
import sys
import time
from pathlib import Path

logging.disable(logging.CRITICAL)
from dg_commons.sim.simulator import Simulator  # noqa: E402
from pdm4ar.exercises_def.ex14.perf_metrics import ex14_metrics  # noqa: E402
from pdm4ar.exercises_def.ex14.utils_config import load_config, sim_context_from_config  # noqa: E402


def plain(v):
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    try:
        return float(v)
    except Exception:
        return str(v)


for path in sys.argv[1:]:
    cfg = load_config(path)
    ctx = sim_context_from_config(cfg)
    t0 = time.time()
    Simulator().run(ctx)
    wall = time.time() - t0
    m, pms = ex14_metrics(ctx)
    players = {}
    for name, log in ctx.log.items():
        st = log.states
        ts = [float(t) for t in st.timestamps]
        players[str(name)] = {
            "t": [round(t, 3) for t in ts],
            "x": [round(float(s.x), 4) for s in st.values],
            "y": [round(float(s.y), 4) for s in st.values],
            "psi": [round(float(s.psi), 4) for s in st.values],
            "color": cfg["agents"][name]["color"] if name in cfg["agents"] else None,
        }
    gm = ctx.shared_goals_manager
    goals = []
    for gid, g in gm.all_goals.items():
        d = {k: plain(v) for k, v in vars(g).items() if k != "polygon"}
        d["id"] = gid
        goals.append(d)
    out = {
        "config": Path(path).name,
        "boundary": cfg["boundary"],
        "obstacles": cfg.get("static_obstacles", []),
        "goals_cfg": cfg["shared_goals"],
        "cps_cfg": cfg["collection_points"],
        "players": players,
        "goal_events": goals,
        "score": m.reduce_to_score(),
        "metrics": {k: plain(v) for k, v in vars(m).items()},
        "collisions": len(ctx.collision_reports),
        "wall_s": wall,
    }
    Path("/out", Path(path).stem + ".json").write_text(json.dumps(out))
    print(Path(path).name, "score", round(out["score"], 2), "delivered", m.num_goals_delivered, "collisions", out["collisions"], flush=True)
