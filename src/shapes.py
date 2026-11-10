"""Break mark glyphs into components and give each distinct outline shape an id.

Many mark glyphs are the same drawing (a fatha, a shadda...) placed at a different
offset, or several such drawings combined. Naming each distinct shape once names them all.
"""
import glob
import os
from collections import defaultdict

from fontTools.cffLib import CFFFontSet
from fontTools.pens.recordingPen import RecordingPen

PKG = os.path.join(os.path.dirname(__file__), "..", "khalaf_recovery_package")


def load_fonts():
    fonts = {}
    for p in glob.glob(os.path.join(PKG, "font_*.cff")):
        name = os.path.basename(p)[:-4].split("_", 2)[2]
        cff = CFFFontSet()
        cff.decompile(open(p, "rb"), None)
        fonts[name] = cff[cff.fontNames[0]]
    return fonts


def contours(top, glyph):
    """List of contours; each is a list of (x, y) on/off-curve points."""
    pen = RecordingPen()
    top.CharStrings[glyph].draw(pen)
    out, cur = [], []
    for op, args in pen.value:
        if op == "moveTo":
            if cur:
                out.append(cur)
            cur = [args[0]]
        elif op in ("lineTo", "curveTo", "qCurveTo"):
            cur.extend(args)
        elif op in ("closePath", "endPath"):
            if cur:
                out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def components(top, glyph):
    """Group contours whose boxes nest/overlap; return [(shape_key, bbox)]."""
    cs = [(c, bbox(c)) for c in contours(top, glyph)]
    groups = []
    for c, b in sorted(cs, key=lambda t: -(t[1][2] - t[1][0]) * (t[1][3] - t[1][1])):
        for g in groups:
            gb = g["bbox"]
            if b[0] >= gb[0] - 1 and b[1] >= gb[1] - 1 and b[2] <= gb[2] + 1 and b[3] <= gb[3] + 1:
                g["cs"].append(c)
                break
        else:
            groups.append({"bbox": b, "cs": [c]})
    out = []
    for g in groups:
        x0, y0, x1, y1 = g["bbox"]
        # shape key: translation-invariant point list (rounded) of all contours
        key = tuple(sorted(tuple((round(x - x0), round(y - y0)) for x, y in c) for c in g["cs"]))
        out.append((key, g["bbox"]))
    return out


def shape_table(fonts, font_names):
    """Return ({shape_key: id}, {(font, glyph): [(id, bbox)]})."""
    ids, glyphs = {}, {}
    for fn in font_names:
        top = fonts[fn]
        for g in top.charset:
            if g == ".notdef":
                continue
            comps = []
            for key, bb in components(top, g):
                sid = ids.setdefault(key, len(ids))
                comps.append((sid, bb))
            glyphs[(fn, g)] = comps
    return ids, glyphs
