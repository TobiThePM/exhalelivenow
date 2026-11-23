# QA Patterns

Known issues the QA loop should catch. These are confirmed patterns from testing on a 245-page Anthropic system card.

## Header Issues

**Missing header prefixes** — Some bookmark headers lose their `##`/`###` prefix and get merged with the following paragraph as plain text. The pipeline matches bookmark titles against body text to insert the right markdown prefix, but edge cases slip through — especially section titles with footnote markers or unusual formatting.

What to look for: a line that reads like a section title (e.g., "2.1 RSP risk assessment process") but lacks a `#` prefix. Compare against the bookmark tree from preflight.

**Header-body merge** — A section header and its first paragraph end up on the same line. Split them: header on its own line, blank line, then body.

## Link Issues

**Nested/broken links** — `[our [alignment risk update](url)](url)` double-wrapping. Fix by collapsing to a single `[text](url)`.

**Partial-word links** — The pipeline protects against these (e.g., `[A](url)ttempts`), but if one slips through, remove the link annotation or expand the link text to the full word.

## Text Flow Issues

**Cross-page sentence splits** — The last paragraph on a page ends mid-sentence, and the continuation on the next page starts as a new paragraph. The pipeline handles most of these by checking for sentence-ending punctuation, but ambiguous cases (e.g., ending with a closing parenthesis or quote) can slip through.

**Dialogue/conversation formatting** — Transcript excerpts with `User:`/`Assistant:` labels may need formatting cleanup. Consider using blockquotes or code blocks for conversation transcripts.

## Tables

**Complex nested tables** — PyMuPDF's table extraction handles simple tables well but can garble complex nested structures. For these, use `scripts/check_page.sh` to get Gemini's rendering of that specific page, then replace the garbled table in the output.

## Footnotes

**Footnote definitions spanning multiple blocks** — When a footnote definition is split across two PDF blocks, the second part can merge oddly with surrounding text. Check that each `[^N]:` definition reads as a complete sentence.

## Do No Harm Rule

When fixing QA issues, never strip existing hyperlinks. The programmatic extraction preserves links from PDF annotations — these are the ground truth. If you're rewriting a paragraph to fix a header merge or broken sentence, make sure every `[text](url)` link from the original is present in your fix.

Common mistake: replacing a paragraph that has `our [Responsible Scaling Policy](url)` with a "cleaned" version that drops the link to just `our Responsible Scaling Policy`.

## PDFs Without Bookmarks

When a PDF has no bookmark tree, the pipeline falls back to font-size heuristics: the most common font size = body, anything larger = headers ranked by size. This works well for simple documents but can misclassify pull-quotes or large captions as headers. Spot-check the header hierarchy against what the document actually shows.
