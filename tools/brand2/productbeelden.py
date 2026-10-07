"""Productbeelden in de merkstijl (getekend, geen foto's), 1600x2000.
Plaatsvervangers tot de echte productfoto's er zijn. Schrijft per beeld een html-pagina naar
tools/brand2/uit/productbeelden/; tools/brand2/productbeelden.mjs maakt er jpg's van."""
import json, pathlib, random
import tas as TAS
from tas import BOARD, PANEEL, BAND, NAVY, CREME, PAPIER, TERRA, BLAUW, MOSTERD, ROEST

HIER = pathlib.Path(__file__).parent
ASSETS = HIER.parent.parent / 'theme' / 'assets'
UIT = HIER / 'uit' / 'productbeelden'
UIT.mkdir(parents=True, exist_ok=True)
L = json.load(open(HIER / 'logo2.json'))
G, BD = L['gestapeld'], L['board']
BABY, ROSE, ZAND = '#BFD3EA', '#EDBDB8', '#E3CFAE'


def logo(kleur=NAVY, breedte=220):
    return f'<svg viewBox="0 0 {G["w"]} {G["h"]}" style="width:{breedte}px;fill:{kleur};display:block"><path d="{G["d"]}"/></svg>'


def icoon(kleur=NAVY, hoogte=60):
    return f'<svg viewBox="0 0 {BD["w"]} {BD["h"]}" style="height:{hoogte}px;fill:{kleur};display:block"><path d="{BD["d"]}"/></svg>'


def vlak(stiksels=True):
    """De tas als vlakke tekening in kleur, zonder stickerrand."""
    st = ''
    if stiksels:
        st = (f'<path d="{PANEEL}" transform="translate(300 189) scale(.95) translate(-300 -189)" fill="none" stroke="{CREME}" stroke-width="1.4" stroke-dasharray="5 5" opacity=".7"/>')
    return f'''<defs><clipPath id="vk"><path d="{PANEEL}"/></clipPath>
  <linearGradient id="glans" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".08"/></linearGradient></defs>
  <path d="{BOARD}" fill="{CREME}" stroke="{NAVY}" stroke-width="3"/>
  <path d="M60 170 L548 170" stroke="{NAVY}" stroke-width="1.6" opacity=".35"/>
  <path d="{BOARD}" fill="url(#glans)"/>
  <g clip-path="url(#vk)">{TAS.tegels()}</g>
  <path d="{PANEEL}" fill="none" stroke="{NAVY}" stroke-width="3"/>
  <path d="{BAND}" fill="none" stroke="{BLAUW}" stroke-width="15" stroke-linejoin="round"/>
  <path d="{BAND}" fill="none" stroke="{NAVY}" stroke-width="1.4" stroke-dasharray="4 5" opacity=".55"/>
  {st}'''


KORREL = '''<svg class="korrel" width="100%" height="100%"><filter id="k"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .5 0"/></filter><rect width="100%" height="100%" filter="url(#k)"/></svg>'''


def pagina(naam, achtergrond, inhoud, extra_css=''):
    fonts = ''.join(f"@font-face{{font-family:'{f}';src:url('file://{ASSETS / b}') format('woff2');font-weight:{w}}}"
                    for f, b, w in [('Courier Prime', 'courierprime-regular.woff2', 400), ('Courier Prime', 'courierprime-bold.woff2', 700),
                                    ('Homemade Apple', 'homemadeapple-regular.woff2', 400), ('Tide Tode Display', 'tide-tode-display.woff2', 400)])
    html = f'''<!doctype html><meta charset="utf-8"><style>{fonts}
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ width: 1600px; height: 2000px; overflow: hidden; }}
body {{ position: relative; background: {achtergrond}; color: {NAVY}; font-family: 'Courier Prime', monospace; }}
.korrel {{ position: absolute; inset: 0; opacity: .16; mix-blend-mode: multiply; pointer-events: none; z-index: 50; }}
.label {{ font: 700 30px 'Courier Prime'; letter-spacing: .24em; text-transform: uppercase; }}
.hand {{ font: 400 64px/1.3 'Homemade Apple'; }}
.pil {{ display: inline-block; padding: 22px 40px; border-radius: 999px; background: {NAVY}; color: {CREME}; }}
.hoek {{ position: absolute; }}
{extra_css}
</style><body>{inhoud}{KORREL}</body>'''
    (UIT / f'{naam}.html').write_text(html)


