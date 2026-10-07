"""Het assortiment van Tide-Tode: 22 producten in 3 collecties.

Schrijft:
- docs/producten/producten.csv   Shopify-productimport (beelden via de openbare GitHub-link)
- docs/producten/overzicht.md     lijst met prijzen, collecties en wat nog gecontroleerd moet worden
- tools/producten/uit/*.html      per productbeeld een pagina; render.mjs maakt er jpg's van

Beelden zijn getekend in de merkstijl. Vervang ze door echte foto's zodra die er zijn.
"""
import csv, json, math, pathlib, sys

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
from tas import BOARD, PANEEL, BAND  # noqa: E402
import stickers as ST  # noqa: E402

UIT = HIER / 'uit'
UIT.mkdir(exist_ok=True)
DOCS = ROOT / 'docs' / 'producten'
(DOCS / 'beelden').mkdir(parents=True, exist_ok=True)
ASSETS = ROOT / 'theme' / 'assets'
RAW = 'https://raw.githubusercontent.com/jenstho-png/Veerle/claude/new-session-yk0x8x/docs/producten/beelden/'

L = json.load(open(ROOT / 'tools' / 'brand2' / 'logo2.json'))
I = json.load(open(ROOT / 'tools' / 'brand2' / 'iconen.json'))
G, BD = L['gestapeld'], L['board']

NAVY, CREME, PAPIER = '#22324F', '#F3ECDD', '#FBF7EF'
BABY, ROSE, ZAND = '#BFD3EA', '#EDBDB8', '#E3CFAE'
TERRA, BLAUW, MOSTERD, ROEST = '#C0603E', '#8FA9C8', '#D9A93B', '#9E3B2E'
SALIE, ZEE = '#9DB09A', '#3E6C8A'


# ---------- patronen (tegelgrootte t, binnen een rechthoek) ----------
def p_tegel(x0, y0, x1, y1, t, kleuren=(TERRA, BLAUW, CREME, ROEST, BLAUW, TERRA, CREME), stip=NAVY, ruit=CREME, ruit_op_creme=TERRA):
    o = []
    r = 0
    y = y0
    while y < y1:
        c = 0
        x = x0
        while x < x1:
            kl = kleuren[(r * 3 + c) % len(kleuren)]
            b = ruit if kl not in (CREME, PAPIER) else ruit_op_creme
            h = t / 2
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{t + .5:.1f}" height="{t + .5:.1f}" fill="{kl}"/>'
                     f'<path d="M{x + h:.1f} {y + t * .14:.1f}L{x + t * .86:.1f} {y + h:.1f}L{x + h:.1f} {y + t * .86:.1f}L{x + t * .14:.1f} {y + h:.1f}Z" fill="{b}"/>'
                     f'<circle cx="{x + h:.1f}" cy="{y + h:.1f}" r="{t * .12:.1f}" fill="{stip}"/>')
            x += t; c += 1
        y += t; r += 1
    return ''.join(o)


def p_golfjes(x0, y0, x1, y1, t, achter=NAVY, lijn=BABY):
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{achter}"/>']
    y, r = y0 + t * .3, 0
    while y < y1 + t:
        pts = ' '.join(f'{x0 + i * t / 8:.1f},{y + math.sin(i / 8 * 2 * math.pi + r * math.pi) * t * .16:.1f}' for i in range(int((x1 - x0) / t * 8) + 9))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{lijn}" stroke-width="{t * .11:.1f}" stroke-linecap="round"/>')
        y += t * .55; r += 1
    return ''.join(o)


def p_strepen(x0, y0, x1, y1, t, kleuren=(ROSE, CREME, TERRA, ZAND)):
    o, y, i = [], y0, 0
    while y < y1:
        o.append(f'<rect x="{x0}" y="{y:.1f}" width="{x1 - x0}" height="{t * .62 + .5:.1f}" fill="{kleuren[i % len(kleuren)]}"/>')
        y += t * .62; i += 1
    return ''.join(o)


def p_schubben(x0, y0, x1, y1, t, achter=CREME, schub=ROSE, rand=CREME):
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{achter}"/>']
    r, y = 0, y0 - t
    while y < y1 + t:
        x = x0 - t + (t / 2 if r % 2 else 0)
        while x < x1 + t:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{t * .5:.1f}" fill="{schub}" stroke="{rand}" stroke-width="{t * .07:.1f}"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{t * .26:.1f}" fill="none" stroke="{rand}" stroke-width="{t * .05:.1f}" opacity=".7"/>')
            x += t
        y += t * .5; r += 1
    return ''.join(o)


def p_ruit(x0, y0, x1, y1, t, a=BABY, b=CREME):
    o, y, r = [], y0, 0
    while y < y1:
        x, c = x0, 0
        while x < x1:
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{t + .5:.1f}" height="{t + .5:.1f}" fill="{a if (r + c) % 2 else b}"/>')
            x += t; c += 1
        y += t; r += 1
    return ''.join(o)


def p_diagonaal(x0, y0, x1, y1, t, a=ZAND, b=CREME):
    w, h = x1 - x0, y1 - y0
    o = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{b}"/>']
    k = -h
    while k < w + h:
        o.append(f'<path d="M{x0 + k:.1f} {y1}L{x0 + k + h:.1f} {y0}L{x0 + k + h + t * .4:.1f} {y0}L{x0 + k + t * .4:.1f} {y1}Z" fill="{a}"/>')
        k += t * .8
    return ''.join(o)


