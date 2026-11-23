---
name: markitright
description: "Convert any PDF to clean, publication-ready markdown with figures preserved. Hybrid pipeline: programmatic extraction for digital pages (hyperlinks, bookmark headers, tables, footnotes, bold/italic), region-screenshot for figures (raster AND vector charts with axis labels and captions), vision fallback only for truly scanned pages. Includes a QA verification loop. Use this skill whenever someone provides a PDF, says 'convert this PDF', 'PDF to markdown', 'OCR this document', or needs structured text from any PDF — even if they don't say 'markitright' by name."
version: 6
---

# MarkItRight

Convert any PDF to clean markdown with figures intact. Four phases: preflight → extract → QA → finalize.

**Implementation lives at:** `Creative Intelligence Agency/crux/document-tools/markitright/` — that's where the `markitright` CLI, `pipeline.py`, `.venv`, and `scripts/` are. This SKILL.md in `.claude/skills/` is the registered triggering entrypoint; when invoked, `cd` to the implementation directory and activate the venv.

## Core Principle: Screenshot Regions, Don't Extract Bytes

The single most important lesson from this pipeline: **for any figure region, render a pixmap of that bbox — don't pull `block["image"]` raw bytes.**

```python
rect = fitz.Rect(block["bbox"]) + (-5, -5, 5, 5)  # small margin for labels
mat = fitz.Matrix(2, 2)                            # 2x zoom
pix = page.get_pixmap(matrix=mat, clip=rect)
pix.save(img_path)
```

Why: raw embedded image bytes miss everything drawn *on top* of the image (axis labels, legends, overlaid captions) and miss vector charts entirely. A clip-based pixmap captures exactly what a human sees. This works for raster images AND vector drawings — no detection needed.

## Core Principle: Classify by Text AND Images

A page with 7 characters of text but a full-page chart is **not scanned** — it's a figure page. Route it to the programmatic path, screenshot the figure, move on. The classifier must check both:

```python
has_image_blocks = any(
    b.get("type") == 1 and (b["bbox"][3] - b["bbox"][1]) >= 30
    for b in blocks
)
if len(text) > TEXT_LAYER_THRESHOLD or has_image_blocks:
    digital_pages.append(i)
else:
    scanned_pages.append(i)
```

Pages misclassified as scanned silently get routed to vision, which sometimes returns ~70 chars of garbage for an entire batch. Silent fallbacks are worse than noisy failures — when in doubt, stay programmatic.

## Setup

```bash
cd markitright  # wherever the repo is cloned
source .venv/bin/activate
```

If the venv doesn't exist: `python3.13 -m venv .venv && source .venv/bin/activate && pip install -e .`

Environment: `GEMINI_API_KEY` enables Gemini Vision for scanned pages. If unset, use Claude's native vision as fallback (see Phase 3).

## Phase 1: Preflight

Analyze the PDF before converting. Always run this first.

```bash
markitright INPUT.pdf --preflight
```

Report to the user: digital vs scanned page count, bookmark count, table pages, estimated cost. This shapes the extraction strategy — a fully digital PDF with bookmarks is free and instant; a fully scanned PDF needs vision for every page.

## Phase 2: Extract

```bash
markitright INPUT.pdf -o OUTPUT.md
```

The pipeline handles digital pages programmatically (free, instant) and routes scanned pages through Gemini Vision. It preserves hyperlinks, uses the PDF bookmark tree for exact header hierarchy, detects tables, converts footnotes, joins PDF line breaks into proper paragraphs, strips running headers/footers, and skips TOC pages.

Force vision for all pages with `--vision` (useful when programmatic output is garbled).

**LiteParse digital backup (`--liteparse-backup`, opt-in).** A safety net for *digital* pages only: when a digital page's programmatic PyMuPDF text comes back thin (< 80 chars, e.g. an odd font-encoding or an embedded-text quirk), it's retried with LiteParse (`liteparse parse --no-ocr --format json`) and substituted only when LiteParse clearly beats the thin result. **It never touches scanned/image pages — those stay on Gemini Vision, which is almost always best for image-based scans.** Default off; the proven programmatic + vision paths are unchanged when the flag is absent. Requires the `liteparse` CLI on PATH (`pip install liteparse`, which wraps the npm `@llamaindex/liteparse` binary). The run report appends `(N via LiteParse backup)` to the Method line when it fires.

Figures are automatically captured as 2x-zoom region screenshots into an `images/` directory alongside the output markdown, linked as `![Figure N](images/page_N_fig_M.png)`. This captures raster images, vector charts, axis labels, legends, and overlaid captions — everything rendered on the page within the figure bbox, plus a 5pt margin. Use `--no-images` to skip extraction and use `*(Figure)*` placeholders instead.

Benchmark on Anthropic Claude 4.6 system card (245 pages): 239 programmatic pages, 0 vision calls, 102 figures extracted, ~27 seconds, $0.

## Phase 3: QA Loop

This is the skill's core value — read the output and fix what the pipeline got wrong. **Verify visually, not by reading output in isolation.** Grepping output catches obvious failures but misses misplaced figures, missing captions, silent page skips.

1. Read the output section by section
2. Look for broken paragraphs, missing header prefixes, garbled tables, orphaned footnotes, nested links, figures attributed to the wrong section — read `references/qa-patterns.md` **in the implementation dir** (`Creative Intelligence Agency/crux/document-tools/markitright/`) for the full checklist
3. **Spot-check figure-heavy pages explicitly.** Figures silently vanishing is the highest-impact failure mode. If the preflight reported N image pages, confirm N figures in the output.
4. For anything suspicious, visually check that page:
   - **With Gemini**: `./scripts/check_page.sh INPUT.pdf PAGE_NUM`
   - **Without Gemini** (Claude vision fallback): `./scripts/render_page.sh INPUT.pdf PAGE_NUM` then Read the output PNG
5. Fix the markdown to match what the page actually shows
6. Repeat until clean

### Known residual issues (v6)

- **Footnotes mid-body.** Footnotes `²`/`³` occasionally merge into paragraphs between bullets. Font-size detection alone isn't reliable; needs superscript-reference + bottom-of-page matching.
- **Multi-line headers.** Section titles spanning two PDF blocks sometimes split or merge with body.
- **Caption attribution.** A chart near a section break can get attached to the wrong header; no explicit caption-to-figure binding yet.
- **No automated visual verifier.** Side-by-side PDF-vs-markdown across all pages is the right next tool but doesn't exist yet.

## Phase 4: Finalize

Copy the corrected markdown to the user's requested location. Report:
- Total pages, method breakdown (programmatic vs vision)
- Wall clock time
- Issues found and fixed in QA
- Estimated API cost (free if fully digital)

## Scripts

| Script | What | When |
|--------|------|------|
| `scripts/check_page.sh PDF PAGE` | Send one page to Gemini Vision, print markdown | QA spot-checks (requires GEMINI_API_KEY) |
| `scripts/render_page.sh PDF PAGE [OUT]` | Render page to PNG at 200dpi | Claude vision fallback (no API key needed) |

PAGE is 1-indexed (page 1 = first page).

## References

- `references/qa-patterns.md` — Known issues the QA loop should catch, with examples from testing on a 245-page system card
