#!/usr/bin/env python3
"""master.yaml -> diagram.html (standalone) and diagram_widget.html (fragment for Claude's chat widget).
Each band shows the keycap legend; hovering shows the function and the keystroke sent."""
import html
from common import load_master, ROOT

m = load_master(); K = m["keys"]

def band(name, layer, cls):
    lay = K[name]["layers"].get(layer)
    if not lay: return f'<div class="{cls}"></div>'
    cap = html.escape(lay.get("diagram") or lay.get("cap", "").replace("\n", " ")) or "·"   # 'diagram:' names an icon legend
    if layer == 3:   # Layer 3 is not printed on the caps (except the corner letter): show the Oryx name, greyed = not on the keycap
        corner = lay.get("cap", "")
        cap = (f'<b>{html.escape(corner)}</b> ' if corner else "") + f'<i>{html.escape(lay.get("oryx") or lay.get("fn", ""))}</i>'
    ks = lay.get("key") or lay.get("hold") or ""
    tip = html.escape(lay.get("fn", "") + (f"  ·  {ks}" if ks else ""))
    return f'<div class="{cls}"><span class="b" data-tip="{tip}">{cap}</span></div>'

def key(name, extra="", style=""):
    st = f' style="{style}"' if style else ""
    return (f'<div class="k {extra}"{st}><div class="id"><span>{name}</span><span>{K[name]["size"]}</span></div>'
            + band(name, 0, "l0") + band(name, 1, "l1") + band(name, 2, "l2") + band(name, 3, "l3") + "</div>")

PRIME = {"3A","4A","5A","3B","4B","5B","3C","4C","5C","3D","4D","5D"}
TALL = {"7B","7D","R1B","R1D"}
rows_left = [["1A","2A","3A","4A","5A","6A","7A"],["1B","2B","3B","4B","5B","6B","7B"],["1C","2C","3C","4C","5C","6C"],
             ["1D","2D","3D","4D","5D","6D","7D"],["1E","2E","3E","4E","5E",None]]
rows_right = [["R1A","R2A","R3A","R4A","R5A","R6A","R7A"],["R1B","R2B","R3B","R4B","R5B","R6B","R7B"],["R2C","R3C","R4C","R5C","R6C","R7C"],
              ["R1D","R2D","R3D","R4D","R5D","R6D","R7D"],[None,"R3E","R4E","R5E","R6E","R7E"]]
def grid(rows, cls=""):
    out = []
    for r in rows:
        for n in r:
            out.append("<div></div>" if n is None else key(n, ("tall " if n in TALL else "") + ("prime" if n in PRIME else "")))
    return f'<div class="kb {cls}">' + "".join(out) + "</div>"
LEFT_T = {"T1":"grid-column:2;grid-row:1","T2":"grid-column:3;grid-row:1","T3":"grid-column:1;grid-row:2/4","T4":"grid-column:2;grid-row:2/4","T5":"grid-column:3;grid-row:2","T6":"grid-column:3;grid-row:3"}
RIGHT_T = {"RT2":"grid-column:1;grid-row:1","RT1":"grid-column:2;grid-row:1","RT3":"grid-column:3;grid-row:2/4","RT4":"grid-column:2;grid-row:2/4","RT5":"grid-column:1;grid-row:2","RT6":"grid-column:1;grid-row:3"}
def thumbs(st, cls): return f'<div class="cl {cls}">' + "".join(key(n, "", s) for n, s in st.items()) + "</div>"

