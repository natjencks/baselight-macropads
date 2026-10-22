// Helpers for driving Oryx (configure.zsa.io) from the browser console / Claude's browser pane.
// Oryx has no write API; edits go through its UI. These helpers are pasted into the page and used
// one key at a time: open a key (click it; verify location.pathname ends with /<layer>/<idx>), then
// __setOpen({...}) to set tap/hold/label, then compile with __compile(notes).  Read-back: __pull().
//
// Key index map (ergodox-ez-st): see scripts/common.py NAMES.  Layer tabs: links ending in /latest/<n>.

window.__sleep = ms => new Promise(r => setTimeout(r, ms));
window.__setVal = (inp, v) => { const s = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(inp), 'value').set; s.call(inp, v); inp.dispatchEvent(new Event('input', {bubbles: true})); };

// Pull the latest revision as a compact snapshot (same shape as oryx/snapshot_<rev>.json).
window.__pull = async (hashId = 'Y6DDQ', geometry = 'ergodox-ez-st') => {
  const r = await fetch('https://oryx.zsa.io/graphql', {method: 'POST', headers: {'content-type': 'application/json', authorization: 'Bearer ' + localStorage.jwtToken},
    body: JSON.stringify({query: `{ layout(hashId:"${hashId}", revisionId:"latest", geometry:"${geometry}") { title revision { hashId layers { title keys } } } }`})}).then(r => r.json());
  const rev = r.data.layout.revision;
  const layers = rev.layers.map(l => ({title: l.title, keys: l.keys.map(k => { const o = {};
    for (const f of ['tap', 'hold']) { const v = k[f]; if (v && (v.code || v.layer != null || v.macro)) { const m = v.modifiers || {};
      const mods = Object.entries(m).filter(([a, b]) => b).map(([a]) => a);
      o[f] = {code: v.code, ...(mods.length ? {mods} : {}), ...(v.layer != null ? {layer: v.layer} : {}), ...(v.macro ? {macro: v.macro} : {})}; } }
    if (k.customLabel) o.label = k.customLabel; return o; })}));
  return JSON.stringify({layout: r.data.layout.title, rev: rev.hashId, layers});
};

// Switch layer tab.
window.__goLayer = async l => { const a = [...document.querySelectorAll('a')].find(x => new RegExp('/latest/' + l + '$').test(x.getAttribute('href') || '')); a && a.click(); await __sleep(600); return location.pathname; };

// Centre of key <i> in the pane's 800-px screenshot frame (click it with the computer tool right after).
window.__fc = i => { const el = document.querySelector(`kbd[data-test=key-${i}] a`) || document.querySelector(`kbd[data-test=key-${i}]`); el.scrollIntoView({block: 'center'}); const r = el.getBoundingClientRect(); const s = 800 / innerWidth; return [Math.round((r.left + r.width / 2) * s), Math.round((r.top + r.height / 2) * s)]; };

// In the open key popover: pick a code (search text -> data-code), optional modifiers (Oryx names: 'Left Ctrl','Left Shift','Left Option','Left Cmd').
async function __pick(step, search, code, mods) {
  const link = document.querySelector(`a[data-test=step-${step}]`); if (!link) return 'no step link ' + step; link.click(); await __sleep(400);
  const single = [...document.querySelectorAll('.popover a, .popover button')].find(e => /Single character/.test(e.textContent)); single && single.click(); await __sleep(200);
  const inp = document.querySelector('.popover input[type=search]'); __setVal(inp, search); await __sleep(500);
  const hit = document.querySelector(`.popover [data-test=key-result][data-code="${code}"]`); if (!hit) return 'NO RESULT ' + code; hit.click(); await __sleep(400);
  for (const m of mods || []) { const el = [...document.querySelectorAll('.popover .modifiers .modifier')].find(e => e.textContent.trim() === m); if (el && !el.classList.contains('active')) el.click(); }
  return 'ok';
}
// Set the open key.  spec: {tap:{search,code,mods}|null, hold:{...}|null, label:'<=10 chars'}.  null clears.
window.__setOpen = async spec => {
  const out = [];
  for (const step of ['tap', 'hold']) {
    if (!(step in spec)) continue;
    if (spec[step] === null) { const clr = document.querySelector(`[data-test=action-${step}] a[href="#clear"]`); if (clr) { clr.click(); await __sleep(300); out.push('cleared ' + step); } continue; }
    out.push(step + ': ' + await __pick(step, spec[step].search, spec[step].code, spec[step].mods));
  }
  if ('label' in spec) { const inp = document.querySelector('.popover .custom-label input.label'); if (inp) { __setVal(inp, spec.label); await __sleep(200); out.push('label ' + inp.value); } }
  document.body.click(); await __sleep(300); return out.join(' | ');
};
// Label only (does not touch tap/hold).
window.__label = async (i, txt) => { if (!location.pathname.endsWith('/' + i)) return 'WRONG KEY ' + location.pathname; const inp = document.querySelector('.popover .custom-label input.label'); if (!inp) return 'NO LABEL INPUT'; __setVal(inp, txt); await __sleep(300); const v = inp.value; document.body.click(); await __sleep(300); return 'OK ' + v; };
// Compile with a note; wait ~28 s then __pull() to verify the new revision.
window.__compile = async notes => { await __goLayer(0); const ta = document.querySelector('textarea.textarea'); if (ta) __setVal(ta, notes); const b = [...document.querySelectorAll('button')].find(x => /Compile this layout/i.test(x.textContent)); if (!b) return 'NO BUTTON'; b.click(); return 'compiling'; };

// Set key <i> on the CURRENT layer, which must already be open (URL ends /<layer>/<i>).  Enforces exactly the given
// modifiers (deactivates any others left over from the previous assignment), sets the label, closes the popover.
// spec: {tap:{search,code,mods}|null, label}.  Returns the popover's readback for checking.
window.__setKey = async (layer, i, spec) => {
  if (!location.pathname.endsWith('/' + layer + '/' + i)) return 'WRONG KEY ' + location.pathname;
  const out = [];
  if (spec.tap === null) { const clr = document.querySelector('[data-test=action-tap] a[href="#clear"]'); if (clr) { clr.click(); await __sleep(300); out.push('cleared tap'); } else out.push('nothing to clear'); }
  else {
    out.push('tap: ' + await __pick('tap', spec.tap.search, spec.tap.code, spec.tap.mods));
    const want = new Set(spec.tap.mods || []);
    for (const el of document.querySelectorAll('.popover .modifiers .modifier')) { const n = el.textContent.trim(); if (el.classList.contains('active') && !want.has(n)) { el.click(); await __sleep(150); out.push('-' + n); } }
    const act = [...document.querySelectorAll('.popover .modifiers .modifier.active')].map(e => e.textContent.trim()); out.push('mods=' + act.join('+'));
  }
  const inp = document.querySelector('.popover .custom-label input.label'); if (inp) { __setVal(inp, spec.label || ''); await __sleep(200); out.push('label=' + inp.value); }
  document.body.click(); await __sleep(300); return out.join(' | ');
};
