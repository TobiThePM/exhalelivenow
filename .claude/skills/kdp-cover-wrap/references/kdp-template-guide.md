# KDP Cover Template — Reference

## Where to get it

1. Go to `kdp.amazon.com/cover-templates`
2. Enter trim size, page count, paper type, binding
3. Download ZIP → contains `.pdf` (vector) + `.png` (raster, 300 DPI)

Or: inside a KDP book setup, "Paperback Content" → "Book Cover" → "Download a template".

## 6 × 9 paperback dimensions at 300 DPI

| Element | Inches | Pixels (300 DPI) |
|---|---|---|
| Trim width (per panel) | 6.000" | 1800 px |
| Trim height | 9.000" | 2700 px |
| Bleed (all outer edges) | 0.125" | 37.5 px (round to 38) |
| Safe margin (inside trim) | 0.25" | 75 px |
| Barcode box (back, lower-right) | 2.0" × 1.2" | 600 × 360 px |
| Barcode position from trim edges | 0.25" right, 0.25" bottom | 75 px, 75 px |

**Full wrap dimensions = `(2 × 1800) + spine_px + (2 × 38)` × `2700 + (2 × 38)`**
= `3676 + spine_px` × `2776`

## Spine width formula

| Paper | Inches/page | Formula |
|---|---|---|
| Cream | 0.002252 | `pages × 0.002252" × 300 dpi` |
| White | 0.0025 | `pages × 0.0025" × 300 dpi` |
| Color (premium) | 0.002347 | `pages × 0.002347" × 300 dpi` |

Examples (cream):
- 200 pages → 0.450" → 135 px
- 250 pages → 0.563" → 169 px
- 300 pages → 0.676" → 203 px
- 400 pages → 0.901" → 270 px

**KDP rounds the spine** — trust the template PNG over the calculator. Spine text appears only on books with 100+ pages.

## Template zone colors (standard KDP PNG)

- **Red / magenta fill outside trim** = do not place any art past here (overflow, trimmed off)
- **Yellow fill between trim and bleed line** = bleed area — background art must extend here, NO live type
- **White / clear area** = safe zone — all type and focal art lives here, ≥ 0.25" from trim
- **Pink/magenta rectangle bottom-right of back cover** = ISBN barcode keepout zone
- **Spine rectangle** (center of wrap) = spine safe area, keep text 0.0625" from spine edges

## Composition checklist

- [ ] Wrap pixel dimensions match template exactly
- [ ] Background art extends edge-to-edge including into bleed (yellow zone)
- [ ] All live typography is inside the safe (white) zone
- [ ] Barcode keepout is clean cream/white
- [ ] Spine text is within spine rectangle with inner margin
- [ ] File flattened, 300 DPI, RGB (or CMYK if grayscale managed)
- [ ] Export as PDF/X-1a or PNG