# CSS uses the chat widget's theme variables; the standalone file gets fallbacks.
CSS = """
.wrap{font-size:12px;color:var(--text-primary,#222)}
.kb{display:grid;grid-template-columns:repeat(7,1fr);grid-auto-rows:106px;grid-auto-flow:dense;gap:6px;margin:6px 0 0}
.kb.right .k.tall{grid-column:1}
.k{border-radius:8px;border:0.5px solid var(--border,#cfcac3);background:var(--bg-secondary,#fff);display:flex;flex-direction:column;position:relative}
.k.tall{grid-row:span 2}
.k .id{font-size:10px;color:var(--text-muted,#888);padding:3px 6px 0;display:flex;justify-content:space-between}
.k .l0{flex:1;padding:2px 6px 3px;font-size:13px;font-weight:600;display:flex;align-items:center}
.k .l1,.k .l2,.k .l3{font-size:11px;font-weight:500;padding:3px 6px;border-top:0.5px solid var(--border,#e5e2dc);min-height:19px}
.k .l1{background:#FAECE7;color:#712B13}.k .l2{background:#E1F5EE;color:#085041}.k .l3{background:#E6F1FB;color:#0C447C}
[data-mode="dark"] .k .l1{background:#4a1f10;color:#F5C4B3}[data-mode="dark"] .k .l2{background:#0a3a2e;color:#9FE1CB}[data-mode="dark"] .k .l3{background:#0c2f4f;color:#B5D4F4}
.k .l1:empty,.k .l2:empty,.k .l3:empty{opacity:.35}
.k .l3{border-radius:0 0 8px 8px}.k .l3 i{font-style:normal;opacity:.6}.k .l3 b{font-weight:700}
.prime{outline:2px solid #534AB7;outline-offset:-2px}.prime .id{color:#534AB7}
[data-mode="dark"] .prime{outline-color:#AFA9EC}
.b{position:relative;cursor:default}
.b:hover::after{content:attr(data-tip);position:absolute;left:0;top:calc(100% + 4px);z-index:50;white-space:normal;width:max-content;max-width:240px;
  font-size:11px;font-weight:400;line-height:1.35;color:#fff;background:#1f1f24;padding:6px 8px;border-radius:6px;box-shadow:0 4px 14px rgba(0,0,0,.25)}
.k:hover{z-index:40}
.stage{position:relative;height:300px;margin-top:-6px}
.cl{position:absolute;top:6px;display:grid;grid-template-columns:78px 78px 78px;grid-template-rows:78px 78px 78px;gap:6px;transform-origin:top left}
.cl.left{left:56%;transform:rotate(25deg)}.cl.right{right:56%;transform:rotate(-25deg);transform-origin:top right}
.cl .k .l0{font-size:12px}.cl .k .l1,.cl .k .l2,.cl .k .l3{font-size:10px;min-height:16px;padding:2px 5px}
.chord{position:absolute;left:0;top:30px;width:300px;font-size:12px;line-height:1.5;border:0.5px solid var(--border,#cfcac3);border-radius:8px;padding:8px 10px}
.rnote{position:absolute;right:0;top:30px;width:300px;font-size:12px;line-height:1.5;border:0.5px solid var(--border,#cfcac3);border-radius:8px;padding:8px 10px}
.lab{font-size:14px;font-weight:500;margin:6px 0 2px}.sub{font-size:12px;color:var(--text-secondary,#666);margin-bottom:4px}
.leg{display:flex;flex-wrap:wrap;gap:12px;font-size:11.5px;color:var(--text-secondary,#666);margin-top:6px;align-items:center}
.leg i{display:inline-block;width:14px;height:12px;border-radius:3px;border:0.5px solid var(--border,#ccc);vertical-align:-2px;margin-right:4px}
"""
rev = m["layout"]["oryx_revision"]; title = html.escape(m["layout"]["name"])
body = f"""<div class="wrap">
<div class="lab">{title} — Oryx revision {rev} — left half</div>
<div class="sub">Keycap legends; hover a legend for the function and the keystroke. Top = Layer 0; red = Layer 1 (hold T3); green = Layer 2 (hold T4); blue = Layer 3 (T3+T4 chord, one-shot; greyed names are not printed on the caps, only the bold corner letter is). Purple outline = prime block.</div>
{grid(rows_left)}
<div class="stage"><div class="chord"><b>Layer 3 chord</b><br>Hold T3, tap T4 (or hold T4, tap T3) → next key from Layer 3. Hold both to keep it active. Same on the right cluster.</div>{thumbs(LEFT_T, "left")}</div>
<div class="lab">Right half</div>
{grid(rows_right, "right")}
<div class="stage">{thumbs(RIGHT_T, "right")}<div class="rnote"><b>Right thumb cluster</b><br>Mirror of the left: same keys, same layers.</div></div>
<div class="leg"><span><i style="background:var(--bg-secondary,#fff)"></i>Layer 0</span><span><i style="background:#FAECE7"></i>Layer 1 — hold T3</span><span><i style="background:#E1F5EE"></i>Layer 2 — hold T4</span><span><i style="background:#E6F1FB"></i>Layer 3 — T3+T4 chord</span><span><i style="outline:2px solid #534AB7;outline-offset:-2px"></i>Prime block</span></div>
</div>"""
open(f"{ROOT}/diagram.html", "w", encoding="utf-8").write(
    f'<!doctype html><meta charset="utf-8"><title>{title} — {rev}</title><style>body{{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;background:#f6f5f2;margin:16px;max-width:1150px}}{CSS}</style>{body}')
open(f"{ROOT}/diagram_widget.html", "w", encoding="utf-8").write(f"<style>{CSS}</style>{body}")
print("diagram.html + diagram_widget.html written")