def p_effen(x0, y0, x1, y1, t, kleur=NAVY, draad=None):
    draad = draad or ('#ffffff' if kleur in (NAVY, ZEE, ROEST) else NAVY)
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{kleur}"/>']
    y = y0
    while y < y1:
        o.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{draad}" stroke-opacity=".06" stroke-width="{t * .05:.2f}"/>')
        y += t * .14
    return ''.join(o)


PATRONEN = {
    'tegel': (p_tegel, {}),
    'tegel-navy': (p_tegel, {'kleuren': (NAVY, BABY, CREME, ZEE, BABY, NAVY, CREME), 'stip': CREME, 'ruit': CREME, 'ruit_op_creme': NAVY}),
    'golfjes': (p_golfjes, {}),
    'zonsondergang': (p_strepen, {}),
    'schelp': (p_schubben, {}),
    'ruit': (p_ruit, {}),
    'duin': (p_diagonaal, {}),
    'salie': (p_tegel, {'kleuren': (SALIE, CREME, ZAND, SALIE, ZAND, CREME, SALIE), 'stip': NAVY, 'ruit': CREME, 'ruit_op_creme': SALIE}),
    'effen-navy': (p_effen, {'kleur': NAVY}),
}


def patroon(naam, x0, y0, x1, y1, t):
    f, kw = PATRONEN[naam]
    return f(x0, y0, x1, y1, t, **kw)


# ---------- tekeningen (svg-inhoud) ----------
def tas(pat, band=BLAUW, uid='a'):
    return f'''<defs><clipPath id="p{uid}"><path d="{PANEEL}"/></clipPath>
  <linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".08"/></linearGradient></defs>
  <path d="{BOARD}" fill="{CREME}" stroke="{NAVY}" stroke-width="3"/>
  <path d="M60 170 L548 170" stroke="{NAVY}" stroke-width="1.6" opacity=".35"/>
  <path d="{BOARD}" fill="url(#g{uid})"/>
  <g clip-path="url(#p{uid})">{patroon(pat, 170, 125, 430, 250, 29)}</g>
  <path d="{PANEEL}" fill="none" stroke="{NAVY}" stroke-width="3"/>
  <path d="{PANEEL}" transform="translate(300 189) scale(.95) translate(-300 -189)" fill="none" stroke="{CREME}" stroke-width="1.4" stroke-dasharray="5 5" opacity=".7"/>
  <path d="{BAND}" fill="none" stroke="{band}" stroke-width="15" stroke-linejoin="round"/>
  <path d="{BAND}" fill="none" stroke="{NAVY}" stroke-width="1.4" stroke-dasharray="4 5" opacity=".55"/>'''


def icoon_a(x, y, h, kleur):
    s = h / BD['h']
    return f'<path transform="translate({x - BD["w"] * s / 2:.1f} {y - h / 2:.1f}) scale({s:.4f})" d="{BD["d"]}" fill="{kleur}"/>'


def logo_g(x, y, w, kleur):
    s = w / G['w']
    return f'<path transform="translate({x - w / 2:.1f} {y - G["h"] * s / 2:.1f}) scale({s:.4f})" d="{G["d"]}" fill="{kleur}"/>'


def wax(kleur, label, uid):
    return f'''<defs><linearGradient id="w{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#000" stop-opacity=".06"/></linearGradient></defs>
  <g transform="rotate(-10 300 300)">
    <rect x="130" y="250" width="340" height="70" rx="26" fill="{kleur}" filter="brightness(.85)"/>
    <rect x="130" y="250" width="340" height="70" rx="26" fill="#000" opacity=".12"/>
    <rect x="130" y="170" width="340" height="130" rx="28" fill="{kleur}"/>
    <rect x="130" y="170" width="340" height="130" rx="28" fill="url(#w{uid})"/>
    <rect x="186" y="196" width="228" height="80" rx="10" fill="{CREME}"/>
    {icoon_a(222, 236, 52, NAVY)}
    <text x="250" y="230" font-family="Courier Prime" font-weight="700" font-size="17" letter-spacing="3" fill="{NAVY}">TIDE TODE</text>
    <text x="250" y="256" font-family="Courier Prime" font-weight="700" font-size="14" letter-spacing="2.6" fill="{NAVY}" opacity=".75">{label}</text>
  </g>'''


def kam():
    tanden = ''.join(f'<rect x="{168 + i * 18}" y="330" width="9" height="58" rx="4" fill="{NAVY}"/>' for i in range(15))
    return f'''<g transform="rotate(-8 300 300)">
    <rect x="160" y="200" width="280" height="140" rx="30" fill="{NAVY}"/>
    {tanden}
    <rect x="160" y="200" width="280" height="22" rx="11" fill="#fff" opacity=".12"/>
    {icoon_a(300, 270, 70, CREME)}
  </g>'''


def karabijn(metaal, glans, uid):
    return f'''<defs><linearGradient id="k{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{glans}"/><stop offset=".5" stop-color="{metaal}"/><stop offset="1" stop-color="{glans}"/></linearGradient></defs>
  <g transform="rotate(18 300 300)">
    <path d="M250 120 C190 120 170 160 170 210 L170 390 C170 450 210 480 260 480 L340 480 C390 480 430 450 430 390 L430 210 C430 160 410 120 350 120 Z" fill="none" stroke="url(#k{uid})" stroke-width="34" stroke-linejoin="round"/>
    <path d="M430 250 L430 390" stroke="{CREME}" stroke-width="40"/>
    <path d="M416 228 L380 404" stroke="url(#k{uid})" stroke-width="22" stroke-linecap="round"/>
    <path d="M190 220 C190 170 210 146 252 142" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="7" stroke-linecap="round"/>
  </g>'''


