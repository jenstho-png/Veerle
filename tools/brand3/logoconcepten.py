"""Logoconcepten ronde 4: gestapelde logo's met een eigen golf, elk met een liggende versie en een icoon.
Schrijft docs/brandbook/logo-concepten.html (artifact)."""
import math, pathlib

UIT = pathlib.Path(__file__).parent.parent.parent / 'docs' / 'brandbook' / 'logo-concepten.html'
NAVY, CREME = '#22324F', '#F3ECDD'

FR = "font-family:'Fraunces',serif;font-weight:800;font-variation-settings:'SOFT' 100,'WONK' 0,'opsz' 144"
GL = "font-family:'Gloock',serif"
DM = "font-family:'DM Serif Display',serif"
MONO = "font-family:'Courier Prime',monospace;font-weight:700"


def golf(x, y, w, dikte=None, kleur='currentColor'):
    """De nieuwe golf: een tilde die bovenaan omkrult. (x, y) = linksmidden, w = breedte."""
    d = dikte or w * 0.075
    P = lambda a, b: f'{x + a * w:.1f} {y + b * w:.1f}'
    pad = (f'M{P(0, .05)} C{P(.17, .05)} {P(.27, -.14)} {P(.47, -.14)} C{P(.64, -.14)} {P(.71, -.03)} {P(.65, .04)} '
           f'C{P(.6, .09)} {P(.52, .06)} {P(.54, .0)}')
    staart = f'M{P(.62, .1)} C{P(.76, .14)} {P(.88, .06)} {P(1, .02)}'
    return (f'<path d="{pad}" fill="none" stroke="{kleur}" stroke-width="{d:.1f}" stroke-linecap="round"/>'
            f'<path d="{staart}" fill="none" stroke="{kleur}" stroke-width="{d:.1f}" stroke-linecap="round"/>')


def board(cx, top, h, kleur='currentColor', stringer=CREME):
    b = h * 0.34
    p = (f'M{cx} {top} C{cx + b * .72} {top + h * .2} {cx + b * .62} {top + h * .8} {cx + b * .3} {top + h} '
         f'L{cx - b * .3} {top + h} C{cx - b * .62} {top + h * .8} {cx - b * .72} {top + h * .2} {cx} {top} Z')
    return f'<path d="{p}" fill="{kleur}"/><line x1="{cx}" y1="{top + h * .14}" x2="{cx}" y2="{top + h * .9}" stroke="{stringer}" stroke-width="{h * .03:.1f}" stroke-linecap="round"/>'


