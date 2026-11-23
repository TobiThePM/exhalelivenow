---
name: facsimile-edition
description: Turn a scanned old magazine/journal issue into a print-ready KDP paperback facsimile — render & split folios, transcribe verbatim from the archive markdown, regenerate each page clean with gpt-image-2 (grounded), auto-place into the KDP template, fine-tune in a browser studio, and assemble interior + cover + listing. Use for "facsimile edition", "Cross & Plough facsimile", "reproduce/restore an old magazine for print", "turn this issue into a book", or any scan→faithful-print-reproduction task.
---

# Facsimile Edition Pipeline

Reference implementation lives in `Creative Intelligence Agency/publishing/CLM Publishing/Cross & Plough/_facsimile_samples/experiments/prod/` (and `…/ed52/` for a second-issue example). Scripts have hard-coded C&P paths — copy + repoint for a new title.

## The one load-bearing fact
**A generative image model redraws text from its language prior — it cannot OCR-faithfully reproduce dense body type on its own.** Every page MUST be grounded with its exact transcript, and the model must be told to trust the transcript over the scan. Proven: ungrounded nano-banana/Gemini corrupt ~15 words/page (invisible at a glance); **gpt-image-2 + per-page transcript = ~0 errors**. See `[[feedback_gpt_image2_vs_gemini_facsimile]]`, `[[feedback_vlm_fullpage_autocorrects_text]]`.

## Pipeline (6 stages)

### 1. Render + split source folios
The archive scans are often **2-up spreads on a dark scanner bed**, sometimes skewed. Per page:
- `pdftoppm -r 300 -png source.pdf out` → render.
- Split spreads at the center; **crop to the bright paper region** (rows/cols where `>120` brightness covers >35%) to drop the dark bed.
- Badly-rotated folio (e.g. a 45° scan): rotate to level, then remove the black scanner-bed corners with a **PIL BoxBlur dark-density filter** (`density>0.72` = bed; text columns ~0.3 survive), crop tight to the ink. Don't crop to the diamond bbox — that keeps the black corners.
- **Gutter split (2026-07, `split_spreads.py`):** two strategies — (a) if a dark gutter **shadow** exists, split at the darkest central valley; (b) if the scan is **flat with no shadow** (paper fraction ~0.8 straight across), split at the **midpoint of the paper region**. A pure "darkest column" heuristic fails on flat scans (picks a text column or edge → one half keeps the whole spread). Map PDF spread page → (left folio, right folio) explicitly.

### 2. Transcribe (the grounding)
Spawn **one agent per folio** (parallel). Each reads the rendered folio + the issue's archive markdown (`Sources/OCR_Transcriptions/NN_*.md`) and writes the **verbatim text of that folio only**, in reading order, with light bracketed layout hints (`[Centered heading:]`, `[Two columns, drop-cap "I"]`, `[Three EQUAL-width columns]`). Markdown is the authority for spelling. → `transcripts/page_NN.txt`.
- If the scan is **cut off** (missing words at an edge), add a note: `[IMPORTANT — source scan is cut at the upper-right; render the COMPLETE text below, nothing truncated.]` The grounding then fills the gap.

