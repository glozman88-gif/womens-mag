const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

/** Build a site-relative URL that respects the configured `base` path. */
export function url(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${normalized}`;
}

/** Build a fully-qualified absolute URL (for canonical, OG, sitemap, RSS). */
export function absoluteUrl(path: string, site: URL | string): string {
  const origin = typeof site === "string" ? new URL(site).origin : site.origin;
  return `${origin}${url(path)}`;
}
