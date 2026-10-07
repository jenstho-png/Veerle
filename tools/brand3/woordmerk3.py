"""Definitief woordmerk (richting 3): Fraunces Italic, Soft 100, opsz 144, gewicht 600, omgezet naar vormen.
- De bovenkant van de T golft heel licht: een detail dat je pas ziet als je kijkt.
- Tussen Tide en Tode staat de golf uit het icoon in plaats van de tilde.
Schrijft logo3.json (paden + maten)."""
import json, math, pathlib, re, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HIER = pathlib.Path(__file__).parent
vf = TTFont(HIER / 'fonts' / 'Fraunces-Italic-VF.ttf')
f = instantiateVariableFont(vf, {'wght': 600, 'opsz': 144, 'SOFT': 100, 'WONK': 0})
f.save(HIER / 'fonts' / 'Fraunces-Italic-Logo.ttf')
gs = f.getGlyphSet(); order = f.getGlyphOrder(); upm = f['head'].unitsPerEm
hbf = hb.Font(hb.Face(hb.Blob.from_file_path(str(HIER / 'fonts' / 'Fraunces-Italic-Logo.ttf'))))
GOLF = json.load(open(HIER / 'golf-icoon.json'))
HELLING = math.tan(math.radians(11))  # cursieve hoek van de letter


class PolyPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs); self.rings = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 17):
            t = i / 16; m = 1 - t
            self.cur.append((m**3*p0[0]+3*m*m*t*a[0]+3*m*t*t*b[0]+t**3*c[0], m**3*p0[1]+3*m*m*t*a[1]+3*m*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(self, a, b):
        p0 = self.cur[-1]
        for i in range(1, 11):
            t = i / 10; m = 1 - t
            self.cur.append((m*m*p0[0]+2*m*t*a[0]+t*t*b[0], m*m*p0[1]+2*m*t*a[1]+t*t*b[1]))
    def _closePath(self):
        if len(self.cur) > 2: self.rings.append(self.cur)
        self.cur = []
    _endPath = _closePath


def vorm(naam):
    pen = PolyPen(gs); gs[naam].draw(pen)
    polys = sorted((Polygon(r).buffer(0) for r in pen.rings), key=lambda p: -p.area)
    v = None
    for p in polys:
        if v is None: v = p
        elif v.contains(p.representative_point()): v = v.difference(p)
        else: v = v.union(p)
    return v


def golvende_t(v):
    """Snijdt een zachte golf uit de bovenkant van de dwarsbalk: anderhalve golf, diepte ~2,5% van de letterhoogte."""
    minx, miny, maxx, maxy = v.bounds
    h = maxy - miny; diepte = h * 0.028; n = 120
    boven = [(minx - 50 + (maxx - minx + 100) * i / n, 0) for i in range(n + 1)]
    lijn = []
    for x, _ in boven:
        t = (x - minx) / (maxx - minx)
        lijn.append((x, maxy - diepte * (0.5 - 0.5 * math.cos(2 * math.pi * 1.5 * t + math.pi))))
    knip = Polygon(lijn + [(maxx + 50, maxy + 100), (minx - 50, maxy + 100)])
    return v.difference(knip)


def pad_van(v, dx, dy):
    """shapely-vorm naar svg-pad, met verschuiving en y omgedraaid."""
    def ring(c):
        c = list(c)
        return 'M' + 'L'.join(f'{x + dx:.1f} {-y + dy:.1f}' for x, y in c[:-1]) + 'Z'
    out = ''
    for p in (v.geoms if v.geom_type == 'MultiPolygon' else [v]):
        out += ring(p.exterior.coords) + ''.join(ring(i.coords) for i in p.interiors)
    return out


def golf_pad(x, y_mid, breedte):
    """De golf uit het icoon, geschaald naar 'breedte', met het midden op y_mid (svg-coördinaten) en cursief schuin."""
    bx0, by0, bx1, by1 = GOLF['bbox']
    s = breedte / (bx1 - bx0); cy = (by0 + by1) / 2
    getallen = iter(re.findall(r'-?\d+\.?\d*', GOLF['d']))
    def omzet(m):
        cmd = m.group(1); paren = re.findall(r'-?\d+\.?\d*', m.group(2)); uit = []
        for i in range(0, len(paren), 2):
            px = (float(paren[i]) - bx0) * s; py = (float(paren[i + 1]) - cy) * s
            px -= py * HELLING
            uit.append(f'{x + px:.1f} {y_mid + py:.1f}')
        return cmd + ' '.join(uit)
    return re.sub(r'([MLC])([^MLCZ]*)', omzet, GOLF['d'])


def regel(tekst, x0=0, y0=0):
    buf = hb.Buffer(); buf.add_str(tekst); buf.guess_segment_properties(); hb.shape(hbf, buf, {'kern': True, 'liga': True})
    d = ''; x = x0; minx = miny = 1e9; maxx = maxy = -1e9
    for info, pos, ch in zip(buf.glyph_infos, buf.glyph_positions, tekst):
        naam = order[info.codepoint]
        if ch == '~':
            breedte = upm * 0.86
            d += golf_pad(x + upm * 0.02, y0 - upm * 0.36, breedte)
            hoogte = breedte * (GOLF['bbox'][3] - GOLF['bbox'][1]) / (GOLF['bbox'][2] - GOLF['bbox'][0])
            minx, maxx = min(minx, x), max(maxx, x + breedte)
            miny, maxy = min(miny, y0 - upm * 0.36 - hoogte / 2), max(maxy, y0 - upm * 0.36 + hoogte / 2)
            x += breedte + upm * 0.06
            continue
        v = vorm(naam)
        if ch == 'T':
            v = golvende_t(v)
        if not v.is_empty:
            ox, oy = x + pos.x_offset, y0 - pos.y_offset
            d += pad_van(v, ox, oy)
            a, b, c, e = v.bounds
            minx, maxx = min(minx, a + ox), max(maxx, c + ox)
            miny, maxy = min(miny, -e + oy), max(maxy, -b + oy)
        x += pos.x_advance
    return d, (minx, miny, maxx, maxy)


def maak(regels):
    d = ''; mn = [1e9, 1e9]; mx = [-1e9, -1e9]
    for tekst, x0, y0 in regels:
        p, (a, b, c, e) = regel(tekst, x0, y0)
        d += p; mn = [min(mn[0], a), min(mn[1], b)]; mx = [max(mx[0], c), max(mx[1], e)]
    return {'d': d, 'vb': f'{mn[0]:.0f} {mn[1]:.0f} {mx[0] - mn[0]:.0f} {mx[1] - mn[1]:.0f}', 'w': mx[0] - mn[0], 'h': mx[1] - mn[1]}


lh = upm * 0.86
uit = {'liggend': maak([('Tide~Tode', 0, 0)]),
       'gestapeld': maak([('Tide~', 0, 0), ('Tode', upm * 0.4, lh)])}
json.dump(uit, open(HIER / 'logo3.json', 'w'))
print({k: (round(v['w']), round(v['h'])) for k, v in uit.items()})
