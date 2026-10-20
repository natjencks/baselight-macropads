#!/usr/bin/env python3
"""One-off: build master.yaml from an Oryx snapshot + the v3 cap-label set + function descriptions.
After this, master.yaml is the source of truth and this script is only history."""
import json, sys, yaml
from common import NAMES, YUZU_ID, action_to_str, ROOT

snap = json.load(open(f"{ROOT}/oryx/snapshot_B4K0zD.json", encoding="utf-8"))
L = snap["layers"]

# Cap labels (ALL CAPS, v3). layer -> idx -> text.  '\n' = second line (drops to next slot).
CAP = {}
def k(i, *labs):
    for layer, t in enumerate(labs):
        if t: CAP[(layer, i)] = t
k(0,"ESC","QUIT"); k(1,"ZOOM","TMLN H","TMLN V","TMLN HV"); k(2,"‹MARK","C NOTE"); k(3,"MARK","DELETE","DEL ALL")
k(4,"MARK›","O NOTE"); k(5,"GRAB","GROUP"); k(7,"SELECT","+STRIPS","−STRIPS"); k(8,"1×1","","2×1","BASE")
k(9,"‹SHOT","START","‹SCENE","FACE"); k(10,"BYP","ALL","OPER","WIDE"); k(11,"SHOT›","END","SCENE›","VIGN")
k(12,"SHAPE","EDIT","RESET","CONTR"); k(13,"DBS\nVIEW"); k(14,"LAYER↑","TOP"); k(15,"VS DBS","WIPE","VS BYP")
k(16,"REW"); k(17,"STOP","SCENE","SHOT","RESET"); k(18,"FWD"); k(19,"MATTE","SHAPE›","DISP"); k(20,"LAYER↓","BOTTOM")
k(21,"CUR 1","TOGGLE","GANG"); k(22,"‹KEY","MOVE","EDIT"); k(23,"KEY ±"); k(24,"KEY›","MOVE","EDIT"); k(25,"BLUR","RESET")
k(26,"DBS\nAPPLY"); k(27,"+LYR","−LYR"); k(28,"CUR 2","TOGGLE","VS REF"); k(29,"COPY","SMART","PARAMS"); k(30,"NAME","","MULTI")
k(31,"PASTE","SMART","STRIPS"); k(32,"UNDO","REDO"); k(33,"ALT"); k(34,"SHIFT"); k(35,"L1","","L3"); k(36,"L2","L3"); k(37,"CTRL")
k(38,"PREFS","SETUPS","FORMAT","SCENE"); k(39,"MUTE"); k(40,"ALIGN","VERT"); k(41,"NUM"); k(42,"/"); k(43,"*"); k(44,"−")
k(45,"JOBS"); k(46,"CSJ"); k(47,"FOLD","ALL"); k(48,"7"); k(49,"8"); k(50,"9"); k(51,"+"); k(52,"↑"); k(53,"COUNT","FPS")
k(54,"4"); k(55,"5"); k(56,"6"); k(57,"ENTER"); k(58,"←"); k(59,"↓"); k(60,"→"); k(61,"1"); k(62,"2"); k(63,"3")
k(64,"ENTER","CLOSE"); k(65,"GROUP"); k(66,"CYCLE"); k(67,"0"); k(68,"."); k(69,"WIN","CLOSE")
k(70,"ALT"); k(71,"UNDO","REDO"); k(72,"SHIFT"); k(73,"CTRL"); k(74,"L2","L3"); k(75,"L1","","L3")

# Function descriptions (what the keystroke does in Baselight). layer -> idx -> text
FN = {}
def f(i, *descs):
    for layer, t in enumerate(descs):
        if t: FN[(layer, i)] = t
