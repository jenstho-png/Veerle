"""Instagram feed 2: negen posts die eruitzien als de webshop.

Zelfde letters (Tide Tode Display en Courier Prime), zelfde kleuren, de stickers uit het thema, de stofrondjes
uit de ontwerpkiezer en de eigen studiofoto's. Geen stockfoto's.
Elke post is een ander soort: hero, ontwerpkiezer, stickers, zo werkt hij, productdetail, logo met patroon,
kleding, tekst en wax. Twee vlakken met dezelfde kleur staan nooit naast of onder elkaar.

Uit: docs/social/feed-2/post-01-.../slide-1.jpg enzovoort, plus raster.jpg.
Gebruik: python3 tools/social/feed2.py
"""
import json
import pathlib
import re
import shutil
import subprocess

from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
A = ROOT / 'theme' / 'assets'
PB = ROOT / 'docs' / 'producten' / 'beelden'
DOEL = ROOT / 'docs' / 'social' / 'feed-2'
WERK = HIER / 'uit-feed2'
B, H = 1080, 1350

NAVY, CREME, PAPIER, BABY, ROSE, ZAND, BLAUW, TERRA = '#22324F', '#F3ECDD', '#FBF7EF', '#BFD3EA', '#EDBDB8', '#E3CFAE', '#4A6B97', '#C0603E'
L = json.load(open(ROOT / 'tools' / 'brand2' / 'logo2.json'))

# stickers uit het thema
_stk = (ROOT / 'theme' / 'snippets' / 'tt-stk.liquid').read_text()
STK = {}
for m in re.finditer(r"\{%- when '([a-z]+)' -%\}\n(.*?)(?=\n\s*\{%- (?:when|endcase))", _stk, re.S):
    STK[m.group(1)] = m.group(2).strip().replace('{{ class }}', '')


def u(p):
    return 'file://' + str(p)


def logo(soort, kleur, stijl=''):
    g = L[soort]
    return f'<svg viewBox="0 0 {g["w"]} {g["h"]}" style="display:block;fill:{kleur};{stijl}"><path fill-rule="evenodd" d="{g["d"]}"/></svg>'


def sticker(naam, stijl):
    svg = STK[naam].replace('<svg ', '<svg style="width:100%;height:auto;display:block" ', 1)
    return f'<div style="position:absolute;{stijl};filter:drop-shadow(0 14px 18px rgba(10,20,35,.28))">{svg}</div>'


def rondje(naam, d=230):
    return (f'<div style="width:{d}px;height:{d}px;border-radius:50%;background:url({u(PB / f"draagtas-{naam}-1.jpg")}) 30% 42%/260%;'
            f'box-shadow:0 0 0 2px rgba(34,50,79,.12),0 18px 30px -18px rgba(10,20,35,.45)"></div>')


def kop(tekst, kleur=NAVY, maat=150, accent=BLAUW):
    t = re.sub(r'\*(.+?)\*', rf'<em style="font-style:normal;color:{accent}">\1</em>', tekst).replace('|', '<br>')
    return f'<h1 style="margin:0;font:400 {maat}px/.9 \'Tide Tode Display\';text-transform:uppercase;letter-spacing:.01em;color:{kleur}">{t}</h1>'


def klein(tekst, kleur=NAVY):
    return f'<p style="margin:0;font:700 22px/1 \'Courier Prime\';letter-spacing:.24em;text-transform:uppercase;color:{kleur}">{tekst}</p>'


def foto(pad, pos='50% 50%', maat='cover'):
    return f'background:url({u(pad)}) {pos}/{maat} no-repeat'


def nummer(n, kleur=CREME, achter=NAVY):
    return (f'<div style="width:96px;height:96px;border-radius:50%;background:{achter};color:{kleur};display:grid;place-items:center;'
            f'font:400 54px/1 \'Tide Tode Display\'">{n}</div>')


KORREL = ('<svg style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none" xmlns="http://www.w3.org/2000/svg">'
          '<filter id="korrel"><feTurbulence baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
          '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0"/></filter><rect width="100%" height="100%" filter="url(#korrel)"/></svg>')


