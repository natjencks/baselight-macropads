#!/usr/bin/env python3
"""master.yaml -> diagram.html : colour-coded layout, one band per layer, physical thumb clusters."""
import html
from common import load_master, ROOT

m = load_master(); K = m["keys"]
def band(name, layer, cls):
    lay = K[name]["layers"].get(layer)
    if not lay: return f'<div class="{cls}"></div>'
    fn = html.escape(lay.get("fn", "")); key = html.escape(lay.get("key") or lay.get("hold") or "")
    cap = html.escape(lay.get("cap", "").replace("\n", " "))
    return f'<div class="{cls}"><b>{cap}</b> {fn} <code>{key}</code></div>'
def key(name, extra=""):
    return (f'<div class="k {extra}"><div class="id">{name}<span>{K[name]["size"]}</span></div>'
            + band(name, 0, "l0") + band(name, 1, "l1") + band(name, 2, "l2") + band(name, 3, "l3") + "</div>")

CSS = """
body{font:12px/1.3 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#222;background:#f6f5f2;margin:16px}
h2{font-size:15px;margin:18px 0 6px}
.grid{display:grid;grid-template-columns:repeat(7,150px);grid-auto-flow:dense;gap:6px}
.grid.right .k.tall{grid-column:1}
.k{border:1px solid #cfcac3;border-radius:8px;background:#fff;min-height:120px;display:flex;flex-direction:column;overflow:hidden}
.k.tall{grid-row:span 2;min-height:246px}.k.prime{outline:2px solid #6b5bd2;outline-offset:-2px}
.id{font-size:10px;color:#888;padding:3px 6px 0;display:flex;justify-content:space-between}
.k b{font-weight:600;margin-right:4px}.k code{font-size:10px;color:#666;margin-left:3px}
.l0{flex:1;padding:3px 6px 4px}.l1,.l2,.l3{padding:3px 6px;font-size:11px;min-height:17px;border-top:1px solid #eee}
.l1{background:#fbeae6;color:#7a2b14}.l2{background:#e2f3ec;color:#0b4f3f}.l3{background:#e6f0fb;color:#0d457d}
.thumbs{display:grid;grid-template-columns:repeat(3,120px);grid-template-rows:repeat(3,100px);gap:6px;margin:30px 0 0 180px;transform:rotate(25deg);transform-origin:top left;width:380px}
.thumbs.right{transform:rotate(-25deg);transform-origin:top left;margin-left:40px;margin-top:140px}
.thumbs .k{min-height:0}
.leg{display:flex;gap:14px;font-size:11px;color:#555;margin:8px 0 14px}.leg i{display:inline-block;width:14px;height:11px;border:1px solid #ccc;border-radius:3px;vertical-align:-2px;margin-right:4px}
"""
# None = empty cell; cells covered by a tall key from the row above are simply omitted.
rows_left = [["1A","2A","3A","4A","5A","6A","7A"],["1B","2B","3B","4B","5B","6B","7B"],["1C","2C","3C","4C","5C","6C"],
             ["1D","2D","3D","4D","5D","6D","7D"],["1E","2E","3E","4E","5E",None]]
rows_right = [["R1A","R2A","R3A","R4A","R5A","R6A","R7A"],["R1B","R2B","R3B","R4B","R5B","R6B","R7B"],["R2C","R3C","R4C","R5C","R6C","R7C"],
              ["R1D","R2D","R3D","R4D","R5D","R6D","R7D"],[None,"R3E","R4E","R5E","R6E","R7E"]]
PRIME = {"3A","4A","5A","3B","4B","5B","3C","4C","5C","3D","4D","5D"}
TALL = {"7B","7D","R1B","R1D"}
def grid(rows, cls=""):
    out = []
    for r in rows:
        for n in r:
            if n is None: out.append("<div></div>")
            else: out.append(key(n, ("tall " if n in TALL else "") + ("prime" if n in PRIME else "")))
    return f'<div class="grid {cls}">' + "".join(out) + "</div>"
def thumbs(names, cls):
    # grid cells: T1 T2 top; T3 (big) col1 rows2-3; T4 (big) col2 rows2-3; T5 col3 row2; T6 col3 row3  (mirrored for right)
    L = {n: key(n) for n in names}
    if cls == "left":
        order = [None, "T1", "T2", "T3", "T4", "T5", None, None, "T6"]
        style = {"T3": "grid-column:1;grid-row:2/4", "T4": "grid-column:2;grid-row:2/4", "T5": "grid-column:3;grid-row:2", "T6": "grid-column:3;grid-row:3",
                 "T1": "grid-column:2;grid-row:1", "T2": "grid-column:3;grid-row:1"}
    else:
        style = {"RT3": "grid-column:3;grid-row:2/4", "RT4": "grid-column:2;grid-row:2/4", "RT5": "grid-column:1;grid-row:2", "RT6": "grid-column:1;grid-row:3",
                 "RT1": "grid-column:2;grid-row:1", "RT2": "grid-column:1;grid-row:1"}
    cells = "".join(key(n).replace('class="k ', f'style="{style[n]}" class="k ', 1) for n in style)
    return f'<div class="thumbs {cls}">{cells}</div>'

rev = m["layout"]["oryx_revision"]
page = f"""<!doctype html><meta charset="utf-8"><title>{html.escape(m['layout']['name'])} — {rev}</title><style>{CSS}</style>
<h2>{html.escape(m['layout']['name'])} — Oryx revision {rev} — left half</h2>
<div class="leg"><span><i style="background:#fff"></i>Layer 0</span><span><i style="background:#fbeae6"></i>Layer 1 (hold T3)</span>
<span><i style="background:#e2f3ec"></i>Layer 2 (hold T4)</span><span><i style="background:#e6f0fb"></i>Layer 3 (T3+T4 chord, one-shot)</span>
<span><i style="outline:2px solid #6b5bd2"></i>prime block</span><span>bold = keycap legend</span></div>
{grid(rows_left)}
<div style="height:40px"></div>{thumbs(["T1","T2","T3","T4","T5","T6"], "left")}<div style="height:200px"></div>
<h2>Right half</h2>{grid(rows_right, "right")}
<div style="height:40px"></div>{thumbs(["RT1","RT2","RT3","RT4","RT5","RT6"], "right")}<div style="height:200px"></div>
"""
open(f"{ROOT}/diagram.html", "w", encoding="utf-8").write(page)
print("diagram.html written")
