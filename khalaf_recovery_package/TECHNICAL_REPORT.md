# Technical report: Khalaf ʿan Ḥamzah PDF text recovery

## Executive result

The PDF's visual text is recoverable as vector font outlines, but its embedded text is **not directly extractable as Unicode Arabic**. The PDF has no usable Unicode mapping for its embedded fonts (`pdffonts` reports `uni=no` for every listed font). Its custom font encodings map byte codes to glyph names, not to Unicode characters. Generic Arabic OCR recovers fragments but is not accurate enough to be treated as a Qur'an transcript.

**Status: investigation completed; full Unicode decoder not yet completed.** This package contains the extracted font subsets, the code/glyph inventory, glyph atlases, page renders, and raw OCR tests. It does not contain a decoded Qur'an.

## PDF facts observed locally

- 604 pages; PDF 1.4; unencrypted; 2,723,425 bytes.
- Creation date in metadata: 18 September 2009.
- Creator: `PScript5.dll Version 5.2`.
- Producer: `Acrobat Distiller 8.0.0 (Windows)`.
- PDF metadata keywords identify Islamweb (`www.islamweb.net`).
- The file is not image-only: pages contain vector/text drawing operations and embedded font subsets.
- `pdffonts` lists 11 embedded subset fonts. Every row reports `uni=no`; the main Arabic fonts use `Custom` encodings.
- The custom PDF encodings contain `/Differences` arrays, mapping PDF character codes to glyph names such as `g197`.
- The embedded fonts are Type 1C (CFF) subsets with vector outlines.

## Observed glyph inventory

The extraction pass found **754 distinct (font, PDF-byte-code) pairs** and **627,706 text-character occurrences** across the document.

| font                     |   font_code_pairs |   observed_occurrences |   max_pages_for_a_code |
|:-------------------------|------------------:|-----------------------:|-----------------------:|
| HQPB2                    |               173 |                 205238 |                    604 |
| HQPB4                    |               183 |                 148830 |                    604 |
| HQPB1                    |               174 |                 140554 |                    604 |
| HQPB5                    |                88 |                 124168 |                    604 |
| HQPB3                    |                39 |                   6650 |                    549 |
| MSH-Quraan1              |                31 |                    895 |                    310 |
| Hamd2                    |                20 |                    761 |                    141 |
| TimesNewRomanPSMT        |                14 |                    495 |                     97 |
| DecoType-ProfessionalNas |                29 |                    103 |                      7 |
| HQPB7                    |                 3 |                     12 |                      9 |

The most-used families are HQPB2, HQPB4, HQPB1 and HQPB5. In this PDF the HQPB fonts do not all play the same role: some frequently contribute base letter forms, while other fonts contribute many small marks/overlays. A code must therefore be interpreted in the context of its font; a global byte-to-Arabic substitution is invalid.

`font_code_inventory.csv` is the detailed per-code inventory. `font_summary.json` records font-subset metadata. The `font_*.cff` files are extracted embedded subsets. `glyph_atlas_*.png` sheets render their glyph outlines with PDF code and CFF glyph name labels.

## Why the text extraction is garbled

A PDF text-show operation stores character codes. A font encoding maps those codes to glyphs. To turn a selected glyph back into copyable text, an extractor normally needs a usable `ToUnicode` CMap (or another reliable character mapping). Here the embedded fonts are subset custom-encoded fonts and the PDF has no usable Unicode mapping. The visible glyph can still render correctly while copy/paste produces control characters or unrelated low-byte characters.

The relevant chain in this file is:

`PDF byte code → font-specific /Differences entry → CFF glyph name/outline`

The missing link is:

`CFF glyph → intended Unicode character or Unicode sequence`

Some visible writing is composed from separate glyphs and overlays, so the reconstruction also needs to preserve drawing order, positioning, and mark attachment. Some glyphs may encode ligatures or contextual forms rather than one Unicode letter.

## OCR experiment

Tesseract 5 Arabic (`ara`) was tested using `--psm 4` on 360-DPI page renders for pages 1, 2, 3 and 604. It did recover some recognizable base wording, especially on page 3, but also confused or omitted letters, diacritics, Qur'anic signs, headings and special recitation annotations. `OCR_RESULTS.txt` preserves the raw outputs. `ocr_page*.png` are the rendered input images.

A 600-DPI crop of the first text line on page 3 was also tested with line segmentation. It was more readable than the full-page OCR but still had substitutions and missing/split marks. Raising resolution does not solve the recognition/model problem by itself.

**OCR conclusion:** generic Tesseract is useful as a rough cross-check, but not safe for producing an exact sacred-text transcript without line-by-line verification. A Quran/Othmani-specialized OCR model may improve the draft, but still requires rigorous collation.

## Reverse-engineering path and current blocker

The strongest next experiment is to obtain the **original full HQPB1, HQPB2, HQPB3, HQPB4, HQPB5 and HQPB7 font files** and compare their glyph names/indices with the PDF's subsetted `g###` names. A public font directory listing exposes these filenames and sizes: <https://www.duas.org/fonts/> (HQPB1–5 and HQPB7 are listed together). A historical font archive also attributes this family to Amgad. The original font's character-to-glyph mapping may reveal which legacy code points map to each glyph, but this must be tested rather than assumed: the PDF uses subset CFF fonts, and glyph naming or ordering may have changed during subsetting/conversion.

Once the original fonts are available:

1. Inspect each font's `cmap`, `post` names and glyph order with FontTools/FontForge.
2. Match original glyph names/IDs against the PDF CFF subset glyph names.
3. For every matched glyph, recover the source character mapping. Check whether the source mapping is Unicode or a legacy 8-bit encoding.
4. Rebuild text from PDF text-show operators with font switching and glyph positions preserved; reconstruct attached marks and ligatures as Unicode sequences.
5. Validate whole pages against a scholarly/authoritative Khalaf ʿan Ḥamzah edition. Do not substitute a Hafs text as the ground truth.

The public Quran.ws text dataset is not a suitable full reference for this file: its documented seven editions omit both the Ḥamzah and al-Kisāʾī transmissions. It is useful as an example of a properly structured Unicode corpus, but it cannot validate Khalaf here.

## Reproducibility

- `build_inventory.py`: extracts embedded font subsets, reads PDF `/Differences` arrays, counts observed `(font, code)` pairs, and writes the CSV/JSON inventory.
- `make_glyph_atlas.py`: renders CFF charstrings into glyph atlas PNGs.
- `OCR_RESULTS.txt`: raw Tesseract outputs for the sample pages.

The scripts currently use the uploaded PDF's original absolute path (`/mnt/data/المصحف_برواية_خلف_عن_حمزة.pdf`). Update the `PDF` variable if running elsewhere. Required Python packages include PyMuPDF, FontTools, Pillow and CairoSVG; external binaries include `pdffonts`, `pdfinfo` and Tesseract with its Arabic language data.

## Bottom line

Reverse engineering remains the better route than generic OCR, because the PDF preserves the actual vector glyphs and font-specific code mappings. However, the original full HQPB fonts or another authoritative Khalaf text source are still needed to finish the character map and verify a complete transcript. This package is a reproducible investigation bundle, not a claim that the Quran text has been decoded.
