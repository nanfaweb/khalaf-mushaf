"""Render glyphs at their true position (baseline + origin shown) into a labelled PNG grid."""
import pymupdf
from fontTools.pens.svgPathPen import SVGPathPen


def path(top, glyph):
    pen = SVGPathPen(None)
    top.CharStrings[glyph].draw(pen)
    return pen.getCommands()


def grid(items, out_png, cols=10, cell=150, ymin=-700, ymax=1500, xmin=-400, xmax=1100, under=None):
    """items: [(label, [(top, glyph, colour)])]. Glyph space box (xmin..xmax, ymin..ymax) fills a cell."""
    rows = (len(items) + cols - 1) // cols
    ch = cell + 16
    s = cell / max(xmax - xmin, ymax - ymin)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols*cell}" height="{rows*ch}">',
             f'<rect width="{cols*cell}" height="{rows*ch}" fill="white"/>']
    for i, (label, layers) in enumerate(items):
        cx, cy = (i % cols) * cell, (i // cols) * ch
        ox, oy = cx - xmin * s, cy + 16 + ymax * s
        parts.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{ch}" fill="none" stroke="#bbb"/>')
        parts.append(f'<line x1="{cx}" x2="{cx+cell}" y1="{oy}" y2="{oy}" stroke="#4a4" stroke-width="0.6"/>')
        parts.append(f'<line x1="{ox}" x2="{ox}" y1="{cy+16}" y2="{cy+ch}" stroke="#4a4" stroke-width="0.4"/>')
        for top, glyph, colour in layers:
            parts.append(f'<path transform="translate({ox},{oy}) scale({s},{-s})" d="{path(top, glyph)}" fill="{colour}"/>')
        parts.append(f'<text x="{cx+3}" y="{cy+12}" font-size="11" font-family="Arial" fill="red">{label}</text>')
    parts.append("</svg>")
    doc = pymupdf.open(stream="".join(parts).encode(), filetype="svg")
    doc[0].get_pixmap(dpi=96).save(out_png)
