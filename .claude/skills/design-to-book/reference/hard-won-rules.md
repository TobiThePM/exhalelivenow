# Hard-won rules (typography, layout, pagination)

Accumulated production rules from real books (OLR, Guide Abrégé, RPD, Intuitive Shepherd, Hamerton-Kelly, Cross & Plough, Ten Commitments). Merged 2026-07-01 from the home-dir skill copy (`~/.claude/skills/design-to-book`, preserved at `design-to-book.merged-into-root-20260701`). Some overlap the SKILL.md gotchas — kept here in full because the phrasing carries detail. **Do not relearn these.**

## Rendering engine

- **Headless Chrome renders `@page` margin boxes** (running heads + folios via literal content
  + `counter(page)`) — no Prince/Paged.js needed for a basic book. But native Chrome does NOT
  do page-group `:first` (headless chapter openers), `break-before:right`, or
  `counter-reset: page` — a Vellum-style book (per-chapter verso heads, recto part openers,
  roman→arabic folio restart) needs the **Paged.js print path**: see
  `/Users/charliedeist/Desktop/Desktop - Charlie’s Mac mini/Our Lady’s Ranch - Building A Catholic Family Homestead/book/`
  — playwright-core drives Chrome, waits for `window.__pagedDone` (set in `PagedConfig.after`),
  then `page.pdf()`. Plain `--print-to-pdf --virtual-time-budget` truncates mid-pagination with NO error.
- **Paged.js print path gotchas:** (1) inline the CSS into the HTML — Paged.js re-fetches
  `<link>` stylesheets with fetch(), which file:// blocks (silent ProgressEvent, 1-page PDF);
  (2) ONE `string-set` rule per string name — a second rule for the same name silently replaces
  the first's selector (running heads go blank); combine selectors instead;
  (3) front matter (roman) and interior (arabic) as separate documents merged at the end
  beats `counter-reset: page` (off-by-N in Paged.js) — and lets you extract REAL TOC folios from
  the interior render's `data-page-number` attributes, then rebuild the front matter once.