def stickerset():
    plek = [('golf', 190, 200, -8), ('zon', 410, 190, 6), ('schelp', 180, 410, 5), ('palm', 300, 300, -4), ('zeester', 420, 410, 12), ('busje', 300, 470, 4)]
    S = {s['naam']: s for s in ST.S}
    o = [f'<rect x="80" y="70" width="440" height="470" rx="22" fill="{PAPIER}"/>', f'<rect x="80" y="70" width="440" height="470" rx="22" fill="none" stroke="{NAVY}" stroke-opacity=".12" stroke-width="2"/>']
    for n, x, y, r in plek:
        s = S[n]; vx, vy, vw, vh = map(float, s['vb'].split()); sc = 150 / max(vw, vh)
        binnen = ST.svg(s, schaduw=False)
        binnen = binnen[binnen.index('>') + 1:binnen.rindex('</svg>')]
        o.append(f'<g transform="translate({x} {y}) rotate({r}) scale({sc:.3f}) translate({-(vx + vw / 2):.1f} {-(vy + vh / 2):.1f})">{binnen}</g>')
    return ''.join(o)


SHIRT = 'M215 120 L165 140 L95 210 L140 262 L180 230 L180 500 L420 500 L420 230 L460 262 L505 210 L435 140 L385 120 C370 150 340 165 300 165 C260 165 230 150 215 120 Z'


def shirt(kleur, print_kleur):
    return f'''<path d="{SHIRT}" fill="{kleur}" stroke="{NAVY}" stroke-opacity=".25" stroke-width="3" stroke-linejoin="round"/>
  <path d="M215 120 C230 150 260 165 300 165 C340 165 370 150 385 120" fill="none" stroke="{NAVY}" stroke-opacity=".3" stroke-width="6"/>
  <path d="M180 230 L180 260 M420 230 L420 260" stroke="{NAVY}" stroke-opacity=".12" stroke-width="3"/>
  {logo_g(300, 265, 120, print_kleur)}'''


def pet(kleur):
    return f'''<path d="M140 330 C140 200 210 150 300 150 C390 150 460 200 460 330 Z" fill="{kleur}"/>
  <path d="M300 150 L300 330 M220 170 C200 220 196 280 200 330 M380 170 C400 220 404 280 400 330" stroke="#000" stroke-opacity=".14" stroke-width="3" fill="none"/>
  <circle cx="300" cy="152" r="9" fill="{kleur}" stroke="#000" stroke-opacity=".2" stroke-width="2"/>
  <path d="M120 330 C150 312 450 312 480 330 C470 380 130 380 120 330 Z" fill="{kleur}" filter="brightness(.9)"/>
  <path d="M120 330 C150 312 450 312 480 330 C470 380 130 380 120 330 Z" fill="#000" opacity=".12"/>
  {icoon_a(300, 250, 82, CREME)}'''


def bucket(uid):
    return f'''<defs><clipPath id="b{uid}"><path d="M200 290 L400 290 L388 318 L212 318 Z"/></clipPath></defs>
  <path d="M110 380 C110 330 200 300 300 300 C400 300 490 330 490 380 C490 410 110 410 110 380 Z" fill="{CREME}" stroke="{NAVY}" stroke-opacity=".25" stroke-width="3"/>
  <path d="M215 170 C230 150 370 150 385 170 L410 310 C350 330 250 330 190 310 Z" fill="{CREME}" stroke="{NAVY}" stroke-opacity=".25" stroke-width="3"/>
  <path d="M190 300 C250 320 350 320 410 300 L404 270 C350 288 250 288 196 270 Z" fill="{TERRA}"/>
  <g clip-path="url(#b{uid})"></g>
  <path d="M196 270 C250 288 350 288 404 270 L410 300 C350 320 250 320 190 300 Z" fill="none" stroke="{NAVY}" stroke-width="2"/>
  <path d="M200 285 C250 300 350 300 400 285" fill="none" stroke="{CREME}" stroke-width="2" stroke-dasharray="6 6"/>
  {icoon_a(300, 225, 60, NAVY)}'''


def handdoek(uid):
    franje = ''.join(f'<line x1="{170 + i * 13}" y1="500" x2="{170 + i * 13}" y2="526" stroke="{CREME}" stroke-width="4" stroke-linecap="round"/>' for i in range(21))
    return f'''<defs><clipPath id="h{uid}"><rect x="160" y="90" width="280" height="410" rx="6"/></clipPath></defs>
  {franje}
  <g clip-path="url(#h{uid})">{p_tegel(160, 90, 440, 500, 70)}</g>
  <path d="M160 300 L440 300" stroke="#000" stroke-opacity=".12" stroke-width="10"/>
  <rect x="160" y="90" width="280" height="410" rx="6" fill="none" stroke="{NAVY}" stroke-opacity=".2" stroke-width="3"/>'''


def tote():
    return f'''<path d="M235 200 C235 110 365 110 365 200" fill="none" stroke="{ZAND}" stroke-width="18" filter="brightness(.92)"/>
  <path d="M235 200 C235 110 365 110 365 200" fill="none" stroke="#000" stroke-opacity=".08" stroke-width="18"/>
  <path d="M160 200 L440 200 L452 510 L148 510 Z" fill="{CREME}" stroke="{NAVY}" stroke-opacity=".22" stroke-width="3"/>
  <path d="M160 214 L440 214" stroke="{NAVY}" stroke-opacity=".18" stroke-width="2" stroke-dasharray="6 6"/>
  {logo_g(300, 360, 170, NAVY)}'''