def vlak(kleur, inhoud, extra=''):
    return f'<div style="position:absolute;inset:0;background:{kleur};{extra}">{KORREL}{inhoud}</div>'


# ---------- de negen posts ----------
ONTWERPEN = ['tegel', 'golfjes', 'zonsondergang', 'schelp', 'salie', 'duin']

POSTS = []

# 01 hero: de drie boards op het zand, met het logo, zoals de homepage
POSTS.append(('post-01-handen-vrij', [
    f'<div style="position:absolute;inset:0;{foto(A / "tt-foto-hero-home.jpg", "22% 50%")}"></div>'
    f'<div style="position:absolute;left:70px;top:110px;width:420px">{logo("gestapeld", NAVY, "width:100%")}</div>'
    f'<p style="position:absolute;left:84px;top:470px;margin:0;font:400 40px/1 \'Homemade Apple\';color:{NAVY};rotate:-4deg">Handen vrij,<br>op weg naar zee</p>',
    f'<div style="position:absolute;inset:0;{foto(A / "tt-foto-stap-3.jpg")}"></div>',
    f'<div style="position:absolute;inset:0;{foto(A / "tt-foto-avontuur.jpg")}"></div>',
]))

# 02 ontwerpkiezer: zes stofrondjes, zoals op de site
rij = ''.join(f'<div style="display:grid;justify-items:center;gap:22px">{rondje(n)}<span style="font:700 22px \'Courier Prime\';letter-spacing:.2em;text-transform:uppercase;color:{NAVY}">{n}</span></div>' for n in ONTWERPEN)
POSTS.append(('post-02-kies-je-ontwerp', [
    vlak(CREME, f'<div style="position:absolute;left:80px;top:110px">{klein("De draagtas")}<div style="height:26px"></div>{kop("Kies je|*ontwerp*", maat=136)}</div>'
                f'<div style="position:absolute;left:80px;right:80px;bottom:110px;display:grid;grid-template-columns:repeat(3,1fr);gap:46px 20px">{rij}</div>'),
] + [f'<div style="position:absolute;inset:0;{foto(PB / f"draagtas-{n}-2.jpg")}"></div>' for n in ONTWERPEN]))

# 03 stickers op rose
POSTS.append(('post-03-stickers', [
    vlak(ROSE, sticker('zon', 'left:90px;top:120px;width:250px;rotate:-10deg') + sticker('golf', 'left:520px;top:150px;width:470px;rotate:5deg')
         + sticker('draagtas', 'left:150px;top:470px;width:560px;rotate:-6deg') + sticker('schelp', 'left:720px;top:520px;width:250px;rotate:12deg')
         + sticker('zeester', 'left:100px;top:880px;width:230px;rotate:-14deg') + sticker('palm', 'left:430px;top:860px;width:210px;rotate:6deg')
         + sticker('board', 'left:760px;top:860px;width:200px;rotate:-8deg')
         + f'<div style="position:absolute;left:0;right:0;bottom:70px;display:grid;justify-items:center">{klein("Stickerset, zeven stuks")}</div>'),
    f'<div style="position:absolute;inset:0;{foto(PB / "stickerset-2.jpg")}"></div>',
    f'<div style="position:absolute;inset:0;{foto(PB / "stickerset-1.jpg")}"></div>',
]))

