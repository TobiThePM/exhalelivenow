"""
gpt-image-2 helper for the Adverse Effects book campaign.
Released by OpenAI 2026-04-21. Image API, not Responses API — simpler for one-shot generation.

Usage:
    export OPENAI_API_KEY=sk-...
    python imagegen.py --prompt "..." --out images/generated/my-output.png
    python imagegen.py --prompt "..." --size 1024x1536 --quality high --out ...
    python imagegen.py --prompt "..." --references cover.png otherref.png --out ...

Quality/size reference (gpt-image-2 pricing as of launch):
    low    1024x1024  $0.006    — drafts, thumbs, iteration
    medium 1024x1024  $0.053    — default for social posts
    high   1024x1536  $0.165    — press-kit hero, print-bound
"""

from __future__ import annotations
import argparse, base64, os, sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai>=1.0 first")


def generate(prompt: str, out: Path, size: str, quality: str, references: list[Path] | None):
    client = OpenAI()
    if references:
        result = client.images.edit(
            model="gpt-image-2",
            image=[open(p, "rb") for p in references],
            prompt=prompt,
            size=size,
            quality=quality,
        )
    else:
        result = client.images.generate(
            model="gpt-image-2",
            prompt=prompt,
            size=size,
            quality=quality,
        )
    b64 = result.data[0].b64_json
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    print(f"wrote {out} ({len(b64)//1024} KB base64, size={size}, quality={quality})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--size", default="1024x1024")
    ap.add_argument("--quality", default="medium", choices=["low", "medium", "high", "auto"])
    ap.add_argument("--references", nargs="*", type=Path, default=None,
                    help="Reference image paths for compositional editing")
    args = ap.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY in your environment")
    generate(args.prompt, args.out, args.size, args.quality, args.references)
