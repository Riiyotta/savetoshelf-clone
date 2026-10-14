# Shelf homepage design-repo

A machine-validated PageSpec system for the savetoshelf.com homepage clone. An
LLM can use it to compose on-brand page specs without inventing colours, copy
budgets, sections or motion.

Status: **design-review-pending**, `productionApproved: false`. Built 2026-10-14
per the design-repo-extraction skill (BUILD-GUIDE + MASTER-GUIDE §3/§4).

## What the source is

- **One route, one template.** The live site is a single page (`/`). No sitemap or
  robots.txt exists, common paths return 404, and the original JS references no
  other page. `/api/waitlist` is a POST endpoint, not a page. Do not invent pages.
  In-page anchors: `#waitlist` (hero form), `#finding`, `#saving`, `#faq`.
- **Original:** Astro (static) + Tailwind v4.3.3, Lenis 1.3.26, matter-js 0.20.0,
  inlined figma-squircle. **Clone:** React 18.3.1 + Vite 5.4.21 + Tailwind 3.4.19
  (resolved; package.json ranges are cited in `extraction/measured-values.json`).
- **Ids** (sections, categories, template `template.home`) come verbatim from the
  sibling `ia.json`. `verify_all.py` re-checks parity when that file is present.

## Layout

```
registry.manifest.json   status, counts (recomputed by verify_all), entryPoints (inside this folder only)
tokens/00-foundation/    color, typography, radius, spacing, breakpoint, elevation, icon-size, motion
tokens/10-semantic/      semantic aliases -> foundation
tokens/20-component/     component-scoped aliases
tokens/30-layout/        page/container/bookmark/demo layout tokens
tokens/themes/light.json every semantic token resolved (the only theme; the original has no dark mode)
tokens/llm/              component-allowlist.json, token-catalog.json, token-policy.json
assets/asset-roles.json  closed asset-role vocabulary + generation/licensing policy + pinned roles
primitives/ components/  atomic and composed contracts (props, tokens, evidence)
sections/                one contract per real section type (content schema with x-maxWords, constraints, motion, responsive)
templates/templates.json route inventory + template.home node list (structured nodes)
compatibility/graph.json rhythm/position/policy rules with severity error|warn
schema/                  pagespec.schema.json (draft-07, closed), example.pagespec.json, semantic_validate.py, tests/adversarial_test.py
extraction/              measured-values.json (citations + QA corrections + histograms), verify_all.py, prove_drift.py
```

## Counts (recomputed from disk; verify_all.py fails if these drift)

- sections: 9
- primitives: 13
- components: 8
- templates: 1
- routes: 1
- foundationTokens: 143
- semanticTokens: 19
- componentTokens: 46
- layoutTokens: 21
- themes: 1
- graphRules: 20
- assetRoles: 8
- citations: 381
- files: 58

allowlistVersion 1.0.0 (machine-checked against `tokens/llm/component-allowlist.json`).
`repositoryVersion` and `pageSpecVersion` are documentation-only markers (see
`versionFieldNote` in the manifest).

## Page shape (template.home)

| # | section | category | group | signature motion | reduced-motion fallback |
|---|---|---|---|---|---|
| 1 | chrome.floating-nav | chrome | chrome | nav-stuck-shrink | instant-stuck-state-no-transition |
| 2 | hero.intro | hero | bookmarkHeader | mark-fill-sweep | mark-fill-full-sparks-still |
| 3 | hero.demo-mockup | hero | bookmarkHeader | static-scaled-canvas + palette-autotype | palette-full-text-chips-hits-no-loop |
| 4 | story.why-funnel | story | bookmarkHeader | bookmark-clip-scroll + matter-js-tag-drop | tags-placed-on-floor-no-physics |
| 5 | story.finding | story | main | line-grow-text-reveal + palette-autotype | line-and-text-shown-palette-full-no-loop |
| 6 | story.saving-steps | story | main | feed-marquee / tap-pulse / caret-blink | feed-tap-caret-animation-none |
| 7 | support.faq | support | main | accordion-linear-bounce | panel-toggles-instantly |
| 8 | conversion.closing-waitlist | conversion | main | flex-basis-spring | side-blocks-at-final-flex-basis |
| 9 | chrome.footer | chrome | chrome | static | static-no-motion |

