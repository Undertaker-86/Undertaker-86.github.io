// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// GitHub Pages: the deploy workflow passes SITE_URL (e.g. https://<user>.github.io). Local builds fall back to it too.
// Links are root-relative, so publish from a repository named <user>.github.io (served at the domain root).
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://example.github.io',
  output: 'static',
  trailingSlash: 'ignore',
  prefetch: { prefetchAll: false, defaultStrategy: 'hover' },
  integrations: [mdx(), sitemap()],
  markdown: { remarkPlugins: [remarkMath], rehypePlugins: [rehypeKatex] },
  vite: { plugins: [tailwindcss()] },
  build: { inlineStylesheets: 'always' },
});
