// Tide-Tode logo v2: woordmerk in Fraunces Italic (soft, wonky, 144 opsz) met een getekend golfje,
// een zegel met ronde tekst, en het beeldmerk "de maan draagt": een sikkel die een board draagt.
// Alles wordt als vectorpad weggeschreven, zodat het logo niet van een lettertype afhangt.
import opentype from 'opentype.js';
import fs from 'fs';
const here = (p) => new URL(p, import.meta.url);
const load = (p) => { const b = fs.readFileSync(here(p)); return opentype.parse(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength)); };
const italic = load('fonts/fraunces-italic-600-soft.ttf');
const roman = load('fonts/fraunces-normal-600-soft.ttf');
const f = (n) => +n.toFixed(2);
const r1 = (n) => +n.toFixed(1);

function glyphRun(font, text, size, tracking = 0) {
  const gs = font.stringToGlyphs(text); let x = 0; const runs = [];
  gs.forEach((g, i) => {
    runs.push({ g, x });
    let adv = g.advanceWidth / font.unitsPerEm * size;
    if (i < gs.length - 1) adv += font.getKerningValue(g, gs[i + 1]) / font.unitsPerEm * size;
    x += adv + tracking * size;
  });
  return { runs, width: x - tracking * size };
}
function cmdsToD(cmds, M = (x, y) => [x, y]) {
  return cmds.map((c) => {
    if (c.type === 'M' || c.type === 'L') { const [x, y] = M(c.x, c.y); return `${c.type}${r1(x)} ${r1(y)}`; }
    if (c.type === 'C') { const [a, b] = M(c.x1, c.y1), [d, e] = M(c.x2, c.y2), [x, y] = M(c.x, c.y); return `C${r1(a)} ${r1(b)} ${r1(d)} ${r1(e)} ${r1(x)} ${r1(y)}`; }
    if (c.type === 'Q') { const [a, b] = M(c.x1, c.y1), [x, y] = M(c.x, c.y); return `Q${r1(a)} ${r1(b)} ${r1(x)} ${r1(y)}`; }
    return 'Z';
  }).join('');
}
const textD = (font, text, size, x0 = 0, y0 = 0, tracking = 0) => {
  const { runs, width } = glyphRun(font, text, size, tracking);
  return { d: runs.map(({ g, x }) => cmdsToD(g.getPath(x0 + x, y0, size).commands)).join(''), width };
};

// ---------- golfje (kalligrafisch, dik-dun) ----------
function tilde(x0, x1, yMid, amp, wMax, wMin) {
  const N = 60, top = [], bot = [];
  for (let i = 0; i <= N; i++) {
    const t = i / N, x = x0 + (x1 - x0) * t;
    const y = yMid - amp * Math.sin(t * 2 * Math.PI);
    const dy = -amp * 2 * Math.PI * Math.cos(t * 2 * Math.PI) / (x1 - x0);
    const len = Math.hypot(1, dy), nx = -dy / len, ny = 1 / len;
    const w = wMin + (wMax - wMin) * Math.pow(Math.sin(Math.PI * t), 0.7) * (0.75 + 0.25 * Math.cos(t * 2 * Math.PI)); // breder aan de kam
    top.push([x - nx * w / 2, y - ny * w / 2]); bot.push([x + nx * w / 2, y + ny * w / 2]);
  }
  const pts = top.concat(bot.reverse());
  return 'M' + pts.map(([x, y]) => `${r1(x)} ${r1(y)}`).join('L') + 'Z';
}

// ---------- 1. woordmerk ----------
const SIZE = 120;
const xh = italic.tables.os2.sxHeight / italic.unitsPerEm * SIZE;
const cap = italic.tables.os2.sCapHeight / italic.unitsPerEm * SIZE;
const tide = textD(italic, 'Tide', SIZE, 0, 0, -0.01);
const gap = SIZE * 0.06, tw = SIZE * 0.46;
const tx0 = tide.width + gap, tx1 = tx0 + tw;
const tildeD = tilde(tx0, tx1, -xh * 0.52, SIZE * 0.065, SIZE * 0.085, SIZE * 0.02);
const tode = textD(italic, 'Tode', SIZE, tx1 + gap * 0.6, 0, -0.01);
const wordW = tx1 + gap * 0.6 + tode.width;
const asc = cap * 1.12, desc = SIZE * 0.08;
const woord = { d: tide.d + tilde(tx0, tx1, -xh * 0.52, SIZE * 0.065, SIZE * 0.085, SIZE * 0.02) + tode.d,
  viewBox: `${r1(-SIZE * 0.06)} ${r1(-asc)} ${r1(wordW + SIZE * 0.14)} ${r1(asc + desc)}` };

