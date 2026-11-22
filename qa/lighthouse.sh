#!/usr/bin/env bash
# Lighthouse (mobile) on key pages against `pnpm preview`. Needs Chromium: CHROME_PATH=$(nix build nixpkgs#chromium --no-link --print-out-paths)/bin/chromium
set -euo pipefail
BASE="${1:-http://127.0.0.1:4321}"
OUT="$(cd "$(dirname "$0")" && pwd)/out"; mkdir -p "$OUT"
for pg in ${PAGES:-/ /projects /projects/nomadz-kicking /projects/drone-car /projects/pdm4ar /projects/stethoscope /about}; do
  n=$(echo "${pg#/}" | tr '/' '_'); n=${n:-home}
  pnpm dlx lighthouse@12 "$BASE$pg" --quiet --chrome-flags="--headless=new --no-sandbox" --form-factor=mobile \
    --output=json --output-path="$OUT/lh-$n.json" >/dev/null 2>&1 || echo "FAIL $pg"
  python3 - "$OUT/lh-$n.json" "$pg" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])); a = r['audits']
c = {k[:4]: round(v['score'] * 100) for k, v in r['categories'].items()}
print(f"{sys.argv[2]:32s} {c}  LCP {a['largest-contentful-paint']['displayValue']:>6}  CLS {a['cumulative-layout-shift']['displayValue']:>5}  TBT {a['total-blocking-time']['displayValue']:>6}  {a['total-byte-weight']['displayValue']}")
PY
done
