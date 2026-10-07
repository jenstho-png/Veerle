"""Nieuwe printontwerpen voor de kleding (transparante png's via render_echt.mjs).

lijn      De lijn naar zee: surfspots langs de kust als haltes op een lijn.
getij     Getijden: hoog en laag water als grafiek, de naam Tide Tode letterlijk genomen.
club      Surfclub-badge met het board en de draagtas in tegelstof in het midden.
handen    HANDEN VRIJ in groot zetsel met het board ertussen.
Elk ontwerp in twee inktvarianten: voor crème stof (navy en terracotta) en voor navy stof (crème en lichtblauw).
"""
import pathlib, sys

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import brandbook as BB  # noqa: E402
from echt_art import pagina  # noqa: E402

NAVY, CREME, TERRA, BABY, ROSE = '#22324F', '#F1E9DA', '#C0603E', '#A9C2DE', '#E3AFA9'
INKT = {'licht': dict(hoofd=NAVY, accent=TERRA, zacht='#6C7F9C', vul=CREME),
        'donker': dict(hoofd=CREME, accent='#E07A55', zacht=BABY, vul=NAVY)}
SPOTS = [('PETTEN', "52°46′N  4°39′O"), ('WIJK AAN ZEE', "52°29′N  4°36′O"), ('ZANDVOORT', "52°22′N  4°32′O"),
         ('NOORDWIJK', "52°14′N  4°26′O"), ('SCHEVENINGEN', "52°06′N  4°16′O"), ('DOMBURG', "51°34′N  3°30′O")]
MONO = "font-family=\"Courier Prime\" font-weight=\"700\""
DISP = "font-family=\"Tide Tode Display\""


def lijn(k):
    o = [f'<text x="500" y="70" {MONO} font-size="30" letter-spacing="12" fill="{k["hoofd"]}" text-anchor="middle">DE LIJN NAAR ZEE</text>',
         f'<line x1="230" y1="150" x2="230" y2="935" stroke="{k["accent"]}" stroke-width="12" stroke-linecap="round"/>']
    for i, (naam, plek) in enumerate(SPOTS):
        y = 160 + i * 155
        o.append(f'<circle cx="230" cy="{y}" r="24" fill="{k["vul"]}" stroke="{k["hoofd"]}" stroke-width="9"/>')
        o.append(f'<text x="292" y="{y + 20}" {DISP} font-size="68" letter-spacing="2" fill="{k["hoofd"]}">{naam}</text>')
        o.append(f'<text x="296" y="{y + 62}" {MONO} font-size="22" letter-spacing="5" fill="{k["zacht"]}">{plek}</text>')
    o.append(BB.logo_in('liggend', 290, 1050, 420, k['hoofd']))
    o.append(f'<text x="500" y="1200" {MONO} font-size="24" letter-spacing="9" fill="{k["accent"]}" text-anchor="middle">SINDS 2025</text>')
    return ''.join(o)


def getij(k):
    import math
    x0, x1, ym, amp = 110, 890, 660, 130
    pts = [(x0 + (x1 - x0) * t / 200, ym - amp * math.cos(2 * math.pi * (t / 200 * 1.93 - 0.24))) for t in range(201)]
    pad = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
    vlak = pad + f' L{x1} 860 L{x0} 860 Z'
    streep = ''.join(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{k["zacht"]}" stroke-width="3" opacity=".55"/>' for y in range(520, 860, 24))
    o = [BB.logo_in('gestapeld', 330, 70, 340, k['hoofd']),
         f'<text x="500" y="375" {MONO} font-size="27" letter-spacing="11" fill="{k["hoofd"]}" text-anchor="middle">GETIJDEN SCHEVENINGEN</text>',
         f'<defs><clipPath id="gv"><path d="{vlak}"/></clipPath></defs><g clip-path="url(#gv)">{streep}</g>',
         f'<path d="{pad}" fill="none" stroke="{k["accent"]}" stroke-width="10" stroke-linecap="round"/>',
         f'<line x1="{x0}" y1="860" x2="{x1}" y2="860" stroke="{k["hoofd"]}" stroke-width="5"/>']
    for i, u in enumerate(['00', '06', '12', '18', '24']):
        x = x0 + (x1 - x0) * i / 4
        o.append(f'<line x1="{x}" y1="860" x2="{x}" y2="880" stroke="{k["hoofd"]}" stroke-width="5"/>'
                 f'<text x="{x}" y="920" {MONO} font-size="26" fill="{k["hoofd"]}" text-anchor="middle">{u}</text>')
    # pieken en dalen met tijden
    for t, soort, tijd in [(0.24 / 1.93, 'HOOG', '06:14'), ((0.24 + 0.5) / 1.93, 'LAAG', '12:31'), ((0.24 + 1) / 1.93, 'HOOG', '18:40')]:
        x = x0 + (x1 - x0) * t
        y = ym - amp if soort == 'HOOG' else ym + amp
        ty = y - 36 if soort == 'HOOG' else y + 62
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{k["vul"]}" stroke="{k["accent"]}" stroke-width="7"/>'
                 f'<rect x="{x - 105:.1f}" y="{ty - 28:.1f}" width="210" height="38" fill="{k["vul"]}"/>'
                 f'<text x="{x:.1f}" y="{ty:.1f}" {MONO} font-size="25" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">{soort} {tijd}</text>')
    o.append(f'<text x="500" y="1040" {DISP} font-size="64" letter-spacing="3" fill="{k["hoofd"]}" text-anchor="middle">SURF ALS HET WATER KOMT</text>')
    o.append(f'<text x="500" y="1110" {MONO} font-size="22" letter-spacing="8" fill="{k["zacht"]}" text-anchor="middle">PAK JE BOARD EN GA</text>')
    return ''.join(o)


