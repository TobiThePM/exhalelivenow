---
name: design-to-book
description: Produce a print-ready KDP paperback interior PDF from a markdown manuscript using the CSS→Paged.js pipeline (the "InDesign substitute"). Design is decoupled from content — rebuild is a script, zero AI tokens. Use when the user wants to format a manuscript, pamphlet, or book for Amazon/KDP print, pick a trim size, hit a target page count, set book typography, or render an interior PDF. Trigger phrases: "format as a book", "KDP interior", "print-ready PDF", "lay this out as a pamphlet/paperback", "InDesign skill", "design-to-book".
user-invocable: true
argument-hint: "[manuscript path or project]"
---

Turn a markdown manuscript into a print-ready paperback interior PDF. CSS holds the **look**, a rethread script maps markdown → design-classed HTML, and headless Chrome + Paged.js paginate it. **Rebuilding is a deterministic script — 0 tokens per rebuild.** Tokens are spent only on design decisions and visual verification.

This is the pipeline the repo calls the "InDesign substitute." It was previously documented only in `publishing/LAYOUT-PIPELINE-DOC-20260613.md` and lived as un-packaged `book/` scaffolds; this skill makes it discoverable. Companion: `kdp-cover-wrap` (cover + spine), KDP Toolkit skills (`cover-creator`, `back-cover-writer`, `listing-optimizer`).

## Three-layer decoupling (never collapse these)

```
manuscript.md          ← WORDS — edit freely, 0 tokens
  src/rethread.mjs      ← RULES — markdown patterns → HTML + CSS classes
  design/<book>.css     ← LOOK  — fonts, @page geometry, running heads, folios
  src/pdf.mjs           ← RENDER — Paged.js via playwright → out/book.pdf
```

## Fastest path: clone a working scaffold

Do **not** build from scratch. Clone the nearest existing `book/` and swap content + CSS:

- **Pamphlet / pocket (4.25×6.87, B&W, artwork, colophon):**
  `publishing/CLM Publishing/Catholic Land Movement/book/` — the canonical small-format reference.
- **Pocket guide (5×8):** `clients/rlm/studio/books/pocket-guides/aging-well/book/`
- **Full book w/ roman-front + TOC + two-pass folios:** `publishing/dairy-sheep-book/book/` or `Guide Abrege/book/`

Each clones the same tree: `content/ design/ src/ vendor/ fonts/ assets/ out/ package.json`.

## Procedure

