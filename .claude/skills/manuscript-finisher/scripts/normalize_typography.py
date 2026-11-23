#!/usr/bin/env python3
"""
Layer-1 deterministic typography fixer (house style + Chicago):
  - straight quotes/apostrophes  ->  curly (' ' " ")
  - spaced em dash ( — )         ->  tight (—)
  - double/triple spaces         ->  single
  - space before , . ; : ! ?     ->  removed

Educator is SmartyPants-style. Skips fenced code blocks. Writes in place.

Usage:  normalize_typography.py file1.md [file2.md ...]
        normalize_typography.py --check file.md   (report counts, no write)
"""
import re, sys

def educate(text):
    n = {"quotes": 0, "dashes": 0, "spaces": 0}
    # tighten spaced em dashes (house style = tight)
    text, c = re.subn(r" *— *", "—", text); n["dashes"] += c
    # opening doubles: start / after whitespace or open-bracket or em dash
    text, c = re.subn(r'(\A|[\s([{<—/])"', r'\1“', text); n["quotes"] += c
    text, c = re.subn(r'"', '”', text); n["quotes"] += c           # remaining = closing
    # opening singles
    text, c = re.subn(r"(\A|[\s([{<—/])'", r"\1‘", text); n["quotes"] += c
    text, c = re.subn(r"'", "’", text); n["quotes"] += c           # remaining = apostrophe/closing
    # collapse runs of spaces (not leading indentation)
    text, c = re.subn(r"(?<=\S)  +", " ", text); n["spaces"] += c
    # space before sentence punctuation
    text, c = re.subn(r" +([,.;:!?])", r"\1", text); n["spaces"] += c
    return text, n

def process(text):
    """Educate prose lines, leave fenced code blocks untouched."""
    out, in_code, totals = [], False, {"quotes": 0, "dashes": 0, "spaces": 0}
    for ln in text.split("\n"):
        if ln.lstrip().startswith("```"):
            in_code = not in_code; out.append(ln); continue
        if in_code:
            out.append(ln); continue
        fixed, n = educate(ln)
        for k in totals: totals[k] += n[k]
        out.append(fixed)
    return "\n".join(out), totals

def main():
    args = sys.argv[1:]
    check = "--check" in args
    files = [a for a in args if not a.startswith("--")]
    grand = {"quotes": 0, "dashes": 0, "spaces": 0}
    for path in files:
        src = open(path, encoding="utf-8").read()
        fixed, n = process(src)
        for k in grand: grand[k] += n[k]
        changed = fixed != src
        tag = "would fix" if check else ("fixed" if changed else "clean")
        print(f"  {tag}: {path}  (quotes {n['quotes']}, dashes {n['dashes']}, spaces {n['spaces']})")
        if not check and changed:
            open(path, "w", encoding="utf-8").write(fixed)
    print(f"TOTAL — quotes {grand['quotes']}, dashes {grand['dashes']}, spaces {grand['spaces']}")

if __name__ == "__main__":
    main()