def club(k):
    """Badge met de draagtas zelf in het midden: board, tegelpaneel en de band met de lus."""
    import tas as TAS
    tegel = BB.b64(ROOT / 'docs' / 'producten' / 'fabriek' / 'tegels-2x2.png', 'image/png')
    tas = f'''<g transform="translate(200 455)">
<defs><clipPath id="cpa"><path d="{TAS.PANEEL}"/></clipPath></defs>
<path d="{TAS.BOARD}" fill="{k["vul"]}" stroke="{k["hoofd"]}" stroke-width="7"/>
<path d="M60 170 L548 170" stroke="{k["hoofd"]}" stroke-width="3" opacity=".5"/>
<image href="{tegel}" x="170" y="120" width="260" height="140" preserveAspectRatio="xMidYMid slice" clip-path="url(#cpa)"/>
<path d="{TAS.PANEEL}" fill="none" stroke="{k["hoofd"]}" stroke-width="6"/>
<path d="{TAS.BAND}" fill="none" stroke="{k["hoofd"]}" stroke-width="26" stroke-linejoin="round"/>
<path d="{TAS.BAND}" fill="none" stroke="{k["accent"]}" stroke-width="16" stroke-linejoin="round"/>
</g>'''
    return f'''
<circle cx="500" cy="610" r="430" fill="none" stroke="{k["hoofd"]}" stroke-width="12"/>
<circle cx="500" cy="610" r="404" fill="none" stroke="{k["hoofd"]}" stroke-width="3" stroke-dasharray="3 12"/>
<defs><path id="cb" d="M150 610 a350 350 0 0 1 700 0"/><path id="co" d="M118 610 a382 382 0 0 0 764 0"/></defs>
<text {MONO} font-size="58" letter-spacing="20" fill="{k["hoofd"]}"><textPath href="#cb" startOffset="50%" text-anchor="middle">TIDE TODE SURF CLUB</textPath></text>
<text {MONO} font-size="38" letter-spacing="16" fill="{k["accent"]}"><textPath href="#co" startOffset="50%" text-anchor="middle">NOORDZEEKUST</textPath></text>
{BB.ster(150, 625, 16, k["accent"])}{BB.ster(850, 625, 16, k["accent"])}
{tas}
<text x="500" y="800" {DISP} font-size="92" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">HANDEN VRIJ</text>
<text x="500" y="868" {MONO} font-size="30" letter-spacing="12" fill="{k["zacht"]}" text-anchor="middle">EST 2025</text>'''


def handen(k):
    return f'''
<text x="500" y="330" {DISP} font-size="228" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">HANDEN</text>
{BB.board_in(500, 600, 330, k["accent"])}
<text x="500" y="1010" {DISP} font-size="260" letter-spacing="6" fill="{k["hoofd"]}" text-anchor="middle">VRIJ</text>
<text x="500" y="1110" {MONO} font-size="30" letter-spacing="13" fill="{k["zacht"]}" text-anchor="middle">TIDE TODE  OP WEG NAAR ZEE</text>'''


