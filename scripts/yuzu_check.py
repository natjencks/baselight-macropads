#!/usr/bin/env python3
"""Compare a Yuzu Playground export (Settings > Advanced > Export JSON) against the rendered yuzu/set.json.
Usage: yuzu_check.py export.json"""
import json, sys
from common import ROOT

want = json.load(open(f"{ROOT}/yuzu/set.json", encoding="utf-8"))["keys"]
have = json.load(open(sys.argv[1], encoding="utf-8"))["keys"]
FIELDS = ("textLabel", "textFontId", "textSize", "colorId", "y")
diffs = 0
for kid, w in want.items():
    h = have.get(kid, {"layers": []})
    wl = [tuple(l.get(f) for f in FIELDS) for l in w["layers"]]
    hl = [tuple(l.get(f) for f in FIELDS) for l in h["layers"] if l.get("textLabel")]
    if wl != hl or w["colorId"] != h.get("colorId"):
        diffs += 1; print("DIFF", kid, "\n   want", wl, "\n   have", hl)
print("in sync" if not diffs else f"{diffs} key(s) differ")
sys.exit(1 if diffs else 0)