- **MERGE WITH `pdfunite` (or `qpdf --pages`), NEVER Ghostscript `-sDEVICE=pdfwrite`.** gs
  *re-distills* the inputs into a new PDF and **silently drops embedded image XObjects** (logos,
  QR codes, cover art) on some runs — the standalone part-PDFs keep their images, the merged file
  loses them, and a poppler proof of the *standalone* part hides the bug. `pdfunite a.pdf b.pdf
  out.pdf` copies pages losslessly. Verify after merge: `pdfimages -list merged.pdf` must list
  every expected image. (Our Lady's Ranch, 2026-06-17 — cost a full debug cycle.)
- **Cover = its own margin-0 1-page PDF, merged in front (pdfunite).** Chrome's named-page
  `page:` is unreliable; in Paged.js it blanks on big images (resize a web copy).
- **Paged.js (live preview) crashes** ("item doesn't belong to list") on adjacent-sibling
  selectors (`h1 + p`) and `@import` — in `build-preview.mjs` strip the named `@page`, rewrite
  the sibling rule to a `.flush` class, and load fonts via `<link>` not `@import`.
- **Fixed-height boxes clip silently** (no overset warning). **Auto-flow by default**; hand-lay
  only pages you've confirmed fit (cover, title).

## Typography

- **Header hierarchy pops via typeface contrast** (Didone display heads vs Garamond body), not
  size alone.
- **Standard book gutter**: inner margin ~1.0″, outer ~0.65″, mirrored per recto/verso.
- **Body-size floor (validated 2026-06-14, RPD interior):** headless Chrome renders CSS `px` at 96/inch, so `font-size:12px` = **9pt — too small for a trade interior.** Trade body wants ~10.5–12pt (≈14–16px). When a reviewer says "text too small," you're usually under ~11pt — convert px→pt before nudging margins.
- **Trade body must be JUSTIFIED + `hyphens:auto`** — ragged-right (`text-align:left`) reads amateur; justification is the single biggest "industry-standard" tell. (Ten Commitments interior, 2026-07-01.)
- **Margin sidenotes / citations (Tufte pattern):** for a "citations in the outer margin" book, float each note into the outer margin with a negative `margin-right` ≈ (note width + column gap); on a **verso the outer margin is LEFT, on a recto it's RIGHT** — mirror them. A 6×9 trim with a *wide* citation margin forces a narrow measure: big body text and wide notes pull against each other, so either bump the trim (7×10) or slim the margin if both must be large.
- **Two-voice typographic distinction** (anthology / "in their own words" books): set the editor voice and the subject's verbatim in visibly different treatments (editor = italic + thin left-rule / different face; subject = the body face) so a reader never mistakes editorial framing for the subject's words.
- **Running-head house default (Charlie, 2026-06-10): AUTHOR on the verso (upper-left), TITLE
  on the recto (upper-right)** — `@page:left { @top-left { content:"AUTHOR NAME" } }` /
  `@page:right { @top-right { content:"BOOK TITLE" } }`. Chapter-title running heads are the
  opt-in variant, not the default.

## Figures & plates

- **Constrain figures** `max-height` so a tall plate can't overflow + push its caption off-page.
- **Illustration fidelity audit when rebuilding from a source PDF** (validated Guide Abrégé
  2026-06-10): BEFORE trusting an extracted image set, inventory the ORIGINAL page-by-page
  (render + look) and classify every figure FULL-PAGE / LARGE / INLINE — full-page plates in
  the original must be full-page in the rebuild (`.plate-full`: own page, no running head).
  Check three failure modes: (1) figures the extraction MISSED entirely (Guide Abrégé had 2
  full-page plates with no manuscript reference at all); (2) the scan itself missing page
  ranges — verify via running heads/folios, since redrawn figures may trace to pages absent
  from your copy and can't be fidelity-checked; (3) redraws that silently ADDED modern
  annotations not in the original — period fidelity review per figure. Stage recovered
  source crops as `NN-name-SCAN.png` next to the clean set.
- **Wikimedia Commons placeholders**: original-file URLs 429 under curl regardless of UA;
  use the thumb endpoint (`…/commons/thumb/<h>/<hh>/<File>/1280px-<File>`) — first try.
  Name placeholder files for their final subjects so real photos drop in with no code change.
- **Gallery plates** = bare named pages (no running heads/folios), image grids with generous
  white margins + small-caps captions; "PLACEHOLDER — …" prefix in captions until real art.
- **Download X/Twitter images** via `curl` with a browser UA (urllib/default UA → 403).

## Pagination & flow control

- **Orphan/widow pass is a LAST step, every book**: after content + design lock, set
  `p { orphans: 2; widows: 2 }` (Chrome honors these in print), then render pages to PNG and
  scan page tops/bottoms for stranded lines and lonely heads; fix stragglers with targeted
  `break-inside`/`break-after` rules, never by editing the manuscript. The scan is scriptable:
  `pdftotext -layout`, split on `\f`, flag pages whose first body line matches an attribution/
  caption pattern (`^— \(`) or whose last line is a known head.
- **Weld keep-with-next pairs in the RETHREAD, not just CSS**: a quote block + its attribution
  (or image + caption) must be wrapped in one `<div class="msg-unit">` with `break-inside:avoid`
  — `break-before:avoid` on the second element alone is not reliably honored (a date stranded
  at a page top reads as a typo to the author).
- **The density lever — one knob fixes a whole cluster** (OLR, 2026-06-23). When an author wants
  "quotes to sit with their lead-in text," "fill these gaps," and "fewer pages," the highest-leverage
  move is NOT per-page nudging — it's trimming the reading-page `margin-bottom` by ~1 line (e.g. the
  roomy 1.01in → 0.78in on `@page chapter`/`@page intro`). One change: indented quote blocks
  (`break-inside:avoid`) that were a hair too tall to fit after their lead-in now fit and pull up,
  page-bottom gaps fill, the whole book reflows shorter (−8pp on a 273pp book), AND word-breaks
  across page turns disappear. A quote stuck at the top of the next page is almost always "1–2 lines
  too tall for the space left," not a rule bug — give the page those lines.
