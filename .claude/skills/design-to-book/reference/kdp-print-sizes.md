# KDP Print-Size Reference

*Working reference for the Cross & Plough / CLM pamphlet program. Trim sizes, page-count math, margins, and spine width for Amazon KDP paperbacks. Numbers marked ⚠︎ are KDP policy values that drift — confirm against [kdp.amazon.com](https://kdp.amazon.com/en_US/help/topic/G201834180) before a final upload.*

---

## 1. The decision for this book

| | |
|---|---|
| **Title** | *The Catholic Land Movement* (McNabb + Shove, fwd. Chesterton) |
| **Trim** | **4.25 × 6.87 in** — mass-market pocket-pamphlet |
| **Interior** | **Black ink on cream paper** (cheapest; cream = warm devotional stock) |
| **Body type** | Cormorant Garamond 12 pt / 16.6 pt leading |
| **Result** | **54 pages** (clears the 30-page goal with room to spare) |

---

## 2. Trim sizes that fit a pamphlet (small end)

KDP's smallest supported trims. All accept black-ink interiors on white or cream.

| Trim (in) | Nickname | Body words/pg* | 7,900-word book ≈ | Feel |
|---|---|---|---|---|
| **4.25 × 6.87** | Mass-market | ~180–210 | **44–56 pp** | Pocket tract / CTS pamphlet ✅ *(chosen)* |
| 4.37 × 7.0 | — | ~190–215 | 42–52 pp | Slightly taller mass-market |
| 4 × 6 | Pocket | ~150–180 | 50–60 pp | Smallest KDP trim; very tract-like |
| 4.72 × 7.48 | A6-ish | ~210–240 | 38–46 pp | Continental small |
| **5 × 8** | Digest | ~240–270 | **32–38 pp** | Standard small book; more shelf presence |
| 5.06 × 7.81 | — | ~245–275 | 32–37 pp | Close cousin of 5×8 |
| 5.25 × 8 | — | ~255–285 | 30–35 pp | — |
| 5.5 × 8.5 | US Trade | ~290–330 | 26–30 pp | Tighter to 30-pg floor; needs larger type |

\* *Body words per page assume a serif body (Cormorant/Garamond class) at ~11–12 pt with comfortable leading and prose paragraphs. Lower the estimate for generous leading, block quotes, scripture epigraphs, and section openers that each burn part of a page — this pamphlet runs ~145 effective wpp once those are counted, which is why 7,900 words → 54 pp.*

> **Rule of thumb to hit a page target:** `pages ≈ word_count ÷ words_per_page`, then **add ~1 page per section opener** (each starts on a fresh page and eats whitespace). Drop the trim size or raise the type size to add pages; raise the trim or shrink type to cut them.

---

## 3. Full standard KDP trim list (reference)

The common ones you'll actually choose from, largest selection in **bold**.

| Small / pocket | Standard | Large / workbook |
|---|---|---|
| 4 × 6 | **5 × 8** | 7 × 10 |
| 4.25 × 6.87 | 5.06 × 7.81 | 7.44 × 9.69 |
| 4.37 × 7 | **5.25 × 8** | 7.5 × 9.25 |
| 4.72 × 7.48 | **5.5 × 8.5** | 8 × 10 |
| 5.83 × 8.27 (B-fmt) | **6 × 9** | 8.5 × 11 |
| — | 6.14 × 9.21 | 8.27 × 11.69 (A4) |
| — | 6.69 × 9.61 | 8.5 × 8.5 (square) |

*Devotional / Catholic small-press house default: **4.25 × 6.87** for tracts & pamphlets, **5.5 × 8.5** for full books, **6 × 9** for anthologies.*

---

## 4. Page-count limits ⚠︎

| Interior | Min | Max |
|---|---|---|
| Black ink, **cream** paper | 24 | 828 |
| Black ink, **white** paper | 24 | 828 |
| Premium color, white paper | 24 | 828 |
| Standard color, white paper | 72 | 600 |

- **Minimum 24 pages** for any paperback. A 7,900-word pamphlet clears this at every trim above.
- Page count must be **even** (KDP pads to a blank verso if odd — better to design to an even count yourself).
- A printed spine that holds **text/title** needs **≥ 79 pages** (≥ 0.0625″ spine). Below that, the spine stays blank — fine for a thin pamphlet like this one (54 pp).

---

## 5. Margins & gutter ⚠︎

**Outside margins** (top, bottom, outer): minimum **0.25″** with no bleed; **0.375″** is safer and looks less cramped on a small trim.

**Inside / gutter margin** scales with page count (thicker book = more curl into the spine):

| Page count | Min gutter |
|---|---|
| 24–150 | 0.375″ |
| 151–300 | 0.5″ |
| 301–500 | 0.625″ |
| 501–700 | 0.75″ |
| 701–828 | 0.875″ |

*This book (54 pp) sits in the 0.375″ tier. The interior CSS uses a mirrored 0.58″ inside / 0.42″ outside — comfortably above minimum.*

**Bleed:** only if art runs to the page edge. Add **0.125″** beyond trim on the three outer sides and size the page to trim + bleed. This pamphlet has no full-bleed art, so **no bleed** is needed.

---

## 6. Spine width (for the cover wrap) ⚠︎

`spine_width (in) = page_count × paper_thickness_per_page`

| Paper | Thickness / page |
|---|---|
| Black ink, **cream** 60 lb | 0.0025″ |
| Black ink, **white** 60 lb | 0.002252″ |
| Color (premium) | 0.002347″ |

**This book:** 54 pp × 0.0025″ (cream) = **0.135″ spine.** Too thin for spine text — design the cover as front + back with a blank/rule-only spine.

**Full cover-wrap width** = `bleed + back_cover + spine + front_cover + bleed`
= `0.125 + 4.25 + 0.135 + 4.25 + 0.125` = **8.885 × 7.12 in** (trim height 6.87 + 0.125 × 2 bleed).

---

## 7. Build pipeline (how the interior is produced)

CSS → Paged.js → print-ready PDF (the "InDesign substitute"). Rebuild is a script, not an AI pass — **0 tokens per rebuild.**

```
manuscript.md            ← words (edit freely)
  └ src/rethread.mjs      ← rules: markdown → design-classed HTML
  └ design/clm.css        ← look: Cross & Plough type + 4.25×6.87 @page geometry
  └ src/pdf.mjs           ← Paged.js via headless Chrome → out/book.pdf
```

Run: `npm run flow` (rethread → build flow.html → render PDF).
Full pipeline notes: `publishing/LAYOUT-PIPELINE-DOC-20260613.md`.

---

*Sources: KDP Paperback Submission Guidelines & print-cost/spine calculators. Policy numbers (⚠︎) last cross-checked 2026-06-27 — re-verify the page-count maxima, margin tiers, and paper thicknesses on KDP before any production upload, as Amazon revises them periodically.*
