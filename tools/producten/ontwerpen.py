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
    o.append(f'<text x="500" y="1200" {MONO} font-size="24" letter-spacing="9" fill="{k["accent"]}" text-anchor="middle">HANDEN VRIJ SINDS 2025</text>')
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
    o.append(f'<text x="500" y="1225" {MONO} font-size="22" letter-spacing="9" fill="{k["accent"]}" text-anchor="middle">TIDE TODE  HANDEN VRIJ SINDS 2025</text>')
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
<text x="500" y="960" {MONO} font-size="22" letter-spacing="9" fill="{k["zacht"]}" text-anchor="middle">HANDEN VRIJ OP WEG NAAR ZEE</text>'''


ONTWERPEN = {'lijn': lijn, 'getij': getij, 'club': club, 'handen': handen, 'board': board, 'klok': klok, 'tegel': tegel}

if __name__ == '__main__':
    for naam, f in ONTWERPEN.items():
        for kant, k in INKT.items():
            pagina(f'ontwerp-{naam}-{kant}', 1000, 1250, f'<svg viewBox="0 0 1000 1250" width="1000" height="1250" xmlns="http://www.w3.org/2000/svg">{f(k)}</svg>')
    print('ontwerpen klaar')
