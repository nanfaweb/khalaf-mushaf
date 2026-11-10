# Khalaf Mushaf

Recovering the Qur'an text of an Arabic PDF mushaf (*Khalaf ʿan Ḥamzah* recitation, 604 pages) as real Unicode text.

The PDF looks right on screen but cannot be copied: its custom fonts have no Unicode mapping, so copy-paste gives
garbage and OCR is not accurate enough for a sacred text. This project reads the glyphs the PDF actually draws and
turns each one back into the letter or sign it shows.

## Result

[`out/khalaf_an_hamzah.tsv`](out/khalaf_an_hamzah.tsv): 6,236 verses in 114 surahs, one per row
(`sura`, `aya`, `pdf_page`, `text`), using King Fahd Complex (KFGQPC) Unicode conventions.

**Status:** machine-decoded and cross-checked against the Hafs text only to find decoder mistakes. It has **not**
been collated against an authoritative Khalaf ʿan Ḥamzah edition, so it is not a verified muṣḥaf text.

## How it works

1. `src/extract_glyphs.py` lists every glyph drawn on every page (font, glyph, position).
2. `src/layout.py` groups glyphs into letters with their marks, words, lines and verses.
3. `src/labels.py` and `data/mark_components.json` map glyphs to letters and mark shapes to signs.
4. `src/decode.py` writes the Unicode text. `src/compare.py` and `src/peek.py` help check it.

Details, encoding choices, checks done, misprints in the source PDF and known limits are in
[`docs/DECODING.md`](docs/DECODING.md). Where the work stands and what is next is in [`PLAN.md`](PLAN.md).

## Running it

The source PDF is not included (it is not ours to redistribute). Put it in the project folder, then:

```bash
pip install pymupdf fonttools
python -X utf8 src/extract_glyphs.py <pdf> tmp/glyphs.tsv
python -X utf8 src/decode.py tmp/glyphs.tsv out/khalaf_an_hamzah.tsv
```

`khalaf_recovery_package/` holds the earlier investigation (font subsets, glyph atlases, OCR tests).