# 04 zo werkt hij, drie stappen
stappen = [('1', 'Board erin', A / 'tt-foto-stap-1.jpg'), ('2', 'Band aantrekken', A / 'tt-foto-stap-2.jpg'), ('3', 'Op naar zee', A / 'tt-foto-stap-3.jpg')]
kolom = ''.join(f'<div style="position:relative;border-radius:18px;overflow:hidden;{foto(p)}"><div style="position:absolute;left:18px;top:18px">{nummer(n)}</div></div>' for n, _, p in stappen)
POSTS.append(('post-04-zo-werkt-hij', [
    vlak(BABY, f'<div style="position:absolute;left:80px;top:100px">{kop("Zo werkt|*hij*", maat=130, accent=CREME)}</div>'
               f'<div style="position:absolute;left:80px;right:80px;top:460px;bottom:90px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px">{kolom}</div>'),
] + [f'<div style="position:absolute;inset:0;{foto(p)}"></div><div style="position:absolute;left:70px;bottom:80px;display:flex;align-items:center;gap:26px">{nummer(n)}'
     f'<span style="font:400 76px/1 \'Tide Tode Display\';text-transform:uppercase;color:{CREME};text-shadow:0 2px 24px rgba(10,20,35,.45)">{t}</span></div>' for n, t, p in stappen]))

# 05 productdetail met een ronde sticker zoals op de site
badge = (f'<div style="position:absolute;right:70px;top:70px;width:230px;height:230px;border-radius:50%;background:{CREME};rotate:9deg;display:grid;place-items:center;text-align:center;'
         f'box-shadow:0 18px 30px -16px rgba(10,20,35,.5)"><div>{logo("board", NAVY, "width:34px;margin:0 auto 12px")}'
         f'<p style="margin:0;font:700 24px/1.25 \'Courier Prime\';letter-spacing:.16em;text-transform:uppercase;color:{NAVY}">Handen<br>vrij</p></div></div>')
POSTS.append(('post-05-zonsondergang', [
    f'<div style="position:absolute;inset:0;{foto(PB / "draagtas-zonsondergang-2.jpg")}"></div>{badge}',
    f'<div style="position:absolute;inset:0;{foto(PB / "draagtas-zonsondergang-1.jpg")}"></div>',
    f'<div style="position:absolute;inset:0;{foto(PB / "draagtas-zonsondergang-3.jpg")}"></div>',
]))

# 06 navy met het stickerpatroon en het logo, zoals de afsluiter van de site
patroon = ''.join(sticker(n, s) for n, s in [('zon', 'left:70px;top:90px;width:190px;rotate:-10deg'), ('palm', 'right:90px;top:80px;width:150px;rotate:8deg'),
                                             ('golf', 'left:60px;bottom:110px;width:300px;rotate:5deg'), ('schelp', 'right:100px;bottom:140px;width:170px;rotate:-12deg'),
                                             ('zeester', 'right:60px;top:560px;width:130px;rotate:14deg'), ('draagtas', 'left:40px;top:300px;width:240px;rotate:-6deg')])
POSTS.append(('post-06-tide-tode', [
    vlak(NAVY, patroon + f'<div style="position:absolute;left:50%;top:50%;translate:-50% -50%;width:470px">{logo("gestapeld", CREME, "width:100%")}</div>'),
    vlak(CREME, f'<div style="position:absolute;left:50%;top:50%;translate:-50% -50%;width:150px">{logo("board", NAVY, "width:100%")}</div>'),
]))

# 07 kleding: vier shirts in een raster
shirts = ['t-shirt-golf-2', 'hoodie-twee-boards-2', 'longsleeve-zon-2', 't-shirt-board-2']
raster = ''.join(f'<div style="{foto(PB / f"{s}.jpg")};border-radius:6px"></div>' for s in shirts)
POSTS.append(('post-07-kleding', [
    vlak(PAPIER, f'<div style="position:absolute;inset:40px 40px 120px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:16px">{raster}</div>'
                 f'<div style="position:absolute;left:0;right:0;bottom:46px;display:grid;justify-items:center">{klein("Biologisch katoen")}</div>'),
] + [f'<div style="position:absolute;inset:0;{foto(PB / f"{s}.jpg")}"></div>' for s in shirts]))

# 08 tekst, op rose
POSTS.append(('post-08-we-maken-weinig', [
    vlak(ROSE, f'<div style="position:absolute;left:80px;right:80px;top:50%;translate:0 -50%">{kop("We maken|weinig,|en dat|*goed.*", maat=150, accent=CREME)}</div>'
               f'<div style="position:absolute;left:80px;bottom:90px">{klein("Gaat er iets stuk? Wij repareren het")}</div>'),
    f'<div style="position:absolute;inset:0;{foto(PB / "draagtas-tegel-2.jpg")}"></div>',
]))