def board(k):
    """Technische tekening van een board, met maatlijnen."""
    o = [f'<text x="500" y="70" {MONO} font-size="28" letter-spacing="12" fill="{k["hoofd"]}" text-anchor="middle">GEMAAKT VOOR DE NOORDZEE</text>']
    # board van boven, neus boven
    pad = 'M500 140 C585 210 640 380 640 620 C640 860 600 1010 560 1060 L440 1060 C400 1010 360 860 360 620 C360 380 415 210 500 140 Z'
    o.append(f'<path d="{pad}" fill="none" stroke="{k["hoofd"]}" stroke-width="6"/>')
    o.append(f'<line x1="500" y1="146" x2="500" y2="1056" stroke="{k["accent"]}" stroke-width="3" stroke-dasharray="14 10"/>')
    # vinnen
    for x in (455, 545):
        o.append(f'<path d="M{x - 10} 985 q10 -40 20 0" fill="none" stroke="{k["hoofd"]}" stroke-width="4"/>')
    o.append(f'<path d="M490 1020 q10 -45 20 0" fill="none" stroke="{k["hoofd"]}" stroke-width="4"/>')
    def pijl(x1, y1, x2, y2, tekst, tx, ty, draai=0):
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{k["zacht"]}" stroke-width="3"/>'
                f'<circle cx="{x1}" cy="{y1}" r="6" fill="{k["zacht"]}"/><circle cx="{x2}" cy="{y2}" r="6" fill="{k["zacht"]}"/>'
                f'<text transform="translate({tx} {ty}) rotate({draai})" {MONO} font-size="30" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">{tekst}</text>')
    o.append(pijl(760, 140, 760, 1060, "7'2\"", 800, 600, 90))
    o.append(pijl(360, 1120, 640, 1120, '22\"', 500, 1170))
    o.append(pijl(240, 560, 240, 680, '2¾\"', 200, 620, -90))
    o.append(f'<text x="500" y="1225" {MONO} font-size="22" letter-spacing="9" fill="{k["accent"]}" text-anchor="middle">TIDE TODE  SINDS 2025</text>')
    return ''.join(o)


def klok(k):
    """Getijdenklok: hoog water boven, laag water onder."""
    import math
    cx, cy, r = 500, 560, 360
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{k["hoofd"]}" stroke-width="10"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r - 28}" fill="none" stroke="{k["hoofd"]}" stroke-width="2.5"/>']
    for i in range(48):
        a = 2 * math.pi * i / 48
        l = 30 if i % 4 == 0 else 14
        x1, y1 = cx + math.sin(a) * (r - 30), cy - math.cos(a) * (r - 30)
        x2, y2 = cx + math.sin(a) * (r - 30 - l), cy - math.cos(a) * (r - 30 - l)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{k["hoofd"]}" stroke-width="{4 if l == 30 else 2.5}"/>')
    o.append(f'<text x="{cx}" y="{cy - r + 120}" {DISP} font-size="64" fill="{k["hoofd"]}" text-anchor="middle">HOOG</text>')
    o.append(f'<text x="{cx}" y="{cy + r - 80}" {DISP} font-size="64" fill="{k["hoofd"]}" text-anchor="middle">LAAG</text>')
    for t, u in [(2, '2'), (4, '4'), (8, '4'), (10, '2')]:
        a = 2 * math.pi * t / 12
        o.append(f'<text x="{cx + math.sin(a) * (r - 105):.1f}" y="{cy - math.cos(a) * (r - 105) + 14:.1f}" {MONO} font-size="38" fill="{k["zacht"]}" text-anchor="middle">{u}</text>')
    # golfje in het midden en de wijzer
    o.append(BB.board_in(cx, cy, 150, k['accent']))
    a = 2 * math.pi * 1.6 / 12
    o.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + math.sin(a) * (r - 75):.1f}" y2="{cy - math.cos(a) * (r - 75):.1f}" stroke="{k["hoofd"]}" stroke-width="10" stroke-linecap="round"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="16" fill="{k["hoofd"]}"/>')
    o.append(f'<text x="500" y="1035" {DISP} font-size="78" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">TIDE TODE</text>')
    o.append(f'<text x="500" y="1105" {MONO} font-size="26" letter-spacing="10" fill="{k["accent"]}" text-anchor="middle">SURF ALS HET TIJ GOED STAAT</text>')
    return ''.join(o)