# ---------- pagina's ----------
def fonts():
    return ''.join(f"@font-face{{font-family:'{f}';src:url('file://{ASSETS / b}') format('woff2');font-weight:{w}}}"
                   for f, b, w in [('Courier Prime', 'courierprime-regular.woff2', 400), ('Courier Prime', 'courierprime-bold.woff2', 700),
                                   ('Homemade Apple', 'homemadeapple-regular.woff2', 400), ('Tide Tode Display', 'tide-tode-display.woff2', 400)])


def packshot(naam, achter, svg, titel, label, vb='0 0 600 600', breedte=1250, draai=0, schaduw=True):
    vx, vy, vw, vh = map(float, vb.split())
    hoogte = breedte if abs(draai) > 45 else breedte * vh / vw
    y = min(1660, 960 + hoogte * (.36 if vh == vw else .5))
    sch = f'<div style="position:absolute;left:50%;top:{y:.0f}px;width:760px;height:90px;translate:-50% 0;border-radius:50%;background:radial-gradient(closest-side, rgba(34,50,79,.28), rgba(34,50,79,0));filter:blur(6px)"></div>' if schaduw else ''
    html = f'''<!doctype html><meta charset="utf-8"><style>{fonts()}
* {{ box-sizing: border-box; margin: 0; }} html, body {{ width: 1600px; height: 2000px; overflow: hidden; }}
body {{ position: relative; background: radial-gradient(120% 80% at 50% 38%, #fff8 0%, #fff0 60%), {achter}; color: {NAVY}; font-family: 'Courier Prime', monospace; }}
.label {{ position: absolute; font: 700 30px 'Courier Prime'; letter-spacing: .24em; text-transform: uppercase; }}
.korrel {{ position: absolute; inset: 0; opacity: .12; mix-blend-mode: multiply; }}
</style><body>
<div class="label" style="left:90px;top:90px">Tide Tode</div><div class="label" style="right:90px;top:90px">{titel}</div>
{sch}
<svg viewBox="{vb}" style="position:absolute;left:50%;top:48%;width:{breedte}px;translate:-50% -50%;rotate:{draai}deg;filter:drop-shadow(-14px 18px 26px rgba(34,50,79,.2))">{svg}</svg>
<div class="label" style="left:90px;bottom:96px">{label}</div>
<svg class="korrel" width="100%" height="100%"><filter id="k"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .5 0"/></filter><rect width="100%" height="100%" filter="url(#k)"/></svg>
</body>'''
    (UIT / f'{naam}.html').write_text(html)


def sfeer(naam, svg, vb, breedte, draai, regel):
    """Het product als sticker (witte rand) op de zwart-witfoto van de zee."""
    html = f'''<!doctype html><meta charset="utf-8"><style>{fonts()}
* {{ box-sizing: border-box; margin: 0; }} html, body {{ width: 1600px; height: 2000px; overflow: hidden; background: #2a2f36; }}
img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; filter: grayscale(1) brightness(.72) contrast(1.05); }}
.hand {{ position: absolute; left: 0; right: 0; bottom: 170px; text-align: center; color: {CREME}; font: 400 70px/1.3 'Homemade Apple'; }}
</style><body><img src="file://{ASSETS / 'tt-foto-zee-zw.jpg'}">
<svg viewBox="{vb}" style="position:absolute;left:50%;top:45%;width:{breedte}px;translate:-50% -50%;rotate:{draai}deg;overflow:visible">
<defs><filter id="rand" x="-20%" y="-20%" width="140%" height="140%"><feMorphology in="SourceAlpha" operator="dilate" radius="14" result="d"/><feFlood flood-color="#FFFDF8"/><feComposite in2="d" operator="in" result="wit"/><feGaussianBlur in="d" stdDeviation="10" result="s"/><feOffset in="s" dx="0" dy="14" result="so"/><feFlood flood-color="#000" flood-opacity=".35"/><feComposite in2="so" operator="in" result="schaduw"/><feMerge><feMergeNode in="schaduw"/><feMergeNode in="wit"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g filter="url(#rand)">{svg}</g></svg>
<p class="hand">{regel}</p></body>'''
    (UIT / f'{naam}.html').write_text(html)


def macro(naam, pat, label):
    html = f'''<!doctype html><meta charset="utf-8"><style>{fonts()}
* {{ box-sizing: border-box; margin: 0; }} html, body {{ width: 1600px; height: 2000px; overflow: hidden; }}
.pil {{ position: absolute; left: 90px; bottom: 90px; padding: 22px 40px; border-radius: 999px; background: {NAVY}; color: {CREME}; font: 700 30px 'Courier Prime'; letter-spacing: .24em; text-transform: uppercase; }}
</style><body><svg viewBox="0 0 1600 2000" style="position:absolute;inset:0;width:100%;height:100%"><g transform="rotate(-7 800 1000)">{patroon(pat, -400, -400, 2000, 2400, 270)}</g>
<defs><radialGradient id="v" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient></defs><rect width="1600" height="2000" fill="url(#v)"/></svg>
<div class="pil">{label}</div></body>'''
    (UIT / f'{naam}.html').write_text(html)


# ---------- het assortiment ----------
VERZENDING = '<p>Verzending door heel Europa. Binnen 14 dagen retour.</p>'

