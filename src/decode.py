"""Decode the Khalaf PDF glyph dump into Unicode text, one verse per line.

Usage: python src/decode.py tmp/glyphs.tsv out/khalaf.tsv
"""
import json
import os
import sys

import labels as LB
import layout
import shapes

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = json.load(open(os.path.join(HERE, "..", "data", "mark_components.json")))["table"]
_fonts = shapes.load_fonts()
_bbox = {}

ORDER = ["hamza", "shadda", "vowel", "ishmam", "sukun", "zero", "oval", "dagger", "madda", "meem",
         "dot", "ring", "seen", "noon"]
SIMPLE = {"shadda": "ّ", "sukun": "ۡ", "zero": "ْ", "oval": "۠",
          "dagger": "ٰ", "madda": "ٓ", "dot": "ٜ", "ring": "۪",
          "seen": "ۜ", "noon": "ۨ", "ishmam": "۬"}


def base_bbox(font, glyph):
    k = (font, glyph)
    if k not in _bbox:
        pts = [p for c in shapes.contours(_fonts[font], glyph) for p in c]
        _bbox[k] = shapes.bbox(pts) if pts else (0, 0, 0, 0)
    return _bbox[k]


def letter_index(base, n, x):
    """Which of the n letters (right to left) of a ligature a mark at x belongs to."""
    if n == 1:
        return 0
    if n == 3:
        hi, lo = LB.SPLITS[3]
        return 0 if x > hi else 1 if x > lo else 2
    return 0 if x > 400 else 1  # lam-alif: marks left of 400 units sit on the alif arm


def mark_string(parts, unknown):
    """parts: [(kind, x, y)] for one letter -> combining string in KFGQPC order."""
    out = {}
    uniq = []  # the same mark drawn twice by two overlaid glyphs counts once
    for p in parts:
        if not any(q[0] == p[0] and abs(q[1] - p[1]) < 80 and abs(q[2] - p[2]) < 80 for q in uniq):
            uniq.append(p)
    parts = uniq
    up = [p for p in parts if p[0] == "stroke" and p[2] > 300]
    dn = [p for p in parts if p[0] == "stroke" and p[2] <= 300]
    dam = [p for p in parts if p[0] == "damma"]
    hook = [p for p in parts if p[0] == "hook"]
    v = ""
    if len(up) == 2:
        v += "ً" if abs(up[0][1] - up[1][1]) < 30 else "ٗ"
    elif len(up) == 1:
        v += "َ"
    elif len(up) > 2:
        unknown.append("strokes-above>2")
    if len(dam) == 2:
        v += "ٞ"
    elif len(dam) == 1:
        v += "ٌ" if hook else "ُ"
    if any(p[0] == "dammatan" for p in parts):
        v += "ٌ"
    if len(dn) == 2:
        v += "ٍ" if abs(dn[0][1] - dn[1][1]) < 30 else "ٖ"
    elif len(dn) == 1:
        v += "ِ"
    elif len(dn) > 2:
        unknown.append("strokes-below>2")
    out["vowel"] = v
    for kind, x, y in parts:
        if kind in SIMPLE:
            out[kind] = SIMPLE[kind]
        elif kind == "meem":
            out["meem"] = "ۢ" if y > 0 else "ۭ"
        elif kind == "hamza":
            out["hamza"] = "ٔ" if y > 300 else "ٕ"
    return "".join(out.get(k, "") for k in ORDER)


IMALA = SIMPLE["dot"]


def placeholder(font, glyph):
    return f"⟦{font}:{glyph}⟧"


def decode_cluster(c, unknown):
    """-> ([[letter, marks]], trailing signs)"""
    b = c["base"]
    all_marks = list(c["marks"]) + list(c.get("extra", []))
    trailing = ""
    if b[0] == "Hamd2":
        if b[1] in LB.HAMD:
            l, m, a = LB.HAMD[b[1]]
            return [[l, m], [a, ""]], ""
        if b[1] == "g3":
            return [["ا", "ٜ"]], ""
        unknown.append(f"{b[0]}:{b[1]}")
        return [[placeholder(*b), ""]], ""
    letters = LB.BASE.get(b[0], {}).get(b[1])
    if letters is None:
        unknown.append(f"{b[0]}:{b[1]}")
        letters = (placeholder(*b),)
    n = len(letters)
    parts = [[] for _ in range(n)]
    wasla = False
    carry = ""
    for font, g in all_marks:
        if (font, g) in LB.WHOLE:
            trailing += LB.WHOLE[(font, g)]
            continue
        comps = COMP.get(f"{font} {g}")
        if not comps:
            unknown.append(f"{font}:{g}")
            continue
        if font == "MSH-Quraan1":
            kind = LB.MSH_KIND.get(g)
            if kind is None:
                unknown.append(f"{font}:{g}")
            elif kind == "dagger" and n == 1 and comps[0][1] > 350 and (font, g) in c["marks"]:
                carry += LB.DAGGER  # drawn past the right edge: it follows the previous letter
            elif kind != "patch":
                parts[letter_index(b, n, comps[0][1])].append((kind, comps[0][1], comps[0][2]))
            continue
        kinds = [LB.KIND.get(cid) for cid, _, _ in comps]
        # a tanwin (two strokes above) over a lam-alif belongs to the lam
        pair_on_lam = (n == 2 and len(comps) == 2 and kinds.count("stroke") == 2
                       and all(y > 300 for _, _, y in comps) and abs(comps[0][1] - comps[1][1]) < 150)
        for cid, x, y in comps:
            kind = LB.KIND.get(cid)
            if kind is None:
                unknown.append(f"{font}:{g}#c{cid}")
            elif kind == "patch":
                pass  # a blank bar the typesetter used to cover the Hafs form
            elif kind == "wasla":
                wasla = True
            else:
                parts[0 if pair_on_lam else letter_index(b, n, x)].append((kind, x, y))
    out = []
    for letter, p in zip(letters, parts):
        if wasla and letter == LB.ALEF:
            letter = LB.WASLA_ALEF
        marks = mark_string(p, unknown)
        if letter == LB.HAMZA_THEN_ALEF:
            marks = marks.replace("َ", "")
        if letter == LB.ALEF and marks.startswith("ٔ"):
            letter, marks = "أ", marks[1:]
        out.append([letter, marks])
    if carry:
        out[0].append(carry)
    return out, trailing