- **Keep-with-next (`break-after:avoid`) must be SHORT-lead-ins only.** Gluing a colon lead-in to its
  quote is right for "Isaiah beautifully wrote:" but DISASTROUS for a long narrative ¶ that happens to
  end "…and read:" — it drags the whole ¶ + quote to the next page and leaves a half-empty one. Gate on
  text length (≤~120 chars) in the post-process that tags the lead class.
- **Word-breaks across a page turn ("plann-/ing")** have no direct CSS control and are whack-a-mole —
  they shift every reflow. Don't chase them per-instance; the density lever above clears them in bulk.
  Scan with `pdftotext -layout`, split on `\f`, flag any page whose last non-folio line ends in `-`.
- **Blank page before a back-matter section**: push `<section class="pg pg-blank">&nbsp;</section>`
  (bare, no folio) immediately before the section in the rethread — clean "skip a page" separator.
- **TOC on one facing spread (house default, Charlie 2026-06-10)**: chapters + parts + back
  matter only — chapter-level subheads make a TOC sprawl to 3+ pages; keep them in the book,
  drop them from the contents. Start the TOC on a VERSO (`break-before: left`) so its two pages
  face each other as one spread. If a chapters-only TOC UNDERFILLS the spread (small trim,
  few chapters), balance with entry leading/margins — don't reintroduce subentries.
- **Front-matter parity pad only flips one way** (validated Intuitive Shepherd 2026-06-10):
  the `!folios.frontPad` guard in the OLR pdf.mjs loop is load-bearing — once padded, never
  un-pad on the next pass or the state oscillates (pad → even → removed → odd → …).

## Author collaboration

