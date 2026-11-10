"""Compare the decoded text with the KFGQPC Hafs text to find decoding errors.

Hafs is NOT the expected answer (Khalaf really differs); this only surfaces patterns.
Systematic garbage means a decoder bug; consistent small differences are the reading.

Usage: python src/compare.py tmp/glyphs.tsv tmp/ref/hafsData_v18.json [report.txt]
"""
import collections
import difflib
import json
import sys

import decode


def skeleton(t):
    return "".join(c for c in t if ("ء" <= c <= "ي" and c != "ـ") or c == "ٱ")


def hafs_clean(t):
    t = t.replace(" ", " ")
    return "".join(c for c in t if not ("٠" <= c <= "٩")).strip()


def main(tsv, ref, report=None):
    h = json.load(open(ref, encoding="utf-8"))
    out = open(report, "w", encoding="utf-8") if report else sys.stdout
    same_skel = same_words = same_all = n = 0
    unknown = collections.Counter()
    skel_ops = collections.Counter()
    word_ops = collections.Counter()
    examples = {}
    for i, num, page, text, unk in decode.decode_verses(tsv):
        a = h[i]
        ref_t = hafs_clean(a["aya_text"])
        n += 1
        for u in unk:
            unknown[u] += 1
        s1, s2 = skeleton(text), skeleton(ref_t)
        if s1 == s2:
            same_skel += 1
        else:
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, s1, s2, autojunk=False).get_opcodes():
                if op != "equal":
                    k = (s1[i1:i2], s2[j1:j2])
                    skel_ops[k] += 1
                    examples.setdefault(k, (a["sora"], a["aya_no"], page))
        w1, w2 = text.split(), ref_t.split()
        if len(w1) == len(w2):
            same_words += 1
            for x, y in zip(w1, w2):
                if x != y:
                    word_ops[(x, y)] += 1
                    examples.setdefault((x, y), (a["sora"], a["aya_no"], page))
        if text == ref_t:
            same_all += 1
    p = lambda *a: print(*a, file=out)
    p(f"verses {n}; same skeleton {same_skel}; same word count {same_words}; identical to Hafs {same_all}")
    p("\n== unresolved glyphs ==")
    for k, v in unknown.most_common():
        p(v, k)
    p("\n== skeleton differences (decoded -> hafs) ==")
    for k, v in skel_ops.most_common(150):
        p(v, repr(k[0]), repr(k[1]), k[0], k[1], examples[k])
    p("\n== word differences in verses with equal word count (decoded | hafs) ==")
    for k, v in word_ops.most_common(400):
        p(v, k[0], "|", k[1], examples[k], " ".join(f"{ord(c):04X}" for c in k[0]), "|", " ".join(f"{ord(c):04X}" for c in k[1]))


if __name__ == "__main__":
    main(*sys.argv[1:])
