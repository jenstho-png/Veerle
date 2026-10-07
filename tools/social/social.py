"""Social media-pakket: profielfoto, highlight-covers, 9 eerste posts en een Facebook-header.
Schrijft html naar tools/social/uit/ (render.mjs maakt er png's van) en zet bestaande productbeelden om naar 1080x1350."""
import json, pathlib, sys
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import stickers as ST  # noqa: E402

UIT = HIER / 'uit'; UIT.mkdir(exist_ok=True)
DOEL = ROOT / 'docs' / 'social'; DOEL.mkdir(parents=True, exist_ok=True)
ASSETS = ROOT / 'theme' / 'assets'
PB = ROOT / 'docs' / 'producten' / 'beelden'
L = json.load(open(ROOT / 'tools' / 'brand2' / 'logo2.json'))
IL = json.load(open(ROOT / 'tools' / 'brand2' / 'illustraties.json'))
G, BD = L['gestapeld'], L['board']
NAVY, CREME, BABY, ROSE, ZAND = '#22324F', '#F3ECDD', '#BFD3EA', '#EDBDB8', '#E3CFAE'
FONTS = ''.join(f"@font-face{{font-family:'{f}';src:url('file://{ASSETS / b}') format('woff2');font-weight:{w}}}"
                for f, b, w in [('Courier Prime', 'courierprime-bold.woff2', 700), ('Homemade Apple', 'homemadeapple-regular.woff2', 400), ('Tide Tode Display', 'tide-tode-display.woff2', 400)])


def logo(kleur, w):
    return f'<svg viewBox="0 0 {G["w"]} {G["h"]}" style="width:{w}px;fill:{kleur};display:block"><path d="{G["d"]}"/></svg>'


def icoon(kleur, h):
    return f'<svg viewBox="0 0 {BD["w"]} {BD["h"]}" style="height:{h}px;fill:{kleur};display:block"><path d="{BD["d"]}"/></svg>'


def ill(naam, kleur, w):
    t = IL[naam]
    paden = ''.join(f'<path d="{d if d.startswith("M") else "M" + d}"/>' for d in t['d'])
    return f'<svg viewBox="{t["vb"]}" style="width:{w}px" fill="none" stroke="{kleur}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">{paden}</svg>'


def pagina(naam, b, h, achter, inhoud):
    (UIT / f'{naam}.html').write_text(f'''<!doctype html><meta charset="utf-8"><style>{FONTS}
* {{ margin: 0; box-sizing: border-box; }} html, body {{ width: {b}px; height: {h}px; overflow: hidden; }}
body {{ background: {achter}; color: {NAVY}; display: grid; place-items: center; font-family: 'Courier Prime'; position: relative; }}
.label {{ font: 700 26px 'Courier Prime'; letter-spacing: .24em; text-transform: uppercase; }}
.hand {{ font: 400 54px/1.3 'Homemade Apple'; }}
</style><body>{inhoud}</body>''')


# profielfoto
pagina('profielfoto', 1080, 1080, NAVY, icoon(CREME, 640))
# highlight-covers (story-formaat, icoon in een cirkel in het midden)
for naam, kleur, binnen in [('tassen', BABY, ill('golf', NAVY, 520)), ('onderweg', ZAND, ill('busje', NAVY, 520)),
                            ('stranddag', ROSE, ill('parasol', NAVY, 520)), ('zon', BABY, ill('zon', NAVY, 520)), ('info', ZAND, icoon(NAVY, 440))]:
    pagina(f'highlight-{naam}', 1080, 1920, kleur, f'<div style="width:760px;height:760px;border-radius:50%;background:{CREME};display:grid;place-items:center">{binnen}</div>')
# eigen posts
pagina('post-01-logo', 1080, 1350, CREME, f'<div style="display:grid;justify-items:center;gap:60px">{icoon(NAVY, 120)}{logo(NAVY, 640)}<p class="label">Draagtassen voor je surfboard</p></div>')
pagina('post-06-verhaal', 1080, 1350, NAVY,
       f'<div style="color:{CREME};padding:110px;display:grid;gap:50px"><p style="font:400 92px/1.02 \'Tide Tode Display\';letter-spacing:.02em;text-transform:uppercase">“Dit moet stukken comfortabeler kunnen.”</p>'
       f'<p style="font:700 30px/1.6 \'Courier Prime\'">Na een lange hike naar een verstopte spot, met een longboard onder mijn arm, wist ik het: ik ga een tas maken.</p><p class="hand" style="font-size:60px">Veerle</p></div>')
S = {s['naam']: s for s in ST.S}
stk = ''
for n, x, y, r, w in [('golf', 140, 160, -10, 300), ('zon', 700, 120, 8, 260), ('schelp', 120, 820, 6, 260), ('palm', 760, 760, -6, 240), ('zeester', 450, 1000, 12, 220), ('busje', 420, 420, 3, 300)]:
    svg = ST.svg(S[n]).replace('<svg ', '<svg style="width:100%;height:auto;display:block" ', 1)
    stk += f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;rotate:{r}deg">{svg}</div>'
pagina('post-09-stickers', 1080, 1350, BABY, stk + f'<p class="label" style="position:absolute;bottom:60px;left:0;right:0;text-align:center">De stickerset ligt in de shop</p>')
# facebook-header
pagina('facebook-header', 1640, 624, NAVY, f'<div style="display:flex;align-items:center;gap:80px">{icoon(CREME, 260)}{logo(CREME, 520)}</div>')

# bestaande productbeelden als post (4:5, 1080x1350)
for nr, bron in [('02', 'draagtas-tegel-1'), ('03', 'draagtas-tegel-3'), ('04', 't-shirt-zonsopkomst-2'), ('05', 'draagtas-tegel-2'), ('07', 'hoodie-busje-2'), ('08', 'draagtas-golfjes-1')]:
    im = Image.open(PB / f'{bron}.jpg').convert('RGB').resize((1080, 1350), Image.LANCZOS)
    im.save(DOEL / f'post-{nr}-{bron}.jpg', quality=88, optimize=True)
print('klaar')
