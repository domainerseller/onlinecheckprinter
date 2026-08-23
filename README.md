# OnlineCheckPrinter.com

Marketing and affiliate content site comparing check-printing services and software for
businesses. Sister site to RentByCard.com and PayrollByCreditCards.com (same stack).

Built with **Astro 4**, **Tailwind CSS**, **MDX** content collections, **RSS**, and **sitemap**.

## Local development

```bash
npm install
npm run dev
```

Site runs at `http://localhost:4321`.

## Build

```bash
npm run build
npm run preview   # preview the built dist/ locally
```

Output is written to `dist/` — a fully static site.

## Project structure

```
src/
├── components/      # Header, Footer
├── content/
│   ├── config.ts    # content collection schema
│   └── articles/    # MDX articles
├── layouts/         # BaseLayout, ArticleLayout
├── pages/
│   ├── index.astro          # homepage
│   ├── articles/            # listing + [...slug] detail
│   ├── about.astro
│   ├── disclosure.astro     # FTC affiliate disclosure
│   ├── privacy.astro
│   ├── terms.astro
│   ├── 404.astro
│   └── rss.xml.js           # RSS feed
└── styles/
    └── global.css   # tailwind + prose styles
public/
├── favicon.svg
├── og-default.svg   # social share image — see note below
└── robots.txt
```

## Writing new articles

Create a new `.mdx` file in `src/content/articles/`. Frontmatter:

```yaml
---
title: "Your Article Title"
description: "One-sentence summary for SEO and social cards."
pubDate: 2026-04-15
author: "Your Name"
tags: ["Guide", "Reviews"]
featured: false    # set true to pin on homepage
draft: false       # set true to hide from listings and build
---

Your article body in Markdown/MDX.
```

The slug comes from the filename. `hello-world.mdx` becomes `/articles/hello-world`.

## Deployment

The `dist/` folder is fully static and works on any static host. Three recommended options:

### Cloudflare Pages (recommended)

1. Push the repo to GitHub.
2. In Cloudflare dashboard, create a Pages project and connect the repo.
3. Build command: `npm run build`. Output directory: `dist`.
4. Bind the custom domain `onlinecheckprinter.com`.

### Netlify

1. Push to GitHub.
2. `netlify.toml` isn't required — the defaults work. Build command: `npm run build`, publish dir: `dist`.
3. Add the custom domain in Netlify's DNS panel.

### Vercel

1. Import the repo at vercel.com/new.
2. Framework preset should auto-detect as "Astro."
3. Add the custom domain in project settings.

## Before publishing

Check these:

- [ ] Update `site` in `astro.config.mjs` if the production URL differs.
- [ ] Replace `public/og-default.svg` with a **PNG** (1200×630) — Facebook and LinkedIn don't reliably render SVG for social cards. You can use the provided SVG as a design reference.
- [ ] Replace placeholder contact email `hello@onlinecheckprinter.com` in About, Disclosure, Privacy, and Terms pages if you want a different address.
- [ ] Update the `Last updated` dates on Disclosure, Privacy, and Terms if reviewing before launch.
- [ ] Add Google Search Console verification (drop the meta tag into `BaseLayout.astro` or upload the HTML file to `public/`).
- [ ] Set up analytics (Plausible, Fathom, or Cloudflare Web Analytics — all privacy-friendly and mentioned in the Privacy Policy).
- [ ] Review affiliate disclosures are present and accurate before inserting real affiliate links.

## Content collection schema

Defined in `src/content/config.ts`. Fields: `title`, `description`, `pubDate`, `updatedDate?`,
`author`, `heroImage?`, `tags[]`, `draft`, `featured`.

## License

Proprietary. All rights reserved.
