# Leaf Cover Prompts (watercolor, golden-hour, Penguin Deluxe aesthetic)

Prompts that shipped usable covers for *Master Your Mind* (2026-04-22). Copy and adapt.

## Safe-zone preamble (REQUIRED for KDP-bound panels)

Image models will paint type and ornament right to the edge unless told not to.
KDP trims 0.125" of bleed and considers the next 0.25" inside the trim a no-live-text zone.
At the typical 1024×1536 panel that maps to roughly the **outer 9% of every edge**.

Prepend this block to every front/back panel prompt:

```
SAFE-ZONE CONSTRAINTS (KDP paperback compliance, non-negotiable):

This panel will be trimmed to 5.5" x 8.5" with 0.125" of outer bleed and a 0.25"
"no-live-text" safe inset on all four sides. At 1024 x 1536, that means:

  • Outer ~6% (≈60 px) of every edge is the BLEED zone — paper/background only,
    NO type, NO solitary leaves, NO body of the branch. Bleed is allowed to extend
    color, NOT to carry content.

  • Next ~9% inward (≈90 px) is the SAFE-MARGIN zone — same rule: no type, no critical
    ornament. A leaf may overlap if it is part of a larger composition; a single
    detached leaf or a piece of text MUST sit further in.

  • Live area (where ALL text and the ornament focal point belong) is the inner
    rectangle from x:150 to x:874, y:150 to y:1386. Treat that as the canvas.

For text specifically: no glyph (including descenders) may extend past the inner
rectangle on any side. Author lockup at top, title block centered, subtitle below
title — all entirely inside the inner rectangle. No URL footers, no taglines, no
publisher marks within the outer 150 px.
```

The 1024×1536 panel ratios map cleanly to other trims:
- 6×9 trim: same 9% / 6% rule
- 5×8 trim: keep the same px values (the relative inset is similar enough)

