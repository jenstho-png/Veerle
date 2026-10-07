import pathlib
"""Bouwt het Tide-Tode brandbook (branding 2) als één HTML-bestand.
Posterpagina's in 4:5, alles schaalt mee met de breedte (container query units).
Fonts en foto's gaan als data-URI mee, zodat de pagina los te delen is."""
import base64, json, math, pathlib
import stickers as ST
import tas as TAS

HIER = pathlib.Path(__file__).parent
ASSETS = HIER.parent.parent / 'theme' / 'assets'
UIT = HIER.parent.parent / 'docs' / 'brandbook' / 'brandbook-2.html'

NAVY, CREME, BABY, ROSE, ZAND, PAPIER = '#22324F', '#F3ECDD', '#BFD3EA', '#EDBDB8', '#E3CFAE', '#FBF7EF'
LOGO = json.load(open(HIER / 'logo2.json'))
ILL = json.load(open(HIER / 'illustraties.json'))
STK = {s['naam']: s for s in json.load(open(HIER / 'stickers.json'))}


def b64(pad, mime):
    return f'data:{mime};base64,' + base64.b64encode(pathlib.Path(pad).read_bytes()).decode()


def foto(naam):
    return b64(HIER / 'foto' / f'{naam}.jpg', 'image/jpeg')


