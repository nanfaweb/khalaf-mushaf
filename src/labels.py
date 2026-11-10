"""Glyph -> Unicode tables for the Khalaf PDF fonts.

Base glyphs were identified from the glyph atlases (the fonts are laid out in alphabetical
order, one glyph per letter shape) and cross-checked by aligning against the KFGQPC Hafs
consonant skeleton. Mark shapes were identified by eye from true-position renders.
Output follows KFGQPC Uthmanic-script Unicode conventions.
"""

ALEF, WASLA_ALEF = "ا", "ٱ"
DOTLESS_YA = "ى"  # resolved to ى / ي in decode.py
DAGGER = "ٰ"
# hamza standing before the alif of a lam-alif (as in ٱلۡأٓخِرَةِ). The page shows the hamza
# with a fatha; KFGQPC spells this alif-hamza + madda with no fatha, and we follow that.
HAMZA_THEN_ALEF = "أٓ"


def _ranges(spec):
    out = {}
    for a, b, s in spec:
        for i in range(a, b + 1):
            out[f"g{i}"] = s
    return out


# value: tuple of letters (right-to-left), each letter is a string
def L(*letters):
    return tuple(letters)


BASE = {
    "HQPB1": _ranges([
        (4, 4, L("ل", "ل", "ه")),
        (6, 8, L("ا")), (9, 11, L("أ")), (12, 13, L("إ")), (16, 16, L("آ")),
        (18, 33, L("ب")), (34, 49, L("ت")), (50, 65, L("ث")), (66, 78, L("ج")),
        (79, 91, L("ح")), (92, 104, L("خ")), (105, 106, L("د")), (107, 108, L("ذ")),
        (109, 114, L("ر")), (115, 119, L("ز")), (121, 136, L("س")), (137, 152, L("ش")),
        (153, 169, L("ص")), (170, 186, L("ض")), (187, 190, L("ط")), (191, 194, L("ظ")),
        (195, 205, L("ع")), (206, 216, L("غ")), (217, 221, L("ف")),
    ]),
    "HQPB2": _ranges([
        (5, 7, L("ف")), (8, 16, L("ق")), (17, 27, L("ك")), (28, 36, L("ل")),
        (37, 52, L("م")), (53, 69, L("ن")), (70, 80, L("ه")), (81, 82, L("ة")),
        (83, 84, L("و")), (85, 87, L("ؤ")),
        (89, 90, L("ل", "ا")), (91, 92, L("ل", HAMZA_THEN_ALEF)), (93, 94, L("ل", "أ")), (95, 96, L("ل", "إ")), (97, 98, L("ل", "آ")),
        (99, 112, L("ي")), (113, 116, L(DOTLESS_YA)),
        (119, 137, L("ئ")), (139, 139, L("ـٔ")), (140, 149, L("ئ")),
        (154, 154, L(DAGGER)), (155, 155, L(DAGGER)), (165, 165, L(DAGGER)),
        (156, 156, L("ۥ")), (160, 160, L(DAGGER + "ء")), (158, 158, L("ۦ")), (159, 159, L("ـۧ")),
        (162, 163, L(DAGGER + "ٓ")), (166, 166, L("ن")),
        (179, 179, L(DOTLESS_YA)),
        (181, 181, L("ح")), (182, 182, L("ج")), (183, 183, L("ئ")), (186, 186, L("ج")),
        (187, 187, L("ح")), (188, 188, L("خ")), (189, 190, L("ص")), (191, 191, L("ض")),
        (196, 196, L("ء")), (197, 197, L(DAGGER)), (200, 200, L("ن")), (202, 202, L("ت")), (204, 204, L("ي")),
        (206, 206, L("ئ")), (207, 207, L("ي")), (208, 208, L("ن")), (210, 210, L("ت")),
        (211, 211, L("ب")), (212, 213, L("ئ")), (214, 214, L("ن")), (215, 215, L("ث")),
        (216, 216, L("ت")), (217, 217, L("ب")), (218, 219, L("ن")), (220, 220, L("ي")),
        (221, 221, L("م")),
    ]),
    "HQPB3": _ranges([
        (4, 6, L("ل")), (7, 7, L("د")), (8, 8, L("ذ")), (9, 9, L("ه")), (10, 10, L("ة")),
        (12, 12, L("ت")), (15, 15, L("ي")), (17, 17, L("ئ")), (18, 18, L("م")),
        (20, 20, L(DOTLESS_YA + DAGGER)), (27, 28, L(DOTLESS_YA + DAGGER)),
        (52, 52, L("ل")), (53, 53, L("م")), (54, 54, L("ه")), (55, 55, L("ل", "ل", "ه")),
        (56, 56, L("ب")), (57, 57, L("ت")), (58, 58, L("ث")), (59, 60, L("ق")),
        (61, 62, L("س")), (63, 63, L("ش")), (65, 65, L("ل")), (66, 66, L("ن")),
        (75, 75, L("ك")), (77, 77, L("ت")), (80, 80, L("ي")), (94, 95, L("ك")),
        (96, 96, L("ع")), (99, 99, L(DOTLESS_YA)), (102, 102, L("ه")), (105, 105, L("ص")),
        (107, 107, L("س")), (111, 111, L("ف")), (113, 113, L("ع")),
    ]),
}

