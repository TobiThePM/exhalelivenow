"""
End-to-end KDP wrap pipeline.

  panels (1024x1536)   ->  upscale + center-crop to trim-at-DPI
                           ->  compose wrap (back | spine | front) with bleed
                                ->  alignment check against generated template
                                     ->  pass/fail report + annotated diff

If the input panels are already print-size (e.g. 1800x2700), upscaling is skipped.

Usage:
  python3 pipeline.py \\
    --front front.png --back back.png \\
    --trim 5.5x8.5 --pages 116 --paper cream --dpi 300 \\
    --title "MASTER YOUR MIND" --author "DR. RICHARD LOUIS MILLER" \\
    --outdir /path/to/output
"""

from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
from PIL import Image

SCRIPTS = Path(__file__).parent

PAPER_THICKNESS = {"cream": 0.0025, "white": 0.002252, "color": 0.002347}
BLEED = 0.125


def parse_trim(s: str) -> tuple[float, float]:
    w, h = s.lower().split("x")
    return float(w), float(h)


def fit_panel(src: Path, target_w: int, target_h: int, out: Path) -> Path:
    """Upscale with LANCZOS then center-crop to match exact trim + bleed dims."""
    img = Image.open(src).convert("RGB")
    sw, sh = img.size
    target_aspect = target_w / target_h
    src_aspect = sw / sh

    if abs(src_aspect - target_aspect) < 0.001:
        resized = img.resize((target_w, target_h), Image.LANCZOS)
    elif src_aspect > target_aspect:
        # source is wider → scale by height, crop sides
        new_h = target_h
        new_w = round(sw * (new_h / sh))
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        resized = resized.crop((left, 0, left + target_w, target_h))
    else:
        # source is taller → scale by width, crop top/bottom
        new_w = target_w
        new_h = round(sh * (new_w / sw))
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        top = (new_h - target_h) // 2
        resized = resized.crop((0, top, target_w, top + target_h))

    resized.save(out, "PNG", optimize=True)
    print(f"  fit  {src.name}  {sw}x{sh}  →  {target_w}x{target_h}  ({out.name})")
    return out


def extend_bleed(panel: Path, bleed_px: int, out: Path) -> Path:
    """Wrap each panel with bleed by edge-stretching the outermost pixel row/column."""
    img = Image.open(panel).convert("RGB")
    w, h = img.size
    # Build bleed canvas and paste
    bled = Image.new("RGB", (w + 2 * bleed_px, h + 2 * bleed_px))
    bled.paste(img, (bleed_px, bleed_px))
    # Stretch edges into bleed
    # Left
    left = img.crop((0, 0, 1, h)).resize((bleed_px, h), Image.NEAREST)
    bled.paste(left, (0, bleed_px))
    # Right
    right = img.crop((w - 1, 0, w, h)).resize((bleed_px, h), Image.NEAREST)
    bled.paste(right, (w + bleed_px, bleed_px))
    # Top (incl. corners)
    top = bled.crop((0, bleed_px, bled.width, bleed_px + 1)).resize((bled.width, bleed_px), Image.NEAREST)
    bled.paste(top, (0, 0))
    # Bottom
    bot = bled.crop((0, h + bleed_px - 1, bled.width, h + bleed_px)).resize((bled.width, bleed_px), Image.NEAREST)
    bled.paste(bot, (0, h + bleed_px))
    bled.save(out, "PNG", optimize=True)
    print(f"  bleed {panel.name}  +{bleed_px}px  →  {bled.size}  ({out.name})")
    return out


def run(cmd: list[str]) -> None:
    print("  $ " + " ".join(str(c) for c in cmd))
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit(r.returncode)


def main(front: Path, back: Path, trim: str, pages: int, paper: str, dpi: int,
         title: str, author: str, outdir: Path) -> int:
    tw, th = parse_trim(trim)
    thickness = PAPER_THICKNESS[paper]
    trim_w_px = round(tw * dpi)
    trim_h_px = round(th * dpi)
    bleed_px = round(BLEED * dpi)
    spine_px = round(pages * thickness * dpi)
    panel_with_bleed_w = trim_w_px + 2 * bleed_px
    panel_with_bleed_h = trim_h_px + 2 * bleed_px

    outdir.mkdir(parents=True, exist_ok=True)
    tag = f"{trim}-{pages}p-{paper}-{dpi}dpi"
    template_png = outdir / f"template-{tag}.png"
    front_fit = outdir / "front-fit.png"
    back_fit = outdir / "back-fit.png"
    front_bled = outdir / "front-bled.png"
    back_bled = outdir / "back-bled.png"
    wrap_png = outdir / f"wrap-{tag}.png"
    report_json = outdir / f"report-{tag}.json"
    diff_png = outdir / f"diff-{tag}.png"

    print(f"▶ trim {tw}x{th}, pages {pages}, paper {paper}, dpi {dpi}")
    print(f"  trim_px={trim_w_px}x{trim_h_px}, spine_px={spine_px}, bleed_px={bleed_px}")
    print(f"▶ template")
    run(["python3", SCRIPTS / "make_template.py",
         "--trim", trim, "--pages", pages, "--paper", paper, "--dpi", dpi,
         "--out", template_png])

    print(f"▶ fit panels to trim")
    fit_panel(front, trim_w_px, trim_h_px, front_fit)
    fit_panel(back, trim_w_px, trim_h_px, back_fit)

    print(f"▶ compose wrap with bleed and barcode-keepout clear")
    run(["python3", SCRIPTS / "compose_wrap.py",
         "--front", front_fit, "--back", back_fit, "--out", wrap_png,
         "--spine-px", spine_px, "--bleed-px", bleed_px, "--clear-barcode",
         "--title", title, "--author", author, "--dpi", dpi])

    print(f"▶ alignment check")
    r = subprocess.run([
        "python3", str(SCRIPTS / "alignment_check.py"),
        "--wrap", str(wrap_png), "--template", str(template_png),
        "--trim", trim, "--pages", str(pages), "--paper", paper, "--dpi", str(dpi),
        "--out-report", str(report_json), "--out-diff", str(diff_png),
    ])
    print(f"\n▶ deliverables in {outdir}")
    for p in [template_png, wrap_png, report_json, diff_png]:
        print(f"    {p.name}")
    return r.returncode


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--front", required=True, type=Path)
    ap.add_argument("--back", required=True, type=Path)
    ap.add_argument("--trim", required=True)
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--paper", choices=list(PAPER_THICKNESS), default="cream")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()
    raise SystemExit(main(
        args.front, args.back, args.trim, args.pages, args.paper, args.dpi,
        args.title, args.author, args.outdir,
    ))