def tegel(k):
    """Eén grote tegel uit de echte stof van de tas."""
    tg = BB.b64(ROOT / 'docs' / 'producten' / 'fabriek' / 'tegels-2x2.png', 'image/png')
    return f'''
<defs><clipPath id="tgc"><rect x="230" y="150" width="540" height="540" rx="10"/></clipPath></defs>
<image href="{tg}" x="230" y="150" width="1080" height="1080" clip-path="url(#tgc)" preserveAspectRatio="xMinYMin slice"/>
<rect x="230" y="150" width="540" height="540" rx="10" fill="none" stroke="{k["hoofd"]}" stroke-width="8"/>
<rect x="206" y="126" width="588" height="588" rx="18" fill="none" stroke="{k["hoofd"]}" stroke-width="2.5"/>
<text x="500" y="820" {DISP} font-size="92" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">TIDE TODE</text>
<text x="500" y="890" {MONO} font-size="28" letter-spacing="10" fill="{k["accent"]}" text-anchor="middle">UIT DE STOF VAN ONZE TAS</text>
<text x="500" y="960" {MONO} font-size="22" letter-spacing="9" fill="{k["zacht"]}" text-anchor="middle">NOORDZEE</text>'''


def koudwater(k):
    """Koud water surfclub: ronde stempel, één kleur."""
    return f'''
<circle cx="500" cy="560" r="400" fill="none" stroke="{k["hoofd"]}" stroke-width="9"/>
<circle cx="500" cy="560" r="300" fill="none" stroke="{k["hoofd"]}" stroke-width="3"/>
<defs><path id="kb" d="M150 560 a350 350 0 0 1 700 0"/><path id="ko" d="M130 560 a370 370 0 0 0 740 0"/></defs>
<text {MONO} font-size="56" letter-spacing="22" fill="{k["hoofd"]}"><textPath href="#kb" startOffset="50%" text-anchor="middle">KOUD WATER SURFCLUB</textPath></text>
<text {MONO} font-size="40" letter-spacing="20" fill="{k["hoofd"]}"><textPath href="#ko" startOffset="50%" text-anchor="middle">NOORDZEE</textPath></text>
{BB.ster(150, 575, 13, k["hoofd"])}{BB.ster(850, 575, 13, k["hoofd"])}
<text x="500" y="610" {DISP} font-size="190" fill="{k["hoofd"]}" text-anchor="middle">9°</text>
<text x="500" y="690" {MONO} font-size="30" letter-spacing="12" fill="{k["hoofd"]}" text-anchor="middle">EN TOCH GAAN</text>'''


def evenweg(k):
    """Bordje op de deur van een surfshop. Alleen tekst."""
    return f'''
<rect x="210" y="300" width="580" height="420" rx="26" fill="none" stroke="{k["hoofd"]}" stroke-width="8"/>
<path d="M500 300 L380 160 M500 300 L620 160" stroke="{k["hoofd"]}" stroke-width="5"/>
<circle cx="500" cy="155" r="14" fill="none" stroke="{k["hoofd"]}" stroke-width="5"/>
<text x="500" y="440" {DISP} font-size="120" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">EVEN</text>
<text x="500" y="560" {DISP} font-size="120" letter-spacing="4" fill="{k["hoofd"]}" text-anchor="middle">SURFEN</text>
<text x="500" y="650" {MONO} font-size="24" letter-spacing="6" fill="{k["accent"]}" text-anchor="middle">TERUG ALS HET VLAK IS</text>
<text x="500" y="820" {MONO} font-size="24" letter-spacing="10" fill="{k["hoofd"]}" text-anchor="middle">TIDE TODE</text>'''


def herhaling(k):
    """Dezelfde regel steeds opnieuw, de laatste in de accentkleur."""
    regels = ''
    for i in range(7):
        # alleen omlijnd (één inktkleur), de laatste regel vol in de accentkleur
        verf = f'fill="{k["accent"]}"' if i == 6 else f'fill="none" stroke="{k["hoofd"]}" stroke-width="2.6"'
        regels += f'<text x="500" y="{230 + i * 112}" {DISP} font-size="96" letter-spacing="3" {verf} text-anchor="middle">OP WEG NAAR ZEE</text>'
    return regels + f'<text x="500" y="1060" {MONO} font-size="26" letter-spacing="12" fill="{k["hoofd"]}" text-anchor="middle">TIDE TODE</text>'


