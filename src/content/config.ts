import { defineCollection, z } from 'astro:content';

const articles = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().default('editorial-team'),
    heroImage: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    featured: z.boolean().default(false),
    factCheckedBy: z.string().optional(),
  }),
});

const authors = defineCollection({
  type: 'content',
  schema: z.object({
    name: z.string(),
    title: z.string(),
    avatar: z.string().optional(),
    bio: z.string(),
    credentials: z.array(z.string()).default([]),
    specialties: z.array(z.string()).default([]),
    yearsExperience: z.number().optional(),
    linkedin: z.string().optional(),
    twitter: z.string().optional(),
    email: z.string().optional(),
  }),
});

export const collections = { articles, authors };
