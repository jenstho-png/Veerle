"""Bouwt het Tide-Tode brandbook (branding 2) als één HTML-bestand.
Posterpagina's in 4:5, alles schaalt mee met de breedte (container query units).
Fonts en foto's gaan als data-URI mee, zodat de pagina los te delen is."""
import base64, json, math, pathlib
import stickers as ST

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


def logo(soort, kleur, cls='', stijl=''):
    l = LOGO[soort]
    return f'<svg class="{cls}" style="{stijl}" viewBox="0 0 {l["w"]} {l["h"]}" role="img" aria-label="Tide Tode"><path fill="{kleur}" d="{l["d"]}"/></svg>'


def icoon(kleur, cls='', stijl=''):
    b = LOGO['board']
    return f'<svg class="{cls}" style="{stijl}" viewBox="0 0 {b["w"]} {b["h"]}" aria-hidden="true"><path fill="{kleur}" d="{b["d"]}"/></svg>'


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
def zegel(achter=ROSE, voor=NAVY, rand=PAPIER):
    return f'''<svg viewBox="0 0 340 340" class="badge" aria-hidden="true">
  <circle cx="170" cy="170" r="168" fill="{rand}"/><circle cx="170" cy="170" r="156" fill="{achter}"/>
  <defs><path id="zb" d="M60 170a110 110 0 0 1 220 0"/><path id="zo" d="M44 170a126 126 0 0 0 252 0"/></defs>
  <text font-family="Courier Prime, monospace" font-weight="700" font-size="30" letter-spacing="9" fill="{voor}"><textPath href="#zb" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>
  <text font-family="Courier Prime, monospace" font-weight="700" font-size="19" letter-spacing="5" fill="{voor}"><textPath href="#zo" startOffset="50%" text-anchor="middle">VAN SURFERS VOOR SURFERS</textPath></text>
  <circle cx="44" cy="170" r="6" fill="{voor}"/><circle cx="296" cy="170" r="6" fill="{voor}"/>
  {board_in(170, 178, 150, voor)}
</svg>'''


def ovaal():
    return f'''<svg viewBox="0 0 520 330" class="badge" aria-hidden="true">
  <ellipse cx="260" cy="165" rx="258" ry="163" fill="{PAPIER}"/>
  <ellipse cx="260" cy="165" rx="240" ry="146" fill="{CREME}" stroke="{BABY}" stroke-width="12"/>
  <text x="260" y="88" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="24" letter-spacing="8" fill="{NAVY}">SURFBOARD DRAAGTAS</text>
  {logo_in('liggend', 95, 118, 330, NAVY)}
  <text x="262" y="250" text-anchor="middle" font-family="Homemade Apple, cursive" font-size="30" fill="{NAVY}">handen vrij</text>
  <path d="M190 262 Q262 254 336 262" stroke="{NAVY}" stroke-width="3" fill="none" stroke-linecap="round"/>
</svg>'''