Each node's motion is **const-locked** per section in the schema
(`definitions.motion.<id>`) and re-checked against the section contract by
`SIGNATURE_MOTION_LOCKED`. A signature effect cannot silently degrade to a
generic fade, and a fallback cannot be swapped for another section's.

## Structurally unusual things (documented, not normalised away)

1. **Single route, single template.** Nothing else exists to template.
2. **Live endpoint.** The original form POSTs `{email}` to the live `/api/waitlist`
   (a real signup). The clone stubs it (`src/components/WaitlistForm.jsx`).
   In a PageSpec, `submitTarget` only accepts `local-stub`. `endpointPolicy` must
   equal the pinned `must-not-reuse-live-endpoint`, and a different but still valid
   enum value is rejected (`ENDPOINT_POLICY_PINNED`; adversarial T12/T13; drift-proof
   in `prove_drift.py`).
3. **Real, live company.** The Shelf books logo, app icons and third-party brand
   tag icons (Instagram, YouTube, Figma, X, LinkedIn) are
   `must-not-reproduce-real-brand`. Generated pages (`purpose: "generated"`) must
   use `brand.placeholder-mark` and `icon.source-generic`
   (`GENERATED_NO_REAL_BRAND_ASSETS`, error), and should avoid the real name/domain
   (`GENERATED_NO_REAL_BRAND_TEXT`, warn). The Plausible analytics script is
   intentionally excluded.
4. **No raster content.** Mockup and palette thumbnails are CSS colour blocks
   (`mockup.thumbnail-color-block`, `css-color-block-only`). No photo role exists.
5. **Bookmark header.** hero.intro, hero.demo-mockup and story.why-funnel share one
   `header[data-bookmark]` whose bottom edge is a scroll-driven clip-path, and the
   tags' physics floor follows it. They are locked in order
   (`BOOKMARK_HEADER_SEQUENCE`), and story.finding must follow because its line
   grows from the bookmark tip.
6. **Non-deterministic physics.** Tag shuffle, jitter and velocities use
   `Math.random`. Settle time (~4–5 s) and resting positions vary run-to-run on
   both sites, so no contract claims fixed positions or timings.
7. **Nav CTA targets the hero form**, not the closing waitlist (which has no id).
8. **ia.json categories create real same-category adjacencies** (hero→hero,
   story→story ×2). They are handled by named exceptions on
   `NO_ADJACENT_SAME_CATEGORY`, and `ONE_HERO` treats hero.demo-mockup as the hero's
   companion.

## How to use

```bash
python3 schema/semantic_validate.py [spec.json]   # schema + semantic rules; exit 1 on errors
python3 schema/tests/adversarial_test.py          # every mutation rejected, every control passes
python3 extraction/verify_all.py                  # repo integrity gate (citations WARN when standalone)
python3 extraction/prove_drift.py                 # proves verify_all's drift checks fail on injected drift
```

Requires Python 3 + `jsonschema` (Draft7Validator). All scripts derive paths from
`__file__`, and none references machine-specific paths.

## Citation hand-check

The generator and `verify_all.py` check that each quoted substring appears inside
its cited range. On top of that, this sample was re-read by hand to confirm the
lines describe what the contract claims:
`src/index.css:283` (FAQ grid-rows .75s ease-bounce),
`src/index.css:296-299` (closing side-block flex-basis before/after),
`src/components/Faq.jsx:29-30` (single-open accordion),
`src/lib/bookmark.js:260-265` (reduced motion places tags on the floor),
`src/components/Waitlist.jsx:30` (side blocks `hidden … lg:block`),
`CLONE_SPEC.md:420` (#finding starts at the header's bottom edge),
`src/components/Palette.jsx:54-58` (reduced motion shows full palette, no loop),
`CLONE_SPEC.md:539` (footer sits directly under the green block).

## Not grounded / flagged

- The full list of the 23 probed 404 paths was not available. 8 were re-checked
  directly (all 404).
- The `/api/waitlist` success and error responses are inferred from the JS. They
  were never executed.
- Array cardinalities are locked to the observed counts by policy, and the
  x-maxWords headroom formula (+25%, min +1) is policy, not measurement.
- Dead compiled utilities (`#f3e7dc`, `clamp(2rem,6.5vw,3.75rem)`) have 0 DOM uses
  and are not tokenised.