TASSEN = [
    # handle, naam, patroon, band, achtergrond, prijs, kleuromschrijving, regel
    ('draagtas-tegel', 'Tegel', 'tegel', BLAUW, '#EFE5D3', '40.00', 'tegelprint in terracotta, dusty blue, roest en crème', 'Het origineel'),
    ('draagtas-tegel-navy', 'Tegel Navy', 'tegel-navy', NAVY, BABY, '42.00', 'tegelprint in navy, baby blue en crème', 'Donkere versie van de tegel'),
    ('draagtas-golfjes', 'Golfjes', 'golfjes', BABY, '#DCE6F1', '42.00', 'baby blue golfjes op navy', 'Golfjes op navy'),
    ('draagtas-zonsondergang', 'Zonsondergang', 'zonsondergang', TERRA, ROSE, '42.00', 'strepen in rose, zand, terracotta en crème', 'Strepen in zachte kleuren'),
    ('draagtas-schelp', 'Schelp', 'schelp', ROSE, '#F6E3DF', '42.00', 'schelpenprint in rose en crème', 'Schelpenprint'),
    ('draagtas-ruit', 'Ruit', 'ruit', NAVY, '#E4ECF5', '42.00', 'ruitjes in baby blue en crème', 'Ruitjes in baby blue'),
    ('draagtas-duin', 'Duin', 'duin', TERRA, ZAND, '42.00', 'schuine strepen in zand en crème', 'Zand en crème'),
    ('draagtas-salie', 'Salie', 'salie', NAVY, '#E3E8DF', '42.00', 'tegelprint in saliegroen, zand en crème', 'Tegels in saliegroen'),
    ('draagtas-navy', 'Navy', 'effen-navy', BLAUW, '#E9E2D3', '38.00', 'effen navy', 'Effen navy'),
]

P = []
for handle, naam, pat, band, achter, prijs, kleur, regel in TASSEN:
    P.append(dict(
        handle=handle, titel=f'Draagtas {naam}', type='Draagtas', collectie='Draagtassen', prijs=prijs, gram=650,
        tags=['draagtas', 'surfboard', 'tas'] + (['origineel'] if pat == 'tegel' else []),
        tekst=(f'<p>De Tide-Tode draagtas in {kleur}. Je schuift je surfboard in de tas en hangt hem over je schouder. '
               f'Zo heb je je handen vrij als je naar het strand loopt, fietst of op de scooter zit.</p>'
               '<ul><li>Eén maat, voor softtops en hardboards</li><li>Brede schouderband</li><li>Zware geweven stof met sterke stiksels</li><li>Je natte board mag er gewoon in</li></ul>'
               + VERZENDING),
        seo_titel=f'Draagtas {naam} voor je surfboard | Tide-Tode',
        seo_tekst=f'Surfboard draagtas in {kleur}. Board in de tas, tas over je schouder en je handen zijn vrij. Voor softtops en hardboards.',
        beelden=[
            ('pack', lambda pat=pat, band=band, h=handle: (tas(pat, band, h.replace('-', '')), '0 0 600 300', 1640, -90), achter, naam, f'Draagtas {naam}, staand vooraanzicht'),
            ('macro', pat, f'De stof van draagtas {naam} van dichtbij'),
            ('sfeer', lambda pat=pat, band=band, h=handle: (tas(pat, band, h.replace('-', '') + 's'), '-30 -30 660 360', 1250, -9), 'Handen vrij, op weg naar zee', f'Draagtas {naam} als sticker op een foto van de zee'),
        ]))

WAX = [('surfwax-koud', 'Surfwax koud water', BABY, 'KOUD WATER', 'onder 14 graden', 'Voor de Noordzee in het voorjaar en najaar.'),
       ('surfwax-koel', 'Surfwax koel water', ZAND, 'KOEL WATER', '14 tot 19 graden', 'Voor de Noordzee in de zomer en de Atlantische kust.'),
       ('surfwax-warm', 'Surfwax warm water', ROSE, 'WARM WATER', 'boven 19 graden', 'Voor Portugal in de zomer en verder weg.')]
for handle, titel, kleur, label, temp, waar in WAX:
    P.append(dict(
        handle=handle, titel=titel, type='Surfwax', collectie='Surfgear', prijs='4.50', gram=80, tags=['wax', 'gear'],
        tekst=f'<p>Blok surfwax voor watertemperaturen {temp}. {waar}</p><p>Tip: begin met een basislaag en wax daarna in kleine rondjes tot je goede grip hebt.</p>' + VERZENDING,
        seo_titel=f'{titel} ({temp}) | Tide-Tode',
        seo_tekst=f'Surfwax voor water {temp}. Voor goede grip op je softtop of hardboard.',
        beelden=[('pack', lambda k=kleur, l=label, h=handle: (wax(k, l, h.replace('-', '')), '0 0 600 600', 1750, 0), '#EFE5D3', titel.replace('Surfwax ', ''), f'Blok {titel.lower()} met het Tide-Tode label'),
                 ('sfeer', lambda k=kleur, l=label, h=handle: (wax(k, l, h.replace('-', '') + 's'), '0 0 600 600', 1150, 0), 'Wax on, wax off', f'{titel} als sticker op een foto van de zee')]))

