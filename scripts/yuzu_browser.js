// Helpers for the Yuzu Playground (yuzukeycaps.com/playground).  The set is imported as a JSON file via
// Settings > Advanced > Export/Import JSON > Import JSON.  Paste this file into the page, set window.__json
// to the contents of yuzu/set.json (or merge yuzu/keys.json into the page's own export with __merge), then
// __import().  __export() returns the Playground's current JSON for yuzu_check.py.

window.__export = async () => {
  const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Export/Import JSON'); b.click();
  await new Promise(r => setTimeout(r, 800));
  const d = [...document.querySelectorAll('div')].filter(e => e.children.length === 0 && /keycapProfileId/.test(e.textContent))[0];
  return d.textContent;
};
// Merge a keys map (yuzu/keys.json) into the page's current export -> window.__json
window.__merge = async (keys, name) => { const o = JSON.parse(await __export()); o.keys = keys; o.keyTemplates = {}; o.designUrl = null; if (name) o.name = name; window.__json = JSON.stringify(o); return Object.keys(o.keys).length; };
// Hook the file picker the Import button opens and feed it window.__json.
window.__import = async () => {
  if (!HTMLInputElement.prototype.click.toString().includes('__hooked')) {
    const orig = HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click = function () {
      if (this.type === 'file' && !/ttf|otf/.test(this.accept || '')) { window.__hooked = 'input.click';
        const dt = new DataTransfer(); dt.items.add(new File([window.__json], 'set.json', {type: 'application/json'})); this.files = dt.files;
        setTimeout(() => { this.dispatchEvent(new Event('input', {bubbles: true})); this.dispatchEvent(new Event('change', {bubbles: true})); }, 0); return; }
      return orig.call(this); };
  }
  const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Export/Import JSON'); b.click();
  await new Promise(r => setTimeout(r, 800));
  const i = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Import JSON'); i.click();
  await new Promise(r => setTimeout(r, 1500)); document.body.click(); return 'imported';
};

// --- Saved-design helpers (Open dialog, update-from-repo, verification) ---
window.__sleep = ms => new Promise(r => setTimeout(r, ms));
// The Export/Import dialog must be closed with its X between operations (body.click() leaves stale export text).
window.__closeDlg = async () => { const x = document.querySelector('span.cursor-pointer.p-1'); if (x) x.click(); await __sleep(500); };
// Open the "MY CUSTOM SETS" dialog; click "Load More" when the design is not among the first 9.
window.__openDlg = async () => { const b = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === 'Open'); (b.find(x => x.offsetParent) || b[0]).click(); await __sleep(1500); return !![...document.querySelectorAll('*')].find(e => e.children.length === 0 && /MY CUSTOM SETS/.test(e.textContent)); };
// Screenshot coordinates (800-px frame) of a design entry in the Open dialog -> click it with the computer tool.
window.__entryPos = name => { const el = [...document.querySelectorAll('div.font-semibold')].find(e => e.textContent.trim() === name); if (!el) return null; const r = el.closest('div.w-full').getBoundingClientRect(); const s = 800 / innerWidth; return [Math.round((r.left + r.width / 2) * s), Math.round((r.top + r.height / 2) * s)]; };
// Summary of the open design (name + T3 colour/layers) for verification.
window.__probe = async () => { const c = JSON.parse(await __export()); await __closeDlg(); return c.name + ': T3 ' + c.keys['54TSLP'].colorId + ' ' + c.keys['54TSLP'].layers.map(l => l.textLabel || ('dot ' + l.colorId)).join('/'); };
// Replace the OPEN design with yuzu/<file> from the repo at commit window.__sha (raw /main/ URLs are cached ~5 min).
// Guards: refuses when a different design is open or the file's name differs.  Then the Save click.
window.__loadFromRepo = async (expectName, file) => { let c = JSON.parse(await __export()); await __closeDlg(); if (c.name !== expectName) return 'WRONG DESIGN OPEN: ' + c.name; const r = await fetch('https://raw.githubusercontent.com/natjencks/baselight-macropads/' + window.__sha + '/' + file, {cache: 'no-store'}); const t = await r.text(); const o = JSON.parse(t); if (o.name !== expectName) return 'FILE NAME MISMATCH ' + o.name; window.__json = t; await __import(); await __sleep(2500); return await __probe(); };
// Add a design without overwriting the open one: "New" then import (then Save).
window.__newFromRepo = async (file, expectName) => { const n = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'New'); n.click(); await __sleep(1500); const r = await fetch('https://raw.githubusercontent.com/natjencks/baselight-macropads/' + window.__sha + '/' + file, {cache: 'no-store'}); const t = await r.text(); if (JSON.parse(t).name !== expectName) return 'FILE NAME MISMATCH'; window.__json = t; await __import(); await __sleep(2500); return await __probe(); };
