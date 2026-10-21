#!/usr/bin/env python3
"""Build colour-scheme auditions of the Yuzu set from master.yaml: same legends/slots as render_yuzu.py, but with
per-zone cap colours, per-scheme inks and an optional solid dot on the layer keys (vector legend).
Hex colours are mapped to the nearest Yuzu dye-sub colour (yuzu/colors.txt, from /api/dev/colors).
Usage: yuzu_variant.py SCHEME [...]  -> yuzu/variants/<SCHEME>.json (+ a colour-mapping report)"""
import json, os, sys
from fontTools.ttLib import TTFont
from PIL import ImageFont, Image, ImageDraw
from common import load_master, ROOT

m = load_master(); st = m["style"]; K = m["keys"]
FONT = f"{ROOT}/fonts/HelvNowCn575BL.ttf"
tt = TTFont(FONT); CAPR = tt["OS/2"].sCapHeight / tt["head"].unitsPerEm
_F = ImageFont.truetype(FONT, 400); _d = ImageDraw.Draw(Image.new("L", (4, 4)))
def width_per_cap_mm(t): return _d.textlength(t, font=_F, features=["kern"]) / (400 * CAPR)
TOP_W = {"1u": 11.45, "1uh": 11.55, "1.5u": 20.98, "1.5uv": 11.25, "2uv": 11.25}
H0, HV = st["cap_mm_l0"], st["cap_mm_var"]
c0 = st["top_y"] + H0 / 2; c1 = st["top_y"] + H0 + st["gap_after_l0"] + HV / 2
c2 = c1 + HV + st["gap_var"]; c3 = c2 + HV + st["gap_var"]
SLOT = [c0, c1, c2, c3]
def size(cap_mm): return round(cap_mm / st["cap_ratio"], 2)

# ---- Yuzu palette
PAL = {}
for tok in open(f"{ROOT}/yuzu/colors.txt").read().split():
    i, h = tok.split(":"); PAL[i] = h
def _rgb(h): return tuple(int(h[k:k + 2], 16) for k in (1, 3, 5))
def _lab(h):
    r, g, b = [c / 255 for c in _rgb(h)]
    f = lambda c: ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    r, g, b = f(r), f(g), f(b)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047; y = r * 0.2126 + g * 0.7152 + b * 0.0722; z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    g2 = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = g2(x), g2(y), g2(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)
_LABS = {i: _lab(h) for i, h in PAL.items()}
REPORT = {}
def nearest(hexc):
    if hexc in PAL: return hexc
    if not hexc.startswith("#"): raise KeyError(hexc)
    L, A, B = _lab(hexc)
    best = min(PAL, key=lambda i: (_LABS[i][0] - L) ** 2 + (_LABS[i][1] - A) ** 2 + (_LABS[i][2] - B) ** 2)
    REPORT[hexc] = f"{best} {PAL[best]}"; return best

# ---- zones (same as the PIL exploration)
ZONE = {}
def z(names, zone):
    for n in names.split(): ZONE[n] = zone
z("1A R1A R1B", "sys"); z("2A 2B 2C 2D 2E", "view"); z("R2A R2B R3A R3B R3C R3E R4E", "misc"); z("3A 4A 5A", "marks")
z("3B 5B 3C 4C 5C", "nav"); z("4B", "bypass"); z("3D 4D 5D", "kf"); z("1B 1C 1D 1E", "layer"); z("6A 6B 6C 6D", "shape")
z("7B 7D", "dbs"); z("3E 4E 5E", "edit"); z("7A", "blank"); z("T2 T5 T6 RT2 RT5 RT6", "mod"); z("T1 RT1", "undo")
z("T3 RT3", "l1key"); z("T4 RT4", "l2key"); z("R2C R1D R2D R3D", "arrows")
z("R4A R5A R6A R7A R4B R5B R6B R7B R4C R5C R6C R7C R4D R5D R6D R7D R5E R6E R7E", "num")

