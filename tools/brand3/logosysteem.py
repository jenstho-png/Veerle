"""Logosysteem richting 3: zachte cursieve woordmerk + board-en-golf-icoon.
Schrijft losse SVG-bestanden (uit/) en de presentatiepagina docs/brandbook/logo-systeem.html."""
import base64, json, pathlib

HIER = pathlib.Path(__file__).parent
L = json.load(open(HIER / 'logo3.json'))
ICOON = json.load(open(HIER / 'sporen.json'))['icoon']['d']
FOTO = HIER.parent / 'brand2' / 'foto'
UITDIR = HIER / 'uit'; UITDIR.mkdir(exist_ok=True)
PAGINA = HIER.parent.parent / 'docs' / 'brandbook' / 'logo-systeem.html'
NAVY, CREME = '#22324F', '#F3ECDD'

ICOON_VB = '4 5 318 296'


def woord(soort, cls='', kleur='currentColor'):
    w = L[soort]
    return f'<svg class="{cls}" viewBox="{w["vb"]}" role="img" aria-label="Tide Tode"><path fill="{kleur}" d="{w["d"]}"/></svg>'


def icoon(cls='', kleur='currentColor'):
    return f'<svg class="{cls}" viewBox="{ICOON_VB}" aria-hidden="true"><path fill="{kleur}" d="{ICOON}"/></svg>'


def bestand(naam, inhoud_vb, inhoud):
    (UITDIR / naam).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{inhoud_vb}">{inhoud}</svg>')


# ---- losse logobestanden (navy), voor drukwerk en de website ----
def comp_hoofd(kleur=NAVY):
    g = L['gestapeld']; s = 1000 / g['w']; gh = g['h'] * s
    ix, iy, iw, ih = 4, 5, 318, 296; isch = 300 / iw
    vb = g['vb'].split(); gx, gy = float(vb[0]), float(vb[1])
    icon = f'<g transform="translate({500 - 150:.1f} 0) scale({isch:.4f}) translate({-ix} {-iy})"><path fill="{kleur}" d="{ICOON}"/></g>'
    tekst = f'<g transform="translate(0 {ih * isch + 60:.1f}) scale({s:.5f}) translate({-gx:.1f} {-gy:.1f})"><path fill="{kleur}" d="{g["d"]}"/></g>'
    return f'0 0 1000 {ih * isch + 60 + gh:.0f}', icon + tekst


def comp_liggend(kleur=NAVY):
    g = L['liggend']; s = 1600 / g['w']; gh = g['h'] * s
    ix, iy, iw, ih = 4, 5, 318, 296; hoogte = gh * 1.25; isch = hoogte / ih
    vb = g['vb'].split(); gx, gy = float(vb[0]), float(vb[1])
    icon = f'<g transform="scale({isch:.4f}) translate({-ix} {-iy})"><path fill="{kleur}" d="{ICOON}"/></g>'
    x = iw * isch + 70
    tekst = f'<g transform="translate({x:.1f} {(hoogte - gh) / 2:.1f}) scale({s:.5f}) translate({-gx:.1f} {-gy:.1f})"><path fill="{kleur}" d="{g["d"]}"/></g>'
    return f'0 0 {x + 1600:.0f} {hoogte:.0f}', icon + tekst


for kleur, naam in ((NAVY, 'navy'), (CREME, 'creme')):
    bestand(f'tide-tode-logo-{naam}.svg', *comp_hoofd(kleur))
    bestand(f'tide-tode-logo-liggend-{naam}.svg', *comp_liggend(kleur))
    bestand(f'tide-tode-woordmerk-{naam}.svg', L['gestapeld']['vb'], f'<path fill="{kleur}" d="{L["gestapeld"]["d"]}"/>')
    bestand(f'tide-tode-icoon-{naam}.svg', ICOON_VB, f'<path fill="{kleur}" d="{ICOON}"/>')


def stempel(cls=''):
    return f'''<svg class="{cls}" viewBox="0 0 300 300" role="img" aria-label="Stempel Tide Tode">
  <defs><path id="sb" d="M44 150a106 106 0 0 1 212 0"/><path id="so" d="M33 150a117 117 0 0 0 234 0"/></defs>
  <circle cx="150" cy="150" r="146" fill="none" stroke="currentColor" stroke-width="3"/>
  <circle cx="150" cy="150" r="134" fill="none" stroke="currentColor" stroke-width="1.1"/>
  <text font-family="'Courier Prime', monospace" font-weight="700" font-size="17" letter-spacing="7" fill="currentColor"><textPath href="#sb" startOffset="50%" text-anchor="middle">TIDE~TODE</textPath></text>
  <text font-family="'Courier Prime', monospace" font-weight="700" font-size="13" letter-spacing="4.4" fill="currentColor"><textPath href="#so" startOffset="50%" text-anchor="middle">VAN SURFERS VOOR SURFERS</textPath></text>
  <circle cx="33" cy="150" r="3.6" fill="currentColor"/><circle cx="267" cy="150" r="3.6" fill="currentColor"/>
  <g transform="translate(92 96) scale(.365) translate(-4 -5)"><path fill="currentColor" d="{ICOON}"/></g>
</svg>'''


def foto(n):
    return 'data:image/jpeg;base64,' + base64.b64encode((FOTO / f'{n}.jpg').read_bytes()).decode()


hoofd_vb, hoofd = comp_hoofd('currentColor')
lig_vb, lig = comp_liggend('currentColor')
HOOFD = f'<svg class="hoofdlogo" viewBox="{hoofd_vb}" role="img" aria-label="Tide Tode">{hoofd}</svg>'
LIG = f'<svg class="liglogo" viewBox="{lig_vb}" role="img" aria-label="Tide Tode">{lig}</svg>'

