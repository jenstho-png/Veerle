"""Artwork voor de echte productfoto's: waxlabels, stickervel en losse stickers (html, render_echt.mjs maakt er png's van)."""
import pathlib, sys

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import brandbook as BB  # noqa: E402

UIT = HIER / 'uit_echt'
UIT.mkdir(exist_ok=True)
A = ROOT / 'theme' / 'assets'
FONTS = ''.join(f"@font-face{{font-family:'{f}';src:url('file://{A / b}') format('woff2');font-weight:{w}}}"
                for f, b, w in [('Courier Prime', 'courierprime-bold.woff2', 700), ('Courier Prime', 'courierprime-regular.woff2', 400),
                                ('Homemade Apple', 'homemadeapple-regular.woff2', 400), ('Tide Tode Display', 'tide-tode-display.woff2', 400)])


def pagina(naam, b, h, inhoud, achter='transparent'):
    (UIT / f'{naam}.html').write_text(f'''<!doctype html><meta charset="utf-8"><style>{FONTS}
* {{ margin: 0; box-sizing: border-box; }} html, body {{ width: {b}px; height: {h}px; overflow: hidden; background: {achter}; }}
</style><body>{inhoud}</body>''')


# waxlabels: crème papier, icoon, merk en watertemperatuur
for soort, temp in [('koud', 'KOUD WATER'), ('koel', 'KOEL WATER'), ('warm', 'WARM WATER')]:
    pagina(f'waxlabel-{soort}', 600, 360, f'''
<div style="position:absolute;inset:10px;background:#F6F0E3;border-radius:18px;display:grid;grid-template-columns:120px 1fr;align-items:center;padding:0 36px;gap:22px;color:#22324F">
  {BB.icoon('#22324F', '', 'width:86px;height:auto')}
  <div><div style="font:400 64px/0.95 'Tide Tode Display';letter-spacing:.03em">TIDE<br>TODE</div>
  <div style="margin-top:14px;font:700 22px 'Courier Prime';letter-spacing:.24em">SURF WAX</div>
  <div style="margin-top:6px;font:700 18px 'Courier Prime';letter-spacing:.2em;color:#C0603E">{temp}</div></div>
  <div style="position:absolute;inset:12px;border:2px dashed rgba(34,50,79,.35);border-radius:12px"></div>
</div>''')

# stickervel zoals in het merkboek
vel = (f'<div style="position:absolute;inset:0;background:#FFFDF8;border-radius:34px;container-type:inline-size">'
       f'<style>.badge{{position:absolute;filter:drop-shadow(0 2px 2px rgba(0,0,0,.18))}}</style>'
       f'<p style="position:absolute;left:0;right:0;top:4cqw;text-align:center;font:700 1.7cqw \'Courier Prime\';letter-spacing:.3em;color:#22324F">TIDE TODE STICKERVEL</p>'
       + BB.zonsondergang_sticker().replace('class="badge"', 'class="badge" style="left:7cqw;top:12cqw;width:30cqw;transform:rotate(-5deg)"')
       + BB.boog_sticker().replace('class="badge"', 'class="badge" style="left:41cqw;top:10cqw;width:25cqw;transform:rotate(4deg)"')
       + BB.tegelcirkel_sticker().replace('class="badge"', 'class="badge" style="left:69cqw;top:13cqw;width:23cqw;transform:rotate(-8deg)"')
       + BB.vaantje_sticker().replace('class="badge"', 'class="badge" style="left:5cqw;top:52cqw;width:48cqw;transform:rotate(-7deg)"')
       + BB.postzegel_sticker().replace('class="badge"', 'class="badge" style="left:62cqw;top:48cqw;width:25cqw;transform:rotate(6deg)"')
       + BB.ruit_sticker().replace('class="badge"', 'class="badge" style="left:9cqw;top:88cqw;width:52cqw;transform:rotate(3deg)"')
       + BB.icsticker('icoonC', 'left:70cqw;top:94cqw;width:17cqw;transform:rotate(-12deg)')
       + '</div>')
pagina('stickervel', 1200, 1560, vel)

# losse stickers om op een board te plakken
for naam, svg in [('zegel', BB.zegel()), ('golfrand', BB.golfrand()), ('pil', BB.pil()), ('tegelcirkel', BB.tegelcirkel_sticker()),
                  ('zonsondergang', BB.zonsondergang_sticker()), ('ovaal', BB.ovaal())]:
    pagina(f'sticker-{naam}', 800, 800, svg.replace('class="badge"', 'class="badge" style="position:absolute;left:4%;top:4%;width:92%;height:92%"'))
# neklabels: rechtstreeks in de nek gedrukt (geen kriebellabel), zoals bij goede basics
for naam, kl in [('neklabel-creme', '#EFE7D6'), ('neklabel-navy', '#22324F')]:
    pagina(naam, 520, 300, f'''
<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:{kl};text-align:center">
  <div style="font:400 86px/0.9 'Tide Tode Display';letter-spacing:.04em">TIDE TODE</div>
  <div style="margin-top:20px;font:700 44px 'Courier Prime'">M</div>
  <div style="margin-top:12px;font:700 21px 'Courier Prime';letter-spacing:.22em">100% KATOEN</div>
  <div style="margin-top:4px;font:700 21px 'Courier Prime';letter-spacing:.22em">WAS OP 30 GRADEN</div>
</div>''')

# klepsticker van de pet (zoals die op elke nieuwe pet zit)
pagina('petsticker', 600, 420, f'''
<div style="position:absolute;inset:6px;background:#F3ECDD;border-radius:44px;color:#22324F;font-family:'Courier Prime'">
  <div style="position:absolute;inset:14px;border:3px solid #22324F;border-radius:34px"></div>
  <div style="position:absolute;left:0;right:0;top:30px;text-align:center;font:700 22px 'Courier Prime';letter-spacing:.3em">SURF CLUB</div>
  <div style="position:absolute;left:62px;right:62px;top:70px;height:118px;background:#22324F;border-radius:16px;display:flex;align-items:center;justify-content:center;gap:18px">
    {BB.icoon('#F3ECDD', '', 'height:86px;width:auto')}
    <span style="font:400 74px/1 'Tide Tode Display';color:#F3ECDD;letter-spacing:.04em">TIDE TODE</span></div>
  <div style="position:absolute;left:0;right:0;top:204px;text-align:center;font:700 40px 'Courier Prime';letter-spacing:.12em">CLASSIC FIT</div>
  <div style="position:absolute;left:0;right:0;top:252px;text-align:center;font:700 24px 'Courier Prime';letter-spacing:.24em">ONE SIZE</div>
  <div style="position:absolute;left:62px;right:62px;top:296px;height:56px;background:#C0603E;border-radius:12px;display:flex;align-items:center;justify-content:center;font:700 28px 'Courier Prime';letter-spacing:.3em;color:#F3ECDD">HANDEN VRIJ</div>
</div>''')
print('artwork klaar')
