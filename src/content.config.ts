import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

export const CATEGORIES = [
  'Robotics',
  'Learning & RL',
  'Perception',
  'Planning & Control',
  'Embedded',
  'Signal processing',
  'Hardware/Mechanical',
] as const;

export const categorySlug = (c: string) =>
  c.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

const projects = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/projects' }),
  schema: ({ image }) =>
    z
      .object({
        title: z.string().min(3),
        short: z.string().max(28).describe('Short name for cards and nav'),
        summary: z.string().min(40).max(240),
        org: z.string(),
        context: z.string().describe('Lab, team, course …'),
        role: z.string(),
        team: z.string(),
        start: z.coerce.date(),
        end: z.coerce.date().optional().describe('Omit for ongoing'),
        categories: z.array(z.enum(CATEGORIES)).min(1),
        stack: z.array(z.string()).min(2),
        featured: z.boolean().default(false),
        order: z.number().int(),
        cover: image(),
        coverAlt: z.string().min(10),
        /** Base name of a looping clip in public/media/<slug>/<video>.{mp4,webm}; its poster is `cover`. */
        video: z.string().optional(),
        /** Interactive 3D model for the case-study hero (GLB under /public); `cover` is its poster. */
        model: z.object({ src: z.string().startsWith('/'), size: z.string() }).optional(),
        metrics: z
          .array(
            z.object({
              value: z.string(),
              label: z.string(),
              /** Where the number comes from: simulation, hardware, validation/test split … */
              basis: z.enum(['simulation', 'hardware', 'validation', 'test', 'benchmark', 'experiment', 'team result']),
              note: z.string().optional(),
            }),
          )
          .min(1)
          .max(5),
        award: z.string().optional().describe('Placement or prize, shown as a badge'),
        headline: z.string().optional().describe('One metric for the home card, e.g. "73 % far-goal rate"'),
        links: z
          .array(z.object({ label: z.string(), href: z.string().regex(/^(https:\/\/|\/)/, 'absolute https URL or site path') }))
          .default([]),
        codeNote: z.string().optional().describe('Why code is not linked (e.g. course policy)'),
        credits: z.string().optional(),
      })
      .refine((d) => !d.end || d.end >= d.start, { message: 'end must be after start' }),
});

export const collections = { projects };
