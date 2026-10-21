"""Shared legend geometry for the Yuzu renderers (render_yuzu.py = production set, yuzu_variant.py = auditions).
Three fixed text slots per key (Layer 0 big, Layer 1/2 smaller) at the same heights on every key.
Layer 3 is a corner letter: a one-letter cap in master.yaml is printed small and blue in the bottom-right corner;
an empty Layer-3 cap means unlabelled."""
from fontTools.ttLib import TTFont
from PIL import ImageFont, Image, ImageDraw
from common import ROOT

FONT = f"{ROOT}/fonts/HelvNowCn575BL.ttf"
_tt = TTFont(FONT); CAPR = _tt["OS/2"].sCapHeight / _tt["head"].unitsPerEm
_F = ImageFont.truetype(FONT, 400); _d = ImageDraw.Draw(Image.new("L", (4, 4)))
def width_per_cap_mm(t): return _d.textlength(t, font=_F, features=["kern"]) / (400 * CAPR)
TOP_W = {"1u": 11.45, "1uh": 11.55, "1.5u": 20.98, "1.5uv": 11.25, "2uv": 11.25}   # printable cap-top widths (mm)
TOP_H = 11.45
MARGIN = 0.9   # unusable width at the edges

def slots(st):
    H0, HV = st["cap_mm_l0"], st["cap_mm_var"]
    c0 = st["top_y"] + H0 / 2
    c1 = st["top_y"] + H0 + st["gap_after_l0"] + HV / 2
    c2 = c1 + HV + st["gap_var"]
    return [c0, c1, c2]

def size(st, cap_mm): return round(cap_mm / st["cap_ratio"], 2)

def fit(st, line, cap_mm, key_size):
    """Shrink a label's cap height so it fits the printable width. Returns (cap_mm, shrunk?)."""
    need = width_per_cap_mm(line) * cap_mm; room = TOP_W[key_size] - MARGIN
    return (room / width_per_cap_mm(line), True) if need > room else (cap_mm, False)

def text_layers(st, e, inks, font_id):
    """Layers 0-2 as Yuzu KeyLayer dicts (+ warnings), for a key entry `e` of master.yaml."""
    SL = slots(st); out = []; warn = []
    for layer, lay in sorted(e["layers"].items()):
        t = lay.get("cap", "")
        if layer == 3 or not t: continue
        for n, line in enumerate(t.split("\n")):
            cap_mm, shrunk = fit(st, line, st["cap_mm_l0"] if layer == 0 else st["cap_mm_var"], e["size"])
            if shrunk: warn.append(f"L{layer} '{line}' shrunk to {cap_mm:.2f} mm")
            out.append(dict(colorId=inks[layer], textLabel=line, textFontId=font_id, textSize=size(st, cap_mm), x=0, y=round(SL[layer + n], 2)))
    return out, warn

def corner_layer(st, e, ink, font_id):
    """The Layer-3 corner letter (always bottom-right), or None."""
    t = e["layers"].get(3, {}).get("cap", "")
    if not t: return None
    if len(t) > 1: raise ValueError(f"Layer-3 cap must be one letter or empty, got {t!r}")
    cm, inset = st["l3_corner_mm"], st["l3_corner_inset"]
    w = width_per_cap_mm(t) * cm; half_w = TOP_W[e["size"]] / 2
    y = TOP_H / 2 - inset - cm / 2
    return dict(colorId=ink, textLabel=t, textFontId=font_id, textSize=size(st, cm), x=round(half_w - inset - w / 2, 2), y=round(y, 2))
