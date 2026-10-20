#!/usr/bin/env python3
"""Compare master.yaml against an Oryx snapshot (oryx/snapshot_<rev>.json, as pulled by scripts/oryx_pull.js)
and print the edits Oryx needs: per layer/key, the tap/hold action and the label.
Exit 0 when in sync.  Usage: oryx_diff.py [snapshot.json]  (default: latest snapshot named in master.yaml)"""
import json, sys
from common import load_master, str_to_action, action_to_str, NAMES, ROOT

m = load_master()
path = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/oryx/snapshot_{m['layout']['oryx_revision']}.json"
snap = json.load(open(path, encoding="utf-8"))

def norm(a):
    if not a: return None
    if a.get("code") == "KC_TRANSPARENT" and not a.get("macro"): return None
    a = dict(a)
    if "mods" in a: a["mods"] = sorted(a["mods"])
    if "macro" in a: a["macro"] = json.dumps(a["macro"], sort_keys=True)
    return a

edits = []
for name, e in m["keys"].items():
    idx = e["oryx"]
    for layer in range(4):
        want = e["layers"].get(layer, {})
        have = snap["layers"][layer]["keys"][idx]
        w_tap, w_hold = norm(str_to_action(want.get("key"))), norm(str_to_action(want.get("hold")))
        h_tap, h_hold = norm(have.get("tap")), norm(have.get("hold"))
        w_lab, h_lab = want.get("oryx", "") or "", have.get("label", "") or ""
        if (w_tap, w_hold, w_lab) != (h_tap, h_hold, h_lab):
            edits.append({"layer": layer, "idx": idx, "key": name,
                          "tap": want.get("key", ""), "hold": want.get("hold", ""), "label": w_lab,
                          "was": {"tap": action_to_str(have.get("tap")), "hold": action_to_str(have.get("hold")), "label": h_lab}})
if not edits:
    print(f"Oryx snapshot {snap['rev']} matches master.yaml — nothing to do."); sys.exit(0)
print(f"{len(edits)} edit(s) needed in Oryx (snapshot {snap['rev']}):")
for ed in edits:
    print(f"  L{ed['layer']} {ed['key']:>4} (#{ed['idx']:>2}): tap={ed['tap']!r} hold={ed['hold']!r} label={ed['label']!r}   <- was {ed['was']}")
json.dump(edits, open(f"{ROOT}/oryx/pending_edits.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("written oryx/pending_edits.json (consumed by the Oryx browser helper)")
sys.exit(2)
