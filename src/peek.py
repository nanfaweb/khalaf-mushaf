"""Find decoded words and render the matching PDF region, for checking by eye.

Usage: python src/peek.py <pdf> tmp/glyphs.tsv <out.png> <sura:aya or 'p<page>'> [substring]
Prints each word of the verse with its glyphs; renders the lines of the verse (or matching words).
"""
import json
import sys

import pymupdf

import decode
import layout


def main(pdf, tsv, out_png, where, sub=None, ref="tmp/ref/hafsData_v18.json"):
    pages = layout.load(tsv)
    h = json.load(open(ref, encoding="utf-8"))
    s, a = map(int, where.split(":"))
    idx = next(i for i, v in enumerate(h) if v["sora"] == s and v["aya_no"] == a)
    num, ws = list(layout.verses(pages, decode.is_header))[idx]
    sel = []
    for w in ws:
        t = decode.decode_word(w, [])
        hit = sub is None or sub in t
        if hit:
            sel.append(w)
        print("*" if hit else " ", w["page"], round(w["y"]), round(w["x0"]), t,
              [(c["base"][0][-1] + c["base"][1], [m[0][-1] + m[1] for m in c["marks"]]) for c in w["cl"]],
              [m["marks"] for m in w["loose"]])
    if not sel:
        return
    doc = pymupdf.open(pdf)
    pno = sel[0]["page"]
    on = [w for w in sel if w["page"] == pno]
    x0 = min(w["x0"] for w in on) - 25
    x1 = max(w["x1"] for w in on) + 25
    y0 = min(w["y"] for w in on) - 24
    y1 = max(w["y"] for w in on) + 14
    if sub is None:
        x0, x1 = 60, 540
    doc[pno - 1].get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), dpi=450 if sub else 220).save(out_png)


if __name__ == "__main__":
    main(*sys.argv[1:])
