# Portfolio site: Gyan Edbert Zesiro

Astro 5 (static) · TypeScript strict · MDX content collections · Tailwind v4 · zero-JS by default.

## Run

```bash
nix develop                 # node 22, pnpm, ffmpeg, poppler, imagemagick, librsvg, python (numpy/scipy/matplotlib)
pnpm install
pnpm media                  # copy + compress media from the project folders (idempotent; FORCE=1 to rebuild)
pnpm dev                    # http://localhost:4321
pnpm check && pnpm build && pnpm preview
```

## Layout

| Path | What |
|---|---|
| `src/content/projects/*.mdx` | 11 case studies. The Zod schema in `src/content.config.ts` rejects missing fields, alt text or images at build time |
| `src/site.config.ts` | name, education, roles, publications, skills, **contact/photo flags (all off)** |
| `src/components/` | `VideoLoop`, `Figure`, `Flow` (pipeline diagrams), `BarCompare` / `LineChart` (zero-JS SVG charts), `Metrics`, `EcsDiagram`, `HeroField` (canvas accent) |
| `src/scripts/site.ts` | the only global JS (~1 KB gz): theme, reveals, hover/in-view videos, lightbox |
| `scripts/prepare-media.sh` | ffmpeg/magick pipeline → `public/media/<slug>/*.{mp4,webm}` + `src/assets/<slug>/`; log in `scripts/media-sizes.log` |
| `scripts/make_chart_data.py`, `make_covers.py` | chart JSON + covers regenerated from raw samples (stethoscope log, Stoeber CSVs, ECS firmware constants) |
| `private/profile.jpg` | compressed portrait, **deliberately outside `src/`** so it never ships |
| `qa/` | `shots.mjs` (Playwright full-page screenshots + overflow/broken-image check), `interact.mjs`, `check-links.mjs`, `lighthouse.sh`, `screens.sh` (Firefox fallback) |

QA needs Chromium: `export CHROME_PATH=$(nix build nixpkgs#chromium --no-link --print-out-paths)/bin/chromium`.

## Deploy (GitHub Pages)

1. Create a GitHub repository named **`<username>.github.io`** (links are root-relative, so the site must be served
   at the domain root).
2. Commit and push this folder to its `main` branch (`private/`, `node_modules/`, `dist/` are git-ignored).
3. In the repository: Settings → Pages → Source: **GitHub Actions**. `.github/workflows/deploy.yml` builds and
   deploys on every push; the site URL is taken from the Pages settings automatically.

## Publishing contact details / photo

Set the values and flip `show: true` in `src/site.config.ts`. For the photo, also run
`mkdir -p src/assets/profile && cp private/profile.jpg src/assets/profile/`. The site URL comes from the deploy
workflow (`SITE_URL`).
