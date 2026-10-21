#!/usr/bin/env python3
"""Build colour-scheme auditions of the Yuzu set from master.yaml: same legends/slots as render_yuzu.py, but with
per-zone cap colours, per-scheme inks and an optional solid dot on the layer keys (vector legend).
Hex colours are mapped to the nearest Yuzu dye-sub colour (yuzu/colors.txt, from /api/dev/colors).
Usage: yuzu_variant.py SCHEME [...]  -> yuzu/variants/<SCHEME>.json (+ a colour-mapping report)"""
import json, os, sys
from common import load_master, ROOT
from legends import width_per_cap_mm, TOP_W, slots, text_layers, corner_layer, fit
import legends

m = load_master(); st = m["style"]; K = m["keys"]
H0, HV = st["cap_mm_l0"], st["cap_mm_var"]
SLOT = slots(st)
def size(cap_mm): return legends.size(st, cap_mm)

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
 "B1": dict(dot=False, inks_light=DK, inks_dark=LT,   # palette ids chosen by hand: Yuzu has no paler tints than these
    caps={"default": "GR002", "sys": "GR020", "view": "BL034", "marks": "YW019", "nav": "PK014", "bypass": "PK014",
          "kf": "PK014", "layer": "GN025", "shape": "PL018", "dbs": "GN004", "edit": "BN020", "blank": "GR002",
          "mod": "GR020", "undo": "GR020", "l1key": "RD003", "l2key": "GN023", "num": "GR002", "arrows": "GN004", "misc": "BN002"}),
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
          "mod": "#b8b3ab", "undo": "#b8b3ab", "l1key": "RD003", "l2key": "GN023", "num": "#d9d5ce", "arrows": "GN005", "misc": "BN039"}),
}
for _t in list(SCHEMES):
    _v = dict(SCHEMES[_t]); _v["icons"] = True; SCHEMES[_t + "i"] = _v
def is_dark(h):
    r, g, b = _rgb(PAL.get(h, h)); return 0.299 * r + 0.587 * g + 0.114 * b < 128
ICONS = json.load(open(f"{ROOT}/icons/icons.json"))
# Layer-0 icon per key (icon-variant sets only).  Icons live in icons/*.svg, flattened by scripts/icons.py.
ICON_MAP = {"3A": "MarkerLeft", "4A": "Marker", "5A": "MarkerRight", "3B": "ShotLeft", "5B": "ShotRight", "4B": "NoSymbol",
            "3C": "PlayLeft", "4C": "StopSquare", "5C": "PlayRight", "3D": "CarrotLeft", "4D": "Key", "5D": "CarrotRight",
            "7A": "Trash", "R2A": "AudioMute", "R2C": "ArrowUp", "R2D": "ArrowDown", "R1D": "ArrowLeft", "R3D": "ArrowRight"}
# Slot icons: one height for all, at the top of the stack in place of the Layer-0 word (3.5 mm from top_y down,
# leaving ~0.9 mm clear above the Layer-1 text). 4.4 mm was clipped at the cap-top edge.
ICON_H, ICON_W_MAX = 3.5, 10.2
ICON_Y = round(st["top_y"] + ICON_H / 2, 2)
# Arrow keys: big centred glyph like the numpad; the four arrows are one shape rotated, so one long axis for all.
ARROWS = {"R2C": "ArrowUp", "R2D": "ArrowDown", "R1D": "ArrowLeft", "R3D": "ArrowRight"}
ARROW_LONG_MM = 9.0
ARROW_Y = {"R1D": 4.76}   # R1D is 1.5u tall: drop its arrow 0.25u so it lines up with R3D's
def icon_layer(name, color, height_mm, y):
    # Yuzu's vectScale 100 maps the viewBox HEIGHT to 1u (19.05 mm) — measured in the Playground SVG (getBBox):
    # ArrowUp 8.6x17.1 @23.1 -> 2.2x4.4 mm, ArrowLeft 17.1x8.6 @45.93 -> 17.4x8.75 mm. Square icons can't tell.
    ic = ICONS[name]; w_mm = height_mm * ic["w"] / ic["h"]
    if w_mm > ICON_W_MAX: w_mm = ICON_W_MAX; height_mm = w_mm * ic["h"] / ic["w"]
    return dict(colorId=color, vectDef=ic["d"], vectViewbox=ic["viewBox"], vectScale=round(100 * height_mm / 19.05, 2), x=0, y=y)