If the model still puts the URL footer 30 px from the bottom edge, screenshot the
violation, point at it explicitly in a follow-up edit, and re-render only that
region (see `compose_wrap.py --clear-barcode` for the back's lower-right region).

## Shared prompt structure

Every cover prompt has five sections in this order:

0. **Safe-zone preamble** (above) — locked, non-negotiable
1. **Paper + background** — specify hex, grain, explicit "NO border, NO trompe-l'oeil paper"
2. **Composition** — where the ornament sits, how many leaves, how they move
3. **Typography** — numbered list of every text element, exact strings, font class (Didone/Didot/Georgia/etc.)
4. **Exclusions** — explicit list of what NOT to render ("no author credential line", "no publisher mark", etc.) — model defaults to adding garbled extra text
5. **Aesthetic reference** — editorial touchstones (Penguin Classics Deluxe, botanical monograph, sumi-e)

## Winning front cover (v5 — golden hour)

```
Book cover, portrait 2:3. An aesthetic 'aha' moment. Golden-hour light caught in paper form.

BACKGROUND: Warm cream watercolor paper (#F3E8CC) with a VERY soft, barely-visible radial wash of pale gold-orange behind the title — as if afternoon light filtered through leaves and landed on the page. The wash is so subtle it reads as atmosphere, not a graphic element. Paper grain throughout. No border, no edges, no shadow.

IMAGE: A sumi-e ink-wash branch enters from the upper-LEFT, curves gently downward, reaches just past center, then tapers. The branch carries 10-12 watercolor leaves in a RICHER palette than typical — honey gold, burnt ochre, amber, persimmon orange, rose madder, touches of oxblood at tip — painted wet-on-wet so pigments bloom and blend. A half-dozen leaves have detached and drift in a gentle swirl down the right side and across the lower-right corner — not a straight fall, but a caught-in-the-breeze spiral. Paper texture visible through every leaf. Visible pigment granulation and drying rings — this must feel hand-painted.

TYPOGRAPHY (only these three things, nothing else):
• Top margin, thin letter-spaced all-caps serif: DR. RICHARD LOUIS MILLER
• Centered lower half, three stacked lines in a refined high-contrast Didone, deep charcoal-black, tight leading: MASTER / YOUR / MIND
• Below title, small warm-brown old-style serif, three centered lines: Practical Tools to Calm Anxiety, / Silence Your Inner Critic, / and Stop Overthinking

No author credential line, no byline, no publisher, no URL, no tagline. Empty cream paper below subtitle.

AESTHETIC: The feeling of catching the last light of autumn. Warm, intimate, quietly magical. Hand-painted watercolor, analog, zero digital gradient artifacts.
```

**What tripped up earlier iterations:**
- v1-v4 kept placing leaves only on the left side; "down the RIGHT side and across the lower-right corner" fixed this
- Without "ONLY these three things", model added garbled author credentials like "Author credential of wit: Dr. Richard L. K. L'O MILLER, Ph.D, Mod menhandiaych"
- Without "no digital gradient artifacts", golden wash rendered as a flat tinted plane instead of atmospheric light
- Without "MASTER / YOUR / MIND", model stacked "MASTER YOUR MIND" as one line and blew the layout

## Winning back cover (v1)

> **2026-04-24 update:** original v1 placed the URL footer ~25 px from the bottom edge,
> which violated KDP's 0.25" safe inset. The text below adds the safe-zone preamble
> and tightens "industry-standard margins" into actual pixel coordinates the model
> can honor. If you regenerate, use this version, not the un-updated original.

```
[PASTE SAFE-ZONE PREAMBLE BLOCK HERE FIRST]

Book BACK COVER, portrait 2:3, to pair with a golden-hour watercolor leaf FRONT cover. Same paper, same palette, same illustration sensibility — but the role of the back cover is QUIET and TEXT-FORWARD.

CRITICAL TEXT PLACEMENT: ALL live text — every paragraph, header, bullet, footer,
URL — MUST sit entirely between x:150 and x:874, y:150 and y:1386 on a 1024 x 1536
canvas. The URL footer in particular goes at y≈1330, NOT at y≈1500. The section
header at the top goes at y≈190, NOT at y≈40.

BACKGROUND: Same warm cream watercolor paper (#F3E8CC) edge-to-edge, faint paper grain. A VERY soft golden wash hovers behind the upper third — barely perceptible, just enough to echo the front cover's golden-hour glow. NO border, NO edges, NO drop shadow, NO trompe-l'oeil paper.

ORNAMENT (restrained — back cover is for reading, not for shouting):
A single small sumi-e ink-wash twig with 3-4 honey-gold and amber watercolor leaves arcs gently across the upper-left corner only, occupying maybe 15% of the cover. ONE solitary leaf has detached and drifts down the right margin, paused mid-fall around the vertical center. That is all.

LAYOUT (top to bottom, all centered horizontally within the safe area unless noted):

1. SECTION HEADER (top, just below the small twig, left-aligned within safe margin):
Old-style serif small caps, dark charcoal, letter-spaced, single line:
YOUR MIND IS A TOOL, NOT THE BOSS

2. OPENING PARAGRAPH (warm dark-brown serif body, left-aligned, comfortable leading):
[paragraph 1]

3. SECOND PARAGRAPH (same body style):
[paragraph 2]

4. SUBHEAD (small caps, charcoal, letter-spaced, left-aligned):
WHAT YOU'LL MASTER:

5. FIVE BULLETS (small custom bullet glyph in honey gold, body text in warm dark brown, left-aligned, tight leading):
• [bullet 1]
• [bullet 2]
...

6. CLOSING PARAGRAPH:
[closing]

7. BIO PARAGRAPH (slightly smaller than body, warm dark brown):
[bio]

8. PULL-LINE (centered, italic display serif in warm dark brown, slightly larger):
[tagline]

9. FOOTER (very bottom, all caps, thin letter-spaced, charcoal):
[URL]

NO ISBN block. NO barcode. NO publisher logo. NO category line. The bottom-right barcode area is left as clean cream paper for the print barcode to be added later.

TYPOGRAPHY HIERARCHY: Section header > pull-line > body paragraphs ≈ bullets > bio. All sizes restrained and editorial — this is a back cover meant to be READ at arm's length, not seen from across a room.

STYLE: Penguin Classics deluxe back cover energy. Quiet, confident, hand-set feel.
```

**Why this worked:**
- Numbered sections with per-section typography directive = model got 9/9 elements right
- Explicit "NO barcode" leaves the lower-right clean for post-process barcode drop
- Closing "the book's intelligence comes through in the typography, not visual fireworks" reins in ornament drift

## Pitfalls seen across iterations

| Pitfall | Symptom | Fix |
|---|---|---|
| Type too big | "MASTER YOUR MIND" crowds the page, subtitle rivals title | Specify "title fills ~55% of cover width", subtitle "~2.5x smaller" |
| Type too small | Looks undercooked next to bestsellers | Explicitly say "reads from 10 feet" + fill-width instruction |
| Garbled author credentials line | Faux "Author of PSYCHEDELIC MEDICINE, X, Y" appears | "No author credential line" in exclusions |
| Ornament overwhelms type | Leaves sprawl, title crushed | "Branch tightened to upper third" + "ornament floats quiet above title" |
| Wrong cream hex | Drifts to beige or yellow | Always name hex `#F3E8CC` or `#F1E5C8` explicitly |
| Paper-within-paper | Model renders a paper rectangle floating on another paper | Explicit: "NO trompe-l'oeil paper" |
| Em dashes in text | Shows up as literal — characters | Rewrite copy to use parens or commas before passing to model |