1. **Pick trim + interior.** Read `reference/kdp-print-sizes.md`. Confirm trim size and B&W-vs-color with the user (these drive cost and page count). Compute the page target: `pages ≈ words ÷ words_per_page` (+1 per section opener).
2. **Clone** the closest scaffold into `<project>/book/`.
3. **Place the manuscript.** If the manuscript hasn't had a finishing pass, run `manuscript-finisher` first. Clean OCR artifacts, restore curly quotes/em-dashes, write `manuscript.md`. Markdown headings map to title page / section openers per `rethread.mjs`.
4. **Set the look.** Edit `design/<book>.css`: `@page { size }` to the trim, mirrored gutter margins, body font/size/leading, running heads, folios, section-opener ornaments. Self-host fonts in `fonts/` as woff2 (pull from the fontsource CDN) and `@font-face` them — **local, not CDN** (file:// blocks refetch at render).
5. **Render.** `npm run flow` → `out/book.pdf`. Then `pdftoppm -png -r 130 out/book.pdf out/pg` and **Read the PNGs** to verify visually — never trust the page count alone. Optional: publish `out/*.pdf` + page PNGs via `here-now` for author markup.
6. **Iterate** on CSS until the proof is right. Hand off cover to `kdp-cover-wrap`.

## Non-negotiable gotchas (these cause silent failures)

- **Inline the CSS** into a `<style>` in `flow.html`. Paged.js refetches `<link>` stylesheets with `fetch()`, which `file://` blocks → silent **1-page** PDF.
- **Never** use Chrome `--print-to-pdf` with `--virtual-time-budget` for Paged.js — it truncates pagination mid-run with no error. Use **playwright + `waitForFunction('window.__pagedDone === true')`**.
- **Fix the playwright path** for the current machine. WORKING path on this box (verified 2026-06-30):
  `/Users/charliedeist/.claude/skills/gstack/node_modules/playwright-core/index.mjs`
  Old scaffolds hardcode `/Users/charlesdeist/npm-global/lib/node_modules/clawdbot/...` (**charlesdeist** — wrong user, does NOT exist, crashes with `ERR_MODULE_NOT_FOUND`). `grep -rl charlesdeist src/` and fix every build script (pdf.mjs AND each cover script).
- **B&W interiors:** keep the page background **white** and let KDP's **cream paper stock** supply the warmth — do not print a cream fill (it halftones to gray and costs ink). Knock cream/transparent backgrounds out of line-art (PIL: composite onto white, level the light point, alpha = 255−gray) so plates print as clean black-on-white.
- Page count must be **even** and **≥ 24**; spine text needs **≥ 79 pp**.

## Facing-page illustration spreads (validated 2026-06-30, Catholic Land Movement)

- **Art on verso / text on recto:** the illustration `<section>` gets `break-before: left`, the opener-text section gets `break-before: right`. Verso(left)+recto(right) = a facing spread. Frontispiece-facing-title works the same (frontis `break-before:left`, title `break-before:right`).
- **Parity blanks are the trap.** Two consecutive forced-side breaks (end-of-section plate → next opener-verso) insert a blank whenever the prior section ends on the "wrong" side. Fix: make **end-of-section tailpieces flow IN-COLUMN** (`<figure class="tailpiece">` with `break-inside:avoid`, emitted *inside* the section body before `closeSection()`) instead of a forced full page. They sit below the last text on the same page if they fit; no forced break, no blank. Keep a plate full-page only where it lands cleanly. After changes, scan blanks: `for p in $(seq 1 $N); do [ -z "$(pdftotext -f $p -l $p file.pdf - | tr -d ' \n\f')" ] && echo "blank p$p"; done` — only conventional blanks (a front-matter verso, a verso before a closing plate) should remain.
- **Drop caps:** Paged.js renders `::first-letter` unreliably on non-first-child paragraphs (works on the Foreword's first para, silently no-ops mid-column). Wrap the first letter in an explicit `<span class="dropcap">` instead; float it.
- **Plate provenance:** read the artist off each plate / the source archive — don't assume one artist. (C&P: most cuts = Philip Hagreen, but "Wings Over Home Land" = *John* Hagreen, the Hail-Mary Madonna = H.R. = Harold Robbins.) Gallery manifest with per-image issue numbers: `Cross & Plough/site/src/data/gallery-manifest.json`.
- **No fabricated epigraphs:** before printing a quotation under an author's name, grep the manuscript/corpus — a "popular paraphrase" is not a verbatim quote (caught a fake McNabb epigraph this way; [[feedback_default_reject_author_edits]]).
- Requires: Google Chrome, `node`, `pdftoppm`/`pdfunite` (poppler), a local Paged.js `vendor/paged.polyfill.js`.

## Reference

- `reference/kdp-print-sizes.md` — trim sizes, page-count math, margins/gutter, spine width.
- `reference/hard-won-rules.md` — the accumulated typography/layout/pagination rules from real books (justified+hyphens body, pdfunite-not-Ghostscript merge, density lever, orphan/widow pass, author-proof triage, collected-talks template, facsimile variant). **Read before any non-trivial layout job.**
- `reference/claude-design-bundle.md` — the Claude-Design-bundle workflow variant (bundle fetch via curl, rethread mapping table, Canvas Studio commentable variant, zero-token commands).
- `publishing/LAYOUT-PIPELINE-DOC-20260613.md` — deep pipeline notes (two-pass TOC, ghostscript merge, Paged.js paths).
