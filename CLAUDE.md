# Working notes for Claude (read before touching Oryx or Yuzu)

Project: Nat's Baselight control setup — ErgoDox EZ (ST/glow, firmware v25) as two macropads + Yuzu keycaps.
Nat is a colorist, not a developer: run git/scripts for him, explain in plain words, flag any click he must do himself.
`master.yaml` is the single source of truth; never hand-edit Oryx or Yuzu without updating it. See README for the loop.
After EVERY layout change (even master-only), regenerate and send diagram.html to Nat (SendUserFile, render) — the inline
widget doesn't reach him. The diagram's blue band shows the Layer-3 corner letter in bold plus the Oryx name greyed (not printed on the cap).

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
  `__fc` can also return a neighbouring key's centre (seen for #57 → gave #64's spot after keys were cleared):
  when in doubt take a screenshot, click from it, and trust only the URL. The pane viewport is ~800 px wide.
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
  26415 = "HelvNow Cn300 BL" (Light, width 70: big centred numpad/arrow/NUM/ENTER legends — its 0.52 mm stem matches the
  arrow icons' stroke); 11838 = Helvetica Now Var Text Cond Regular (no longer used); 9658 = Text (normal width).
  Font ids can be looked up in Yuzu's Supabase: fetch /rest/v1/fonts?select=id,name&name=ilike.*X* with the anon key
  from useRuntimeConfig (public.supabase.key) + the sb-*-auth-token access_token. The variable source font is only in
  the session uploads (helvetica-now-var.ttf) — ask Nat for it again if a new instance is needed; fonts/ has the subsets.
  Yuzu applies GPOS kerning to uploaded fonts (verified to 0.001 mm). Helvetica Now lacks ⇄ ◀ ▶ (use ‹ › ← →).
- Nothing persists in the Playground until Save is clicked (Nat, or me when his message asks for it); never Add to cart / purchase — leave that to him.
- Palette: yuzu/colors.txt (id:hex, from /api/dev/colors). No tints paler than e.g. BL034/PK014/GN025/PL018/YW019;
  the dark range is small (GR001, GR029, BL010, BL022, RD006, RD025, PL004, PL002, GN022, GN009, BN024...).
  Light legends on dark caps are orderable (Yuzu's own /dev/json example does it).
- Legends can be SVG: KeyLayer {vectDef, vectViewbox, vectScale}; vectScale 100 maps the viewBox HEIGHT to 1u
  (19.05 mm) whatever the aspect (measured with getBBox on the Playground SVG), so a 20/24-unit circle at
  vectScale 44 is a 7 mm dot and any icon at 23.1 is 4.4 mm tall. Used for the L1/L2 thumb dots and the icon sets.
- Icon sets: Nat's SVGs in icons/ (Illustrator exports) -> scripts/icons.py -> icons/icons.json (one flattened path
  each). yuzu_variant.py builds TAG+"i" variants ("Audition X icons"): ICON_MAP key->icon, slot icons 3.5 mm tall at
  y -3.45 (4.4 mm clipped at the cap-top edge), L1/L2 labels stay in their slots. The ARROW keys use Nat's arrow icons on
  EVERY set (legends.ARROWS): 9 mm long axis, centred, R1D's dropped 0.25u (y 4.76) to line up with R3D. Saved on Yuzu: "Audition C icons", "Audition F icons". legends.SLOT_ICONS (7A Backspace, icons/Backspace.svg: my ⌫ in Nat's style, 2:1 point, floating X — Nat rejected the X-through-to-the-edges version) print on every set; icons/AudioMute.svg was
  redrawn by me (stroke 0.53 mm at 9 mm, arcs concentric on the speaker) and shows full size (BIG_ICON_MAP) on the icon sets.
  Unplaced icons (Dot, Grid, Boundry*, Expand*, Trash*, Carrot*Thin): ask Nat what they are for. master.yaml `diagram:` gives
  a diagram-only label for icon legends.
- Colour auditions: scripts/yuzu_variant.py SCHEME -> yuzu/variants/SCHEME.json (same slots as the production set,
  per-zone caps). The page can fetch variant JSON straight from raw.githubusercontent.com (repo is public) into window.__json.
  The pane's screenshot is capped at 800 px wide: for a readable render, serialise the Playground
  SVG into a fixed full-screen iframe (window.__showFrame in the session notes) and tile 3 screenshots.
