"""Controle van de gemeten boardrand: per kant een rechtgetrokken strook langs de rand (rond het balanspunt),
vergroot, met de gemeten rand als rode stippellijn in het midden.
python3 tools/tas/sfeer_randcheck.py board-xxx.jpg uit.jpg [half_lengte_factor] [breedte_px]"""
import pathlib, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw

HIER = pathlib.Path(__file__).parent
STOCK = HIER.parent.parent / 'docs' / 'producten' / 'stock' / 'lifestyle'


def strook(naam, uit, f=0.9, bp=30, beeld=None):
    img = np.asarray(Image.open(beeld or (STOCK / naam)).convert('RGB')).astype(np.float32)
    g = np.load(STOCK / 'maskers' / (pathlib.Path(naam).stem + '.npz'))
    c, a, tt, lo, hi, tb = g['c'], g['a'], g['tt'], g['lo'], g['hi'], float(g['t_balans'])
    n = np.array([-a[1], a[0]])
    i = np.argmin(np.abs(tt - tb)); W = hi[i] - lo[i]
    ts = np.arange(tb - f * W, tb + f * W, 0.5)
    ds = np.arange(-bp, bp, 0.25)
    delen = []
    for rand, kant in ((lo, -1), (hi, 1)):
        e = np.interp(ts, tt, rand)
        T, D = np.meshgrid(ts, ds, indexing='ij')
        S = e[:, None] + kant * D
        X = c[0] + a[0] * T + n[0] * S; Y = c[1] + a[1] * T + n[1] * S
        st = cv2.remap(img, X.astype(np.float32), Y.astype(np.float32), cv2.INTER_LINEAR)
        st = Image.fromarray(np.clip(st, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(st)
        mid = int(bp / 0.25)
        for y in range(0, st.height, 6):
            d.line([(mid, y), (mid, y + 2)], fill=(255, 0, 0))
        for k in range(-bp, bp + 1, 5):
            x = int((k + bp) / 0.25)
            d.line([(x, 0), (x, 4)], fill=(255, 255, 0))
        for k, t in enumerate(ts):
            if abs((t - tb) % 50) < 0.25:
                d.text((2, k), '%+d' % round(t - tb), fill=(255, 255, 0))
        delen.append(st)
    # buitenkant van beide stroken naar buiten: linkerstrook spiegelen zodat 'buiten' links staat
    links = delen[0].transpose(Image.FLIP_LEFT_RIGHT)
    tot = Image.new('RGB', (links.width + delen[1].width + 10, links.height), 'black')
    tot.paste(links, (0, 0)); tot.paste(delen[1], (links.width + 10, 0))
    s = 1400 / tot.height
    tot = tot.resize((int(tot.width * s), 1400), Image.LANCZOS)
    tot.save(uit, quality=88)
    print(naam, 'breedte %.1f' % W)


if __name__ == '__main__':
    a = sys.argv
    strook(a[1], a[2], float(a[3]) if len(a) > 3 else 0.9, int(a[4]) if len(a) > 4 else 30)
