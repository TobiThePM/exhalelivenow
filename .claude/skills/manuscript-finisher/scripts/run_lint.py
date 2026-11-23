#!/usr/bin/env python3
"""
Layer 0 of manuscript-finisher: deterministic, zero-token proofread.

Runs LanguageTool (grammar/spelling, the open-source "Word grammar") + Vale
(style/consistency/typography) on markdown files, filters spelling against a
proper-noun allowlist, and emits one consolidated report split into:
  AUTO   — high-confidence mechanical fixes an agent can apply without asking
  REVIEW — judgment calls to surface

Usage:  run_lint.py file1.md [file2.md ...]
        run_lint.py --json file1.md     (machine-readable)
"""
import json, subprocess, sys, os, re, tempfile

CFG = os.path.join(os.path.dirname(__file__), "..", "config")
ALLOW = set()
with open(os.path.join(CFG, "allowlist.txt")) as f:
    for ln in f:
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            ALLOW.add(ln.lower())

# LanguageTool rules to skip: markdown/whitespace noise + house-style allowances.
LT_DISABLE = "WHITESPACE_RULE,EN_QUOTES,DASH_RULE,ARROWS,MORFOLOGIK_RULE_EN_US_HYPHEN"

AUTO_VALE = {"Manuscript.StraightQuotes", "Manuscript.SpacedEmDash",
             "Manuscript.Repetition", "Vale.Repetition"}
AUTO_LT_CATEGORIES = {"TYPOS"}  # spelling


def strip_md(text):
    """Line-preserving markdown -> text so LT line numbers map back to the source."""
    out = []
    for ln in text.split("\n"):
        s = re.sub(r"^\s{0,3}#{1,6}\s+", "", ln)        # headings
        s = re.sub(r"^\s*>\s?", "", s)                   # quotes
        s = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", s)        # list markers
        s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)    # links -> text
        s = s.replace("*", "").replace("`", "").replace("_", "")
        out.append(s)
    return "\n".join(out)


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def run_lt(md_text):
    stripped = strip_md(md_text)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        tf.write(stripped)
        path = tf.name
    try:
        r = subprocess.run(
            ["languagetool", "--json", "-l", "en-US", "--disable", LT_DISABLE, path],
            capture_output=True, text=True)
        data = json.loads(r.stdout or "{}")
    except Exception as e:
        return [], f"LanguageTool error: {e}"
    finally:
        os.unlink(path)
    hits = []
    for m in data.get("matches", []):
        flagged = m["context"]["text"][m["context"]["offset"]:
                                       m["context"]["offset"] + m["length"]]
        cat = m["rule"]["category"]["id"]
        if cat == "TYPOS" and flagged.strip().lower() in ALLOW:
            continue
        hits.append({
            "engine": "LanguageTool",
            "line": line_of(stripped, m["offset"]),
            "rule": m["rule"]["id"],
            "category": cat,
            "msg": m["message"],
            "flagged": flagged,
            "suggest": ", ".join(x["value"] for x in m.get("replacements", [])[:3]),
            "auto": cat in AUTO_LT_CATEGORIES,
        })
    return hits, None


def run_vale(path):
    r = subprocess.run(
        ["vale", "--config", os.path.join(CFG, ".vale.ini"), "--output=JSON", path],
        capture_output=True, text=True)
    try:
        data = json.loads(r.stdout or "{}")
    except Exception:
        return []
    hits = []
    for _f, alerts in data.items():
        for a in alerts:
            hits.append({
                "engine": "Vale",
                "line": a["Line"],
                "rule": a["Check"],
                "category": a["Check"].split(".")[-1],
                "msg": a["Message"],
                "flagged": a.get("Match", ""),
                "suggest": "",
                "auto": a["Check"] in AUTO_VALE,
            })
    return hits


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    files = [a for a in args if not a.startswith("--")]
    report = {}
    for path in files:
        md = open(path, encoding="utf-8").read()
        lt, err = run_lt(md)
        vale = run_vale(path)
        hits = sorted(lt + vale, key=lambda h: (h["line"], h["engine"]))
        report[path] = {"hits": hits, "error": err}

    if as_json:
        print(json.dumps(report, indent=2))
        return

    for path, res in report.items():
        name = os.path.basename(path)
        hits = res["hits"]
        auto = [h for h in hits if h["auto"]]
        review = [h for h in hits if not h["auto"]]
        print(f"\n{'='*72}\n{name}  —  {len(auto)} auto, {len(review)} review")
        if res["error"]:
            print(f"  ! {res['error']}")
        print(f"{'='*72}")
        if auto:
            print("\n-- AUTO (mechanical, safe to apply) --")
            for h in auto:
                sug = f"  → {h['suggest']}" if h["suggest"] else ""
                print(f"  L{h['line']:<4} [{h['rule']}] “{h['flagged']}”{sug}")
        if review:
            print("\n-- REVIEW (judgment) --")
            for h in review:
                sug = f"  → {h['suggest']}" if h["suggest"] else ""
                print(f"  L{h['line']:<4} [{h['rule']}] {h['msg']}{sug}")
                if h["flagged"]:
                    print(f"        “{h['flagged'].strip()}”")
    tot_a = sum(len([x for x in r['hits'] if x['auto']]) for r in report.values())
    tot_r = sum(len([x for x in r['hits'] if not x['auto']]) for r in report.values())
    print(f"\n{'='*72}\nTOTAL: {tot_a} auto-fixable, {tot_r} to review across {len(report)} file(s)")


if __name__ == "__main__":
    main()