- Saving: the harness refuses an UNREQUESTED Save click, but when Nat's message itself asks for the save ("save B1",
  "...and save it") the click is allowed — verified 2026-10-21. Otherwise it is Nat's click. To add a design without overwriting the open one:
  click "New" (button text becomes "No name"), import, then Nat clicks Save. To update a saved design: "Open" (JS
  click on the button, then click the entry by ref), import, Nat saves. The Export/Import dialog must be CLOSED
  with its X between operations (document.body.click() doesn't close it and the export text goes stale).
  Saved on Nat's account: Audition G, B1, C, F, C icons, F icons (B1 and G: solid RD003/GN023 layer keys) (right half: arrows own colour; PREFS/JOBS admin grey;
  MUTE/ALIGN/FOLD/COUNT/CYCLE/CSJ/GROUP one "other" colour; numpad plain). Nat's favourites: C and F. All four
  match yuzu/variants/*.json as of 2026-10-21 (thumb cluster in one colour with L1/L2 dots in the L1/L2 ink colours,
  ALT/SHIFT/CTRL one big centred label, ENTER sized like NUM, 7A DELETE/BKSP, R1A SCENE/FORMAT, R7D ALL SHOTS, R7E TAPE).
- Design decisions (Nat's, 2026-10-21): ALL CAPS; THREE fixed text slots per key at the same heights on every key
  (scripts/legends.py: L0 3.2 mm shrinking to fit wide words, L1/L2 2.25 mm uniform; blank slot when unassigned;
  slot centres -3.6 / 0.82 / 3.88 — gap_after_l0 1.7 so the L0 word has air, L2 ends 0.2 mm above the printable edge).
  Layer 3 is NOT a slot: a one-letter cap in master.yaml prints as a 1.5 mm blue letter in the bottom-right corner
  (the layer it jumps to: B/F/W/V/C on row B); empty L3 cap = unlabelled (2A, 4C).
  White caps, inks black / red RD003 / green GN010 / blue BL023; numpad + arrows one big centred legend; SemiBold for
  labels, Regular for the big glyphs. Previews can be rendered locally with PIL from fonts/ to avoid Yuzu round-trips.
- Saved designs on Nat's account (all re-saved 2026-10-21 21:50 at repo 8121fbf / Oryx 3vAb4w: 3-slot legends, Light digits, NUM/ENTER SemiBold at L0 size+position, arrow icons everywhere, 2A GRID/CYC F6, 6A zoom set, 7A ⌫ icon/DEL, R2A MUTE icon full size on icon sets, B1/G solid layer keys with no text, F marks row RD006): Baselight V16 (production, white),
  Audition B1, C, F, G, C icons, F icons, + (21:55) White icons (Wi: production look + icons), Black (K: all black, white L0 + coral/mint/blue
  L1-L3 text, solid red/green layer keys), Black icons (Ki). The Open dialog lists 9 designs; click "Load More" for the rest. Update loop (helpers now in scripts/yuzu_browser.js): set window.__sha = commit -> __openDlg() -> click entry at __entryPos(name)
  -> __loadFromRepo(name, 'yuzu/variants/X.json') -> Save click at (286,20) in the 800-px frame (1024-wide pane). The dates in the Open
  dialog are creation dates, NOT last-saved: verify a save by reloading the page, re-opening the design and probing its JSON.
  ALL TEN re-saved 2026-10-22 17:05 at repo 7f96610 (Oryx XbpMoW): 2A ZOOM/GRID/CYC F6, 6A TL H/TL V/TL HV, 2B 1×1/2x1D/2x1C,
  2C WIP D/ANGLE/Z-GANG, 1C SEL SHOT/BEFORE/AFTER, 1D +LYR/−LYR/NAME, 1E WIN/UI/IMG/LOUPE (mod grey, 3 slots), 4D TOG CAT, 4E WKSP/RST OP,
  6C V-MAT/G‹›M/INS MAT, R3B FOLD/ALL/SHT>TOP, R3C 00:00, R3E GRUP, R7D ALL SHOTS/TAPE, R7E WIN (mod grey, big word).
  Save click at (286,20) is allowed when Nat's message asks for the push. The Open-dialog lookup can race the dialog animation:
  wait 1.5 s after __openDlg before __entryPos. yuzu_variant mod zone: big centred word only when the key has Layer 0 alone.
  Nat wants NO label under full size where possible; remaining shrunk ones are accepted (V-MAT 3.06, SHT>TOP 2.09, ‹MARK 2.89...).
  2026-10-22 17:00: Nat keeps ONLY the icon designs. His account now has exactly six: Audition Black icons, White icons, F icons,
  C icons, B1 icons, G icons (B1/G converted from the text sets; the text designs and Baselight V16 were deleted by Nat).
  Regenerate with `yuzu_variant.py B1i Ci Fi Gi Wi Ki` — the plain tags are no longer needed on Yuzu (set.json is the diagram/text reference).

## Baselight facts used
Shortcuts from the 7.0 Linux sheet (new): play shot Ctrl+Space; Ctrl+F1 is stereo-only; Reset Operator Ctrl+Backspace;
Timeline Alignment panel Win+; vs Align Timeline Vertically Ctrl+;. Layer-3 jumps send F13–F17 for a FLAPI script (todo); Formats is JOBS(R1B)+L1 since B4KY9x; since VqwoWd: 2x1 Cursor 2B+L1, Byp Op 4B+L1 / Byp All 4B+L2,
Grab Still 3C(REW)+L1, Group Grade 5C(FWD)+L1; WvRLzn: 6B L2 Next Shape, 6C View Matte (O) / Grd⇄Matte (G); wOXdx9: 2D L2 Cur|Ref,
2E L2 Gang Curs; GGKD5j: zoom set 2A→6A, 2A = 1x1 Shots view F6 / Cycle F6 Ctrl+F6; 3vAb4w: 7A Backspace L0 / Delete L1, 4C L1 Group Grd,
5C L1 Play Scene / L2 Play Shot; R7D F18 = ALL SHOTS view, R7E F19 = CURRENT TAPE view (Shots View filters, script todo);
NowGbA (2026-10-22): 1C Select Shot Ctrl+Enter / Sel Before Alt+Enter / Sel After Alt+Shift+Enter, 1D Reset Operator Ctrl+Backspace,
4E Toggle last Workspace F8, 7B/7D L1 Layer Up/Down PgUp/PgDn, L2 selected-layer row up/down Alt+PgUp/PgDn, L3 stack top/bottom
Win+PgUp/PgDn, 1E L2 Rename Ctrl+Shift+R, 5C L3 Loop/Bounce Ctrl+B, 5E L3 Multi-paste Ctrl+M, 6C L2 Insert Matte Merge T.
Oryx quirk: clicking "Modify layout" creates the next revision id immediately (NowGbA appeared before compiling, same content as
3vAb4w); the compile then keeps that id — so "rev changed" is not a compile signal; compare key contents instead.
XbpMoW (2026-10-22 17:00): 2A Disp Zoom F12 / 1x1 Shots F6 / Cycle Ctrl+F6; 6A TL zoom F7 / Shift+F7 / Ctrl+Shift+F7 (L3 cleared);
2B L1 2x1|DBS Ctrl+Alt+3, L2 2x1 Cursor F2; 2C Wipe|DBS Ctrl+Alt+4 / Wipe Angle Ctrl+Shift+F3 / Zoom-Pan Gang F9; 1D P / Shift+P / Ctrl+Shift+R;
1E Left Win (hold, for paint-tool Win+drag) / UI-Image Ctrl+Esc / Loupe Win+Esc; 4D L1 Toggle Strip Category F; 4E L1 Reset Op Ctrl+Delete
(FilmLight support: Ctrl+Backspace is Retime/Curve only); 4C L3 cleared; 5E L3 Multi-paste VIEW Win+M (Ctrl+M performs the paste);
R3B L2 Fold Shot into Top Strip Alt+\; R7D L1 CUR TAPE F19; R7E Left Win. Confirmed by Nat: Play Shot = Ctrl+Space, FPS = Win+F.
Shortcut sheets: the 8-page Typst "Baselight_v7.0_KB_Shortcuts_Linux.pdf" (maintained copy, dated 2026-10-20) and FilmLight's
6-page QR-1051; they agree except Play Current Shot (Shift+Ctrl+Space in QR-1051) and FPS (Ctrl+F in Typst — wrong, that's Paste Strips).
The v7 User Guide (1180 pp) was uploaded to the session; extract with pdftotext -layout to grep (Zoom/Pan Ganging p.449, gestural p.86).
