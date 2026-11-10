# Khalaf Mushaf — plan

## Goal

Recover the Qur'an text (Khalaf ʿan Ḥamzah transmission) from the Islamweb 2009 PDF as accurate Unicode Arabic,
by decoding its embedded HQPB fonts rather than relying on OCR.

## Where it stands

- `khalaf_recovery_package/` holds the earlier investigation: extracted font subsets (`font_*.cff`),
  the code/glyph inventory, glyph atlases, sample page renders and OCR tests. See its `TECHNICAL_REPORT.md`.
- **The source PDF is not in this folder yet.** Decoding the text needs it (the page content streams).
- Finding (2026-11-10): glyph names in the subsets are `gNNN` with NNN ≤ 224 in every HQPB font, and the PDF
  byte codes are handed out in order of first use (0x02, 0x03, ...), so they carry no meaning themselves.
  This fits PScript5/Distiller converting TrueType fonts, where `gNNN` is the glyph's index in the
  original font. If confirmed, the original font's cmap gives each glyph's character code directly.

## Next

1. Get the PDF into this folder.
2. Get the original HQPB1–5, HQPB7 font files (listed at https://www.duas.org/fonts/) and confirm `gNNN` = glyph index
   by comparing outlines between subset and original.
3. Build glyph → character-code → Unicode tables per font (legacy codes likely need a hand-made table).
4. Write the decoder: walk each page's text operators, switch fonts, order glyphs and attach marks.
5. Check output against an authoritative Khalaf ʿan Ḥamzah text, page by page.

## Ideas (not scheduled)

- Rebuild the PDF with a proper ToUnicode text layer once the decoder is trusted.
