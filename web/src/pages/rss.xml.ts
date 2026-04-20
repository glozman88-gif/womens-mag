import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import type { APIContext } from "astro";
import { SITE } from "~/consts";

export async function GET(context: APIContext) {
  const articles = (await getCollection("articles", ({ data }) => !data.draft)).sort(
    (a, b) => b.data.publishedAt.valueOf() - a.data.publishedAt.valueOf(),
  );

  return rss({
    title: SITE.name,
    description: SITE.description,
    site: context.site!,
    items: articles.map((entry) => ({
      title: entry.data.title,
      description: entry.data.description,
      pubDate: entry.data.publishedAt,
      link: `/${entry.data.category}/${entry.slug}`,
      categories: [entry.data.category, ...entry.data.tags],
    })),
    customData: `<language>ru-RU</language>`,
  });
}
