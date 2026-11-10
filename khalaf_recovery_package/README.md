# Khalaf an Hamzah PDF encoding investigation

This is an extraction inventory and glyph-reference package, not a completed Unicode transcription.

## Findings
- The supplied PDF has 604 pages and is vector/text based rather than image-only.
- The custom Arabic text layer extracts to low-byte/control characters because the embedded Type 1C/CFF fonts do not provide usable ToUnicode mappings.
- The content uses multiple font subsets. The PDF Encoding Differences arrays map byte codes to CFF glyph names (for example `g197`), but that mapping only identifies the glyph, not the Unicode character represented.
- The visible writing is layered: HQPB1/HQPB2/HQPB3 contain many base letter shapes; HQPB4/HQPB5 contain many small overlay/mark glyphs. Therefore there is not one universal byte-to-letter substitution.
- `font_code_inventory.csv` lists each observed font/code pair, CFF glyph name, frequency, and number of pages on which it occurs.
- `font_summary.json` summarizes embedded font subsets. The glyph atlases are visual references generated from the embedded CFF charstrings.

## What remains to complete a decoder
1. Establish the mapping from each relevant glyph (and overlay) to Arabic Unicode or a Unicode sequence.
2. Reconstruct text order and combining-mark attachment from glyph positions / text-show operations.
3. Validate against an authoritative Khalaf an Hamzah text, not just a Hafs Quran corpus.
4. Rebuild the PDF text layer or produce an extracted UTF-8 transcript, then audit verse-by-verse.

## OCR test
A 600-DPI render of page 3 was tested with Tesseract Arabic OCR. It recovers much of the base wording but not all diacritics or special Qur'anic/recitation annotations. Treat OCR as a draft/validation signal, not an authoritative transcript.