def weerbericht(k):
    """Surfbericht zoals je het 's ochtends checkt. Alleen tekst."""
    rij = lambda y, a, b: (f'<text x="210" y="{y}" {MONO} font-size="34" letter-spacing="6" fill="{k["hoofd"]}">{a}</text>'
                           f'<text x="790" y="{y}" {MONO} font-size="34" letter-spacing="6" fill="{k["hoofd"]}" text-anchor="end">{b}</text>'
                           f'<line x1="210" y1="{y + 26}" x2="790" y2="{y + 26}" stroke="{k["hoofd"]}" stroke-width="2" stroke-dasharray="3 9"/>')
    return (f'<text x="210" y="250" {MONO} font-size="28" letter-spacing="10" fill="{k["hoofd"]}">SURFBERICHT</text>'
            f'<text x="210" y="380" {DISP} font-size="120" letter-spacing="3" fill="{k["hoofd"]}">ZATERDAG</text>'
            + rij(480, 'GOLVEN', '1,2 M') + rij(560, 'PERIODE', '9 SEC') + rij(640, 'WIND', '2 BFT ZO') + rij(720, 'WATER', '14°')
            + f'<text x="210" y="850" {DISP} font-size="84" letter-spacing="3" fill="{k["accent"]}">WE GAAN</text>'
            + f'<text x="210" y="930" {MONO} font-size="24" letter-spacing="10" fill="{k["hoofd"]}">TIDE TODE</text>')


def boog(k):
    """Klassiek: naam in een boog boven een klein board. Eén kleur."""
    return f'''
<defs><path id="bg" d="M170 640 a330 330 0 0 1 660 0"/></defs>
<text {DISP} font-size="150" letter-spacing="10" fill="{k["hoofd"]}"><textPath href="#bg" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>
{BB.board_in(500, 600, 210, k["hoofd"])}
<text x="500" y="800" {MONO} font-size="34" letter-spacing="16" fill="{k["hoofd"]}" text-anchor="middle">NOORDZEE</text>
<text x="500" y="852" {MONO} font-size="24" letter-spacing="14" fill="{k["hoofd"]}" text-anchor="middle">SINDS 2025</text>'''


def grootboard(k):
    """Ons board groot, met TIDE TODE en HANDEN VRIJ langs de rails geschreven."""
    import re as _re, numpy as np
    from scipy.spatial import ConvexHull
    L = BB.LOGO['board']
    pts = np.array([[float(a), float(b)] for a, b in _re.findall(r'(-?\d+\.?\d*) (-?\d+\.?\d*)', L['d'])])
    h_doel = 860
    sch = h_doel / L['h']
    cx, cy = 500, 600
    ox, oy = cx - L['w'] * sch / 2, cy - h_doel / 2
    P = pts * sch + [ox, oy]
    hull = P[ConvexHull(P).vertices]
    c = hull.mean(0)
    # rand iets naar buiten voor de tekst
    v = hull - c
    gat = 34
    buiten = hull + v / np.linalg.norm(v, axis=1)[:, None] * gat
    neus = int(np.argmin(buiten[:, 1])); staart = int(np.argmax(buiten[:, 1]))
    n = len(buiten)
    def keten(a, b):
        i, uit = a, [buiten[a]]
        while i != b:
            i = (i + 1) % n; uit.append(buiten[i])
        return np.array(uit)
    k1, k2 = keten(neus, staart), keten(staart, neus)
    rechts, links = (k1, k2) if k1[:, 0].mean() > cx else (k2, k1)
    if rechts[0][1] > rechts[-1][1]: rechts = rechts[::-1]          # rechts: van neus naar staart (tekst naar buiten)
    if links[0][1] < links[-1][1]: links = links[::-1]               # links: van staart naar neus
    d = lambda a: 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in a)
    return f'''
<defs><path id="gbr" d="{d(rechts)}"/><path id="gbl" d="{d(links)}"/></defs>
{BB.board_in(cx, cy, h_doel, k["hoofd"])}
<text {DISP} font-size="64" letter-spacing="10" fill="{k["hoofd"]}"><textPath href="#gbr" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>
'''