# letters the typesetter patched in from another font for Khalaf-only spellings
BASE["MSH-Quraan1"] = {"g96": L("ي"), "g97": L("ل"), "g98": L("ا"), "g119": L("ح"), "g170": L("و"),
                       "g178": L("ك"), "g210": L("ء"), "g221": L("ي")}

# x boundaries (glyph units) splitting a multi-letter base into its letters, right to left
SPLITS = {3: (570, 300)}  # لله: lam | lam | ha ; two-letter bases split at bbox centre

# shape-class id (data/mark_components.json) -> kind
KIND = {}
for _k, _ids in {
    "stroke": (1, 3, 5, 6, 9, 15, 21, 33, 34, 38, 39, 65, 68, 71),
    "damma": (0, 11), "hook": (7,), "sukun": (2, 26), "shadda": (4, 20, 69),
    "madda": (8, 12, 22, 28, 43), "meem": (17, 29, 37), "wasla": (19,), "dagger": (25,),
    "zero": (27,), "oval": (36,), "dot": (30, 74, 75, 76), "ring": (67,), "seen": (35,),
    "ishmam": (40,), "patch": (41, 45),
}.items():
    for _i in _ids:
        KIND[_i] = _k

# whole-glyph meanings that bypass component analysis
WHOLE = {
    ("HQPB4", "g5"): "ۗ", ("HQPB4", "g21"): "ۗ", ("HQPB4", "g11"): "ۖ",
    ("HQPB4", "g22"): "ۚ", ("HQPB4", "g12"): "۩", ("HQPB4", "g13"): "۞",
    ("HQPB5", "g135"): "ۙ", ("HQPB5", "g136"): "ۛ", ("HQPB5", "g137"): "ۘ",
    ("MSH-Quraan1", "g7"): "ۖ", ("MSH-Quraan1", "g9"): "ۚ",
    ("MSH-Quraan1", "g155"): "", ("MSH-Quraan1", "g156"): "",
    ("HQPB4", "g3"): "", ("HQPB5", "g3"): "", ("MSH-Quraan1", "g3"): "",
    ("Hamd2", "g198"): "", ("Hamd2", "g199"): "", ("Hamd2", "g200"): "",  # calligraphic basmala
}
WAQF = set("ۖۗۘۙۚۛ۞۩")

# MSH-Quraan1 single marks: glyph -> list of (kind) placed by the glyph's own y
MSH_KIND = {
    "g17": "dagger", "g43": "dagger", "g78": "dagger", "g87": "dagger",
    "g29": "madda", "g30": "madda", "g33": "meem", "g36": "seen", "g38": "dot",
    "g41": "noon", "g46": "hamza", "g54": "damma", "g58": "stroke", "g60": "stroke",
    "g73": "stroke", "g70": "dammatan",
}

# Hamd2 pre-composed lam-alef with marks: (letters, marks on lam)
FATHATAN, OPEN_FATHATAN = "ً", "ٗ"
HAMD = {
    "g90": ("ل", OPEN_FATHATAN, "ا"), "g91": ("ل", OPEN_FATHATAN, "ا"),
    "g92": ("ل", FATHATAN, "ا"), "g93": ("ل", FATHATAN, "ا"),
    "g96": ("ل", "َۢ", "ا"), "g97": ("ل", "َۢ", "ا"),
    "g98": ("ل", "َّۢ", "ا"),
    "g101": ("ل", "ّ" + FATHATAN, "ا"), "g103": ("ل", "ّ" + OPEN_FATHATAN, "ا"),
    "g104": ("ل", "ّ" + OPEN_FATHATAN, "ا"),
    "g105": ("ل", "ِ", "إِ"), "g100": ("ل", "ِّ", "إِ"),
}