def pil():
    return f'''<svg viewBox="0 0 520 170" class="badge" aria-hidden="true">
  <rect x="2" y="2" width="516" height="166" rx="83" fill="{PAPIER}"/>
  <rect x="14" y="14" width="492" height="142" rx="71" fill="{NAVY}"/>
  {logo_in('liggend', 80, 64, 360, CREME)}
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
        r = 162 + 7 * math.cos(a * 16)
        pts2.append(f'{170 + r * math.cos(a):.1f},{170 + r * math.sin(a):.1f}')
    t = ILL['golf']
    paden = ''.join(f'<path d="{p}"/>' for p in t['d'])
    return f'''<svg viewBox="0 0 340 340" class="badge" aria-hidden="true">
  <polygon points="{' '.join(pts2)}" fill="{PAPIER}"/><polygon points="{' '.join(pts)}" fill="{NAVY}"/>
  <g transform="translate(70 66) scale(.5)" fill="none" stroke="{CREME}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">{paden}</g>
  <text x="170" y="250" text-anchor="middle" font-family="Courier Prime, monospace" font-weight="700" font-size="22" letter-spacing="7" fill="{CREME}">EST 2025</text>
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
.familie .duo svg:first-child { width: 20%; } .familie .duo svg:last-child { width: 80%; }
.metic { display: grid; justify-items: center; gap: 3cqw; width: 62%; }
.metic svg:first-child { width: 30%; } .metic svg:last-child { width: 100%; }
.cover .icoon { position: absolute; left: 6cqw; bottom: 57cqw; width: 11cqw; }

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
.badges .badge { position: absolute; filter: drop-shadow(0 .8cqw 1.4cqw rgba(0, 0, 0, .28)); }

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
.kaart-navy .groot { position: absolute; left: 3cqw; right: 3cqw; top: -2.6cqw; }
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
    # 4 kleur en letter
    kleuren = [('Navy', NAVY, '#F3ECDD'), ('Crème', CREME, NAVY), ('Baby', BABY, NAVY), ('Rose', ROSE, NAVY), ('Zand', ZAND, NAVY)]
    strook = ''.join(f'<div style="background:{h};color:{t}"><span class="naam">{n}</span><span class="hex">{h}</span></div>' for n, h, t in kleuren)
    paginas.append(f'''<section class="pagina" aria-label="Kleur en letter"><div class="kleur">{strook}</div>
  <div class="letters">
    <div class="rij"><span class="label">Display<br>koppen en logo</span><span class="proef-d">HANDEN VRIJ</span></div>
    <div class="rij"><span class="label">Courier Prime<br>tekst en labels</span><span class="proef-m">Leg je board in de tas, trek de banden aan en hang hem op je rug. Zo heb je allebei je handen vrij.</span></div>
    <div class="rij"><span class="label">Homemade Apple<br>één woord, met de hand</span><span class="proef-h">op weg naar zee</span></div>
  </div></section>''')
    # 5 stickers op zee
    paginas.append(f'''<section class="pagina stickers" aria-label="Stickers">
  <img class="bg" src="{foto('zee-zw')}" alt="">
  {S('board', 14, 10, 30, -6)}{S('zon', 58, 8, 26, 0)}{S('schelp', 10, 46, 28, 4)}{S('zeester', 56, 40, 27, 12)}
  {S('golf', 30, 72, 44, -3)}{S('palm', 75, 64, 18, 6)}
  <p class="voet label">Stickers en illustraties</p></section>''')
    # 6 logostickers op zand
    paginas.append(f'''<section class="pagina badges" aria-label="Logostickers">
  <img class="bg" src="{foto('zand')}" alt="">
  {ovaal().replace('class="badge"', 'class="badge" style="left:8cqw;top:10cqw;width:52cqw;transform:rotate(-8deg)"')}
  {zegel().replace('class="badge"', 'class="badge" style="left:58cqw;top:22cqw;width:34cqw;transform:rotate(9deg)"')}
  {golfrand().replace('class="badge"', 'class="badge" style="left:14cqw;top:58cqw;width:30cqw;transform:rotate(-4deg)"')}
  {pil().replace('class="badge"', 'class="badge" style="left:46cqw;top:78cqw;width:46cqw;transform:rotate(-12deg)"')}
  {sticker('board', 's', 'position:absolute;left:52cqw;top:52cqw;width:20cqw;transform:rotate(14deg);filter:drop-shadow(0 .8cqw 1.4cqw rgba(0,0,0,.28))')}
</section>''')
    # 7 illustraties
    paginas.append(f'''<section class="pagina" aria-label="Illustraties"><div class="ill">
  <h2>GETEKEND MET DE HAND</h2>
  <p class="m" style="grid-column:1/-1;font-size:1.8cqw;line-height:1.5;max-width:60ch">Eén lijndikte, ronde uiteinden, en net niet perfect. Voor kaartjes, de verpakking, de website en de binnenkant van de tas.</p>
  <figure>{tekening('parasol', NAVY)}<figcaption>aan het strand</figcaption></figure>
  <figure>{tekening('tas', NAVY)}<figcaption>de draagtas</figcaption></figure>
  <figure>{tekening('busje', NAVY)}<figcaption>op roadtrip</figcaption></figure>
  <figure>{tekening('golf', NAVY)}<figcaption>de golf</figcaption></figure>
</div></section>''')
    # 7b patroon
    paginas.append(f'<section class="pagina" aria-label="Patroon">{patroon()}<div style="position:absolute;left:0;right:0;bottom:5cqw;display:grid;justify-items:center">{logo("liggend", CREME, "", "width:34cqw")}</div></section>')
    # 8 grid
    paginas.append(f'''<section class="pagina" aria-label="Collectie"><div class="grid9">
  <img src="{foto('g1')}" alt="Surfer loopt met een geel board over het strand">
  <div class="tegel"><span class="hand">De Draagtas</span><span class="m">Zware stof<br>Twee banden<br>Softtop en hardboard</span></div>
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
    # 10 website
    paginas.append(f'''<section class="pagina" aria-label="Website" style="background:var(--baby)">
  <div class="browser"><div class="balk"><i></i><i></i><i></i></div>
    <div class="scherm"><img src="{foto('web')}" alt="">
      <nav>{logo('liggend', CREME)}<span class="links"><span>SHOP</span><span>ONS VERHAAL</span><span>FAQ</span></span></nav>
      {logo('gestapeld', CREME, 'hero-logo')}
      <span class="hero-hand">Handen vrij, op weg naar zee</span>
      <div class="hero-tekst">Een draagtas voor je surfboard. Je board op je rug, je handen vrij voor de wandeling, de fiets en de scooter.<br><span class="knop">BEKIJK DE DRAAGTAS</span></div>
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
