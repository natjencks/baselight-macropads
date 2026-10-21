#!/usr/bin/env python3
"""master.yaml -> yuzu/set.json (full Playground import file) and yuzu/keys.json (keys map only).
Layout rules: four fixed slots per key (L0 big, L1-L3 variants); 'big_keys' get one centred legend."""
import json, os, sys
from fontTools.ttLib import TTFont
from PIL import ImageFont, Image, ImageDraw
from common import load_master, ROOT

m = load_master(); st = m["style"]
FONT = f"{ROOT}/fonts/HelvNowCn575BL.ttf"
tt = TTFont(FONT); CAPR = tt["OS/2"].sCapHeight / tt["head"].unitsPerEm
_F = ImageFont.truetype(FONT, 400); _d = ImageDraw.Draw(Image.new("L", (4, 4)))
def width_per_cap_mm(t): return _d.textlength(t, font=_F, features=["kern"]) / (400 * CAPR)
TOP_W = {"1u": 11.45, "1uh": 11.55, "1.5u": 20.98, "1.5uv": 11.25, "2uv": 11.25}

H0, HV = st["cap_mm_l0"], st["cap_mm_var"]
c0 = st["top_y"] + H0 / 2
c1 = st["top_y"] + H0 + st["gap_after_l0"] + HV / 2
c2 = c1 + HV + st["gap_var"]; c3 = c2 + HV + st["gap_var"]
SLOT = [c0, c1, c2, c3]
INK = {int(k): v for k, v in st["ink"].items()}
def size(cap_mm): return round(cap_mm / st["cap_ratio"], 2)

tpl = json.load(open(f"{ROOT}/yuzu/template.json"))
keys = {}; warnings = []
for name, e in m["keys"].items():
    kid = e["yuzu"]; layers = []
    if name in st["big_keys"]:
        t = e["layers"].get(0, {}).get("cap", "")
        if t:
            cap_mm = min(st["big_cap_max_mm"], (TOP_W[e["size"]] - 1.2) / width_per_cap_mm(t))
            if t.isalpha() and len(t) > 1:  # word legends (NUM, ENTER) share one size: the one that fits NUM on a 1u key
                cap_mm = min(st["big_cap_max_mm"], (TOP_W["1u"] - 1.2) / width_per_cap_mm("NUM"))
            layers.append({"colorId": INK[0], "textLabel": t, "textFontId": st["font_big"],
                           "textSize": size(cap_mm), "x": 0, "y": 0})
    else:
        for layer, lay in sorted(e["layers"].items()):
            t = lay.get("cap", "")
            if not t: continue
            for n, line in enumerate(t.split("\n")):
                cap_mm = H0 if layer == 0 else HV
                need = width_per_cap_mm(line) * cap_mm
                if need > TOP_W[e["size"]] - 0.9:
                    fitted = (TOP_W[e["size"]] - 0.9) / width_per_cap_mm(line)
                    warnings.append(f"{name} L{layer} '{line}' needs {need:.1f} mm, cap allows {TOP_W[e['size']]-0.9:.1f} -> shrunk to {fitted:.2f} mm cap")
                    cap_mm = fitted
                layers.append({"colorId": INK[layer], "textLabel": line, "textFontId": st["font_label"],
                               "textSize": size(cap_mm), "x": 0, "y": round(SLOT[layer + n], 2)})
    keys[kid] = {"colorId": st["cap_color"], "layers": layers}

out = dict(tpl); out["name"] = m["layout"]["yuzu_name"]; out["author"] = "Nat"
out["keys"] = keys; out["keyTemplates"] = {}; out["designUrl"] = None
os.makedirs(f"{ROOT}/yuzu", exist_ok=True)
json.dump(out, open(f"{ROOT}/yuzu/set.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(keys, open(f"{ROOT}/yuzu/keys.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"yuzu/set.json written ({len(keys)} keys). slots {[round(v,2) for v in SLOT]}")
for w in warnings: print("WARNING:", w)
sys.exit(1 if warnings else 0)
