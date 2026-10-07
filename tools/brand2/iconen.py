"""Nieuwe icoonvoorstellen in de stijl van het woordmerk: dikke, ronde, gevulde vormen.
Schrijft iconen.json met per voorstel een svg-pad (viewBox 0 0 400 400)."""
import json, math, pathlib
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
from woordmerk import board

HIER = pathlib.Path(__file__).parent


def zacht(g, r=10):
    return g.buffer(r, join_style=1).buffer(-2 * r, join_style=1).buffer(r, join_style=1)


def pad(g):
    def ring(c):
        c = list(c)
        return 'M' + 'L'.join(f'{x:.1f} {400 - y:.1f}' for x, y in c[:-1]) + 'Z'
    out = ''
    for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
        out += ring(p.exterior.coords) + ''.join(ring(i.coords) for i in p.interiors)
    return out


def krul(cx, cy, schaal, dikte, staart=1.0):
    """Een dikke golf met krul: staart van links, omhoog, en dan naar binnen draaien."""
    pts = []
    for i in range(41):  # staart
        t = i / 40
        x = -1.6 * staart + 1.6 * staart * t
        y = -0.55 + 0.55 * (0.5 - 0.5 * math.cos(math.pi * t))
        pts.append((x, y))
    c = (0.0, 0.42)
    for i in range(1, 91):  # spiraal: begint onder het middelpunt, draait tegen de klok in naar binnen
        t = i / 90
        hoek = -math.pi / 2 + t * 1.12 * 2 * math.pi
        r = 0.42 * (1 - 0.5 * t)
        pts.append((c[0] + r * math.cos(hoek), c[1] + r * math.sin(hoek)))
    lijn = LineString([(cx + x * schaal, cy + y * schaal) for x, y in pts])
    return lijn.buffer(dikte, cap_style=1, join_style=1)


V = {}

# 1. Board met een golf erdoorheen uitgespaard (één vorm, golf als witte lijn)
b = board(330, 120, 200, 35)
g = unary_union([LineString([(60 + i * 2.8, 150 + 36 * k + 14 * math.sin(i / 100 * 2 * math.pi * 1.5)) for i in range(101)]).buffer(8, cap_style=1) for k in range(2)])
V['board-golf'] = zacht(b.difference(g), 4)

# 3. Zon boven zee met board: rond embleem
zon = Point(200, 200).buffer(170)
zee = unary_union([LineString([(20 + i * 3.6, 140 - k * 46 + 14 * math.sin(i / 100 * 2 * math.pi * 2)) for i in range(101)]).buffer(10, cap_style=1) for k in range(2)])
bd = board(250, 92, 200, 95)
V['zon'] = zacht(zon.difference(zee).difference(bd.buffer(14)).union(bd), 3)

# 4. Tegel: afgeronde tegel (zoals de tegelstof) met het board uitgespaard en golven eronder
tegel = box(30, 30, 370, 370).buffer(-40).buffer(40)
bd = board(260, 96, 200, 92)
golven = unary_union([LineString([(10 + i * 3.8, 70 + 32 * k + 11 * math.sin(i / 100 * 2 * math.pi * 2)) for i in range(101)]).buffer(9, cap_style=1) for k in range(2)])
V['tegel'] = zacht(tegel.difference(bd).difference(golven.difference(bd.buffer(-1000))), 3)

# 5. Zegel: board op een schijf, golfjes alleen onder het board door
schijf = Point(200, 200).buffer(178)
bd = board(250, 92, 200, 120)
golfjes = unary_union([LineString([(10 + i * 3.8, 66 + 30 * k + 10 * math.sin(i / 100 * 2 * math.pi * 2.5)) for i in range(101)]).buffer(8, cap_style=1) for k in range(2)])
V['zegel'] = zacht(schijf.difference(bd.buffer(14)).union(bd).difference(golfjes), 3)

json.dump({k: pad(v) for k, v in V.items()}, open(HIER / 'iconen.json', 'w'))
print(list(V))
