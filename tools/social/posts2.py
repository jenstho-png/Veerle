"""Social media-pakket, tweede ronde.

Maakt in docs/social/:
- profielfoto.png, highlight-*.png (story-formaat) en facebook-header.png

De covers zijn html, gerenderd met Playwright Chromium.
De Instagram-posts zelf (carrousels in 4:5) komen uit carrousels.py.

Gebruik: python3 tools/social/posts2.py
"""
import json
import pathlib
import subprocess
import sys


HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import stickers as ST  # noqa: E402

UIT = HIER / 'uit2'
UIT.mkdir(exist_ok=True)
DOEL = ROOT / 'docs' / 'social'
ASSETS = ROOT / 'theme' / 'assets'
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
    covers()
    subprocess.run(['node', '--input-type=module', '-e', RENDER], cwd=HIER, check=True)

    for f in DOEL.glob('highlight-*'):
        f.unlink()
    for png in UIT.glob('*.png'):
        png.replace(DOEL / png.name)
    print('klaar: profielfoto, highlights en facebook-header')


if __name__ == '__main__':
    main()
