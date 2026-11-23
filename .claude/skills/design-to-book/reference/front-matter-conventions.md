# Front & Back Matter Conventions (CLM imprint)

*House patterns for the pages before and after the text, drawn from the shipped editions (Rerum Novarum 2025, Quadragesimo Anno print, Catholic Land Movement pamphlet). Every element below is a rethread-emitted section — bare pages, no running heads, no folios until the text proper begins.*

## Page order (recto/verso discipline)

| Page | Side | Content |
|------|------|---------|
| Half title | recto | Title only, small caps or display face, upper third |
| (blank or frontispiece) | verso | Frontispiece art gets `break-before:left` facing the title |
| Title page | recto | Title, subtitle/author line, imprint mark at foot |
| Copyright page | verso | Always the title page's verso — see block below |
| Publisher's note / dedication | recto | Optional; CLM editions carry a publisher's note |
| Contents | recto | Only if the book has chapters/sections worth navigating |
| Text | recto | Arabic folios and running heads start here |

Back matter: colophon last (the pamphlet scaffold has one — type, paper, imprint line). About-the-imprint page optional before it.

## Copyright page — public-domain edition template

The shipped Rerum Novarum language, reusable verbatim for any PD reprint:

```
<Title>
<Author/origin line, e.g. "Encyclical of Pope Leo XIII">
Originally issued <date>
Public Domain

This edition © <year>

This edition includes modernized formatting and typesetting.
The text of <Title> is in the public domain. No copyright is
claimed on the original work. Rights are reserved only for this
edition's layout, design, and any added material.

ISBN: <once assigned by KDP>
First Edition: <Month Year>
Printed in the United States of America
```

Set small (8.5–9 pt), centered or flush-left block, bottom-anchored or vertically centered. For an original work, replace the PD block with a standard `© <year> <author>. All rights reserved.` line.

## Publisher's note pattern

The QA print edition opens with a short CLM publisher's note: 2–3 sentences of why-this-reprint, one pull quote from the text itself, then `Learn more at CatholicLandMovement.info.` Keep it under a page; it earns its place by framing, not summarizing.

## Encyclical-specific conventions

- **Numbered paragraphs are canonical.** §-numbers (1., 2., …) are how encyclicals are cited — preserve them in the markdown master and typeset them (run-in bold or hanging) rather than stripping.
- **Footnotes**: the Vatican apparatus (citations to prior encyclicals, scripture) becomes markdown `[^n]`; typeset as endnotes for pocket trims (footnotes on a 4.25×6.87 page eat too much column) unless the count is trivial.
- **Formal address opening** ("Venerable Brethren…") is part of the text, not front matter — it takes the drop cap.

## Display-block rules (learned on the encyclical builds, 2026-07-02)

- **Title page author/origin line** ("Encyclical of Pope …") is serif letterspaced small-caps — never the sans; sans appears only in the imprint wordmark at the foot.
- **Narrow-measure display blocks** (pull quotes, address/superscription blocks, epigraphs): never justified — center or left-rag them, and never let a line begin with an em dash.
- **Centered display blocks get `hyphens:none`** — Chrome happily hyphenates centered text ("ordinar-ies" on an opener page).
- **Encyclical address + salutation**: the ALL-CAPS formal superscription sets well as a small tracked sans block; the "Venerable Brethren…" salutation as centered italic; neither is a numbered body paragraph. The unnumbered opening paragraph takes the drop cap and shows no ¶ number.

## Checks that live here

- Copyright page must NOT carry a folio or running head.
- Front matter paginates independently of the interior (roman vs arabic) — see hard-won-rules.md.
- Total page count even and ≥ 24 after front/back matter are in.