def paklijst(k):
    """Wat mee moet. Het laatste vinkje in de accentkleur."""
    items = [('BOARD', 1), ('WAX', 1), ('WETSUIT', 1), ('HANDDOEK', 1), ('KOFFIE', 2)]
    o = [f'<text x="250" y="250" {DISP} font-size="92" letter-spacing="3" fill="{k["hoofd"]}">PAKLIJST</text>']
    for i, (t, soort) in enumerate(items):
        y = 380 + i * 120
        kl = k['accent'] if soort == 2 else k['hoofd']
        o.append(f'<rect x="250" y="{y - 52}" width="60" height="60" rx="6" fill="none" stroke="{k["hoofd"]}" stroke-width="6"/>')
        o.append(f'<path d="M262 {y - 24} l18 20 l38 -52" fill="none" stroke="{kl}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<text x="350" y="{y}" {MONO} font-size="46" letter-spacing="8" fill="{kl}">{t}</text>')
    o.append(f'<text x="250" y="1020" {MONO} font-size="24" letter-spacing="10" fill="{k["hoofd"]}">TIDE TODE</text>')
    return ''.join(o)


def hawaii(k):
    """Droge Hollandse knipoog. Alleen tekst."""
    return f'''
<text x="500" y="420" {DISP} font-size="110" letter-spacing="3" fill="{k["hoofd"]}" text-anchor="middle">NOORDZEE</text>
<text x="500" y="520" {MONO} font-size="40" letter-spacing="12" fill="{k["hoofd"]}" text-anchor="middle">IS GEEN HAWAII</text>
<line x1="380" y1="590" x2="620" y2="590" stroke="{k["accent"]}" stroke-width="5"/>
<text x="500" y="680" {MONO} font-size="40" letter-spacing="12" fill="{k["accent"]}" text-anchor="middle">GELUKKIG</text>
<text x="500" y="900" {MONO} font-size="24" letter-spacing="10" fill="{k["hoofd"]}" text-anchor="middle">TIDE TODE</text>'''


def groeten(k):
    """Oude ansichtkaart: groeten uit."""
    return f'''
<rect x="150" y="260" width="700" height="480" rx="8" fill="none" stroke="{k["hoofd"]}" stroke-width="7"/>
<rect x="170" y="280" width="660" height="440" rx="4" fill="none" stroke="{k["hoofd"]}" stroke-width="2" stroke-dasharray="6 8"/>
<text x="500" y="380" {MONO} font-size="38" letter-spacing="14" fill="{k["hoofd"]}" text-anchor="middle">GROETEN UIT</text>
<text x="500" y="520" {DISP} font-size="120" letter-spacing="2" fill="{k["accent"]}" text-anchor="middle">DE GOLVEN</text>
<path d="M240 610 q35 -30 70 0 t70 0 t70 0 t70 0 t70 0 t70 0 t70 0" fill="none" stroke="{k["hoofd"]}" stroke-width="6" stroke-linecap="round"/>
<path d="M240 660 q35 -30 70 0 t70 0 t70 0 t70 0 t70 0 t70 0 t70 0" fill="none" stroke="{k["hoofd"]}" stroke-width="6" stroke-linecap="round"/>
<text x="500" y="830" {MONO} font-size="24" letter-spacing="10" fill="{k["hoofd"]}" text-anchor="middle">TIDE TODE</text>'''


def zout(k):
    """Drie regels over een goede dag."""
    regel = lambda y, t, kl: f'<text x="500" y="{y}" {DISP} font-size="86" letter-spacing="3" fill="{kl}" text-anchor="middle">{t}</text>'
    return (regel(380, 'ZOUT IN JE HAAR', k['hoofd']) + regel(500, 'ZAND IN JE AUTO', k['hoofd']) + regel(620, 'GEEN HAAST', k['accent'])
            + BB.board_in(500, 800, 150, k['hoofd'])
            + f'<text x="500" y="960" {MONO} font-size="24" letter-spacing="10" fill="{k["hoofd"]}" text-anchor="middle">TIDE TODE</text>')


def _rand(pad_d, schaal, ox, oy):
    """Buitenrand (convex omhulsel) van een logo-pad, geschaald."""
    import re as _re, numpy as np
    from scipy.spatial import ConvexHull
    pts = np.array([[float(a), float(b)] for a, b in _re.findall(r'(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)', pad_d)])
    P = pts * schaal + [ox, oy]
    return P[ConvexHull(P).vertices]


