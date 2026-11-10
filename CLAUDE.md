# Khalaf Mushaf — how to run

- Python 3.13 (`python`). Packages: PyMuPDF, fontTools, Pillow, CairoSVG.
- Investigation scripts are in `khalaf_recovery_package/`:
  - `build_inventory.py` — font subsets + code/glyph inventory from the PDF.
  - `make_glyph_atlas.py` — renders glyph atlas PNGs from the `.cff` files.
  - Both have a hardcoded `PDF` path from the original machine; point it at the local PDF before running.
- `pdffonts`/`pdfinfo`/Tesseract are not installed on this machine.
- `python src/extract_glyphs.py <pdf> tmp/glyphs.tsv` dumps every glyph with position.
- Scratch output goes in `tmp/` (git-ignored).
- The text is sacred: never treat OCR or a Ḥafṣ text as ground truth for Khalaf.