DOT = dict(vectDef="M12 2a10 10 0 1 0 0 20a10 10 0 1 0 0-20z", vectViewbox="0 0 24 24", vectScale=44, x=0, y=0)  # ≈7 mm

def build(tag):
    sc = SCHEMES[tag]; REPORT.clear()
    tpl = json.load(open(f"{ROOT}/yuzu/template.json")); keys = {}
    for name, e in K.items():
        zone = ZONE.get(name, "default"); cap_hex = sc["caps"].get("l1key" if (zone == "mod" and sc["dot"]) else zone, sc["caps"]["default"])
        cap = nearest(cap_hex)
        inks = [nearest(h) for h in (sc["inks_dark"] if is_dark(cap_hex) else sc["inks_light"])]
        layers = []
        if sc["dot"] and zone in ("l1key", "l2key"):
            dc = sc.get("dot_colors", ("RD003", "GN010"))
            layers.append(dict(colorId=dc[0] if zone == "l1key" else dc[1], **DOT))
        elif zone in ("l1key", "l2key"):
            inks = [nearest(h) for h in LT]
            layers, _ = text_layers(st, e, inks, st["font_label"])
        elif zone == "mod":
            t = e["layers"].get(0, {}).get("cap", "")
            cap_mm = min(st["big_cap_max_mm"], (TOP_W["1u"] - 1.2) / max(width_per_cap_mm(x) for x in ("ALT", "SHIFT", "CTRL")))
            layers.append(dict(colorId=inks[0], textLabel=t, textFontId=st["font_label"], textSize=size(cap_mm), x=0, y=0))
        elif name in st["big_keys"] and not (sc.get("icons") and name in ICON_MAP):
            t = e["layers"].get(0, {}).get("cap", "")
            if t:
                cap_mm = min(st["big_cap_max_mm"], (TOP_W[e["size"]] - 1.2) / width_per_cap_mm(t))
                if t.isalpha() and len(t) > 1:  # word legends (NUM, ENTER) share one size: the one that fits NUM on a 1u key
                    cap_mm = min(st["big_cap_max_mm"], (TOP_W["1u"] - 1.2) / width_per_cap_mm("NUM"))
                layers.append(dict(colorId=inks[0], textLabel=t, textFontId=st["font_big"], textSize=size(cap_mm), x=0, y=0))
        elif sc.get("icons") and name in ARROWS:
            ic = ICONS[ARROWS[name]]; h_mm = ARROW_LONG_MM * ic["h"] / max(ic["w"], ic["h"])
            layers.append(icon_layer(ARROWS[name], inks[0], h_mm, ARROW_Y.get(name, 0)))
        elif sc.get("icons") and name in ICON_MAP:
            layers.append(icon_layer(ICON_MAP[name], inks[0], ICON_H, ICON_Y))
            txt, _ = text_layers(st, e, inks, st["font_label"])
            layers += [l for l in txt if l["y"] != round(SLOT[0], 2)]   # icon replaces the Layer-0 word
            c = corner_layer(st, e, inks[3], st["font_label"])
            if c: layers.append(c)
        else:
            layers, _ = text_layers(st, e, inks, st["font_label"])
            c = corner_layer(st, e, inks[3], st["font_label"])
            if c: layers.append(c)
        keys[e["yuzu"]] = {"colorId": cap, "layers": layers}
    out = dict(tpl); out["name"] = f"Audition {tag[:-1]} icons" if tag.endswith("i") else f"Audition {tag}"; out["author"] = "Nat"; out["keys"] = keys; out["keyTemplates"] = {}; out["designUrl"] = None
    os.makedirs(f"{ROOT}/yuzu/variants", exist_ok=True)
    json.dump(out, open(f"{ROOT}/yuzu/variants/{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{tag}: yuzu/variants/{tag}.json  colour mapping:"); [print(f"   {h} -> {v}") for h, v in REPORT.items()]

for tag in sys.argv[1:] or SCHEMES: build(tag)
