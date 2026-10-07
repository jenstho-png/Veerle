"""Vier typografische logorichtingen, gepresenteerd zoals een studio dat doet:
op een foto, op crème, op navy en als stempel. Schrijft docs/brandbook/logo-richtingen.html."""
import base64, pathlib

HIER = pathlib.Path(__file__).parent
FOTO = HIER.parent / 'brand2' / 'foto'
UIT = HIER.parent.parent / 'docs' / 'brandbook' / 'logo-richtingen.html'


def foto(n):
    return 'data:image/jpeg;base64,' + base64.b64encode((FOTO / f'{n}.jpg').read_bytes()).decode()


R = [
    {'code': 'l1', 'naam': 'Redactioneel', 'idee': 'Twee woorden die verspringen, de golf hangt ertussen als een handtekening. Rustig, luxe en heel leesbaar.',
     'foto': 'g5', 'gest': '<span>Tide</span><span class="ins"><i>~</i>Tode</span>', 'lig': 'Tide<i>~</i>Tode', 'stempel': 'Tide~Tode', 'sfont': "'Instrument Serif', serif", 'sgr': 44},
    {'code': 'l2', 'naam': 'Klassiek label', 'idee': 'Ruim gespatieerde hoofdletters met de golf tussen twee lijnen. Voelt als een etiket of een geweven label.',
     'foto': 'g6', 'gest': '<span>TIDE</span><span class="lijn"><b></b><i>~</i><b></b></span><span>TODE</span><small>EST 2025</small>', 'lig': 'TIDE<i>~</i>TODE', 'stempel': 'TIDE~TODE', 'sfont': "'Bodoni Moda', serif", 'sgr': 23},
    {'code': 'l3', 'naam': 'Zacht en warm', 'idee': 'Een ronde, cursieve letter met veel karakter. De golf loopt mee in het schrift. Persoonlijk, alsof Veerle het zelf schreef.',
     'foto': 'cover', 'gest': '<span>Tide<i>~</i></span><span>Tode</span>', 'lig': 'Tide<i>~</i>Tode', 'stempel': 'Tide~Tode', 'sfont': "'Fraunces', serif", 'sgr': 33},
    {'code': 'l4', 'naam': 'Stevig met tegelkleur', 'idee': 'Compacte, krachtige letters dicht op elkaar, met de golf in terracotta uit de tegelstof van de tas.',
     'foto': 'g2', 'gest': '<span>TIDE</span><span><i>~</i>TODE</span>', 'lig': 'TIDE<i>~</i>TODE', 'stempel': 'TIDE~TODE', 'sfont': "'Gloock', serif", 'sgr': 30},
]


def stempel(r):
    c = r['code']
    return f'''<svg class="stempel" viewBox="0 0 240 240" role="img" aria-label="Stempel {r['stempel']}">
  <defs><path id="o-{c}" d="M28 120a92 92 0 0 0 184 0"/></defs>
  <circle cx="120" cy="120" r="114" fill="none" stroke="currentColor" stroke-width="2.4"/>
  <circle cx="120" cy="120" r="104" fill="none" stroke="currentColor" stroke-width=".9"/>
  <text x="120" y="122" text-anchor="middle" style="font-family:{r['sfont']}" class="s-{c}" font-style="{"italic" if c=="l3" else "normal"}" font-weight="{600 if c=="l3" else 400}" font-size="{r['sgr']}" fill="currentColor">{r['stempel']}</text>
  <text font-family="'Courier Prime', monospace" font-weight="700" font-size="11.5" letter-spacing="3.4" fill="currentColor"><textPath href="#o-{c}" startOffset="50%" text-anchor="middle">VAN SURFERS VOOR SURFERS</textPath></text>
  <text x="120" y="62" text-anchor="middle" font-family="'Courier Prime', monospace" font-weight="700" font-size="11" letter-spacing="3" fill="currentColor">EST 2025</text>
</svg>'''


def blok(r, i):
    c = r['code']
    return f'''
<section class="richting" aria-labelledby="t-{c}">
  <header><span class="nr">{i}</span><div><h2 id="t-{c}">{r['naam']}</h2><p>{r['idee']}</p></div></header>
  <div class="raster">
    <figure class="poster" style="background-image:url({foto(r['foto'])})">
      <div class="lk {c} gest">{r['gest']}</div>
      <figcaption>Draagtassen voor surfboards</figcaption>
    </figure>
    <div class="tegel creme"><div class="lk {c} gest">{r['gest']}</div></div>
    <div class="tegel navy"><div class="lk {c} lig">{r['lig']}</div></div>
    <div class="tegel creme"><div class="lk-stempel">{stempel(r)}</div></div>
    <div class="tegel navy klein"><div class="lk {c} lig mini">{r['lig']}</div><p class="naast">tide-tode.nl</p></div>
  </div>
</section>'''


