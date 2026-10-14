# Asset manifest — savetoshelf.com homepage

Source: https://www.savetoshelf.com/

The page uses no raster content images, videos, background images or og:image. Every "screenshot"/thumbnail in the app mockups is a flat CSS colour block (see CLONE_SPEC.md). Network log for a full page load (1440px) listed only: `/`, 2 fonts, the CSS, the Astro JS bundle, `/logo.svg`, `/site.webmanifest`, `/favicon.svg`, `/icon-192.png`, and the Plausible analytics script and beacon (analytics.mammutstudios.com, not cloned).

## Fonts (in `public/fonts/`)

| Original URL | Local path | Format | Used for |
|---|---|---|---|
| https://www.savetoshelf.com/fonts/Switzer-Variable.woff2 | /fonts/Switzer-Variable.woff2 | woff2 variable, wght 100–900, 43,220 B | `--font-body`: all body text, nav, buttons, inputs |
| https://www.savetoshelf.com/fonts/GeneralSans-Variable.woff2 | /fonts/GeneralSans-Variable.woff2 | woff2 variable, wght 200–700, 38,132 B | `--font-display`: h1, h2, h3, `.font-display` |

Both were preloaded in the original: `<link rel="preload" href="/fonts/…woff2" as="font" type="font/woff2" crossorigin>`.

## Images / icons (in `public/assets/`)

| Original URL | Local path | Dimensions / format | Where used |
|---|---|---|---|
| https://www.savetoshelf.com/logo.svg | /assets/logo.svg | SVG, 32×32 viewBox, three #1A1A1A "book" paths | Demo app top bar, `<img>` 30×30 (`size-[30px]`). Saving step 2 inside a black 48×48 tile, `<img>` 24×24 with `filter: brightness(0) invert(1)`, so it renders white. Footer `<img>` 18×18. In the original it sits at the site root (`/logo.svg`); use `/assets/logo.svg` in the clone. |
| https://www.savetoshelf.com/favicon.svg | /assets/icons/favicon.svg | SVG 256×256, black rounded square (rx 54) with white logo | `<link rel="icon" type="image/svg+xml">` |
| https://www.savetoshelf.com/favicon-32.png | /assets/icons/favicon-32.png | PNG 32×32 | `<link rel="icon" sizes="32x32" type="image/png">` |
| https://www.savetoshelf.com/apple-touch-icon.png | /assets/icons/apple-touch-icon.png | PNG 180×180 | `<link rel="apple-touch-icon">` |
| https://www.savetoshelf.com/icon-192.png | /assets/icons/icon-192.png | PNG 192×192 | web manifest icon |
| https://www.savetoshelf.com/icon-512.png | /assets/icons/icon-512.png | PNG 512×512 | web manifest icon, also used as the maskable icon |
| https://www.savetoshelf.com/site.webmanifest | /assets/icons/site.webmanifest | JSON | `<link rel="manifest">`. Its icon `src` values point at `/icon-192.png` and `/icon-512.png`. Edit them to `/assets/icons/…`, or copy the PNGs to the public root. |

`theme-color` meta is `#1a1a18`. The manifest has `background_color: #f2f1ed`, `theme_color: #1a1a18`, `display: standalone`.

## Inline SVGs (in `public/assets/svg/`)

On the original page these are all inline `<svg>` elements, and the clone should inline them as JSX too, because CSS animates their child paths. Each file starts with a comment that gives the original classes on the `<svg>`. Colours come from `currentColor` unless the file sets a fill.

| File | viewBox | Where used (in DOM order) | Size / colour on page |
|---|---|---|---|
| logo-books-inline.svg | 0 0 32 32, fill currentColor | Nav logo link. Its 3 paths have `class="book"` (hover animation) | 28×28 (`size-7`), `overflow: visible`, colour #1a1a18 |
| arrow-right.svg | 0 0 24 24, stroke currentColor, stroke-width 2 | Nav "Join waitlist" button-009, used twice (`.button-009__icon.is--left` and `.is--right`) | 0.875em = 14×14 |
| spark-eyebrow.svg | 0 0 24 24, fill currentColor | Hero eyebrow "Bookmarks with a Brain". Paths `.spark-big` and `.spark-small` twinkle | 18×18 |
| waitlist-tick.svg | 0 0 24 24, stroke 2.4 | Waitlist success state (hidden until submit). Path `.tick` draws in with stroke-dashoffset | 24×24 inside a 44×44 accent tile |
| search-magnifier.svg | 0 0 24 24, stroke 2 | Both search palettes (hero demo and #finding) | 22×22, colour #76766e |
| question-ask.svg | 0 0 24 24, stroke 2.1 | "Why Shelf" eyebrow, `.ask` wobble animation | 18×18 |
| question-ask-faq.svg | same paths as question-ask | FAQ heading tile, `.ask` wobble | 24×24 below 640px, 28×28 at 640px and up |
| inbox-tray.svg | 0 0 24 24, stroke 1.9 | "Getting things in" eyebrow (#saving) | 18×18 |
| faq-plus.svg | 0 0 24 24, stroke 2.2 | FAQ item toggle icon (rotates 45° when open) | 16×16 |
| tag-instagram.svg | 0 0 24 24, fill #FF0069 | Falling tag "Instagram" | 1.15em |
| tag-linkedin.svg | 0 0 24 24, stroke 1.7, currentColor = #2d64bc | Falling tag "LinkedIn" | 1.15em |
| tag-web-globe.svg | stroke 1.7, currentColor = #3fbf4a | Falling tag "Web page" | 1.15em |
| tag-voice-note-mic.svg | stroke 1.7, currentColor = #76766e | Falling tag "Voice note" | 1.15em |
| tag-document.svg | stroke 1.7 | Falling tags "Note" (#76766e), "PDF" (#76766e), "Article" (#3fbf4a): same paths, different colour class | 1.15em |
| tag-screenshot.svg | stroke 1.7, #76766e | Falling tag "Screenshot" | 1.15em |
| tag-x.svg | fill #000000 | Falling tag "X post" | 1.15em |
| tag-youtube.svg | fill #FF0000 | Falling tag "YouTube" | 1.15em |
| tag-newsletter.svg | stroke 1.7, #76766e | Falling tag "Newsletter" | 1.15em |
| tag-figma.svg | fill #F24E1E | Falling tag "Figma file" | 1.15em |

Tag pill sizes: 1.15em is 25.3px at 1440px (font 22px) and 14.7px below 640px (font 12.8px).