def tekst(x, y, s, grootte, stijl, anker='middle', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{grootte}" text-anchor="{anker}" style="{stijl}" fill="currentColor" {extra}>{s}</text>'


def svg(vb, inhoud, cls='logo'):
    return f'<svg class="{cls}" viewBox="{vb}" role="img" aria-label="Tide Tode">{inhoud}</svg>'


# ---------- A: zuil (vier kolommen, I = board, O = zon met golf) ----------
def a_gestapeld(bg=CREME):
    kol = [60, 170, 280, 390]
    o = (f'<circle cx="{kol[1]}" cy="{235 - 42}" r="44" fill="currentColor"/>'
         + golf(kol[1] - 40, 235 - 36, 80, 9, bg))
    r1 = tekst(kol[0], 128, 'T', 124, FR) + board(kol[1], 40, 90) + tekst(kol[2], 128, 'D', 124, FR) + tekst(kol[3], 128, 'E', 124, FR)
    r2 = tekst(kol[0], 238, 'T', 124, FR) + o + tekst(kol[2], 238, 'D', 124, FR) + tekst(kol[3], 238, 'E', 124, FR)
    return svg('0 20 450 240', r1 + r2)


def a_liggend(bg=CREME):
    return svg('0 0 760 110', tekst(0, 92, 'T', 112, FR, 'start') + board(98, 16, 82) + tekst(128, 92, 'DE', 112, FR, 'start')
               + golf(292, 56, 130, 14) + tekst(436, 92, 'TODE', 112, FR, 'start'))


def a_icoon(bg=CREME):
    return svg('0 0 120 120', f'<circle cx="60" cy="60" r="56" fill="currentColor"/>' + golf(14, 66, 92, 10, bg), 'icoon')


# ---------- B: golflijn (de golf als lijn tussen de woorden) ----------
def b_gestapeld(bg=CREME):
    return svg('0 0 460 330', tekst(230, 112, 'TIDE', 132, GL) + golf(80, 172, 300, 11)
               + tekst(230, 312, 'TODE', 132, GL)
               + tekst(20, 178, 'EST.', 15, MONO, 'start', 'letter-spacing="3"') + tekst(440, 178, '2025', 15, MONO, 'end', 'letter-spacing="3"'))


def b_liggend(bg=CREME):
    return svg('0 0 760 120', tekst(0, 98, 'TIDE', 116, GL, 'start') + golf(282, 64, 170, 11) + tekst(468, 98, 'TODE', 116, GL, 'start'))


def b_icoon(bg=CREME):
    return svg('0 0 120 120', f'<rect x="4" y="4" width="112" height="112" rx="10" fill="none" stroke="currentColor" stroke-width="5"/>'
               + tekst(60, 58, 'TT', 46, GL) + golf(22, 82, 76, 6), 'icoon')


# ---------- C: surfclub (TIDE in een boog, TODE recht, golf ertussen) ----------
def c_gestapeld(bg=CREME):
    return svg('0 0 460 330', '<defs><path id="boog" d="M40 176 A250 250 0 0 1 420 176"/></defs>'
               + f'<text font-size="104" style="{FR}" fill="currentColor" letter-spacing="8"><textPath href="#boog" startOffset="50%" text-anchor="middle">TIDE</textPath></text>'
               + golf(160, 200, 140, 12) + tekst(230, 300, 'TODE', 104, FR, 'middle', 'letter-spacing="8"')
               + tekst(40, 206, 'SURF', 15, MONO, 'start', 'letter-spacing="4"') + tekst(420, 206, 'CLUB', 15, MONO, 'end', 'letter-spacing="4"'))


def c_liggend(bg=CREME):
    return svg('0 0 760 110', tekst(0, 92, 'TIDE', 104, FR, 'start', 'letter-spacing="6"') + golf(292, 56, 150, 13)
               + tekst(460, 92, 'TODE', 104, FR, 'start', 'letter-spacing="6"'))


def c_icoon(bg=CREME):
    return svg('0 0 120 120', board(60, 10, 100) + golf(18, 62, 84, 9, 'currentColor'), 'icoon')


# ---------- D: embleem (ovaal met het hele merk erin) ----------
def d_gestapeld(bg=CREME):
    return svg('0 0 460 330', '<defs><path id="ob" d="M70 165 A160 125 0 0 1 390 165"/><path id="oo" d="M58 165 A172 137 0 0 0 402 165"/></defs>'
               + '<ellipse cx="230" cy="165" rx="214" ry="156" fill="none" stroke="currentColor" stroke-width="5"/>'
               + '<ellipse cx="230" cy="165" rx="200" ry="142" fill="none" stroke="currentColor" stroke-width="1.6"/>'
               + tekst(230, 140, 'TIDE', 82, DM) + golf(184, 164, 92, 7) + tekst(230, 248, 'TODE', 82, DM)
               + f'<text font-size="15" style="{MONO}" fill="currentColor" letter-spacing="4"><textPath href="#ob" startOffset="50%" text-anchor="middle">SURFBOARD DRAAGTASSEN</textPath></text>'
               + f'<text font-size="15" style="{MONO}" fill="currentColor" letter-spacing="4"><textPath href="#oo" startOffset="50%" text-anchor="middle">VAN SURFERS VOOR SURFERS</textPath></text>')


def d_liggend(bg=CREME):
    return svg('0 0 760 110', tekst(0, 94, 'TIDE', 112, DM, 'start') + golf(268, 58, 150, 11) + tekst(432, 94, 'TODE', 112, DM, 'start'))


def d_icoon(bg=CREME):
    return svg('0 0 120 120', '<ellipse cx="60" cy="60" rx="56" ry="44" fill="none" stroke="currentColor" stroke-width="5"/>' + golf(18, 64, 84, 8), 'icoon')


# ---------- E: tegel (verwijst naar de tegelstof van de tas) ----------
def hoekje(x, y, r, rot, kleur):
    return f'<path transform="translate({x} {y}) rotate({rot})" d="M0 0 L{r} 0 A{r} {r} 0 0 1 0 {r} Z" fill="{kleur}"/>'


def e_gestapeld(bg=CREME):
    k = ''.join(hoekje(x, y, 34, r, bg) for x, y, r in ((22, 22, 0), (438, 22, 90), (438, 308, 180), (22, 308, 270)))
    ruit = ''.join(f'<path d="M{x} {y - 9} L{x + 9} {y} L{x} {y + 9} L{x - 9} {y} Z" fill="{bg}"/>' for x, y in ((230, 40), (230, 290)))
    return svg('0 0 460 330', f'<rect width="460" height="330" rx="6" fill="currentColor"/><rect x="22" y="22" width="416" height="286" fill="none" stroke="{bg}" stroke-width="2.4"/>'
               + k + ruit + f'<g fill="{bg}">' + tekst(230, 142, 'TIDE', 96, FR).replace('fill="currentColor"', f'fill="{bg}"')
               + '</g>' + golf(176, 168, 108, 9, bg) + tekst(230, 270, 'TODE', 96, FR).replace('fill="currentColor"', f'fill="{bg}"'))


def e_liggend(bg=CREME):
    return svg('0 0 760 110', tekst(0, 92, 'TIDE', 108, FR, 'start') + golf(282, 56, 150, 13) + tekst(450, 92, 'TODE', 108, FR, 'start'))


def e_icoon(bg=CREME):
    k = ''.join(hoekje(x, y, 22, r, bg) for x, y, r in ((10, 10, 0), (110, 10, 90), (110, 110, 180), (10, 110, 270)))
    return svg('0 0 120 120', '<rect width="120" height="120" rx="4" fill="currentColor"/>' + k + golf(22, 64, 76, 8, bg), 'icoon')


CONCEPTEN = [
    ('A', 'De zuil', 'TIDE en TODE delen dezelfde letters op dezelfde plek. In de middelste kolom wordt de I een surfboard en de O een zon boven de golf. Een logo dat je ook zonder te lezen herkent.', a_gestapeld, a_liggend, a_icoon),
    ('B', 'De golflijn', 'De golf wordt de lijn tussen de woorden, met de krul precies in het midden. Rustig en klassiek, zoals een etiket.', b_gestapeld, b_liggend, b_icoon),
    ('C', 'De surfclub', 'TIDE in een boog als een clubembleem, TODE er recht onder. Speels en sportief, werkt goed op shirts en stickers.', c_gestapeld, c_liggend, c_icoon),
    ('D', 'Het embleem', 'Het hele merk in een ovaal, met tekst rondom. Voelt als een geweven label in de tas.', d_gestapeld, d_liggend, d_icoon),
    ('E', 'De tegel', 'Een vierkante tegel met hoekjes, net als de tegelstof van de tas. Het product en het logo horen zo echt bij elkaar.', e_gestapeld, e_liggend, e_icoon),
]


def kaart(code, naam, uitleg, gest, lig, ico):
    return f'''
<article class="kaart">
  <header><span class="code">{code}</span><div><h2>{naam}</h2><p>{uitleg}</p></div></header>
  <div class="hoofd licht">{gest(CREME)}</div>
  <div class="rij">
    <div class="vlak donker">{gest(NAVY)}</div>
    <div class="vlak licht">{ico(CREME)}</div>
    <div class="vlak donker">{ico(NAVY)}</div>
  </div>
  <div class="vlak licht breed">{lig(CREME)}</div>
</article>'''


html = f'''<title>Tide-Tode Logo Concepten</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=DM+Serif+Display&family=Fraunces:opsz,wght,SOFT,WONK@9..144,800,0..100,0..1&family=Gloock&display=swap">
<style>
/* Per concept: groot gestapeld logo, daaronder op navy en de iconen, onderaan de liggende versie. */
:root {{ --navy: {NAVY}; --creme: {CREME}; --papier: #FBF7EF; --lijn: rgba(34, 50, 79, .18); --mono: 'Courier Prime', 'Courier New', monospace; color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--creme); color: var(--navy); font-family: var(--mono); padding: 40px 16px 72px; }}
main {{ max-width: 1240px; margin: 0 auto; display: grid; gap: 32px; }}
.intro h1 {{ margin: 0 0 10px; font: 700 15px/1.2 var(--mono); letter-spacing: .18em; text-transform: uppercase; }}
.intro p {{ margin: 0; max-width: 66ch; font-size: 14px; line-height: 1.7; }}
.raster {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 560px), 1fr)); gap: 24px; }}
.kaart {{ background: var(--papier); border: 1px solid var(--lijn); padding: 22px; display: grid; gap: 12px; min-width: 0; }}
.kaart header {{ display: flex; gap: 16px; align-items: flex-start; margin-bottom: 4px; }}
.code {{ flex-shrink: 0; display: grid; place-items: center; width: 34px; height: 34px; border: 1.5px solid var(--navy); border-radius: 50%; font: 700 14px var(--mono); }}
.kaart h2 {{ margin: 2px 0 4px; font: 700 13px/1.2 var(--mono); letter-spacing: .16em; text-transform: uppercase; }}
.kaart p {{ margin: 0; font-size: 13px; line-height: 1.55; opacity: .82; }}
.licht {{ background: var(--creme); color: var(--navy); }}
.donker {{ background: var(--navy); color: var(--creme); }}
.hoofd {{ display: grid; place-items: center; padding: 44px 24px; }}
.hoofd .logo {{ width: min(100%, 360px); height: auto; }}
.rij {{ display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 12px; }}
.vlak {{ display: grid; place-items: center; padding: 20px 14px; min-width: 0; }}
.vlak .logo {{ width: 100%; max-width: 200px; height: auto; }}
.vlak .icoon {{ width: 70px; height: auto; }}
.breed .logo {{ max-width: 380px; }}
svg {{ overflow: visible; }}
@media (max-width: 520px) {{ .rij {{ grid-template-columns: 1fr 1fr; }} .rij .vlak:first-child {{ grid-column: 1 / -1; }} }}
</style>
<main>
  <section class="intro"><h1>Tide~Tode, vijf logoconcepten</h1>
  <p>Een nieuwe golf, en elk concept als gestapeld logo, als liggende versie en als klein icoon. Zo zie je hoe het merk op een label, een sticker, de website en als favicon werkt. Kies een concept, dan werk ik het uit tot het definitieve logo.</p></section>
  <div class="raster">{"".join(kaart(*c) for c in CONCEPTEN)}</div>
</main>'''

UIT.write_text(html)
print(UIT, round(len(html) / 1024), 'KB')
