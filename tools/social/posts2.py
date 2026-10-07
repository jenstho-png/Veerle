"""Social media-pakket, tweede ronde.

Maakt in docs/social/:
- post-01 tot en met post-12: vierkante Instagram-posts (1080x1080 jpg) die samen een raster vormen
- profielfoto.png, highlight-*.png (story-formaat) en facebook-header.png

Fotoposts zijn uitsneden van de studiobeelden in docs/producten/beelden/ en theme/assets/tt-foto-*.
Tekstposts en covers zijn html, gerenderd met Playwright Chromium.

Gebruik: python3 tools/social/posts2.py
"""
import json
import pathlib
import subprocess
import sys

from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import stickers as ST  # noqa: E402

UIT = HIER / 'uit2'
UIT.mkdir(exist_ok=True)
DOEL = ROOT / 'docs' / 'social'
ASSETS = ROOT / 'theme' / 'assets'
PB = ROOT / 'docs' / 'producten' / 'beelden'
L = json.load(open(ROOT / 'tools' / 'brand2' / 'logo2.json'))
IL = json.load(open(ROOT / 'tools' / 'brand2' / 'illustraties.json'))
STK = {s['naam']: s for s in ST.S}

NAVY, CREME, TERRA, BABY, ROSE, ZAND = '#22324F', '#F3ECDD', '#C0603E', '#BFD3EA', '#EDBDB8', '#E3CFAE'
FONTS = ''.join(
    f"@font-face{{font-family:'{f}';src:url('file://{ASSETS / b}') format('woff2');font-weight:{w}}}"
    for f, b, w in [('Courier Prime', 'courierprime-regular.woff2', 400),
                    ('Courier Prime', 'courierprime-bold.woff2', 700),
                    ('Tide Tode Display', 'tide-tode-display.woff2', 400)])


# bouwstenen ---------------------------------------------------------------

def logo(kleur, w, soort='gestapeld'):
    g = L[soort]
    return f'<svg viewBox="0 0 {g["w"]} {g["h"]}" style="width:{w}px;fill:{kleur};display:block"><path d="{g["d"]}"/></svg>'


def icoon(kleur, h):
    b = L['board']
    return f'<svg viewBox="0 0 {b["w"]} {b["h"]}" style="height:{h}px;fill:{kleur};display:block"><path d="{b["d"]}"/></svg>'


def ill(naam, kleur, w, dikte=3.4):
    t = IL[naam]
    paden = ''.join(f'<path d="{d if d.startswith("M") else "M" + d}"/>' for d in t['d'])
    return (f'<svg viewBox="{t["vb"]}" style="width:{w}px;display:block" fill="none" stroke="{kleur}" '
            f'stroke-width="{dikte}" stroke-linecap="round" stroke-linejoin="round">{paden}</svg>')


def sticker(naam, w):
    svg = ST.svg(STK[naam]).replace('<svg ', '<svg style="width:100%;height:auto;display:block" ', 1)
    return f'<div style="width:{w}px">{svg}</div>'


def pagina(naam, b, h, achter, inhoud, kleur=NAVY):
    (UIT / f'{naam}.html').write_text(f'''<!doctype html><meta charset="utf-8"><style>{FONTS}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {b}px; height: {h}px; overflow: hidden; }}
body {{ background: {achter}; color: {kleur}; font-family: 'Courier Prime'; position: relative; }}
.mid {{ position: absolute; inset: 0; display: grid; place-items: center; }}
.label {{ font: 700 26px 'Courier Prime'; letter-spacing: .24em; text-transform: uppercase; }}
.kop {{ font: 400 96px/1 'Tide Tode Display'; text-transform: uppercase; letter-spacing: .01em; }}
.tekst {{ font: 400 32px/1.45 'Courier Prime'; }}
.rand {{ position: absolute; left: 70px; right: 70px; display: flex; justify-content: space-between; }}
</style><body>{inhoud}</body>''')


def hoeken(boven_l, boven_r, onder_l='', onder_r=''):
    """Kleine labels in de hoeken, zoals op de productbeelden."""
    return (f'<div class="rand label" style="top:62px;font-size:23px">{f"<span>{boven_l}</span><span>{boven_r}</span>"}</div>'
            f'<div class="rand label" style="bottom:62px;font-size:23px"><span>{onder_l}</span><span>{onder_r}</span></div>')


# tekstposts (1080x1080) ----------------------------------------------------

