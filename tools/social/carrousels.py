"""Instagram-carrousels (staand 4:5, 1080x1350).

Maakt in docs/social/:
- post-01-<naam>/ tot en met post-09-<naam>/, elk met slide-1.jpg, slide-2.jpg enzovoort
- raster-voorbeeld.jpg: de eerste slides in drie kolommen, zoals je profiel eruitziet

De foto's doen het werk. Tekst is hooguit één korte regel per slide en de meeste slides hebben geen tekst.
Slides met tekst worden als html gerenderd met Playwright Chromium (zelfde fonts als posts2.py en tt.css).
Profielfoto, highlights en Facebook-header komen nog steeds uit posts2.py.

Gebruik: python3 tools/social/carrousels.py
"""
import pathlib
import shutil
import subprocess

from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
UIT = HIER / 'uit3'
DOEL = ROOT / 'docs' / 'social'
ASSETS = ROOT / 'theme' / 'assets'
PB = ROOT / 'docs' / 'producten' / 'beelden'

B, H = 1080, 1350
NAVY, CREME = '#22324F', '#F3ECDD'
FONTS = ''.join(
    f"@font-face{{font-family:'{f}';src:url('file://{ASSETS / b}') format('woff2');font-weight:{w}}}"
    for f, b, w in [('Courier Prime', 'courierprime-bold.woff2', 700),
                    ('Tide Tode Display', 'tide-tode-display.woff2', 400),
                    ('Homemade Apple', 'homemadeapple-regular.woff2', 400)])


# tekstsoorten: (css, plek)
def label(t, kleur=NAVY, plek='onder'):
    """Klein label in hoofdletters, zoals op de productbeelden."""
    pos = {'onder': 'left:72px;bottom:76px', 'boven': 'left:72px;top:76px',
           'rechtsonder': 'right:72px;bottom:76px'}[plek]
    return (f'<p style="position:absolute;{pos};font:700 27px Courier Prime;letter-spacing:.24em;'
            f'text-transform:uppercase;color:{kleur}">{t}</p>')


def woord(t, kleur=NAVY, plek='boven'):
    """Eén woord in de display-letter, in een hoek waar de foto rustig is."""
    pos = {'boven': 'left:68px;top:70px', 'onder': 'right:68px;bottom:70px',
           'linksonder': 'left:68px;bottom:70px'}[plek]
    return (f'<p style="position:absolute;{pos};font:400 86px/1 \'Tide Tode Display\';'
            f'text-transform:uppercase;letter-spacing:.02em;color:{kleur}">{t}</p>')


def hand(t, kleur=NAVY):
    """Handschrift. Komt maar één keer voor in de hele set."""
    return (f'<p style="position:absolute;left:80px;top:120px;font:400 74px/1.2 \'Homemade Apple\';'
            f'color:{kleur};rotate:-4deg">{t}</p>')


# foto's: bron, plus optioneel (y, zoom) voor de uitsnede.
# y = waar de 4:5 uitsnede verticaal ligt (0 boven, 0.5 midden, 1 onder); zoom > 1 snijdt dichterbij in.
def pb(naam):
    return PB / f'{naam}.jpg'


def fa(naam):
    return ASSETS / f'{naam}.jpg'


