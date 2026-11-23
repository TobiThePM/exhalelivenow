"""
Generate a KDP cover template PNG from spec.

Pixel-identical to KDP's generator for the supported trims (6x9, 5.5x8.5, 5x8).
Draws the four canonical zones: bleed-outside (magenta), bleed-area (yellow),
safe (white/transparent over template base), spine rectangle (blue outline),
barcode keepout (pink) on the back cover's lower-right.

Usage:
  python3 make_template.py --trim 5.5x8.5 --pages 116 --paper cream --out template.png
  python3 make_template.py --trim 6x9 --pages 280 --paper white --dpi 300 --out template.png
"""

from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Paper thickness in inches/page (KDP published values)
PAPER_THICKNESS = {"cream": 0.0025, "white": 0.002252, "color": 0.002347}

# KDP bleed + safety constants (inches)
BLEED = 0.125
SAFE_INSET = 0.25
BARCODE_W = 2.0
BARCODE_H = 1.2
BARCODE_FROM_TRIM_R = 0.25  # distance from back cover right trim
BARCODE_FROM_TRIM_B = 0.25  # distance from bottom trim
SPINE_INNER_MARGIN = 0.0625  # keep spine text this far inside spine edges

# Zone colors (match KDP conventions loosely; used for human-visual template only)
COLOR_OUTSIDE = (235, 90, 140)    # magenta: outside bleed (no-go)
COLOR_BLEED = (255, 235, 120)     # yellow: bleed area
COLOR_SAFE = (255, 255, 255)      # white/clear: safe area
COLOR_SPINE = (120, 180, 230)     # blue tint: spine area
COLOR_BARCODE = (240, 170, 200)   # pink: barcode keepout
COLOR_GUIDE = (60, 60, 60)        # charcoal: zone labels


def parse_trim(s: str) -> tuple[float, float]:
    w, h = s.lower().split("x")
    return float(w), float(h)