def productfoto(pad, breedte=900):
    """Foto uit docs/producten, verkleind zodat het merkboek licht blijft."""
    import io
    from PIL import Image
    im = Image.open(pad).convert('RGB')
    im = im.resize((breedte, int(im.height * breedte / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def logo(soort, kleur, cls='', stijl=''):
    l = LOGO[soort]
    return f'<svg class="{cls}" style="{stijl}" viewBox="0 0 {l["w"]} {l["h"]}" role="img" aria-label="Tide Tode"><path fill="{kleur}" d="{l["d"]}"/></svg>'


def icoon(kleur, cls='', stijl=''):
    b = LOGO['board']
    return f'<svg class="{cls}" style="{stijl}" viewBox="0 0 {b["w"]} {b["h"]}" aria-hidden="true"><path fill="{kleur}" d="{b["d"]}"/></svg>'


def icsticker(naam, stijl, rond=False):
    l = LOGO[naam]
    m = 26
    vorm = f'<path fill-rule="evenodd" d="{l["d"]}"/>'
    rand = (f'<circle cx="{l["w"]/2}" cy="{l["h"]/2}" r="{max(l["w"], l["h"])/2 + m}" fill="{PAPIER}"/>' if rond else
            f'<rect x="{-m}" y="{-m}" width="{l["w"] + 2*m}" height="{l["h"] + 2*m}" rx="{60 + m}" fill="{PAPIER}"/>')
    return (f'<svg class="badge" style="position:absolute;{stijl}" viewBox="{-m - 4} {-m - 4} {l["w"] + 2*m + 8} {l["h"] + 2*m + 8}" aria-hidden="true">'
            f'{rand}<g fill="{NAVY}">{vorm}</g></svg>')


def tekening(naam, kleur, cls=''):
    t = ILL[naam]
    paden = ''.join(f'<path d="{p}"/>' for p in t['d'])
    return f'<svg class="{cls}" viewBox="{t["vb"]}" fill="none" stroke="{kleur}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paden}</svg>'


def sticker(naam, cls='', stijl=''):
    s = ST.svg(STK[naam])
    return s.replace('<svg ', f'<svg class="{cls}" style="{stijl}" aria-hidden="true" ', 1)


def board_in(cx, cy, hoogte, kleur):
    b = LOGO['board']
    s = hoogte / b['h']
    return f'<path transform="translate({cx - b["w"] * s / 2:.1f} {cy - hoogte / 2:.1f}) scale({s:.4f})" fill="{kleur}" d="{b["d"]}"/>'


def logo_in(soort, x, y, breedte, kleur):
    l = LOGO[soort]
    s = breedte / l['w']
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" fill="{kleur}" d="{l["d"]}"/>'


# ---------- logostickers ----------
def glans(vorm):
    """Vinyl: een zachte glans over de sticker, geknipt op de buitenvorm."""
    uid = abs(hash(vorm)) % 99999
    return (f'<defs><linearGradient id="gl{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".32"/>'
            f'<stop offset=".38" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".06"/></linearGradient>'
            f'<clipPath id="cl{uid}">{vorm}</clipPath></defs><rect x="-50" y="-50" width="1200" height="1200" fill="url(#gl{uid})" clip-path="url(#cl{uid})"/>')


def ster(cx, cy, r, kleur):
    pts = ' '.join(f'{cx + (r if i % 2 == 0 else r * .38) * math.cos(math.pi / 4 * i - math.pi / 2):.1f},{cy + (r if i % 2 == 0 else r * .38) * math.sin(math.pi / 4 * i - math.pi / 2):.1f}' for i in range(8))
    return f'<polygon points="{pts}" fill="{kleur}"/>'


def zegel(achter=ROSE, voor=NAVY, rand=PAPIER):
    return f'''<svg viewBox="0 0 340 340" class="badge" aria-hidden="true">
  <circle cx="170" cy="170" r="168" fill="{rand}"/><circle cx="170" cy="170" r="154" fill="{achter}"/>
  <circle cx="170" cy="170" r="142" fill="none" stroke="{voor}" stroke-width="2" stroke-dasharray="2 6" opacity=".55"/>
  <defs><path id="zb" d="M58 170a112 112 0 0 1 224 0"/><path id="zo" d="M40 170a130 130 0 0 0 260 0"/></defs>
  <text font-family="Courier Prime, monospace" font-weight="700" font-size="31" letter-spacing="11" fill="{voor}"><textPath href="#zb" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>
  <text font-family="Courier Prime, monospace" font-weight="700" font-size="22" letter-spacing="8" fill="{voor}"><textPath href="#zo" startOffset="50%" text-anchor="middle">HANDEN VRIJ</textPath></text>
  {ster(40, 170, 9, voor)}{ster(300, 170, 9, voor)}
  {board_in(170, 172, 132, voor)}
  {glans('<circle cx="170" cy="170" r="168"/>')}
</svg>'''


def ovaal():
    """Klassieke surfshop-ovaal: tekst langs de rand, logo in het midden."""
    return f'''<svg viewBox="0 0 520 330" class="badge" aria-hidden="true">
  <ellipse cx="260" cy="165" rx="258" ry="163" fill="{PAPIER}"/>
  <ellipse cx="260" cy="165" rx="244" ry="149" fill="{NAVY}"/>
  <ellipse cx="260" cy="165" rx="178" ry="92" fill="{CREME}"/>
  <defs><path id="ovb" d="M60 165 A200 118 0 0 1 460 165"/><path id="ovo" d="M48 165 A212 130 0 0 0 472 165"/></defs>
  <text font-family="Courier Prime, monospace" font-weight="700" font-size="22" letter-spacing="9" fill="{CREME}"><textPath href="#ovb" startOffset="50%" text-anchor="middle">SURFBOARD DRAAGTAS</textPath></text>
  <text font-family="Courier Prime, monospace" font-weight="700" font-size="19" letter-spacing="7" fill="{BABY}"><textPath href="#ovo" startOffset="50%" text-anchor="middle">HANDEN VRIJ</textPath></text>
  {ster(46, 165, 9, BABY)}{ster(474, 165, 9, BABY)}
  {logo_in('liggend', 120, 143, 280, NAVY)}
  {glans('<ellipse cx="260" cy="165" rx="258" ry="163"/>')}
</svg>'''


# ---------- extra stickers ----------
def zonsondergang_sticker():
    kl = [ROSE, ZAND, '#C0603E', CREME]
    banen = ''.join(f'<rect x="0" y="{150 + k * 26}" width="340" height="16" fill="{kl[k % 3 + (1 if k > 2 else 0) - (1 if k > 2 else 0)]}"/>' for k in range(5))
    return f'''<svg viewBox="0 0 340 340" class="badge" aria-hidden="true">
  <rect x="2" y="2" width="336" height="336" rx="60" fill="{PAPIER}"/>
  <defs><clipPath id="zsk"><rect x="16" y="16" width="308" height="308" rx="48"/></clipPath></defs>
  <g clip-path="url(#zsk)">
    <rect width="340" height="340" fill="{CREME}"/>
    <circle cx="170" cy="200" r="104" fill="#C0603E"/>
    {''.join(f'<rect x="0" y="{196 + k * 22}" width="340" height="{9 + k * 2}" fill="{CREME}"/>' for k in range(6))}
    <rect x="0" y="262" width="340" height="80" fill="{NAVY}"/>
  </g>
  {board_in(170, 168, 150, NAVY)}
  <text x="170" y="304" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="22" letter-spacing="8" fill="{CREME}">TIDE TODE</text>
  {glans('<rect x="2" y="2" width="336" height="336" rx="60"/>')}
</svg>'''


def boog_sticker():
    t = ILL['golf']
    paden = ''.join(f'<path d="{p}"/>' for p in t['d'])
    vorm = 'M20 330 L20 170 A150 150 0 0 1 320 170 L320 330 Z'
    return f'''<svg viewBox="0 0 340 350" class="badge" aria-hidden="true">
  <path d="M6 344 L6 170 A164 164 0 0 1 334 170 L334 344 Z" fill="{PAPIER}"/>
  <path d="{vorm}" fill="{BABY}"/>
  <circle cx="170" cy="150" r="46" fill="{ZAND}"/>
  <g transform="translate(40 128) scale(.65)" fill="none" stroke="{NAVY}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">{paden}</g>
  <rect x="20" y="266" width="300" height="64" fill="{NAVY}"/>
  <text x="170" y="306" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="20" letter-spacing="6" fill="{CREME}">OP WEG NAAR ZEE</text>
  {glans('<path d="M6 344 L6 170 A164 164 0 0 1 334 170 L334 344 Z"/>')}
</svg>'''


def tegelcirkel_sticker():
    tegels = ''
    kl = ['#C0603E', BABY, CREME, '#9E3B2E', BABY, '#C0603E', CREME]
    for r in range(8):
        for k in range(8):
            x, y = k * 44, r * 44
            c = kl[(r * 3 + k) % len(kl)]
            b = CREME if c != CREME else '#C0603E'
            tegels += f'<rect x="{x}" y="{y}" width="44" height="44" fill="{c}"/><path d="M{x + 22} {y + 6}L{x + 38} {y + 22}L{x + 22} {y + 38}L{x + 6} {y + 22}Z" fill="{b}"/><circle cx="{x + 22}" cy="{y + 22}" r="5" fill="{NAVY}"/>'
    return f'''<svg viewBox="0 0 340 340" class="badge" aria-hidden="true">
  <circle cx="170" cy="170" r="168" fill="{PAPIER}"/>
  <defs><clipPath id="tck"><circle cx="170" cy="170" r="154"/></clipPath></defs>
  <g clip-path="url(#tck)">{tegels}</g>
  <circle cx="170" cy="170" r="70" fill="{NAVY}" stroke="{PAPIER}" stroke-width="8"/>
  {board_in(170, 170, 96, CREME)}
  {glans('<circle cx="170" cy="170" r="168"/>')}
</svg>'''


def vaantje_sticker():
    vorm = 'M20 40 L470 110 L20 180 Z'
    return f'''<svg viewBox="0 0 490 220" class="badge" aria-hidden="true">
  <path d="M4 22 L4 198 L488 110 Z" fill="{PAPIER}" stroke="{PAPIER}" stroke-width="14" stroke-linejoin="round"/>
  <path d="{vorm}" fill="{NAVY}"/>
  <rect x="20" y="40" width="22" height="140" fill="#C0603E"/>
  <text x="66" y="100" font-family="Courier Prime, monospace" font-weight="700" font-size="18" letter-spacing="7" fill="{BABY}">SURF CLUB</text>
  {logo_in('liggend', 64, 116, 168, CREME)}
  {glans('<path d="M4 22 L4 198 L488 110 Z"/>')}
</svg>'''


def postzegel_sticker():
    gaatjes = ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="{PAPIER}"/>' for x in range(16, 300, 22) for y in (12, 368)) + ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="{PAPIER}"/>' for y in range(34, 350, 22) for x in (12, 288))
    tas = TAS.lijn().replace('<svg ', '<svg x="34" y="70" width="232" height="116" ', 1)
    return f'''<svg viewBox="0 0 300 380" class="badge" aria-hidden="true">
  <rect x="0" y="0" width="300" height="380" fill="{PAPIER}"/>
  <rect x="20" y="20" width="260" height="340" fill="{CREME}"/>
  {gaatjes}
  <rect x="30" y="30" width="240" height="320" fill="none" stroke="{NAVY}" stroke-width="2"/>
  {tas}
  <text x="150" y="250" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="20" letter-spacing="6" fill="{NAVY}">TIDE TODE</text>
  <text x="150" y="282" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="14" letter-spacing="4" fill="{NAVY}">DRAAGTAS</text>
  <text x="150" y="330" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="14" letter-spacing="5" fill="#C0603E">EST 2025</text>
  {glans('<rect x="0" y="0" width="300" height="380"/>')}
</svg>'''


def ruit_sticker():
    ruit = ''.join(f'<rect x="{x}" y="{y}" width="20" height="20" fill="{NAVY if (x // 20 + y // 20) % 2 else CREME}"/>' for x in range(16, 504, 20) for y in (16, 36))
    ruit += ''.join(f'<rect x="{x}" y="{y}" width="20" height="20" fill="{NAVY if (x // 20 + y // 20) % 2 else CREME}"/>' for x in range(16, 504, 20) for y in (124, 144))
    return f'''<svg viewBox="0 0 520 180" class="badge" aria-hidden="true">
  <rect x="2" y="2" width="516" height="176" rx="24" fill="{PAPIER}"/>
  <defs><clipPath id="rk"><rect x="16" y="16" width="488" height="148" rx="12"/></clipPath></defs>
  <g clip-path="url(#rk)"><rect x="0" y="0" width="520" height="180" fill="{ROSE}"/>{ruit}</g>
  {logo_in('liggend', 120, 70, 280, NAVY)}
  {glans('<rect x="2" y="2" width="516" height="176" rx="24"/>')}
</svg>'''


def pil():
    return f'''<svg viewBox="0 0 520 170" class="badge" aria-hidden="true">
  <rect x="2" y="2" width="516" height="166" rx="83" fill="{PAPIER}"/>
  <rect x="14" y="14" width="492" height="142" rx="71" fill="{NAVY}"/>
  {ster(62, 85, 10, BABY)}{ster(458, 85, 10, BABY)}
  {logo_in('liggend', 98, 62, 324, CREME)}
  {glans('<rect x="2" y="2" width="516" height="166" rx="83"/>')}
</svg>'''


def tegelsticker():
    """Sticker van een echte tegel uit de stof van de tas."""
    tegel = b64(HIER.parent.parent / 'docs' / 'producten' / 'fabriek' / 'tegels-2x2.png', 'image/png')
    return f'''<svg viewBox="0 0 300 340" class="badge" aria-hidden="true">
  <rect x="2" y="2" width="296" height="336" rx="34" fill="{PAPIER}"/>
  <defs><clipPath id="tgk"><rect x="16" y="16" width="268" height="308" rx="22"/></clipPath></defs>
  <image href="{tegel}" x="16" y="16" width="268" height="308" preserveAspectRatio="xMidYMid slice" clip-path="url(#tgk)"/>
  {glans('<rect x="2" y="2" width="296" height="336" rx="34"/>')}
</svg>'''


def labelsticker():
    """Zoals het geweven label op de tas."""
    steek = ''.join(f'<line x1="{x}" y1="22" x2="{x + 7}" y2="22"/><line x1="{x}" y1="218" x2="{x + 7}" y2="218"/>' for x in range(26, 330, 13))
    return f'''<svg viewBox="0 0 360 240" class="badge" aria-hidden="true">
  <rect x="2" y="2" width="356" height="236" rx="16" fill="{PAPIER}"/>
  <rect x="12" y="12" width="336" height="216" rx="6" fill="{NAVY}"/>
  <g stroke="{BABY}" stroke-width="2" opacity=".7">{steek}</g>
  {logo_in('gestapeld', 92, 58, 176, CREME)}
  <text x="180" y="196" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="15" letter-spacing="6" fill="{BABY}">EST 2025</text>
  {glans('<rect x="2" y="2" width="356" height="236" rx="16"/>')}
</svg>'''


def golfrand():
    pts = []
    for i in range(0, 361, 2):
        a = math.radians(i)
        r = 150 + 7 * math.cos(a * 16)
        pts.append(f'{170 + r * math.cos(a):.1f},{170 + r * math.sin(a):.1f}')
    pts2 = []
    for i in range(0, 361, 2):
        a = math.radians(i)
        r = 163 + 7 * math.cos(a * 16)
        pts2.append(f'{170 + r * math.cos(a):.1f},{170 + r * math.sin(a):.1f}')
    g = LOGO['icoonGolf']
    s = 170 / g['w']
    return f'''<svg viewBox="0 0 340 340" class="badge" aria-hidden="true">
  <polygon points="{' '.join(pts2)}" fill="{PAPIER}"/><polygon points="{' '.join(pts)}" fill="{NAVY}"/>
  <path transform="translate({170 - g['w'] * s / 2:.1f} 62) scale({s:.4f})" fill="{CREME}" fill-rule="evenodd" d="{g['d']}"/>
  <text x="170" y="262" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="24" letter-spacing="8" fill="{CREME}">EST 2025</text>
  {glans('<polygon points="' + ' '.join(pts2) + '"/>')}
</svg>'''



def constructie():
    l = LOGO['liggend']
    s = 820 / l['w']
    h = l['h'] * s
    y0 = 560
    lijnen = ''
    for y in (y0 - 70, y0 - 30, y0 + h + 30, y0 + h + 70):
        lijnen += f'<line x1="-200" x2="1200" y1="{y:.0f}" y2="{y:.0f}"/>'
    for x in (70, 930):
        lijnen += f'<line x1="{x}" x2="{x}" y1="-300" y2="1500"/>'
    lab = lambda x, y, t, a='start': f'<text x="{x}" y="{y:.0f}" text-anchor="{a}">{t}</text>'
    return f'''<svg viewBox="0 0 1000 1250" class="vol" aria-label="Constructie van het liggende logo">
  <rect width="1000" height="1250" fill="{PAPIER}"/>
  <g transform="rotate(-12 500 625)">
    <g stroke="{NAVY}" stroke-width="2" stroke-dasharray="7 7" fill="none">{lijnen}</g>
    {logo_in('liggend', 90, y0, 820, NAVY)}
    <g font-family="Courier Prime, monospace" font-size="26" letter-spacing="3" fill="{NAVY}">
      {lab(90, y0 - 42, 'EST 2025')}{lab(910, y0 - 42, 'SURFBOARD / DRAAGTAS', 'end')}
      {lab(90, y0 + h + 58, 'HANDEN VRIJ')}{lab(500, y0 + h + 58, 'VAN SURFERS', 'middle')}{lab(910, y0 + h + 58, 'VOOR SURFERS', 'end')}
    </g>
  </g>
</svg>'''


def patroon():
    vormen = []
    plek = [('zon', 130, 150, 0.55, 0), ('golf', 520, 170, 0.62, -6), ('schelp', 850, 140, 0.55, 8), ('palm', 140, 520, 0.6, -4),
            ('zeester', 480, 520, 0.6, 14), ('board', 830, 540, 0.55, 10), ('busje', 220, 880, 0.58, -3), ('wax', 600, 900, 0.5, 6),
            ('schelp', 880, 930, 0.45, -12), ('zeester', 110, 1130, 0.4, -10), ('golf', 880, 1130, 0.45, 4)]
    for naam, x, y, sc, r in plek:
        s = STK[naam]
        vx, vy, vw, vh = map(float, s['vb'].split())
        vormen.append(f'<path transform="translate({x} {y}) rotate({r}) scale({sc}) translate({-(vx + vw / 2):.0f} {-(vy + vh / 2):.0f})" fill="{CREME}" d="{s["vorm"]}"/>')
    return f'<svg viewBox="0 0 1000 1250" class="vol" aria-label="Patroon met de vormen uit de stickers"><rect width="1000" height="1250" fill="{NAVY}"/>{"".join(vormen)}</svg>'


def bouw():
    fonts = f'''
@font-face {{ font-family: 'Tide Tode Display'; src: url({b64(ASSETS / 'tide-tode-display.woff2', 'font/woff2')}) format('woff2'); }}
@font-face {{ font-family: 'Courier Prime'; src: url({b64(ASSETS / 'courierprime-regular.woff2', 'font/woff2')}) format('woff2'); font-weight: 400; }}
@font-face {{ font-family: 'Courier Prime'; src: url({b64(ASSETS / 'courierprime-bold.woff2', 'font/woff2')}) format('woff2'); font-weight: 700; }}
@font-face {{ font-family: 'Homemade Apple'; src: url({b64(ASSETS / 'homemadeapple-regular.woff2', 'font/woff2')}) format('woff2'); }}'''

    css = '''
/* Posterboek: elke pagina is een 4:5-poster; maten in cqw schalen mee met de breedte. */
:root {
  --navy: #22324F; --creme: #F3ECDD; --papier: #FBF7EF; --baby: #BFD3EA; --rose: #EDBDB8; --zand: #E3CFAE; --grond: #E9E2D3;
  --display: 'Tide Tode Display', 'Cooper Black', Georgia, serif;
  --mono: 'Courier Prime', 'Courier New', Courier, monospace;
  --hand: 'Homemade Apple', 'Brush Script MT', cursive;
  color-scheme: light;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--grond); color: var(--navy); font-family: var(--mono); padding: 32px 16px 64px; }
.boek { display: grid; gap: 28px; justify-items: center; }
.kop { width: min(100%, 880px); display: flex; justify-content: space-between; align-items: baseline; gap: 16px; flex-wrap: wrap; font-size: 13px; letter-spacing: .14em; text-transform: uppercase; }
.kop strong { font-family: var(--display); font-weight: 400; font-size: 22px; letter-spacing: .08em; }
.pagina { position: relative; width: min(100%, 880px); aspect-ratio: 4 / 5; overflow: hidden; container-type: inline-size; background: var(--papier); box-shadow: 0 30px 60px -40px rgba(34, 50, 79, .55); }
.pagina > img.bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
svg.vol { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.m { font-family: var(--mono); }
.label { font: 400 1.5cqw/1.4 var(--mono); letter-spacing: .16em; text-transform: uppercase; }
.hand { font-family: var(--hand); }
.onderschrift { width: min(100%, 880px); font-size: 13px; line-height: 1.6; max-width: 880px; }

/* 1 cover */
.cover::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(20, 28, 44, .25) 0%, rgba(20, 28, 44, 0) 30%, rgba(20, 28, 44, .1) 55%, rgba(20, 28, 44, .62) 100%); }
.cover > * { z-index: 1; }
.cover .boven { position: absolute; top: 5cqw; left: 6cqw; right: 6cqw; display: flex; justify-content: space-between; color: var(--navy); }
.cover .woordmerk { position: absolute; left: 6cqw; bottom: 26cqw; width: 44cqw; }
.cover .slogan { position: absolute; left: 8cqw; bottom: 17cqw; margin: 0; color: var(--creme); font-size: 2.8cqw; transform: rotate(-5deg); }
.cover .tekst { position: absolute; right: 6cqw; bottom: 7cqw; width: 33cqw; color: var(--creme); font: 400 1.75cqw/1.5 var(--mono); }
.cover .tekst .regel { display: flex; justify-content: space-between; margin-top: 2cqw; font: 400 2.2cqw var(--hand); }

/* 3 logofamilie */
.familie { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; height: 100%; }
.familie > div { position: relative; display: grid; place-items: center; }
.familie > div > svg { width: 62%; }
.familie .label { position: absolute; left: 4cqw; bottom: 3.4cqw; }
.familie .duo { display: flex; align-items: center; gap: 5cqw; width: 78%; }
.familie .duo svg:first-child { width: 7%; } .familie .duo svg:last-child { width: 80%; }
.metic { display: grid; justify-items: center; gap: 3cqw; width: 62%; }
.metic svg:first-child { height: 9cqw; width: auto; } .metic svg:last-child { width: 100%; }
.cover .icoon { position: absolute; left: 7cqw; bottom: 57cqw; height: 10cqw; width: auto; }

/* 4 kleur en letter */
.kleur { display: grid; grid-template-columns: repeat(5, 1fr); height: 52%; }
.kleur > div { position: relative; padding: 3cqw 2cqw; display: flex; flex-direction: column; justify-content: flex-end; gap: .6cqw; }
.kleur .naam { font: 700 1.6cqw var(--mono); letter-spacing: .14em; text-transform: uppercase; }
.kleur .hex { font: 400 1.5cqw var(--mono); letter-spacing: .08em; }
.letters { padding: 4.5cqw 6cqw; display: grid; gap: 3.2cqw; }
.letters .rij { display: grid; grid-template-columns: 24cqw 1fr; align-items: baseline; gap: 3cqw; border-top: 1px dashed var(--navy); padding-top: 2.2cqw; }
.letters .proef-d { font: 400 6.4cqw/1 var(--display); letter-spacing: .06em; }
.letters .proef-m { font: 400 2.1cqw/1.45 var(--mono); }
.letters .proef-h { font: 400 3.6cqw/1.2 var(--hand); }

/* 5 en 6 stickers */
.stickers .s { position: absolute; filter: drop-shadow(0 .6cqw 1cqw rgba(0, 0, 0, .25)); }
.stickers .voet { position: absolute; left: 0; right: 0; bottom: 4cqw; text-align: center; color: var(--creme); }
.vel { background: var(--baby); display: grid; place-items: center; }
.vel__blad { position: relative; width: 90%; height: 92%; background: #FFFDF8; border-radius: 1.6cqw; box-shadow: 0 1.4cqw 3cqw rgba(34, 50, 79, .22); }
.vel__kop { position: absolute; left: 0; right: 0; top: 4cqw; margin: 0; text-align: center; font: 700 1.5cqw var(--mono); letter-spacing: .3em; color: var(--navy); }
.vel .badge { position: absolute; filter: drop-shadow(0 .15cqw .2cqw rgba(0, 0, 0, .18)); }
.badges .badge { position: absolute; filter: drop-shadow(0 .25cqw .25cqw rgba(0, 0, 0, .22)) drop-shadow(0 1.2cqw 1.8cqw rgba(60, 40, 20, .25)); }

/* 7 illustraties */
.ill { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto 1fr 1fr; height: 100%; padding: 6cqw; gap: 2cqw 4cqw; }
.ill h2 { grid-column: 1 / -1; margin: 0; font: 400 5.4cqw/1 var(--display); letter-spacing: .06em; }
.ill h2 + p { margin: 0; }
.ill figure { margin: 0; display: grid; align-content: center; justify-items: center; gap: 1cqw; }
.ill figure svg { width: 100%; }
.ill figcaption { font: 400 2.2cqw var(--hand); }

/* 8 grid */
.grid9 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-rows: repeat(3, minmax(0, 1fr)); height: 100%; }
.grid9 > * { min-height: 0; min-width: 0; }
.grid9 > img { width: 100%; height: 100%; object-fit: cover; }
.grid9 .tegel { background: var(--papier); padding: 3cqw; display: flex; flex-direction: column; justify-content: center; gap: 1cqw; }
.grid9 .tegel .hand { font-size: 2.6cqw; }
.grid9 .tegel .m { font-size: 1.55cqw; line-height: 1.6; letter-spacing: .1em; text-transform: uppercase; }
.grid9 .logo { align-items: center; gap: 1.5cqw; }
.grid9 .logo svg { width: 70%; }
.grid9 .logo .m { letter-spacing: .2em; }

/* 9 drukwerk */
.kaart-navy { position: absolute; left: 13cqw; right: 13cqw; top: 12cqw; height: 46cqw; background: var(--navy); overflow: hidden; box-shadow: 0 1.4cqw 3cqw rgba(0, 0, 0, .3); }
.kaart-navy .groot { position: absolute; left: 4cqw; right: 4cqw; top: 4cqw; }
.kaart-navy .links { position: absolute; left: 3cqw; bottom: 3cqw; color: var(--creme); font: 400 1.55cqw/1.6 var(--mono); }
.kaart-navy .rechts { position: absolute; right: 3cqw; bottom: 3cqw; color: var(--creme); font: 400 1.55cqw/1.6 var(--mono); display: grid; grid-template-columns: auto auto; gap: 0 1.6cqw; align-items: baseline; }
.kaart-navy .rechts .hand { font-size: 1.9cqw; }
.kaart-creme { position: absolute; left: 13cqw; right: 13cqw; top: 61cqw; height: 46cqw; background: var(--papier); display: grid; place-items: center; box-shadow: 0 1.4cqw 3cqw rgba(0, 0, 0, .3); }
.kaart-creme svg { width: 52%; }

/* 10 website */
.browser { position: absolute; left: 6cqw; right: 6cqw; top: 10cqw; bottom: 10cqw; background: var(--papier); border-radius: 1.2cqw; overflow: hidden; box-shadow: 0 2cqw 4cqw rgba(0, 0, 0, .3); display: flex; flex-direction: column; }
.browser .balk { height: 4cqw; display: flex; align-items: center; gap: .9cqw; padding: 0 2cqw; background: #e5ddcd; }
.browser .balk i { width: 1.1cqw; height: 1.1cqw; border-radius: 50%; background: #c9bfae; }
.browser .scherm { position: relative; flex: 1; }
.browser .scherm img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.browser .scherm::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(20, 28, 44, .35), rgba(20, 28, 44, 0) 30%, rgba(20, 28, 44, .6)); }
.browser .scherm > :not(img) { z-index: 1; }
.browser nav { position: absolute; top: 2.4cqw; left: 3cqw; right: 3cqw; display: flex; justify-content: space-between; align-items: center; color: var(--creme); font: 700 1.25cqw var(--mono); letter-spacing: .18em; }
.browser nav .links { display: flex; gap: 2.4cqw; }
.browser nav svg { width: 13cqw; }
.browser .hero-logo { position: absolute; left: 3cqw; bottom: 9cqw; width: 42cqw; }
.browser .hero-hand { position: absolute; left: 10cqw; bottom: 4.6cqw; color: var(--creme); font: 400 2.6cqw var(--hand); transform: rotate(-5deg); }
.browser .hero-tekst { position: absolute; right: 3cqw; bottom: 4cqw; width: 30cqw; color: var(--creme); font: 400 1.35cqw/1.55 var(--mono); }
.browser .knop { display: inline-block; margin-top: 1.6cqw; padding: 1.1cqw 2.2cqw; border-radius: 99px; background: var(--creme); color: var(--navy); font: 700 1.15cqw var(--mono); letter-spacing: .16em; }

/* drie iconen */
.drie { display: grid; grid-template-rows: auto 1fr auto; height: 100%; padding: 6cqw; gap: 3cqw; }
.drie h2, .tasp h2 { margin: 0; font: 400 5.4cqw/1 var(--display); letter-spacing: .04em; }
.drie .rij3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2cqw; }
.drie .kol { display: grid; grid-template-rows: 1fr 1fr auto; gap: 1.6cqw; }
.drie .tg { display: grid; place-items: center; }
.drie .tg svg { height: 55%; width: auto; max-width: 70%; }
.drie .rol { font: 400 1.55cqw/1.5 var(--mono); }
.drie .rol b { display: block; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; margin-bottom: .4cqw; }
/* de tas */
.fotop { display: grid; grid-template-rows: auto auto 1fr; height: 100%; padding: 6cqw; gap: 2.4cqw; }
.fotop h2 { margin: 0; font: 400 5.4cqw/1 var(--display); letter-spacing: .04em; }
.fotop p { margin: 0; font: 400 1.7cqw/1.5 var(--mono); max-width: 60ch; }
.fotogrid { display: grid; grid-template-columns: 1.5fr 1fr; grid-template-rows: 1fr 1fr; gap: 1.6cqw; min-height: 0; }
.fotogrid div, .negen figure div, .twee div { background-size: cover; background-position: center; }
.fotogrid .groot { grid-row: span 2; background-position: 78% 50% !important; }
.negen { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.4cqw; min-height: 0; }
.negen figure { margin: 0; display: grid; grid-template-rows: 1fr auto; gap: .8cqw; min-height: 0; }
.negen figcaption { font: 700 1.2cqw var(--mono); letter-spacing: .2em; }
.twee { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6cqw; min-height: 0; }
.tasp { display: grid; grid-template-rows: auto auto 1fr; height: 100%; padding: 6cqw; gap: 2.4cqw; }
.tasp .lijn svg { width: 100%; }
.tasp .foto { position: relative; background-size: cover; background-position: center; display: grid; place-items: center; }
.tasp .foto svg { width: 76%; transform: rotate(-6deg); filter: drop-shadow(0 1cqw 1.4cqw rgba(0,0,0,.25)); }
.tasp p { margin: 0; font: 400 1.7cqw/1.5 var(--mono); max-width: 60ch; }
@media (max-width: 600px) { body { padding-inline: 12px; } }
'''

    S = lambda n, l, t, w, r: sticker(n, 's', f'left:{l}cqw;top:{t}cqw;width:{w}cqw;transform:rotate({r}deg)')

    paginas = []
    # 1 cover
    paginas.append(f'''<section class="pagina cover" aria-label="Cover">
  <img class="bg" src="{foto('cover')}" alt="Twee surfers lopen met hun board naar zee bij zonsondergang">
  <div class="boven label"><span>Brandbook</span><span>Tide Tode 2025</span></div>
  {icoon(CREME, 'icoon')}
  {logo('gestapeld', CREME, 'woordmerk')}
  <p class="slogan hand">Handen vrij, op weg naar zee</p>
  <div class="tekst">Tide Tode maakt draagtassen voor surfboards. Bedacht op surftrips in Australië en Midden-Amerika, voor de wandeling door de duinen, de fiets naar het strand en de scooter naar een spot verderop.<div class="regel"><span>est.</span><span>2025</span></div></div>
</section>''')
    # 2 constructie
    paginas.append(f'<section class="pagina" aria-label="Logo constructie">{constructie()}</section>')
    # 3 familie
    paginas.append(f'''<section class="pagina" aria-label="Logofamilie"><div class="familie">
  <div style="background:var(--papier)"><div class="metic">{icoon(NAVY)}{logo('gestapeld', NAVY)}</div><span class="label">Hoofdlogo</span></div>
  <div style="background:var(--navy)"><div class="metic">{icoon(CREME)}{logo('gestapeld', CREME)}</div><span class="label" style="color:var(--creme)">Op donker</span></div>
  <div style="background:var(--baby)"><div class="duo"><svg viewBox="0 0 {LOGO['board']['w']} {LOGO['board']['h']}"><path fill="{NAVY}" d="{LOGO['board']['d']}"/></svg>{logo('liggend', NAVY)}</div><span class="label">Liggend met beeldmerk</span></div>
  <div style="background:var(--rose)">{zegel(achter=ROSE, rand=ROSE).replace('class="badge"', 'style="width:62%"')}<span class="label">Zegel</span></div>
</div></section>''')
    # 3b drie iconen
    def ic(naam, kleur):
        l = LOGO[naam]
        return f'<svg viewBox="0 0 {l["w"]} {l["h"]}"><path fill="{kleur}" fill-rule="evenodd" d="{l["d"]}"/></svg>'
    kol = lambda naam, titel, rol: f'<div class="kol"><div class="tg" style="background:var(--creme)">{ic(naam, NAVY)}</div><div class="tg" style="background:var(--navy)">{ic(naam, CREME)}</div><p class="rol"><b>{titel}</b>{rol}</p></div>'
    paginas.append(f'''<section class="pagina" aria-label="Drie iconen"><div class="drie">
  <h2>DRIE ICONEN, ÉÉN FAMILIE</h2>
  <div class="rij3">{kol('board', 'A, het board', 'Het hoofdicoon. Boven het logo, naast de liggende versie en op het label in de tas.')}{kol('icoonB', 'B, zon en zee', 'Het zegel. Profielfoto op Instagram, stempel op dozen en kaartjes.')}{kol('icoonC', 'C, de tegel', 'Klein en herkenbaar. Favicon, hanglabel en sticker, net als de tegelstof van de tas.')}</div>
  <p class="label">Navy op crème, of crème op navy. Altijd één icoon tegelijk.</p>
</div></section>''')
    # 3c de tas
    paginas.append(f'''<section class="pagina" aria-label="De draagtas"><div class="tasp">
  <h2>DE DRAAGTAS</h2>
  <p>Het board erin, het tegelpaneel eromheen en de schouderband omhoog. Als lijntekening voor kaartjes en uitleg, als sticker in de kleuren van de stof.</p>
  <div style="display:grid;grid-template-rows:1fr 1.2fr;gap:2cqw;min-height:0">
    <div class="lijn" style="background:var(--creme);display:grid;place-items:center;padding:2cqw">{TAS.lijn()}</div>
    <div class="foto" style="background-image:url({foto('zand')})">{TAS.sticker()}</div>
  </div>
</div></section>''')
    # 3d productfotografie
    PB = HIER.parent.parent / 'docs' / 'producten'
    paginas.append(f'''<section class="pagina" aria-label="Productfotografie"><div class="fotop">
  <h2>PRODUCTFOTO'S</h2>
  <p>Van bovenaf op een crème studiodoek. Altijd de echte stof, de band in een lus en het label zichtbaar. Eén vaste opstelling voor elk ontwerp.</p>
  <div class="fotogrid">
    <div class="groot" style="background-image:url({productfoto(PB / 'beelden' / 'draagtas-tegel-1.jpg', 1100)})"></div>
    <div style="background-image:url({productfoto(PB / 'beelden' / 'draagtas-tegel-3.jpg', 700)})"></div>
    <div style="background-image:url({productfoto(PB / 'beelden' / 'draagtas-tegel-2.jpg', 700)})"></div>
  </div>
</div></section>''')
    # 3e negen ontwerpen
    namen = ['tegel', 'tegel-navy', 'golfjes', 'zonsondergang', 'schelp', 'ruit', 'duin', 'salie', 'navy']
    tegels9 = ''.join(f'<figure><div style="background-image:url({productfoto(PB / "beelden" / f"draagtas-{n}-1.jpg", 520)})"></div><figcaption>{n.replace("-", " ").upper()}</figcaption></figure>' for n in namen)
    paginas.append(f'''<section class="pagina" aria-label="Negen ontwerpen"><div class="fotop">
  <h2>NEGEN ONTWERPEN</h2>
  <p>De schouderband krijgt per ontwerp een eigen kleur: dusty blue, navy, baby blue, terracotta of rose.</p>
  <div class="negen">{tegels9}</div>
</div></section>''')
    # 3f onderweg
    paginas.append(f'''<section class="pagina" aria-label="Onderweg"><div class="fotop">
  <h2>ONDERWEG</h2>
  <p>Sfeerbeelden: echte plekken, natuurlijk licht, de tas in gebruik. Geen poses, geen studio.</p>
  <div class="twee">
    <div style="background-image:url({productfoto(PB / 'fotos' / 'sfeer-zand-tegel.jpg', 800)})"></div>
    <div style="background-image:url({productfoto(PB / 'fotos' / 'sfeer-muur-tegel.jpg', 800)})"></div>
  </div>
</div></section>''')
    # 3g kleding en accessoires: echte productfoto's
    def raster(items):
        return ''.join(f'<figure><div style="background-image:url({productfoto(PB / "beelden" / f"{f}.jpg", 520)})"></div><figcaption>{t}</figcaption></figure>'
                       for f, t in items if (PB / 'beelden' / f'{f}.jpg').exists())
    kleding = [('t-shirt-board-2', 'BOARD'), ('t-shirt-zon-2', 'ZON'), ('t-shirt-golf-2', 'GOLF'),
               ('t-shirt-klassiek-2', 'KLASSIEK'), ('t-shirt-op-weg-naar-zee-2', 'OP WEG NAAR ZEE'), ('t-shirt-lijn-naar-zee-2', 'LIJN NAAR ZEE'),
               ('hoodie-twee-boards-2', 'HOODIE'), ('sweater-boards-1', 'SWEATER'), ('longsleeve-vin-1', 'LONGSLEEVE VIN')]
    paginas.append(f'''<section class="pagina" aria-label="Kleding"><div class="fotop">
  <h2>KLEDING</h2>
  <p>Zware shirts en truien van biologisch katoen. Op de rug een tekening in één of twee kleuren: een board, de zon, een golf. In de nek altijd ons eigen label.</p>
  <div class="negen">{raster(kleding)}</div>
</div></section>''')
    accessoires = [('karabijnhaak-messing-1', 'KARABIJNHAAK'), ('karabijnhaak-zwart-1', 'MAT ZWART'), ('pet-navy-1', 'PET'),
             ('bucket-hat-tegel-1', 'BUCKET HAT'), ('canvas-tas-1', 'CANVAS TAS'), ('stickerset-1', 'STICKERVEL'),
             ('surfwax-koud-1', 'SURF WAX'), ('strandhanddoek-tegel-1', 'HANDDOEK'), ('waxkam-1', 'WAXKAM')]
    paginas.append(f'''<section class="pagina" aria-label="Accessoires en gear"><div class="fotop">
  <h2>ACCESSOIRES EN GEAR</h2>
  <p>Kleine dingen met dezelfde zorg. De karabijnhaak heeft een lus van onze tasband met het geweven logo, de pet een geborduurd board.</p>
  <div class="negen">{raster(accessoires)}</div>
</div></section>''')
    # 4 kleur en letter
    kleuren = [('Navy', NAVY, '#F3ECDD'), ('Crème', CREME, NAVY), ('Baby', BABY, NAVY), ('Rose', ROSE, NAVY), ('Zand', ZAND, NAVY)]
    strook = ''.join(f'<div style="background:{h};color:{t}"><span class="naam">{n}</span><span class="hex">{h}</span></div>' for n, h, t in kleuren)
    paginas.append(f'''<section class="pagina" aria-label="Kleur en letter"><div class="kleur">{strook}</div>
  <div class="letters">
    <div class="rij"><span class="label">Display<br>koppen en logo</span><span class="proef-d">HANDEN VRIJ</span></div>
    <div class="rij"><span class="label">Courier Prime<br>tekst en labels</span><span class="proef-m">Schuif je board in de tas en hang hem over je schouder. Zo heb je allebei je handen vrij.</span></div>
    <div class="rij"><span class="label">Homemade Apple<br>één woord, met de hand</span><span class="proef-h">op weg naar zee</span></div>
  </div></section>''')
    # 5 stickers op zee
    paginas.append(f'''<section class="pagina stickers" aria-label="Stickers">
  <img class="bg" src="{foto('zee-zw')}" alt="">
  {TAS.sticker('s', 'left:6cqw;top:12cqw;width:46cqw;transform:rotate(-8deg)')}{S('zon', 58, 8, 26, 0)}{S('schelp', 10, 46, 28, 4)}{S('zeester', 56, 40, 27, 12)}
  {S('golf', 30, 72, 44, -3)}{S('palm', 75, 64, 18, 6)}
  <p class="voet label">Stickers en illustraties</p></section>''')
    # 6 logostickers op zand
    paginas.append(f'''<section class="pagina badges" aria-label="Logostickers">
  <img class="bg" src="{foto('zand')}" alt="">
  {ovaal().replace('class="badge"', 'class="badge" style="left:5cqw;top:5cqw;width:50cqw;transform:rotate(-7deg)"')}
  {zegel().replace('class="badge"', 'class="badge" style="left:60cqw;top:4cqw;width:33cqw;transform:rotate(8deg)"')}
  {golfrand().replace('class="badge"', 'class="badge" style="left:6cqw;top:42cqw;width:29cqw;transform:rotate(-6deg)"')}
  {tegelsticker().replace('class="badge"', 'class="badge" style="left:39cqw;top:38cqw;width:20cqw;transform:rotate(6deg)"')}
  {labelsticker().replace('class="badge"', 'class="badge" style="left:63cqw;top:42cqw;width:31cqw;transform:rotate(-5deg)"')}
  {pil().replace('class="badge"', 'class="badge" style="left:4cqw;top:72cqw;width:40cqw;transform:rotate(-9deg)"')}
  {icsticker('icoonB', 'left:76cqw;top:76cqw;width:16cqw;transform:rotate(-10deg)', rond=True)}
</section>''')
    # 6b stickervel
    paginas.append(f'''<section class="pagina vel" aria-label="Stickervel">
  <div class="vel__blad">
    <p class="vel__kop">STICKERVEL</p>
    {zonsondergang_sticker().replace('class="badge"', 'class="badge" style="left:6cqw;top:12cqw;width:30cqw;transform:rotate(-5deg)"')}
    {boog_sticker().replace('class="badge"', 'class="badge" style="left:40cqw;top:9cqw;width:26cqw;transform:rotate(4deg)"')}
    {tegelcirkel_sticker().replace('class="badge"', 'class="badge" style="left:66cqw;top:12cqw;width:21cqw;transform:rotate(-8deg)"')}
    {vaantje_sticker().replace('class="badge"', 'class="badge" style="left:5cqw;top:50cqw;width:46cqw;transform:rotate(-7deg)"')}
    {postzegel_sticker().replace('class="badge"', 'class="badge" style="left:58cqw;top:46cqw;width:24cqw;transform:rotate(6deg)"')}
    {ruit_sticker().replace('class="badge"', 'class="badge" style="left:10cqw;top:84cqw;width:52cqw;transform:rotate(3deg)"')}
    {icsticker('icoonC', 'left:72cqw;top:88cqw;width:16cqw;transform:rotate(-12deg)')}
  </div>
</section>''')
    # 7 illustraties
    paginas.append(f'''<section class="pagina" aria-label="Illustraties"><div class="ill">
  <h2>GETEKEND MET DE HAND</h2>
  <p class="m" style="grid-column:1/-1;font-size:1.8cqw;line-height:1.5;max-width:60ch">Eén lijndikte, ronde uiteinden, en net niet perfect. Voor kaartjes, de verpakking, de website en de binnenkant van de tas.</p>
  <figure>{tekening('parasol', NAVY)}<figcaption>aan het strand</figcaption></figure>
  <figure>{TAS.lijn()}<figcaption>de draagtas</figcaption></figure>
  <figure>{tekening('busje', NAVY)}<figcaption>op roadtrip</figcaption></figure>
  <figure>{tekening('golf', NAVY)}<figcaption>de golf</figcaption></figure>
</div></section>''')
    # 7b patroon
    paginas.append(f'<section class="pagina" aria-label="Patroon">{patroon()}<div style="position:absolute;left:0;right:0;bottom:5cqw;display:grid;justify-items:center">{logo("liggend", CREME, "", "width:34cqw")}</div></section>')
    # 8 grid
    paginas.append(f'''<section class="pagina" aria-label="Collectie"><div class="grid9">
  <img src="{foto('g1')}" alt="Surfer loopt met een geel board over het strand">
  <div class="tegel"><span class="hand">De Draagtas</span><span class="m">Zware stof<br>Brede schouderband<br>Softtop en hardboard</span></div>
  <img src="{foto('g3')}" alt="Surfster met board onder een roze lucht">
  <div class="tegel logo">{logo('gestapeld', NAVY)}<span class="m">Est 2025</span></div>
  <img src="{foto('g6')}" alt="Twee surfers lopen de zee in">
  <div class="tegel logo">{logo('gestapeld', NAVY)}<span class="m">Handen vrij</span></div>
  <img src="{foto('g2')}" alt="Surfboard tegen een busje in de duinen">
  <div class="tegel"><span class="hand">Het Verhaal</span><span class="m">Bedacht in Australië<br>Gemaakt voor onderweg<br>Van surfers voor surfers</span></div>
  <img src="{foto('g4')}" alt="Wit surfboard rechtop in het zand">
</div></section>''')
    # 9 drukwerk
    paginas.append(f'''<section class="pagina" aria-label="Drukwerk">
  <img class="bg" src="{foto('kaart')}" alt="">
  <div class="kaart-navy">{logo('liggend', CREME, 'groot')}
    <div class="links">Draagtassen voor surfboards<br>Handen vrij, <i>op weg naar zee</i></div>
    <div class="rechts"><span>Plaats</span><span class="hand">Nederland</span><span>Sinds</span><span class="hand">2025</span><span>Voor</span><span class="hand">surfers overal</span></div>
  </div>
  <div class="kaart-creme">{tekening('parasol', NAVY)}</div>
</section>''')
    # 9b prints van de kleding
    O = HIER.parent / 'producten' / 'uit_echt'
    prints = [('lijn', 'licht', 'var(--creme)', 'LIJN NAAR ZEE'), ('herhaling', 'licht', 'var(--creme)', 'OP WEG NAAR ZEE'), ('boog', 'licht', 'var(--baby)', 'KLASSIEK'),
              ('grootboard', 'licht', 'var(--zand)', 'BOARD'), ('zon', 'donker', 'var(--navy)', 'ZON'), ('golf', 'licht', 'var(--rose)', 'GOLF'),
              ('vin', 'donker', 'var(--navy)', 'VIN'), ('tweeboards', 'donker', 'var(--navy)', 'TWEE BOARDS'), ('tweeboardslos', 'licht', 'var(--creme)', 'BOARDS')]
    def printvak(naam, soort, kleur, titel):
        pad = O / f'ontwerp-{naam}-{soort}.png'
        if not pad.exists():
            return ''
        return (f'<figure><div style="background:{kleur} url({b64(pad, "image/png")}) center/78% no-repeat"></div>'
                f'<figcaption>{titel}</figcaption></figure>')
    paginas.append(f'''<section class="pagina" aria-label="Prints"><div class="fotop">
  <h2>PRINTS</h2>
  <p>De tekeningen op de rug van de shirts en truien. Eén of twee kleuren, gedrukt met inkt op waterbasis.</p>
  <div class="negen">{"".join(printvak(*x) for x in prints)}</div>
</div></section>''')
    # 9c homepage, video en zo werkt hij
    A = HIER.parent.parent / 'theme' / 'assets'
    paginas.append(f'''<section class="pagina" aria-label="Homepage"><div class="fotop">
  <h2>HOMEPAGE</h2>
  <p>De hero: drie boards met de draagtas op het zand, in dezelfde studiostijl als de productfoto's. Daaronder de drie stappen van Zo werkt hij.</p>
  <div style="display:grid;grid-template-rows:1.15fr 1fr;gap:1.4cqw;min-height:0">
    <div style="background:url({productfoto(A / 'tt-foto-hero-home.jpg', 1400)}) center/cover"></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.4cqw;min-height:0">
      <div style="background:url({productfoto(A / 'tt-foto-stap-1.jpg', 500)}) center/cover"></div>
      <div style="background:url({productfoto(A / 'tt-foto-stap-2.jpg', 500)}) center/cover"></div>
      <div style="background:url({productfoto(A / 'tt-foto-stap-3.jpg', 500)}) center/cover"></div>
    </div>
  </div>
</div></section>''')
    V = HIER.parent.parent / 'docs' / 'video'
    import subprocess, tempfile
    beelden = []
    if (V / 'tide-tode-hero-720.mp4').exists():
        tmp = pathlib.Path(tempfile.mkdtemp())
        for i, t in enumerate((0.6, 2.6, 4.6, 6.6)):
            uit = tmp / f'v{i}.jpg'
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i', str(V / 'tide-tode-hero-720.mp4'), '-frames:v', '1', str(uit)], check=False)
            if uit.exists():
                beelden.append(productfoto(uit, 700))
    if beelden:
        vakken = ''.join(f'<div style="background:url({b}) center/cover"></div>' for b in beelden)
        paginas.append(f'''<section class="pagina" aria-label="Video" style="background:var(--navy);color:var(--creme)"><div class="fotop">
  <h2>VIDEO</h2>
  <p>Een korte film voor de hero, gemaakt uit onze eigen tasbeelden: close-ups van label en stof, het geheel van boven, warme filmkleur en korrel.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.4cqw;min-height:0">{vakken}</div>
</div></section>''')
    S = HIER.parent.parent / 'docs' / 'social'
    if (S / 'raster-voorbeeld.jpg').exists():
        paginas.append(f'''<section class="pagina" aria-label="Instagram" style="background:var(--rose)"><div class="fotop">
  <h2>INSTAGRAM</h2>
  <p>Twaalf carrousels in 4:5. Weinig tekst, de foto's doen het werk. Zo ziet het profiel eruit.</p>
  <div style="background:url({productfoto(S / 'raster-voorbeeld.jpg', 900)}) center/contain no-repeat;min-height:0"></div>
</div></section>''')
    # 10 website
    paginas.append(f'''<section class="pagina" aria-label="Website" style="background:var(--baby)">
  <div class="browser"><div class="balk"><i></i><i></i><i></i></div>
    <div class="scherm"><img src="{productfoto(HIER.parent.parent / 'theme' / 'assets' / 'tt-foto-hero-home.jpg', 1200)}" alt="" style="object-position:70% 50%">
      <nav>{logo('liggend', CREME)}<span class="links"><span>SHOP</span><span>ONS VERHAAL</span><span>FAQ</span></span></nav>
      {logo('gestapeld', NAVY, 'hero-logo')}
      <span class="hero-hand">Handen vrij, op weg naar zee</span>
      <div class="hero-tekst"><span class="knop">NAAR DE SHOP</span></div>
    </div></div>
  <p class="label" style="position:absolute;left:6cqw;bottom:4cqw;margin:0">De voorkant van de website</p>
</section>''')

    html = f'''<meta charset="utf-8"><title>Tide-Tode Brandbook</title>
<style>{fonts}{css}</style>
<main class="boek">
  <header class="kop"><strong>TIDE TODE</strong><span>Brandbook 2025</span></header>
  {"".join(paginas)}
  <p class="onderschrift m">Lettertypes: een eigen display-letter op basis van Kavoon (SIL Open Font License), Courier Prime (OFL) en Homemade Apple (Apache 2.0). Foto's zijn tijdelijke sfeerbeelden van Unsplash, tot Veerles eigen beelden er zijn.</p>
</main>'''
    UIT.write_text(html)
    print('brandbook', UIT, round(len(html) / 1e6, 2), 'MB')


if __name__ == '__main__':
    bouw()
