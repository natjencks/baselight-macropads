#!/usr/bin/env python3
"""Flatten Nat's icon SVGs (icons/*.svg, Illustrator exports) into single-path legends for Yuzu:
   icons/icons.json = {name: {"d": <path data>, "viewBox": "x y w h", "w": mm_w, "h": mm_h}}
Yuzu KeyLayer vector legends take one path (vectDef) + a viewBox (vectViewbox); vectScale 100 maps the viewBox
WIDTH to 1u = 19.05 mm, so vectScale = 100 * wanted_mm / (vbw_units * 19.05 / vbw_units) -> 100 * wanted_mm / 19.05.
Shapes with fill:none are dropped (they were Illustrator cut-out helpers); polygon/rect/ellipse/line become path data."""
import re, json, glob, os, math
from common import ROOT

def num(s): return float(s)
def rect_d(a):
    x, y, w, h = (num(a.get(k, "0")) for k in ("x", "y", "width", "height"))
    return f"M{x} {y}h{w}v{h}h{-w}Z"
def polygon_d(a):
    pts = [num(v) for v in re.split(r"[\s,]+", a["points"].strip()) if v]
    xy = list(zip(pts[0::2], pts[1::2]))
    return "M" + " L".join(f"{x} {y}" for x, y in xy) + "Z"
def ellipse_d(a):
    cx, cy, rx, ry = (num(a.get(k, "0")) for k in ("cx", "cy", "rx", "ry"))
    return f"M{cx-rx} {cy}a{rx} {ry} 0 1 0 {2*rx} 0a{rx} {ry} 0 1 0 {-2*rx} 0Z"

def flatten(svg_text):
    vb = re.search(r'viewBox="([^"]+)"', svg_text).group(1)
    styles = dict(re.findall(r"\.(st\d+)\s*\{\s*fill:\s*([^;]+);", svg_text))
    parts = []
    for m in re.finditer(r"<(path|polygon|rect|ellipse|line)\b([^>]*?)/?>", svg_text, re.S):
        tag, attrs = m.group(1), m.group(2)
        a = dict(re.findall(r'([\w:-]+)="([^"]*)"', attrs))
        fill = a.get("fill"); st = re.search(r"fill:\s*([^;\"]+)", a.get("style", ""))
        if st: fill = st.group(1).strip()
        if fill is None and a.get("class") in styles: fill = styles[a["class"]].strip()
        if fill == "none" or tag == "line": continue
        if tag == "path": parts.append(re.sub(r"\s+", " ", a["d"]).strip())
        elif tag == "polygon": parts.append(polygon_d(a))
        elif tag == "rect": parts.append(rect_d(a))
        elif tag == "ellipse": parts.append(ellipse_d(a))
    x, y, w, h = (float(v) for v in vb.split())
    return {"d": " ".join(parts), "viewBox": vb, "w": w, "h": h}

if __name__ == "__main__":
    out = {}
    for f in sorted(glob.glob(f"{ROOT}/icons/*.svg")):
        name = os.path.splitext(os.path.basename(f))[0]
        out[name] = flatten(open(f, encoding="utf-8").read())
        print(f"{name:18s} viewBox {out[name]['viewBox']:>22s}  {len(out[name]['d'])} chars")
    json.dump(out, open(f"{ROOT}/icons/icons.json", "w"), indent=1)