# 1. Packshot: de tas staand, zacht licht, schaduw op de grond
pagina('tt-product-1', f'radial-gradient(120% 80% at 50% 38%, #FBF7EF 0%, #EFE5D3 60%, #E6D9C1 100%)', f'''
<div class="hoek label" style="left:90px;top:90px">Tide Tode</div>
<div class="hoek label" style="right:90px;top:90px">De draagtas</div>
<div style="position:absolute;left:50%;top:1720px;width:640px;height:90px;translate:-50% 0;border-radius:50%;background:radial-gradient(closest-side, rgba(34,50,79,.32), rgba(34,50,79,0));filter:blur(6px)"></div>
<svg viewBox="0 0 600 300" style="position:absolute;left:50%;top:50%;width:1640px;translate:-50% -52%;rotate:-90deg;filter:drop-shadow(-18px 10px 30px rgba(34,50,79,.22))">{vlak()}</svg>
<div class="hoek" style="left:90px;bottom:90px">{icoon(NAVY, 74)}</div>
<div class="hoek label" style="right:90px;bottom:96px">Tegelprint</div>''')

# 2. Tegelstof van dichtbij
random.seed(4)
tegel, kleuren = 270, [TERRA, BLAUW, CREME, ROEST, BLAUW, TERRA, CREME]
cellen = ''
for r in range(11):
    for c in range(9):
        x, y = c * tegel - 300, r * tegel - 300
        kl = kleuren[(r * 3 + c) % len(kleuren)]
        binnen = CREME if kl != CREME else TERRA
        h = tegel / 2
        cellen += (f'<rect x="{x}" y="{y}" width="{tegel}" height="{tegel}" fill="{kl}"/>'
                   f'<path d="M{x + h} {y + 26} L{x + tegel - 26} {y + h} L{x + h} {y + tegel - 26} L{x + 26} {y + h} Z" fill="{binnen}"/>'
                   f'<circle cx="{x + h}" cy="{y + h}" r="24" fill="{NAVY}"/>')
weef = ''.join(f'<line x1="-400" y1="{y}" x2="2400" y2="{y}" stroke="#000" stroke-opacity=".05" stroke-width="3"/>' for y in range(-400, 2600, 9))
weef += ''.join(f'<line x1="{x}" y1="-400" x2="{x}" y2="2600" stroke="#fff" stroke-opacity=".05" stroke-width="3"/>' for x in range(-400, 2400, 9))
pagina('tt-product-2', CREME, f'''
<svg viewBox="0 0 1600 2000" style="position:absolute;inset:0;width:100%;height:100%"><g transform="rotate(-7 800 1000)">{cellen}</g>
<rect width="1600" height="2000" fill="url(#vig)"/><defs><radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/></radialGradient></defs></svg>
<div class="hoek label pil" style="left:90px;bottom:90px">Tegelstof</div>''', '.korrel { opacity: .07; }')

# 3. Het tegelvak om je board (uitsnede uit de tekening)
pagina('tt-product-3', BABY, f'''
<svg viewBox="170 110 260 150" style="position:absolute;left:50%;top:50%;width:2300px;translate:-50% -50%;rotate:-8deg;filter:drop-shadow(0 30px 40px rgba(34,50,79,.25))">{vlak()}</svg>
<div class="hoek label pil" style="left:90px;bottom:90px">Het vak</div>
<div class="hoek label" style="right:90px;top:90px">Om het midden van je board</div>''')

# 4. Schouderband van dichtbij
pagina('tt-product-4', ROSE, f'''
<svg viewBox="200 0 200 150" style="position:absolute;left:50%;top:50%;width:2000px;translate:-50% -46%;rotate:4deg;filter:drop-shadow(0 30px 40px rgba(34,50,79,.25))">{vlak()}</svg>
<div class="hoek label pil" style="left:90px;bottom:90px">Schouderband</div>
<div class="hoek label" style="right:90px;top:90px">Over je schouder</div>''')

