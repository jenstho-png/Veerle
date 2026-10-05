// Lokale preview: rendert de surf-secties met liquidjs + Shopify-shims (geen echte store).
import { Liquid } from 'liquidjs';
import fs from 'fs';
import path from 'path';

const T = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../theme');
const OUT = path.resolve(path.dirname(new URL(import.meta.url).pathname), 'out');
fs.mkdirSync(OUT, { recursive: true });
for (const f of fs.readdirSync(`${T}/assets`)) if (/\.(css|woff2|png|webp)$/.test(f) || f === 'mk-stijl.js') fs.copyFileSync(`${T}/assets/${f}`, `${OUT}/${f}`);
fs.copyFileSync(`${T}/assets/surf.js`, `${OUT}/surf.js`);

const engine = new Liquid({ root: [`${T}/snippets`], extname: '.liquid', strictFilters: false, jsTruthy: false });
const noop = { parse(tk, remain) { this.tpls = []; const s = this.liquid.parser.parseStream(remain); s.on(`tag:end${tk.name}`, () => s.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => {}); s.start(); }, *render() { return ''; } };
engine.registerTag('schema', noop);
engine.registerTag('form', {
  parse(tk, remain) { this.tpls = []; const s = this.liquid.parser.parseStream(remain); s.on('tag:endform', () => s.stop()).on('template', (t) => this.tpls.push(t)); s.start(); },
  *render(ctx, emitter) { ctx.push({ form: { posted_successfully: false } }); emitter.write('<form method="post">'); yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter); emitter.write('</form>'); ctx.pop(); },
});
const F = {
  asset_url: (s) => s, image_url: (i) => i?.src || i, money: (c) => `€${(c / 100).toFixed(2).replace('.', ',')}`,
  json: (v) => JSON.stringify(v ?? null), t: (k) => k, stylesheet_tag: (u) => `<link rel="stylesheet" href="${u}">`,
  image_tag: (src, ...a) => `<img src="${src}" alt="">`, payment_type_svg_tag: () => '',
  preload_tag: (u) => `<link rel="preload" href="${u}" as="image">`,
  placeholder_svg_tag: (n, cls) => `<svg class="${cls || ''}" viewBox="0 0 10 10"></svg>`,
};
for (const [k, fn] of Object.entries(F)) engine.registerFilter(k, fn);

const settings = {
  surf_popup_enable: false, social_instagram_link: 'https://instagram.com/', logo: null,
};
const globals = {
  settings, shop: { name: 'Tide-Tode', url: 'https://example.com' },
  routes: { root_url: '/', search_url: '/search', cart_url: '/cart', account_url: '/account', all_products_collection_url: '/collections/all' },
  cart: { item_count: 1 }, request: { page_type: 'index', path: '/' }, images: {},
};

const schemaOf = (src) => JSON.parse(src.match(/{% schema %}([\s\S]*?){% endschema %}/)[1]);
async function renderSection(type, data, idx) {
  const src = fs.readFileSync(`${T}/sections/${type}.liquid`, 'utf8');
  const sch = schemaOf(src);
  const s = {};
  for (const x of sch.settings || []) if ('default' in x) s[x.id] = x.default;
  Object.assign(s, data.settings || {});
  const blocks = (data.block_order || []).map((id) => {
    const b = data.blocks[id]; const bs = (sch.blocks || []).find((x) => x.type === b.type);
    const st = {}; for (const x of bs?.settings || []) if ('default' in x) st[x.id] = x.default;
    return { type: b.type, settings: Object.assign(st, b.settings), shopify_attributes: '' };
  });
  const body = src.replace(/{% schema %}[\s\S]*?{% endschema %}/, '');
  return engine.parseAndRender(body, { ...globals, section: { id: `s${idx}`, index: idx, settings: s, blocks } });
}

async function page(name, tplPath, extra = {}) {
  const tpl = JSON.parse(fs.readFileSync(`${T}/templates/${tplPath}`, 'utf8'));
  const hg = JSON.parse(fs.readFileSync(`${T}/sections/header-group.json`, 'utf8'));
  const fg = JSON.parse(fs.readFileSync(`${T}/sections/footer-group.json`, 'utf8'));
  Object.assign(globals.request, extra.request || {});
  let html = '';
  for (const k of hg.order) html += await renderSection(hg.sections[k].type, hg.sections[k], 0);
  let i = 1;
  for (const k of tpl.order) {
    const d = tpl.sections[k];
    if (!d.type.startsWith('surf-') && !d.type.startsWith('mk-')) { html += `<div style="padding:40px;text-align:center;opacity:.5">[Dawn: ${d.type}]</div>`; continue; }
    html += await renderSection(d.type, d, i++);
  }
  html += await renderSection('surf-footer', fg.sections['surf-footer'], 99);
  const schemes = JSON.parse(fs.readFileSync(`${T}/config/settings_data.json`, 'utf8')).presets.Dawn.color_schemes;
  const hex = (h) => [1, 3, 5].map((n) => parseInt(h.slice(n, n + 2), 16)).join(',');
  const css = Object.entries(schemes).map(([id, { settings: c }]) => `.color-${id}{--color-background:${hex(c.background)};--color-foreground:${hex(c.text)};--color-button:${hex(c.button)};--color-button-text:${hex(c.button_label)};background-color:rgb(var(--color-background));color:rgb(var(--color-foreground))}`).join('\n');
  const doc = `<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${name}</title>
<style>html{font-size:62.5%}body{margin:0;font-size:1.6rem;line-height:1.5;font-family:var(--font-body-family);background:#F4EEE4;color:#142029}*,*::before,*::after{box-sizing:border-box}.visually-hidden{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}${css}</style>
<link rel="stylesheet" href="surf.css">${await engine.renderFile('mk-stijl', { papier: true, leesbalk: true })}<script src="surf.js" defer></script></head><body>${html}</body></html>`;
  fs.writeFileSync(`${OUT}/${name}.html`, doc);
}

await page('home', 'index.json');
await page('over-ons', 'page.over-ons.json', { request: { page_type: 'page' } });
await page('faq', 'page.veelgestelde-vragen.json', { request: { page_type: 'page' } });
console.log('rendered');