- **An author's marked-up print proof — triage by category before touching anything** (OLR,
  Phil Zeiter, 2026-06-19): STRUCTURAL + TEXT marks port across a rebuild — recto chapter
  starts (`#ch-N { break-before: right }` on the section id; the renderer inserts blank versos
  automatically), word edits, spacing, quote-format fixes. But page-position line-nudges ("move
  the bottom line to the next page") are *aesthetic page-density* calls tied to line positions
  that DON'T survive re-pagination — they're not widow bugs (`orphans/widows:3` already bars
  1–2 line strands), and the moment any structural change reflows the book those page refs are
  dead. Don't port them: apply the structural/text edits, rebuild, ask the author to re-mark the
  nudges on the NEW PDF. Exception: **front matter (roman folios) paginates independently of the
  interior**, so an author's roman-numeral refs (Introduction, etc.) DO survive interior changes
  — act on those directly.
- **Author-controllable spacing markers** (cheap, no CSS edit): a standalone `[[NEWPAGE]]`
  manuscript line → `break-before:page`; `[[GAP]]` → one blank line (`p.vskip{text-indent:0;margin:0}`).
  Mirror the same handler in the rethread loop. Lets the author rebalance a page or separate a
  list of short quotes by editing the markdown, not the stylesheet.

## Manuscript preprocessing

- **Script gotcha — `re.M` + `\s*$` eats the next block.** When regex-converting per-line markup
  in a manuscript (e.g. lifting an inline `(date)` out to its own attribution line), `\s*$` is
  greedy and swallows the trailing blank line(s), gluing the following block (it once ate a
  `# Heading`). Match the token and INSERT `\n\n`; never let the pattern consume trailing whitespace.
- **Headingless pandoc exports (Atticus/Word)**: promote chapter titles to `#` by EXACT-line
  match walked in document order with a sequential pointer — never "short line" heuristics
  (one-word titles like "Culling" collide with note fragments). Renumbering corrupted Word
  list numbers positionally is the one sanctioned exception to "emit the SOURCE number."
- **Scrape-sourced prose is garbled — normalize in the rethread, not by hand.** Archive/Wayback
  text doubles opening quotes (`"'…` → one curly `“`), glues numbered books (`1Thessalonians`),
  and mixes `--`/em-dash. Fix all of it in `inline()`/helpers so one rule covers 100+ chapters.
- **pdftoppm zero-pads page numbers to the doc's digit count** — glob outputs, never
  construct `p-53.png`-style names.
- **Verify, don't assume** — every change, render to PNG and look. This is the real token cost;
  iterate on ONE chapter (`FROM=... TO=... npm run flow`) to keep it cheap.

## Collected-talks template (sermon / lecture / homily) — validated

A talk collection = one talk per `# Title` (each opens on its own page via `.sermon-open
{break-before:page}`), with a metadata line (`date · venue`) and scripture/citation. Two rules
earned on the Hamerton-Kelly sermons (133 talks, 2000–2010):
- **Treat the opener as a "lection zone."** After the title block, a run of *citation lines* and
  *one verse quote* precede the prose. Gate it: `zone=true` until the first prose paragraph;
  only the FIRST quote-leading paragraph inside the zone becomes the `.epigraph` (later quotes
  are ordinary block quotes in the body).
- **Two roles, two consistent styles.** ALL scripture **citations** (the appointed reading under
  the title AND every standalone ref in the body) share one style (centered small-caps); the
  **verse quote** is the other (centered italic, curly quotes). A reader's "why is the Acts line
  different from the Luke line?" means a citation leaked into the wrong bucket.
- Citation detection must be a *whole-line* match anchored with `$` (so prose isn't caught) yet
  tolerant of: space after the colon (`Luke 3: 15-17`), comma/verse lists, trailing period,
  leading dash, a `Scripture:`/`Text:` label, and inline `--Book c:v` attributions split off the
  end of the quote onto their own citation line.

## Facsimile variant (page-for-page reproduction of a scanned original)

When the job is a faithful **facsimile** of an existing scanned publication (not a fresh layout),
the bar changes: each column must **start and end on the same word** as the scan with ~the same
line count. Reference implementation + full method:
`CIA/publishing/CLM Publishing/Cross & Plough/_facsimile_css/` (`LEARNINGS.md`, `MANIFEST.md`).
Key deltas from the normal flow:
- **Explicit columns, never CSS auto-flow** — author the real column break in the content md
  (`+++COL+++`); auto-flow picks its own break and can never be faithful.
- **Markdown threading**: `content/<issue>.md` (marked-up, seeded from the source OCR — don't
  retype) → `src/rethread.mjs` → HTML between THREAD markers. `node render.mjs` runs rethread +
  Chrome→PDF + a **clip-guard** (every HTML word must appear in the rendered PDF raw text — catches
  silent `overflow:hidden` clipping a vision pass misses; normalize hyphenation + folio digit glue).
- **Calibrate type to the scan's line density** (measure lines/column; tune size+leading). A 1930s
  octavo enlarged to 8.5×11 KDP ≈ Cardo 11.8/1.05 body, Libre Caslon display caps.
- **Graphics from a Gemini clean-render**, not PDF crops: screenshot/crop → near-white→transparent
  → drop in `images/`. Keep TEXT as text; only genuinely graphic elements become images.
- **QA workflows**: `facsimile-transcribe.js` (scan+OCR → column markup, one agent/page) and
  `facsimile-wordcheck.js` (STRICT per-column start/end-word + line-count gate). A vision checker
  can false-pass a 1-line clip → the deterministic clip-guard is the backstop.

## Sibling skills (same engine, different template)

`whitepaper`, `one-pager`/`sell-sheet`, `cookbook`/`recipe-card`, `chapbook`/zine, `workbook`,
`bulletin`/program/menu. Pairs with **`kdp-cover-wrap`** (interior → final page count → spine
width → cover). Print-shop layer (crop marks / CMYK / imposition) is a `print-prep` add-on.
See `Creative Intelligence Agency/publishing/print-skill-family-brainstorm.md`.

## Gaps / next (not yet built into the engine)

Per-chapter auto-switching running heads (needs Paged.js `string()`), footnotes floating to
page bottom in flow, auto-TOC/index, CMYK + crop marks for offset/KDP-print. All bolt onto the
same design/content split via one heavier renderer (Prince/Paged.js).
