#!/usr/bin/env bash
# Screenshot QA with system Firefox (headless): 320/390/768/1440 px, light + dark, reduced motion.
# Usage: bash qa/screens.sh [base_url]   (run `pnpm preview` first)
set -euo pipefail
BASE="${1:-http://127.0.0.1:4321}"
OUT="$(cd "$(dirname "$0")" && pwd)/out"; mkdir -p "$OUT"
P=$(mktemp -d); printf 'user_pref("ui.prefersReducedMotion", 1);\n' > "$P/user.js"
pages=("/" "/projects" "/projects/nomadz-kicking" "/projects/drone-car" "/projects/stethoscope" "/about")
for w in 320 390 768 1440; do
  h=$(( w < 800 ? 5200 : 4200 ))
  for theme in dark light; do
    for pg in "${pages[@]}"; do
      name=$(echo "${pg#/}" | tr '/' '_'); name=${name:-home}
      timeout 60 firefox --headless --profile "$P" --no-remote --window-size="$w,$h" \
        --screenshot "$OUT/${name}-${w}-${theme}.png" "$BASE$pg?theme=$theme" >/dev/null 2>&1 || echo "FAIL $pg $w $theme"
    done
  done
done
ls "$OUT" | wc -l