DK = ["#262626", "#db3537", "#346563", "#2b4782"]          # current inks (black, RD003, GN010, BL023)
LT = ["#faf7f0", "#ff8a7a", "#7fe0b8", "#9cc8ff"]          # light inks for dark caps
SCHEMES = {
 "B1": dict(dot=True, inks_light=DK, inks_dark=LT,   # palette ids chosen by hand: Yuzu has no paler tints than these
    caps={"default": "GR002", "sys": "GR020", "view": "BL034", "marks": "YW019", "nav": "PK014", "bypass": "PK014",
          "kf": "PK014", "layer": "GN025", "shape": "PL018", "dbs": "GN004", "edit": "BN020", "blank": "GR002",
          "mod": "GR020", "undo": "GR020", "l1key": "GR020", "l2key": "GR020", "num": "GR002", "arrows": "GN004", "misc": "BN002"}),
 "C": dict(dot=True, dot_colors=("OG030", "GN011"), inks_light=DK, inks_dark=LT,   # Yuzu's dark palette is small; ids picked by hand
    caps={"default": "GR001", "sys": "GR001", "view": "BL010", "marks": "BN024", "nav": "RD006", "bypass": "RD006",
          "kf": "RD006", "layer": "GN022", "shape": "PL004", "dbs": "GN009", "edit": "GN037", "blank": "GR001",
          "mod": "GR029", "undo": "GR029", "l1key": "GR001", "l2key": "GR001", "num": "GR001", "arrows": "GR028", "misc": "BN019"}),
 "F": dict(dot=True, dot_colors=("PK014", "GN004"), inks_light=DK, inks_dark=["#faf7f0", "#ffd1c9", "#c9f5e2", "#cfe3ff"],
    caps={"default": "GR001", "sys": "GR001", "view": "BL022", "marks": "OG010", "nav": "RD025", "bypass": "RD025",
          "kf": "RD025", "layer": "GN023", "shape": "PL002", "dbs": "GN010", "edit": "YW026", "blank": "GR001",
          "mod": "GR029", "undo": "GR029", "l1key": "GR001", "l2key": "GR001", "num": "GR001", "arrows": "GN007", "misc": "BN034"}),
 "G": dict(dot=False, inks_light=["#262626"] * 4, inks_dark=["#faf7f0"] * 4,
    caps={"default": "#d9d5ce", "sys": "#b8b3ab", "view": "#4a90d9", "marks": "#f0a030", "nav": "#e74c3c", "bypass": "#e74c3c",
          "kf": "#e74c3c", "layer": "#7cb342", "shape": "PL021", "dbs": "#16a085", "edit": "#f1c40f", "blank": "#d9d5ce",
          "mod": "#b8b3ab", "undo": "#b8b3ab", "l1key": "#d8232a", "l2key": "#1f9d4a", "num": "#d9d5ce", "arrows": "GN005", "misc": "BN039"}),
}
def is_dark(h):
    r, g, b = _rgb(PAL.get(h, h)); return 0.299 * r + 0.587 * g + 0.114 * b < 128
DOT = dict(vectDef="M12 2a10 10 0 1 0 0 20a10 10 0 1 0 0-20z", vectViewbox="0 0 24 24", vectScale=44, x=0, y=0)  # ≈7 mm

def build(tag):
    sc = SCHEMES[tag]; REPORT.clear()
    tpl = json.load(open(f"{ROOT}/yuzu/template.json")); keys = {}
    for name, e in K.items():
        zone = ZONE.get(name, "default"); cap_hex = sc["caps"].get("l1key" if zone == "mod" else zone, sc["caps"]["default"])
        cap = nearest(cap_hex)
        inks = [nearest(h) for h in (sc["inks_dark"] if is_dark(cap_hex) else sc["inks_light"])]
        layers = []
        if sc["dot"] and zone in ("l1key", "l2key"):
            dc = sc.get("dot_colors", ("RD003", "GN010"))
            layers.append(dict(colorId=dc[0] if zone == "l1key" else dc[1], **DOT))
        elif zone in ("l1key", "l2key"):
            inks = [nearest(h) for h in LT]
            for layer, lay in sorted(e["layers"].items()):
                t = lay.get("cap", "")
                if t: layers.append(dict(colorId=inks[layer], textLabel=t, textFontId=st["font_label"], textSize=size(H0 if layer == 0 else HV), x=0, y=round(SLOT[layer], 2)))
        elif zone == "mod":
            t = e["layers"].get(0, {}).get("cap", "")
            cap_mm = min(st["big_cap_max_mm"], (TOP_W["1u"] - 1.2) / max(width_per_cap_mm(x) for x in ("ALT", "SHIFT", "CTRL")))
            layers.append(dict(colorId=inks[0], textLabel=t, textFontId=st["font_label"], textSize=size(cap_mm), x=0, y=0))
        elif name in st["big_keys"]:
            t = e["layers"].get(0, {}).get("cap", "")
            if t:
                cap_mm = min(st["big_cap_max_mm"], (TOP_W[e["size"]] - 1.2) / width_per_cap_mm(t))
                if t.isalpha() and len(t) > 1:  # word legends (NUM, ENTER) share one size: the one that fits NUM on a 1u key
                    cap_mm = min(st["big_cap_max_mm"], (TOP_W["1u"] - 1.2) / width_per_cap_mm("NUM"))
                layers.append(dict(colorId=inks[0], textLabel=t, textFontId=st["font_big"], textSize=size(cap_mm), x=0, y=0))
        else:
            for layer, lay in sorted(e["layers"].items()):
                t = lay.get("cap", "")
                if not t: continue
                for n, line in enumerate(t.split("\n")):
                    cap_mm = H0 if layer == 0 else HV
                    need = width_per_cap_mm(line) * cap_mm
                    if need > TOP_W[e["size"]] - 0.9: cap_mm = (TOP_W[e["size"]] - 0.9) / width_per_cap_mm(line)
                    layers.append(dict(colorId=inks[layer], textLabel=line, textFontId=st["font_label"], textSize=size(cap_mm), x=0, y=round(SLOT[layer + n], 2)))
        keys[e["yuzu"]] = {"colorId": cap, "layers": layers}
    out = dict(tpl); out["name"] = f"Audition {tag}"; out["author"] = "Nat"; out["keys"] = keys; out["keyTemplates"] = {}; out["designUrl"] = None
    os.makedirs(f"{ROOT}/yuzu/variants", exist_ok=True)
    json.dump(out, open(f"{ROOT}/yuzu/variants/{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{tag}: yuzu/variants/{tag}.json  colour mapping:"); [print(f"   {h} -> {v}") for h, v in REPORT.items()]

for tag in sys.argv[1:] or SCHEMES: build(tag)
