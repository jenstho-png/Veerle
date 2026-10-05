"""Drie extra logorichtingen voor Tide-Tode, elk met eigen beeldmerk en lettertype.

B  Handen vrij        board met draagbanden      Archivo Expanded ExtraBold
C  De weg naar de spot voetstappen die een golf worden   Caprasimo
D  Het golfje         het teken uit de naam      Gilda Display

Letters worden met fontTools omgezet naar vectorpaden; beeldmerken met shapely opgebouwd.
Schrijft richtingen.json met per richting de paden voor alle logoversies."""
import json, math, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity
import icons as ic  # strook, schijf, ellips, kalligrafie, knip, boardvorm

HIER = pathlib.Path(__file__).parent
FONTS = HIER / 'fonts'


class Letter:
    def __init__(self, bestand):
        self.f = TTFont(FONTS / bestand)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f['head'].unitsPerEm
        os2 = self.f['OS/2']
        self.cap = getattr(os2, 'sCapHeight', 0) or self.upm * 0.7

    def glyph(self, ch):
        return self.cmap.get(ord(ch), self.cmap.get(ord('?')))

    def adv(self, ch, size):
        return self.f['hmtx'][self.glyph(ch)][0] / self.upm * size

    def run(self, tekst, size, tracking=0.0):
        x, out = 0.0, []
        for ch in tekst:
            out.append((ch, x))
            x += self.adv(ch, size) + tracking * size
        return out, x - tracking * size

    def pad(self, tekst, size, x0=0.0, y0=0.0, tracking=0.0):
        """Tekst als SVG-pad, basislijn op y0. Geeft (d, breedte)."""
        run, w = self.run(tekst, size, tracking)
        s = size / self.upm
        d = ''
        for ch, x in run:
            pen = SVGPathPen(self.gs, lambda v: f"{v:.1f}")
            self.gs[self.glyph(ch)].draw(TransformPen(pen, (s, 0, 0, -s, x0 + x, y0)))
            d += pen.getCommands()
        return d, w

    def boog(self, tekst, size, r, boven=True, tracking=0.1, cx=100, cy=100):
        """Tekst langs een cirkel (boven: leesbaar van buiten, onder: leesbaar van binnen)."""
        run, w = self.run(tekst, size, tracking)
        span = w / r
        s = size / self.upm
        d = ''
        for ch, x in run:
            a = self.adv(ch, size)
            mid = x + a / 2
            th = (-span / 2 + mid / r) if boven else (span / 2 - mid / r)
            c, n = math.cos(th), math.sin(th)
            ry = -r if boven else r + self.cap / self.upm * size
            # glyph rond (−a/2, 0), dan naar de cirkel en draaien
            m = (s * c, s * n, s * n, -s * c, cx + (-a / 2) * c - ry * n, cy + (-a / 2) * n + ry * c)
            pen = SVGPathPen(self.gs, lambda v: f"{v:.1f}")
            self.gs[self.glyph(ch)].draw(TransformPen(pen, m))
            d += pen.getCommands()
        return d


def schoon(geom):
    """Strak pad zonder knipruis (voor de strakke richtingen)."""
    geom = geom.buffer(0.2, 16).buffer(-0.2, 16).simplify(0.06)
    polys = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
    d = ''
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            d += 'M' + 'L'.join(f"{x:.1f} {y:.1f}" for x, y in list(ring.coords)[:-1]) + 'Z'
    return d


def vb(x, y, w, h):
    return f"{x:.1f} {y:.1f} {w:.1f} {h:.1f}"


out = {}

# ===================== B · HANDEN VRIJ =====================
arch = Letter('archivo-expanded-800.ttf')
inter = Letter('inter-600.ttf')


def board_met_banden(schaal=1.0):
    """Board schuin omhoog, twee draagbanden (uitgespaard) en een schouderband erover."""
    rot = -58
    vorm = ic.boardvorm(50, 52, 84, 26, rot)
    a = math.radians(rot)
    T = lambda x, y: (50 + x * math.cos(a) - y * math.sin(a), 52 + x * math.sin(a) + y * math.cos(a))
    gaten = []
    for bx in (-16, 14):
        for dx in (-5.2, 5.2):
            gaten.append(ic.strook([T(bx + dx, -16), T(bx + dx, 16)], 1.2, 1.2, False))
    stringer = ic.strook([T(-34, 0), T(-22, 0)], 0.9, 0.9, False)
    board = vorm.difference(unary_union(gaten + [stringer]))
    band = ic.strook([T(-16, 13), T(-18, 30), T(-4, 42), T(12, 34), T(14, 13)], 3.6, 3.6)
    band = band.difference(vorm.buffer(2.2))
    return unary_union([board, band])


b_merk = schoon(board_met_banden())
b_woord, b_w = arch.pad('TIDE-TODE', 100, 0, 0, 0.01)
b_cap = arch.cap / arch.upm * 100
b_tag, b_tw = inter.pad('HANDEN VRIJ', 100, 0, 0, 0.32)
i_cap = inter.cap / inter.upm * 100
# monogram: TT als ligatuur, één doorlopende band als dwarsbalk (zoals de draagband)
_bar = box(4, 6, 96, 26).buffer(4, 16).buffer(-2, 16)
_stem = lambda x: box(x - 9, 18, x + 9, 92).buffer(1.5, 8)
b_tt = schoon(unary_union([_bar, _stem(27), _stem(73)]))
b_ttw = 100
out['B'] = {
    'naam': 'Handen vrij', 'font': 'Archivo Expanded ExtraBold', 'fontBestand': 'archivo-expanded-800.ttf',
    'merk': b_merk, 'merkVB': '0 0 100 100',
    'woord': b_woord, 'woordVB': vb(-4, -b_cap - 6, b_w + 8, b_cap + 12),
    'tag': b_tag, 'tagVB': vb(-2, -i_cap - 4, b_tw + 4, i_cap + 8),
    'mono': b_tt, 'monoVB': '0 0 100 100',
    'zegelBoven': arch.boog('TIDE-TODE', 15, 74, True, 0.12),
    'zegelOnder': inter.boog('HANDEN VRIJ · SURF CARRY', 8.4, 76, False, 0.28),
}

