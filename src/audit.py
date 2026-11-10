"""Account for every glyph in the dump: decoded, or dropped for a stated reason.

Usage: python src/audit.py tmp/glyphs.tsv
"""
import collections
import sys

import decode
import labels as LB
import layout


def main(tsv):
    pages = layout.load(tsv)
    why = collections.Counter()
    detail = collections.defaultdict(collections.Counter)
    total = sum(len(v) for v in pages.values())
    used = set()
    for num, ws in layout.verses(pages, decode.is_header):
        for w in ws:
            for c in w["cl"] + w["loose"] + w.get("lead", []) + w.get("inword", []):
                used.add(id(c))
    # re-walk with the same objects is not possible (verses rebuilt them), so classify per page instead
    for pno in sorted(pages):
        rows = pages[pno]
        for font, glyph, x, y, size in rows:
            if font not in layout.BASE_FONTS | layout.MARK_FONTS:
                why["other font (page furniture)"] += 1
                detail["other font (page furniture)"][font] += 1
            elif size > layout.MAX_SIZE:
                why["large size (title ornaments)"] += 1
                detail["large size (title ornaments)"][f"{font} {glyph}"] += 1
        cl = layout.clusters(rows)
        ws = layout.words(rows)
        placed = set()
        for w in ws:
            for c in w["cl"] + w["loose"] + w.get("lead", []) + w.get("inword", []):
                placed.add(id(c))
        # layout.words() ran clusters() again, so compare by value
        placed_keys = collections.Counter()
        for w in ws:
            for c in w["cl"] + w["loose"] + w.get("lead", []) + w.get("inword", []):
                placed_keys[(c["base"], tuple(c["marks"]), c["x"], c["y"])] += 1
        for c in cl:
            k = (c["base"], tuple(c["marks"]), c["x"], c["y"])
            if placed_keys[k]:
                placed_keys[k] -= 1
                continue
            r = "blank glyph" if all(g in layout.BLANK for g in c["marks"]) else "loose mark with no word on its line"
            why[r] += len(c["marks"])
            for g in c["marks"]:
                detail[r][f"{g[0]} {g[1]} p{pno}"] += 1
        # header lines
        line, prev = [], False
        for i, w in enumerate(ws):
            line.append(w)
            if i + 1 == len(ws) or ws[i + 1]["y"] != w["y"]:
                prev = decode.is_header(line, prev)
                if prev:
                    n = sum(1 + len(c["marks"]) for v in line for c in v["cl"])
                    why["surah title line"] += n
                line = []
        # marks that decode to nothing
        for w in ws:
            for c in w["cl"]:
                for g in c["marks"]:
                    if LB.WHOLE.get(g) == "":
                        why["ornament / calligraphic basmala"] += 1
                        detail["ornament / calligraphic basmala"][f"{g[0]} {g[1]}"] += 1
                    elif g[0] == "MSH-Quraan1" and LB.MSH_KIND.get(g[1]) == "patch":
                        why["cover-up bar"] += 1
                    elif g[0] != "MSH-Quraan1" and g not in LB.WHOLE:
                        for cid, _, _ in decode.COMP.get(f"{g[0]} {g[1]}", []):
                            if LB.KIND.get(cid) == "patch":
                                why["cover-up bar"] += 1
                if c["base"] in layout.SKIP_BASE:
                    why["connector bar / space"] += 1
    print("glyphs in dump:", total)
    for k, v in why.most_common():
        print(f"  not decoded: {v:6d}  {k}")
        for g, n in detail[k].most_common(12):
            print(f"        {n:5d}  {g}")


if __name__ == "__main__":
    main(sys.argv[1])