### 3. Generate (gpt-image-2, grounded)
`generate_page.py NN` — builds the prompt and calls `gpt-image-2` via `/v1/images/edits`. The prompt = GROUND + `<page_text>transcript</page_text>` + RULES. **Non-negotiable prompt rules (baked in):**
- "render character-for-character from the transcript; trust it over the scan; do not autocorrect, drop, paraphrase, **or ADD** any word."
- **Anti-masthead:** "Add NOTHING not in the transcript — no masthead/banner/title/logo/editor line unless it's in the transcript. If the transcript begins with body text, the page begins with body text." (Stops gpt-image inventing a letterhead on continuation pages.)
- **De-skew:** "Keep every text line perfectly horizontal."
- **Completeness (2026-07):** "Render EVERY paragraph and line in the transcript, including the last paragraph at the foot of each column and the page-number digit. Do not omit, merge, or truncate. A hyphen at a column's end (`poss-`) continues at the top of the next column." (gpt-image-2 silently drops a lone page number or a bottom paragraph on dense pages — this + a verify pass catch it.)
- **Scan-anchored measure (2026-07):** "Preserve the EXACT column width, gutter, and text-block width of the source scan; do not reflow/widen/narrow the columns; the scan's measure is constant across the issue — match it." (Inch specs like "3.15in columns" do NOT bind gpt-image-2; anchoring to the scan it's editing helps more — but only marginally. Width consistency remains the main open problem.)
- `size=1600x1888` — the magazine **0.846 aspect**, NOT 1536×2048 (0.75) which stretches text ~13% vertically. Resolution doesn't affect text fidelity; aspect + grounding do.
- `quality=high`, `background=opaque`, `output_format=png`. Caps ~3.15 MP (pixel budget).
- Per-page input override: `exp/page_NN_input.png` (the deskewed/cleaned scan) is used if present.
- **Reference impl:** `…/experiments/ed52/gen_v2.py` (has the completeness + scan-anchored-measure rules baked in).

### 4. Normalize (deterministic — `normalize.py`, the validated 2026-07 realignment; replaces raw Tesseract auto-place)
One deterministic pass lands every generated page on the same canvas so the whole issue is consistent. `…/experiments/ed52/normalize.py`. Principles, each earned the hard way:
1. **Deskew only if ≥0.6°** (projection-profile). Rotating an already-level page by a spurious 0.5° *introduces* skew — the #1 realignment bug.
2. **Constant BODY type size via median Tesseract glyph height** (uniform scale to a target). NEVER scale-to-width — that shrinks type ("scrunch"), which the user vetoes.
3. **Ink-bbox rejects the dark scanner bed** (near-solid rows/cols excluded) + foxing.
4. **Separate the folio number** from the body: dense-block bottom = body; the lone digit below (found via Tesseract, `\d{1,3}`) is cropped out and placed **low in the bottom margin**, its **left/right (verso/recto) side preserved**.
5. **Vertically center the body block**, top margin slightly < bottom (small upward bias). Do NOT top-anchor (pages then spill past the bottom while leaving the top empty) and do NOT bottom-anchor (dense pages shove the top off).
6. **Wider type area** (side margins ~0.5″) so the block sits mid-page; a wider-rendered page just has thinner margins (accepted — see width problem).
7. **Display/title pages** (word count < ~130) *fill* the page instead of holding body type size.
- The old raster Tesseract `auto_place.py`/Layout-Studio path is superseded for realignment — keep it only if you need manual per-page nudging of mixed layouts.

### 5. Fine-tune (browser studio)
`auto_place52.py` seeds a **Layout Studio** (`stretch.html`, served via `python3 -m http.server`) with the auto-placement transforms. Modes: **Place** (drag/8-handle free-stretch, column + baseline guides overlaid *on top* of the image), **Spread** (facing pages), **Gallery** (all pages). Exports each placed page at 300 dpi. Placements persist in localStorage; pull them with `evaluate_script` → save to `page-placements.json`.

### 6. Assemble + list
- `build_frontmatter.py` → 5 CSS front-matter pages (title · colophon w/ imprint logo · *Pro Foco* motto frontispiece + McNabb epigraph · the imprint note · contents). Compose with PIL on 2550×3300; **flatten transparent PNGs onto white first** (alpha→black trap).
- `kdp_build.py` → composite all pages into the 8.5×11 @300dpi interior (un-stretches legacy 0.75 renders, glyph-normalized type, mirrored gutter, **stamped serif folios** at a fixed foot).
- `build_kdp_package.py` → 24-page interior PDF (front matter + body) + **wraparound cover** (front = masthead, back = emblem, spine = pages × 0.002252 in white paper) + KDP standards check.
- Listing: title, description, 7 keywords, 3 BISAC, price → `KDP-LISTING.md`.
- Consolidate interior + cover + template + listing into one `…-SUBMISSION/` folder with a README.

## The harness (2026-07 — run everything through this)
**`_facsimile_samples/harness/facsimile.py <command> [pages] --issue <dir>`** — stateful CLI wrapping the whole pipeline with a per-issue `manifest.json` (verify results, rolls, $ spent, waivers). State lives on disk, not in the conversation — a session once claimed "1–16 done" when only 1–10 existed; `status` audits the dirs and never lies.
- Issue-dir convention: `input/folio_<ID>.png` · `transcripts/folio_<ID>.txt` · `renders/folio_<ID>.png` (canonical render dir) · `normalized/` · `upscaled/` · `manifest.json`.
- **`preverify` is the free money-gate**: scan↔transcript diff runs BEFORE any generation; `generate` refuses a page whose preverify failed (human adjudicates → `waive <page> "note"`). Catches transcript drops at $0 instead of a $0.20 re-roll. Known false positive: Tesseract reads columns in a different order than the transcript → an "unmatched run" whose words all exist; check + waive.
- `generate` skips pages that already have a render (`--reroll` to spend again); never auto-re-roll for width/measure variance — that's stochastic and unwinnable; normalize absorbs it.
- `postverify` = transcript↔render + page-# check; `review` builds `review.html` (all flagged pages, scan vs render side-by-side) so a human adjudicates a whole issue in one sitting; `upscale` runs waifu2x/realesrgan from PATH or `harness/bin/` (never diffusion).
- Splitting gotcha (ed52): a spread MAP can assign a folio to an **empty scanner-bed half** (ed52 "back cover" was the bed — no back cover in the John Carroll scan at all). Eyeball `src_render/` halves before transcribing.
- **`geometry` gate (2026-07)** — catches what text-verify can't: per-column skew, column measure, type stretch. Three earned rules: **(1)** flag against the **issue median of renders**, not each page's scan — aged paper + foxing make the scan too noisy a yardstick, and the original used one measure issue-wide anyway; **(2)** skew sensing must be **line-baseline regression** on Tesseract line boxes (~0.1° sensitivity, per column) — projection-profile search at 0.25° steps misses the 0.2–0.5° band a human reviewer notices (thresholds: flag ≥0.3° abs or ≥0.25° column disagreement); **(3)** **uniform** tilt → normalize rotates it out (`rotate(mean_measured)`, sign verified empirically; correct the 0.15–0.6° band the old 0.6° threshold ignored), **differential** tilt (columns opposing) → generation artifact, only a re-roll fixes it. Reroll archives the old render (`folio_NN.rollK.png`) so the better roll wins.
- **normalize never-clip rule:** glyph-match is a *target*, fitting the canvas is a *constraint* — cap scale so no page (esp. large-scanned originals) ever overflows the canvas and gets cut in the compare view.
- **widen-to-median (the downstream fix for narrow measure):** a render that came out NARROW is stretched **horizontally only** to the issue's median measure (cap +6%). Type height untouched — this is NOT the vetoed "scrunch" (which shrank type); ≤6% glyph widening is imperceptible and margins land consistently. Renders only, never originals. Kills most measure-drift re-rolls.
- **assemble stage** (`experiments/ed52/assemble.py` — edit only the ISSUE block for a new issue): 24pp interior = half-title/blank/title/colophon/motto-frontispiece/imprint-note/contents + the folios + a re-set "JOIN NOW!/WHAT THE POPES SAY" back-matter page (roster omitted — anachronism); **mirrored KDP gutter** = shift every page 0.15in toward its outside edge (recto→right, verso→left; KDP inside-margin min 0.375in at ≤150pp); wraparound cover = emblem back + spine (pages×0.002252in) + facsimile-cover front; PDFs → ~/Downloads.

### Canonical run order (kick off a new issue end-to-end)
```
check PROGRESS.md                 # ../_facsimile_samples/PROGRESS.md — is this issue already started? what's blocking it?
split_spreads.py (edit MAP; eyeball src_render/ halves!) → split OCR per page → transcripts/
facsimile.py preverify all        # FREE gate — nothing generates till clean/waived
facsimile.py generate all         # gpt-image-2, ~$0.20/page
facsimile.py postverify all && facsimile.py geometry all
facsimile.py review               # human eyes on review.html; waive or --reroll flagged pages
facsimile.py upscale all          # waifu2x 2x, free
normalize.py                      # fine-deskew + widen-to-median + never-clip → compare.html check
assemble.py                       # edit ISSUE block → interior + cover PDFs
append to LEARNINGS.md            # ../_facsimile_samples/LEARNINGS.md — dated entry, even a short one; update PROGRESS.md row(s)
```

## Verification
**`verify_harness.py NN …`** (deterministic, free, `…/experiments/ed52/`; now split across the harness's `preverify`/`postverify`) is the primary gate. It Tesseract-OCRs the scan and the render and difflib-diffs both against the transcript, catching BOTH failure modes: **(A)** scan text missing from the transcript = a **transcript drop** (folio-5 bug — the OCR itself had dropped a paragraph), and **(B)** transcript text missing from the render = a **generation drop**. Plus a page-number-present check. Adjudicate every flag by **crop + 3× zoom** — the harness over-flags isolated page numbers (Tesseract can't see a lone digit in white space) and Tesseract on aged scans is noisy, so use the flagged *runs*, not the ratio.
- Full-page VLM reads (yours and subagents') silently auto-correct errors — don't trust them. Skip the Gemini pass on short runs (over-flags; on #52 all its "errors" were correct).

### Source text: split the OCR, don't re-transcribe
If a full-issue OCR markdown exists (`Sources/OCR_Transcriptions/NN_*.md`), **split it into per-page files** and verify each against the scan with the harness — do NOT re-transcribe every page from the image (redundant, and re-invents clean text, risking new errors). Only read the scan on pages the harness flags as incomplete. (Re-transcribing is only the fallback when no OCR exists.) Caveat: the OCR can itself drop content, so the scan-verify step is mandatory either way. **Subagent gotcha:** the API content-filter can false-positive and block a subagent's *output* on benign apocalyptic/violent verse (folio-14 sonnet on *After London*) — transcribe those pages in the main thread instead.

## Upscaling (make pages crisp for print)
gpt-image-2 caps at ~1600×1888; print wants 2550×3300 @300dpi (~2× up). **Use a NON-generative, text-safe upscaler only** — creative ones (Clarity, Magnific, SUPIR, any SD-based) re-imagine glyphs and silently alter the text you just verified.
- **Best:** Topaz **"Text Refine"** model (Replicate `topazlabs/image-upscale`) — purpose-built for documents.
- **Free/local:** **waifu2x** (`waifu2x-ncnn-vulkan`, or Upscayl) — zero hallucination, preserves linework. Real-ESRGAN is prettier but can break vertical rhythm/kerning slightly.
- Recipe: upscale the raw 1600×1888 output 2× **before** `normalize.py` resizes it; optional **binarize** to pure #000/#fff for razor edges (safe — pages are already black-on-white). Full write-up: `_facsimile_samples/facsimile-hard-problems-and-upscaling-20260701.md`.

## Per-edition efficiency + cross-issue audit
The closing pages often repeat across issues. `audit_backmatter.py` difflib-compares the tail of every issue's OCR to find shared closing content (found #52 ≈ #53 verbatim on "THE OTHER SIX"). Reuse a rendered page rather than re-making it. NOTE: OCR omits the back COVER, so shared association/subscription back covers need a separate **image-level** audit. Keep a per-edition manifest of done/todo. **The hardest unsolved problem is the type-size ↔ column-width coupling** — see the write-up above.

## Scope / limits
- Display type (bold sans labels in cartoons) defeats EVERY model (`FOREIGN`→`FOREICN`) → use the deterministic cleaned scan for those pages.
- Mixed-layout pages → manual placement.
- KDP minimums: **24 pages**, 8.5×11; pad a thin issue with front matter.
- OpenAI account must not be billing-hard-limited.

## Cost / speed
gpt-image-2 ~$0.15–0.20 and ~2 min per page. A 20-page issue ≈ $3–4, ~40 min (or parallel). Front matter + cover are reusable per title.
