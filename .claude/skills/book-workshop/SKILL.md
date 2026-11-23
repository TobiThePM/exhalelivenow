---
name: book-workshop
description: The book workshop — router for the full markdown→Amazon-paperback pipeline. Routes a book job to the right bench (intake, finishing, interior layout, cover, listing, quality gate) and holds the cross-bench dependency map (trim → margins/gutter → page count → spine → cover wrap). Use when the user says "book workshop", "book factory", "make this a book", "publish this on Amazon/KDP", "pocket edition", or brings any source text (PDF, .doc, URL, scan) destined for print.
user-invocable: true
argument-hint: "[source text or project]"
---

# The Book Workshop

One bundle, many benches. Each bench is an independent skill — usable alone — and this file is the floor plan: which bench does what, in what order, and which numbers flow between them. The distributist point of the shop: the whole craft lives on Charlie's own bench, no Vellum, no InDesign, rebuilds are deterministic scripts at zero tokens.

## The benches

| Stage | Bench (skill) | What it does |
|-------|--------------|--------------|
| 0. Market | `niche-scout` | Is the niche worth printing into? (optional) |
| 1. Intake | `markitright` (PDF) / `textutil` (.doc/.docx) / WebFetch (URL) | Render ANY source into a clean **markdown master** first. Markdown is the WORDS layer; nothing goes to CSS that isn't markdown yet. |
| 2. Draft | `book-writer` + `book-quality-loop` | Only for books being *written*, not reprinted |
| 3. Finish | `manuscript-finisher` | Proofread/copyedit pass before layout — content locks here |
| 4. Interior | `design-to-book` | Trim, margins, typography, CSS→Paged.js render → `out/book.pdf` |
| 5. Cover | `cover-concept` (brief) → `kdp-cover-wrap` (front/spine/back wrap) | Needs FINAL interior page count first — see dependency map |
| 6. Listing | KDP Toolkit skills (`CIA/publishing/KDP Toolkit/`) | Title/subtitle/keywords/categories, back-cover copy |
| — Facsimile lane | `facsimile-edition` | Scan→faithful-reproduction jobs bypass benches 1–4 |

## Cross-bench dependency map (why order matters)

```
trim size ──→ interior margins + gutter (kdp-print-sizes.md §margins)
words ÷ words-per-page (+1/section opener) ──→ page count (even, ≥24)
page count × paper factor ──→ spine width (kdp-print-sizes.md §spine)
trim + spine + bleed ──→ full cover-wrap canvas (kdp-cover-wrap)
```

**Never build the cover before the interior page count is final.** Spine text requires ≥ 79 pp. Gutter grows with page count. Cover trim = interior trim + bleed.

## House defaults (CLM imprint)

- **Pocket encyclical / tract:** 4.25 × 6.87 in, black ink on cream, Cormorant Garamond ~12/16.6. Clone scaffold: `publishing/CLM Publishing/Catholic Land Movement/book/` — the canonical template (fonts, colophon, CSS all in place).
- **Full book:** 5.5 × 8.5. **Anthology:** 6 × 9.
- Front matter (half title, title page, copyright page w/ public-domain edition language, publisher's note) follows the shipped CLM editions: `design-to-book/reference/front-matter-conventions.md`.

## Order of checks

Content → design → **then** the end-stage passes, in this order (they're invalidated by any re-pagination): orphan/widow pass (`p { orphans:2; widows:2 }` + PNG scan), blank-page scan, hyphenation-at-page-break scan, even-page + ≥24pp gate, TOC folio verification. All specified in `design-to-book/reference/hard-won-rules.md` — read it before any non-trivial layout job.

## Staffing (model routing)

The benches run on **Sonnet** (`routine` agent or `model: sonnet`) — every bench has rails (a SKILL.md, a scaffold to clone, a script to run) and is exactly the "documented pipeline" case. The orchestrator (Fable/Opus) does only: bench sequencing, verifying outputs at handoffs (Read the rendered PNGs, diff extracted text against source), taste calls (trim/typography when NOT cloning a house template), and patching SKILL.md gaps the run exposes. Text-fidelity verification on source texts (encyclicals, reprints) follows the ensemble gate: extraction diffed against an independent second source (e.g. vatican.va for encyclicals) — pdftotext drops ligatures silently (`fi` → `#`), so never trust a single extraction.

## Reference shelf

- `design-to-book/reference/kdp-print-sizes.md` — trims, words/page math, margins/gutter, spine formula, page limits
- `design-to-book/reference/hard-won-rules.md` — accumulated typography/pagination rules from every shipped book
- `design-to-book/reference/front-matter-conventions.md` — title page, copyright page, publisher's note, colophon patterns
- Live KDP policy numbers drift — confirm at kdp.amazon.com before final upload

## Intake rule (the one new discipline)

Whatever Charlie points at — a Vatican PDF, an old .doc, a webpage, a Vellum export — bench 1 renders it to a markdown master **before** any design work, stored as `<project>/book/manuscript.md` (or `content/`). Footnotes become markdown footnotes (`[^n]`). The markdown master is the single source of truth; every downstream artifact is a deterministic rebuild from it.