def zon(k):
    """Grote zon met stralen, de naam in een cirkel eromheen."""
    import math
    cx, cy = 500, 580
    o = [f'<circle cx="{cx}" cy="{cy}" r="230" fill="{k["hoofd"]}"/>']
    for i in range(24):
        a = 2 * math.pi * i / 24
        r1, r2 = 262, 262 + (70 if i % 2 == 0 else 42)
        o.append(f'<line x1="{cx + math.cos(a) * r1:.1f}" y1="{cy + math.sin(a) * r1:.1f}" x2="{cx + math.cos(a) * r2:.1f}" y2="{cy + math.sin(a) * r2:.1f}" stroke="{k["hoofd"]}" stroke-width="14" stroke-linecap="round"/>')
    o.append(f'<defs><path id="zc" d="M{cx - 400} {cy} a400 400 0 1 1 800 0 a400 400 0 1 1 -800 0"/></defs>')
    o.append(f'<text {DISP} font-size="70" fill="{k["hoofd"]}"><textPath href="#zc" startOffset="0%" textLength="2500" lengthAdjust="spacing">TIDE TODE   TIDE TODE   TIDE TODE   </textPath></text>')
    return ''.join(o)


def golf(k):
    """Onze golf groot, de naam over de kam."""
    L = BB.LOGO['icoonGolf']
    br = 760
    s = br / L['w']; ox = 500 - br / 2; oy = 640 - L['h'] * s / 2
    return (f'<path transform="translate({ox:.1f} {oy:.1f}) scale({s:.4f})" fill="{k["hoofd"]}" d="{L["d"]}"/>'
            f'<defs><path id="gk" d="M{ox + 40:.0f} {oy - 30:.0f} Q 500 {oy - 230:.0f} {ox + br - 40:.0f} {oy - 30:.0f}"/></defs>'
            f'<text {DISP} font-size="96" letter-spacing="12" fill="{k["hoofd"]}"><textPath href="#gk" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>')


def vin(k):
    """Een surfvin als grote vorm, met de naam langs de achterrand."""
    pad = 'M300 1000 C320 800 360 560 470 380 C560 230 680 170 760 160 C700 300 670 520 690 760 C700 860 720 940 740 1000 Z'
    return (f'<path d="{pad}" fill="{k["hoofd"]}"/>'
            f'<defs><path id="vr" d="M820 170 C750 320 725 530 745 760 C755 860 775 940 795 1010"/></defs>'
            f'<text {DISP} font-size="78" letter-spacing="12" fill="{k["hoofd"]}"><textPath href="#vr" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>'
            f'<line x1="250" y1="1040" x2="790" y2="1040" stroke="{k["hoofd"]}" stroke-width="8"/>')


def tweeboards(k):
    """Twee boards gekruist, de naam in een boog eronder."""
    b = BB.board_in(0, 0, 760, k['hoofd'])
    return (f'<g transform="translate(340 540)">{b}</g><g transform="translate(660 540)">{b}</g>'
            f'<defs><path id="tb" d="M230 960 a300 200 0 0 0 540 0"/></defs>'
            f'<text {DISP} font-size="88" letter-spacing="12" fill="{k["hoofd"]}"><textPath href="#tb" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>')


def tweeboardslos(k):
    """Twee boards naast elkaar, zonder tekst."""
    b = BB.board_in(0, 0, 820, k['hoofd'])
    return f'<g transform="translate(340 600)">{b}</g><g transform="translate(660 600)">{b}</g>'


ONTWERPEN = {'tweeboardslos': tweeboardslos, 'zon': zon, 'golf': golf, 'vin': vin, 'tweeboards': tweeboards, 'paklijst': paklijst, 'hawaii': hawaii, 'groeten': groeten, 'zout': zout, 'grootboard': grootboard, 'koudwater': koudwater, 'evenweg': evenweg, 'herhaling': herhaling, 'weerbericht': weerbericht, 'boog': boog, 'lijn': lijn, 'getij': getij, 'club': club, 'handen': handen, 'board': board, 'klok': klok, 'tegel': tegel}

if __name__ == '__main__':
    for naam, f in ONTWERPEN.items():
        for kant, k in INKT.items():
            pagina(f'ontwerp-{naam}-{kant}', 1000, 1250, f'<svg viewBox="0 0 1000 1250" width="1000" height="1250" xmlns="http://www.w3.org/2000/svg">{f(k)}</svg>')
    print('ontwerpen klaar')
