---
name: spin-design
description: Scaffold a self-contained design-handoff subfolder inside the current project, then hand off to an open-ended Claude Design session. Use when the user says "spin up a design folder", "/spin-design", "prepare a design subfolder", "make a design handoff", "kick off a Claude Design session for this", or wants to design/redesign a cover, interior, page, brand, or visual asset and needs the package + brief assembled. Infers the design objectives from the current conversation.
---

# spin-design

Shorthand for "prepare a design subfolder within this project." It packages everything a **Claude Design** session needs — a basic design package plus a README and a paste-ready brief — with the **specific objectives inferred from the current conversation**, then points the user at it to start an open-ended design session.

The model for the output folder is the proven `CIA/publishing/Guide Abrege/_claude-design-prep/` package (README + DESIGN-PROMPT + manuscript/asset references + reference images).

## When invoked

`/spin-design [optional: subfolder name or short topic]`

## What to do

### 1. Resolve the project + target
- The project = the folder the conversation is about (the cwd, or the path most recently discussed). Confirm if ambiguous.
- The design target = what we're designing (cover, book interior, landing page, brand system, a single page, a deck…). **Infer it from the conversation** — do not ask if the chat already makes it obvious.

### 2. Create the subfolder
- Default location: `<project>/design-<slug>/` where `<slug>` comes from the arg or the inferred target (e.g. `design-cover`, `design-interior`, `design-landing`). If the project already has a design-prep convention (`_claude-design-prep/`, `design/`), match it.
- Never overwrite an existing folder — if it exists, add a dated sibling or ask.

### 3. Populate it (the "basic design package")
Write these files, filling them with specifics inferred from the conversation — not generic boilerplate:

- **`README.md`** — what this folder is; the design target in one line; the **inferred objectives** (a tight bulleted list pulled from what the user actually said in chat — aesthetic direction, what to keep, what to change, constraints, audience, format/trim); what's in the folder; and the one-line "how to start" (open a Claude Design session here / paste DESIGN-PROMPT.md).
- **`DESIGN-PROMPT.md`** — the paste-ready, **open-ended** kickoff prompt for the Claude Design session. State the goal, the inferred objectives, the constraints, the references included, and "what to produce" — but leave room for the designer to explore (open-ended, not a rigid spec). End with the deliverables list.
- **Copy in the real package** — duplicate (don't symlink) the relevant existing assets so the folder is self-contained:
  - current design artifacts if any (existing cover/`cover.jpg`, `*.css`, current PDF/page, brand files),
  - the content the design serves (manuscript excerpt, copy, product description),
  - reference images discussed in the chat (e.g. a photo to incorporate, a style reference),
  - any house style / typography notes.
  If an asset is large or lives elsewhere, copy it in anyway (self-contained beats tidy) unless it's huge (>50MB) — then reference its path in the README.

### 4. Hand off
Report: the folder path, a one-line summary of the inferred objectives, the list of files created, and the next step ("Start a Claude Design session pointed at this folder, or paste `DESIGN-PROMPT.md`"). Offer to open the README in Typora.

**When the design comes back** (you're handed a `claude_design` project to implement): see memory `reference_claude_design_mcp_roundtrip` — `render_preview`→`serve_url`→headless-Chrome `--print-to-pdf` for a faithful PDF; `read_file` output is entity-escaped + `<x-dc>`/`<helmet>`/`support.js`-wrapped (unescape once + strip to edit locally); and `write_files` base64 friction means **edit + render LOCALLY for the deliverable**, don't try to sync the full design back.

## Rules
- **Infer, don't interrogate.** Pull objectives from the conversation. Ask at most one clarifying question, and only if the target is genuinely unclear.
- **Self-contained.** The folder should let a fresh Claude Design session start cold with no other context.
- **Open-ended brief.** The DESIGN-PROMPT states goals + constraints + references, then invites exploration — it is not a pixel spec.
- **Don't design here.** This skill assembles the handoff; the actual design happens in the Claude Design session it kicks off.
