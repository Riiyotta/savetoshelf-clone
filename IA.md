# https://www.savetoshelf.com/

Source: https://www.savetoshelf.com/ · React 18 + Vite + Tailwind v3 clone in this folder (original is Astro + Tailwind v4)
Status: **measured-from-live-site** · production approved: **false**
1 routes · 1 templates · 9 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 1 template (Homepage (single-page site)) accounts for 1 of 1 routes (100%). The remaining 0 routes span 0 templates.

| template | routes | share |
|---|---:|---:|
| Homepage (single-page site) | 1 | 100% |

## Page chrome

**1 routes carry chrome = `full`** — Homepage (single-page site).

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `chrome.floating-nav` | CHROME | 1 | 1 | `src/components/Nav.jsx` | Present on the only route, the homepage. |
| `hero.intro` | HERO | 1 | 1 | `src/components/Hero.jsx (+ WaitlistForm.jsx variant=hero, Eyebrow.jsx)` | Present on the only route, the homepage. |
| `hero.demo-mockup` | HERO | 1 | 1 | `src/components/HeroMockup.jsx (+ Palette.jsx)` | Present on the only route, the homepage, directly under the hero intro. |
| `story.why-funnel` | STORY | 1 | 1 | `src/components/Funnel.jsx + src/lib/bookmark.js` | Present on the only route, the homepage, as the tail of the hero header. |
| `story.finding` | STORY | 1 | 1 | `src/components/Finding.jsx (+ Palette.jsx keep mode)` | Present on the only route, the homepage. |
| `story.saving-steps` | STORY | 1 | 1 | `src/components/Saving.jsx` | Present on the only route, the homepage. |
| `support.faq` | SUPPORT | 1 | 1 | `src/components/Faq.jsx` | Present on the only route, the homepage. |
| `conversion.closing-waitlist` | CONVERSION | 1 | 1 | `src/components/Waitlist.jsx (+ WaitlistForm.jsx variant=closing)` | Present on the only route, the homepage, directly before the footer. |
| `chrome.footer` | CHROME | 1 | 1 | `src/components/Footer.jsx` | Present on the only route, the homepage. |

**0 shared sections** appear in more than one template and belong in a component library.

**9 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

## Templates

### Homepage (single-page site) — `template.home`

1 route · `/` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | CHROME | `chrome.floating-nav` | page-local |
| 2 | HERO | `hero.intro` | page-local |
| 3 | HERO | `hero.demo-mockup` | page-local |
| 4 | STORY | `story.why-funnel` | page-local |
| 5 | STORY | `story.finding` | page-local |
| 6 | STORY | `story.saving-steps` | page-local |
| 7 | SUPPORT | `support.faq` | page-local |
| 8 | CONVERSION | `conversion.closing-waitlist` | page-local |
| 9 | CHROME | `chrome.footer` | page-local |

## Section reference

### CHROME

_Page frame that sits outside the story: floating navigation and the footer._

**`chrome.floating-nav`** — Fixed, floating pill navigation: Shelf logo (books tip over on hover), anchor links to the in-page sections, and a Join waitlist button with an arrow-swap hover. Shrinks in width and gains a thin ring once the page scrolls past 12px.

· Present on the only route, the homepage. · appears on 1 routes · implemented by `src/components/Nav.jsx`

**`chrome.footer`** — Raised panel with top-only rounded corners sitting under the closing green block: small logo plus copyright line on the left, the plain-text domain (not a link) on the right. Row from 640px up, stacked below.

· Present on the only route, the homepage. · appears on 1 routes · implemented by `src/components/Footer.jsx`

### HERO

_Opening, above-the-fold block: the headline pitch and the product demo it introduces._

**`hero.intro`** — Headline block: eyebrow pill with twinkling sparks, h1 whose highlighted word gets a green sweep on load, supporting line, and the first waitlist email form (anchor #waitlist). Sits inside the header whose bottom edge is the scroll-driven bookmark shape.

· Present on the only route, the homepage. · appears on 1 routes · implemented by `src/components/Hero.jsx (+ WaitlistForm.jsx variant=hero, Eyebrow.jsx)`

**`hero.demo-mockup`** — Non-interactive fake Shelf app UI rendered at a fixed 1440x820 and scaled to the container width, with an auto-typing search palette overlaid on it. Thumbnails are flat CSS colour blocks, not images.

· Present on the only route, the homepage, directly under the hero intro. · appears on 1 routes · implemented by `src/components/HeroMockup.jsx (+ Palette.jsx)`

### STORY

_Scroll-driven narrative explaining the problem and how Shelf finds and saves things._

**`story.why-funnel`** — The header's bottom edge flips from an upward chevron into a downward V as you scroll; a sticky 'Why Shelf' title reveals and source-tag pills (Instagram, LinkedIn, PDF, YouTube and others) drop into the V under matter-js physics, then fly back out when scrolling up. Tag landing positions are random each run.

· Present on the only route, the homepage, as the tail of the hero header. · appears on 1 routes · implemented by `src/components/Funnel.jsx + src/lib/bookmark.js`

**`story.finding`** — Section #finding: a gradient line grows down from the V's tip, then a heading and line of copy reveal, followed by a second auto-typing search palette that keeps its results shown between loops.

· Present on the only route, the homepage. · appears on 1 routes · implemented by `src/components/Finding.jsx (+ Palette.jsx keep mode)`

**`story.saving-steps`** — Section #saving: raised rounded panel, two columns from 1024px up, with an intro on one side and three numbered step cards (find, tap to save, write why), each with its own small looping visual: scrolling feed, tap ripple, blinking caret.

· Present on the only route, the homepage. · appears on 1 routes · implemented by `src/components/Saving.jsx`

### SUPPORT

_Objection handling and answers to common questions._

**`support.faq`** — Section #faq: centred heading with an animated question icon above a six-item accordion. Only one item open at a time; panels open with a springy linear() easing and the plus icon rotates 45 degrees.

· Present on the only route, the homepage. · appears on 1 routes · implemented by `src/components/Faq.jsx`

### CONVERSION

_Closing call to action that asks the visitor to join the waitlist._

**`conversion.closing-waitlist`** — Closing call to action: three green blocks whose widths spring into place when scrolled into view, with the second waitlist email form in the centre block. The side blocks are hidden below 1024px.

· Present on the only route, the homepage, directly before the footer. · appears on 1 routes · implemented by `src/components/Waitlist.jsx (+ WaitlistForm.jsx variant=closing)`
