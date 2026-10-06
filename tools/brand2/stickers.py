"""Tide-Tode stickers (branding 2): eigen illustraties als gevulde vorm met
lichte binnenlijnen en een stickerrand eromheen. Onderwerpen uit Veerles
wereld: board met tas, schelp, zeester, golf, zon, palm, busje en wax.
Uitvoer: uit/sticker-*.svg en stickers.json."""
import json, math, random, pathlib
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
from illustraties import lijn, board_omtrek, rot

HIER = pathlib.Path(__file__).parent
random.seed(11)

NAVY, BABY, ROSE, CREME, ZAND, PAPIER = '#22324F', '#BFD3EA', '#EDBDB8', '#F3ECDD', '#E3CFAE', '#FBF7EF'


def pad(g):
    def ring(c):
        c = list(c)
        return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in c[:-1]) + 'Z'
    out = []
    for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
        out.append(ring(p.exterior.coords) + ''.join(ring(i.coords) for i in p.interiors))
    return ''.join(out)


def zacht(g, r):
    return g.buffer(r, join_style=1).buffer(-r, join_style=1)


def sticker(naam, vorm, lijnen, vul, lijnkleur, rand=11):
    vorm = zacht(vorm, 3).simplify(0.35)
    randvorm = zacht(vorm.buffer(rand, join_style=1), 6).simplify(0.5)
    minx, miny, maxx, maxy = randvorm.bounds
    m = 6
    vb = f'{minx - m:.0f} {miny - m:.0f} {maxx - minx + 2 * m:.0f} {maxy - miny + 2 * m:.0f}'
    return {'naam': naam, 'vb': vb, 'rand': pad(randvorm), 'vorm': pad(vorm), 'lijnen': lijnen, 'vul': vul, 'lijn': lijnkleur}


S = []

# 1. Board met de tas: het product
c = (200, 200)
bo = Polygon(board_omtrek(200, 200, 300, 78, 35))
lus = LineString([rot((236, 140), c, 35), rot((300, 175), c, 35), rot((300, 238), c, 35), rot((236, 262), c, 35)]).buffer(9, cap_style=1)
vorm = unary_union([bo, lus.difference(bo.buffer(-2))])
lj = [lijn([rot((200, 66), c, 35), rot((200, 330), c, 35)], 0.4)]
for t in (-58, 52):
    lj.append(lijn([rot((158, 200 + t), c, 35), rot((242, 200 + t), c, 35)], 0.3))
    lj.append(lijn([rot((158, 200 + t + 14), c, 35), rot((242, 200 + t + 14), c, 35)], 0.3))
S.append(sticker('board', vorm, lj, NAVY, CREME))

# 2. Schelp
pts = []
for i in range(0, 181):
    a = math.radians(200 + i * 140 / 180)
    r = 120 + 7 * math.cos(i / 180 * math.pi * 18)
    pts.append((200 + r * math.cos(a), 230 + r * math.sin(a)))
waaier = Polygon([(200, 250)] + pts)
oor = Polygon([(170, 240), (230, 240), (250, 268), (150, 268)])
vorm = unary_union([waaier.buffer(4), oor])
lj = []
for i in range(1, 9):
    a = math.radians(200 + i * 140 / 9)
    lj.append(lijn([(200, 246), (200 + 70 * math.cos(a), 230 + 70 * math.sin(a)), (200 + 112 * math.cos(a), 230 + 112 * math.sin(a))], 0.5))
lj.append(lijn([(160, 258), (240, 258)], 0.3))
S.append(sticker('schelp', vorm, lj, ROSE, NAVY))

# 3. Zeester
ster = []
for i in range(10):
    a = math.radians(-90 + i * 36)
    r = 130 if i % 2 == 0 else 52
    ster.append((200 + r * math.cos(a), 200 + r * math.sin(a)))
vorm = zacht(Polygon(ster), 14).buffer(4)
lj = []
for i in range(5):
    a = math.radians(-90 + i * 72)
    lj.append(lijn([(200, 200), (200 + 100 * math.cos(a), 200 + 100 * math.sin(a))], 0.4))
    for k in (40, 62, 84):
        x, y = 200 + k * math.cos(a), 200 + k * math.sin(a)
        lj.append(lijn([(x + 8 * math.cos(a + 1.57), y + 8 * math.sin(a + 1.57)), (x + 9 * math.cos(a + 1.57) + 1, y + 9 * math.sin(a + 1.57) + 1)], 0.1))
        lj.append(lijn([(x - 8 * math.cos(a + 1.57), y - 8 * math.sin(a + 1.57)), (x - 9 * math.cos(a + 1.57) + 1, y - 9 * math.sin(a + 1.57) + 1)], 0.1))
S.append(sticker('zeester', vorm, lj, CREME, NAVY))

# 4. Golf: een volle golf met een krul, de voorkant loopt door tot onderaan
vorm = Polygon([(30, 320), (30, 298), (110, 290), (180, 260), (232, 210), (272, 160), (312, 124), (356, 110), (394, 130), (408, 170),
                (394, 204), (364, 216), (342, 200), (346, 178), (364, 170), (352, 156), (326, 166), (308, 198), (298, 240), (298, 290), (312, 320)]).buffer(0)