html = f'''<title>Tide-Tode Logo</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap">
<style>
/* Logosysteem: een grote poster, daarna de vormen van het logo in een raster van tegels. */
:root {{ --navy: {NAVY}; --creme: {CREME}; --papier: #FAF6EE; --mono: 'Courier Prime', 'Courier New', monospace; color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--papier); color: var(--navy); font-family: var(--mono); padding: 48px 16px 80px; }}
main {{ max-width: 1180px; margin: 0 auto; display: grid; gap: 14px; }}
.kop {{ display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px 24px; margin-bottom: 18px; font: 700 12px var(--mono); letter-spacing: .2em; text-transform: uppercase; }}
.poster {{ position: relative; aspect-ratio: 16 / 8; background-size: cover; background-position: center 60%; display: flex; align-items: flex-end; padding: 5%; color: var(--creme); }}
.poster::before {{ content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(20, 28, 44, .1), rgba(20, 28, 44, .5)); }}
.poster > * {{ position: relative; }}
.poster .hoofdlogo {{ width: min(30%, 300px); height: auto; }}
.poster p {{ position: absolute; right: 5%; bottom: 6%; margin: 0; font: 700 12px var(--mono); letter-spacing: .22em; text-transform: uppercase; }}
.raster {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
.tegel {{ position: relative; aspect-ratio: 1; display: grid; place-items: center; padding: 14%; min-width: 0; }}
.tegel.breed {{ grid-column: span 2; aspect-ratio: auto; }}
.creme {{ background: var(--creme); color: var(--navy); }}
.navy {{ background: var(--navy); color: var(--creme); }}
.tegel .label {{ position: absolute; left: 18px; bottom: 14px; margin: 0; font: 700 10.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; opacity: .7; }}
.tegel .hoofdlogo {{ width: 72%; height: auto; }}
.tegel .liglogo {{ width: 84%; height: auto; }}
.tegel .icoon {{ width: 54%; height: auto; }}
.tegel .woord {{ width: 76%; height: auto; }}
.tegel .stempel {{ width: 84%; height: auto; }}
.klein {{ display: flex; align-items: flex-end; gap: 28px; flex-wrap: wrap; justify-content: center; }}
.klein div {{ display: grid; justify-items: center; gap: 10px; font: 700 10px var(--mono); letter-spacing: .14em; }}
.fav {{ display: grid; place-items: center; border-radius: 22%; background: var(--navy); color: var(--creme); }}
.fav svg {{ width: 70%; height: auto; }}
.cirkel {{ width: 62%; aspect-ratio: 1; border-radius: 50%; background: var(--navy); color: var(--creme); display: grid; place-items: center; }}
.cirkel svg {{ width: 56%; height: auto; }}
.regels {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px 40px; padding: 28px 4px 0; font-size: 13px; line-height: 1.65; }}
.regels h2 {{ margin: 0 0 6px; font: 700 12px var(--mono); letter-spacing: .2em; text-transform: uppercase; }}
.regels p {{ margin: 0; }}
@media (max-width: 760px) {{ .raster {{ grid-template-columns: 1fr 1fr; }} .tegel.breed {{ grid-column: 1 / -1; aspect-ratio: 2 / 1; }} .poster {{ aspect-ratio: 4 / 5; }} .poster .hoofdlogo {{ width: 56%; }} }}
</style>
<main>
  <div class="kop"><span>Tide~Tode</span><span>Logo, richting 3</span></div>
  <figure class="poster" style="margin:0;background-image:url({foto('cover')})">{HOOFD}<p>Draagtassen voor surfboards</p></figure>
  <div class="raster">
    <div class="tegel creme">{HOOFD}<p class="label">Hoofdlogo</p></div>
    <div class="tegel navy">{HOOFD}<p class="label">Op donker</p></div>
    <div class="tegel creme">{stempel('stempel')}<p class="label">Stempel</p></div>
    <div class="tegel creme breed" style="padding:9% 8%">{LIG}<p class="label">Liggend, voor de menubalk</p></div>
    <div class="tegel navy">{icoon('icoon')}<p class="label">Icoon</p></div>
    <div class="tegel navy">{woord('gestapeld', 'woord')}<p class="label">Woordmerk</p></div>
    <div class="tegel creme"><div class="cirkel">{icoon()}</div><p class="label">Profielfoto</p></div>
    <div class="tegel creme"><div class="klein">
      <div><span class="fav" style="width:64px;height:64px">{icoon()}</span>64</div>
      <div><span class="fav" style="width:32px;height:32px">{icoon()}</span>32</div>
      <div><span class="fav" style="width:16px;height:16px">{icoon()}</span>16</div>
    </div><p class="label">Favicon</p></div>
    <section class="regels">
      <div><h2>Het idee</h2><p>Een zachte, cursieve letter, alsof Veerle de naam zelf schreef. De tilde tussen de woorden is de golf. Het icoon laat zien waar het merk om draait: je board, gedragen over de golf.</p></div>
      <div><h2>Wanneer welke vorm</h2><p>Het hoofdlogo op labels, verpakking en de voorkant van de site. Liggend in de menubalk en op mails. Het icoon los als favicon, profielfoto en borduursel.</p></div>
      <div><h2>Kleur en ruimte</h2><p>Navy op crème, of crème op navy. Houd rondom minstens de hoogte van de golf vrij. Niet uitrekken, niet draaien, geen schaduw.</p></div>
    </section>
  </div>
</main>'''

PAGINA.write_text(html)
print(PAGINA, round(len(html) / 1024), 'KB', sorted(p.name for p in UITDIR.glob('tide-tode-*')))
