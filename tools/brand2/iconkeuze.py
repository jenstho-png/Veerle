"""Icoonkeuze: vier iconen naast het blok-logo, als favicon en op navy. Schrijft docs/brandbook/icoon-keuze.html."""
import json, pathlib

HIER = pathlib.Path(__file__).parent
I = json.load(open(HIER / 'iconen.json'))
L = json.load(open(HIER / 'logo2.json'))
UIT = HIER.parent.parent / 'docs' / 'brandbook' / 'icoon-keuze.html'
G, B = L['gestapeld'], L['board']

OPTIES = [
    ('A', 'Board met golven', 'Het board met twee golven erdoorheen. Simpel, en hetzelfde board als de I in het logo.', f'<svg viewBox="0 0 400 400"><path fill-rule="evenodd" d="{I["board-golf"]}"/></svg>'),
    ('B', 'Zon en zee', 'Het board staat in een ronde zon, met de zee eronder. Werkt als zegel en als profielfoto.', f'<svg viewBox="0 0 400 400"><path fill-rule="evenodd" d="{I["zon"]}"/></svg>'),
    ('C', 'De tegel', 'Een afgeronde tegel met het board en de golven eruit geknipt. Verwijst naar de tegelstof van de tas.', f'<svg viewBox="0 0 400 400"><path fill-rule="evenodd" d="{I["tegel"]}"/></svg>'),
    ('D', 'Huidig icoon', 'Het board met de golf eroverheen, zoals het nu op de site staat.', f'<svg viewBox="0 0 {B["w"]} {B["h"]}"><path d="{B["d"]}"/></svg>'),
]
LOGO = f'<svg class="blok" viewBox="0 0 {G["w"]} {G["h"]}" role="img" aria-label="Tide Tode"><path d="{G["d"]}"/></svg>'


def kaart(code, naam, uitleg, svg):
    return f'''<article class="kaart">
  <header><span class="code">{code}</span><div><h2>{naam}</h2><p>{uitleg}</p></div></header>
  <div class="rij">
    <div class="vlak licht groot">{svg}</div>
    <div class="vlak donker lock"><div class="ic">{svg}</div>{LOGO}</div>
  </div>
  <div class="rij klein">
    <div class="vlak licht"><span class="fav">{svg}</span><span class="fav s">{svg}</span><span class="fav xs">{svg}</span></div>
    <div class="vlak licht"><span class="sticker">{svg}</span></div>
  </div>
</article>'''


html = f'''<title>Tide-Tode Icoonkeuze</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@700&display=swap">
<style>
/* Per icoon: groot, met het logo op navy, als favicon en als sticker. */
:root {{ --navy: #22324F; --creme: #F3ECDD; --papier: #FAF6EE; --lijn: rgba(34, 50, 79, .16); --mono: 'Courier Prime', 'Courier New', monospace; color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--papier); color: var(--navy); font-family: var(--mono); padding: 44px 16px 72px; }}
main {{ max-width: 1180px; margin: 0 auto; display: grid; gap: 28px; }}
h1 {{ margin: 0; font: 700 13px var(--mono); letter-spacing: .2em; text-transform: uppercase; }}
.raster {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 540px), 1fr)); gap: 22px; }}
.kaart {{ background: #fff8; border: 1px solid var(--lijn); padding: 20px; display: grid; gap: 10px; min-width: 0; }}
.kaart header {{ display: flex; gap: 14px; align-items: flex-start; margin-bottom: 6px; }}
.code {{ flex-shrink: 0; display: grid; place-items: center; width: 32px; height: 32px; border: 1.5px solid currentColor; border-radius: 50%; font: 700 13px var(--mono); }}
h2 {{ margin: 2px 0 4px; font: 700 12px var(--mono); letter-spacing: .18em; text-transform: uppercase; }}
.kaart p {{ margin: 0; font-size: 12.5px; line-height: 1.55; opacity: .8; }}
.rij {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
.vlak {{ display: flex; align-items: center; justify-content: center; gap: 18px; padding: 24px; min-width: 0; }}
.licht {{ background: var(--creme); fill: var(--navy); }}
.donker {{ background: var(--navy); fill: var(--creme); }}
.groot svg {{ width: 62%; height: auto; }}
.lock {{ flex-direction: column; gap: 12px; }}
.lock .ic svg {{ width: 54px; height: auto; display: block; }}
.lock .blok {{ width: 64%; height: auto; }}
.klein .vlak {{ min-height: 110px; }}
.fav {{ display: grid; place-items: center; width: 56px; height: 56px; border-radius: 13px; background: var(--navy); fill: var(--creme); }}
.fav svg {{ width: 72%; height: auto; }}
.fav.s {{ width: 32px; height: 32px; border-radius: 8px; }}
.fav.xs {{ width: 18px; height: 18px; border-radius: 4px; }}
.sticker {{ display: grid; place-items: center; width: 84px; height: 84px; border-radius: 50%; background: var(--navy); fill: var(--creme); box-shadow: 0 0 0 5px #fff, 0 6px 14px rgba(0,0,0,.18); transform: rotate(-8deg); }}
.sticker svg {{ width: 62%; height: auto; }}
</style>
<main>
  <h1>Tide~Tode, kies een icoon</h1>
  <div class="raster">{"".join(kaart(*o) for o in OPTIES)}</div>
</main>'''
UIT.write_text(html)
print(UIT)
