# Changelog

## 1.0.1 — 2026-10-14 (recheck pass)

allowlistVersion 1.0.0 · repositoryVersion 1.0.1 · pageSpecVersion 1.0.0

- Independent recheck (BUILD-GUIDE §4). The only defect found was a stale fact: the project was put under git and pushed
  after the build, but `registry.manifest.json` still said `isGitRepository: false` and "not a git repo".
  Both fields were corrected; `design-repo.zip` is confirmed listed in `.gitignore` and untracked.
- Re-verified with checks written independently of the build: 16 new mutations (template sequence, route
  binding, one-per-page, footer position, motion locks, pinned endpoint, asset roles, real-brand guard)
  all rejected for the right rule; 136 maxWords fields recounted, none over; 9/9 example nodes carry every
  required field; 7 random citations hand-checked against the quoted lines.

## 1.0.0 — 2026-10-14 (initial build)

allowlistVersion 1.0.0 · repositoryVersion 1.0.0 · pageSpecVersion 1.0.0

- Built from scratch per BUILD-GUIDE, bottom-up: tokens (143 foundation, 19 semantic,
  46 component, 21 layout; light theme) → 13 primitives → 8 components → 9 section
  contracts → template.home (route `/`) → 20 graph rules → draft-07 PageSpec schema →
  real-copy example → semantic validator → adversarial suite → measured-values (381
  citations) → verify_all + prove_drift → manifest/docs.
- Section ids, categories and template id were aligned to the sibling `ia.json`
  (written mid-build). That alignment needed two rule adjustments, checked against
  templates.json at write time: `ONE_HERO` now keys on `hero.intro`, with
  `hero.demo-mockup` as a named companion, and `NO_ADJACENT_SAME_CATEGORY` has three
  named exception pairs.
- QA corrections QA1–QA7 cited in `extraction/measured-values.json`. They take
  precedence over CLONE_SPEC.md where the two differ (e.g. CLONE_SPEC.md:217
  `focus:outline-none` is superseded by `outline-style:none`).
- Pinned-value checks (MASTER-GUIDE 3.23) for form.waitlist-endpoint and the
  real-brand and colour-block roles, in both semantic_validate (PageSpec) and
  verify_all (registry).
- Excluded as dead utilities: `#f3e7dc`, `clamp(2rem,6.5vw,3.75rem)` (compiled, 0 DOM uses).
