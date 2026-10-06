"""Tide-Tode woordmerk (branding 2): TIDE boven TODE, zachte vloeibare letters.
Basis: een retro-letter (OFL), daarna in code afgerond en licht golvend gemaakt,
ruim gespatieerd, met een surfboard als I in TIDE.
Uitvoer: SVG-paden (viewBox) als JSON en een preview-PNG."""
import json, math, sys, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

HIER = pathlib.Path(__file__).parent

class PolyPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs); self.rings = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 13):
            t = i / 12; mt = 1 - t
            self.cur.append((mt**3*p0[0]+3*mt*mt*t*a[0]+3*mt*t*t*b[0]+t**3*c[0], mt**3*p0[1]+3*mt*mt*t*a[1]+3*mt*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(self, a, b):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; mt = 1 - t
            self.cur.append((mt*mt*p0[0]+2*mt*t*a[0]+t*t*b[0], mt*mt*p0[1]+2*mt*t*a[1]+t*t*b[1]))
    def _closePath(self):
        if len(self.cur) > 2: self.rings.append(self.cur)
        self.cur = []
    _endPath = _closePath

def glyf(font, ch):
    gs = font.getGlyphSet(); naam = font.getBestCmap()[ord(ch)]
    pen = PolyPen(gs); gs[naam].draw(pen)
    # ringen naar polygonen met gaten via even-odd
    polys = [Polygon(r).buffer(0) for r in pen.rings]
    polys.sort(key=lambda p: -p.area)
    vorm = None
    for p in polys:
        if vorm is None: vorm = p
        elif vorm.contains(p.representative_point()) and vorm.contains(p.buffer(-1)): vorm = vorm.difference(p)
        else: vorm = vorm.union(p)
    return vorm, gs[naam].width

def zacht(g, r):
    return g.buffer(r, join_style=1).buffer(-2*r, join_style=1).buffer(r, join_style=1)

def golf(g, amp, freq, fase=0):
    def w(geom):
        if geom.geom_type == 'Polygon':
            ext = [(x + amp*math.sin(y*freq + fase), y + amp*0.5*math.sin(x*freq*0.7 + fase)) for x, y in geom.exterior.coords]
            ints = [[(x + amp*math.sin(y*freq + fase), y + amp*0.5*math.sin(x*freq*0.7 + fase)) for x, y in r.coords] for r in geom.interiors]
            return Polygon(ext, ints).buffer(0)
        return unary_union([w(p) for p in geom.geoms])
    return w(g)

def board(h, b, x, y):
    """surfboard van onder (x,y) omhoog: ronde staart onder, breedste punt
    op ongeveer 40%, spitse neus boven, met een smalle stringer erin."""
    def breedte(t):
        return (max(0.0, 1 - t) ** 0.55) * ((t + 0.18) ** 0.42)
    m = max(breedte(i / 200) for i in range(201))
    rechts = [(x + b / 2 * breedte(i / 80) / m, y + h * i / 80) for i in range(81)]
    links = [(x - b / 2 * breedte(i / 80) / m, y + h * i / 80) for i in range(80, -1, -1)]
    vorm = Polygon(rechts + links).buffer(0)
    stringer = Polygon([(x - b*0.03, y + h*0.1), (x + b*0.03, y + h*0.1), (x + b*0.03, y + h*0.84), (x - b*0.03, y + h*0.84)])
    return vorm.difference(stringer)

def rechte_t(g):
    """De T van Kavoon krult onderaan (leest als J): dwarsbalk houden, eigen stam die onderaan iets uitloopt."""
    minx, miny, maxx, maxy = g.bounds
    h = maxy - miny
    plak = g.intersection(Polygon([(minx - 5, miny + h * 0.45), (maxx + 5, miny + h * 0.45), (maxx + 5, miny + h * 0.55), (minx - 5, miny + h * 0.55)]))
    sx0, _, sx1, _ = plak.bounds; mid = (sx0 + sx1) / 2; sw = sx1 - sx0
    dwars = g.intersection(Polygon([(minx - 5, maxy - h * 0.3), (maxx + 5, maxy - h * 0.3), (maxx + 5, maxy + 5), (minx - 5, maxy + 5)]))
    stam = Polygon([(mid - sw * 0.72, miny), (mid + sw * 0.72, miny), (mid + sw * 0.5, miny + h * 0.16), (mid + sw * 0.5, maxy - h * 0.2), (mid - sw * 0.5, maxy - h * 0.2), (mid - sw * 0.5, miny + h * 0.16)])
    return dwars.union(stam).buffer(18, join_style=1).buffer(-18, join_style=1)


def regel(font, tekst, spatie, r, board_i=False):
    x = 0; vormen = []
    upm = font['head'].unitsPerEm
    capH = getattr(font['OS/2'], 'sCapHeight', 0) or upm*0.7
    for ch in tekst:
        if ch == 'I' and board_i:
            g, w = glyf(font, 'I')
            minx, miny, maxx, maxy = g.bounds
            bw = (maxx - minx) * 1.05; bh = (maxy - miny) * 1.12
            vormen.append(board(bh, bw, x + (minx + maxx)/2, miny - (maxy-miny)*0.03))
            x += w + spatie; continue
        g, w = glyf(font, ch)
        if ch == 'T':
            g = rechte_t(g)
        vormen.append(affinity.translate(g, x, 0)); x += w + spatie
    v = unary_union(vormen)
    v = zacht(v, r)
    return v, x - spatie, capH

def pad(g, H):
    def ring(c):
        c = list(c)
        return 'M' + 'L'.join(f'{x:.1f} {H - y:.1f}' for x, y in c[:-1]) + 'Z'
    ps = []
    for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
        ps.append(ring(p.exterior.coords) + ''.join(ring(i.coords) for i in p.interiors))
    return ''.join(ps)

def maak(fontnaam, spatie_f=0.32, r_f=0.022, amp_f=0.012, regel_gat=0.18):
    font = TTFont(HIER / 'fonts' / fontnaam)
    upm = font['head'].unitsPerEm
    boven, wb, cap = regel(font, 'TIDE', upm*spatie_f, upm*r_f, board_i=True)
    onder, wo, _ = regel(font, 'TODE', upm*spatie_f, upm*r_f)
    # beide regels even breed: TODE iets wijder spatiëren is lastig; centreren
    W = max(wb, wo)
    b0 = boven.bounds; o0 = onder.bounds
    hb = b0[3] - b0[1]; ho = o0[3] - o0[1]
    gat = upm*regel_gat
    boven = affinity.translate(boven, (W - wb)/2 - b0[0] + 0, ho + gat - b0[1])
    onder = affinity.translate(onder, (W - wo)/2 - o0[0], -o0[1])
    alles = unary_union([boven, onder])
    alles = golf(alles, upm*amp_f, 2*math.pi/(upm*0.9))
    minx, miny, maxx, maxy = alles.bounds
    alles = affinity.translate(alles, -minx, -miny)
    Wt, Ht = maxx - minx, maxy - miny
    s = 1000 / Wt
    alles = affinity.scale(alles, s, s, origin=(0, 0))
    return pad(alles, Ht*s), (1000, round(Ht*s, 1))

if __name__ == '__main__' and (len(sys.argv) < 2 or sys.argv[1] != 'alles'):
    uit = {}
    for f in sys.argv[1:] or ['Kavoon-Regular.ttf']:
        d, vb = maak(f)
        uit[f] = {'d': d, 'w': vb[0], 'h': vb[1]}
    json.dump(uit, open(HIER / 'proef.json', 'w'))
    print('ok', list(uit))


def liggend(fontnaam='Kavoon-Regular.ttf', spatie_f=0.32, r_f=0.022, amp_f=0.012, woordgat=0.9):
    font = TTFont(HIER / 'fonts' / fontnaam)
    upm = font['head'].unitsPerEm
    a, wa, _ = regel(font, 'TIDE', upm*spatie_f, upm*r_f, board_i=True)
    b, wb, _ = regel(font, 'TODE', upm*spatie_f, upm*r_f)
    a0 = a.bounds; b0 = b.bounds
    b = affinity.translate(b, a0[2] + upm*woordgat - b0[0], a0[1] - b0[1])
    alles = golf(unary_union([a, b]), upm*amp_f, 2*math.pi/(upm*0.9))
    minx, miny, maxx, maxy = alles.bounds
    alles = affinity.translate(alles, -minx, -miny)
    s = 1000 / (maxx - minx)
    alles = affinity.scale(alles, s, s, origin=(0, 0))
    return pad(alles, (maxy - miny)*s), (1000, round((maxy - miny)*s, 1))


def beeldmerk(fontnaam='Kavoon-Regular.ttf'):
    font = TTFont(HIER / 'fonts' / fontnaam)
    g, _ = glyf(font, 'I')
    minx, miny, maxx, maxy = g.bounds
    bd = board((maxy - miny)*1.12, (maxx - minx)*1.05, 0, 0)
    bd = zacht(bd, 8)
    minx, miny, maxx, maxy = bd.bounds
    bd = affinity.translate(bd, -minx, -miny)
    s = 1000 / (maxy - miny)
    bd = affinity.scale(bd, s, s, origin=(0, 0))
    return pad(bd, (maxy - miny)*s), (round((maxx - minx)*s, 1), 1000)


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'alles':
    st, vb = maak('Kavoon-Regular.ttf')
    li, vbl = liggend()
    bm, vbb = beeldmerk()
    json.dump({'gestapeld': {'d': st, 'w': vb[0], 'h': vb[1]}, 'liggend': {'d': li, 'w': vbl[0], 'h': vbl[1]}, 'board': {'d': bm, 'w': vbb[0], 'h': vbb[1]}}, open(HIER / 'logo2.json', 'w'))
    print('logo2.json', vb, vbl, vbb)
