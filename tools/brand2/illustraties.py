"""Handgetekende lijnillustraties voor Tide-Tode (branding 2).
Eén lijndikte, ronde uiteinden, een klein beetje trilling zodat het
er met de hand getekend uitziet. Uitvoer: SVG-bestanden + JSON met paden."""
import json, math, random, pathlib

HIER = pathlib.Path(__file__).parent
random.seed(7)


def ruis(n, schaal):
    """vloeiende ruis: een paar sinussen met willekeurige fase"""
    f = [(random.uniform(0.6, 1.6), random.uniform(0, 6.28), random.uniform(0.4, 1)) for _ in range(3)]
    return [schaal * sum(a * math.sin(i / max(n - 1, 1) * math.pi * 2 * k + p) for k, p, a in f) / 2 for i in range(n)]


def glad(pts, stappen=8):
    """Catmull-Rom door de punten"""
    if len(pts) < 3:
        return pts
    uit = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for s in range(stappen):
            t = s / stappen
            t2, t3 = t * t, t * t * t
            uit.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    uit.append(pts[-1])
    return uit


def lijn(pts, beef=0.9, gesloten=False, stappen=8):
    pts = glad(pts + ([pts[0]] if gesloten else []), stappen)
    n = len(pts)
    rx, ry = ruis(n, beef), ruis(n, beef)
    q = [(x + rx[i], y + ry[i]) for i, (x, y) in enumerate(pts)]
    return 'M' + ' '.join(f'{x:.1f} {y:.1f}' for x, y in q)


def boog(cx, cy, r, a0, a1, n=24, rx=None):
    rx = rx or r
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def board_omtrek(cx, cy, lengte, breedte, hoek):
    """surfboard-omtrek rond (cx, cy), neus in richting 'hoek' (graden, 0 = omhoog)"""
    pts = []
    for i in range(0, 41):
        t = i / 40
        b = breedte / 2 * (max(0, 1 - t) ** 0.55) * ((t + 0.18) ** 0.42) / 0.62
        pts.append((b, lengte * (0.5 - t)))
    rechts = pts
    links = [(-x, y) for x, y in reversed(pts)]
    a = math.radians(hoek)
    rot = lambda x, y: (cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a))
    return [rot(x, y) for x, y in rechts + links[1:]]


def rot(p, c, hoek):
    a = math.radians(hoek)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


TEKENINGEN = {}

# 1. Parasol met een surfboard in het zand (zoals de parasol en strandstoel bij ELARA)
d = []
cx, top = 170, 40
d.append(lijn(boog(cx, 106, 70, 180, 360, 30, rx=99)))                               # doek: halve ellips
for i in range(8):                                                                  # schulprand
    x0 = cx - 99 + i * 24.75
    d.append(lijn([(x0, 106), (x0 + 6, 116), (x0 + 12.4, 118), (x0 + 19, 116), (x0 + 24.75, 106)], 0.5, stappen=5))
for i in range(1, 8):                                                               # baleinen over het doek
    x = cx - 99 + i * 24.75
    xm = cx + (x - cx) * 0.6
    ym = 106 - 70 * math.sqrt(max(0, 1 - ((xm - cx) / 99) ** 2)) * 0.96
    d.append(lijn([(cx, 36), (xm, ym), (x, 106)], 0.5))
d.append(lijn([(cx - 4, 36), (cx, 27), (cx + 4, 36)], 0.3))       # knopje
d.append(lijn([(cx + 2, 112), (cx + 6, 200), (cx + 9, 278)], 0.6))                 # stok
bo = board_omtrek(270, 190, 190, 58, 8)
d.append(lijn(bo, 0.7, gesloten=True, stappen=3))
d.append(lijn([rot((270, 120), (270, 190), 8), rot((270, 262), (270, 190), 8)], 0.5))  # stringer
for x0 in (60, 110, 200, 300, 340):                                                 # zandstreepjes
    d.append(lijn([(x0, 286), (x0 + 22, 284)], 0.4))