# 09 wax, drie temperaturen
wax = [('surfwax-koud-1', 'Koud', 'Onder 14°'), ('surfwax-koel-1', 'Koel', '14 tot 19°'), ('surfwax-warm-1', 'Warm', 'Boven 19°')]
blokken = ''.join(f'<div style="display:grid;grid-template-rows:1fr auto;gap:16px"><div style="{foto(PB / f"{w}.jpg")};border-radius:14px"></div>'
                  f'<div style="text-align:center"><p style="margin:0;font:400 46px/1 \'Tide Tode Display\';text-transform:uppercase;color:{NAVY}">{t}</p>'
                  f'<p style="margin:8px 0 0;font:700 19px \'Courier Prime\';letter-spacing:.16em;color:{NAVY}">{g}</p></div></div>' for w, t, g in wax)
POSTS.append(('post-09-surfwax', [
    vlak(BABY, f'<div style="position:absolute;left:80px;top:100px">{kop("Welke wax|*vandaag?*", maat=120, accent=CREME)}</div>'
               f'<div style="position:absolute;left:60px;right:60px;top:440px;bottom:80px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px">{blokken}</div>'),
] + [f'<div style="position:absolute;inset:0;{foto(PB / f"{w}.jpg")}"></div>' for w, _, _ in wax]))

FONTS = ''.join(f"@font-face{{font-family:'{f}';src:url('{u(A / b)}') format('woff2');font-weight:{w}}}"
                for f, b, w in [('Courier Prime', 'courierprime-bold.woff2', 700), ('Courier Prime', 'courierprime-regular.woff2', 400),
                                ('Tide Tode Display', 'tide-tode-display.woff2', 400), ('Homemade Apple', 'homemadeapple-regular.woff2', 400)])

RENDER = r'''
import { chromium } from '../preview/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const map = process.argv[1];
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
for (const f of fs.readdirSync(map).filter((f) => f.endsWith('.html')).sort()) {
  await p.goto('file://' + map + '/' + f, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(150);
  await p.screenshot({ path: map + '/' + f.replace('.html', '.png') });
}
await b.close();
'''


def main():
    shutil.rmtree(WERK, ignore_errors=True); WERK.mkdir()
    shutil.rmtree(DOEL, ignore_errors=True); DOEL.mkdir(parents=True)
    for post, slides in POSTS:
        for i, inhoud in enumerate(slides, 1):
            (WERK / f'{post}--{i}.html').write_text(f'<!doctype html><meta charset="utf-8"><style>{FONTS}*{{box-sizing:border-box}}html,body{{margin:0;width:{B}px;height:{H}px;overflow:hidden;background:{PAPIER}}}</style><body><div style="position:relative;width:{B}px;height:{H}px;overflow:hidden">{inhoud}</div></body>')
    subprocess.run(['node', '--input-type=module', '-e', RENDER, str(WERK)], cwd=HIER, check=True)
    for png in sorted(WERK.glob('*.png')):
        post, i = png.stem.split('--')
        (DOEL / post).mkdir(exist_ok=True)
        Image.open(png).convert('RGB').save(DOEL / post / f'slide-{i}.jpg', quality=90, optimize=True)
    shutil.rmtree(WERK)
    eerste = [DOEL / post / 'slide-1.jpg' for post, _ in POSTS]
    tw, th, gat = 360, 450, 4
    raster = Image.new('RGB', (3 * tw + 2 * gat, 3 * th + 2 * gat), 'white')
    for i, p in enumerate(eerste):
        raster.paste(Image.open(p).resize((tw, th), Image.LANCZOS), ((i % 3) * (tw + gat), (i // 3) * (th + gat)))
    raster.save(DOEL / 'raster.jpg', quality=86)
    print(f'klaar: {len(POSTS)} posts, {sum(len(s) for _, s in POSTS)} slides')


if __name__ == '__main__':
    main()
