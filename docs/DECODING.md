# How the Khalaf ʿan Ḥamzah PDF is decoded

Result: `out/khalaf_an_hamzah.tsv`, one verse per row (`sura`, `aya`, `pdf_page`, `text`), 6,236 verses in 114 surahs.

**Status: machine-decoded and cross-checked against Hafs as an alignment aid only. It has not been
collated against an authoritative Khalaf ʿan Ḥamzah edition, so do not treat it as a verified muṣḥaf text.**

## Why the original fonts were not needed

The earlier report assumed the original HQPB fonts were required. They are not:

- Every base glyph in HQPB1/2/3 is one letter in one positional shape, and the fonts are laid out in
  alphabetical order (alif shapes, then bāʾ shapes, ...). The letter is readable straight off the glyph atlas.
- Marks (HQPB4/5) are drawn at the same origin as the letter they belong to, so attachment is exact.
- Each word is drawn as one left-to-right run, so word breaks are recoverable although the PDF has no spaces.

## Pipeline

1. `src/extract_glyphs.py` dumps every drawn glyph (font, glyph name, position, size) with PyMuPDF.
2. `src/layout.py` groups glyphs into clusters (letter + its marks), words, lines and verses.
   Verses are split on the verse-number digits; surah title lines and the calligraphic basmala are dropped.
3. `src/labels.py` holds the tables: base glyph → letter(s), mark shape → sign.
   `data/mark_components.json` lists, for each mark glyph, its component shapes and where they sit.
4. `src/decode.py` turns each cluster into Unicode and writes the TSV.
5. `src/compare.py` lists differences from the KFGQPC Hafs text; `src/peek.py` renders a verse from the PDF
   next to its glyphs for checking by eye.

## How marks are read

A mark glyph is split into components (one fatḥa stroke, one shadda, ...). Each component is classified by
shape, then by position:

- stroke above the letter = fatḥa, below = kasra; two strokes = tanwīn (stacked ً ٍ or offset ٗ ٖ)
- one ḍamma, two ḍammas (ٞ), ḍamma with hook (ٌ)
- with a small mīm = iqlāb forms (َۢ ُۢ ِۭ)
- on ligatures (lām-alif, لله) the component's x position decides which letter it belongs to

## Encoding choices

The text follows KFGQPC Uthmanic conventions (sukūn = U+06E1, open tanwīn = U+0657/U+065E/U+0656, etc.) so it
renders with KFGQPC fonts. Signs that Hafs does not have:

| Sign in the PDF | Meaning | Unicode used |
|---|---|---|
| filled dot under a letter | imāla | U+065C |
| small ring under a letter | taqlīl | U+06EA |
| diamond (12:11) | ishmām | U+06EC |
| small لا | no-stop sign | U+06D9 |

Other choices:

- The hamza standing before the alif of a lām-alif (as in ٱلۡأٓخِرَةِ) is written أٓ as KFGQPC does; the page
  shows a hamza with a fatḥa.
- Final dotless yāʾ is the same glyph for ى and ي. It is written ى when it carries a small alif, or has no
  vowel of its own and follows a fatḥa/imāla; otherwise ي.
- The basmala between surahs is a decoration in the PDF and is not part of any verse row (1:1 is real text).
- Colours in the PDF (which highlight Khalaf-specific spots) are not exported.

## Checks done

- Verse numbers printed on the pages match the Kufan numbering for all 6,236 verses.
- Against KFGQPC Hafs (skeleton = letters only): 6,000 verses have an identical skeleton. The other 236 show
  the kind of differences expected between readings (ن/ي, ت/ي, إِن/أَن, هُزُؤًا, ...).
- Letter by letter on those 6,000 verses: 305,160 letters line up, 6,271 differ in their marks. About 5,300 of
  these fall into well-known Khalaf patterns: shadda on و/ي after tanwīn or nūn (assimilation without
  ghunna), the imāla dot, عَلَيۡهُمۡ / إِلَيۡهُمۡ, no sukūn on قَد / إِذ before assimilated letters.
  The rest were reviewed by frequency and look like individual reading differences, but were **not** checked
  one by one.
- All 199 ḥizb marks and all 15 sajda marks fall on the same verses as in Hafs.
- Spot checks by eye against rendered pages (e.g. 2:4, 19:1-4, 6:124, 53:23, 4:8).

## Misprints in the PDF, reproduced as printed

- 4:8 has ٱلۡيَتَٰمَىٰ without the وَ before it.
- Surah 53: the marker for verse 23 is printed after أَمۡ, so أَمۡ ends verse 23 instead of starting 24.
- A stray "alif with a dot" glyph (Hamd2 g3) appears in four places (PDF pages 107, 170, 239, 563; the first
  is inside أَكَلَ in 5:3). It is ignored.

## Hand corrections

One, in `labels.WORD_FIXES`: in 12:39 and 12:41 the typesetter used the "yāʾ + small alif" glyph as a plain
connector, which decoded as يَٰصَىٰحِبَيِ; it is corrected to يَٰصَٰحِبَيِ.

## Known limits

- Not collated against a printed or scholarly Khalaf edition.
- Where the typesetter reused a Hafs glyph that only approximates the Khalaf form, the output follows the glyph.
- Pause signs are placed by position; a few may sit one word away from where the page shows them.
- The sajda overline that KFGQPC encodes as U+06E4 is not in the PDF.
- Hafs is used only to find decoder errors. No letter or mark in the output is taken from the Hafs text.
