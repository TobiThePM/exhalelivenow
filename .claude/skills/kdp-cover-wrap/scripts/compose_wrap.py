"""
Compose a paperback wrap from front + back panels + generated spine.

Panels must be the same size (2:3 portrait). For a 6x9 trim:
  - screen comp: 1024x1536 (~170 DPI)
  - print:       1800x2700 (300 DPI)

Spine width: auto-calculated from page count + paper type, OR pass --spine-px
directly (pull from the KDP template PNG for accuracy, since KDP rounds).

Usage:
  python3 compose_wrap.py --front front.png --back back.png --pages 300 --out wrap.png
  python3 compose_wrap.py --front f.png --back b.png --spine-px 203 --title "..." --author "..."
"""

from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PAPER_HEX = "#F3E8CC"
CHARCOAL = "#1A1915"

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
DIDOT_BOLD_INDEX = 1
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"

PAPER_THICKNESS = {
    "cream": 0.0025,
    "white": 0.002252,
    "color": 0.002347,
}


def make_spine(height: int, width: int, title: str, author: str, paper_hex: str) -> Image.Image:
    """Spine strip: solid paper fill, vertical title at head, author at foot."""
    title_size = max(22, int(width * 0.42))
    author_size = max(14, int(width * 0.24))

    try:
        title_font = ImageFont.truetype(DIDOT, title_size, index=DIDOT_BOLD_INDEX)
    except OSError:
        title_font = ImageFont.truetype(GEORGIA, title_size)
    author_font = ImageFont.truetype(GEORGIA, author_size)

    # Draw horizontally then rotate 90° clockwise:
    #   LEFT of horizontal → TOP (head) of spine
    #   RIGHT of horizontal → BOTTOM (foot) of spine
    h_canvas = Image.new("RGB", (height, width), paper_hex)
    draw = ImageDraw.Draw(h_canvas)

    head_margin = int(height * 0.08)
    foot_margin = int(height * 0.08)

    t_bbox = draw.textbbox((0, 0), title, font=title_font)
    t_h = t_bbox[3] - t_bbox[1]
    draw.text(
        (head_margin, (width - t_h) // 2 - t_bbox[1]),
        title, fill=CHARCOAL, font=title_font,
    )

    a_bbox = draw.textbbox((0, 0), author, font=author_font)
    a_w = a_bbox[2] - a_bbox[0]
    a_h = a_bbox[3] - a_bbox[1]
    draw.text(
        (height - a_w - foot_margin, (width - a_h) // 2 - a_bbox[1]),
        author, fill=CHARCOAL, font=author_font,
    )

    return h_canvas.rotate(-90, expand=True)


def compose(front: Path, back: Path, out: Path,
            pages: int | None, paper: str, spine_px: int | None,
            title: str, author: str, dpi: float, paper_hex: str,
            bleed_px: int = 0, clear_barcode: bool = False,
            trim_w_px: int | None = None, trim_h_px: int | None = None) -> Path:
    """Compose full paperback wrap.

    If bleed_px > 0, treats panels as TRIM size and adds bleed on outer edges of
    the wrap (back's left/top/bottom, front's right/top/bottom, spine top/bottom)
    by edge-stretching. Panels paste at (bleed, bleed) and (bleed+trim+spine, bleed).

    If bleed_px == 0, panels are pasted edge-to-edge with the spine between (legacy
    behavior — screen comps only, not print-ready).
    """
    front_img = Image.open(front).convert("RGB")
    back_img = Image.open(back).convert("RGB")
    if front_img.size != back_img.size:
        raise SystemExit(f"front {front_img.size} != back {back_img.size} — resize first")
    w, h = front_img.size

    if spine_px is None:
        if pages is None:
            raise SystemExit("provide either --spine-px or --pages")
        thickness = PAPER_THICKNESS[paper]
        spine_in = pages * thickness
        spine_px = round(spine_in * dpi)
        print(f"pages={pages} paper={paper} spine={spine_in:.3f}\" width={spine_px}px @ {dpi:.0f}dpi")

    if bleed_px > 0:
        # Panels are trim-size. Build wrap canvas = 2*trim + spine + 2*bleed wide,
        # trim + 2*bleed tall. Paste panels at (bleed, bleed) and
        # (bleed+trim+spine, bleed). Extend bleed zones by edge-stretching from
        # each panel's outermost pixel rows/cols.
        canvas_w = 2 * w + spine_px + 2 * bleed_px
        canvas_h = h + 2 * bleed_px
        wrap = Image.new("RGB", (canvas_w, canvas_h), paper_hex)
        back_x = bleed_px
        front_x = bleed_px + w + spine_px
        inner_y = bleed_px

        wrap.paste(back_img, (back_x, inner_y))
        wrap.paste(front_img, (front_x, inner_y))

        # Bleed-fill LEFT edge from back's left column
        left_col = back_img.crop((0, 0, 1, h)).resize((bleed_px, h), Image.NEAREST)
        wrap.paste(left_col, (0, inner_y))
        # Bleed-fill RIGHT edge from front's right column
        right_col = front_img.crop((w - 1, 0, w, h)).resize((bleed_px, h), Image.NEAREST)
        wrap.paste(right_col, (canvas_w - bleed_px, inner_y))
        # Bleed-fill TOP edge from full-width strip (back + spine-paper + front's top row)
        # For simplicity, pull from each panel's top row
        back_top = back_img.crop((0, 0, w, 1)).resize((w, bleed_px), Image.NEAREST)
        front_top = front_img.crop((0, 0, w, 1)).resize((w, bleed_px), Image.NEAREST)
        wrap.paste(back_top, (back_x, 0))
        wrap.paste(front_top, (front_x, 0))
        # Spine top fills paper color (already paper_hex background)
        # Corners: extend from back left col top pixel, front right col top pixel
        tl_color = back_img.getpixel((0, 0))
        tr_color = front_img.getpixel((w - 1, 0))
        bl_color = back_img.getpixel((0, h - 1))
        br_color = front_img.getpixel((w - 1, h - 1))
        # Top-left corner
        for y in range(bleed_px):
            for x in range(bleed_px):
                wrap.putpixel((x, y), tl_color)
        # Top-right corner
        for y in range(bleed_px):
            for x in range(canvas_w - bleed_px, canvas_w):
                wrap.putpixel((x, y), tr_color)
        # Bottom edges
        back_bot = back_img.crop((0, h - 1, w, h)).resize((w, bleed_px), Image.NEAREST)
        front_bot = front_img.crop((0, h - 1, w, h)).resize((w, bleed_px), Image.NEAREST)
        wrap.paste(back_bot, (back_x, canvas_h - bleed_px))
        wrap.paste(front_bot, (front_x, canvas_h - bleed_px))
        for y in range(canvas_h - bleed_px, canvas_h):
            for x in range(bleed_px):
                wrap.putpixel((x, y), bl_color)
            for x in range(canvas_w - bleed_px, canvas_w):
                wrap.putpixel((x, y), br_color)

        # Spine (full height including bleed top/bottom)
        spine_img = make_spine(canvas_h, spine_px, title, author, paper_hex)
        wrap.paste(spine_img, (bleed_px + w, 0))

        # Clear barcode keepout (back cover, lower-right within trim)
        if clear_barcode:
            bc_w = round(2.0 * dpi)
            bc_h = round(1.2 * dpi)
            bc_r = round(0.25 * dpi)
            bc_b = round(0.25 * dpi)
            back_trim_right = bleed_px + w
            back_trim_bottom = bleed_px + h
            bx1 = back_trim_right - bc_r
            by1 = back_trim_bottom - bc_b
            bx0 = bx1 - bc_w
            by0 = by1 - bc_h
            # Pad slightly inward to leave clean keepout
            pad = 4
            ImageDraw.Draw(wrap).rectangle(
                [bx0 - pad, by0 - pad, bx1 + pad, by1 + pad],
                fill=paper_hex,
            )
    else:
        # Legacy: panels pasted edge-to-edge, no bleed
        spine_img = make_spine(h, spine_px, title, author, paper_hex)
        wrap = Image.new("RGB", (w + spine_px + w, h), paper_hex)
        wrap.paste(back_img, (0, 0))
        wrap.paste(spine_img, (w, 0))
        wrap.paste(front_img, (w + spine_px, 0))

    wrap.save(out, "PNG", optimize=True)
    print(f"wrote {out}  {wrap.size[0]}x{wrap.size[1]}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--front", required=True, type=Path)
    ap.add_argument("--back", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--pages", type=int, default=None)
    ap.add_argument("--paper", choices=list(PAPER_THICKNESS), default="cream")
    ap.add_argument("--spine-px", type=int, default=None,
                    help="override spine width in pixels (pull from KDP template for accuracy)")
    ap.add_argument("--title", default="BOOK TITLE")
    ap.add_argument("--author", default="AUTHOR NAME")
    ap.add_argument("--dpi", type=float, default=170.67,
                    help="panel DPI (170.67 for 1024x1536 at 6x9, 300 for print-ready 1800x2700)")
    ap.add_argument("--paper-hex", default=PAPER_HEX)
    ap.add_argument("--bleed-px", type=int, default=0,
                    help="when >0, treat panels as TRIM size and add bleed on outer edges")
    ap.add_argument("--clear-barcode", action="store_true",
                    help="fill the back cover's barcode keepout with paper color")
    args = ap.parse_args()
    compose(args.front, args.back, args.out, args.pages, args.paper,
            args.spine_px, args.title, args.author, args.dpi, args.paper_hex,
            bleed_px=args.bleed_px, clear_barcode=args.clear_barcode)