VOWELISH = set("ًٌٍَُِّْٖٗٞۡ")


def resolve_ya(tokens):
    """Dotless final ya: keep as alif maqsura or turn into ya, following KFGQPC spelling."""
    for i, t in enumerate(tokens):
        if not t[0].startswith(LB.DOTLESS_YA):
            continue
        if i and tokens[i - 1][0] == LB.DAGGER and not t[1]:
            # free-standing small alif drawn before the ya: KFGQPC writes it after (ىٰ)
            t[1] = LB.DAGGER + tokens[i - 1][1]
            tokens[i - 1][0] = tokens[i - 1][1] = ""
            continue
        marks = t[0][1:] + t[1]
        prev = tokens[i - 1][1] if i else ""
        if "ٰ" in marks:
            continue
        if set(marks) & VOWELISH:
            t[0] = "ي" + t[0][1:]
        elif set(prev) & set("ًَٜٗ"):
            continue
        else:
            t[0] = "ي" + t[0][1:]


def attach_inword(w):
    """Marks drawn on their own inside a word: give them to the right letter."""
    for c in w["cl"]:
        c.pop("extra", None)
    for m in w.get("inword", []):
        near = min(w["cl"], key=lambda c: abs(c["x"] - m["x"]))
        if abs(near["x"] - m["x"]) > 1.0:
            # e.g. a free-standing small alif: it follows the letter on its right
            right = [c for c in w["cl"] if c["x"] >= m["x"]]
            if right:
                near = min(right, key=lambda c: c["x"])
        near.setdefault("extra", []).extend(m["marks"])


def decode_word(w, unknown):
    tokens, trailing = [], ""
    attach_inword(w)
    for c in w["cl"]:
        t, tr = decode_cluster(c, unknown)
        if len(t[0]) == 3:  # marks that belong to the letter before this cluster
            carry = t[0].pop()
            if tokens:
                tokens[-1][1] += carry
        tokens += t
        trailing += tr
    lead = ""
    for m in w["loose"]:
        for font, g in m["marks"]:
            if (font, g) in LB.WHOLE:
                trailing += LB.WHOLE[(font, g)]
            else:
                unknown.append(f"loose {font}:{g}")
    for m in w.get("lead", []):
        for font, g in m["marks"]:
            lead += LB.WHOLE.get((font, g), "")
    for i, t in enumerate(tokens):
        # an imala dot drawn under the alif belongs to the letter before it
        if i and t[0] == LB.ALEF and IMALA in t[1] and IMALA not in tokens[i - 1][1]:
            t[1] = t[1].replace(IMALA, "")
            tokens[i - 1][1] += IMALA
    resolve_ya(tokens)
    body = "".join(l + m for l, m in tokens)
    return lead + LB.WORD_FIXES.get(body, body) + trailing


def _skeleton(t):
    return "".join(ch for ch in t if "ء" <= ch <= "ي" or ch == "ٱ")


def is_header(line, prev_was_header):
    """Surah title line (سورة ...) and the مكية/مدنية line under it."""
    text = [w for w in line if not layout._is_num(w["cl"][0])]
    if not text:
        return False
    sks = [_skeleton(decode_word(w, [])) for w in text]
    if sks[0].startswith("سورة"):
        # titles are short or carry مكية/مدنية; a verse may also begin with the word سورة (24:1)
        return len(text) <= 4 or "مكية" in sks or "مدنية" in sks
    return prev_was_header and sks[0] in ("مكية", "مدنية")


def decode_verses(tsv):
    """Yield (index, number_on_page, first_page, text, unknown list)."""
    pages = layout.load(tsv)
    for i, (num, ws) in enumerate(layout.verses(pages, is_header)):
        unknown = []
        text = " ".join(decode_word(w, unknown) for w in ws)
        yield i, num, (ws[0]["page"] if ws else None), text, unknown


def main(tsv, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    n = bad = sura = 0
    with open(out_path, "w", encoding="utf-8", newline=chr(10)) as out:
        print("sura", "aya", "pdf_page", "text", sep=chr(9), file=out)
        for i, num, page, text, unknown in decode_verses(tsv):
            if num == 1:
                sura += 1  # verse numbers printed in the PDF restart at each surah
            print(sura, num, page, text, sep=chr(9), file=out)
            n += 1
            bad += bool(unknown)
            for u in unknown:
                print(f"unresolved in {sura}:{num} (page {page}): {u}")
    print(f"{n} verses in {sura} surahs written to {out_path}; {bad} contain unresolved glyphs")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
