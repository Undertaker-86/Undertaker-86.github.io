# Gyan Edbert Zesiro · Robotics portfolio

**Live site: https://undertaker-86.github.io**

Portfolio of my work in robot learning, perception, planning and embedded systems: humanoid RL for RoboCup,
autonomous-driving perception, multi-robot planning, an autonomous submarine, a transforming drone/car and more.
Each project page leads with results and media, then explains the problem, approach and what I learned. Every metric
says whether it comes from simulation, hardware, validation or a test set.

## Built with

- **[Astro 5](https://astro.build)**: static site, zero JavaScript by default, view transitions between pages
- **MDX content collections**: one file per project in `src/content/projects/`, checked against a schema at build time
- **Tailwind CSS 4**: dark/light theme from CSS design tokens
- **Media**: images as responsive AVIF/WebP; videos as short H.264/VP9 loops that only load when played; the Steelhead
  AUV CAD as a rotatable 3D model (`<model-viewer>`, loaded on request)
- **Charts and diagrams**: drawn as inline SVG/HTML at build time, so they follow the theme and need no JavaScript

## Structure

| Path | Contents |
|---|---|
| `src/content/projects/` | the case studies (MDX) |
| `src/pages/` | home, project index, project pages, about, technical write-ups |
| `src/components/` | video loops, figures, pipeline diagrams, charts, 3D viewer |
| `src/site.config.ts` | profile, education, roles, publications, skills, contact links |
| `scripts/` | media pipeline: video/image compression, chart data, CAD → GLB conversion, PDM4AR render tools |
| `qa/` | screenshot, link, interaction and Lighthouse checks |

## Run locally

```bash
nix develop          # Node 22, pnpm, ffmpeg, ImageMagick, Python (or install these yourself)
pnpm install
pnpm dev             # http://localhost:4321
pnpm build && pnpm preview
```

`pnpm media` regenerates the compressed media from the original project folders. It needs those folders locally; the
compressed outputs are already committed, so building the site does not.

## Deployment

Every push to `main` builds the site and publishes it to GitHub Pages
(`.github/workflows/deploy.yml`, with Settings → Pages → Source set to *GitHub Actions*).

## Contact

gyan.gyan26@gmail.com · [Google Scholar](https://scholar.google.com/citations?user=eKzf9uoAAAAJ&hl=en)

© Gyan Edbert Zesiro. The content and media are mine and my teams'. Please ask before reusing them.
