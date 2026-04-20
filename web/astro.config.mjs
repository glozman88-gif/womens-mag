import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";

// SITE can be set via env (CI sets it to the real GitHub Pages URL or custom domain).
// Defaults to a placeholder so the build works locally too.
const SITE_URL = process.env.SITE || "https://example.github.io/womens-mag";

// If the site lives under a sub-path (e.g. https://user.github.io/repo), we must
// also set `base`. We auto-derive it from the URL path.
const siteUrl = new URL(SITE_URL);
const basePath = siteUrl.pathname.replace(/\/$/, "") || "/";

export default defineConfig({
  site: `${siteUrl.origin}${basePath === "/" ? "" : basePath}`,
  base: basePath,
  trailingSlash: "never",
  build: {
    format: "directory",
  },
  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
  ],
  markdown: {
    shikiConfig: {
      theme: "github-light",
    },
  },
});
