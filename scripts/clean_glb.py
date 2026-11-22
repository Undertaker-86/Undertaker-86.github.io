"""Post-process an OCCT-exported GLB for the web viewer.

- drops parts far from the main assembly (stray sub-assemblies placed off to the side in the CAD),
- rotates the vehicle so its long axis is horizontal (glTF is Y-up),
- merges the thousands of CAD parts into one mesh per colour (few draw calls).
Usage: python3 clean_glb.py in.glb out.glb [max_dist_m=0.6] [rot_x_deg=-90]
"""
import sys
from collections import defaultdict

import numpy as np
import trimesh

src, out = sys.argv[1], sys.argv[2]
max_d = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
rot = float(sys.argv[4]) if len(sys.argv) > 4 else -90.0
parts = trimesh.load(src).dump(concatenate=False)
cent = np.array([m.bounds.mean(0) for m in parts])
d = np.linalg.norm(cent - np.median(cent, 0), axis=1)
keep = [m for m, dd in zip(parts, d) if dd < max_d]
print(f"parts {len(parts)} kept {len(keep)} dropped {len(parts) - len(keep)}")

def colour(m):
    mat = getattr(m.visual, "material", None)
    c = getattr(mat, "baseColorFactor", None)
    if c is None and hasattr(m.visual, "face_colors"):
        c = m.visual.face_colors[0]
    c = np.asarray(c if c is not None else [180, 185, 190, 255], dtype=float)
    if c.max() <= 1.0:
        c = c * 255
    return tuple(int(round(v)) for v in c[:4])

groups = defaultdict(list)
for m in keep:
    groups[colour(m)].append(m)
R = trimesh.transformations.rotation_matrix(np.radians(rot), [1, 0, 0])
scene = trimesh.Scene()
for (r, g, b, a), ms in groups.items():
    merged = trimesh.util.concatenate([trimesh.Trimesh(vertices=m.vertices, faces=m.faces, process=False) for m in ms])
    merged.apply_transform(R)
    mat = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[r / 255, g / 255, b / 255, a / 255], metallicFactor=0.3, roughnessFactor=0.5,
        alphaMode="BLEND" if a < 250 else "OPAQUE", doubleSided=True)
    merged.visual = trimesh.visual.TextureVisuals(material=mat)
    scene.add_geometry(merged, geom_name=f"c{r}_{g}_{b}_{a}")
c = scene.bounds.mean(0)
scene.apply_translation(-c)
print("colours", len(groups), "extents", np.ptp(scene.bounds, 0).round(3), "faces", sum(len(g.faces) for g in scene.geometry.values()))
scene.export(out)
