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

- 2026-11-10: **decoder works.** `src/decode.py` writes `out/khalaf_an_hamzah.tsv`: 6,236 verses in 114 surahs
  (verse numbers read from the page match the Kufan count everywhere). Labels came from the glyph atlases
  (fonts are in alphabetical order, one glyph per letter shape) plus mark shapes named by eye; no original fonts needed.
  Check against KFGQPC Hafs (`src/compare.py`, alignment aid only): 5,998 verses have the same letter skeleton,
  ~305k letters line up and ~6.3k differ, of which ~5.2k are known Khalaf patterns (idgham shadda on و/ي,
  imala dot, عليهُم, no sukun on قد/إذ). Not yet checked against a real Khalaf edition.
- Encoding choices: KFGQPC Uthmanic conventions; imala dot = U+065C, taqlil ring = U+06EA, ishmam = U+06EC;
  hamza before the alif of lam-alif is written أٓ (the page shows hamza + fatha).
- Misprints in the PDF itself, reproduced as printed: 4:8 lacks وَ before ٱلۡيَتَٰمَىٰ; the verse-23 marker in
  surah 53 comes after أَمۡ; a stray alif-with-dot glyph (Hamd2 g3, 4 places, e.g. 5:3) is ignored.
- 2026-11-10 (later): loose ends fixed (6:124, 12:39/41, loose imala dots and small alifs, squeezed 12pt words,
  line-end hizb marks). 0 unresolved glyphs. Now 6,000 verses share the Hafs skeleton; 6,271 of 305,160
  aligned letters differ. Method, encoding choices, PDF misprints and limits are in `docs/DECODING.md`.

- 2026-11-10 (ground-truth pass): the user confirmed the PDF itself is the Khalaf ground truth. Added `src/audit.py`
  (every glyph accounted for; nothing dropped but titles, ornaments, page furniture, decorative basmala).
  Checked every letter and mark glyph by eye on labelled contact sheets; fixed three mislabels (HQPB3 g66 is a
  final yāʾ, HQPB2 g121/g123 and g87 carry a hamza below). Line-start pause signs now go to the previous line's
  last word. The sajda small madda (U+06E4) is simply not printed in the PDF. 6,044 verses share the Hafs skeleton.

## Next

1. Optional: make a copy-pasteable PDF by adding an invisible Unicode text layer from `out/khalaf_an_hamzah.tsv`.
2. Optional: a human proofread of the TSV against the pages (the decoder checks are glyph-level, not word-level).

## Ideas (not scheduled)

- Export the colour coding; rebuild the PDF with a proper ToUnicode text layer.
