import type { APIContext } from "astro";
import { getCollection } from "astro:content";
import { CATEGORY_META } from "~/content/config";

export async function GET(context: APIContext) {
  const site = context.site!;
  const articles = await getCollection("articles", ({ data }) => !data.draft);

  const urls: { loc: string; lastmod?: string; priority?: string; changefreq?: string }[] = [];

  const add = (path: string, opts: Partial<{ lastmod: string; priority: string; changefreq: string }> = {}) => {
    urls.push({ loc: new URL(path, site).toString(), ...opts });
  };

  add("/", { priority: "1.0", changefreq: "daily" });
  add("/about", { priority: "0.3", changefreq: "yearly" });
  add("/contacts", { priority: "0.3", changefreq: "yearly" });
  add("/privacy", { priority: "0.2", changefreq: "yearly" });

  for (const key of Object.keys(CATEGORY_META)) {
    add(`/${key}`, { priority: "0.8", changefreq: "daily" });
  }

  for (const a of articles) {
    const lastmod = (a.data.updatedAt ?? a.data.publishedAt).toISOString();
    add(`/${a.data.category}/${a.slug}`, {
      priority: "0.7",
      changefreq: "weekly",
      lastmod,
    });
  }

  const body = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`,
    ...urls.map(
      (u) =>
        `  <url><loc>${u.loc}</loc>` +
        (u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : "") +
        (u.changefreq ? `<changefreq>${u.changefreq}</changefreq>` : "") +
        (u.priority ? `<priority>${u.priority}</priority>` : "") +
        `</url>`,
    ),
    `</urlset>`,
  ].join("\n");

  return new Response(body, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
}
