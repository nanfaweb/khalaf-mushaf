"""Turn the raw glyph dump into reading-order words grouped by verse.

A cluster is one base glyph plus the mark glyphs drawn at the same origin, or a lone mark
(pause signs, ornaments). The PDF draws each word as one left-to-right run and has no
space glyphs, so a new word starts wherever x steps back to the left (or the line changes).
Verses are split on the verse-number digits (HQPB2 g169-g178).
"""
import csv
from collections import defaultdict

BASE_FONTS = {"HQPB1", "HQPB2", "HQPB3"}
MARK_FONTS = {"HQPB4", "HQPB5", "HQPB7", "MSH-Quraan1", "Hamd2"}
# glyphs in the "mark" fonts that are really stand-alone letters / ligatures
EXTRA_BASES = {("Hamd2", f"g{i}") for i in (90, 91, 92, 93, 96, 97, 98, 100, 101, 103, 104, 105)} | {
    ("MSH-Quraan1", g) for g in ("g96", "g97", "g98", "g119", "g170", "g178", "g210", "g221")
}
DIGITS = {f"g{169 + i}": i for i in range(10)}  # HQPB2
ORNAMENTS = {"g167", "g168", "g193", "g194"}  # HQPB2 verse-number brackets
SKIP_BASE = {("HQPB1", "g3"), ("HQPB2", "g3"), ("HQPB2", "g164")}  # space, kashida bar
MAX_SIZE = 18.5
HIZB = ("HQPB4", "g13")
# pause / sajdah signs that stand between words (everything else loose belongs inside a word)
SIGNS = {("HQPB4", g) for g in ("g5", "g21", "g11", "g22", "g12")} | {
    ("HQPB5", g) for g in ("g135", "g136", "g137")} | {("MSH-Quraan1", "g7"), ("MSH-Quraan1", "g9")}
BLANK = {("Hamd2", "g3"), ("HQPB4", "g3"), ("HQPB5", "g3"), ("MSH-Quraan1", "g3"), ("Hamd2", "g198"), ("Hamd2", "g199"), ("Hamd2", "g200")}


def load(tsv):
    pages = defaultdict(list)
    with open(tsv, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pages[int(r["page"])].append(
                (r["font"], r["glyph"], float(r["x"]), float(r["y"]), float(r["size"]))
            )
    return pages


def clusters(page_rows):
    """Clusters in stream order: {base, marks, x, y}. Body-size text only."""
    out, pending = [], []
    px = py = None
    for font, glyph, x, y, size in page_rows:
        # body text is 13.98pt; a few words are squeezed to 12pt. Titles' ornaments are ~20pt.
        if size > MAX_SIZE or font not in BASE_FONTS | MARK_FONTS:
            continue
        same = px is not None and abs(x - px) < 0.1 and y == py
        if pending and not same:
            out.append({"base": None, "marks": pending, "x": px, "y": py})
            pending = []
        if font in BASE_FONTS or (font, glyph) in EXTRA_BASES:
            last = out[-1] if out else None
            if last and last["base"] == (font, glyph) and abs(last["x"] - x) < 0.1 and last["y"] == y:
                last["marks"] += [m for m in pending if m not in last["marks"]]  # fake-bold repeat
            elif (font, glyph) in SKIP_BASE:
                if pending:  # a mark sitting on a connector bar: keep it as a loose mark
                    out.append({"base": None, "marks": pending, "x": x, "y": y})
            else:
                out.append({"base": (font, glyph), "marks": pending, "x": x, "y": y})
            pending = []
            px = None
        else:
            if (font, glyph) not in pending:  # repeats are fake-bold overprints
                pending.append((font, glyph))
            px, py = x, y
    if pending:
        out.append({"base": None, "marks": pending, "x": px, "y": py})
    return out


def _is_num(c):
    return c["base"][0] == "HQPB2" and (c["base"][1] in DIGITS or c["base"][1] in ORNAMENTS)


def _dist(w, m):
    if w["x0"] - 1 <= m["x"] <= w["x1"]:
        return 0
    return min(abs(m["x"] - w["x0"]), abs(m["x"] - w["x1"]))


def words(page_rows):
    """Words in reading order; each word is a list of clusters, right to left.

    Lone marks are attached (key "loose") to the word on the same line nearest in x.
    """
    ws, loose = [], []
    prev = None
    for c in clusters(page_rows):
        if c["base"] is None:
            loose.append(c)
            continue
        if prev is None or c["y"] != prev["y"] or c["x"] < prev["x"] or _is_num(c) != _is_num(prev):
            ws.append({"cl": [], "loose": []})
        ws[-1]["cl"].append(c)
        prev = c
    for w in ws:
        w["cl"].sort(key=lambda c: -c["x"])
        w["y"] = w["cl"][0]["y"]
        w["x1"] = w["cl"][0]["x"] + 6.0  # rough right edge
        w["x0"] = w["cl"][-1]["x"]
    for m in loose:
        line = [w for w in ws if w["y"] == m["y"]]
        if not line:
            continue
        if HIZB in m["marks"]:
            # the hizb rosette stands before the word on its left
            left = [w for w in line if w["x0"] <= m["x"] + 8]
            w = max(left, key=lambda w: w["x0"]) if left else min(line, key=lambda w: _dist(w, m))
            w.setdefault("lead", []).append(m)
            continue
        if all(g in BLANK for g in m["marks"]):
            continue
        if not any(g in SIGNS for g in m["marks"]):
            text = [w for w in line if not _is_num(w["cl"][0])] or line
            min(text, key=lambda w: _dist(w, m)).setdefault("inword", []).append(m)
            continue
        # pause signs are drawn 4-8pt left of the end of the word they belong to
        right = [w for w in line if w["x0"] >= m["x"] - 1]
        w = min(right, key=lambda w: w["x0"]) if right else min(line, key=lambda w: _dist(w, m))
        w["loose"].append(m)
    ws.sort(key=lambda w: (w["y"], -w["x1"]))
    return ws


def verses(pages, is_header=None):
    """Yield (verse_number_read_from_page, [words]) across the whole document.

    is_header(line_words, previous_line_was_header) -> True drops that line (surah titles).
    """
    cur, digits, held = [], [], []
    for pno in sorted(pages):
        kept, line, prev_hdr = [], [], False
        ws = words(pages[pno])
        for i, w in enumerate(ws):
            line.append(w)
            if i + 1 == len(ws) or ws[i + 1]["y"] != w["y"]:
                prev_hdr = bool(is_header and is_header(line, prev_hdr))
                if not prev_hdr:
                    kept += line
                line = []
        for w in kept:
            w["page"] = pno
            bases = [c["base"] for c in w["cl"]]
            if all(b[0] == "HQPB2" and (b[1] in DIGITS or b[1] in ORNAMENTS) for b in bases):
                # digits are drawn left-to-right; clusters are sorted right-to-left
                digits += [DIGITS[b[1]] for b in reversed(bases) if b[1] in DIGITS]
                if w["loose"] and cur:
                    cur[-1]["loose"] += w["loose"]
                held += w.get("lead", [])  # a hizb rosette at a line end: goes to the next word
                continue
            if held:
                w["lead"] = held + w.get("lead", [])
                held = []
            if digits:
                yield int("".join(map(str, digits))), cur
                cur, digits = [], []
            cur.append(w)
    if digits:
        yield int("".join(map(str, digits))), cur
    elif cur:
        yield None, cur
