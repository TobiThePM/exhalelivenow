---
name: kdp-cover-wrap
description: Build KDP paperback covers (front, back, spine, full wrap) using GPT Image 2 for panels and deterministic Pillow composition for the wrap. Aligns to Amazon's official KDP cover template (PDF + PNG overlay) so bleed, safe zones, spine, and barcode box land correctly at print resolution.
triggers:
  - "design a book cover"
  - "KDP cover"
  - "paperback wrap"
  - "full cover with spine"
  - "back cover for book"
---

# KDP Cover Wrap

Build print-ready paperback covers for Amazon KDP. Three surfaces: front, back, spine — plus the composited wrap. AI generates the artwork panels; Pillow handles the wrap geometry so nothing drifts.

## When to use

- User wants a book cover or back cover for a print paperback.
- User wants the "full wrap" (back | spine | front) as one file for the KDP upload.
- User asks about spine width, bleed, or safe zones on a cover.

## Mental model

**Panels are art. The wrap is math.** Never ask an image model to render the entire wrap in one shot — back-cover copy gets smudged, spine text hallucinates characters at <128 px wide, and centering drifts. Generate panels at 2:3 aspect, then composite.

Three phases:

1. **Panel generation** — front and back at 1024×1536 (or 1800×2700 for print) via GPT Image 2 `high` quality.
2. **Wrap composition** — Pillow script stitches back | spine | front with a spine generated locally (true typography, not AI-hallucinated text).
3. **Template alignment** — overlay the KDP template PNG to verify bleed, safe zones, spine position, barcode box.

## KDP template — the source of truth

Amazon provides a free per-book template at `kdp.amazon.com/cover-templates` (or the "Cover Creator → Download template" link inside a KDP book setup).

