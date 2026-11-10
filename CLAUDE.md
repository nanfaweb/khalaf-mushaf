# Khalaf Mushaf — how to run

- Python 3.13 (`python`). Packages: PyMuPDF, fontTools, Pillow, CairoSVG.
- Investigation scripts are in `khalaf_recovery_package/`:
  - `build_inventory.py` — font subsets + code/glyph inventory from the PDF.
  - `make_glyph_atlas.py` — renders glyph atlas PNGs from the `.cff` files.
  - Both have a hardcoded `PDF` path from the original machine; point it at the local PDF before running.
- `pdffonts`/`pdfinfo`/Tesseract are not installed on this machine.
- `python src/extract_glyphs.py <pdf> tmp/glyphs.tsv` dumps every glyph with position.
- `python -X utf8 src/decode.py tmp/glyphs.tsv out/khalaf_an_hamzah.tsv` decodes to Unicode (one verse per row).
- `python -X utf8 src/compare.py tmp/glyphs.tsv tmp/ref/hafsData_v18.json tmp/report.txt` lists differences from
  KFGQPC Hafs (download `hafs/data/hafsData_v18.json` from github.com/ibnhazm/KFGQPC into `tmp/ref/`).
- `python -X utf8 src/peek.py <pdf> tmp/glyphs.tsv tmp/x.png 2:4 [word]` shows a verse's glyphs and renders it.
- Scratch output goes in `tmp/` (git-ignored).
- The text is sacred: never treat OCR or a Ḥafṣ text as ground truth for Khalaf.
