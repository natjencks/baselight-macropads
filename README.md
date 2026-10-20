# Baselight macropads — master layout

Single source of truth for Nat's Filmlight Baselight control setup on an **ErgoDox EZ** (two macropads)
with custom **Yuzu** keycaps. Edit `master.yaml`; everything else is generated from it.

```
master.yaml            the truth: every key × layer → function, keystroke, Oryx label, keycap legend; plus cap styling
scripts/sync.py        renders yuzu/set.json + diagram.html and diffs Oryx → oryx/pending_edits.json
scripts/common.py      key naming (1A..7E, R1A..R7E, T1..T6, RT1..RT6) ↔ Oryx index ↔ Yuzu key id; keystroke notation
scripts/render_yuzu.py master → Yuzu Playground import file (fixed 4-slot layout, big centred numpad/arrows)
scripts/render_diagram.py  master → diagram.html (colour-coded layer diagram)
scripts/oryx_diff.py   master vs oryx/snapshot_<rev>.json → list of edits Oryx needs
scripts/yuzu_check.py  Yuzu export vs rendered set
scripts/oryx_browser.js / yuzu_browser.js   paste-in helpers for the two web UIs (neither has a write API)
oryx/snapshot_<rev>.json   read-back of an Oryx revision (GraphQL), the firmware side of the truth
yuzu/template.json     Yuzu's stock ErgoDox layout (key ids/positions) — do not edit
yuzu/set.json          generated; import in the Playground: Settings → Advanced → Export/Import JSON → Import
fonts/                 Helvetica Now Cn 575 subset used for legends (uploaded to Yuzu as id 26345; numpad uses 11838)
```

## Workflow

1. Edit `master.yaml` (labels, keystrokes, which layer a function lives on, cap styling).
2. `python3 scripts/sync.py`
   - exit 0: nothing to push anywhere
   - exit 1: a keycap legend is too wide for its cap — shorten it
   - exit 2: Oryx needs edits; they're listed and saved to `oryx/pending_edits.json`
3. **Yuzu**: import `yuzu/set.json` in the Playground (or paste `scripts/yuzu_browser.js`, `__merge(keys)`, `__import()`), then Save.
4. **Oryx**: apply the pending edits in configure.zsa.io (`scripts/oryx_browser.js` helpers), compile, then pull the new
   revision with `__pull()` into `oryx/snapshot_<rev>.json` and set `layout.oryx_revision` in `master.yaml`.
   `sync.py` should then report Oryx in sync.
5. Commit.

## Conventions (master.yaml)

- Keystrokes: `Ctrl+Shift+Enter`, `Win+;`, `F13`, `KP-`, `MO(1)` / `OSL(3)` for layer actions, `macro: Win+Alt+Shift+C, Tab`.
- `oryx:` labels ≤ 10 characters (Oryx limit). `cap:` legends are ALL CAPS; Layer 0 ≤ ~5 chars on a 1u key, variants ≤ 7;
  `\n` makes a second line that takes the next slot (used on the tall DBS keys).
- Layers: 0 = plain press; 1 = hold T3 (red); 2 = hold T4 (green); 3 = T3+T4 chord, one-shot (blue).
- `style.big_keys`: keys drawn with one large centred legend (numpad block + arrows).

## Baselight notes

- Layer-3 jumps send F13–F17; a FLAPI script in Baselight maps them to BASE GRADE / FACE1 / WIDE1 / VIGNETTE / CONTRAST (todo).
- Shortcut sources: Filmlight *Baselight 7.0 Keyboard Shortcuts (Linux)* and the 7.0 User Guide.