vorm = zacht(vorm, 10)
lj = [lijn([(70, 306), (150, 298), (210, 268), (252, 222), (288, 178), (322, 150)], 0.5),
      lijn([(120, 312), (190, 302), (240, 270), (274, 232)], 0.4),
      lijn([(352, 132), (384, 142), (392, 172), (376, 196)], 0.4)]
S.append(sticker('golf', vorm, lj, BABY, NAVY))

# 5. Zon
stralen = [Polygon([(200 + 74 * math.cos(math.radians(a - 9)), 200 + 74 * math.sin(math.radians(a - 9))),
                    (200 + 132 * math.cos(math.radians(a)), 200 + 132 * math.sin(math.radians(a))),
                    (200 + 74 * math.cos(math.radians(a + 9)), 200 + 74 * math.sin(math.radians(a + 9)))]) for a in range(0, 360, 30)]
vorm = zacht(unary_union([Point(200, 200).buffer(84)] + stralen), 6)
lj = [lijn([(200 + 58 * math.cos(math.radians(a)), 200 + 58 * math.sin(math.radians(a))) for a in range(0, 361, 15)], 0.4)]
S.append(sticker('zon', vorm, lj, ZAND, NAVY))

# 6. Palm
stam = LineString([(196, 360), (204, 300), (212, 240), (214, 180)]).buffer(13, cap_style=1)
bladeren = []
lj = []
for hoek, lengte in ((-160, 120), (-130, 110), (-95, 100), (-60, 112), (-25, 120), (15, 95), (-195, 92)):
    a = math.radians(hoek)
    tip = (214 + lengte * math.cos(a), 176 + lengte * math.sin(a) + 30 * abs(math.cos(a)))
    mid = (214 + lengte * 0.55 * math.cos(a), 176 + lengte * 0.55 * math.sin(a) - 6)
    blad = LineString([(214, 176), mid, tip]).buffer(16, cap_style=1)
    bladeren.append(blad)
    lj.append(lijn([(214, 176), mid, tip], 0.4))
vorm = unary_union([stam] + bladeren)
for y in (340, 310, 280, 250, 220):
    lj.append(lijn([(194 + (360 - y) * 0.06, y), (214 + (360 - y) * 0.06, y - 3)], 0.2))
S.append(sticker('palm', vorm, lj, NAVY, CREME))

# 7. Busje met board op het dak
romp = box(60, 150, 340, 270)
neus = Polygon([(60, 150), (90, 118), (310, 116), (340, 150)])
dak = Polygon(board_omtrek(200, 88, 300, 44, 90))
drager = unary_union([box(110, 100, 120, 118), box(280, 100, 290, 118)])
wielen = unary_union([Point(115, 272).buffer(28), Point(285, 272).buffer(28)])
vorm = unary_union([romp, neus, dak, drager, wielen])
vorm = zacht(vorm, 10)
lj = [lijn([(84, 136), (140, 134), (140, 182), (76, 184)], 0.4), lijn([(162, 134), (226, 133), (226, 182), (162, 183)], 0.4),
      lijn([(248, 133), (304, 132), (318, 150), (318, 182), (248, 183)], 0.4), lijn([(62, 206), (338, 205)], 0.4), lijn([(66, 88), (334, 88)], 0.3),
      lijn([(115 + 13 * math.cos(math.radians(a)), 272 + 13 * math.sin(math.radians(a))) for a in range(0, 361, 20)], 0.2),
      lijn([(285 + 13 * math.cos(math.radians(a)), 272 + 13 * math.sin(math.radians(a))) for a in range(0, 361, 20)], 0.2)]
S.append(sticker('busje', vorm, lj, ROSE, NAVY))

# 8. Blokje wax
blok = Polygon([(110, 140), (290, 120), (310, 270), (130, 290)])
vorm = zacht(blok, 16)
lj = [lijn([(150, 175), (270, 162)], 0.3), lijn([(160, 255), (285, 242)], 0.3)]
S.append(sticker('wax', vorm, lj, BABY, NAVY))

for s in S:
    s['tekst'] = 'SURF WAX' if s['naam'] == 'wax' else ''


def svg(s, randkleur=PAPIER, schaduw=True):
    lijnen = ''.join(f'<path d="{d}"/>' for d in s['lijnen'])
    tekst = ''
    if s['tekst']:
        tekst = f'<text x="210" y="216" text-anchor="middle" transform="rotate(-6 210 205)" font-family="Courier Prime, Courier, monospace" font-weight="700" font-size="30" letter-spacing="4" fill="{s["lijn"]}">{s["tekst"]}</text>'
    sch = f'<path d="{s["rand"]}" fill="#000" opacity=".16" transform="translate(3 5)"/>' if schaduw else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{s["vb"]}">{sch}<path d="{s["rand"]}" fill="{randkleur}"/>'
            f'<path d="{s["vorm"]}" fill="{s["vul"]}"/><g fill="none" stroke="{s["lijn"]}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">{lijnen}</g>{tekst}</svg>')


if __name__ == '__main__':
    (HIER / 'uit').mkdir(exist_ok=True)
    for s in S:
        (HIER / 'uit' / f'sticker-{s["naam"]}.svg').write_text(svg(s))
    json.dump(S, open(HIER / 'stickers.json', 'w'))
    print('stickers:', ', '.join(s['naam'] for s in S))
