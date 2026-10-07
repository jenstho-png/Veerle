// Lokale preview: rendert de surf-secties met liquidjs + Shopify-shims (geen echte store).
import { Liquid } from 'liquidjs';
import fs from 'fs';
import path from 'path';

const T = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../theme');
const OUT = path.resolve(path.dirname(new URL(import.meta.url).pathname), 'out');
fs.mkdirSync(OUT, { recursive: true });
for (const f of fs.readdirSync(`${T}/assets`)) if (/\.(css|woff2|png|webp|jpg)$/.test(f) || ['mk-stijl.js', 'tt.js'].includes(f)) fs.copyFileSync(`${T}/assets/${f}`, `${OUT}/${f}`);
fs.copyFileSync(`${T}/assets/surf.js`, `${OUT}/surf.js`);

const engine = new Liquid({ root: [`${T}/snippets`], extname: '.liquid', strictFilters: false, jsTruthy: false });
const noop = { parse(tk, remain) { this.tpls = []; const s = this.liquid.parser.parseStream(remain); s.on(`tag:end${tk.name}`, () => s.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => {}); s.start(); }, *render() { return ''; } };
engine.registerTag('schema', noop);
engine.registerTag('form', {
  parse(tk, remain) { this.tpls = []; const s = this.liquid.parser.parseStream(remain); s.on('tag:endform', () => s.stop()).on('template', (t) => this.tpls.push(t)); s.start(); },
  *render(ctx, emitter) { ctx.push({ form: { posted_successfully: false } }); emitter.write('<form method="post">'); yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter); emitter.write('</form>'); ctx.pop(); },
});
engine.registerTag('paginate', {
  parse(tk, remain) { this.tpls = []; const s = this.liquid.parser.parseStream(remain); s.on('tag:endpaginate', () => s.stop()).on('template', (t) => this.tpls.push(t)); s.start(); },
  *render(ctx, emitter) { ctx.push({ paginate: { pages: 1 } }); yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter); ctx.pop(); },
});
engine.registerTag('style', {
  parse(tk, remain) { this.tpls = []; const s = this.liquid.parser.parseStream(remain); s.on('tag:endstyle', () => s.stop()).on('template', (t) => this.tpls.push(t)); s.start(); },
  *render(ctx, emitter) { emitter.write('<style>'); yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter); emitter.write('</style>'); },
});
const F = {
  asset_url: (s) => s, image_url: (i) => i?.src || i, money: (c) => `€${(c / 100).toFixed(2).replace('.', ',')}`, money_without_trailing_zeros: (c) => `€${(c / 100).toFixed(2).replace('.00', '').replace('.', ',')}`,
  json: (v) => JSON.stringify(v ?? null), t: (k) => k, stylesheet_tag: (u) => `<link rel="stylesheet" href="${u}">`,
  image_tag: (src, ...a) => { const kv = Object.fromEntries(a.filter(Array.isArray)); return `<img src="${src}" alt="${kv.alt || ''}" class="${kv.class || ''}" loading="${kv.loading || 'lazy'}">`; }, payment_type_svg_tag: () => '', payment_button: () => '<div class="shopify-payment-button"><button class="shopify-payment-button__button" style="width:100%;background:#5a31f4;color:#fff;border:0;padding:18px">Koop met Shop Pay</button></div>', divided_by: (a, b) => a / b, prepend: (a, b) => b + a, strip_html: (s) => String(s || '').replace(/<[^>]+>/g, ''), strip_newlines: (s) => String(s || '').replace(/\n/g, ''),
  preload_tag: (u) => `<link rel="preload" href="${u}" as="image">`,
  placeholder_svg_tag: (n, cls) => `<svg class="${cls || ''}" viewBox="0 0 10 10"></svg>`,
};
for (const [k, fn] of Object.entries(F)) engine.registerFilter(k, fn);

const settings = {
  surf_popup_enable: false,
  // nep-product zodat prijs en knoppen in de preview te zien zijn
  tt_product: { title: 'De Draagtas', url: '/products/de-draagtas', available: true, media: [], featured_media: null, has_only_default_variant: true, options_with_values: [], variants: [],
    selected_or_first_available_variant: { id: 1, price: 4000, compare_at_price: null, available: true } }, social_instagram_link: 'https://instagram.com/', logo: null,
};
// standaardwaarden uit settings_schema (alleen wat nog niet gezet is)
for (const g of JSON.parse(fs.readFileSync(`${T}/config/settings_schema.json`, 'utf8'))) for (const x of g.settings || []) if (x.id && 'default' in x && !(x.id in settings)) settings[x.id] = x.default;
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
  if (type === 'tt-check') s.bevestigd = true; // preview: checker tonen met de voorlopige maten
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
    if (!/^(surf|mk|tt)-/.test(d.type)) { html += `<div style="padding:40px;text-align:center;opacity:.5">[Dawn: ${d.type}]</div>`; continue; }
    html += await renderSection(d.type, d, i++);
  }
  html += await renderSection('surf-footer', fg.sections['surf-footer'], 99);
  if (extra.popup) html += await engine.renderFile('surf-lead-popup', { ...globals, settings: { ...settings, surf_popup_enable: true, surf_popup_code: extra.code || '' }, template: { name: 'index' } });
  const schemes = JSON.parse(fs.readFileSync(`${T}/config/settings_data.json`, 'utf8')).presets.Dawn.color_schemes;
  const hex = (h) => [1, 3, 5].map((n) => parseInt(h.slice(n, n + 2), 16)).join(',');
  const css = Object.entries(schemes).map(([id, { settings: c }]) => `.color-${id}{--color-background:${hex(c.background)};--color-foreground:${hex(c.text)};--color-button:${hex(c.button)};--color-button-text:${hex(c.button_label)};background-color:rgb(var(--color-background));color:rgb(var(--color-foreground))}`).join('\n');
  const doc = `<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${name}</title>
<style>html{font-size:62.5%}body{margin:0;font-size:1.6rem;line-height:1.5;font-family:var(--font-body-family);background:#F4EEE4;color:#142029}*,*::before,*::after{box-sizing:border-box}.visually-hidden{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}${css}</style>
<link rel="stylesheet" href="surf.css">${await engine.renderFile('mk-stijl', { papier: true, leesbalk: true })}<link rel="stylesheet" href="tt.css"><script>document.documentElement.classList.add('tt-js');if(location.hash==='#stil')document.documentElement.classList.add('tt-stil');</script><script src="surf.js" defer></script><script src="tt.js" defer></script></head><body>${html}</body></html>`;
  fs.writeFileSync(`${OUT}/${name}.html`, doc);
}

