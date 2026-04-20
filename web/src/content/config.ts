import { defineCollection, z } from "astro:content";

const CATEGORIES = [
  "zvezdy",
  "krasota",
  "moda",
  "otnosheniya",
  "psihologiya",
  "stil-zhizni",
] as const;

const articles = defineCollection({
  type: "content",
  schema: ({ image }) =>
    z.object({
      title: z.string().min(5).max(160),
      description: z.string().min(20).max(300),
      category: z.enum(CATEGORIES),
      tags: z.array(z.string()).default([]),
      heroImage: z.string().optional(),
      heroImageAlt: z.string().optional(),
      publishedAt: z.coerce.date(),
      updatedAt: z.coerce.date().optional(),
      sourceUrl: z.string().url(),
      sourceName: z.string(),
      author: z.string().default("Редакция"),
      draft: z.boolean().default(false),
    }),
});

export const collections = { articles };

export const CATEGORY_META: Record<
  (typeof CATEGORIES)[number],
  { label: string; description: string }
> = {
  zvezdy: {
    label: "Звёзды",
    description: "Новости шоу-бизнеса, интервью, светская хроника",
  },
  krasota: {
    label: "Красота",
    description: "Бьюти-тренды, уход за кожей, макияж, волосы",
  },
  moda: {
    label: "Мода",
    description: "Тренды, стиль, гардероб, недели моды",
  },
  otnosheniya: {
    label: "Отношения",
    description: "Любовь, семья, советы психолога",
  },
  psihologiya: {
    label: "Психология",
    description: "Самопознание, отношения, эмоции",
  },
  "stil-zhizni": {
    label: "Стиль жизни",
    description: "Путешествия, дом, еда, хобби",
  },
};