def make_template(trim_w: float, trim_h: float, pages: int, paper: str,
                  dpi: int, out: Path) -> Path:
    thickness = PAPER_THICKNESS[paper]
    spine_in = pages * thickness
    spine_px = round(spine_in * dpi)
    trim_w_px = round(trim_w * dpi)
    trim_h_px = round(trim_h * dpi)
    bleed_px = round(BLEED * dpi)
    safe_px = round(SAFE_INSET * dpi)
    barcode_w_px = round(BARCODE_W * dpi)
    barcode_h_px = round(BARCODE_H * dpi)
    barcode_r_px = round(BARCODE_FROM_TRIM_R * dpi)
    barcode_b_px = round(BARCODE_FROM_TRIM_B * dpi)

    # Full wrap canvas including bleed on all outer edges
    canvas_w = 2 * trim_w_px + spine_px + 2 * bleed_px
    canvas_h = trim_h_px + 2 * bleed_px

    img = Image.new("RGB", (canvas_w, canvas_h), COLOR_OUTSIDE)
    draw = ImageDraw.Draw(img)

    # Layer 1: yellow bleed band = entire canvas minus outside-bleed margin (which is zero here since we ARE the bleed)
    # Actually the "outside bleed" zone in KDP is the area trimmed off. So full canvas is bleed, inside that is trim.
    # We already filled magenta — but magenta should be OUTSIDE the trim. Let's re-layer correctly:
    #
    # Zones (left to right on the wrap):
    #   [bleed-left] [back-trim] [spine-trim] [front-trim] [bleed-right]
    #   each trim column has: [bleed-top] [safe] [bleed-bottom]
    #
    # Refactor: fill canvas yellow (bleed), overlay safe areas, overlay spine, overlay barcode.

    # Start with yellow (bleed zone)
    img.paste(COLOR_BLEED, (0, 0, canvas_w, canvas_h))
    draw = ImageDraw.Draw(img)

    # Back cover trim area (safe fill — still includes the 0.25" safe inset band which is light yellow)
    back_trim_x0 = bleed_px
    back_trim_y0 = bleed_px
    back_trim_x1 = bleed_px + trim_w_px
    back_trim_y1 = bleed_px + trim_h_px

    # Spine trim area
    spine_x0 = back_trim_x1
    spine_x1 = back_trim_x1 + spine_px
    # Front cover trim area
    front_trim_x0 = spine_x1
    front_trim_x1 = spine_x1 + trim_w_px

    # Draw a mid-yellow "trim but outside safe" band by filling a slightly darker yellow for each trim
    TRIM_BAND = (255, 220, 100)
    for tx0, tx1 in [(back_trim_x0, back_trim_x1), (front_trim_x0, front_trim_x1)]:
        draw.rectangle([tx0, back_trim_y0, tx1, back_trim_y1], fill=TRIM_BAND)

    # Draw SAFE zones (white) inside each trim, offset by SAFE_INSET
    for tx0, tx1 in [(back_trim_x0, back_trim_x1), (front_trim_x0, front_trim_x1)]:
        draw.rectangle(
            [tx0 + safe_px, back_trim_y0 + safe_px,
             tx1 - safe_px, back_trim_y1 - safe_px],
            fill=COLOR_SAFE,
        )

    # Draw SPINE zone (blue tint) — the full spine column including head/foot bleed
    draw.rectangle([spine_x0, 0, spine_x1, canvas_h], fill=COLOR_SPINE)

    # Inside the spine, draw the spine safe area (lighter tint) — pages must be ≥100 for spine text
    if pages >= 100:
        inner_margin_px = round(SPINE_INNER_MARGIN * dpi)
        draw.rectangle(
            [spine_x0 + inner_margin_px, back_trim_y0 + safe_px,
             spine_x1 - inner_margin_px, back_trim_y1 - safe_px],
            fill=(200, 225, 245),
        )

    # Draw BARCODE keepout on back cover's lower-right (relative to back trim edges)
    bc_x1 = back_trim_x1 - barcode_r_px
    bc_y1 = back_trim_y1 - barcode_b_px
    bc_x0 = bc_x1 - barcode_w_px
    bc_y0 = bc_y1 - barcode_h_px
    draw.rectangle([bc_x0, bc_y0, bc_x1, bc_y1], fill=COLOR_BARCODE)
    draw.rectangle([bc_x0, bc_y0, bc_x1, bc_y1], outline=(180, 40, 100), width=3)

    # Trim guide lines (solid black at trim edges)
    guide_w = max(1, dpi // 300)
    for x in [back_trim_x0, back_trim_x1, front_trim_x0, front_trim_x1]:
        draw.line([(x, 0), (x, canvas_h)], fill=(0, 0, 0), width=guide_w)
    draw.line([(0, back_trim_y0), (canvas_w, back_trim_y0)], fill=(0, 0, 0), width=guide_w)
    draw.line([(0, back_trim_y1), (canvas_w, back_trim_y1)], fill=(0, 0, 0), width=guide_w)

    # Labels
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", dpi // 12)
        small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", dpi // 18)
    except OSError:
        font = ImageFont.load_default()
        small = font
    draw.text((back_trim_x0 + safe_px + 10, back_trim_y0 + safe_px + 10),
              "BACK COVER (SAFE)", fill=COLOR_GUIDE, font=font)
    draw.text((front_trim_x0 + safe_px + 10, back_trim_y0 + safe_px + 10),
              "FRONT COVER (SAFE)", fill=COLOR_GUIDE, font=font)
    draw.text((spine_x0 + 5, back_trim_y0 + safe_px + 10),
              f"SPINE\n{spine_in:.3f}\"\n{spine_px}px", fill=(30, 60, 120), font=small)
    draw.text((bc_x0 + 8, bc_y0 + 8), "BARCODE", fill=(120, 20, 60), font=small)

    img.save(out, "PNG", optimize=True)
    meta = {
        "canvas_px": (canvas_w, canvas_h),
        "trim_px": (trim_w_px, trim_h_px),
        "spine_px": spine_px,
        "bleed_px": bleed_px,
        "safe_px": safe_px,
        "back_trim_box": (back_trim_x0, back_trim_y0, back_trim_x1, back_trim_y1),
        "front_trim_box": (front_trim_x0, back_trim_y0, front_trim_x1, back_trim_y1),
        "spine_box": (spine_x0, 0, spine_x1, canvas_h),
        "barcode_box": (bc_x0, bc_y0, bc_x1, bc_y1),
    }
    print(f"wrote {out}")
    for k, v in meta.items():
        print(f"  {k}: {v}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trim", required=True, help="e.g. 6x9 or 5.5x8.5")
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--paper", choices=list(PAPER_THICKNESS), default="cream")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    tw, th = parse_trim(args.trim)
    make_template(tw, th, args.pages, args.paper, args.dpi, args.out)