Inputs to the generator:
- Trim size (e.g. 6 × 9 inches)
- Page count (drives spine width)
- Paper type (cream = 0.0025"/page, white = 0.002252"/page, color = 0.002347"/page)
- Binding (paperback)

> **2026-06-12 constants fix:** the scripts (and this doc) previously had cream/white SWAPPED. All four scripts now carry Amazon's official values above. Any wrap built before this date with `--paper cream` actually used the white thickness — the Master Your Mind 116-pp cream reference build has a spine 0.026" too narrow (0.261" vs the correct 0.29"); regenerate before any reprint.

Output is a ZIP with:
- `*.pdf` — vector template with guide layers
- `*.png` — raster template at 300 DPI (use this as the composition overlay)

Template zones (color-coded in the PNG):
- **Red / pink** — total bleed trim (do not place live art past here)
- **Yellow** — bleed area (0.125" all outer edges; extend background art into here, no live type)
- **White / clear** — safe area (all type + focal art lives here)
- **Spine rectangle** — pre-measured for the chosen page count; keep text 0.0625" from spine edges
- **Barcode box** — 2" × 1.2" clear area on back cover's lower-right for the ISBN barcode

See [`references/kdp-template-guide.md`](references/kdp-template-guide.md) for the zone measurements cheatsheet.

## Workflow

### 1. Gather inputs

- Trim size (default 6 × 9)
- Final page count
- Paper type (cream/white/color)
- Front cover creative direction (palette, imagery, typography)
- Back cover copy (header, body paragraphs, bullets, bio, pull-line, URL)
- Whether Richard's voice rule applies → strip em dashes (see `/Users/charliedeist/Root/.claude/rules/writing-quality.md`)

### 2. Download KDP template

Ask the user to download the matching template ZIP from KDP. Save to the book's cover-concepts folder as `kdp-template-<pages>p.png` and `.pdf`. The PNG is the overlay you'll align to.

### 3. Generate panels

Use `scripts/gen_openai.py` — OpenAI GPT Image 2, `high` quality.

```bash
export OPENAI_API_KEY=sk-proj-...
python3 scripts/gen_openai.py --prompt "..." --size 1024x1536 --quality high --out front.png
python3 scripts/gen_openai.py --prompt "..." --size 1024x1536 --quality high --out back.png
```

Prompts that worked well for a watercolor-leaf aesthetic live in [`prompts/leaf-cover.md`](prompts/leaf-cover.md). **Always prepend the safe-zone preamble** from that file — without it, models will paint type and ornament right to the panel edge and the alignment check will flag G4 violations downstream.

Other lessons:

- Specify paper hex (`#F3E8CC` warm cream) — model drifts otherwise.
- Call out "NO paper border, NO trompe-l'oeil paper within paper" — otherwise it renders a paper-on-paper.
- Spell out EVERY typography element and explicitly forbid everything else: "No author credentials line. No byline. No publisher mark. No URL. No tagline." The model loves to add garbled extra text.
- For back covers with lots of copy, break layout into numbered sections and give each a one-line visual instruction. Anchor every block in absolute pixel coordinates (`x:150–874, y:150–1386`) — "industry-standard margins" is too loose.
- Em dashes: replace with parens or commas per RLM voice rule.
- Pass an existing cover as `--references` if iterating on one.

### 4. Run the full pipeline

The end-to-end orchestrator does template generation, panel fitting, wrap composition, and alignment check in one shot:

```bash
python3 scripts/pipeline.py \
  --front front.png --back back.png \
  --trim 5.5x8.5 --pages 116 --paper cream --dpi 300 \
  --title "MASTER YOUR MIND" --author "DR. RICHARD LOUIS MILLER" \
  --outdir /path/to/output
```

Outputs in `--outdir`:
- `template-<tag>.png` — synthetic KDP template (zones color-coded)
- `wrap-<tag>.png` — composited print-ready wrap
- `report-<tag>.json` — per-gate pass/fail
- `diff-<tag>.png` — annotated wrap with violations marked in red

Or run the steps individually with `compose_wrap.py` (use `--bleed-px` and `--clear-barcode` flags) and then `alignment_check.py`.

### 5. Read the alignment report

Four compliance gates (G1-G4):

- **G1 — dimensions**: wrap matches template canvas exactly. If FAIL, panels were sized wrong; rerun pipeline.
- **G2 — bleed extension**: outer 0.125" band is paper color on all sides. If FAIL, bleed didn't extend; check `compose_wrap.py --bleed-px`.
- **G3 — barcode keepout**: lower-right 2"×1.2" of back cover is clean. If FAIL, regenerate back without art there OR use `--clear-barcode` flag.
- **G4 — safe-margin text**: no dark "text-like" pixels in the 0.25" band inside trim. If FAIL, the panel has type too close to the edge — regenerate with the safe-zone preamble (see step 3).

G4 has a known false-positive class: dark sumi-e ink branches that legitimately cross into the safe-margin band. Eyeball the diff PNG to distinguish ornament from text before acting.

### 6. Export for KDP

- Flatten to single layer, RGB (KDP accepts both RGB and CMYK; RGB is simpler).
- Export at 300 DPI minimum.
- PDF/X-1a or PNG both accepted; PDF is preferred.

## Claude Design interplay (validated 2026-06-11, The Intuitive Shepherd)

Claude Design is a complementary front-end, not a competing pipeline. Division of labor:

- **Claude Design owns iteration**: live preview, tweak toggles (guides/template overlays), spine-calculator widgets, verifier agents, sending a look to the client. Its value is the loop, not the artifact.
- **This skill owns geometry + export**: the artifact is plain HTML/CSS; print-exact PDF comes from headless Chrome locally — never ask Claude Design "for the export."

Working pattern:

1. **Prep a kit folder** before the Claude Design session: template PNG from `make_template.py`, a `text-elements.md` with verbatim copy, placeholder images, and a prompt specifying exact panel px (e.g. 1688 × 2625 per panel @ 5.5×8.5 trim), safe insets, and the 600×360 barcode keepout. Claude Design respects absolute pixel specs well.
2. **Fetch the handoff bundle**: `api.anthropic.com/v1/design/h/<id>` is a gzipped tar — `curl -sL … -o b.bin && tar -xzf b.bin`. Read `chats/chat1.md` first (locked decisions live there), then the `.dc.html`.
3. **Strip to a static print file**: the `.dc.html` is a mockup (scaled preview frame, calculator, spec sheet). Copy just the wrap layers into a static HTML with the spine width baked in. A design built panel-per-image converts to a full-span single image by moving the `<img>` out of the panels to a wrap-level layer with explicit width/left/top — panels keep only scrims and text.
4. **Export with `scripts/html_wrap_to_pdf.mjs`** (see Gotchas below for why plain `--print-to-pdf` isn't enough).
5. Compositional tweaks to an established design (move art, swap image structure) are faster done locally with screenshot iteration than another Claude Design round trip. Go back to Claude Design when the *client* needs to react to options.

## Full-bleed art covers — gate false-positives

G1/G2/G3 were written for flat-paper-color covers (MYM). On a full-bleed art cover:

- **G1** may report height 2626 vs your 2625: `make_template.py` rounds 0.125" bleed to 38 px and doubles it; true KDP height is trim+0.25" exactly (8.75" → 2625 px). Your file is right.
- **G2/G3** sample "paper color" from the bleed band — on dark art they sample the art and flag everything. Verify directly instead: barcode keepout std ≈ 0 (`np.std` over the plate region) and 0% near-white pixels in all four 38-px bleed bands. G4 (safe-margin text) remains trustworthy as-is.

## Deterministic text panels (back cover) — validated 2026-06-23 (Guide Abrégé)

For a **text-heavy back cover** (blurb + small photo + imprint), skip GPT Image entirely and compose the panel in **HTML/CSS rendered locally** — pixel-exact type, no AI text garble, instant iteration:

- Build `back.html` with `body{width:1800px;height:2700px}` (trim @300dpi), then render a pixel-exact PNG with Chrome **`--screenshot`** (NOT print-to-pdf):
  `Chrome --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1800,2700 --screenshot=back.png file://…/back.html`
- **Left-align the body copy.** Centered back-cover paragraphs read awkward; a left-aligned text block with a centered/left hero line looks like a real book.
- **Keep ALL content above the barcode keepout.** On the back panel the barcode box is lower-right ≈ `x:1125–1725, y:2265–2625` (panel coords; from `make_template.py` output, subtract the 38px bleed offset). Put ONLY the bottom-left imprint in the lower band; everything else (plate, repertoire line, body) must end above y≈2230. `compose_wrap --clear-barcode` **fills that box with paper color**, so anything you place there gets erased — a centered full-width line or a centered plate will get its right edge clipped.
- Type sizes @300dpi: body ≈ 47–49px (~11–11.5pt) reads well; <35px (~8pt) is too small for a back cover.

**Front from an existing flat cover image** (don't regenerate): `sips -z 2700 1800 cover.jpg --out front.png` to fit trim, then `compose_wrap … --bleed-px 38` extends the bleed (a solid cream/paper background extends cleanly).

**Env:** the image venv (see memory `reference_image_edit_gemini_gpt_recipe`) needs **`numpy`** for `alignment_check.py` (`pip install numpy`); `make_template.py`/`compose_wrap.py` run on Pillow alone.

## Scripts

- [`scripts/gen_openai.py`](scripts/gen_openai.py) — GPT Image 2 wrapper (needs `OPENAI_API_KEY`, requires verified org)
- [`scripts/make_template.py`](scripts/make_template.py) — generate synthetic KDP template PNG from trim+pages+paper+dpi
- [`scripts/compose_wrap.py`](scripts/compose_wrap.py) — Pillow wrap composer; pass `--bleed-px` and `--clear-barcode` for print-ready output
- [`scripts/alignment_check.py`](scripts/alignment_check.py) — G1-G4 compliance check, annotated diff PNG
- [`scripts/pipeline.py`](scripts/pipeline.py) — end-to-end: template → fit → compose → check
- [`scripts/html_wrap_to_pdf.mjs`](scripts/html_wrap_to_pdf.mjs) — HTML wrap artboard → single-page print-exact PDF (playwright-core via agent-browser; patches MediaBox to exact points)

## Known gotchas

- **HTML → print-exact PDF (2026-06-11):** build the artboard in 300-DPI pixels, then print via a CSS scale of 0.32 (300 → 96 css-dpi) inside a fixed-size clipping container — `transform: scale()` changes paint but NOT layout size, so without an `overflow: hidden` page container the wrap paginates into 3 pages. Chrome quantizes fractional-inch page sizes by ±0.48 pt (1/150") no matter how they're specified (`@page` in/px, or printToPDF paperWidth) — patch the `/MediaBox` bytes to the exact points afterward (same-length replacement keeps the xref valid). Both handled by `scripts/html_wrap_to_pdf.mjs`.

- **OpenAI org must be verified** to use `gpt-image-2`. Returns 403 otherwise; verify at `platform.openai.com/settings/organization/general`.
- **Python 3.9 compat** — scripts use `from __future__ import annotations` so `list[Path] | None` parses on the macOS system Python.
- **Don't `source` `OpenEd Vault/.env` in a wrapper** — unquoted-path values blow up bash. Use `grep + cut` to extract just `OPENAI_API_KEY`.
- **Spine typography at <128 px** is hard — auto-scale title/author by spine width ratio (0.42 / 0.24 worked for 115 px).
- **DPI check:** 1024×1536 panels at 6×9 trim = 170 DPI. KDP requires 300 DPI. Regenerate large for the print build; keep small files for review loops.

## Reference state — Master Your Mind (last updated 2026-04-24)

Trim is **5.5 × 8.5** (Digest), 116 pages, cream paper. Confirmed via `pdfinfo` on the print PDF (page size 396×612 pts).

Working files at `Creative Intelligence Agency/clients/rlm/studio/books/master-your-mind/cover-concepts/gpt2-20260421/`:

- `mym-leaf-gpt2-v5-golden-hour.png` — approved front (panel only, has G4 violations at top: author lockup too high)
- `mym-leaf-gpt2-back-v1.png` — approved back (panel only, has G4 violations: URL footer + section header outside safe area)
- pipeline output dir at `kdp-pipeline-out-5.5x8.5-116p/` — current wrap, template, report, diff

**Pipeline state as of 2026-04-24:**
- G1 ✓ dimensions match (3454×2626)
- G2 ✓ bleed extends correctly
- G3 ✓ barcode keepout clean (via `--clear-barcode`)
- G4 ✗ safe-margin text — 16,070 px violations (4.4× over threshold). Mix of real text-too-close-to-edge and false positives from sumi-e branches.

**Next session pickup:**
1. Regenerate panels using updated `prompts/leaf-cover.md` with safe-zone preamble (forces type inside `x:150–874, y:150–1386`)
2. Re-run `pipeline.py`; confirm G4 drops to <threshold for text-class violations (sumi-e false positives are acceptable)
3. Once all four gates pass, regenerate at 1800×2700 for full 300 DPI print build
4. Hand to Inner Traditions production via Ashley Kolesnik