GEAR = [
    dict(handle='waxkam', titel='Waxkam', type='Surfgear', prijs='5.00', gram=30, tags=['wax', 'gear'],
         tekst='<p>Kam en schraper in één. Met de tanden maak je oude wax weer ruw voor meer grip. Met de rechte kant haal je wax eraf als je opnieuw wilt beginnen.</p>',
         seo_tekst='Waxkam met schraper om je surfwax ruw te maken of eraf te halen.',
         svg=lambda: (kam(), '0 0 600 600', 1650, 0), achter=BABY, label='Waxkam', alt='Navy waxkam met het Tide-Tode icoon', regel='Meer grip'),
    dict(handle='karabijnhaak-messing', titel='Karabijnhaak messing', type='Surfgear', prijs='9.00', gram=40, tags=['karabijnhaak', 'gear'],
         tekst='<p>Karabijnhaak van messing. Handig voor je sleutels, een waterfles of je slippers aan je tas.</p><p>Niet geschikt om te klimmen.</p>',
         seo_tekst='Messing karabijnhaak voor sleutels, waterfles of slippers aan je tas.',
         svg=lambda: (karabijn('#B48A3E', '#E9CF8E', 'm'), '0 0 600 600', 1450, 0), achter=ROSE, label='Messing', alt='Messing karabijnhaak', regel='Alles aan je tas'),
    dict(handle='karabijnhaak-zwart', titel='Karabijnhaak zwart', type='Surfgear', prijs='8.00', gram=40, tags=['karabijnhaak', 'gear'],
         tekst='<p>Karabijnhaak in mat zwart metaal. Handig voor je sleutels, een waterfles of je slippers aan je tas.</p><p>Niet geschikt om te klimmen.</p>',
         seo_tekst='Zwarte karabijnhaak voor sleutels, waterfles of slippers aan je tas.',
         svg=lambda: (karabijn('#2B2F36', '#6B7280', 'z'), '0 0 600 600', 1450, 0), achter=ZAND, label='Mat zwart', alt='Zwarte karabijnhaak', regel='Alles aan je tas'),
    dict(handle='stickerset', titel='Stickerset', type='Stickers', prijs='6.00', gram=20, tags=['stickers', 'gear', 'cadeau'],
         tekst='<p>Zes vinyl stickers met onze tekeningen: golf, zon, schelp, palm, zeester en board. Waterbestendig, dus ook voor je board, fles of laptop.</p>',
         seo_tekst='Zes vinyl stickers van Tide-Tode: golf, zon, schelp, palm, zeester en board.',
         svg=lambda: (stickerset(), '0 0 600 600', 1250, -3), achter=BABY, label='Zes stickers', alt='Vel met zes Tide-Tode stickers', regel='Plak ze overal op'),
]
for g in GEAR:
    P.append(dict(handle=g['handle'], titel=g['titel'], type=g['type'], collectie='Surfgear', prijs=g['prijs'], gram=g['gram'], tags=g['tags'],
                  tekst=g['tekst'] + VERZENDING, seo_titel=f"{g['titel']} | Tide-Tode", seo_tekst=g['seo_tekst'],
                  beelden=[('pack', g['svg'], g['achter'], g['label'], g['alt']), ('sfeer', g['svg'], g['regel'], g['alt'] + ' als sticker op een foto van de zee')]))

exec(open(HIER / 'kleding.py', encoding='utf-8').read())


# ---------- beelden schrijven ----------
# Staat er een echte foto (png met transparante achtergrond) in docs/producten/fotos, dan gebruiken we die in plaats van de tekening.
FOTOS = DOCS / 'fotos'
FOTOS.mkdir(exist_ok=True)


def foto(handle, kant=''):
    for ext in ('png', 'webp', 'jpg'):
        f = FOTOS / f'{handle}{kant}.{ext}'
        if f.exists():
            return f
    return None


def met_foto(f, breedte):
    return (f'<image href="file://{f}" x="0" y="0" width="600" height="600" preserveAspectRatio="xMidYMid meet"/>', '0 0 600 600', breedte, 0)


for p in P:
    p['bestanden'] = []
    for i, b in enumerate(p['beelden'], 1):
        naam = f"{p['handle']}-{i}"
        soort = b[0]
        if soort == 'pack':
            f = foto(p['handle'], '-achter' if b[3] == 'Achterkant' else '')
            svg, vb, br, dr = met_foto(f, 1500) if f else b[1]()
            packshot(naam, b[2], svg, p['titel'] if len(p['titel']) < 26 else p['type'], b[3], vb, br, dr)
            alt = b[4]
        elif soort == 'macro':
            macro(naam, b[1], 'De stof')
            alt = b[2]
        else:
            f = foto(p['handle'], '-achter') or foto(p['handle'])
            svg, vb, br, dr = met_foto(f, 1450) if f else b[1]()
            sfeer(naam, svg, vb, br * .82, dr if dr else -6, b[2] if p['collectie'] == 'Draagtassen' else '')
            alt = b[3]
        p['bestanden'].append((naam + '.jpg', alt))

# ---------- csv ----------
KOP = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value',
       'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service',
       'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Image Src', 'Image Position', 'Image Alt Text',
       'Gift Card', 'SEO Title', 'SEO Description', 'Variant Weight Unit', 'Status']
