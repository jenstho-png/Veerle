"""Surfwax met verpakking: echte stockfoto's (zie docs/producten/stock/bronnen.json) met onze eigen papieren wikkel.

Verpakking: elk blok wax zit in een papieren wikkel (crème papier, navy druk, een kleurvlak in de kleur van de
watertemperatuur). De wikkel loopt als een brede band om het blok; de uiteinden van de wax blijven zichtbaar.

Stappen:
1. python3 tools/producten/echt_wax.py art     schrijft de html van de wikkels naar tools/producten/uit_wax/
2. node tools/producten/render_wax.mjs          maakt er png's van
3. python3 tools/producten/echt_wax.py          maakt docs/producten/beelden/surfwax-<soort>-1.jpg en -2.jpg

-1: stapel van drie blokken met wikkel op een houten tafel tegen een witte muur (packshot).
-2: één blok rechtop op een tafel met blaadjes, warm licht, met de voorkant van de wikkel (sfeer en detail).
"""
import pathlib, sys
import cv2
import numpy as np

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import mockup as MK  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock'
ART = HIER / 'uit_wax'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
NAVY, CREME, TERRA = '#22324F', '#F3ECDD', '#C0603E'

SOORTEN = {
    'koud': dict(kleur='#C9DAEC', label='KOUD WATER', temp='ONDER 14 GRADEN'),
    'koel': dict(kleur='#E8D6B5', label='KOEL WATER', temp='14 TOT 19 GRADEN'),
    'warm': dict(kleur='#F0C9C4', label='WARM WATER', temp='BOVEN 19 GRADEN'),
}


# ---------- artwork ----------
def art_html():
    import brandbook as BB
    A = ROOT / 'theme' / 'assets'
    fonts = ''.join(f"@font-face{{font-family:'{f}';src:url('file://{A / b}') format('woff2');font-weight:{w}}}"
                    for f, b, w in [('Courier Prime', 'courierprime-bold.woff2', 700), ('Courier Prime', 'courierprime-regular.woff2', 400),
                                    ('Tide Tode Display', 'tide-tode-display.woff2', 400)])
    ART.mkdir(exist_ok=True)

    def pagina(naam, b, h, inhoud):
        (ART / f'{naam}.html').write_text(f'''<!doctype html><meta charset="utf-8"><style>{fonts}
* {{ margin: 0; box-sizing: border-box; }} html, body {{ width: {b}px; height: {h}px; overflow: hidden; background: transparent; }}
.c {{ font-family: 'Courier Prime'; font-weight: 700; text-transform: uppercase; color: {NAVY}; }}
</style><body>{inhoud}</body>''')

    def logo(soort, breedte):
        l = BB.LOGO[soort]
        return f'<svg viewBox="0 0 {l["w"]} {l["h"]}" style="width:{breedte}px;height:auto;display:block"><path fill="{NAVY}" fill-rule="evenodd" d="{l["d"]}"/></svg>'

    for s, d in SOORTEN.items():
        # zijkant van de wikkel (wat je ziet van een blok in de stapel): 1330 x 460
        pagina(f'band-zij-{s}', 1330, 460, f'''
<div style="position:absolute;inset:0;background:{CREME}">
  <div style="position:absolute;left:0;right:0;top:92px;display:flex;justify-content:center">{logo('liggend', 560)}</div>
  <div class="c" style="position:absolute;left:0;right:0;top:200px;text-align:center;font-size:30px;letter-spacing:.42em;padding-left:.42em">SURF WAX</div>
  <div style="position:absolute;left:50%;top:268px;transform:translateX(-50%);background:{d['kleur']};border-radius:40px;padding:16px 40px 14px 50px">
    <div class="c" style="font-size:32px;letter-spacing:.32em;white-space:nowrap">{d['label']}</div></div>
  <div class="c" style="position:absolute;left:60px;top:376px;font-size:22px;letter-spacing:.3em;font-weight:400">70 GRAM</div>
  <div class="c" style="position:absolute;right:60px;top:376px;font-size:22px;letter-spacing:.3em;font-weight:400">{d['temp']}</div>
</div>''')
        # voorkant van de wikkel (grote kant van het blok): 1080 x 1030
        pagina(f'band-voor-{s}', 1080, 1030, f'''
<div style="position:absolute;inset:0;background:{CREME}">
  <div class="c" style="position:absolute;left:0;right:0;top:92px;text-align:center;font-size:30px;letter-spacing:.46em;padding-left:.46em">SURF WAX</div>
  <div style="position:absolute;left:0;right:0;top:170px;display:flex;justify-content:center">{logo('gestapeld', 520)}</div>
  <div style="position:absolute;left:0;right:0;top:640px;height:150px;background:{d['kleur']};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">
    <div class="c" style="font-size:44px;letter-spacing:.34em;padding-left:.34em">{d['label']}</div>
    <div class="c" style="font-size:24px;letter-spacing:.34em;padding-left:.34em;font-weight:400">{d['temp']}</div></div>
  <div class="c" style="position:absolute;left:70px;bottom:92px;font-size:22px;letter-spacing:.28em;font-weight:400">BIJENWAS EN KOKOSOLIE</div>
  <div class="c" style="position:absolute;right:70px;bottom:92px;font-size:22px;letter-spacing:.28em;font-weight:400">70 GRAM</div>
</div>''')
    print('html klaar in', ART)


if __name__ == '__main__' and sys.argv[1:2] == ['art']:
    art_html()
    sys.exit()