f(0,"Escape","Quit Baselight"); f(1,"Display zoom","Timeline horizontal zoom","Timeline vertical zoom","Timeline H+V zoom")
f(2,"Previous mark","Colour note (Win+Alt+Shift+C, Tab)"); f(3,"Add mark","Delete marks under cursor","Delete all marks")
f(4,"Next mark","Conform note (Win+Alt+Shift+O, Tab)"); f(5,"Grab to gallery","Group grading")
f(7,"Select / deselect all shots","Select all strips","Deselect all strips"); f(8,"1x1 view","","2x1 cursors","Jump to BASE GRADE layer (FLAPI F13)")
f(9,"Previous shot","Shot start","Scene head","Jump to FACE1 layer (FLAPI F14)")
f(10,"Bypass strip","Bypass all","Bypass operator","Jump to WIDE1 layer (FLAPI F15)")
f(11,"Next shot","Shot end","Scene tail","Jump to VIGNETTE layer (FLAPI F16)")
f(12,"Add shape","Create/edit shapes","Reset shape","Jump to CONTRAST layer (FLAPI F17)")
f(13,"DBS view"); f(14,"Layer up","Top of stack"); f(15,"2x1 vs DBS","Wipe vs DBS","Cursor vs bypassed")
f(16,"Rewind (J)"); f(17,"Stop (K)","Play scene","Play shot","Reset all parameters"); f(18,"Forward (L)")
f(19,"Toggle grade / matte","Next shape","Matte display"); f(20,"Layer down","Bottom of stack")
f(21,"Cursor 1","Toggle cursor 1","Gang cursors"); f(22,"Previous keyframe","Move keyframe left","Edit keyframe left")
f(23,"Toggle keyframe"); f(24,"Next keyframe","Move keyframe right","Edit keyframe right"); f(25,"Blur (matte)","Reset blur")
f(26,"DBS apply"); f(27,"Insert layer","Delete layer"); f(28,"Cursor 2","Toggle cursor 2","Cursor vs reference")
f(29,"Copy","Smart copy","Copy parameters"); f(30,"Rename strip","","Multi-paste"); f(31,"Paste","Smart paste","Paste strips")
f(32,"Undo","Redo"); f(33,"Alt (hold)"); f(34,"Shift (hold)"); f(35,"Layer 1 while held","","Layer 3 one-shot (with T4 held)")
f(36,"Layer 2 while held","Layer 3 one-shot (with T3 held)"); f(37,"Ctrl (hold)")
f(38,"Preferences","Setups","Formats","Scene settings"); f(39,"Mute audio"); f(40,"Timeline alignment panel","Align timeline vertically")
f(41,"Num lock"); f(42,"Keypad /"); f(43,"Keypad *"); f(44,"Keypad -"); f(45,"Jobs"); f(46,"CSJ"); f(47,"Fold layer","Fold all")
for i, d in zip(range(48,52), ["Keypad 7","Keypad 8","Keypad 9","Keypad +"]): f(i, d)
f(52,"Up arrow"); f(53,"Counters","Show FPS")
for i, d in zip(range(54,58), ["Keypad 4","Keypad 5","Keypad 6","Keypad Enter"]): f(i, d)
f(58,"Left arrow"); f(59,"Down arrow"); f(60,"Right arrow")
for i, d in zip(range(61,64), ["Keypad 1","Keypad 2","Keypad 3"]): f(i, d)
f(64,"Keypad Enter","Close comment (V15 macro: Tab, Tab, Enter)"); f(65,"Groups"); f(66,"Cycle numpad mode"); f(67,"Keypad 0"); f(68,"Keypad .")
f(69,"Win","Close comment (V15 macro: Tab, Tab, Enter)"); f(70,"Alt (hold)"); f(71,"Undo","Redo"); f(72,"Shift (hold)"); f(73,"Ctrl (hold)")
f(74,"Layer 2 while held","Layer 3 one-shot (with RT3 held)"); f(75,"Layer 1 while held","","Layer 3 one-shot (with RT4 held)")

tpl = json.load(open(f"{ROOT}/yuzu/template.json"))
size_of = {kk["id"]: kk["sizeId"] for kk in tpl["layoutKeys"]}

keys = {}
for idx in range(76):
    name = NAMES[idx]
    entry = {"oryx": idx, "yuzu": YUZU_ID[idx], "size": size_of[YUZU_ID[idx]], "layers": {}}
    for layer in range(4):
        kd = L[layer]["keys"][idx]
        tap = kd.get("tap"); hold = kd.get("hold")
        if tap and tap.get("code") == "KC_TRANSPARENT" and not tap.get("macro"): tap = None
        lay = {}
        if (layer, idx) in FN: lay["fn"] = FN[(layer, idx)]
        if tap: lay["key"] = action_to_str(tap)
        if hold: lay["hold"] = action_to_str(hold)
        if kd.get("label"): lay["oryx"] = kd["label"]
        if (layer, idx) in CAP: lay["cap"] = CAP[(layer, idx)]
        if lay: entry["layers"][layer] = lay
    keys[name] = entry

master = {
    "layout": {
        "name": "Ergodox Baselight V16",
        "oryx_hash": "Y6DDQ", "oryx_geometry": "ergodox-ez-st", "oryx_revision": snap["rev"],
        "yuzu_name": "Baselight V16 v3 (caps, slots)",
    },
    "style": {
        "profile": "kam", "cap_color": "GR002",
        "ink": {"0": "GR001", "1": "RD003", "2": "GN010", "3": "BL023"},
        "font_label": 26345, "font_big": 11838,
        "cap_mm_l0": 2.65, "cap_mm_var": 1.80, "top_y": -5.2, "gap_after_l0": 1.05, "gap_var": 0.65,
        "cap_ratio": 0.712, "big_cap_max_mm": 6.5,
        "big_keys": ["R4A","R5A","R6A","R7A","R4B","R5B","R6B","R7B","R2C","R4C","R5C","R6C","R7C",
                     "R1D","R2D","R3D","R4D","R5D","R6D","R5E","R6E"],
    },
    "keys": keys,
}

class D(yaml.SafeDumper):
    pass
def _str(dumper, s):
    if "\n" in s: return dumper.represent_scalar("tag:yaml.org,2002:str", s, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", s)
D.add_representer(str, _str)
with open(f"{ROOT}/master.yaml", "w", encoding="utf-8") as out:
    out.write("# Master source of truth for the Baselight ErgoDox macropads.\n"
              "# Edit THIS file, then run scripts/sync.py (see README). Key names: 1A..7E / R1A..R7E / T1..T6 / RT1..RT6.\n"
              "# layers.N: fn = what it does; key = keystroke sent (or macro:); hold = hold action; oryx = Oryx label (<=10 chars);\n"
              "#           cap = keycap legend (L0 <= ~5 chars on 1u keys, variants <= 7). Omit a layer to leave it transparent.\n")
    yaml.dump(master, out, Dumper=D, allow_unicode=True, sort_keys=False, width=120)
print("wrote master.yaml with", len(keys), "keys")
