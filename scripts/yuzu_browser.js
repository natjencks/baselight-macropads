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