await page('home', 'index.json');
await page('popup', 'index.json', { popup: true, code: 'TIDE10' });
// productpagina met een nep-product en losse foto's als 'productfoto's'
{
  const foto = (f) => ({ media_type: 'image', alt: 'De Tide-Tode draagtas', preview_image: { src: f } });
  // zonder eigen media: dan toont de galerij de getekende productbeelden
  globals.product = { ...settings.tt_product, title: 'Draagtas Tegel', description: '<p>De Tide-Tode draagtas in tegelprint. Je schuift je surfboard in de tas en hangt hem over je schouder.</p>',
    vendor: 'Tide-Tode', url: '/products/draagtas-tegel', featured_media: null, media: [],
    variants: [{ id: 1, price: 4000, available: true, url: '/products/de-draagtas?variant=1', sku: 'TT-01', options: [] }] };
  globals.template = { name: 'product' };
  globals.cart = { ...globals.cart, currency: { iso_code: 'EUR' } };
  globals.request.origin = 'https://tide-tode.example';
  await page('product', 'product.json', { request: { page_type: 'product' } });
}
await page('over-ons', 'page.over-ons.json', { request: { page_type: 'page' } });
await page('faq', 'page.veelgestelde-vragen.json', { request: { page_type: 'page' } });
globals.page = { title: 'Contact', content: '' };
await page('contact', 'page.contact.json', { request: { page_type: 'page', path: '/pages/contact' } });
globals.page = { title: 'Herroepingsrecht', content: fs.readFileSync(path.resolve(T, '../docs/juridisch/herroepingsrecht.html'), 'utf8') };
await page('herroepingsrecht', 'page.juridisch.json', { request: { page_type: 'page', path: '/pages/herroepingsrecht' } });
globals.page = { title: 'Maatwijzer', content: '<p>Hier lees je welke boards in de draagtas passen en welke maat kleding je kiest.</p>' };
await page('maatwijzer', 'page.maatwijzer.json', { request: { page_type: 'page', path: '/pages/maatwijzer' } });
globals.page = { title: 'Duurzaamheid', content: '' };
await page('duurzaamheid', 'page.duurzaamheid.json', { request: { page_type: 'page', path: '/pages/duurzaamheid' } });
globals.page = { title: 'Actie', content: '' };
await page('actie', 'page.actie.json', { request: { page_type: 'page', path: '/pages/actie' } });
// collectie met de producten uit de csv
{
  const B = path.resolve(T, '../docs/producten/beelden');
  for (const f of fs.readdirSync(B)) fs.copyFileSync(`${B}/${f}`, `${OUT}/${f}`);
  const rijen = fs.readFileSync(path.resolve(T, '../docs/producten/producten.csv'), 'utf8');
  const prod = {};
  for (const m of rijen.matchAll(/^([^,\n]*),([a-z0-9-]+),/gm)) if (m[1] && !prod[m[2]]) prod[m[2]] = m[1];
  const lijst = Object.entries(prod).map(([h, t]) => ({ title: t, url: `/products/${h}`, available: true, price: 4000, price_varies: false,
    featured_media: { src: `${h}-1.jpg`, alt: t }, media: [{ src: `${h}-1.jpg` }, { src: fs.existsSync(`${B}/${h}-3.jpg`) ? `${h}-3.jpg` : `${h}-2.jpg` }] }));
  const col = { title: 'Alle producten', handle: 'all', description: '<p>Draagtassen, surfgear en kleding van Tide-Tode.</p>', products: lijst, products_count: lijst.length,
    sort_options: [{ value: 'manual', name: 'Uitgelicht' }, { value: 'price-ascending', name: 'Prijs, laag naar hoog' }], default_sort_by: 'manual' };
  globals.collection = col;
  globals.collections = { draagtassen: { products_count: 9, products: [lijst[0]] }, surfgear: { products_count: 7 }, 'kleding-en-merch': { products_count: 11 } };
  globals.routes.collections_url = '/collections';
  await page('collectie', 'collection.json', { request: { page_type: 'collection', path: '/collections/all' } });
  await page('collecties', 'list-collections.json', { request: { page_type: 'list-collections', path: '/collections' } });
}
console.log('rendered');
