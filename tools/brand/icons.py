"""Tide-Tode iconen: handgeknipte papiervormen (zoals uit gekleurd papier geknipt).

Elke vorm wordt opgebouwd uit taps toelopende stroken, schijven en uitsnijdingen (shapely),
daarna krijgt de rand een kleine, vloeiende onregelmatigheid, zoals een schaar die nooit
precies de lijn volgt. Eén kleur (currentColor), details als uitsparing. 64-grid."""
import math, json, random
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

# ---------- bouwstenen ----------

def catmull(pts, n=12):
    """Vloeiende lijn door controlepunten."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def strook(pts, r0, r1, glad=True):
    """Taps toelopende strook langs een (vloeiende) lijn: dik begin r0, dun eind r1."""
    line = LineString(catmull(pts) if glad and len(pts) > 2 else pts)
    L = line.length
    n = max(8, int(L / 0.6))
    discs = []
    for i in range(n + 1):
        t = i / n
        p = line.interpolate(t * L)
        r = r0 + (r1 - r0) * t
        discs.append(p.buffer(max(r, 0.25), 12))
    return unary_union(discs)


def schijf(x, y, r):
    return Point(x, y).buffer(r, 32)


def ellips(x, y, rx, ry, rot=0):
    return affinity.rotate(affinity.scale(Point(x, y).buffer(1, 32), rx, ry), rot)


def kalligrafie(x0, x1, y, amp, wmax, wmin):
    """Het golfje uit het logo: dik-dun, als met een penseel."""
    N, top, bot = 60, [], []
    for i in range(N + 1):
        t = i / N
        x = x0 + (x1 - x0) * t
        yy = y - amp * math.sin(t * 2 * math.pi)
        dy = -amp * 2 * math.pi * math.cos(t * 2 * math.pi) / (x1 - x0)
        ln = math.hypot(1, dy); nx, ny = -dy / ln, 1 / ln
        w = wmin + (wmax - wmin) * math.sin(math.pi * t) ** 0.7 * (0.75 + 0.25 * math.cos(t * 2 * math.pi))
        top.append((x - nx * w / 2, yy - ny * w / 2)); bot.append((x + nx * w / 2, yy + ny * w / 2))
    return Polygon(top + bot[::-1]).buffer(0)


# ---------- de schaar: organische rand ----------

def ruis(seed):
    rnd = random.Random(seed)
    golven = [(rnd.uniform(0.25, 0.55), rnd.uniform(0, 6.28), rnd.uniform(0.6, 1.0)) for _ in range(3)]
    return lambda s: sum(a * math.sin(s * f + p) for f, p, a in golven) / 2.2


def knip_ring(coords, amp, noise, stap=1.0):
    ring = LineString(coords)
    L = ring.length
    n = max(24, int(L / stap))
    pts = [ring.interpolate(i / n * L) for i in range(n)]
    out = []
    for i in range(n):
        a, b = pts[i - 1], pts[(i + 1) % n]
        tx, ty = b.x - a.x, b.y - a.y
        ln = math.hypot(tx, ty) or 1
        nx, ny = ty / ln, -tx / ln
        d = amp * noise(i / n * L)
        out.append((pts[i].x + nx * d, pts[i].y + ny * d))
    return out


def pad_ring(pts):
    """Gesloten vloeiend pad (Catmull-Rom -> Bezier) door de punten."""
    p = pts
    n = len(p)
    f = lambda v: f"{v:.1f}".rstrip('0').rstrip('.')
    d = f"M{f(p[0][0])} {f(p[0][1])}"
    for i in range(n):
        p0, p1, p2, p3 = p[i - 1], p[i], p[(i + 1) % n], p[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d + "Z"


def knip(geom, seed, amp=0.5):
    geom = geom.buffer(0.35, 16).buffer(-0.35, 16).simplify(0.12)
    polys = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
    d = ""
    for k, poly in enumerate(polys):
        d += pad_ring(knip_ring(list(poly.exterior.coords), amp, ruis(seed + k)))
        for j, hole in enumerate(poly.interiors):
            d += pad_ring(knip_ring(list(hole.coords), amp * 0.6, ruis(seed + 50 + j)))
    return d


# ---------- de iconen ----------

def schelp():
    cx, cy, R = 32, 47, 24
    sector = Polygon([(cx, cy)] + [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(196, 345, 4)])
    schulp = unary_union([schijf(cx + (R - 0.5) * math.cos(math.radians(a)), cy + (R - 0.5) * math.sin(math.radians(a)), 3.4) for a in range(200, 341, 17)])
    scharnier = Polygon([(cx - 7, cy - 1), (cx + 7, cy - 1), (cx + 9, cy + 6), (cx + 3, cy + 5), (cx, cy + 7), (cx - 3, cy + 5), (cx - 9, cy + 6)])
    vorm = unary_union([sector, schulp, scharnier])
    ribs = unary_union([strook([(cx + 6 * math.cos(math.radians(a)), cy + 6 * math.sin(math.radians(a))), (cx + 20.5 * math.cos(math.radians(a)), cy + 20.5 * math.sin(math.radians(a)))], 0.45, 1.1, False) for a in range(208, 334, 17)])
    return vorm.difference(ribs)


def golf():
    krul = strook([(4, 50), (14, 44), (22, 32), (30, 20), (42, 12), (54, 14), (59, 24), (55, 32), (47, 32), (45, 26), (50, 23)], 8.5, 1.6)
    water = strook([(3, 52), (12, 49.5), (22, 52.5), (32, 49.5), (42, 52.5), (52, 49.5), (61, 52)], 4.2, 4.2)
    vorm = unary_union([krul, water])
    schuim = unary_union([schijf(55, 41, 1.6), schijf(59.5, 37, 1.1), schijf(50, 43, 1.0)])
    lijnen = strook([(8, 52), (17, 50), (27, 52.6), (37, 50), (47, 52.6), (56, 50.4)], 0.6, 0.6)
    binnen = strook([(16, 44), (22, 36), (28, 27)], 0.6, 1.2)
    return unary_union([vorm.difference(lijnen).difference(binnen), schuim])


def zon():
    schijf_ = schijf(32, 32, 12)
    stralen = []
    for i in range(10):
        a = i * 2 * math.pi / 10 - math.pi / 2
        pts = []
        for k in range(5):
            r = 16 + k * 3
            off = 1.4 * math.sin(k * 1.6)
            pts.append((32 + r * math.cos(a) - off * math.sin(a), 32 + r * math.sin(a) + off * math.cos(a)))
        stralen.append(strook(pts, 2.6, 1.1))
    spiraal = []
    for i in range(70):
        t = i / 69
        ang = -math.pi / 2 + t * 2 * math.pi * 1.6
        r = 1.2 + 6.6 * t
        spiraal.append((32 + r * math.cos(ang), 32 + r * math.sin(ang)))
    return unary_union([schijf_.difference(strook(spiraal, 0.7, 1.2, False))] + stralen)


def maan():
    sikkel = schijf(30, 33, 23).difference(schijf(41, 26, 19.5))
    kraters = unary_union([schijf(16, 32, 2.4), schijf(21, 45, 1.7), schijf(30, 51, 1.3)])
    return sikkel.difference(kraters)


def zeester():
    armen = []
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        bocht = 2.2 if i % 2 else -2.2
        pts = [(32, 33), (32 + 12 * math.cos(a) - bocht * math.sin(a), 33 + 12 * math.sin(a) + bocht * math.cos(a)), (32 + 25 * math.cos(a), 33 + 25 * math.sin(a))]
        armen.append(strook(pts, 7.5, 2.4))
    vorm = unary_union(armen + [schijf(32, 33, 8)])
    stip = []
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        for r, s in ((9, 1.2), (14.5, 1.0), (19.5, 0.8)):
            stip.append(schijf(32 + r * math.cos(a), 33 + r * math.sin(a), s))
    return vorm.difference(unary_union(stip + [schijf(32, 33, 1.6)]))


def koraal():
    takken = [
        strook([(32, 61), (32, 50), (31, 40), (32, 30)], 4.6, 2.6),
        strook([(31.5, 46), (25, 42), (19, 34), (17, 24)], 3.4, 1.6),
        strook([(19, 34), (12, 30), (8, 22)], 2.4, 1.3),
        strook([(17, 26), (21, 19), (20, 12)], 2.2, 1.2),
        strook([(32, 42), (39, 37), (44, 28), (45, 18)], 3.4, 1.6),
        strook([(44, 30), (51, 26), (55, 18)], 2.3, 1.2),
        strook([(45, 20), (41, 13), (42, 7)], 2.0, 1.1),
        strook([(32, 31), (30, 22), (33, 12)], 2.4, 1.2),
    ]
    knoppen = [schijf(8, 21.5, 2.2), schijf(20, 11.5, 2.0), schijf(55.5, 17.5, 2.0), schijf(42, 6.5, 1.9), schijf(33, 11.5, 2.1)]
    return unary_union(takken + knoppen)


def palmblad():
    nerf = [(13, 58), (20, 46), (30, 32), (42, 18), (52, 8)]
    vorm = [strook(nerf, 2.8, 0.9)]
    line = LineString(catmull(nerf))
    for i in range(1, 9):
        t = i / 9.5
        p = line.interpolate(t * line.length)
        q = line.interpolate(min(1, t + 0.02) * line.length)
        ang = math.atan2(q.y - p.y, q.x - p.x)
        L = 15 * (1 - t) + 4
        for kant in (-1, 1):
            a = ang + kant * 1.05
            e = (p.x + L * math.cos(a), p.y + L * math.sin(a))
            m = (p.x + L * .55 * math.cos(a) + kant * 1.6 * math.cos(ang), p.y + L * .55 * math.sin(a) + kant * 1.6 * math.sin(ang))
            vorm.append(strook([(p.x, p.y), m, e], 2.4, 0.8))
    return unary_union(vorm)


def meeuw():
    links = strook([(32, 31), (24, 22), (14, 21), (5, 27)], 3.6, 0.6)
    rechts = strook([(32, 31), (40, 21), (51, 19), (60, 24)], 3.6, 0.6)
    lijf = ellips(32, 32, 4, 2.6, 0)
    return unary_union([links, rechts, lijf])


def boardvorm(cx=32, cy=32, L=64, W=17, rot=-45):
    pts_top, pts_bot = [], []
    for i in range(61):
        t = i / 60
        x = -L / 2 + L * t
        prof = math.sin(math.pi * min(1, t * 1.05)) ** 0.6 * (1 - 0.3 * t ** 3)
        pts_top.append((x, -W / 2 * prof)); pts_bot.append((x, W / 2 * prof))
    vorm = Polygon(pts_top + pts_bot[::-1]).buffer(0)
    vorm = affinity.translate(affinity.rotate(vorm, rot, origin=(0, 0)), cx, cy)
    return vorm


def board():
    vorm = boardvorm()
    a = math.radians(-45)
    T = lambda x, y: (32 + x * math.cos(a) - y * math.sin(a), 32 + x * math.sin(a) + y * math.cos(a))
    snedes = [strook([T(-24, 0), T(27, 0)], 0.5, 0.5, False)]
    return vorm.difference(unary_union(snedes))


def tas():
    vorm = boardvorm(31, 40, 60, 16, -32)
    a = math.radians(-32)
    T = lambda x, y: (31 + x * math.cos(a) - y * math.sin(a), 40 + x * math.sin(a) + y * math.cos(a))
    band = strook([T(-14, -5), T(-17, -19), T(-4, -29), T(12, -22), T(12, -5)], 2.6, 2.6)
    paneel = strook([T(-8, 0), T(8, 0)], 0.6, 0.6, False)  # naad van het tegelpaneel
    return unary_union([vorm.difference(paneel.buffer(0)), band])


def wax():
    blok = box(11, 17, 53, 49).buffer(5, 16).buffer(-2, 16)
    golfje = kalligrafie(19, 45, 33, 3.6, 3.2, 0.9)
    korrels = unary_union([schijf(20, 23, 0.9), schijf(44, 24, 0.8), schijf(25, 43, 0.8), schijf(41, 42, 0.9), schijf(32, 41.5, 0.7)])
    return blok.difference(golfje).difference(korrels)


def karabijn():
    pts = []
    for i in range(41):
        t = i / 40 * math.pi
        pts.append((32 + 9 * math.cos(math.pi + t), 18 - 9 * math.sin(t) * -1 * -1))
    ring = LineString([(23, 18), (23, 46)]).buffer(0)
    stad = Point(0, 0).buffer(1, 64)
    stad = affinity.scale(stad, 15, 26)
    stad = affinity.translate(stad, 32, 32)
    binnen = affinity.scale(Point(0, 0).buffer(1, 64), 9, 20)
    binnen = affinity.translate(binnen, 32, 32)
    vorm = stad.difference(binnen)
    vorm = vorm.difference(box(40, 14, 48, 32))  # opening voor de snapper
    snapper = strook([(44.5, 10), (43.2, 22), (43.4, 35)], 2.6, 2.6, False)
    slot = box(39.6, 33, 47.6, 45).buffer(1)
    ribbels = unary_union([strook([(39.8, y), (47.4, y)], 0.45, 0.45, False) for y in (36, 39, 42)])
    return unary_union([vorm, snapper, slot.difference(ribbels)])


def golfjes():
    return unary_union([kalligrafie(9, 55, 20, 4.4, 6.6, 1.6), kalligrafie(6, 58, 32, 4.8, 7.4, 1.8), kalligrafie(11, 53, 44, 4.4, 6.6, 1.6)])


def tij():
    pts = []
    for i in range(140):
        t = i / 139
        ang = -math.pi / 2 + t * 2 * math.pi * 2.3
        r = 2 + 21 * t
        pts.append((32 + r * math.cos(ang), 32 + r * math.sin(ang)))
    return strook(pts, 1.6, 4.2, False)


def voeten():
    def voet(x, y, rot, flip):
        zool = unary_union([ellips(0, 4, 4.6, 7.6), ellips(0, -3, 5.4, 6.4)])
        tenen = [schijf(-4.2 * flip, -11.5, 1.9), schijf(-1.3 * flip, -13, 1.75), schijf(1.4 * flip, -12.6, 1.55), schijf(3.6 * flip, -11.3, 1.35), schijf(5.2 * flip, -9.2, 1.15)]
        v = unary_union([zool] + tenen)
        return affinity.translate(affinity.rotate(v, rot, origin=(0, 0)), x, y)
    return unary_union([voet(21, 42, -14, 1), voet(42, 24, 12, -1)])


ICONEN = [
    ('golf', 'Golf', golf), ('schelp', 'Schelp', schelp), ('zon', 'Zon', zon), ('maan', 'Maan', maan),
    ('zeester', 'Zeester', zeester), ('koraal', 'Koraal', koraal), ('palmblad', 'Palmblad', palmblad), ('meeuw', 'Meeuw', meeuw),
    ('board', 'Board', board), ('tas', 'De tas', tas), ('wax', 'Wax', wax), ('karabijn', 'Karabijnhaak', karabijn),
    ('golfjes', 'Getij', golfjes), ('tij', 'Spiraal', tij), ('voeten', 'Onderweg', voeten),
]


def build():
    symbols, namen = [], []
    for i, (key, naam, fn) in enumerate(ICONEN):
        d = knip(fn(), seed=11 + i * 7, amp=0.55)
        symbols.append(f'<symbol id="i-{key}" viewBox="0 0 64 64"><path d="{d}" fill="currentColor" fill-rule="evenodd"/></symbol>')
        namen.append([key, naam])
    # los golfje (het teken uit de naam), zonder knipruis: dit is logo, geen icoon
    g = kalligrafie(4, 60, 32, 6.2, 9.5, 2.2).simplify(0.05)
    golfje = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in g.exterior.coords) + "Z"
    symbols.append(f'<symbol id="golfje" viewBox="0 20 64 24"><path d="{golfje}" fill="currentColor"/></symbol>')
    return {'symbols': "\n    ".join(symbols), 'namen': namen}


if __name__ == '__main__':
    print(json.dumps(build()))
