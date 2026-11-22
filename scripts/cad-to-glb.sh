#!/usr/bin/env bash
# STEP assembly → web GLB for the CadViewer component (OpenCASCADE tessellation keeps the CAD colours).
# Usage: bash scripts/cad-to-glb.sh "<in.step>" public/media/<slug>/<name>.glb
set -euo pipefail
IN="$1"; OUT="$2"; T=$(mktemp -d); HERE="$(cd "$(dirname "$0")" && pwd)"
OCCT=$(nix build nixpkgs#opencascade-occt --no-link --print-out-paths)
GLTFPACK=$(nix build nixpkgs#meshoptimizer.bin --no-link --print-out-paths)/bin/gltfpack
cp "$IN" "$T/in.step"
cat > "$T/conv.tcl" <<'TCL'
pload ALL
ReadStep D in.step
XGetOneShape s D
incmesh s 3 -a 25 -parallel
WriteGltf D raw.glb
exit
TCL
(cd "$T" && LD_LIBRARY_PATH="$OCCT/lib" CASROOT="$OCCT" "$OCCT/bin/DRAWEXE" -b -f conv.tcl >/dev/null)
(cd "$T" && nix-shell -p 'python3.withPackages(p: [p.trimesh p.numpy p.scipy p.networkx])' --run "python3 $HERE/clean_glb.py raw.glb clean.glb 0.6 -90")
mkdir -p "$(dirname "$OUT")"
"$GLTFPACK" -i "$T/clean.glb" -o "$OUT" -si 0.5   # quantised (KHR_mesh_quantization), no decoder needed
du -h "$OUT"
