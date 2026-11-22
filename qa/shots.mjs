// Full-page screenshots with lazy media loaded: 320/390/768/1440 px × light/dark, reduced motion.
// Usage: CHROME_PATH=…/bin/chromium node qa/shots.mjs [base]
import { chromium } from 'playwright-core';
import { mkdirSync } from 'node:fs';
const base = process.argv[2] ?? 'http://127.0.0.1:4321';
const out = new URL('./out/', import.meta.url).pathname;
mkdirSync(out, { recursive: true });
const pages = ['/', '/projects', '/projects/nomadz-kicking', '/projects/header-net', '/projects/drone-car', '/projects/subbots',
  '/projects/scene-graph-localization', '/projects/pdm4ar', '/projects/cvaiac-dense-prediction', '/projects/cvaiac-lidar-detection',
  '/projects/stethoscope', '/projects/stoeber-porous-valve', '/projects/ecs-haptic-wheel', '/about', '/404'];
const widths = (process.env.WIDTHS ?? '320,390,768,1440').split(',').map(Number);
const themes = (process.env.THEMES ?? 'dark,light').split(',');
const only = process.env.PAGES?.split(',');
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH, args: ['--no-sandbox'] });
const problems = [];
for (const w of widths) for (const theme of themes) {
  const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, reducedMotion: 'reduce', deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => problems.push(`JS error ${page.url()}: ${e.message}`));
  for (const p of only ?? pages) {
    await page.goto(`${base}${p}?theme=${theme}`, { waitUntil: 'networkidle' });
    await page.evaluate(async () => { // scroll through so lazy images load
      for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); }
      window.scrollTo(0, 0);
    });
    await page.waitForLoadState('networkidle');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (overflow > 0) problems.push(`horizontal overflow ${overflow}px on ${p} @${w}`);
    const broken = await page.evaluate(() => [...document.images].filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.currentSrc));
    if (broken.length) problems.push(`broken images on ${p}: ${broken.join(', ')}`);
    const name = (p.replace(/^\//, '').replace(/\//g, '_') || 'home') + `-${w}-${theme}.png`;
    await page.screenshot({ path: out + name, fullPage: true });
  }
  await ctx.close();
}
await browser.close();
console.log(problems.length ? problems.join('\n') : 'no overflow, no broken images, no JS errors');
