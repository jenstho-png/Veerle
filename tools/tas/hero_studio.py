"""Herofoto van de homepage in dezelfde studiostijl als de productfoto's van de draagtas.

Drie boards met de draagtas (Golfjes, Tegel, Zonsondergang) liggen recht van boven naast elkaar op het zand, rechts in
beeld; links blijft rustig zand voor het logo en de tekst. Zelfde opbouw, licht en zand als studio2.py.
Schrijft theme/assets/tt-foto-hero-home.jpg (2560 x 1440) en -800.jpg.
Gebruik: python3 tools/tas/hero_studio.py
"""
import pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent / 'producten'))
import studio2 as S2  # noqa: E402
import stijl as ST  # noqa: E402

THEMA = HIER.parent.parent / 'theme' / 'assets'
B, H = 2560, 1440
BOARDS = [('draagtas-golfjes', 1290), ('draagtas-tegel', 1780), ('draagtas-zonsondergang', 2270)]


def staand_los(handle, hoogte):
    rb, rl = S2.bouw(handle)
    rb, rl = S2.staand(rb), S2.staand(rl)
    ys, xs = np.where(np.maximum(rb[..., 3], rl[..., 3]) > 0.01)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rb, rl = rb[y0:y1, x0:x1], rl[y0:y1, x0:x1]
    ys2 = np.where(rb[..., 3].max(1) > 0.01)[0]
    s = hoogte / (ys2.max() - ys2.min())                 # de lengte van het board bepaalt de schaal
    def schaal(r):
        pm = np.dstack([r[..., :3] * r[..., 3:4], r[..., 3]])
        pm = cv2.resize(pm, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        a = np.clip(pm[..., 3], 0, 1)
        return np.dstack([np.clip(pm[..., :3] / np.maximum(a[..., None], 1e-4), 0, 1), a]).astype(np.float32)
    rb, rl = schaal(rb), schaal(rl)
    # midden van het board (niet van de lus) in de laag
    xs3 = np.where(rb[..., 3].max(0) > 0.5)[0]
    return rb, rl, (xs3.min() + xs3.max()) / 2


if __name__ == '__main__':
    ST.B, ST.H = B, H
    _licht = ST._licht
    ST._licht = lambda h=H, b=B: _licht(h, b)
    doek = S2.zand_detail(1.0, zaad=4)
    k = 1.0
    # eerst de boards, dan pas de lussen: de handvatten liggen over het board ernaast, zodat je ze goed ziet
    lagen = []
    for handle, cx in BOARDS:
        rb, rl, bx = staand_los(handle, 1160)
        h, w = rb.shape[:2]
        midden = (cx - bx + w / 2, H / 2 + 10)
        lagen.append((rb, rl, w, midden))
        a_b = S2.alfa_op_doek(rb, 1.0, midden, doek)
        doek = S2.slagschaduw(doek, a_b, [(3 * k, 3 * k, 0.5), (14 * k, 12 * k, 0.32), (40 * k, 34 * k, 0.26)])
        doek = ST.leg(doek, rb, breedte=w, midden=midden, hoogte=20 * k, zachtheid=0.9, contact=0.7)
        print('gelegd', handle)
    for rb, rl, w, midden in lagen:
        a_l = S2.alfa_op_doek(rl, 1.0, midden, doek)
        doek = S2.slagschaduw(doek, a_l, [(2.0 * k, 1.6 * k, 0.6), (7 * k, 6 * k, 0.3)])
        doek = ST.leg(doek, rl, breedte=w, midden=midden, hoogte=3 * k, contact=0.6)
    img = ST.afwerking(doek, korrel=0.005, zaad=11)
    u8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(u8).save(THEMA / 'tt-foto-hero-home.jpg', quality=84, optimize=True, progressive=True)
    Image.fromarray(u8).resize((1280, 720), Image.LANCZOS).save(THEMA / 'tt-foto-hero-home-800.jpg', quality=82, optimize=True, progressive=True)
    print('klaar', (THEMA / 'tt-foto-hero-home.jpg').stat().st_size // 1000, 'kB')
