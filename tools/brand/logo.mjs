// Genereert het Tide-Tode woordmerk als vectorpaden (Bagel Fat One), vervormd in een surfboard.
import opentype from 'opentype.js';
import fs from 'fs';
const buf = fs.readFileSync(new URL('node_modules/@fontsource/bagel-fat-one/files/bagel-fat-one-latin-400-normal.woff', import.meta.url));
const font = opentype.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
const SIZE = 100;
const cap = font.tables.os2.sCapHeight / font.unitsPerEm * SIZE;

function layout(text, tracking = 0) {
  // losse glyphs met eigen letterafstand, als commandolijst in SVG-coördinaten (baseline y=0)
  const glyphs = font.stringToGlyphs(text);
  let x = 0; const cmds = [];
  glyphs.forEach((g, i) => {
    const p = g.getPath(x, 0, SIZE);
    cmds.push(...p.commands);
    let adv = g.advanceWidth / font.unitsPerEm * SIZE;
    if (i < glyphs.length - 1) adv += font.getKerningValue(g, glyphs[i + 1]) / font.unitsPerEm * SIZE;
    x += adv + tracking * SIZE;
  });
  const width = x - tracking * SIZE;
  return { cmds, width };
}
const lerp = (a, b, t) => a + (b - a) * t;
function subdivide(cmds, n = 8) {
  // zet Q/C om in n kleinere C-stukken zodat de vervorming vloeiend blijft
  const out = []; let px = 0, py = 0, sx = 0, sy = 0;
  for (const c of cmds) {
    if (c.type === 'M') { out.push(c); px = sx = c.x; py = sy = c.y; continue; }
    if (c.type === 'L') {
      for (let i = 1; i <= n; i++) { const t = i / n; out.push({ type: 'L', x: lerp(px, c.x, t), y: lerp(py, c.y, t) }); }
      px = c.x; py = c.y; continue;
    }
    if (c.type === 'Z') {
      if (px !== sx || py !== sy) for (let i = 1; i <= n; i++) { const t = i / n; out.push({ type: 'L', x: lerp(px, sx, t), y: lerp(py, sy, t) }); }
      out.push(c); px = sx; py = sy; continue;
    }
    let c1x, c1y, c2x, c2y;
    if (c.type === 'Q') { c1x = px + 2 / 3 * (c.x1 - px); c1y = py + 2 / 3 * (c.y1 - py); c2x = c.x + 2 / 3 * (c.x1 - c.x); c2y = c.y + 2 / 3 * (c.y1 - c.y); }
    else { c1x = c.x1; c1y = c.y1; c2x = c.x2; c2y = c.y2; }
    let P = [[px, py], [c1x, c1y], [c2x, c2y], [c.x, c.y]];
    for (let i = n; i >= 1; i--) {
      const t = 1 / i; // split het resterende stuk
      const [a, b, cc, d] = P;
      const ab = [lerp(a[0], b[0], t), lerp(a[1], b[1], t)], bc = [lerp(b[0], cc[0], t), lerp(b[1], cc[1], t)], cd = [lerp(cc[0], d[0], t), lerp(cc[1], d[1], t)];
      const abc = [lerp(ab[0], bc[0], t), lerp(ab[1], bc[1], t)], bcd = [lerp(bc[0], cd[0], t), lerp(bc[1], cd[1], t)];
      const m = [lerp(abc[0], bcd[0], t), lerp(abc[1], bcd[1], t)];
      out.push({ type: 'C', x1: ab[0], y1: ab[1], x2: abc[0], y2: abc[1], x: m[0], y: m[1] });
      P = [m, bcd, cd, d];
    }
    px = c.x; py = c.y;
  }
  return out;
}
const f = (n) => +n.toFixed(1);
function toD(cmds, map = (x, y) => [x, y]) {
  return cmds.map((c) => {
    if (c.type === 'M' || c.type === 'L') { const [x, y] = map(c.x, c.y); return `${c.type}${f(x)} ${f(y)}`; }
    if (c.type === 'C') { const [a, b] = map(c.x1, c.y1), [d, e] = map(c.x2, c.y2), [x, y] = map(c.x, c.y); return `C${f(a)} ${f(b)} ${f(d)} ${f(e)} ${f(x)} ${f(y)}`; }
    if (c.type === 'Q') { const [a, b] = map(c.x1, c.y1), [x, y] = map(c.x, c.y); return `Q${f(a)} ${f(b)} ${f(x)} ${f(y)}`; }
    return 'Z';
  }).join('');
}

// ---------- 1. surfboard-woordmerk ----------
const { cmds, width } = layout('TIDE-TODE', -0.055);
const SPAN = 0.87;                 // deel van de boardlengte dat de tekst vult
const L = width / SPAN;            // boardlengte
const HB = L / 6.3;                // halve boardhoogte in het midden
const prof = (t) => Math.pow(Math.max(0, 1 - t * t), 0.82); // boardvorm
const PAD = HB * 0.17;              // ruimte tussen rand en letters
const warp = (x, y) => {
  const t = (x - width / 2) / (L / 2);
  const v = (y + cap / 2) / (cap / 2);              // -1 boven, +1 onder
  const h = Math.max(HB * prof(t) - PAD, HB * 0.12);
  const xs = (x - width / 2) * 1.0;
  return [xs, v * h];
};
const wordD = toD(subdivide(cmds, 6), warp);
// board-rand
const pts = [];
for (let i = 0; i <= 120; i++) { const t = -1 + 2 * i / 120; pts.push([t * L / 2, -HB * prof(t)]); }
for (let i = 120; i >= 0; i--) { const t = -1 + 2 * i / 120; pts.push([t * L / 2, HB * prof(t)]); }
const boardD = 'M' + pts.map(([x, y]) => `${f(x)} ${f(y)}`).join('L') + 'Z';
const stroke = HB * 0.1;
const pad = stroke * 2;
const board = { viewBox: `${f(-L / 2 - pad)} ${f(-HB - pad)} ${f(L + 2 * pad)} ${f(2 * HB + 2 * pad)}`, wordD, boardD, stroke: f(stroke) };

// ---------- 2. rechte woordmerken ----------
function flat(text, tr) {
  const { cmds, width } = layout(text, tr);
  const g = font.getPath(text, 0, 0, SIZE).getBoundingBox();
  return { d: toD(cmds), viewBox: `-2 ${f(-cap - 26)} ${f(width + 4)} ${f(cap + 52)}`, width: f(width) };
}
const flatCaps = flat('TIDE-TODE', -0.02);
const flatMixed = flat('Tide-Tode', -0.02);
const flatTT = flat('TT', -0.06);
fs.writeFileSync(new URL('logo.json', import.meta.url), JSON.stringify({ board, flatCaps, flatMixed, flatTT, cap: f(cap) }));
console.log('board', board.viewBox, 'stroke', board.stroke, 'len', board.wordD.length, 'caps', flatCaps.viewBox, 'mixed', flatMixed.viewBox);