POSTS = [
    ('post-01-ons-verhaal', [
        (fa('tt-foto-slot'), 0.5, 1, label('Zo begon het', plek='rechtsonder')),
        (fa('tt-foto-probleem-2'), 0.55, 1, ''),
        (fa('tt-foto-hero'), 0.7, 1, hand('Veerle')),
    ]),
    ('post-02-draagtas-tegel', [
        (pb('draagtas-tegel-1'), 0.5, 1, label('Draagtas Tegel', plek='rechtsonder')),
        (pb('draagtas-tegel-3'), 0.5, 1, ''),
        (pb('draagtas-tegel-4'), 0.5, 1, ''),
        (pb('draagtas-tegel-2'), 0.5, 1, ''),
    ]),
    ('post-03-t-shirts', [
        (pb('t-shirt-golf-2'), 0.5, 1, label('T-shirts')),
        (pb('t-shirt-board-2'), 0.5, 1, ''),
        (pb('t-shirt-klassiek-2'), 0.5, 1, ''),
        (pb('t-shirt-zon-2'), 0.5, 1, ''),
        (pb('t-shirt-lijn-naar-zee-2'), 0.5, 1, ''),
        (pb('t-shirt-op-weg-naar-zee-2'), 0.5, 1, ''),
    ]),
    ('post-04-accessoires', [
        (pb('pet-navy-1'), 0.5, 1, ''),
        (pb('bucket-hat-tegel-1'), 0.5, 1, ''),
        (pb('karabijnhaak-messing-1'), 0.5, 1, ''),
        (pb('strandhanddoek-tegel-1'), 0.5, 1, ''),
        (pb('canvas-tas-1'), 0.5, 1, ''),
        (pb('stickerset-2'), 0.5, 1, ''),
    ]),
    ('post-05-alle-draagtassen', [
        (pb('draagtas-salie-2'), 0.5, 1, label('Negen stoffen', plek='rechtsonder')),
        (pb('draagtas-ruit-2'), 0.5, 1, ''),
        (pb('draagtas-tegel-navy-2'), 0.5, 1, ''),
        (pb('draagtas-schelp-2'), 0.5, 1, ''),
        (pb('draagtas-duin-2'), 0.5, 1, ''),
        (pb('draagtas-navy-2'), 0.5, 1, ''),
    ]),
    ('post-06-surfwax', [
        (pb('surfwax-koud-1'), 0.5, 1, label('Koud')),
        (pb('surfwax-koud-3'), 0.5, 1, ''),
        (pb('surfwax-koel-1'), 0.5, 1, label('Koel')),
        (pb('surfwax-warm-1'), 0.5, 1, label('Warm')),
        (pb('waxkam-1'), 0.5, 1, ''),
    ]),
    ('post-07-zo-werkt-het', [
        (pb('draagtas-golfjes-1'), 0.5, 1, woord('Omdoen', plek='onder')),
        (pb('draagtas-golfjes-3'), 0.5, 1, woord('Aantrekken', plek='onder')),
        (fa('tt-foto-stap-1'), 0.35, 1, woord('Dragen', CREME, 'linksonder')),
        (fa('tt-foto-mood-1'), 0.5, 1, woord('Lopen')),
    ]),
    ('post-08-najaar', [
        (pb('uv-shirt-lange-mouw-1'), 0.5, 1, label('Najaar')),
        (pb('hoodie-twee-boards-2'), 0.5, 1, ''),
        (pb('sweater-boards-2'), 0.5, 1, ''),
        (pb('longsleeve-vin-2'), 0.5, 1, ''),
        (pb('longsleeve-zon-2'), 0.5, 1, ''),
        (pb('surfponcho-tegel-2'), 0.5, 1, ''),
    ]),
    ('post-09-draagtas-zonsondergang', [
        (pb('draagtas-zonsondergang-2'), 0.5, 1, label('Zonsondergang', plek='rechtsonder')),
        (pb('draagtas-zonsondergang-1'), 0.5, 1, ''),
        (pb('draagtas-zonsondergang-3'), 0.5, 1, ''),
        (pb('draagtas-zonsondergang-4'), 0.5, 1, ''),
    ]),
]


def staand(bron, y=0.5, zoom=1.0):
    """Snijdt een foto bij tot 4:5 en schaalt naar 1080x1350."""
    im = Image.open(bron).convert('RGB')
    w, h = im.size
    if w / h > B / H:
        cw, ch = h * B / H, h
    else:
        cw, ch = w, w * H / B
    cw, ch = cw / zoom, ch / zoom
    x0 = (w - cw) / 2
    y0 = (h - ch) * y
    return im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((B, H), Image.LANCZOS)


RENDER = r'''
import { chromium } from '../preview/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const map = new URL('./uit3/', 'file://' + process.cwd() + '/').pathname;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
for (const f of fs.readdirSync(map).filter((f) => f.endsWith('.html')).sort()) {
  await p.goto('file://' + map + f);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(100);
  await p.screenshot({ path: map + f.replace('.html', '.png') });
}
await b.close();
'''


def main():
    shutil.rmtree(UIT, ignore_errors=True)
    UIT.mkdir()
    # oude posts weg (vierkante jpg's en eerdere carrouselmappen)
    for f in DOEL.glob('post-*'):
        shutil.rmtree(f) if f.is_dir() else f.unlink()

    for post, slides in POSTS:
        (DOEL / post).mkdir()
        for i, (bron, y, zoom, tekst) in enumerate(slides, 1):
            foto = staand(bron, y, zoom)
            if not tekst:
                foto.save(DOEL / post / f'slide-{i}.jpg', quality=90, optimize=True)
                continue
            achter = UIT / f'{post}--{i}.jpg'
            foto.save(achter, quality=95)
            (UIT / f'{post}--{i}.html').write_text(f'''<!doctype html><meta charset="utf-8"><style>{FONTS}
* {{ margin: 0; padding: 0; }}
html, body {{ width: {B}px; height: {H}px; overflow: hidden; }}
body {{ background: url('file://{achter}') center / cover; position: relative; }}
</style><body>{tekst}</body>''')

    subprocess.run(['node', '--input-type=module', '-e', RENDER], cwd=HIER, check=True)
    for png in UIT.glob('*.png'):
        post, i = png.stem.split('--')
        Image.open(png).convert('RGB').save(DOEL / post / f'slide-{i}.jpg', quality=90, optimize=True)
    shutil.rmtree(UIT)

    # raster: eerste slides, drie kolommen. Instagram toont het profielraster ook staand (4:5)
    eerste = [DOEL / post / 'slide-1.jpg' for post, _ in POSTS]
    tw, th, gat = 360, 450, 4
    rijen = (len(eerste) + 2) // 3
    raster = Image.new('RGB', (3 * tw + 2 * gat, rijen * th + (rijen - 1) * gat), 'white')
    for i, p in enumerate(eerste):
        raster.paste(Image.open(p).resize((tw, th), Image.LANCZOS), ((i % 3) * (tw + gat), (i // 3) * (th + gat)))
    raster.save(DOEL / 'raster-voorbeeld.jpg', quality=85)
    print(f'klaar: {len(POSTS)} carrousels, {sum(len(s) for _, s in POSTS)} slides')


if __name__ == '__main__':
    main()