// ---------- 2. beeldmerk: de maan draagt het getij (200-grid) ----------
// sikkel = buitencirkel min binnencirkel (snijpunten uitgerekend), gekanteld; in de holte drie golfjes
const C1 = { x: 92, y: 100, r: 66 }, C2 = { x: 118, y: 100, r: 58 }, KANTEL = -28;
function circleX(a, b) {
  const dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy);
  const l = (a.r * a.r - b.r * b.r + d * d) / (2 * d), h = Math.sqrt(a.r * a.r - l * l);
  const mx = a.x + dx * l / d, my = a.y + dy * l / d;
  return [[mx + h * dy / d, my - h * dx / d], [mx - h * dy / d, my + h * dx / d]];
}
const rot = (x, y) => { const a = KANTEL * Math.PI / 180; return [100 + (x - 100) * Math.cos(a) - (y - 100) * Math.sin(a), 100 + (x - 100) * Math.sin(a) + (y - 100) * Math.cos(a)]; };
const [P, Q] = circleX(C1, C2).map(([x, y]) => rot(x, y));
const c1 = rot(C1.x, C1.y), c2 = rot(C2.x, C2.y);
const sikkel = `M${f(P[0])} ${f(P[1])}A${C1.r} ${C1.r} 0 1 0 ${f(Q[0])} ${f(Q[1])}A${C2.r} ${C2.r} 0 0 1 ${f(P[0])} ${f(P[1])}Z`;
const gravure = [58, 51].map((r) => `M${f(c1[0] - r)} ${f(c1[1])}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0`).join('');
// golfjes in de holte (eerst recht getekend, dan mee gekanteld)
function rotD(d) { return d.replace(/(-?\d+\.?\d*) (-?\d+\.?\d*)/g, (m, x, y) => { const [a, b] = rot(+x, +y); return `${r1(a)} ${r1(b)}`; }); }
const golfjes = rotD([[88, 138, 84, 5.6, 8.6], [84, 142, 102, 6, 9.6], [90, 134, 120, 5.6, 8.6]].map(([x0, x1, y, a, w]) => tilde(x0, x1, y, a, w, w * 0.24)).join(''));
const board = '', boardDetail = {};

// ---------- 3. zegel: ronde tekst (200-grid, midden 100,100) ----------
function arcText(font, text, size, radius, top, tracking) {
  const { runs, width } = glyphRun(font, text, size, tracking);
  const span = width / radius; let out = '';
  runs.forEach(({ g, x }) => {
    const adv = g.advanceWidth / font.unitsPerEm * size;
    const mid = x + adv / 2;
    const th = top ? (-span / 2 + mid / radius) : (span / 2 - mid / radius);
    const cs = Math.cos(th), sn = Math.sin(th);
    const cmds = g.getPath(-adv / 2, 0, size).commands;
    const M = top
      ? (px, py) => { const y = py - radius; return [100 + px * cs - y * sn, 100 + px * sn + y * cs]; }
      : (px, py) => { const y = py + radius; return [100 + px * cs - y * sn, 100 + px * sn + y * cs]; };
    out += cmdsToD(cmds, M);
  });
  return out;
}
const capR = roman.tables.os2.sCapHeight / roman.unitsPerEm;
const ZS = 15;
const zegel = {
  boven: arcText(roman, 'TIDE      TODE', ZS, 74, true, 0.2),
  onder: arcText(roman, 'VAN RIDERS VOOR RIDERS', ZS * 0.62, 74 + ZS * 0.62 * capR, false, 0.22),
};
// golfje tussen TIDE en TODE in de boog
// golfje bovenaan in het midden van de boog
zegel.tilde = tilde(84, 116, 100 - 74 - ZS * capR * 0.5, 3.6, 5.4, 1.4);

fs.writeFileSync(here('logo.json'), JSON.stringify({ woord, sikkel, gravure, golfjes, zegel, tildeMini: tilde(0, 46, 0, 6.5, 8.5, 2) }));
console.log('woord', woord.viewBox, 'sikkel ok');
