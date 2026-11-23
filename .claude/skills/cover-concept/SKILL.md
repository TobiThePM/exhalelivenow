---
name: cover-concept
description: Generate book cover concepts by analyzing bestselling covers in the target category, extracting design patterns, and producing detailed cover briefs and AI image prompts. Use when designing or brainstorming a book cover before producing final art.
---

# Cover Concept Generator

Generate book cover concepts by analyzing bestselling covers in the target category, extracting design patterns, and producing detailed cover briefs + AI image prompts.

## When to Use

When designing a book cover for any project. Works for Amazon KDP, print, or digital distribution.

## Workflow

### Phase 1: Research (Competitive Scan)

1. User provides: book title, subtitle, author name, genre/category, target audience
2. Search Amazon bestsellers and new releases in the target category
3. Screenshot or fetch 8-10 top-performing covers using browse/gstack tools
4. Analyze each cover for:
   - **Typography:** Font style, weight, size ratio (title vs subtitle vs author), case, color
   - **Color palette:** Background, text, accent colors. Note contrast at thumbnail size.
   - **Imagery:** Photo, illustration, abstract, geometric, none (text-only)
   - **Layout:** Center-weighted, asymmetric, full-bleed, bordered
   - **Genre signals:** What makes this look like it belongs in its category?
   - **Thumbnail test:** Is it readable at 100px wide? What stands out?

### Phase 2: Pattern Extraction

Synthesize the scan into a design brief:

```markdown
## Cover Design Brief

**Category conventions:** [what the top sellers share]
**Differentiation opportunities:** [what's overused vs. underused]
**Thumbnail-first principles:** [what works at small size]
**Color strategy:** [based on what competitors use and what would stand out]
**Typography direction:** [serif vs sans, weight, case]
**Imagery direction:** [photo, illustration, abstract, or text-only]
```

### Phase 3: Concept Generation

Generate 3-5 distinct cover concepts. For each:

```markdown
### Concept N: [Name]

**Visual description:** [detailed enough for a designer or AI to execute]
**Typography:** [specific font direction, size hierarchy, color]
**Color palette:** [hex codes if possible, or descriptive]
**Imagery:** [what appears on the cover, where, how]
**Why it works:** [what genre signals it hits, how it differentiates]
**Reference covers:** [which bestsellers inspired this direction]
```

### Phase 4: AI Image Generation

For each concept, generate a cover mockup using the nano-banana-image-generator skill or similar:

**Prompt template:**
```
Book cover design, [dimensions], [style description]. 
Title: "[TITLE]" in [font description]. 
Subtitle: "[SUBTITLE]" in [font description]. 
Author: "[AUTHOR]" in [font description].
Background: [description]. 
[Additional imagery description].
Professional publishing quality, high contrast, readable at thumbnail size.
```

**Important constraints:**
- AI image generators struggle with text. Generate the visual/background separately, then note the text placement for manual overlay.
- Always specify "book cover" and dimensions (6x9 for print, 1600x2560 for Kindle)
- Request multiple variations of the best concept

### Phase 5: Refinement

Present concepts to user. Iterate based on feedback:
- Adjust typography weight, color, positioning
- Try color inversions (dark bg → light bg)
- Swap imagery while keeping the same layout
- A/B test: which one is more readable at thumbnail?

## 2026 Cover Design Principles (Nonfiction/Self-Help)

From competitive analysis of Amazon bestsellers:

1. **Bold typography dominates.** Large, confident lettering IS the design. Imagery is secondary or absent.
2. **High contrast at thumbnail size.** The cover must be readable at 100px wide. If you squint and can't read the title, it fails.
3. **Minimal palette.** 2-3 colors max. One background, one text, one accent.
4. **Genre signaling matters more than originality.** A psychology book should look like a psychology book. Don't confuse the browser.
5. **Trending colors (2026):** Orange revival. Blues (aqua, teal, cobalt). White/cream backgrounds for authority. Avoid: generic gradients, stock photo vibes.
6. **Humanistic touches:** Subtle texture, grain, or imperfect lettering signals authenticity in a sea of AI-generated covers.
7. **Author credential placement:** For credentialed authors (PhD, MD), the credential goes right under the name. It's a trust signal.
8. **Subtitle sells the benefit.** Title = curiosity. Subtitle = "here's what you get." Both must be readable at thumbnail.

## Test Cases

- Master Your Mind (Dr. Richard Louis Miller) — current: glowing orb on blue. Direction: bold text-forward, minimal imagery.
- Aging Well / [new title TBD] — category: aging/psychology. Direction: authority + warmth.

## Dependencies

- Web search for Amazon category browsing
- Screenshot/browse tools for cover analysis
- nano-banana-image-generator or gemini-imagegen for mockup generation
- Image editing for text overlay (manual step)
