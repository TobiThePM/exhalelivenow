"""
Check a composed paperback wrap against a KDP template.

Verifies four compliance gates:
  G1: Wrap dimensions match template canvas exactly
  G2: Paper/background extends into bleed zone (no white/transparent edges at bleed)
  G3: Barcode keepout on back cover is "clean" (matches paper color +/- tolerance)
  G4: No high-contrast "live" pixels in the outer bleed where they'd be trimmed
       (heuristic: reject pixels that aren't in paper-color family along the outer 38px)

Outputs pass/fail + annotated diff PNG showing any violation regions in red.

Usage:
  python3 alignment_check.py --wrap wrap.png --template template.png \\
         --pages 116 --trim 5.5x8.5 --paper cream --dpi 300 \\
         --out-report report.json --out-diff diff.png
"""

from __future__ import annotations
import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

# KDP constants (inches)
BLEED = 0.125
SAFE_INSET = 0.25
BARCODE_W = 2.0
BARCODE_H = 1.2
BARCODE_FROM_R = 0.25
BARCODE_FROM_B = 0.25

PAPER_THICKNESS = {"cream": 0.0025, "white": 0.002252, "color": 0.002347}


def parse_trim(s: str) -> tuple[float, float]:
    w, h = s.lower().split("x")
    return float(w), float(h)


def zones(trim_w: float, trim_h: float, pages: int, paper: str, dpi: int) -> dict:
    spine_px = round(pages * PAPER_THICKNESS[paper] * dpi)
    trim_w_px = round(trim_w * dpi)
    trim_h_px = round(trim_h * dpi)
    bleed_px = round(BLEED * dpi)
    safe_px = round(SAFE_INSET * dpi)
    bc_w = round(BARCODE_W * dpi)
    bc_h = round(BARCODE_H * dpi)
    bc_r = round(BARCODE_FROM_R * dpi)
    bc_b = round(BARCODE_FROM_B * dpi)

    canvas_w = 2 * trim_w_px + spine_px + 2 * bleed_px
    canvas_h = trim_h_px + 2 * bleed_px

    back_trim = (bleed_px, bleed_px, bleed_px + trim_w_px, bleed_px + trim_h_px)
    front_trim = (
        bleed_px + trim_w_px + spine_px,
        bleed_px,
        bleed_px + 2 * trim_w_px + spine_px,
        bleed_px + trim_h_px,
    )
    spine_box = (back_trim[2], 0, front_trim[0], canvas_h)

    # Barcode on back cover (relative to back trim edges)
    bc_x1 = back_trim[2] - bc_r
    bc_y1 = back_trim[3] - bc_b
    bc_x0 = bc_x1 - bc_w
    bc_y0 = bc_y1 - bc_h

    return {
        "canvas": (canvas_w, canvas_h),
        "bleed_px": bleed_px,
        "safe_px": safe_px,
        "back_trim": back_trim,
        "front_trim": front_trim,
        "spine": spine_box,
        "barcode": (bc_x0, bc_y0, bc_x1, bc_y1),
    }


def sample_paper_color(arr: np.ndarray, zones_: dict) -> tuple[int, int, int]:
    """Grab a safe-zone swatch from the back cover as ground-truth paper color."""
    bt = zones_["back_trim"]
    s = zones_["safe_px"]
    y0 = bt[1] + s + 10
    y1 = bt[1] + s + 30
    x0 = bt[2] - s - 30
    x1 = bt[2] - s - 10
    patch = arr[y0:y1, x0:x1]
    return tuple(np.median(patch.reshape(-1, 3), axis=0).astype(int))