TEKSTPOSTS = {}

# 01: merk
TEKSTPOSTS['post-01-merk'] = (NAVY, CREME, hoeken('Tide Tode', 'Sinds 2025', 'Draagtassen', 'Kleding en gear') + f'''
<div class="mid"><div style="display:grid;justify-items:center;gap:56px">
{icoon(CREME, 110)}{logo(CREME, 560)}<p class="label" style="font-size:30px">Voor de weg naar zee</p></div></div>''')

# 05: duurzaamheid
dingen = [('Een dop', 'Van een fles of een blikje'),
          ('Een stuk touw', 'Of visdraad, waar vogels in verstrikt raken'),
          ('Een stukje plastic', 'Een zakje, een rietje, een snoeppapiertje')]
rijen = ''.join(f'''<div style="display:grid;grid-template-columns:84px 1fr;gap:32px;align-items:center">
<div style="width:84px;height:84px;border-radius:50%;background:{TERRA};color:{CREME};display:grid;place-items:center;font:400 44px 'Tide Tode Display'">{i}</div>
<div><p class="label" style="font-size:30px">{t}</p><p class="tekst" style="font-size:31px">{s}</p></div></div>''' for i, (t, s) in enumerate(dingen, 1))
TEKSTPOSTS['post-05-drie-dingen'] = (CREME, NAVY, hoeken('Na het surfen', 'Duurzaamheid', 'Elke keer dat je gaat', 'Zo blijft het strand mooi') + f'''
<div style="position:absolute;left:96px;right:96px;top:150px;display:grid;gap:52px">
<p class="kop" style="font-size:92px">Neem drie<br>dingen mee<br><span style="color:{TERRA}">van het strand</span></p>
<div style="display:grid;gap:40px">{rijen}</div></div>
<div style="position:absolute;right:86px;top:160px">{ill('golf', NAVY, 210)}</div>''')

# 09: het begin, citaat van Veerle
TEKSTPOSTS['post-09-verhaal'] = (TERRA, CREME, hoeken('Ons verhaal', 'Veerle') + f'''
<div style="position:absolute;left:96px;right:96px;top:170px;display:grid;gap:56px">
<p class="kop" style="font-size:98px">“Dit moet<br>stukken<br>comfortabeler<br>kunnen.”</p>
<p class="tekst" style="font-weight:700;font-size:36px;max-width:860px">Na een lange hike naar een verstopte spot, met een longboard onder mijn arm, wist ik het: ik ga een tas maken.</p></div>
<div style="position:absolute;left:96px;bottom:140px">{icoon(CREME, 90)}</div>''')

# 10: zo werkt de draagtas
stappen = [('Leg de tas om je board', 'Op het midden, het balanspunt'),
           ('Trek de band aan', 'Eén band loopt in één stuk rondom'),
           ('Over je schouder', 'Handen vrij, op weg naar zee')]
rijen = ''.join(f'''<div style="display:grid;grid-template-columns:84px 1fr;gap:32px;align-items:center">
<div style="width:84px;height:84px;border-radius:50%;background:{NAVY};color:{CREME};display:grid;place-items:center;font:400 44px 'Tide Tode Display'">{i}</div>
<div><p class="label" style="font-size:30px">{t}</p><p class="tekst" style="font-size:31px">{s}</p></div></div>''' for i, (t, s) in enumerate(stappen, 1))
TEKSTPOSTS['post-10-zo-werkt-het'] = (ROSE, NAVY, hoeken('De draagtas', 'In drie stappen') + f'''
<div style="position:absolute;left:96px;right:96px;top:150px;display:grid;gap:60px">
<p class="kop" style="font-size:100px">Zo werkt<br>de draagtas</p>
<div style="display:grid;gap:44px">{rijen}</div></div>
<div style="position:absolute;right:96px;top:140px;rotate:8deg">{sticker('board', 170)}</div>''')

