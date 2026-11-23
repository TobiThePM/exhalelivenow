---
name: css-facsimile
description: Re-typeset a scanned magazine/book page (or whole issue) as a pure-vector CSS facsimile — real type, no raster text, no upscaling, resolution-independent at print. Page-anchor fidelity standard (first/last words match the scan; headers keep their scan columns; free threading otherwise). Use for "CSS facsimile", "typeset facsimile", "no-pixels facsimile", "vector reprint of a scan", or scaling the Cross & Plough v11n3 method to other issues/projects. Companion to facsimile-edition (the image-gen lane, now reserved for ART only).
user-invocable: true
argument-hint: "[issue/page or scan path]"
---

# CSS Facsimile (the "no pixels" lane)

Proven zero-to-one: Cross & Plough v11n3 (Ladyday 1945), 16/16 pages, 2026-07-03 — full issue = 872KB pure vector vs 17MB image-gen. Reference run: `CIA/publishing/CLM Publishing/Cross & Plough/_facsimile_css/v11n3-run/`.

## The three documents (in authority order)

1. **`v11n3-run/RULEBOOK.md`** — the distilled per-page method. A bench reads THIS and nothing else. All gates, all element recipes, all learned rules.
2. **`v11n3-run/PIPELINE.md`** — the loop architecture, fidelity standard v2.1, escalation policy, illustrations lane.
3. **`v11n3-run/LEARNINGS-RUN.md`** + `_facsimile_css/LEARNINGS.md` — full rationale, escalation-only reading.

Reference implementation to clone: `v11n3-run/pages/folio-12/build/` (or the freshest page of the newest run).

## Fidelity standard (v2.1 "page-anchor", Charlie 2026-07-03)

Page's FIRST and LAST body words match the scan (threading integrity across pages) + headers land in their scan columns. Everything else: free natural threading, best-practice justification. NOT line-for-line — that was v1, retired (forced breaks create unjustifiable lines).

## Staffing (hard-won 2026-07-03)

- **Benches: Sonnet, BATCHED 3–4 pages per agent** (~18 min/page, near-zero fix rate once the rulebook covers the page types). Batching ≈ halves cost vs solo pages.
- **HAIKU IS RETIRED** from bench duty: on folios 10–11 it silently shipped pages with missing text, skipped gates, filed no reports. It executes mechanics but cannot be trusted with the verification half of the loop even when explicitly spelled out. Do not re-try below Sonnet until the gate suite is one exit-code script a model cannot skip.
- **Orchestrator (Fable/Opus): verifies EVERY page visually against the scan** (gates-green ≠ visually faithful — proven repeatedly), makes taste calls, writes each fix into the rulebook. Fix curve on the reference run: 4 → 1 → 0 → 0.

## Art lane

Typeset text is always vector. Art (mastheads, cuts, plates) = raster, REUSED from approved generated assets where they exist (crop from the image-gen pipeline's upscaled renders at ≥300ppi placed, knock white→alpha, corners must be alpha-0, composite-QA on the RENDERED PAGE not the asset). Never-generated art → the facsimile-edition generation process, as an escalation.

## Learned in review rounds 1–3 (2026-07-04) — now in the RULEBOOK, summarized here

- **MEASURE, DON'T EYEBALL (rule 0c):** all display sizes/positions derived from scan ink-heights (px→pt arithmetic) via `v11n3-run/measure.py`; verify the RENDER the same way. Measure clean glyphs only (a J's swash descender contaminates the band — the threshold trap).
- **Display lettering is ART (rule 0b):** nameplates/blackletter/calligraphy are never font-mimicked — crop from approved generated art.
- **Bottom-flush hard rule (0a), tolerance ≤0.03in** where the scan is flush; leading is the fill lever (content is anchor-fixed). Some footnote-bearing pages have a content-bound floor (footnote anchors to margin, not leading — two levers, one height budget); if uniform tuning stalls, ESCALATE to digital carding (rule 0a-ESCALATION): explicit per-column divs at the pinned break + INDEPENDENT per-column leading (±0.005 steps; deltas ≤0.04 are faithful — metal compositors carded columns separately). Round 4 proved every 'irreducible floor' false this way; never accept a documented floor until carding has been tried.
- **Pin exception:** if free flow can't reach flush, pin the column break at the SCAN's break word — the compositor balanced there (verified empirically both directions).
- **Footnote rules match the SOURCE's convention** (C&P = full column width), not book front-matter conventions; reserve the footnote's height in the flow (absolute-positioned footnotes + flush retunes = overlap bug).
- **Opener heads are usually a house constant** — v11n3's all cluster 17.3–18.7pt cap-height. Measure once, spec once.
- **Review-studio** (`v11n3-run/review-studio/`, generalize per consolidation plan): pair-mode annotations (left box then right), cache-busted image loads. GOTCHA: annotations persist in localStorage across rounds — reviewer must "Clear all" after each export or the next export re-ships resolved items as if unfixed.

## Per-issue quickstart

1. Inputs: per-folio verbatim transcripts (the facsimile-edition pipeline produces them) + original scans + (optional) image-gen renders as comparison baselines.
2. Create `<project>/_facsimile_css/<issue>-run/` with LEDGER.md (folio table from the contents page — provisional; benches correct it) and copies/links of RULEBOOK + PIPELINE.
3. Launch Sonnet benches in batches of 3–4, sequential, each delivering per page: PDF + PNG + 3-way comparison + ledger row + learnings-only-if-new.
4. Orchestrator verifies every comparison, bounces defects (each fix → a rulebook rule), then `pdfunite` in reading order + whole-issue gate sweep.
5. New page types cost one escalation each, then never again — budget most attention for the first 3–4 pages of a new publication.