def check(wrap_path: Path, template_path: Path, trim_w: float, trim_h: float,
          pages: int, paper: str, dpi: int,
          out_report: Path, out_diff: Path,
          paper_tol: int = 40) -> dict:
    wrap = Image.open(wrap_path).convert("RGB")
    z = zones(trim_w, trim_h, pages, paper, dpi)

    report: dict = {"pass": True, "gates": {}, "zones": z}

    # G1: dimensions
    g1_ok = wrap.size == z["canvas"]
    report["gates"]["G1_dimensions"] = {
        "pass": g1_ok,
        "expected": list(z["canvas"]),
        "actual": list(wrap.size),
    }
    if not g1_ok:
        report["pass"] = False

    arr = np.asarray(wrap)
    paper_rgb = sample_paper_color(arr, z)
    report["paper_rgb_sampled"] = list(map(int, paper_rgb))

    # Build violations mask
    h, w = arr.shape[:2]
    violations = np.zeros((h, w), dtype=bool)

    # G2: outer bleed band should be close to paper color (background extends)
    b = z["bleed_px"]
    paper_arr = np.array(paper_rgb)
    diff = np.abs(arr.astype(int) - paper_arr).max(axis=2)
    outer_band = np.zeros((h, w), dtype=bool)
    outer_band[:b, :] = True
    outer_band[-b:, :] = True
    outer_band[:, :b] = True
    outer_band[:, -b:] = True
    g2_violations = outer_band & (diff > paper_tol)
    g2_count = int(g2_violations.sum())
    g2_ok = g2_count < (h * w * 0.001)  # <0.1% of canvas
    report["gates"]["G2_bleed_extension"] = {
        "pass": g2_ok,
        "violation_px": g2_count,
        "threshold": int(h * w * 0.001),
    }
    violations |= g2_violations
    if not g2_ok:
        report["pass"] = False

    # G4: live type must stay inside safe margin (0.25" inset from trim)
    # We check the 0.25" band INSIDE each trim edge (between trim and safe-inset).
    # Any dark-enough pixel there is assumed to be text/live type that escaped.
    # Dark threshold: luminance < paper_lum - 0.25 (pretty dark vs cream paper).
    s = z["safe_px"]
    paper_lum = (0.299 * paper_rgb[0] + 0.587 * paper_rgb[1] + 0.114 * paper_rgb[2]) / 255
    lum = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]) / 255
    text_like = lum < (paper_lum - 0.25)

    safe_margin_band = np.zeros((h, w), dtype=bool)
    for trim_box in (z["back_trim"], z["front_trim"]):
        tx0, ty0, tx1, ty1 = trim_box
        # Full trim rectangle
        inside = np.zeros((h, w), dtype=bool)
        inside[ty0:ty1, tx0:tx1] = True
        # Inside the safe inset (the subarea that's SAFE for text)
        safe_inset = np.zeros((h, w), dtype=bool)
        safe_inset[ty0 + s:ty1 - s, tx0 + s:tx1 - s] = True
        # Band = inside trim but not in safe inset
        safe_margin_band |= (inside & ~safe_inset)

    g4_violations = safe_margin_band & text_like
    g4_count = int(g4_violations.sum())
    band_px = int(safe_margin_band.sum())
    # Threshold: <0.3% of band contains text-like pixels
    g4_ok = g4_count < band_px * 0.003
    report["gates"]["G4_safe_margin_text"] = {
        "pass": g4_ok,
        "violation_px": g4_count,
        "band_px": band_px,
        "threshold": int(band_px * 0.003),
    }
    violations |= g4_violations
    if not g4_ok:
        report["pass"] = False

    # G3: barcode keepout should be clean (paper color)
    bx0, by0, bx1, by1 = z["barcode"]
    bc_patch = arr[by0:by1, bx0:bx1]
    bc_diff = np.abs(bc_patch.astype(int) - paper_arr).max(axis=2)
    bc_violations_mask = bc_diff > paper_tol
    bc_count = int(bc_violations_mask.sum())
    bc_ok = bc_count < ((by1 - by0) * (bx1 - bx0) * 0.02)  # <2% of keepout
    report["gates"]["G3_barcode_keepout"] = {
        "pass": bc_ok,
        "violation_px": bc_count,
        "keepout_px": (bx1 - bx0) * (by1 - by0),
    }
    full_mask = np.zeros((h, w), dtype=bool)
    full_mask[by0:by1, bx0:bx1] = bc_violations_mask
    violations |= full_mask
    if not bc_ok:
        report["pass"] = False

    # Annotated diff
    annotated = wrap.copy()
    overlay = Image.new("RGBA", wrap.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    vy, vx = np.where(violations)
    if len(vy) > 0:
        # Draw red dots at violations (downsample to keep file small)
        step = max(1, len(vy) // 5000)
        for i in range(0, len(vy), step):
            odraw.ellipse([vx[i] - 2, vy[i] - 2, vx[i] + 2, vy[i] + 2],
                          fill=(255, 0, 0, 180))
    # Draw zone guides
    odraw.rectangle(z["back_trim"], outline=(0, 120, 255, 200), width=3)
    odraw.rectangle(z["front_trim"], outline=(0, 120, 255, 200), width=3)
    odraw.rectangle(z["spine"], outline=(0, 200, 120, 200), width=3)
    odraw.rectangle(z["barcode"], outline=(200, 0, 100, 220), width=4)
    annotated = Image.alpha_composite(annotated.convert("RGBA"), overlay).convert("RGB")
    annotated.save(out_diff, "PNG", optimize=True)

    out_report.write_text(json.dumps(report, indent=2))
    status = "PASS" if report["pass"] else "FAIL"
    print(f"[{status}] report → {out_report}")
    print(f"         diff   → {out_diff}")
    for name, g in report["gates"].items():
        flag = "✓" if g["pass"] else "✗"
        print(f"   {flag} {name}: {g}")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wrap", required=True, type=Path)
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--trim", required=True)
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--paper", choices=list(PAPER_THICKNESS), default="cream")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--out-report", required=True, type=Path)
    ap.add_argument("--out-diff", required=True, type=Path)
    args = ap.parse_args()
    tw, th = parse_trim(args.trim)
    r = check(args.wrap, args.template, tw, th, args.pages, args.paper,
              args.dpi, args.out_report, args.out_diff)
    raise SystemExit(0 if r["pass"] else 1)
