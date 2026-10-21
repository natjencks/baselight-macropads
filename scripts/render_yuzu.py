#!/usr/bin/env python3
"""master.yaml -> yuzu/set.json (full Playground import file) and yuzu/keys.json (keys map only).
Layout rules (scripts/legends.py): three fixed slots per key (L0 big, L1/L2 smaller), Layer-3 jumps as a small blue
corner letter; 'big_keys' get one centred legend."""
import json, os, sys
from common import load_master, ROOT
from legends import width_per_cap_mm, TOP_W, slots, text_layers, corner_layer, ARROWS, arrow_layer
import legends

m = load_master(); st = m["style"]
SLOT = slots(st)
INK = {int(k): v for k, v in st["ink"].items()}
def size(cap_mm): return legends.size(st, cap_mm)

tpl = json.load(open(f"{ROOT}/yuzu/template.json"))
keys = {}; warnings = []
for name, e in m["keys"].items():
    kid = e["yuzu"]; layers = []
    if name in ARROWS:
        layers.append(arrow_layer(name, INK[0]))
    elif name in st["big_keys"]:
        t = e["layers"].get(0, {}).get("cap", "")
        if t:
            cap_mm = min(st["big_cap_max_mm"], (TOP_W[e["size"]] - 1.2) / width_per_cap_mm(t))
            font = st["font_big"]   # Light: digits and symbols match the arrow icons' stroke
            if t.isalpha() and len(t) > 1:  # word legends (NUM, ENTER): label font (SemiBold) and one shared size
                cap_mm = min(st["big_cap_max_mm"], (TOP_W["1u"] - 1.2) / width_per_cap_mm("NUM")); font = st["font_label"]
            layers.append({"colorId": INK[0], "textLabel": t, "textFontId": font,
                           "textSize": size(cap_mm), "x": 0, "y": 0})
    else:
        layers, warn = text_layers(st, e, INK, st["font_label"])
        warnings += [f"{name} {w}" for w in warn]
        c = corner_layer(st, e, INK[3], st["font_label"])
        if c: layers.append(c)
    keys[kid] = {"colorId": st["cap_color"], "layers": layers}

out = dict(tpl); out["name"] = m["layout"]["yuzu_name"]; out["author"] = "Nat"
out["keys"] = keys; out["keyTemplates"] = {}; out["designUrl"] = None
os.makedirs(f"{ROOT}/yuzu", exist_ok=True)
json.dump(out, open(f"{ROOT}/yuzu/set.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(keys, open(f"{ROOT}/yuzu/keys.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"yuzu/set.json written ({len(keys)} keys). slots {[round(v,2) for v in SLOT]}")
for w in warnings: print("WARNING:", w)