html = f'''<title>Tide-Tode Logorichtingen</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,500&family=Courier+Prime:wght@400;700&family=Fraunces:ital,opsz,wght,SOFT@1,9..144,600,100&family=Gloock&family=Instrument+Serif:ital@0;1&display=swap">
<style>
/* Studio-presentatie: per richting een fotoposter links (2 rijen hoog) en vier tegels rechts. */
:root {{
  --navy: #22324F; --creme: #F3ECDD; --papier: #FAF6EE; --terra: #C0603E; --lijn: rgba(34, 50, 79, .16);
  --mono: 'Courier Prime', 'Courier New', monospace;
  color-scheme: light;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--papier); color: var(--navy); font-family: var(--mono); padding: 48px 16px 80px; }}
main {{ max-width: 1180px; margin: 0 auto; display: grid; gap: 72px; }}
.kop h1 {{ margin: 0 0 10px; font: 700 13px/1.2 var(--mono); letter-spacing: .22em; text-transform: uppercase; }}
.kop p {{ margin: 0; max-width: 62ch; font-size: 14px; line-height: 1.7; }}
.richting header {{ display: flex; gap: 18px; align-items: baseline; margin-bottom: 20px; }}
.nr {{ font: 700 13px var(--mono); letter-spacing: .1em; }}
.richting h2 {{ margin: 0 0 4px; font: 700 13px/1.2 var(--mono); letter-spacing: .2em; text-transform: uppercase; }}
.richting header p {{ margin: 0; font-size: 13px; line-height: 1.6; max-width: 70ch; opacity: .8; }}
.raster {{ display: grid; grid-template-columns: 1.15fr 1fr 1fr; grid-template-rows: repeat(2, minmax(0, 1fr)); gap: 10px; aspect-ratio: 16 / 9; }}
.poster {{ grid-row: 1 / 3; margin: 0; position: relative; background-size: cover; background-position: center; display: flex; flex-direction: column; justify-content: flex-end; padding: 8%; color: var(--creme); container-type: inline-size; }}
.poster::before {{ content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(20, 28, 44, 0) 35%, rgba(20, 28, 44, .55)); }}
.poster > * {{ position: relative; }}
.poster figcaption {{ margin-top: 5cqw; font: 700 2.6cqw var(--mono); letter-spacing: .24em; text-transform: uppercase; }}
.tegel {{ display: grid; place-items: center; padding: 6%; container-type: inline-size; min-width: 0; position: relative; }}
.creme {{ background: var(--creme); color: var(--navy); }}
.navy {{ background: var(--navy); color: var(--creme); }}
.lk-stempel {{ width: 72cqw; }}
.stempel {{ width: 100%; height: auto; display: block; }}
.naast {{ position: absolute; left: 8%; bottom: 7%; margin: 0; font: 700 3.4cqw var(--mono); letter-spacing: .2em; text-transform: uppercase; opacity: .7; }}

/* ---------- gedeelde opbouw ---------- */
.lk {{ line-height: 1; white-space: nowrap; }}
.lk i {{ font-style: normal; }}
.gest {{ display: flex; flex-direction: column; }}
.poster .gest {{ font-size: 21cqw; }}
.tegel .gest {{ font-size: 25cqw; }}
.lig {{ font-size: 13cqw; }}
.lig.mini {{ font-size: 8.5cqw; }}

/* 1 redactioneel: Instrument Serif, verspringend */
.l1 {{ font-family: 'Instrument Serif', Georgia, serif; letter-spacing: -.01em; }}
.l1.gest {{ line-height: .82; }}
.l1.gest .ins {{ padding-left: .62em; }}
.l1 i {{ font-family: 'Instrument Serif', serif; font-style: italic; display: inline-block; transform: translateY(-.08em); margin: 0 .03em 0 -.02em; }}
.l1.gest i {{ font-size: .9em; }}

/* 2 klassiek label: Bodoni, ruim gespatieerd */
.l2 {{ font-family: 'Bodoni Moda', Didot, serif; font-weight: 500; letter-spacing: .26em; text-align: center; align-items: center; }}
.l2.gest {{ font-size: 15cqw !important; gap: .14em; padding-left: .26em; }}
.poster .l2.gest {{ font-size: 12.5cqw !important; align-self: flex-start; }}
.l2 .lijn {{ display: flex; align-items: center; gap: .3em; width: 100%; letter-spacing: 0; margin-left: -.26em; }}
.l2 .lijn b {{ flex: 1; height: max(1px, .028em); background: currentColor; }}
.l2 .lijn i {{ font-size: .9em; line-height: .5; transform: translateY(-.06em); }}
.l2 small {{ font: 700 .13em var(--mono); letter-spacing: .4em; margin-top: .6em; margin-left: -.26em; }}
.l2.lig i {{ margin: 0 .1em 0 -.12em; }}

/* 3 zacht en warm: Fraunces cursief, soft */
.l3 {{ font-family: 'Fraunces', Georgia, serif; font-style: italic; font-weight: 600; font-variation-settings: 'SOFT' 100, 'opsz' 144; letter-spacing: -.02em; }}
.l3.gest {{ line-height: .86; }}
.l3.gest span + span {{ padding-left: .4em; }}
.l3 i {{ font-style: italic; display: inline-block; transform: translateY(-.1em); }}

/* 4 stevig met tegelkleur: Gloock, compact, golf in terracotta */
.l4 {{ font-family: 'Gloock', Georgia, serif; letter-spacing: -.015em; }}
.l4.gest {{ line-height: .8; }}
.l4.gest span + span {{ margin-left: -.06em; }}
.l4 i {{ color: var(--terra); display: inline-block; transform: translateY(-.06em); margin-right: .02em; }}
.poster .l4 i, .navy .l4 i {{ color: #E09A7E; }}

@media (max-width: 760px) {{
  .raster {{ grid-template-columns: 1fr 1fr; grid-template-rows: auto; aspect-ratio: auto; }}
  .poster {{ grid-column: 1 / -1; grid-row: auto; aspect-ratio: 4 / 5; }}
  .tegel {{ aspect-ratio: 1; }}
}}
</style>
<main>
  <section class="kop"><h1>Tide~Tode, vier logorichtingen</h1>
  <p>Vier richtingen, elk zoals het merk er echt uit zou zien: op een foto, op crème, op navy, als stempel en klein naast een adres. De golf is de tilde uit de letter zelf, zodat alles één geheel blijft.</p></section>
  {"".join(blok(r, f'0{i}') for i, r in enumerate(R, 1))}
</main>'''

UIT.write_text(html)
print(UIT, round(len(html) / 1024), 'KB')
