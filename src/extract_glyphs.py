"""Dump every drawn glyph in the PDF as one TSV row: page, order, font, glyph name, position.

Glyph names come from each embedded CFF subset's charset (e.g. g197), which is the
stable identity of the glyph; PDF byte codes are arbitrary per document.

Usage: python src/extract_glyphs.py <pdf> <out.tsv>
"""
import io
import sys

import pymupdf
from fontTools.cffLib import CFFFontSet


def charsets(doc):
    """font base name -> list of glyph names indexed by subset GID."""
    out = {}
    for page in doc:
        for xref, ext, _typ, name, *_ in page.get_fonts():
            base = name.split("+")[-1]
            if base in out or ext != "cff":
                continue
            buf = doc.extract_font(xref)[3]
            cff = CFFFontSet()
            cff.decompile(io.BytesIO(buf), None)
            out[base] = list(cff[cff.fontNames[0]].charset)
    return out


def main(pdf, out_path):
    doc = pymupdf.open(pdf)
    names = charsets(doc)
    rows = 0
    with open(out_path, "w", encoding="utf-8", newline="\n") as out:
        out.write("page\tseq\tfont\tglyph\tx\ty\tsize\n")
        for pno, page in enumerate(doc, 1):
            seq = 0
            for span in page.get_texttrace():
                font = span["font"]
                table = names.get(font)
                for _uni, gid, origin, _bbox in span["chars"]:
                    glyph = table[gid] if table and 0 <= gid < len(table) else f"gid{gid}"
                    out.write(f"{pno}\t{seq}\t{font}\t{glyph}\t{origin[0]:.2f}\t{origin[1]:.2f}\t{span['size']:.2f}\n")
                    seq += 1
                    rows += 1
    print(f"{rows} glyphs from {len(doc)} pages -> {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
