# Shelf homepage clone — information architecture

> `ia.json` is the only file to hand-edit. `IA.md` and `matrix.csv` are
> **generated** by `build.mjs` and will be overwritten.

Local clone of https://www.savetoshelf.com/ (React 18 + Vite + Tailwind v3;
the original is Astro + Tailwind v4). Run it with `npm install && npm run dev`
(serves on http://localhost:5200).

## IA files

| file | what it is |
|---|---|
| `ia.json` | Source of truth: categories, sections (each defined once, with `implementedBy`), templates and routes |
| `IA.md` | Generated readable doc |
| `matrix.csv` | Generated section × template matrix |
| `validate.mjs` / `build.mjs` | Generic checker / generator, copied from the ia-builder skill |

Re-run after editing `ia.json`:

```bash
node validate.mjs && node build.mjs
```

## What the data shows

- **One route, one template.** savetoshelf.com is a single page: `/` only.
  The sitemap and robots.txt don't exist, 23 common paths all return the
  hosting platform's default 404, and the site's JS calls no other page
  routes (only the `/api/waitlist` POST, which this clone stubs locally).
- **Nine sections, all page-local.** With a single template, no section is
  shared across templates, so reuse lives one level down, in components:
  `WaitlistForm` renders inside both `hero.intro` and
  `conversion.closing-waitlist`, and `Palette` inside both
  `hero.demo-mockup` and `story.finding`. Those two are the real shared
  components; everything else can stay section-local.
- **The build effort is in the STORY band.** `story.why-funnel` alone
  (scroll-driven bookmark clip-path + matter-js tag physics in
  `src/lib/bookmark.js`) is the most complex piece. Its tag positions are
  random on every run on both the original and the clone, so they can't be
  pinned in any spec.

Measured values behind every section (sizes, type, colour, motion timings)
are in `CLONE_SPEC.md`.
