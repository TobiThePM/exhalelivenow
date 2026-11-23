# Claude Design bundle → book (workflow variant)

Merged 2026-07-01 from the home-dir skill copy (`~/.claude/skills/design-to-book`, preserved at `design-to-book.merged-into-root-20260701`). Use this variant when the design comes from a **Claude Design bundle** instead of a cloned scaffold. Same three-layer decoupling as the main skill.

> **Reference implementation (copy this, don't reinvent):**
> `Creative Intelligence Agency/publishing/Guide Abrege/book/`
> — has `design/`, `content/`, `src/` (build.mjs, rethread.mjs, build-flow.mjs, pdf.mjs,
> reader.js, preview-nav.js, build-preview.mjs), and the docs `README.md`, `PIPELINE.md`,
> `LEARNINGS.md`. Clone its structure for a new book.

> **Collaborative / commentable variant — "Canvas Studio" (Conspire v2):** to make a
> design-to-book render reviewable (a non-technical collaborator leaves comments/suggestions
> that re-anchor across rebuilds), emit a stable **block-manifest** (opaque block ids +
> normalized-text `textHash`) alongside the HTML, anchor comments with layered **W3C selectors**
> (BlockID + fuzzy TextQuote + TextPosition), and re-anchor on rebuild with a **relocation pass**
> (id → intra-block fuzzy → cross-block heal-as-unconfirmed → orphan tray; never CRDT). Working
> reference: `Creative Intelligence Agency/clients/case/Wonderbliss/book-interior/stage/`
> (`lib/{normalize,manifest,anchors,relocate}.mjs`, 28 tests). Plan:
> `Creative Intelligence Agency/conspire/docs/plans/2026-06-04-001-feat-conspire-canvas-studio-plan.md`.

## Architecture

```
manuscript.md  → SOURCE OF TRUTH (edit freely)
   │  src/rethread.mjs   (deterministic JS — maps markdown patterns → HTML with CSS classes)
content/flow-body.html
   │  design/*.css        (the LOOK — from Claude Design; edit one rule, all instances change)
flow.html
   │  headless Chrome --print-to-pdf  (true @page trim; cover merged via pdfunite — lossless)
book.pdf
```
Three independent layers: **words** (md) · **rules** (converter) · **look** (CSS).

## Workflow

1. **Fetch the Claude Design bundle** (it's a gzipped tarball — `curl`, NOT WebFetch):
   `curl -sL https://api.anthropic.com/v1/design/h/<ID> -o bundle.bin && tar -xzf bundle.bin`
   Read `README.md`, then `chats/chat1.md` (intent — which direction the user landed on),
   then the primary HTML + the CSS it imports.
2. **Scaffold** `book/` like the reference: `design/` (the bundle's CSS + an `images.css` that
   swaps `<image-slot>` for real `<img>`), `content/` (the threaded HTML), `src/` (copy the
   reference scripts), `assets/` (real images), `out/`.
3. **Rethread**: point `rethread.mjs` at the manuscript. It maps (the whole "language"):

   | Markdown | → class |
   |---|---|
   | `# Chapter I: Title` | `.chapter-open` (kicker · numeral · title) |
   | `## 13. Title` | `.sec` — **use the DISPLAY/Didone face so heads pop vs body serif** |
   | `### Title` | `.subsec` (small-caps accent subhead) |
   | `1.` `2.` … | `.ord` — **emit the SOURCE number** (`<span class="ord-n">13°</span>`), never a CSS counter (counters reset per `<ol>` → "1° 1° 1°") |
   | `- ` `* ` | `.tiret` (em-dash list) |
   | `\| … \|` | `.session` table (parse header/sep/body rows) |
   | `![](images/x.png)` | `.plate` figure (rewrite `images/`→`assets/`) |
   | `***` | `.break` (asterism) |
   | `**b**` `*i*` `« »` | inline, kept literally |

4. **Build + render**: `npm run flow` → `out/book.pdf`. `npm run live` → live page-turning
   Paged.js preview. Verify by **rendering pages to PNG and looking** (`pdftoppm` + view).

## Commands (all zero-token)

```bash
npm run flow     # whole manuscript → PDF (cover + interior, merged)
npm run live     # live page-turning preview (Paged.js) — open in a browser
npm run pdf      # hand-laid sample pages → PDF
FROM='# Chapter II: ...' TO='# Chapter III:' npm run flow   # one chapter (cheap iteration)
```

## Token economics

Rebuild = 0 tokens (it's a script). Editing text = 0. Restyle/add-rule = a few tokens, once.
The cost is design decisions + visual verification — so lock the rules + CSS, then the user can
edit markdown forever and regenerate free.
