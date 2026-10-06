"""Letterproef: de golf en het board-icoon uit het gekozen logo, met zes letterrichtingen.
Schrijft docs/brandbook/logo-letters.html (artifact)."""
import json, pathlib

HIER = pathlib.Path(__file__).parent
UIT = HIER.parent.parent / 'docs' / 'brandbook' / 'logo-letters.html'
S = json.load(open(HIER / 'sporen.json'))
GOLF, ICOON = S['golf']['d'], S['icoon']['d']

RICHTINGEN = [
    ('A', 'Zachte jaren 70', 'Ronde, volle letters met zachte uiteinden. Warm en vrolijk, zoals een oude surfposter.', "'Fraunces', serif", "font-weight:800;font-variation-settings:'SOFT' 100,'WONK' 0,'opsz' 144;letter-spacing:-.01em"),
    ('B', 'Retro rond', 'Dikke, ronde letters met veel karakter. Het meest speels van de zes.', "'Caprasimo', serif", 'letter-spacing:.01em'),
    ('C', 'Mediterraan hotel', 'Een elegante schreefletter met veel contrast. Rustig en luxe.', "'Gloock', serif", 'letter-spacing:.02em'),
    ('D', 'Warm klassiek', 'Een vriendelijke schreefletter met ronde vormen. Tijdloos en betrouwbaar.', "'Young Serif', serif", 'letter-spacing:.01em'),
    ('E', 'Strand in de zon', 'Hoog contrast met bolletjes aan de uiteinden. Zomers en een tikje chic.', "'DM Serif Display', serif", 'letter-spacing:.02em'),
    ('F', 'Met de hand', 'Met een kwast geschreven hoofdletters. Persoonlijk, alsof Veerle het zelf schilderde.', "'Caveat Brush', cursive", 'letter-spacing:.02em'),
]

golf = f'<svg class="golf" viewBox="0 33 260 94" aria-hidden="true"><path d="{GOLF}"/></svg>'
icoon = f'<svg class="icoon" viewBox="0 0 326 300" aria-hidden="true"><path d="{ICOON}"/></svg>'


def kaart(code, naam, uitleg, familie, extra):
    stijl = f"font-family:{familie};{extra}"
    return f'''
<article class="kaart" id="richting-{code.lower()}">
  <header><span class="code">{code}</span><div><h2>{naam}</h2><p>{uitleg}</p></div></header>
  <div class="vlak licht"><div class="lock" style="{stijl}" role="img" aria-label="TIDE TODE"><span>TIDE</span>{golf}<span>TODE</span></div></div>
  <div class="rij">
    <div class="vlak donker"><div class="lock klein" style="{stijl}" role="img" aria-label="TIDE TODE"><span>TIDE</span>{golf}<span>TODE</span></div></div>
    <div class="vlak licht badge-vlak">
      <svg class="badge" viewBox="0 0 300 300" role="img" aria-label="Zegel TIDE TODE">
        <defs><path id="b-{code}" d="M52 150a98 98 0 0 1 196 0"/><path id="o-{code}" d="M30 150a120 120 0 0 0 240 0"/></defs>
        <circle cx="150" cy="150" r="140" fill="none" stroke="currentColor" stroke-width="4"/>
        <text style="{stijl}" font-size="31" fill="currentColor"><textPath href="#b-{code}" startOffset="50%" text-anchor="middle">TIDE~TODE</textPath></text>
        <text font-family="'Courier Prime', monospace" font-weight="700" font-size="16" letter-spacing="4" fill="currentColor"><textPath href="#o-{code}" startOffset="50%" text-anchor="middle">VAN SURFERS VOOR SURFERS</textPath></text>
        <g transform="translate(96 92) scale(.33)"><path d="{ICOON}" fill="currentColor"/></g>
      </svg>
    </div>
  </div>
</article>'''


html = f'''<title>Tide-Tode Logoletters</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caprasimo&family=Caveat+Brush&family=Courier+Prime:wght@400;700&family=DM+Serif+Display&family=Fraunces:opsz,wght,SOFT,WONK@9..144,800,0..100,0..1&family=Gloock&family=Young+Serif&display=swap">
<style>
/* Proefvel: zes kaarten in een raster; per kaart het logo groot op crème, klein op navy, en het zegel. */
:root {{
  --navy: #22324F; --creme: #F3ECDD; --papier: #FBF7EF; --lijn: rgba(34, 50, 79, .18);
  --mono: 'Courier Prime', 'Courier New', monospace;
  color-scheme: light;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--creme); color: var(--navy); font-family: var(--mono); padding: 40px 16px 72px; }}
main {{ max-width: 1240px; margin: 0 auto; display: grid; gap: 32px; }}
.intro {{ display: grid; grid-template-columns: auto 1fr; gap: 28px; align-items: center; }}
.intro .icoon {{ width: 96px; fill: var(--navy); }}
.intro h1 {{ margin: 0 0 8px; font: 700 15px/1.2 var(--mono); letter-spacing: .18em; text-transform: uppercase; }}
.intro p {{ margin: 0; max-width: 64ch; font-size: 14px; line-height: 1.7; }}
.raster {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 560px), 1fr)); gap: 24px; }}
.kaart {{ background: var(--papier); border: 1px solid var(--lijn); padding: 22px; display: grid; gap: 14px; min-width: 0; }}
.kaart header {{ display: flex; gap: 16px; align-items: flex-start; }}
.code {{ flex-shrink: 0; display: grid; place-items: center; width: 34px; height: 34px; border: 1.5px solid var(--navy); border-radius: 50%; font: 700 14px var(--mono); }}
.kaart h2 {{ margin: 2px 0 4px; font: 700 13px/1.2 var(--mono); letter-spacing: .16em; text-transform: uppercase; }}
.kaart p {{ margin: 0; font-size: 13px; line-height: 1.55; opacity: .8; }}
.vlak {{ display: grid; place-items: center; padding: 34px 20px; container-type: inline-size; }}
.licht {{ background: var(--creme); color: var(--navy); }}
.donker {{ background: var(--navy); color: var(--creme); }}
.rij {{ display: grid; grid-template-columns: 1.6fr 1fr; gap: 14px; }}
.lock {{ display: flex; align-items: center; font-size: 13.5cqw; line-height: 1; white-space: nowrap; }}
.lock.klein {{ font-size: 13cqw; }}
.lock .golf {{ width: 1.55em; height: auto; margin: .12em -.06em 0; fill: currentColor; flex-shrink: 0; }}
.badge {{ width: 100%; max-width: 170px; color: var(--navy); }}
.badge-vlak {{ padding: 16px; }}
.voet {{ font-size: 13px; line-height: 1.6; max-width: 70ch; }}
@media (max-width: 520px) {{ .rij {{ grid-template-columns: 1fr; }} }}
</style>
<main>
  <section class="intro">{icoon.replace('class="icoon"', 'class="icoon"')}
    <div><h1>Tide~Tode, zes letterrichtingen</h1>
    <p>De golf tussen de woorden en het board met de golf komen uit het logo dat je goed vond. Alleen de letters verschillen. Kies een letter (A tot en met F), dan teken ik die richting uit tot een vast logo.</p></div>
  </section>
  <div class="raster">{"".join(kaart(*r) for r in RICHTINGEN)}</div>
  <p class="voet">Alle letters zijn gratis te gebruiken (Google Fonts, Open Font License). Het gekozen logo zet ik daarna om naar vaste vormen, zodat het er overal precies hetzelfde uitziet.</p>
</main>'''

UIT.write_text(html)
print(UIT, round(len(html) / 1024), 'KB')
