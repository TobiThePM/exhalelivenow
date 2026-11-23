# MarkItRight v6 — Debugging Session Notes (2026-04-09)

Fixing silent figure loss in the PDF → markdown pipeline. Benchmark document: Anthropic Claude 4.6 system card (245 pages).

## The problem

Output looked clean in isolation but silently failed on figure-heavy pages. Symptoms:

- Pages 76–80, 151, 242 came through with almost nothing. Page 151 (a full-page 9-subplot vector chart) had zero image references.
- Figure captions (`[Figure 2.2.5.4.A]`, etc.) disappeared entirely.
- Figures got attributed to the wrong section (chart for §2.2.5.4 landed under §2.2.5.5).
- A batch of 6 "scanned" pages routed to Gemini vision came back with ~70 characters of garbage for the whole batch.
- No warning, no error — the markdown just read as if those pages didn't exist.

## Root causes (two bugs compounding)

**1. Page classifier only checked text length.**

```python
if len(text) > TEXT_LAYER_THRESHOLD:  # 30 chars
    digital_pages.append(i)
else:
    scanned_pages.append(i)
```

Page 151's text layer was literally `"151"`. Below threshold → routed to Gemini vision → silent drop. The page had a perfectly extractable `type == 1` image block; it was just mislabeled.

**2. Image extraction used raw embedded bytes.**

For each figure block the old pipeline did `block["image"]` to grab raw bytes. This:

- Missed vector drawings entirely — matplotlib-style charts drawn as SVG paths have no embedded image object.
- Even for raster images, stripped surrounding axis labels, legends, and overlaid captions that were drawn on top of the bitmap in the PDF, not baked into it.

## The fixes

Both in `markitright/pipeline.py`.

### Classification checks image blocks in addition to text

```python
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text().strip()
    blocks = page.get_text("dict")["blocks"]
    has_image_blocks = any(
        b.get("type") == 1 and (b["bbox"][3] - b["bbox"][1]) >= 30
        for b in blocks
    )
    if len(text) > TEXT_LAYER_THRESHOLD or has_image_blocks:
        digital_pages.append(i)
    else:
        scanned_pages.append(i)
```

The `>= 30` filter rejects decorative dividers. A page only routes to vision if it has NEITHER meaningful text NOR a substantial image block.

### Screenshot figure regions instead of extracting raw bytes

```python
rect = fitz.Rect(block["bbox"]) + (-5, -5, 5, 5)  # 5pt margin for axis labels
mat = fitz.Matrix(2, 2)                            # 2x zoom
pix = page.get_pixmap(matrix=mat, clip=rect)
pix.save(img_path)
output_parts.append(f"![Figure {fig_idx}](images/{img_name})")
```

`page.get_pixmap(clip=rect)` renders whatever's in that rectangle — raster, vector, text overlays, axis labels, everything. 5pt margin catches labels that sit just outside the reported bbox. 2x zoom keeps the output readable when viewed inline. This is the Marker approach (crop page regions) without needing Marker's ML layout model — we reuse PyMuPDF's bboxes directly.

## Results

| Metric | Before (v5) | After (v6) |
|---|---|---|
| Programmatic pages | 233 | **239** |
| Vision calls | 6 | **0** |
| Figures extracted | 88 | **102** |
| Wall clock | ~25s | **27s** |
| Cost | small Gemini hit | **$0** |

Spot-checked page 151 (9-subplot Behavioral Audit chart), page 242, pages 76–80 (multi-subplot clusters) — all now present as clean screenshots.

## Learnings (rules for future pipeline work)

1. **Screenshot regions, don't extract raw bytes.** A pixmap of the bbox captures exactly what a human sees. Format-agnostic, handles raster and vector, includes overlays. Use this pattern anywhere you need to preserve a figure with its labels.

2. **Classify pages by text AND image presence, not text length alone.** A thin text layer is ambiguous — it might be a scanned page, or it might be a full-page chart. Check for image blocks before routing to vision.

3. **Silent fallbacks are worse than noisy failures.** The "scanned → vision → empty batch → drop" path failed without any warning. Any fallback should emit loud logging when it produces < N chars for a page it claimed to process.

4. **Add margin to bboxes before screenshotting.** 5pt on each side catches axis labels, tick marks, and caption baselines that sit just outside the reported image bbox.

5. **Verify visually, not by reading output in isolation.** Grepping the markdown catches obvious failures but misses misplaced figures, missing captions, silent page skips. The only reliable check is side-by-side PDF vs markdown.

6. **"Looks clean" is not "works."** Pre-v6 output grepped clean and passed a casual read. The bug only surfaced when we opened the PDF next to the markdown. A skill is not shipped until it's verified against a non-trivial real document.

## Known residual issues

- **Footnotes mid-body.** Superscript refs (`²`, `³`) occasionally merge into body paragraphs between bullets. Font-size detection alone is unreliable. Fix needs: superscript-reference scan + bottom-of-page footnote matching, then re-insert as `[^N]:` definitions.
- **Multi-line headers.** Section titles spanning two PDF blocks sometimes split or merge with body text. Bookmark-matching pass catches most but not all.
- **Caption-to-figure binding.** A chart near a section break can get attached to the wrong header. No explicit binding logic yet.
- **No automated visual verifier.** Side-by-side PDF-vs-markdown across all pages is the right next tool. Didn't build it this session.

## Process notes (what actually moved us)

- **Comparative eval against Marker** (datalab-to/marker) on the same PDF. Marker took 16m41s to markitright's 25s, but its output had clean figure screenshots — that's what told us the fix was about the extraction method, not the speed.
- **PyMuPDF probing scripts.** Small throwaway scripts to inspect `page.get_text("dict")["blocks"]` and `get_drawings()` on the "silent" pages surfaced the classification bug (`text = "151"` → scanned).
- **Two-line code fixes.** Once the root cause was identified, the fix was small.
- **Rebuild + visual spot check.** `markitright /tmp/anthropic-test.pdf -o /tmp/anthropic-v12.md`, then opened in Typora.

## Output artifacts

- Markdown: `~/Downloads/anthropic-markitright-v12/anthropic-system-card.md` (418KB)
- Figures: `~/Downloads/anthropic-markitright-v12/images/` (102 PNGs)
- Gist: https://gist.github.com/cdeistopened/fe532c916b97a4e94f66c2014967e972 (markdown only — gists don't support directories, images not attachable)
- Code: `Creative Intelligence Agency/crux/document-tools/markitright/markitright/pipeline.py`