rijen = []
for p in P:
    tags = ', '.join(p['tags'] + [p['collectie']])
    maten = p.get('maten') or [None]
    for vi, maat in enumerate(maten):
        r = dict.fromkeys(KOP, '')
        r['Handle'] = p['handle']
        if vi == 0:
            r.update({'Title': p['titel'], 'Body (HTML)': p['tekst'], 'Vendor': 'Tide-Tode', 'Type': p['type'], 'Tags': tags, 'Published': 'TRUE',
                      'Gift Card': 'FALSE', 'SEO Title': p['seo_titel'], 'SEO Description': p['seo_tekst'], 'Status': 'active'})
        r['Option1 Name'] = 'Maat' if maat else 'Title'
        r['Option1 Value'] = maat or 'Default Title'
        r.update({'Variant SKU': 'TT-' + p['handle'].upper() + (f'-{maat}' if maat else ''), 'Variant Grams': p['gram'], 'Variant Inventory Tracker': 'shopify',
                  'Variant Inventory Qty': 25, 'Variant Inventory Policy': 'deny', 'Variant Fulfillment Service': 'manual', 'Variant Price': p['prijs'],
                  'Variant Requires Shipping': 'TRUE', 'Variant Taxable': 'TRUE', 'Variant Weight Unit': 'g'})
        if vi < len(p['bestanden']):
            f, alt = p['bestanden'][vi]
            r.update({'Image Src': RAW + f, 'Image Position': vi + 1, 'Image Alt Text': alt})
        rijen.append(r)
    for bi in range(len(maten), len(p['bestanden'])):
        f, alt = p['bestanden'][bi]
        r = dict.fromkeys(KOP, '')
        r.update({'Handle': p['handle'], 'Image Src': RAW + f, 'Image Position': bi + 1, 'Image Alt Text': alt})
        rijen.append(r)
