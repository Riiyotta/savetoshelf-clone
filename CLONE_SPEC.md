Source: https://www.savetoshelf.com/

# Shelf homepage — clone spec

I measured the live site with Playwright at 1440×900, 1280×800, 768×1024 and 390×844 on 2026-10-14. All values below are computed styles or bounding rects unless a line says otherwise. For the exact markup, cross-check the local snapshot `Shelf_ Everything you saved. Finally findable..html`. The original CSS (`index.C1emElDY.css`) and JS (`Base.astro…C5_EadgT.js`) are in `Shelf_ Everything you saved. Finally findable._files/` and match the live files byte for byte. Read them when a value here needs confirming.

Assets and fonts are already downloaded. See `public/assets/MANIFEST.md`.

---

## 0. Framework, libraries, widgets

- **Framework:** Astro (static output, hashed `/_astro/` assets, `data-astro-cid-*` scoped styles). No React, Next.js, Framer or Webflow.
- **CSS:** Tailwind **v4.3.3**. The clone uses Tailwind v3, so the porting notes in §1.6 apply.
- **JS libraries in the bundle:**
  - **Lenis 1.3.26** smooth scroll (`window.lenis`, `window.lenisVersion`). Config: `new Lenis({ lerp: 0.1, smoothWheel: true, syncTouch: false, anchors: { offset: -100 } })`, driven by a manual `requestAnimationFrame` loop calling `lenis.raf(t)`. Skipped entirely when `prefers-reduced-motion: reduce`. It adds the classes `lenis`, `lenis-scrolling` and `lenis-smooth` to `<html>`, and injects the standard Lenis CSS (`html.lenis, html.lenis body{height:auto}` and so on).
  - **matter-js 0.20.0**: 2D physics for the falling "source tags" in the hero funnel (§3.4).
  - **figma-squircle** algorithm, inlined: every element with `data-squircle` gets an inline `clip-path: path(...)` squircle. It takes `border-radius` from computed style and uses `cornerSmoothing = 0.6` (or the attribute's value), `preserveSmoothing: false`. A ResizeObserver recomputes it, and it recomputes again on `document.fonts.ready`. In React, use the npm package `figma-squircle` (`getSvgPath({width,height,cornerRadius,cornerSmoothing:0.6})`) in a `useSquircle` ref hook.
  - No GSAP and no framer-motion. Everything else is CSS transitions, keyframes, IntersectionObserver and scroll listeners.
- **Analytics:** Plausible-style script from analytics.mammutstudios.com. Do not clone it.
- **Interactive widgets:**
  1. Fixed nav whose bar shrinks once `scrollY > 12` (`.is-stuck`).
  2. Two waitlist forms (hero `#waitlist-hero`, closing `#waitlist-closing`). They POST `{email}` JSON to `/api/waitlist`. I did not submit them (that would be a real signup), so the success response is inferred from the JS. On `ok` the form gets `hidden` and the `-done` card fades in. On failure, text appears in the `-note` paragraph.
  3. Auto-typing search "command palettes", 2 instances, looping.
  4. FAQ accordion: 6 items, at most one open.
  5. Scroll-driven "bookmark" clip-path on the hero, with a physics tag pile.
  6. IntersectionObserver reveals.
  7. Closing CTA side blocks that animate their `flex-basis`.
- No modals and no tabs.

---

## 1. Global

### 1.1 @font-face (copy exactly)

```css
@font-face{font-family:"Switzer";src:url(/fonts/Switzer-Variable.woff2) format("woff2");font-weight:100 900;font-style:normal;font-display:swap}
@font-face{font-family:"General Sans";src:url(/fonts/GeneralSans-Variable.woff2) format("woff2");font-weight:200 700;font-style:normal;font-display:swap}
```
Also preload both fonts in `index.html`: `<link rel="preload" href="/fonts/GeneralSans-Variable.woff2" as="font" type="font/woff2" crossorigin>` and the same for Switzer.

- `--font-body: "Switzer", ui-sans-serif, system-ui, sans-serif`
- `--font-display: "General Sans", ui-sans-serif, system-ui, sans-serif`
- Weights in use: Switzer 400, 500, 600. General Sans 500 (FAQ questions) and 600 (all headings).
- `<kbd>` uses the Tailwind mono stack `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace`.

### 1.2 Design tokens (`:root`)

| token | value | rgb |
|---|---|---|
| --text | #1a1a18 | rgb(26,26,24) |
| --text-muted | #76766e | rgb(118,118,110) |
| --text-faint | #a5a59c | rgb(165,165,156) |
| --surface | #f2f1ed | page background (body) |
| --surface-raised | #fcfcfb | cards, hero block, nav bar |
| --surface-sunken | #e9e8e3 | eyebrow pill, sunken chips |
| --border | #e1e0da | 1px borders |
| --border-strong | #c6c4bd | dashed border, gradient line |
| --accent | #9ee86f | lime green: CTA, highlights, closing block |
| --source-linkedin | #2d64bc | |
| --source-instagram | #d6336c | |
| --source-x | #1a1a18 | |
| --source-note | #76766e | |

Other literal colours in use: #3fbf4a (web green), #1c1c1a, #dfe4ee, #e2ded4, #e4e8f2, #e6e2ec, #e8effa, #eae7df, #efe3d6, #f3e7dc. In Tailwind v4, opacity modifiers compile to `color-mix(in oklab, var(--x) N%, transparent)`. In v3, use `rgb(r g b / a)`:
- `text-text/70` = rgba(26,26,24,.7)
- `bg-surface-raised/45` = rgba(252,252,251,.45)
- `bg-accent/45` = rgba(158,232,111,.45)
- `bg-border-strong/40|50|60` = rgba(198,196,189,.4|.5|.6)
- Nav stuck ring: `color-mix(in srgb, #e1e0da 55%, transparent)` = rgba(225,224,218,.55)

Easing tokens:
- `--ease-out: cubic-bezier(0,0,.2,1)`
- `--ease-in-out: cubic-bezier(.4,0,.2,1)`. This is also Tailwind's default transition easing, at 150ms.
- `--ease-bounce` (a CSS `linear()` spring, used for the FAQ panel and the closing blocks):
```
linear(0 0%, .001 1.1%, .003 2.3%, .007 3.6%, .014 4.9%, .022 6.3%, .033 7.8%, .046 9.2%, .061 10.6%, .08 12%, .126 13.9%, .185 15.7%, .255 17.5%, .335 19.2%, .424 20.8%, .521 22.5%, .626 24.3%, .735 26.1%, .85 28%, .912 29.4%, .964 31%, 1.019 32.6%, 1.108 34.4%, 1.173 36.3%, 1.215 38.4%, 1.234 40.5%, 1.232 42.7%, 1.208 45%, 1.158 47.4%, 1.113 49.8%, 1.073 52.4%, 1.04 55%, 1.014 57.8%, .996 60.6%, .987 63.6%, .988 66.7%, 1 70%, 1.014 73.3%, 1.021 76.7%, 1.023 80%, 1.021 83.3%, 1.017 86.7%, 1.012 90%, 1.006 93.3%, 1.002 96.7%, 1 100%)
```

### 1.3 Base

- `html`: class `antialiased` (`-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale`), line-height 1.5. `--nav-h` is set inline by JS to the nav's offsetHeight: 76px at 640px and up, 72px below.
- `body`: `min-height: 100dvh`, background #f2f1ed, colour #1a1a18, Switzer 16px/24px.
- `h1,h2,h3 { font-family: var(--font-display); letter-spacing: -0.03em }`. The em value is resolved on the heading element, so a child with a different font-size inherits the px value. Example: FAQ `<h3>` is 16px, so its button gets -0.48px even at 18px. Visually styled "headings" that are `<p>` (the funnel title, "Good morning") get **no** negative tracking.
- Preflight: lists have no style, img/svg are `display: block`, buttons and inputs inherit font.

### 1.4 Breakpoints used

- `sm` = 640px (40rem)
- `lg` = 1024px (64rem)
- An extra `@media (width < 40rem)` rule on the bookmark header.

Nothing else. At 768 everything is in "sm" mode but not "lg". At 390 it is base (mobile).

### 1.5 Page skeleton and document y-positions (1440×900, doc height 5364px)

| block | y | height | note |
|---|---|---|---|
| `<nav data-nav>` fixed | 0 | 76 | z-50, outside the clipped header |
| wrapper `div.px-2.sm:px-3` > `header[data-bookmark]` | 0 | 2378 | max-w 1440, mx-auto, bg #fcfcfb, padding-top var(--nav-h) |
|  • hero `section` | 76 | 600.1 | |
|  • demo wrapper | 676.1 | 801.9 | |
|  • `.funnel` | 1478 | 900 (=100svh) | |
| `main > section` (no id) wrapping `#finding` content | 2378 | 921.5 | **Note:** the `<section id="finding">` is the outer element. Its child div holds the content. |
| `section#saving` | 3299.5 | 624 | |
| `section#faq` | 3923.5 | 891.3 | |
| closing waitlist `section` | 4814.8 | 453.6 | |
| `footer` | 5268.4 | 96 | |

At 1280×800 the doc height is 5173 (header 2186.9, funnel 800). At 768×1024 it is 5467 (header 2081.1). At 390×844 it is 5553 (header 1673).

The page background #f2f1ed shows as a 12px gutter left and right of every rounded card at 640px and up, and an 8px gutter below 640px. That gutter comes from the `px-2 sm:px-3` wrappers.

### 1.6 Tailwind v3 porting notes

- Extend the theme:
  - `colors`: `text: {DEFAULT:'#1a1a18', muted:'#76766e', faint:'#a5a59c'}`, `surface: {DEFAULT:'#f2f1ed', raised:'#fcfcfb', sunken:'#e9e8e3'}`, `border: {DEFAULT:'#e1e0da', strong:'#c6c4bd'}`, `accent:'#9ee86f'`, `source: {linkedin:'#2d64bc', instagram:'#d6336c'}`.
  - `fontFamily`: `{ body: [...], display: [...] }`.
  - `spacing: { 13: '3.25rem' }` (needed for `sm:size-13`).
- v3 has no `size-*` utilities before 3.4. With 3.4.14 `size-*` works.
- v4 `shadow-sm` equals the v3 `shadow` value (0 1px 3px 0 rgb(0 0 0/.1), 0 1px 2px -1px rgb(0 0 0/.1)). It is not visibly used.
- v4's `rounded-full` is 3.4e38px, while v3's is 9999px. Both render as pill shapes.
- The original animates the individual `translate`/`scale`/`rotate` CSS properties, not `transform`. Keep those rules in plain CSS (`src/index.css`) so they don't fight Tailwind transforms.
- `text-4xl` = 36px/40px; `text-5xl` = 48px/1; `text-lg` = 18px/28px; `text-sm` = 14px/20px; `leading-relaxed` = 1.625; `leading-snug` = 1.375; `leading-tight` = 1.25. These match between v3 and v4.
- `text-[17px]` and similar arbitrary sizes in v4 carry **no** line-height, so they inherit 1.5. Many of the measured line-heights below are therefore 1.5 × size unless a `leading-*` class applies. Use the measured px values.
- `max-w-lg` = 512, `max-w-xl` = 576, `max-w-2xl` = 672, `max-w-3xl` = 768, `max-w-4xl` = 896, `max-w-6xl` = 1152 (same in v3).

---

## 2. Nav (`<nav data-nav aria-label="Main">`)

**Structure:** `nav.fixed.inset-x-0.top-0.z-50` > `div[data-nav-bar]` (flex, items-center, justify-between) > [logo link] [div: ul of links + CTA].

- **nav:** padding 12px 12px 0 at 640px and up (`px-3 pt-3`), 8px 8px 0 below 640px. Height 76 (sm and up) / 72 (mobile). Transparent; no backdrop-filter anywhere on the page.
- **bar:** width 100%, max-width 56rem (896px), margin auto. Background #fcfcfb, radius 16px. Padding 8px 8px 8px 24px. Height 64px. No border or shadow at rest.
  - Measured x: 272 at 1440, 192 at 1280, 12 at 768 (width 744), 8 at 390 (width 374).
  - `transition: max-width .6s cubic-bezier(.32,.72,0,1), box-shadow .4s ease-out`.
  - **Stuck state:** JS toggles `.is-stuck` on `nav` when `window.scrollY > 12` (rAF-throttled, passive scroll listener). Stuck values: max-width 46rem (736px) and `box-shadow: 0 0 0 1px rgba(225,224,218,.55)`. Measured: at scrollY 8 the bar is 896 wide; at 13 it is 736. At the top, the bar background (#fcfcfb) matches the hero block, so the bar is invisible. Once scrolled it reads as a floating pill.
  - Reduced motion: no transition.
- **Logo:** `a.logo[href="/"][aria-label="Shelf, home"]`, flex, gap 8px, with `span.sr-only` "Shelf". The inline svg is 28×28 (`size-7`), `overflow: visible`, fill currentColor (#1a1a18). See `public/assets/svg/logo-books-inline.svg`. At 1440 it sits at x 296, y 30.
  - **Hover:** each `.book` path has `transform-box: fill-box; transform-origin: 0% 100%` (book 3: `100% 100%`), with `transition: rotate .5s cubic-bezier(.34,1.4,.64,1), translate .5s cubic-bezier(.34,1.4,.64,1)`.
  - On `.logo:hover`: book1 `rotate: -54deg` (delay .1s), book2 `rotate: -44deg` (delay .05s), book3 `rotate: -35deg` (delay 0). On un-hover they return with the same delays, because the delay is declared in the hover rule only, so un-hover has 0 delay.
- **Right group:** flex, items-center, gap 24px at 640px and up (20px below).
  - **Links** `ul` (hidden below 640px; flex at 640px and up), gap 20px (16px base). Font Switzer 15px/22.5px, weight 400, colour #1a1a18. Items: **Finding** → `#finding`, **Saving** → `#saving`, **FAQ** → `#faq`. Measured widths 49.9 / 45.7 / 28.5. At 1440 the ul starts at x 821.5.
    - Hover (only under `@media (hover:hover)`): colour → #76766e. Transition: Tailwind `transition` (all listed props) 150ms cubic-bezier(.4,0,.2,1).
    - Lenis `anchors: {offset:-100}` smooth-scrolls these to 100px above the target.
  - **CTA, "Join waitlist" (Osmo "Button 009")**: `a.button-009[href="#waitlist"][data-squircle]`, 150.3×48. Markup:
    ```html
    <a class="button-009" href="#waitlist" data-squircle>
      <span class="button-009__inner">
        <svg class="button-009__icon is--left">arrow</svg>
        <span class="button-009__text">Join waitlist</span>
        <svg class="button-009__icon is--right">arrow</svg>
      </span>
      <span class="button-009__bg"></span>
    </a>
    ```
    - Variables: colour #1a1a18; background #9ee86f; radius .9rem (14.4px); padding 1em 1.25em 1em 1.5em (16/20/16/24); gap .375em (6px); icon .875em (14px). Font-size 16px, weight 500, line-height 1 (16px), `display: inline-grid`; `__inner` and `__bg` both sit in `grid-area: 1/1`. `__inner` has `overflow: clip`. The left icon is `position: absolute; left: 20px; opacity: 0; translate: -1.5em` (-24px).
    - Base transitions: `.button-009 { transition: scale .15s cubic-bezier(.4,0,.2,1) }`; `__text { transition: translate .5s cubic-bezier(.32,.72,0,1) }`; `__icon { transition: translate .5s cubic-bezier(.32,.72,0,1), opacity .15s ease-out }`.
    - Hover / focus-visible, only under `(hover:hover) and (pointer:fine) and (prefers-reduced-motion:no-preference)`:
      - `__text` translates to `calc(.875em + .375em + 1.25em - 1.5em)` = **16px** right, `transition: translate .5s 75ms cubic-bezier(.32,.72,0,1)`.
      - The left icon goes to `opacity: 1; translate: 0` with `transition: translate .5s 75ms <ease>, opacity .15s 75ms ease-out`.
      - The right icon goes to `opacity: 0; translate: 1.5em` with `transition: translate .5s 50ms <ease>, opacity .15s 75ms ease-out`.
      - Net effect: the arrow slides out to the right while a new arrow slides in from the left and the label shifts right.
    - `:active` → `scale: .955 .925`.
    - Focus-visible: the `::after` overlay (`inset: -.125em`, same radius, `transition: box-shadow .3s cubic-bezier(.32,.72,0,1)`) gets `box-shadow: 0 0 0 .125em #1a1a18`.
    - A squircle clip-path is applied (radius 14.4, smoothing .6).

---

## 3. Hero block (`header[data-bookmark]`)

**Wrapper:** `div.px-2.sm:px-3` (12px / 8px side padding).

**header:** `position: relative`, mx-auto, max-width 1440px, bg #fcfcfb, `rounded-b-[3.5rem]` (56px bottom radius, which is only the no-JS fallback). Padding-top `var(--nav-h, 82px)` (76 measured). The JS replaces the shape with a clip-path (see §3.4). Width 1416 at 1440, 1256 at 1280, 744 at 768, 374 at 390.

CSS custom props on the header (all used by the JS):
```
--notch: clamp(96px, 15vw, 220px);   /* 216 @1440, 192 @1280, 115.2 @768 */
--gap: 32px;
--hold: calc(100svh - var(--notch) - var(--gap));  /* 652 @1440×900, 576 @1280×800, 876.8 @768×1024 */
--bend: 620px;
--corner: 56px;
@media (width < 40rem) { --notch: 120px; --corner: 20px }   /* @390×844: hold 692 */
```
Register `--bend`, `--hold`, `--gap` and `--notch` with `@property { syntax: "<length>"; inherits: true; initial-value: 0 }`.

### 3.1 Hero text section

`section.mx-auto.max-w-4xl.px-6.text-center`: max-width 896, padding 96/24/80/24 at 640px and up (`sm:pt-24 sm:pb-20`), 64/24/64/24 below 640px. Height 600.1 at 1440. All children are centred.

1. **Eyebrow pill**, `p[data-squircle]`, inline-flex, items-center, gap 6px. Padding 6px 14px 6px 10px, radius 10px, bg #e9e8e3. Switzer 14px/21px, **600**, letter-spacing -0.14px (-0.01em), colour #1a1a18. Size 197.4×33, y 172.
   - Content: the spark svg (18×18, `public/assets/svg/spark-eyebrow.svg`) followed by **"Bookmarks with a Brain"**.
   - Animations: `.spark-big { animation: twinkle-big 2.4s ease-in-out infinite }`; `.spark-small { animation: twinkle-small 2.4s ease-in-out .35s infinite }`. Both have `transform-box: fill-box; transform-origin: center`.
     ```css
     @keyframes twinkle-big{0%,100%{scale:1;rotate:0deg}50%{scale:.68;rotate:-32deg}}
     @keyframes twinkle-small{0%,100%{scale:.72;opacity:.45}45%{scale:1.45;opacity:1}}
     ```
2. **h1**, margin-top 20px. General Sans 600, `font-size: clamp(2.75rem, 8.5vw, 5.25rem)`, line-height 1.02, letter-spacing -0.03em.
   - Measured: 84px/85.68px, ls -2.52px at 1440 and 1280; 65.28px/66.59px, ls -1.958px at 768; 44px/44.88px, ls -1.32px at 390. Box 848×171.4 at 1440 (two lines).
   - Markup:
     ```html
     <h1><span class="line" style="display:block">Everything you saved</span>
         <span class="line" style="display:block"><span class="mark px-[0.23em]"><span class="mark-fill rounded-[0.23em]" data-squircle aria-hidden></span>finally</span> findable</span></h1>
     ```
   - `.mark` is `position: relative` with horizontal padding .23em (19.32px at 84px).
   - `.mark-fill`: `position: absolute; inset: .14em 0 -.01em; z-index: -1; background: #9ee86f; border-radius: .23em` (19.32px), squircle clip.
   - **Load animation:** `transform-origin: left center; scale: 0 1; animation: sweep .95s cubic-bezier(.625,.05,0,1) .25s forwards; @keyframes sweep { to { scale: 1 1 } }`. The green highlight wipes in from left to right 250ms after load.
   - Measured mark box at 1440: 262.5×105, fill 262.5×94.1 starting 11.76px below the mark top.
   - Below 640px the h1 still breaks after "saved". At 390 it measures 326×134.6, three lines: "Everything you" / "saved" / "finally findable".
3. **Sub paragraph**, `p.mx-auto.mt-8.max-w-lg`: margin-top 32px, max-width 512. Switzer 19px, line-height 1.625 (30.875px), colour #76766e, `text-wrap: pretty`.
   - Copy: "Your personal inspiration library that remembers`<br class="hidden sm:inline">` not just what you saved, but why." (Two lines at 640px and up, breaking after "remembers"; 3 lines at 390.)
4. **Waitlist anchor** `div#waitlist.mt-10.scroll-mt-24`: margin-top 40px, scroll-margin-top 96px.
   - **form#waitlist-hero[data-waitlist]**: flex, items-center, gap 8px, width 100%, max-width 460px, mx-auto. Padding 8px, radius 16px, bg #fcfcfb, **1px solid #e1e0da**. Height 66. On `:focus-within` the border colour becomes #76766e (transition colours 150ms std).
     - `label.sr-only` "Your email address".
     - `input#waitlist-hero-email[type=email][required][autocomplete=email][placeholder="Enter your email"]`: flex 1, min-width 0, transparent, padding 12px 16px, 16px/24px, height 48. Placeholder colour #a5a59c. `focus:outline-none`.
     - **button[type=submit][data-squircle][disabled]** "Join waitlist": shrink-0, radius .7rem (11.2px), padding 12px 24px, 16px/24px, **500**, nowrap, 134.3×48.
       - Enabled: bg #1a1a18, text #fcfcfb. Disabled (the initial state): bg #f2f1ed, text #a5a59c.
       - `hover: filter: brightness(1.25)` (not when disabled). `focus-visible`: 2px ring #1a1a18, no outline. Transition colours 150ms.
       - The button is enabled only when `input.checkValidity()` passes **and** the email matches `/^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/`. It is re-checked on every `input` event.
   - **Submit flow:** preventDefault. The button text changes to "One moment" and the button is disabled. Then `fetch('/api/waitlist', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({email})})`.
     - If the response is ok: `form.hidden = true`, un-hide `#waitlist-hero-done`, then after 2 rAFs add `.is-in`.
     - If not ok: note text "That did not go through. Try again in a moment."
     - On network error: "That did not go through. Check your connection and try again."
     - Finally the original label is restored and validity re-checked.
   - **Done card** `div#waitlist-hero-done[data-waitlist-done][hidden][role=status]`: when shown it is flex, items-center, gap 14px, max-width 460, mx-auto, padding 12px, radius 16px, bg #fcfcfb.
     - Start state: `opacity: 0; translate: 0 8px`. Transition `opacity .5s ease-out, translate .6s cubic-bezier(.22,1,.36,1)`. `.is-in` → opacity 1, translate 0.
     - Contents: a 44×44 tile (radius 13px, bg #9ee86f, squircle) holding the tick svg (24px, stroke 2.4), plus two text lines:
       - "You are on the list": 15px/20.625px, 500.
       - "Check your inbox, a confirmation is on its way.": 14px/19.25px, #76766e, margin-top 2px.
     - Tick draw: `.tick { stroke-dasharray: 24; stroke-dashoffset: 24 }` → `.is-in .tick { stroke-dashoffset: 0; transition: stroke-dashoffset .45s ease-out .15s }`.
   - **Error note** `p#waitlist-hero-note.mt-3.hidden.text-sm`: 14px/20px, colour rgba(26,26,24,.7), margin-top 12px.

### 3.2 Demo app mockup (scaled 1440-wide fake UI)

- Wrapper `div.px-4.pb-4.sm:px-8.sm:pb-8`: padding 0 32px 32px at 640px and up; 0 16px 16px below 640px.
- `div[data-demo][role=img]`: relative, `aspect-ratio: 1440/820`, overflow hidden, radius 12px, 1px solid #e1e0da, bg #fcfcfb. Measured 1352×769.9 at 1440 (x 44), 1192×678.8 at 1280, 680×387.2 at 768, 342×194.8 at 390. aria-label: "The Shelf app. A sidebar lists collections, sources and tags with the number saved in each. The main panel offers a box to paste a link into and shows recent saves, each with the note written at the time. A search field, opened over the top, takes a question in plain language, shows the filters it read out of that question, and lists the saves that match."
- Inner `div[data-demo-scale]`: **fixed 1440×820**, `transform-origin: top left`, `transform: scale(container.clientWidth / 1440)`, updated by a ResizeObserver. Measured scales: 0.9375 (1440), 0.826389 (1280), 0.470833 (768), 0.236111 (390). Everything inside is laid out in unscaled px:
  - **Top bar:** flex, justify-between, items-center, h 64, border-bottom 1px #e1e0da, px 28. Left: `<img src=logo.svg>` 30×30. Right: flex gap 10px containing an avatar ("S", 32×32 grid, radius 8, bg #e9e8e3, 13px/19.5px, 500, #76766e) and "▾" (13px, #a5a59c).
  - **Body:** flex, h 756.
    - **Sidebar** `aside`: w 264, border-right 1px #e1e0da, padding 24px 16px.
      - ul (space-y 4px) of rows (flex, justify-between, radius 8, px 12, py 10, 15px/22.5px, #76766e). Each row has an 18×18 radius-4 square in rgba(198,196,189,.5), gap 12, then the label.
        - "Today"
        - "My shelf" (active row: bg #e9e8e3, weight 500, colour #1a1a18) with count "128"
        - "Favourites" with count "14"
        - Counts are 13px, #a5a59c.
      - Group "COLLECTIONS" (mt 32; label 12px/18px, uppercase, ls 0.6px (`tracking-wider` .05em), #a5a59c, px 12). Then ul mt 10, rows py 8 with truncate text: Website redesign 23, Brand refresh 11, New pitch 38.
      - Group "SOURCE" (mt 32): rows with an 8×8 round dot: LinkedIn (#2d64bc) 41, Instagram (#d6336c) 27, Web (#3fbf4a) 60.
    - **Main** (flex 1, padding 36px 40px):
      - "Good morning": `p.font-display`, 30px/37.5px, 600, no letter-spacing.
      - "Nine new saves this week, and four things came back from May.": mt 8, 16px/24px, #76766e.
      - Paste box `p`: mt 32, w 560, flex, gap 14, radius 12, **1px dashed #c6c4bd**, padding 16px 20px, 16px, #a5a59c. Contents: "+" · "Paste a link, or drop it here" (flex 1) · `<kbd>` "⌘V" 13px mono.
      - Block mt 40:
        - "Your last saves": `p.font-display` 20px/30px, 600.
        - "The most recent, straight from the extension": mt 4, 14px/21px, #a5a59c.
        - ul mt 20, flex, gap 16, of 4 cards (w 318, shrink-0, radius 16, bg #f2f1ed, p 16; the row overflows and is clipped). Each card has:
          - Meta row (flex, justify-between, 12px/18px, uppercase, ls .6px, #a5a59c) with a day in normal case and tracking.
          - Title (mt 12, 16px/22px, 500).
          - Note (mt 12, border-left 2px #9ee86f, pl 12, 14px/19.25px, #76766e).
          - Thumbnail block (mt 16, h 132, radius 8).
        - The cards:
          1. WEB / Today / "How Linear writes its changelog" / "The tone we want for release notes" / thumb #1c1c1a
          2. OTHER / Mon / "Neue Haas Grotesk specimen" / "The weights actually worth licensing" / thumb #e9e8e3
          3. LINKEDIN / Tue / "Why retainers beat project fees" / "Saved for the anchoring argument" / thumb #2d64bc
          4. WEB / Wed / "Stripe docs, the sidebar pattern" / "Three levels deep without getting lost" / thumb #e4e8f2
  - **Scrim** `div[data-demo-scrim]`: absolute inset 0, bg rgba(252,252,251,.45), opacity 0, transition opacity .3s. **Never activated by any script** (stays at 0). Include it inert.
  - **Hero palette** `div[data-demo-palette]`: absolute, top 60px, left 50%, translateX(-50%), w 845, pointer-events none. Contains the palette component (§3.3) with:
    - question "typography I saved about two weeks ago for the redesign"
    - variant: rounded-2xl (16px), shadow `0 18px 50px -24px rgba(26,26,24,.22)`, question row **without** a bottom border, chips row **with** border-top 1px #e1e0da
    - question text 20px/30px, caret h 24px
    - chips: "tag: typography", "saved 8 to 20 Aug" (bg #f2f1ed, #76766e), "Website redesign" (bg #e9e8e3, #1a1a18)
    - "My shelf" hits:
      - "Neue Haas Grotesk specimen" / "The weights actually worth licensing" / 28 Jul / thumb 52×38 #eae7df
      - "Blocky display type on a phone" / "Still readable at the smallest size" / 4 Aug / #e6e2ec
      - "Type scale for the redesign" / "Two sizes fewer than we have now, cleaner" / 11 Aug / #e4e8f2
    - Hit subtitles 14px/21px.
    - Footer rows: "Show all 12 results" + "Enter" (14px), then "Enter to see all · Tab to browse · Esc to close" (14px/21px).
    - **No `data-palette-keep`**, so chips and hits get `display: none` when closed. The palette is **77px tall when closed** (question row only) and **498px when open** (unscaled).

### 3.3 Palette component (shared by hero and #finding)

```
div[data-palette][data-palette-question=...][data-palette-animate] .overflow-hidden.border.border-border(#e1e0da 1px).bg-surface-raised(#fcfcfb)
  div.flex.items-center.px-8.py-6.gap-4   (padding 24px 32px, gap 16)  [+ border-b in #finding variant]
    svg magnifier 22×22 #76766e (stroke 2: circle cx11 cy11 r6.5 + path m16 16 4.5 4.5)
    span.min-w-0.flex-1.truncate (font 20px hero / 21px finding)
      span[data-palette-typed]
      span[data-palette-caret].ml-0.5.inline-block.w-px.translate-y-[4px].bg-text.opacity-0 (h 24px hero / 26px finding)
  div[data-palette-chips].flex.items-center.gap-3.px-8.py-4.transition-opacity.duration-300  (gap 12, padding 16px 32px; opacity .3s cubic-bezier(.4,0,.2,1))
    span "Searching" 14px/21px #76766e
    chips: span.rounded-lg(8px).text-[14px].px-3.5.py-2 (14px padding x, 8px y; 14px/21px) — first two bg #f2f1ed text #76766e, last bg #e9e8e3 text #1a1a18
  div[data-palette-hits].transition-opacity.duration-300
    div.border-t.px-8.pt-4.pb-2 (padding 16px 32px 8px)
      p "My shelf" 14px #76766e
      ul.mt-2 > li.flex.items-center.gap-4.py-3 (gap 16, py 12):
        span thumb (radius 6, size 52×38 hero / 56×40 finding)
        span.flex-1 > span.block 17px/25.5px 500 title + span.block.mt-0.5 subtitle (14px hero / 15px/22.5px finding, #76766e)
        span date 13px/19.5px #a5a59c
    p.flex.justify-between.bg-surface(#f2f1ed).px-8.py-4 17px/25.5px 500 "Show all N results" + span "Enter" (14/15px, 400, #a5a59c)
    p.flex.gap-8.border-t.px-8.py-3.5 (gap 32, padding 14px 32px) 14px (hero) / 15px (finding) #76766e: "Enter to see all" "Tab to browse" "Esc to close"
```

**Typing loop**, taken from the JS and confirmed by sampling the hero instance every 500ms:
- An IntersectionObserver with `threshold: .35` sets a `visible` flag. The loop polls every 400ms while the palette is not visible.
- Each cycle:
  1. Add class `is-open` and set caret `opacity: 1` (instant, no transition). Wait **700ms**.
  2. Type the question one character at a time, waiting `38 + Math.random()*40` ms per character (38–78ms).
  3. Wait **350ms**, then show chips: unless `data-palette-keep` is set, `display: ''`; then on the next rAF `opacity: 1` (with the .3s fade). Wait **300ms**, then show hits the same way. Wait **6500ms**.
  4. Remove `is-open`. Set chips and hits to `opacity: 0`; without keep, they get `display: none` after 320ms. Set caret opacity to 0. Wait **500ms**, clear the text, wait **1400ms**, and start the next cycle.
- With `prefers-reduced-motion: reduce`, show the full text, chips and hits immediately, with no loop.
- Measured on the hero: typing 55 characters took about 3.5s; the open state held for about 6.5s; the whole cycle took about 14s.
- The caret does not blink in the palettes. Only the `.caret` in the Saving step 3 blinks.

### 3.4 Funnel: "Why Shelf" sticky title, bookmark clip-path and falling tags

The bottom edge of the hero block is a scroll-driven polygon. JS writes `header.style.clipPath = path("…")` on every scroll (rAF-throttled) and on resize.

**Markup (inside the header, after the demo):**
```
div[data-funnel].funnel        height: calc(var(--notch) + var(--hold) + var(--gap))  (= 100svh: 900 @1440×900, 800 @1280×800); padding-top 3.5rem (56px)
  div.funnel-stick             height: var(--hold)   (652 @1440)
    div[data-funnel-trigger].sticky.top-[40%].-translate-y-1/2.px-6.text-center   (position: sticky; top: 40% of the viewport = 360px @900h; translate 0 -50%; px 24)
      p.reveal.mx-auto.w-fit  > span[data-squircle] eyebrow (accent pill): ask-icon svg 18px + "Why Shelf"
      p.reveal.mx-auto.mt-5.max-w-3xl.font-display.text-4xl.font-semibold.text-balance.sm:text-5xl > span.inline-block "You save all over the place"
      p.reveal.mx-auto.mt-5.max-w-xl.text-[17px].leading-relaxed.text-text-muted.text-pretty > span.inline-block "Every app has its own save button, and none of them talks to the next. What you keep ends up scattered over a dozen of them."
div[data-tags].tags.pointer-events-none.absolute.inset-0 (z-index: -2) — 12 span[data-tag].tag pills (sibling of .funnel, child of header)
```

- **Accent eyebrow pill** (used here, in #saving, and in the done tile): same box as the hero eyebrow (padding 6/14/6/10, radius 10, gap 6, 14px/21px, 600, ls -0.14px) but with bg #9ee86f and colour #1a1a18. Size 112.5×33 for "Why Shelf".
  - `.ask` icon animation: `animation: ask 2.8s ease-in-out infinite; transform-box: fill-box; transform-origin: center`.
    ```css
    @keyframes ask{0%,55%,100%{rotate:0deg;scale:1}18%{rotate:-16deg;scale:1.12}36%{rotate:12deg;scale:1.06}}
    ```
- **Title:** General Sans 600, 48px/48px (`sm:text-5xl`; 36px/40px below 640px). It is a `<p>`, so letter-spacing is normal. max-width 768, mt 20, balance. Measured 1440: 768×48, text span 592.1 wide. 390: two lines, 80 tall.
- **Body:** Switzer 17px/27.625px, #76766e, max-width 576, mt 20, pretty. Two lines at 1440 (55.3); four lines at 390.
- **Reveal:** each `p.reveal` has `overflow: hidden`. Its child starts at `translate: 0 115%` with `transition: translate .7s cubic-bezier(.22,1,.36,1)`; the 2nd `p` has delay .08s and the 3rd has .15s. When `[data-funnel-trigger]` gets `.is-in`, the children go to `translate: 0 0`. The bookmark script toggles `.is-in` on every frame as `hold >= 0.45` (see below), so it **reverses** when you scroll back up. Measured: at scrollY 1000 (1440×900) it is not in; at 1200 it is in.
- Because the title is sticky at 40% of the viewport inside `.funnel-stick` (height = hold), it stays pinned while the bottom edge travels. The hero palette and demo scroll up past it.

**Bookmark geometry** (port verbatim; the original source is in the bundle as `et()` and `B()`):
```js
const ease = cubicBezier(.45,0,.55,1);           // Newton/bisection solver as in the bundle
const cssNum = (el, v, fb) => { const n = parseFloat(getComputedStyle(el).getPropertyValue(v)); return Number.isFinite(n) ? n : fb };
function measure(el){                            // el = header[data-bookmark]
  const {width:W, height:H, top} = el.getBoundingClientRect(); if(!W||!H) return null;
  const notch = cssNum(el,'--notch',96), hold = cssNum(el,'--hold',180);
  const line = innerHeight*0.7, a = H - hold;
  const holdP = clamp01((line - top + notch - a)/hold);      // 0→1 while the edge is "held"
  const base  = a + hold*holdP;
  const n     = line - top - (H - notch);
  const tipP  = clamp01(n/notch);
  const bendP = clamp01(n/cssNum(el,'--bend',620));
  return { width:W, height:H, sideY: base - notch*ease(bendP), tipY: base - notch + notch*tipP, hold: holdP };
}
// path: rectangle top, bottom edge = two straight lines from (0,sideY) → (W/2,tipY) → (W,sideY), corners rounded with quadratic curves of radius s=min(--corner, sideY, W/2)
function pathD(w, corner, sideY, tipY){
  const L={x:0,y:sideY}, R={x:w,y:sideY}, T={x:w/2,y:tipY}, s=Math.min(corner, sideY, w/2);
  const toward=(p,q,d)=>{const dx=q.x-p.x,dy=q.y-p.y,len=Math.hypot(dx,dy)||1,u=Math.min(d/len,.5);return{x:p.x+dx*u,y:p.y+dy*u}};
  const e=toward(R,T,s), i=toward(T,R,s), o=toward(T,L,s), f=toward(L,T,s);
  return `M 0 0 H ${w} V ${sideY-s} Q ${R.x} ${R.y} ${e.x} ${e.y} L ${i.x} ${i.y} Q ${T.x} ${T.y} ${o.x} ${o.y} L ${f.x} ${f.y} Q ${L.x} ${L.y} 0 ${sideY-s} Z`;
}
// on scroll/resize (rAF-throttled): header.style.clipPath = `path("${pathD(m.width, cssNum(header,'--corner',56), m.sideY, m.tipY)}")`; trigger.classList.toggle('is-in', m.hold >= .45)
```
The path is relative to the header box (W = 1416 at 1440).

**Shape over time:**
- At rest the bottom edge is an **upward-pointing chevron**: sides at `H − hold`, the tip `notch` px higher, in the middle.
- While held, the chevron moves down with the scroll, so it stays still on screen.
- Then it **inverts into a downward-pointing V** (bookmark tail) whose tip ends exactly at the header bottom (tipY = H) and whose sides end at H − notch.

Clip-path samples at 1440×900 (W=1416, H=2378, notch 216, hold 652):

| scrollY | path (sideY = `V`+56, tip = middle Q y) |
|---|---|
| 0–700 | `M 0 0 H 1416 V 1669.99 Q 1416 1725.99 1362.44 1709.65 L 761.563 1526.33 Q 708 1509.99 654.437 1526.33 L 53.5627 1709.65 Q 0 1725.99 0 1669.99 Z` (sides 1726, tip 1510) |
| 1000 | sides 1846, tip 1630 |
| 1200 | sides 2046, tip 1830 |
| 1500 | sides 2346, tip 2130 |
| 1600 | sides 2373.4, tip 2230 |
| 1700 | sides 2347.18, tip 2330 (nearly flat) |
| 1800 | sides 2296.21, tip 2377.99 (V pointing down) |
| 1900 | sides 2234.25, tip 2378 |
| 2000 | sides 2186.89 |
| 2100 | sides 2164.63 |
| ≥2200 | final: `M 0 0 H 1416 V 2105.99 Q 1416 2161.99 1362.44 2178.33 L 761.563 2361.65 Q 708 2377.99 654.437 2361.65 L 53.5627 2178.33 Q 0 2161.99 0 2105.99 Z` |

Reference screenshots (not deliverables): `.playwright-mcp/shot-1440-funnel-1250.png` shows the upward chevron; `.playwright-mcp/shot-1440-funnel-1400.png` shows the tags resting on it.

**Falling tags (matter-js):**
- 12 pills in DOM order: Instagram, LinkedIn, Web page, Voice note, Note, Screenshot, PDF, X post, YouTube, Newsletter, Article, Figma file. Icons are listed in the MANIFEST.
- Pill style:
  - `position: absolute; top: 0; left: 0; visibility: hidden; will-change: transform`, flex, items-center, rounded-full.
  - 1px #e1e0da border, bg #f2f1ed, colour #76766e, nowrap.
  - 640px and up: padding 14px 24px, gap 10px, font 1.375rem (22px/33px), size about 126–200×63 (Instagram 186.2×63).
  - Below 640px: padding 8px 12px, gap 6px, font .8rem (12.8px/19.2px), Instagram 105.4×37.2.
  - Icon size 1.15em.
- The whole tags container is `absolute inset-0` in the header with **z-index: -2**, so the pills render behind the text but inside the header's clip.
- Physics constants:
  - `Engine.create({enableSleeping:false})`, gravity.y **2.4** (falling) and **-3.2** (on release).
  - Floor: two static rectangles 240px thick whose top edges follow the clip path's two bottom lines: from (-24, sideY) to (W/2, tipY), and from (W/2, tipY) to (W+24, sideY). Their vertices are updated every frame via `Body.setVertices`. There are also side walls 240 wide outside x=0 and x=W.
  - Floor friction .6.
- Spawn (on start), with tags shuffled:
  - Rows start at x=24. Each tag goes at `x + w/2 + (rand-.5)*18`, then x advances by `w + 34`. Wrap to a new row when `x + w > W - 24`.
  - y = `funnel.offsetTop - 40 - row*(h+30) - rand*150`.
  - Body: `Bodies.rectangle(x, y, w, h, {chamfer:{radius:h/2}, restitution:.2, friction:.28, frictionStatic:.25, frictionAir:.055})`, angle `(rand-.5)*1` rad, angularVelocity `(rand-.5)*.26`, velocity `{x:(rand-.5)*6, y: rand*3}`.
  - Step `Engine.update(engine, min(32, dt))`. Render each tag: `el.style.visibility = 'visible'; el.style.transform = translate(${x-w/2}px, ${y-h/2}px) rotate(${angle}rad)`.
  - The loop sleeps when no body moves (speed < .05 and |angularSpeed| < .0015) and the shape is unchanged.
- Triggers, via a passive scroll listener that tracks direction (deltas over 2px):
  - Start when scrolling **down** and `hold >= .45`.
  - Release (gravity -3.2, each body gets velocity `{x:(rand-.5)*6, y:-(9+rand*7)}`, angular `(rand-.5)*.3`) when scrolling **up** with hold < .42, or whenever hold < .15.
  - Reset (hide all) when every live body is above the viewport (`headerTop + y < -h - 40`).
  - The first check runs 300ms after `load`. On resize: reset, then start again.
- Reduced motion: no simulation; tags are placed directly on the floor line.
- Measured: tags land on the two sloped floor lines around the tip (y about 1975–2120 in header coordinates at 1440, sampled at scrollY 1400). Positions are random on every run.

---

## 4. `section#finding`: "You can find them in one place now"

- `section#finding` > `div.mx-auto.max-w-4xl.px-6.pb-20.text-center.sm:pb-28`: max-width 896, padding 0 24px 112px (80px bottom below 640px). Height 921.5 at 1440. It starts directly at the header's bottom edge (y 2378), so the V tip points straight at the line.
- `div[data-reveal]` holds:
  1. **Line** `span.line.mx-auto.block.h-24.w-px.sm:h-32`: 1px wide, 96px tall below 640px and 128px at 640px and up. `background-image: linear-gradient(to bottom, transparent, #c6c4bd)`.
     - Animation: `transform-origin: top; scale: 1 0; transition: scale .8s cubic-bezier(.45,0,.55,1)` → `.is-in` gives `scale: 1 1`. The line grows down from the funnel tip.
  2. **h2.reveal** "You can find them in one place now": mt 32, max-width 768, General Sans 600, 48px, line-height 1.1 (52.8px), ls -1.44px. Below 640px: 36px/39.6px, ls -1.08px. Balance. One line at 1440 (span 743.8 wide); two lines at 768; two at 390.
  3. **p.reveal**: mt 20, max-width 576, 17px/27.625px, #76766e, pretty. "Shelf catches all twelve of them. Ask in the same words you would use out loud, and it answers with what you saved, and why you saved it."
  - Reveal mechanics: the h2 and p have `overflow: hidden`, and their inner `span.inline-block` starts at `translate: 0 115%`, `transition: translate .7s cubic-bezier(.22,1,.36,1)`. On `.is-in`, the h2 span has **delay .32s** and the p span has **delay .42s**, so the line grows first and the text follows.
  - Trigger: an IntersectionObserver with `rootMargin: "0px 0px -32% 0px"` adds `.is-in` when intersecting. When it stops intersecting, it adds `.no-anim` (transition: none), removes `.is-in`, and removes `.no-anim` on the next rAF. So it resets **instantly** when scrolled out (below the bottom 32% or above the top) and replays.
- **Palette #2** (§3.3 component), mt 56, `text-left`, radius **1.25rem (20px)**, **no shadow**, `data-palette-keep` (height stays constant: 848×465.5 at 1440; 342×698 at 390 where the text wraps).
  - Question row has `border-b` 1px #e1e0da (height 83.5); chips row has no top border.
  - Question font 21px/31.5px, caret 1px×26px.
  - Question text: "Every LinkedIn post about Webflow pricing I saved".
  - Chips: "source: LinkedIn", "topic: pricing" (#f2f1ed/#76766e), "Webflow" (#e9e8e3/#1a1a18).
  - Hits (thumbs 56×40, radius 6):
    1. "Why Webflow's per-site pricing breaks agency retainers" / "LinkedIn, saved for the anchoring argument in the client deck" / 12 Aug / thumb #e8effa
    2. "webflow.com/pricing" / "Web, saved while comparing the Growth and Agency tiers" / 3 Aug / thumb #e9e8e3
  - Subtitles 15px/22.5px.
  - "Show all 9 results" (17px/25.5px, 500, bg #f2f1ed, padding 16px 32px) with "Enter" (15px, 400, #a5a59c).
  - Hint row 15px/22.5px #76766e, gap 32, padding 14px 32px, border-top.
  - Chips and hits start at `opacity: 0` and fade in on each typing cycle (.3s).

---

## 5. `section#saving`: "Save it where you found it."

- `section#saving.px-2.sm:px-3` > `div[data-squircle].mx-auto.max-w-[1440px].rounded-[2rem].bg-surface-raised`
  - Radius 32px (squircle-clipped), bg #fcfcfb.
  - Padding 96px 40px at 640px and up; 80px 24px below 640px.
  - Height 624 at 1440 and 1280; 971.3 at 768; 1324.3 at 390.
- Inner grid `div.mx-auto.grid.max-w-6xl.items-center.gap-14.lg:grid-cols-2.lg:gap-20`: max-width 1152; at 1024px and up 2 columns (536px + 536px) with gap 80; below 1024px 1 column with gap 56. `align-items: center`.
- **Left column** (536×347.4 at 1440, vertically centred):
  - Accent eyebrow pill (`p.flex` > span): inbox-tray icon 18px + "Getting things in" (150.1×33).
  - **h2** "Save it where you found it.": mt 24, General Sans 600. 52px/56.16px (`sm:text-[3.25rem]`, leading 1.08), ls -1.56px; below 640px 36px/38.88px, ls -1.08px. Balance. At 1440 it breaks into 2 lines ("Save it where" / "you found it."); 1 line at 768.
  - p mt 24, max-width 512, 17px/27.625px, #76766e, pretty: "A button in your browser for the web, the share sheet on your phone. Three seconds, and you are back to what you were doing."
  - p mt 16, same style: "What you already have comes along too. Your bookmarks and saved posts import in one go, so you are not starting from an empty shelf."
- **Right column** `ol.space-y-3` (12px between items), 536 wide. Three `li[data-squircle]`, each:
  - flex, bg #f2f1ed, radius 24px (squircle).
  - 640px and up: row, items-center, gap 24, padding 20 (136px tall at 1440).
  - Below 640px: column, items-start, gap 16, padding 16.
  - Contents: visual box `h-24 w-full sm:w-44` (176×96 at 640px and up, full width below), radius 16, bg #fcfcfb. Then a text div:
    - `p.flex.items-center.gap-2.5` containing a number badge (30×30 grid, radius 10px squircle, bg #1a1a18, text #f2f1ed, 14px/21px, 600, tabular-nums) and a title (Switzer 20px/27.5px, 500).
    - Description: mt 10, 14px/22.75px (leading-relaxed), #76766e, pretty.
  1. **"You find a gem"**: "Halfway down a feed, in a message, or an idea that turns up on the walk home."
     - Visual: `div.feed` with overflow hidden and `mask-image: linear-gradient(transparent, #000 22%, #000 78%, transparent)`.
     - Inside, `span.feed-strip.block.space-y-2.px-3.py-3` (padding 12, 8px between rows) holds 6 rows. Each row is flex, gap 8: a 28×28 square (radius 6) plus two bars (space-y 6px, h 6px, rounded-full; first bar rgba(198,196,189,.6), second rgba(198,196,189,.4)).
     - Row squares and bar widths, in order:
       - #efe3d6, full / 60%
       - #dfe4ee, 80% / 40%
       - #e2ded4, full / 50%
       - then the same three again
     - **Marquee:** `.feed-strip { animation: scroll-feed 9s linear infinite }` with `@keyframes scroll-feed { to { translate: 0 -108px } }`. 108px = 3 rows × (28 + 8). It scrolls up seamlessly in a loop.
  2. **"One tap to save"**: "The browser button, or Shelf in the share sheet."
     - Visual: a centred grid. Inside, a `relative grid` holds:
       - `span.tap.absolute.size-14.rounded-full` (56×56, bg rgba(158,232,111,.45)) with `animation: tap 2.6s ease-out infinite`.
       - A 48×48 tile (radius 11px squircle, bg #1a1a18) containing `<img src=/assets/logo.svg>` 24×24 with `filter: brightness(0) invert(1)`.
     - ```css
       @keyframes tap{0%,55%,100%{scale:.62;opacity:0}12%{scale:.62;opacity:1}45%{scale:1.15;opacity:0}}
       ```
  3. **"One line about why"**: "Written while it is still in your head. That line is what finds it back."
     - Visual: flex column, justify-center, px 14.
       - "WHY THIS": 10px/15px, uppercase, ls .5px, #a5a59c.
       - Below it (mt 6): border-left 2px #9ee86f, pl 10, 13px/17.875px, #1a1a18: "The empty state does the teaching", followed by `span.caret`.
     - `.caret{display:inline-block;width:1px;height:.95em;margin-left:1px;translate:0 .15em;background:currentColor;animation:blink 1.1s steps(1) infinite}` with `@keyframes blink{0%,50%{opacity:1}50.01%,100%{opacity:0}}`.
- Reduced motion: feed, tap and caret animations are set to none.

---

## 6. `section#faq`: "Before you ask"

- `section#faq.mx-auto.max-w-3xl.px-6.py-20.sm:py-28`: max-width 768, padding 112px 24px (80px vertical below 640px). Height 891.3 at 1440 with everything closed.
- Heading row: flex, centred, gap 12.
  - Tile 52×52 at 640px and up (44×44 below), radius 15px (13px below), bg #9ee86f, squircle. It holds the ask icon (28px at 640px and up, 24px below) with the `ask` animation.
  - **h2** "Before you ask": General Sans 600, 48px/48px, ls -1.44px (36px/40px, ls -1.08px below 640px).
- p mt 20, max-width 512, centred, 17px/27.625px, #76766e: "What people want to know before they hand over an archive they spent years building."
- `ul.mt-12.space-y-3`: mt 48, 12px between items, width 720.
- Each `li.item[data-squircle]`: overflow hidden, radius 20px (squircle), bg #fcfcfb.
  - `h3` > `button[data-faq][aria-expanded][aria-controls=faq-N]`:
    - flex, w-full, justify-between, items-center, gap 24, cursor pointer, text-left.
    - Padding 20px 20px 20px 32px (left 24 below 640px).
    - General Sans **500**, 18px/28px at 640px and up (16px/24px below), letter-spacing -0.48px (inherited from the h3). Height 72.
    - The button holds the question text and `span.icon`: 32×32 grid, radius 10 squircle, bg #f2f1ed, colour #76766e, transition colours 150ms std. Inside the icon is the plus svg 16px, stroke 2.2, with `transition: rotate .3s ease-out`.
  - `div#faq-N.panel`: `display: grid; grid-template-rows: 0fr; transition: grid-template-rows .75s var(--ease-bounce)`. Its child div has `overflow: hidden`. The panel holds a p: padding 0 32px 24px (0 24px 24px below 640px), 16px/26px at 640px and up (15px/24.375px below), #76766e, pretty.
  - **Open state** (`li.item.is-open`): `.panel { grid-template-rows: 1fr }`; `.icon { background: #9ee86f; color: #1a1a18 }`; `.icon svg { rotate: 45deg }`.
    - Measured: item 1 grows from 72px to 174px (panel 102px) at 1440.
  - JS: a click closes any other open item in the same list (setting `aria-expanded="false"`), then toggles this one. Clicking an open item closes it.
- Q&A copy, in order:
  0. **Which sources can Shelf pull from?** Bookmarks, LinkedIn saved posts, Instagram collections, X bookmarks and any web page you send it. Your own notes count as a source too, often the most useful one, because that is where the why lives.
  1. **Do I have to tag everything?** No. Tagging is the reason most swipe files die. Shelf reads what you saved and takes the note you wrote at the moment you saved it, and that is enough to find it back later.
  2. **What happens to the archive I already have?** You import it. The point of Shelf is not to start a sixth silo. It is to make the five you already have searchable from one field.
  3. **Who can see what I save?** Only you. A swipe file is competitive material, and a private one is the only kind worth keeping.
  4. **What will it cost?** Not settled yet. Shelf is built for people who save professionally, and the price will reflect that rather than chase the free-app crowd. Waitlist members hear it first.
  5. **When can I use it?** Shelf is in private testing. The waitlist is in order, and we widen it as fast as the import can keep up.

---

## 7. Closing waitlist (`section.px-2.sm:px-3`, no id, no top margin)

- `div[data-blocks].mx-auto.flex.max-w-[1440px].gap-2.sm:gap-3`: gap 12px (8 below 640px). Height 453.6 at 640px and up; 404.7 at 390.
- Three blocks, all bg #9ee86f, radius **28px** (1.75rem), squircle:
  - `div.side.left.hidden.lg:block.shrink-0` (aria-hidden)
  - `div.min-w-0.flex-1` (content): padding 112px 56px at 640px and up, 80px 32px below.
  - `div.side.right.hidden.lg:block.shrink-0` (aria-hidden)
  - The side blocks are shown only at 1024px and up.
- **Side block animation:**
  - Base: `.side { transition: flex-basis .7s cubic-bezier(.45,0,.55,1) }`, `.left { flex-basis: calc(50% - 360px - 8.75rem) }` (= 50% − 500px), `.right { flex-basis: 20% }`.
  - On `[data-blocks].is-in`: `.side { transition: flex-basis 1.1s var(--ease-bounce) }`, `.left { flex-basis: calc(50% - 360px - .75rem) }` (= 50% − 372px), `.right { flex-basis: 9%; transition-delay: .1s }`.
  - Measured at 1440: before, widths 208 / 900.8 / 283.2; after, **336 / 929 / 127**. At 1280 before: 128 / 852.8 / 251.2.
  - The left block grows and the right block shrinks with a springy overshoot, so the green middle panel shifts right.
  - Trigger: an IntersectionObserver with `rootMargin: "0px 0px -15% 0px"` adds `.is-in` and removes it when not intersecting (no no-anim, so it animates back with the .7s ease).
  - Reduced motion: final values, no transition.
- Content:
  - **h2** "Join the waitlist": max-width 672, General Sans 600, 48px, line-height 1.05 (50.4px), ls -1.44px (36px/37.8px below 640px).
  - p mt 20, max-width 512, 17px/27.625px, colour **rgba(26,26,24,.7)**: "Shelf is in private testing. The list moves in order, and members hear the price before anyone else."
  - div mt 40 > `form#waitlist-closing`: same as the hero form, except it is **not centred** (left-aligned), has **no border** (64px tall), and uses `focus-within: box-shadow 0 0 0 1px rgba(26,26,24,.6)` (ring-1 text/60). Then the done card `#waitlist-closing-done` and note `#waitlist-closing-note` (colour rgba(26,26,24,.7)).

---

## 8. Footer

- `footer.px-2.pt-2.sm:px-3.sm:pt-3`: padding 12px 12px 0 (8px below 640px). It sits directly under the green block.
- Inner `div.mx-auto.flex.max-w-[1440px]`: bg #fcfcfb, radius 32px 32px 0 0 (top only).
  - Padding 32px 48px at 640px and up (32px 32px below).
  - 640px and up: row, justify-between, items-center. Below 640px: column, items-start, gap 12. Height 84 (136 at 390).
  - Left `p.flex.items-center.gap-2`: 14px/20px, #a5a59c. Contents: `<img src=/assets/logo.svg>` 18×18 followed by "© 2026 Shelf. Bookmarks with a Brain. All rights reserved."
  - Right p: "savetoshelf.com" (14px/20px, #a5a59c, not a link).

---

## 9. Motion index (everything that moves)

| element | trigger | property | from → to | duration / easing / delay |
|---|---|---|---|---|
| h1 `.mark-fill` | load | scale | `0 1` → `1 1` (origin left) | .95s cubic-bezier(.625,.05,0,1), delay .25s, forwards |
| eyebrow `.spark-big` | loop | scale / rotate | 1/0 → .68/-32deg at 50% | 2.4s ease-in-out infinite |
| eyebrow `.spark-small` | loop | scale / opacity | .72/.45 → 1.45/1 at 45% | 2.4s ease-in-out, delay .35s, infinite |
| `.ask` icons (Why Shelf, FAQ) | loop | rotate / scale | 0 → -16deg/1.12 (18%) → 12deg/1.06 (36%) → 0 (55–100%) | 2.8s ease-in-out infinite |
| nav bar | scrollY > 12 | max-width, box-shadow | 896 → 736; none → 0 0 0 1px rgba(225,224,218,.55) | .6s cubic-bezier(.32,.72,0,1); shadow .4s ease-out |
| nav links | hover | color | #1a1a18 → #76766e | .15s cubic-bezier(.4,0,.2,1) |
| logo books | hover | rotate | 0 → -54 / -44 / -35deg | .5s cubic-bezier(.34,1.4,.64,1), delays .1 / .05 / 0s |
| Button 009 | hover | translate / opacity | text +16px; arrows swap | .5s cubic-bezier(.32,.72,0,1), 50–75ms delays; opacity .15s ease-out |
| Button 009 | active | scale | 1 → .955 .925 | .15s cubic-bezier(.4,0,.2,1) |
| form submit | hover | filter | brightness(1) → 1.25 | none (filter is not in the transition-colors list) |
| hero form | focus-within | border-color | #e1e0da → #76766e | .15s std |
| palettes | in view (threshold .35) | typing loop | see §3.3 | chips/hits opacity .3s cubic-bezier(.4,0,.2,1) |
| header clip-path | scroll | clip-path path | see §3.4 | rAF per scroll, no CSS transition |
| funnel `.reveal` spans | hold ≥ .45 (reversible) | translate | 0 115% → 0 0 | .7s cubic-bezier(.22,1,.36,1); delays 0 / .08 / .15s |
| tags | hold ≥ .45 scrolling down | matter-js | fall and pile on the V floor | gravity 2.4; release −3.2 |
| #finding line | IO rootMargin −32% bottom | scale | 1 0 → 1 1 (origin top) | .8s cubic-bezier(.45,0,.55,1) |
| #finding h2 / p | same IO | translate | 0 115% → 0 | .7s cubic-bezier(.22,1,.36,1), delays .32s / .42s; instant reset when out |
| feed strip | loop | translate | 0 → 0 -108px | 9s linear infinite |
| tap ripple | loop | scale / opacity | see keyframes | 2.6s ease-out infinite |
| caret | loop | opacity | steps(1) blink | 1.1s infinite |
| FAQ panel | click | grid-template-rows | 0fr → 1fr | .75s var(--ease-bounce) |
| FAQ icon | click | bg, colour; svg rotate | #f2f1ed/#76766e → #9ee86f/#1a1a18; 0 → 45deg | colours .15s std; rotate .3s ease-out |
| closing side blocks | IO rootMargin −15% bottom | flex-basis | left 50%−500px → 50%−372px; right 20% → 9% | in: 1.1s ease-bounce (right +.1s); out: .7s cubic-bezier(.45,0,.55,1) |
| waitlist done card | after submit | opacity, translate | 0 / 8px → 1 / 0 | .5s ease-out / .6s cubic-bezier(.22,1,.36,1) |
| tick | done `.is-in` | stroke-dashoffset | 24 → 0 | .45s ease-out, delay .15s |
| page | wheel | smooth scroll | Lenis lerp .1 | anchors offset −100 |

All of these have `prefers-reduced-motion: reduce` fallbacks that show the final state with no transition. There are no hover effects on cards or FAQ items besides the cursor.

---

## 10. Breakpoint behaviour summary

| | 1440 | 1280 | 768 | 390 |
|---|---|---|---|---|
| nav padding / height | 12 / 76 | 12 / 76 | 12 / 76 | 8 / 72 |
| nav bar width (rest) | 896 | 896 | 744 | 374 |
| nav links | shown | shown | shown | **hidden** (logo and CTA only; no hamburger) |
| header width | 1416 | 1256 | 744 | 374 |
| hero section padding top / bottom | 96 / 80 | 96 / 80 | 96 / 80 | 64 / 64 |
| h1 size | 84px | 84px | 65.28px (8.5vw) | 44px (min) |
| hero p | 2 lines | 2 lines | 2 lines | 3 lines (br hidden) |
| demo box | 1352×770, scale .9375 | 1192×679, .8264 | 680×387, .4708 | 342×195, .2361; wrapper padding 16 |
| --notch / --corner / --hold | 216 / 56 / 652 | 192 / 56 / 576 | 115.2 / 56 / 876.8 | 120 / 20 / 692 |
| funnel title | 48px | 48px | 48px | 36px, 2 lines |
| tag pills | 22px font, padding 14×24 | same | same | 12.8px, padding 8×12 |
| #finding h2 | 48px, 1 line | 1 line | 48px, 2 lines | 36px |
| saving grid | 2 columns 536 / 536, gap 80 | 2 columns | 1 column, gap 56 | 1 column; step cards stack vertically, padding 16 |
| saving card padding | 96 / 40 | 96 / 40 | 96 / 40 | 80 / 24 |
| FAQ section padding | 112 | 112 | 112 | 80; button pl 24, 16px text |
| closing blocks | 3 blocks (sides visible) | 3 blocks | middle only | middle only, padding 80 / 32, gap 8 |
| footer | row | row | row | column, padding 32 |
| doc height | 5364 | 5173 | 5467 | 5553 |

---

## 11. Not measurable / caveats

- I did not submit the `/api/waitlist` POST (doing so creates a real signup). The success and error UI states come from the JS and CSS, not from a live run.
- Tag pile positions are random on every page load (shuffle plus random offsets), so no fixed coordinates exist.
- Lenis smooth scroll is visible only with real wheel input. Programmatic scroll sampling bypasses it.
- The hero `[data-demo-scrim]` is never toggled by any shipped script. It stays at opacity 0.
