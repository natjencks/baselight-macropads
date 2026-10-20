# Working notes for Claude (read before touching Oryx or Yuzu)

Project: Nat's Baselight control setup — ErgoDox EZ (ST/glow, firmware v25) as two macropads + Yuzu keycaps.
Nat is a colorist, not a developer: run git/scripts for him, explain in plain words, flag any click he must do himself.
`master.yaml` is the single source of truth; never hand-edit Oryx or Yuzu without updating it. See README for the loop.

## Naming
Left half columns 1–7 left→right, rows A–E top→bottom (1A upper-left). Right half R1 (centre) → R7 (outer).
Thumbs T1/T2 top pair, T3 big outer, T4 big inner, T5 upper small, T6 lower small; right side RT1–RT6 mirrored.
Layers are "Layer 0/1/2/3" (never shift/tool). L1 = hold T3 (red), L2 = hold T4 (green), L3 = T3+T4 chord one-shot (blue).
Oryx key index ↔ name ↔ Yuzu id tables are in scripts/common.py (geometry ergodox-ez-st).

## Oryx (configure.zsa.io) — layout Y6DDQ "Ergodox Baselight V16", forked from V15 eLNjy
- No write API. Read-back: GraphQL `POST https://oryx.zsa.io/graphql` with `Bearer localStorage.jwtToken`
  (query in scripts/oryx_browser.js `__pull`). Always verify a compile by pulling the new revision hash.
- Editing is via the UI in the built-in browser pane. After every compile the layout is READ-ONLY until the
  "Modify layout" link is clicked (find it with `find`, click by ref). First-time: Oryx needs "Detect my keyboard"
  (STM32 chip) before it allows editing.
- `.click()` on key anchors from JS does NOT open keys. Use `__fc(i)` to get the key's centre in screenshot
  coordinates, then click with the computer tool immediately (coordinates shift with scroll), then check
  `location.pathname` ends with `/<layer>/<idx>` BEFORE editing. Wrong-key edits happened twice this way.
- Popover helpers: `__setOpen({tap:{search,code,mods}|null, hold:{...}|null, label})`, `__label(i, txt)`.
  Modifier names in the popover: 'Left Ctrl' 'Left Shift' 'Left Option' 'Left Cmd'. Labels max 10 chars.
  Key-code search quirks: KC_LBRACKET/KC_RBRACKET, "minus"→KC_KP_MINUS, "quot"→KC_QUOTE, "period"→KC_DOT,
  "layer"→MO/OSL. Re-open the step link before each search (the search box doesn't re-filter otherwise).
- Firmware rules: a key that holds→Layer N is forced transparent on Layer N (Oryx refuses to assign it).
  OSL keys cannot have hold actions. Combos fire on release and cannot contain MO. Tap-dance keys lose
  hold-on-other-key-press — avoid. Settings: "Hold On Other Key Press" ON, retro tapping OFF.
- Compile: set the notes textarea (`textarea.textarea`), click "Compile this layout", wait ~28 s, `__pull()`.
- The pane sometimes resets (tabs vanish, helpers gone): re-open the layout, re-paste scripts/oryx_browser.js.

## Yuzu (yuzukeycaps.com) — Playground, ErgoDox stock layout, KAM profile (only profile with 1.5u-vertical caps)
- Developer docs at /dev: JSON import/export + public config API (/api/dev/profiles, sizes, outlines, colors...).
- The set is imported via Settings → Advanced → Export/Import JSON → Import JSON. The button opens a file picker;
  scripts/yuzu_browser.js hooks it and feeds `window.__json` (`__merge(keys)` then `__import()`).
  The Advanced section is hidden at narrow widths: resize the pane viewport to ≥1400 px first; reset after.
- Units: SVG is in mm; `textSize` ≈ em height in mm, cap height ≈ 0.712 × textSize for Helvetica Now;
  layer `y` is mm from the key centre (negative = up). 1u KAM top is 11.45 × 11.45 mm (usable ≈ 10.4).
- Fonts: Nat's uploads live on HIS account — the pane must be signed in to see them. IDs: 26345 =
  "HelvNow Cn575 BL" (our subset, weight 575 / width 70 / opsz 8, used for all slot labels);
  11838 = Helvetica Now Var Text Cond Regular (big centred numpad/arrow legends); 9658 = Text (normal width).
  Yuzu applies GPOS kerning to uploaded fonts (verified to 0.001 mm). Helvetica Now lacks ⇄ ◀ ▶ (use ‹ › ← →).
- Nothing persists in the Playground until Nat clicks Save; never Add to cart / purchase — leave that to him.
- Design decisions (Nat's): ALL CAPS; four fixed slots per key at the same heights on every key (blank slot when a
  layer is unassigned); L0 2.65 mm, variants 1.8 mm uniform (sized by the longest label); white caps, inks
  black / red RD003 / green GN010 / blue BL023; numpad + arrows one big centred legend; SemiBold for labels,
  Regular for the big glyphs. Previews can be rendered locally with PIL from fonts/ to avoid Yuzu round-trips.

## Baselight facts used
Shortcuts from the 7.0 Linux sheet (new): play shot Ctrl+Space; Ctrl+F1 is stereo-only; Reset Operator Ctrl+Backspace;
Timeline Alignment panel Win+; vs Align Timeline Vertically Ctrl+;. Layer-3 jumps send F13–F17 for a FLAPI script (todo).