with open(DOCS / 'producten.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=KOP)
    w.writeheader(); w.writerows(rijen)

# ---------- overzicht ----------
regels = ['# Assortiment Tide-Tode', '', f'{len(P)} producten in 3 collecties. Importeren: Shopify admin, Producten, Importeren, `producten.csv`.', '',
          'De beelden zijn getekend in de merkstijl en worden bij de import van GitHub opgehaald. Vervang ze door echte foto\'s zodra die er zijn.', '']
for col in ('Draagtassen', 'Surfgear', 'Kleding en merch'):
    regels += [f'## {col}', '', '| Product | Prijs | Handle |', '|---|---|---|']
    regels += [f"| {p['titel']} | € {p['prijs'].replace('.', ',')} | `{p['handle']}` |" for p in P if p['collectie'] == col]
    regels.append('')
regels += ['## Collecties aanmaken', '',
           'Maak in Shopify drie automatische collecties (Producten, Collecties, Collectie maken, Automatisch):', '',
           '| Collectie | Voorwaarde | Handle |', '|---|---|---|',
           '| Draagtassen | Producttag is gelijk aan `Draagtassen` | `draagtassen` |',
           '| Surfgear | Producttag is gelijk aan `Surfgear` | `surfgear` |',
           '| Kleding en merch | Producttag is gelijk aan `Kleding en merch` | `kleding-en-merch` |', '',
           '## Nog controleren met Veerle', '',
           '- Prijzen (alleen de € 40 van de draagtas komt uit de intake, de rest is een voorstel).',
           '- Materialen en gewichten van de kleding, de UPF van het UV-shirt, maat handdoek en canvas tas.',
           '- Temperaturen van de wax.',
           '- Voorraad staat op 25 per variant als testwaarde.', '']
(DOCS / 'overzicht.md').write_text('\n'.join(regels))
print(len(P), 'producten,', sum(len(p['bestanden']) for p in P), 'beelden')

# ---------- prompts voor echte productfoto's ----------
TAS_EN = ('a surfboard carry bag. It is a trapezoid-shaped fabric sleeve that wraps around the middle of a cream surfboard, '
          'made of thick woven jacquard fabric with {kleur}. A wide padded {band} shoulder strap is stitched to the two top corners of the sleeve '
          'and forms a loop above it. There are NO other straps, NO buckles and NO extra belts around the board')
PATROON_EN = {
    'tegel': 'a square tile pattern in terracotta, dusty blue, rust and cream, each tile with a cream diamond and a small navy dot',
    'tegel-navy': 'a square tile pattern in navy, baby blue and cream, each tile with a diamond and a small dot',
    'golfjes': 'rows of baby blue wavy lines on navy',
    'zonsondergang': 'horizontal stripes in soft rose, sand, terracotta and cream',
    'schelp': 'a scallop shell scale pattern in soft rose with cream outlines',
    'ruit': 'a baby blue and cream checkerboard',
    'duin': 'diagonal stripes in sand and cream',
    'salie': 'a square tile pattern in sage green, sand and cream with small navy dots',
    'effen-navy': 'a plain navy colour with a subtle woven texture',
}
BAND_EN = {BLAUW: 'dusty blue', NAVY: 'navy', BABY: 'baby blue', TERRA: 'terracotta', ROSE: 'soft rose'}
OVERIG_EN = {
    'surfwax-koud': 'a rounded rectangular block of surf wax in pale baby blue, with a small cream paper label showing a navy surfboard icon and the text TIDE TODE KOUD WATER',
    'surfwax-koel': 'a rounded rectangular block of surf wax in warm sand colour, with a small cream paper label showing a navy surfboard icon and the text TIDE TODE KOEL WATER',
    'surfwax-warm': 'a rounded rectangular block of surf wax in soft rose, with a small cream paper label showing a navy surfboard icon and the text TIDE TODE WARM WATER',
    'waxkam': 'a navy plastic surf wax comb with a row of teeth on one side and a straight scraper edge, with a small cream surfboard icon printed on it',
    'karabijnhaak-messing': 'a brushed brass carabiner with a spring gate',
    'karabijnhaak-zwart': 'a matte black metal carabiner with a spring gate',
    'stickerset': 'a sheet of six die-cut vinyl stickers with white borders on cream paper: a blue wave, a sand coloured sun, a pink shell, a navy palm tree, a cream starfish and a pink camper van',
    'pet-navy': 'a navy cotton baseball cap with a small embroidered cream surfboard icon on the front',
    'bucket-hat-tegel': 'a cream cotton bucket hat with a terracotta band and a small embroidered navy surfboard icon',
    'strandhanddoek-tegel': 'a folded cotton beach towel with a tile pattern in terracotta, dusty blue, rust and cream and short fringes on the end',
    'canvas-tas': 'a cream heavy canvas tote bag with sand coloured handles and the stacked TIDE TODE logo printed in navy',
}
KLEDING_EN = {
    't-shirt-zonsopkomst': ('a cream heavyweight cotton t-shirt with a tiny navy surfboard icon on the left chest',
                            'the same cream t-shirt seen from the back, with a large screen print: a terracotta half sun with cream horizontal cut lines rising above three navy wave lines, the words TIDE TODE in an arc above it and HANDEN VRIJ OP WEG NAAR ZEE in small type below'),
    't-shirt-stickers': ('a navy heavyweight cotton t-shirt with the small stacked cream TIDE TODE logo on the left chest',
                         'the same navy t-shirt seen from the back, with a print of six colourful sticker illustrations (wave, sun, shell, palm, starfish, camper van) and the small text TIDE TODE SURF CLUB below'),
    'longsleeve-golf': ('a cream cotton long sleeve t-shirt with a tiny navy surfboard icon on the chest and the words HANDEN VRIJ printed vertically along the left sleeve',
                        'the same cream long sleeve seen from the back, with a large navy single-line drawing of a curling wave and the words HANDEN VRIJ below'),
    'longsleeve-tegel': ('a navy cotton long sleeve t-shirt with one small tile print on the chest',
                         'the same navy long sleeve seen from the back, with a large rectangular tile print in terracotta, dusty blue, rust and cream and the cream stacked TIDE TODE logo below'),
    'uv-shirt-lange-mouw': ('a navy fitted long sleeve surf rash vest with flatlock seams, the cream stacked TIDE TODE logo on the chest and tile pattern cuffs in terracotta, dusty blue and cream',
                            'the same navy rash vest seen from the back, with a small cream surfboard icon and TIDE TODE between the shoulders'),
    'hoodie-busje': ('a heavyweight baby blue cotton hoodie with kangaroo pocket, navy drawstrings and the small stacked navy TIDE TODE logo on the chest',
                     'the same baby blue hoodie seen from the back, with a large navy single-line drawing of a camper van with a surfboard on the roof and OP WEG NAAR ZEE below'),
    'surfponcho-tegel': ('a sea blue terry cotton surf changing poncho with hood and short wide sleeves, a tile pattern border at the bottom hem and a small cream surfboard icon on the chest',
                         'the same sea blue surf poncho seen from the back, with the large cream stacked TIDE TODE logo and the tile pattern border at the bottom'),
}
STIJL = ('Photorealistic studio product photo. Straight front view, the whole product centred with generous margin, soft natural daylight from the upper left, '
         'subtle realistic shadow under the product, true-to-life fabric texture and stitching. Transparent background, PNG, portrait 1600 x 2000 pixels. '
         'Match the attached drawing exactly in shape, colours and print. No added text, no extra logos, no props, no people, no watermark.')
regels = ['# Prompts voor echte productfoto\'s', '',
          'Zo maak je met ChatGPT een echte productfoto van elk product, waarna het script alle productbeelden opnieuw opbouwt met die foto.', '',
          '1. Open ChatGPT en upload de tekening die bij het product staat (link hieronder). Upload bij de draagtassen ook de fabrieksfoto van de tas, dan klopt de vorm beter.',
          '2. Plak de prompt. Vraag om een **png met transparante achtergrond**.',
          '3. Sla de foto op in `docs/producten/fotos/` met precies de naam die erbij staat. Bij kleding maak je twee foto\'s: voorkant en achterkant.',
          '4. Vraag mij om de productbeelden opnieuw te maken. Het script zet je foto dan in de packshot, het sfeerbeeld met stickerrand en alle labels.', '',
          'Let op: een AI-foto is een visualisatie. Laat de echte tas en kleding later fotograferen, zodat klanten zien wat ze krijgen.', '']
for p in P:
    h = p['handle']
    regels += [f"## {p['titel']}", '', f"Tekening: {RAW}{h}-1.jpg", '']
    if p['collectie'] == 'Draagtassen':
        t = next(x for x in TASSEN if x[0] == h)
        wat = TAS_EN.format(kleur=PATROON_EN[t[2]], band=BAND_EN.get(t[3], 'dusty blue'))
        regels += [f'Opslaan als `{h}.png`', '', '```', f'Use the attached drawing and photo as reference. Create {wat}. Show it standing upright on the tail of the surfboard, nose up. {STIJL}', '```', '']
    elif h in KLEDING_EN:
        voor, achter = KLEDING_EN[h]
        regels += [f'Voorkant, opslaan als `{h}.png`', '', '```', f'Use the attached drawing as reference. Create a flat lay of {voor}, laid out neatly and seen from above. {STIJL}', '```', '',
                   f'Achterkant, opslaan als `{h}-achter.png` (tekening: {RAW}{h}-2.jpg)', '', '```', f'Use the attached drawing as reference. Create a flat lay of {achter}, laid out neatly and seen from above. {STIJL}', '```', '']
    else:
        regels += [f'Opslaan als `{h}.png`', '', '```', f'Use the attached drawing as reference. Create {OVERIG_EN[h]}. {STIJL}', '```', '']
(DOCS / 'chatgpt-prompts.md').write_text('\n'.join(regels))
