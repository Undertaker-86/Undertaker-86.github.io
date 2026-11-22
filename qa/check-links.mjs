// Verify every internal href/src in dist/ resolves to a file; list external links for review.
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
const dist = new URL('../dist/', import.meta.url).pathname;
const walk = (d) => readdirSync(d).flatMap((f) => (statSync(join(d, f)).isDirectory() ? walk(join(d, f)) : [join(d, f)]));
const html = walk(dist).filter((f) => f.endsWith('.html'));
const bad = new Set(), ext = new Set();
for (const f of html) {
  const s = readFileSync(f, 'utf8');
  for (const m of s.matchAll(/(?:href|src|srcset|poster)="([^"]+)"/g)) {
    for (let u of m[1].split(',').map((x) => x.trim().split(' ')[0])) {
      if (/^(https?:)?\/\//.test(u)) { ext.add(u); continue; }
      if (!u.startsWith('/') || u.startsWith('//')) continue;
      u = decodeURIComponent(u.split(/[?#]/)[0]);
      const p = join(dist, u);
      if (!(existsSync(p) && statSync(p).isFile()) && !existsSync(join(p, 'index.html')) && !existsSync(p + '.html')) bad.add(`${u}  (in ${f.replace(dist, '')})`);
    }
  }
  for (const m of s.matchAll(/<source src="([^"]+)"/g)) if (!existsSync(join(dist, m[1]))) bad.add(m[1]);
}
console.log(`${html.length} pages; broken internal: ${bad.size}`); bad.forEach((b) => console.log('  BROKEN', b));
console.log('external links:'); ext.forEach((e) => console.log('  ', e));