# fotoposts: (bestand, uitsnede) ---------------------------------------------
# uitsnede = waar het vierkant verticaal begint, als fractie van de vrije ruimte (0 boven, 0.5 midden, 1 onder)
FOTOPOSTS = {
    'post-02-draagtas-tegel': (PB / 'draagtas-tegel-1.jpg', 0.5),
    'post-03-t-shirt-board': (PB / 't-shirt-board-1.jpg', 0.5),
    'post-04-onderweg': (ASSETS / 'tt-foto-avontuur.jpg', 0.75),
    'post-06-pet-navy': (PB / 'pet-navy-1.jpg', 0.5),
    'post-07-longsleeve-zon': (PB / 'longsleeve-zon-1.jpg', 0.5),
    'post-08-draagtas-golfjes': (PB / 'draagtas-golfjes-1.jpg', 0.5),
    'post-11-surfwax-koud': (PB / 'surfwax-koud-1.jpg', 0.5),
    'post-12-draagtas-zonsondergang': (PB / 'draagtas-zonsondergang-1.jpg', 0.5),
}


def vierkant(bron, y):
    im = Image.open(bron).convert('RGB')
    w, h = im.size
    z = min(w, h)
    x0 = (w - z) // 2
    y0 = round((h - z) * y)
    return im.crop((x0, y0, x0 + z, y0 + z)).resize((1080, 1080), Image.LANCZOS)


# profiel, highlights en facebook ------------------------------------------

def covers():
    pagina('profielfoto', 1080, 1080, NAVY, f'<div class="mid">{icoon(CREME, 640)}</div>')
    for naam, kleur, binnen in [
        ('tassen', BABY, icoon(NAVY, 440)),
        ('kleding', ROSE, ill('zon', NAVY, 520)),
        ('gear', ZAND, sticker('wax', 500)),
        ('onderweg', BABY, ill('busje', NAVY, 520)),
        ('strand', ROSE, ill('parasol', NAVY, 520)),
        ('info', ZAND, ill('golf', NAVY, 520)),
    ]:
        pagina(f'highlight-{naam}', 1080, 1920, kleur,
               f'<div class="mid"><div style="width:760px;height:760px;border-radius:50%;background:{CREME};display:grid;place-items:center">{binnen}</div></div>')
    pagina('facebook-header', 1640, 624, NAVY, f'''<div class="mid"><div style="display:flex;align-items:center;gap:70px">
{icoon(CREME, 230)}<div style="display:grid;gap:34px">{logo(CREME, 440)}<p class="label" style="color:{CREME};font-size:24px">Voor de weg naar zee</p></div></div></div>''', CREME)


# renderen -----------------------------------------------------------------

RENDER = r'''
import { chromium } from '../preview/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const map = new URL('./uit2/', 'file://' + process.cwd() + '/').pathname;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
for (const f of fs.readdirSync(map).filter((f) => f.endsWith('.html')).sort()) {
  const html = fs.readFileSync(map + f, 'utf8');
  const w = +html.match(/width: (\d+)px; height/)[1], h = +html.match(/height: (\d+)px; overflow/)[1];
  const p = await b.newPage({ viewport: { width: w, height: h } });
  await p.goto('file://' + map + f);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(150);
  await p.screenshot({ path: map + f.replace('.html', '.png') });
  await p.close();
}
await b.close();
'''


def main():
    for f in UIT.glob('*'):
        f.unlink()
    for naam, (achter, kleur, inhoud) in TEKSTPOSTS.items():
        pagina(naam, 1080, 1080, achter, inhoud, kleur)
    covers()
    subprocess.run(['node', '--input-type=module', '-e', RENDER], cwd=HIER, check=True)

    # oude bestanden weg, zodat de map alleen de huidige set bevat
    for f in list(DOEL.glob('post-*')) + list(DOEL.glob('highlight-*')):
        f.unlink()
    for png in UIT.glob('*.png'):
        if png.stem.startswith('post-'):
            Image.open(png).convert('RGB').save(DOEL / f'{png.stem}.jpg', quality=90, optimize=True)
        else:
            png.replace(DOEL / png.name)
    for png in UIT.glob('*.png'):
        png.unlink()
    for naam, (bron, y) in FOTOPOSTS.items():
        vierkant(bron, y).save(DOEL / f'{naam}.jpg', quality=90, optimize=True)

    # rasteroverzicht (zoals het profiel er straks uitziet)
    posts = sorted(DOEL.glob('post-*.jpg'))
    raster = Image.new('RGB', (3 * 360 + 8, 4 * 360 + 12), 'white')
    for i, p in enumerate(posts):
        im = Image.open(p).resize((358, 358), Image.LANCZOS)
        raster.paste(im, ((i % 3) * 362, (i // 3) * 362))
    raster.save(DOEL / 'raster-voorbeeld.jpg', quality=85)
    print(f'klaar: {len(posts)} posts')


if __name__ == '__main__':
    main()
