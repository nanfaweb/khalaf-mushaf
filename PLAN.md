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

- PDF is in the project root (git-ignored). `src/extract_glyphs.py` dumps all 646,365 drawn glyphs
  (page, order, font, glyph name, x, y, size) to a TSV in ~6 s. That's more than the old inventory
  (627,706) because the old `get_text('dict')` pass dropped glyphs stacked at the same position.
  Mark glyphs (HQPB4/5) are drawn at the same origin as their base glyph (HQPB1/2).
- Original fonts: duas.org/fonts/ is now 404 with no Wayback copy; islamicstudies.info blocks automated access.
  Not found elsewhere yet.
- No Unicode Khalaf text exists in the KFGQPC repos (ibnhazm/KFGQPC has hafs, warsh, qaloon, shouba, doori,
  soosi, bazzi, qumbul only).

## Next

1. Decide the labelling route (see below), then build the glyph → Unicode tables.
2. Write the decoder: order glyphs per line (right-to-left), attach marks to bases, emit Unicode.
3. Check output against an authoritative Khalaf ʿan Ḥamzah text, page by page.

Labelling routes:
- A. Original HQPB fonts (if the user can find them): cmap gives codes directly, then a legacy → Unicode table.
- B. Without them: align base glyphs (HQPB1/2/3) against the KFGQPC Hafs/Shuʿbah consonant skeleton,
  which Khalaf almost always shares, to label base letters automatically; label the ~270 mark glyphs
  (HQPB4/5) by hand from the atlases. Hafs is only an alignment scaffold here, never the answer.

## Ideas (not scheduled)

- Rebuild the PDF with a proper ToUnicode text layer once the decoder is trusted.