# 5. Uitleg met nummers
punten = [('Schouderband', 50, 8), ('Tegelstof', 50, 70), ('Je board', 88, 50)]
stippen = ''.join(f'<span class="stip" style="left:{x}%;top:{y}%">{i}</span>' for i, (_, x, y) in enumerate(punten, 1))
legenda = ''.join(f'<li><span class="stip stip--los">{i}</span>{t}</li>' for i, (t, _, _) in enumerate(punten, 1))
pagina('tt-product-5', PAPIER, f'''
<div class="hoek" style="left:90px;top:100px"><p class="hand" style="color:#4a6b97">De details</p><p style="font:400 120px/1 'Tide Tode Display';letter-spacing:.03em;text-transform:uppercase;margin-top:10px">Zo zit hij<br>in elkaar</p></div>
<div class="vlakje" style="position:absolute;left:90px;right:90px;top:640px;background:{CREME};padding:110px 70px"><div style="position:relative">{TAS.lijn('lijn')}{stippen}</div></div>
<ul class="legenda">{legenda}</ul>''', '''
.lijn { width: 100%; height: auto; display: block; }
.stip { position: absolute; width: 74px; height: 74px; margin: -37px 0 0 -37px; border-radius: 50%; display: grid; place-items: center; background: #22324F; color: #F3ECDD; font: 700 34px 'Courier Prime'; box-shadow: 0 0 0 9px #F3ECDD; }
.stip--los { position: static; margin: 0 26px 0 0; box-shadow: none; width: 62px; height: 62px; font-size: 28px; background: none; color: #22324F; border: 3px solid #22324F; }
.legenda { position: absolute; left: 90px; right: 90px; bottom: 110px; list-style: none; padding: 0; display: grid; grid-template-columns: 1fr; gap: 30px; font: 700 34px 'Courier Prime'; letter-spacing: .16em; text-transform: uppercase; }
.legenda li { display: flex; align-items: center; }''')

# 6. Sfeer: de tas als sticker op zee
pagina('tt-product-6', '#2a2f36', f'''
<img src="file://{ASSETS / 'tt-foto-zee-zw.jpg'}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:grayscale(1) brightness(.72) contrast(1.05)">
<div style="position:absolute;left:50%;top:44%;width:1280px;translate:-50% -50%;rotate:-9deg">{TAS.sticker('stk', 'width:100%;height:auto;display:block;filter:drop-shadow(0 24px 30px rgba(0,0,0,.35))')}</div>
<div class="hoek" style="left:0;right:0;bottom:150px;text-align:center;color:{CREME}"><p class="hand" style="font-size:78px">Handen vrij, op weg naar zee</p><p class="label" style="margin-top:22px;opacity:.85">Van surfers, voor surfers</p></div>
<div class="hoek" style="left:90px;top:90px">{logo(CREME, 260)}</div>''')

# 7. De kleuren van de tas
stalen = [('Terracotta', TERRA), ('Dusty blue', BLAUW), ('Mosterd', MOSTERD), ('Roest', ROEST), ('Crème', CREME), ('Navy', NAVY)]
staal_html = ''.join(f'''<div class="staal"><div class="tegel" style="background:{k}"><i style="background:{CREME if k not in (CREME,) else TERRA}"></i><b style="background:{CREME if k == NAVY else NAVY}"></b></div><p class="label">{n}</p><p class="hex">{k}</p></div>''' for n, k in stalen)
pagina('tt-product-7', CREME, f'''
<div class="hoek" style="left:90px;top:100px"><p class="hand" style="color:#4a6b97">Uit de tas</p><p style="font:400 120px/1 'Tide Tode Display';letter-spacing:.03em;text-transform:uppercase;margin-top:10px">De kleuren</p></div>
<div class="stalen">{staal_html}</div>
<div class="hoek" style="right:90px;bottom:90px">{icoon(NAVY, 74)}</div>''', f'''
.stalen {{ position: absolute; left: 90px; right: 90px; top: 520px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 70px 50px; }}
.tegel {{ position: relative; aspect-ratio: 1; border-radius: 26px; box-shadow: 0 24px 40px -24px rgba(34,50,79,.45); overflow: hidden; }}
.tegel i {{ position: absolute; inset: 18%; rotate: 45deg; scale: .78; border-radius: 8px; }}
.tegel b {{ position: absolute; left: 50%; top: 50%; width: 15%; aspect-ratio: 1; translate: -50% -50%; border-radius: 50%; background: {NAVY}; }}
.staal:last-child .tegel b {{ background: {CREME}; }}
.staal .label {{ margin-top: 30px; }}
.hex {{ margin-top: 8px; font: 400 26px 'Courier Prime'; opacity: .7; text-transform: uppercase; }}''')

print(sorted(p.name for p in UIT.glob('*.html')))