# ===================== C · DE WEG NAAR DE SPOT =====================
cap_ = Letter('caprasimo.ttf')


def voetstap(x, y, rot, flip, s=1.0):
    zool = unary_union([ic.ellips(0, 4, 4.6, 7.6), ic.ellips(0, -3, 5.4, 6.4)])
    tenen = [ic.schijf(-4.2 * flip, -11.5, 1.9), ic.schijf(-1.3 * flip, -13, 1.75), ic.schijf(1.4 * flip, -12.6, 1.55), ic.schijf(3.6 * flip, -11.3, 1.35), ic.schijf(5.2 * flip, -9.2, 1.15)]
    v = affinity.scale(unary_union([zool] + tenen), s, s, origin=(0, 0))
    return affinity.translate(affinity.rotate(v, rot, origin=(0, 0)), x, y)


def de_weg():
    """Voetstappen die om en om schuin omhoog lopen, naar een krullende golf."""
    stappen = []
    x0, y0, x1, y1 = 13, 90, 47, 50
    ux, uy = (x1 - x0), (y1 - y0)
    L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    for i, t in enumerate((0.0, 0.42, 0.84)):
        kant = -1 if i % 2 == 0 else 1
        x = x0 + (x1 - x0) * t + kant * 6.5 * -uy
        y = y0 + (y1 - y0) * t + kant * 6.5 * ux
        stappen.append(voetstap(x, y, 40, kant, 0.68))
    golf = affinity.translate(affinity.scale(ic.golf(), 0.6, 0.6, origin=(0, 0)), 50, 3)
    return unary_union(stappen + [golf])


c_merk = ic.knip(de_weg(), seed=303, amp=0.7)
c_woord, c_w = cap_.pad('Tide-Tode', 100, 0, 0, 0.0)
c_cap = cap_.cap / cap_.upm * 100
c_tag, c_tw = inter.pad('VAN DE HIKE NAAR DE GOLF', 100, 0, 0, 0.26)
c_voet = ic.knip(voetstap(50, 54, 18, 1, 2.6), seed=313, amp=0.9)
out['C'] = {
    'naam': 'De weg naar de spot', 'font': 'Caprasimo', 'fontBestand': 'caprasimo.ttf',
    'merk': c_merk, 'merkVB': '0 0 100 100',
    'woord': c_woord, 'woordVB': vb(-4, -c_cap * 1.32 - 4, c_w + 8, c_cap * 1.32 + 30),
    'tag': c_tag, 'tagVB': vb(-2, -i_cap - 4, c_tw + 4, i_cap + 8),
    'mono': c_voet, 'monoVB': '0 0 100 100',
    'zegelBoven': cap_.boog('Tide-Tode', 19, 72, True, 0.04),
    'zegelOnder': inter.boog('VAN DE HIKE NAAR DE GOLF', 7.6, 76, False, 0.26),
}

# ===================== D · HET GOLFJE =====================
gilda = Letter('gilda-display.ttf')
g_cap = gilda.cap / gilda.upm * 100


def golfje(x0, x1, y, amp, wmax, wmin):
    return ic.kalligrafie(x0, x1, y, amp, wmax, wmin)


d_merk = schoon(golfje(8, 92, 50, 11, 15, 3.4))
# woordmerk: TIDE  ~  TODE met ruime spatiëring en een getekend golfje in het midden
t1, w1 = gilda.pad('TIDE', 100, 0, 0, 0.16)
gap = 22
gx0, gx1 = w1 + gap, w1 + gap + 58
gd = schoon(golfje(gx0, gx1, -g_cap * 0.5, 7.5, 7.4, 1.4))
t2, w2 = gilda.pad('TODE', 100, gx1 + gap, 0, 0.16)
d_w = gx1 + gap + w2
d_tag, d_tw = inter.pad('DRAAGTASSEN VOOR SURFERS', 100, 0, 0, 0.3)
# monogram: T~T
m1, mw1 = gilda.pad('T', 100, 0, 0)
mg = schoon(golfje(mw1 + 6, mw1 + 46, -g_cap * 0.5, 6.5, 6.6, 1.3))
m2, mw2 = gilda.pad('T', 100, mw1 + 52, 0)
out['D'] = {
    'naam': 'Het golfje', 'font': 'Gilda Display', 'fontBestand': 'gilda-display.ttf',
    'merk': d_merk, 'merkVB': '0 26 100 48',
    'woord': t1 + gd + t2, 'woordVB': vb(-6, -g_cap - 10, d_w + 12, g_cap + 20),
    'tag': d_tag, 'tagVB': vb(-2, -i_cap - 4, d_tw + 4, i_cap + 8),
    'mono': m1 + mg + m2, 'monoVB': vb(-6, -g_cap - 10, mw1 + 52 + mw2 + 12, g_cap + 20),
    'zegelBoven': gilda.boog('TIDE  ·  TODE', 15, 74, True, 0.3),
    'zegelOnder': inter.boog('DRAAGTASSEN VOOR SURFERS', 7.6, 76, False, 0.3),
}

if __name__ == '__main__':
    (HIER / 'richtingen.json').write_text(json.dumps(out))
    for k, v in out.items():
        print(k, v['naam'], 'woordVB', v['woordVB'], 'monoVB', v['monoVB'], len(json.dumps(v)) // 1024, 'KB')