d.append(lijn([(30, 280), (370, 279)], 1.0))
TEKENINGEN['parasol'] = {'vb': '0 0 400 300', 'd': d}


# 3. Golf
d = []
d.append(lijn([(30, 230), (90, 226), (150, 200), (200, 150), (250, 110), (300, 104), (335, 128), (338, 160), (316, 176), (296, 168), (292, 150), (306, 140)], 0.9))
d.append(lijn([(60, 238), (130, 230), (190, 196), (230, 160), (270, 136), (300, 136)], 0.7))
d.append(lijn([(110, 246), (170, 236), (220, 210), (262, 186)], 0.6))
d.append(lijn([(20, 262), (380, 258)], 1.0))
d.append(lijn([(40, 276), (120, 274)], 0.5)); d.append(lijn([(200, 276), (330, 273)], 0.5))
TEKENINGEN['golf'] = {'vb': '0 0 400 300', 'd': d}

# 4. Zon boven zee
d = []
d.append(lijn(boog(200, 190, 62, 180, 360, 30), 0.7))
for i in range(9):
    hk = 180 + i * 22.5
    p1 = (200 + 78 * math.cos(math.radians(hk)), 190 + 78 * math.sin(math.radians(hk)))
    p2 = (200 + 104 * math.cos(math.radians(hk)), 190 + 104 * math.sin(math.radians(hk)))
    d.append(lijn([p1, p2], 0.4))
d.append(lijn([(30, 192), (370, 190)], 1.0))
for y, x0, x1 in ((214, 120, 280), (234, 150, 250), (252, 175, 225)):
    d.append(lijn([(x0, y), (x1, y + 1)], 0.5))
TEKENINGEN['zon'] = {'vb': '0 0 400 300', 'd': d}

# 5. Busje met board op het dak
d = []
d.append(lijn([(70, 230), (70, 150), (90, 120), (300, 118), (330, 150), (334, 230), (300, 232)], 0.8))
d.append(lijn([(250, 232), (150, 232)], 0.6)); d.append(lijn([(108, 232), (80, 231)], 0.5))
d.append(lijn(boog(129, 232, 21, 0, 360, 24), 0.5)); d.append(lijn(boog(275, 232, 21, 0, 360, 24), 0.5))
d.append(lijn([(96, 132), (150, 130), (150, 175), (84, 176)], 0.5))
d.append(lijn([(170, 130), (230, 129), (230, 175), (170, 176)], 0.5))
d.append(lijn([(250, 129), (304, 128), (318, 150), (318, 175), (250, 176)], 0.5))
d.append(lijn([(70, 195), (334, 194)], 0.6))
bo = board_omtrek(205, 104, 250, 34, 90)
d.append(lijn(bo, 0.6, gesloten=True, stappen=3))
d.append(lijn([(120, 116), (122, 108)], 0.3)); d.append(lijn([(290, 116), (288, 108)], 0.3))
TEKENINGEN['busje'] = {'vb': '0 0 400 300', 'd': d}


def svg(naam, kleur='#22324F', dikte=3.2):
    t = TEKENINGEN[naam]
    paden = ''.join(f'<path d="{p}"/>' for p in t['d'])
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{t["vb"]}" fill="none" stroke="{kleur}" stroke-width="{dikte}" stroke-linecap="round" stroke-linejoin="round">{paden}</svg>'


if __name__ == '__main__':
    (HIER / 'uit').mkdir(exist_ok=True)
    for n in TEKENINGEN:
        (HIER / 'uit' / f'illustratie-{n}.svg').write_text(svg(n))
    json.dump({n: {'vb': t['vb'], 'd': t['d']} for n, t in TEKENINGEN.items()}, open(HIER / 'illustraties.json', 'w'))
    print('illustraties:', ', '.join(TEKENINGEN))
