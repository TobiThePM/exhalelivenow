---
name: manuscript-finisher
description: Layered proofread + copyedit for a finished manuscript before layout. A deterministic, zero-token first pass (LanguageTool + Vale) catches spelling/grammar/style/typography; an agent auto-applies the mechanical fixes and surfaces the judgment calls; then parallel subagents run construal-level passes (cross-chapter redundancy + internal consistency, voice/AI-tells, line-level Chicago copyedit). Use when finalizing a book interior, when asked to "proofread / copyedit / finish / clean up the manuscript," enforce a style guide (Chicago), or make punctuation/quoting consistent before typesetting. NOT for drafting or developmental editing.
---

# Manuscript Finisher

Finishing pass for a manuscript that is **content-complete** and headed for layout. The point is to spend tokens only where judgment is needed: cheap local tools do the mechanical work; agents do the thinking.

Default style guide: **Chicago**. Default typography (house): curly quotes/apostrophes (' ' " "), tight em dashes (word—word). Both are configurable in `config/`.

## The four layers (high token-efficiency → high judgment)

### Layer 0 — Deterministic report (zero tokens)
Two local engines, no API:
- **LanguageTool** (`languagetool` CLI) — the open-source "Word grammar & spelling." Grammar, agreement, spelling, comma rules, repeated sentence openers.
- **Vale** (`vale`) — prose **style + consistency**: repeated words, house typography (straight quotes, spaced em dashes), and any custom rules.

Run it:
```bash
python3 scripts/run_lint.py <chapter>.md [more.md ...]      # human report
python3 scripts/run_lint.py --json <chapter>.md             # machine report
```
Output splits every hit into **AUTO** (mechanical, safe) and **REVIEW** (judgment). Spelling is filtered against `config/allowlist.txt` (proper nouns / domain terms — extend it per project; unknown real words flagged once go in here, not into prose changes).

### Layer 1 — Mechanical auto-fix (cheap)
- **Typography** is fixed deterministically (no agent):
  ```bash
  python3 scripts/normalize_typography.py <chapter>.md      # straight→curly, spaced em dash→tight, double spaces, space-before-punct
  python3 scripts/normalize_typography.py --check <file>.md  # preview counts
  ```
- The agent then applies the remaining **AUTO** items from Layer 0 (clear typos, obvious agreement slips), and **leaves every REVIEW item for Layer 2/the human.** Never auto-apply a REVIEW item.

Re-run Layer 0 after fixing; AUTO should drop to ~0, leaving only REVIEW.

### Layer 2 — Agentic construal-level passes (parallel subagents)
Spawn one agent per lens over the **whole manuscript** (not per chapter — these need cross-chapter view). Each returns findings only; it does not edit. Lenses:

1. **Redundancy + internal consistency (macro).** Stories/frameworks/quotes repeated across chapters (full retell vs. callback); names/dates/ages/numbers that contradict each other across chapters (e.g. "three years" vs "five years"; a surgeon named two ways; a place spelled two ways). This is the lens the linters cannot do.
2. **Voice + AI-tells (register).** Does it sound like the author? Run the project's voice spec (for RLM: `rlm-stylometry` + `de-ai-tell`; for non-RLM books the generic AI-tell spec is `.claude/skills/clear-writing/references/forbidden-patterns.md`). Flag staccato piles, correlative "not just X but Y," manufactured framing, post-quote summary, hedge stacks.
3. **Line-level copyedit adjudication (micro).** Take the Layer-0 REVIEW list and rule on each: which LanguageTool/Vale flags are real (apply) vs. false positives or intentional voice (reject, with reason). Enforce Chicago consistency on numbers, hyphenation, serial commas, capitalization.

Orchestrate with the Workflow tool (pipeline by lens) or a `parallel()` Agent fan-out. Keep each agent read-only; collect structured findings.

> **Output cap (learned the hard way):** the copyedit lens must return a **prioritized, capped list (top ~40 APPLY items + grouped REJECT reasons)**, NOT every lint hit verbatim. A full book can produce 150–200+ REVIEW flags; dumping them all exceeds the 32K subagent output limit and the agent dies silently. For exhaustive coverage, page the REVIEW list per-chapter across several agents rather than one agent over the whole book.

### Layer 3 — Synthesis
Merge into one report: **applied** (what Layer 1 + confirmed Layer 2 fixes changed) and **flagged** (judgment calls for the author — name, location, the one-line decision). Mirror of the editor's-log pattern. Then the manuscript is ready for the interior build (`design-to-book` / Paged.js).

## Process (typical run)
```
content-complete chapters
   ↓  normalize_typography.py  (Layer 1 typography)
   ↓  run_lint.py             (Layer 0 report)
   ↓  agent applies AUTO, holds REVIEW   (Layer 1)
   ↓  parallel subagents: redundancy+consistency · voice · copyedit   (Layer 2)
   ↓  synthesis report: applied + flagged   (Layer 3)
   → hand to layout
```

## Config
- `config/.vale.ini` + `config/styles/Manuscript/*.yml` — house typography + repetition rules. Add Chicago/proselint packages with `vale sync` if network/disk allow (optional; the built-ins + custom rules work offline).
- `config/allowlist.txt` — proper nouns/domain terms the spell-checker must not flag. **Extend per book.**

## Notes
- LanguageTool runs on a markdown-stripped, line-preserving copy so line numbers map back to the source.
- House style allows em dashes (set tight); the EN_QUOTES/DASH LanguageTool rules are disabled so they don't fight the normalizer.
- Borrows from: `book-quality-loop` (judge structure), `de-ai-tell` + `rlm-stylometry` (voice/AI-tells; `rlm-stylometry` is a scoped skill at `Creative Intelligence Agency/clients/rlm/.claude/skills/rlm-stylometry/`), the cross-chapter redundancy method from RLM book integration.
