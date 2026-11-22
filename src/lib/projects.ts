import { getCollection, type CollectionEntry } from 'astro:content';

export type Project = CollectionEntry<'projects'>;

export async function getProjects(): Promise<Project[]> {
  const all = await getCollection('projects');
  return all.sort((a, b) => a.data.order - b.data.order);
}

const fmt = new Intl.DateTimeFormat('en', { month: 'short', year: 'numeric', timeZone: 'UTC' });

export function dateRange(p: Project): string {
  const s = fmt.format(p.data.start);
  if (!p.data.end) return `${s} – present`;
  const e = fmt.format(p.data.end);
  return s === e ? s : `${s} – ${e}`;
}

export function years(p: Project): string {
  const a = p.data.start.getUTCFullYear();
  const b = p.data.end?.getUTCFullYear();
  if (!b) return `${a}–`;
  return a === b ? `${a}` : `${a}–${String(b).slice(2)}`;
}
