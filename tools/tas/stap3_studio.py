"""Stap 3 van 'Zo werkt hij' (op naar de spot): boards met de draagtas op het zand, een spoor van voetstappen
ernaast en wat zand op de tas. Zelfde studiostijl als de productfoto's (studio2 / hero_studio).
Schrijft theme/assets/tt-foto-stap-3(.jpg/-800.jpg)."""
import pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER)); sys.path.insert(0, str(HIER.parent / 'producten'))
import studio2 as S2  # noqa: E402
import stijl as ST  # noqa: E402
import hero_studio as HS  # noqa: E402

THEMA = HIER.parent.parent / 'theme' / 'assets'
B, H = 1500, 1875
LICHT = np.array([-0.62, -0.78], np.float32)            # naar het raam (linksboven)


def voet(links, lengte=200):
    """Hoogtekaart van één voetafdruk (0..1, 1 = diepst), hiel onder, tenen boven."""
    w, h = int(lengte * 0.55), int(lengte * 1.25)
    m = np.zeros((h, w), np.float32)
    cx = w / 2
    cv2.ellipse(m, (int(cx), int(h * 0.70)), (int(lengte * 0.17), int(lengte * 0.20)), 0, 0, 360, 1, -1, cv2.LINE_AA)   # hiel
    cv2.ellipse(m, (int(cx + (6 if links else -6)), int(h * 0.42)), (int(lengte * 0.20), int(lengte * 0.26)), 0, 0, 360, 0.85, -1, cv2.LINE_AA)  # bal
    tenen = [(-0.13, 0.13, 0.07), (-0.03, 0.10, 0.055), (0.05, 0.10, 0.05), (0.12, 0.12, 0.045), (0.18, 0.15, 0.04)]
    for dx, dy, r in tenen:
        x = cx + (dx if links else -dx) * lengte
        cv2.circle(m, (int(x), int(h * dy + lengte * 0.06)), int(r * lengte), 0.55, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), lengte * 0.045)
    # los droog zand: de rand is rafelig en de afdruk is niet overal even diep
    rng = np.random.default_rng(int(lengte * 7 + links))
    ruis = cv2.GaussianBlur(rng.normal(0, 1, m.shape).astype(np.float32), (0, 0), lengte * 0.03)
    m = np.clip(m * (0.75 + 0.35 * ruis / (np.abs(ruis).max() + 1e-6)), 0, 1)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = cv2.GaussianBlur(rng.normal(0, 1, m.shape).astype(np.float32), (0, 0), 6) * 40
    dy = cv2.GaussianBlur(rng.normal(0, 1, m.shape).astype(np.float32), (0, 0), 6) * 40
    m = cv2.remap(m, xs + dx, ys + dy, cv2.INTER_LINEAR)
    # opgeworpen zand rond de rand
    rand = cv2.GaussianBlur(cv2.dilate((m > 0.2).astype(np.float32), np.ones((9, 9), np.uint8)), (0, 0), lengte * 0.05)
    return m, rand


def stempel(veld, rand_veld, m, r, cx, cy, hoek, schaal=1.0):
    h, w = m.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), hoek, schaal)
    M[0, 2] += cx - w / 2; M[1, 2] += cy - h / 2
    veld[:] = np.maximum(veld, cv2.warpAffine(m, M, (B, H)))
    rand_veld[:] = np.maximum(rand_veld, cv2.warpAffine(r, M, (B, H)))


def voetstappen(doek):
    diep = np.zeros((H, B), np.float32); rand = np.zeros((H, B), np.float32)
    rng = np.random.default_rng(3)
    y = H + 120
    links = True
    while y > -200:
        x = 190 + (-46 if links else 46) + rng.normal(0, 10)
        m, r = voet(links, 190)
        stempel(diep, rand, m, r, x, y, (4 if links else -4) + rng.normal(0, 3))
        y -= 470 + rng.normal(0, 25)
        links = not links
    hoogte = 0.45 * rand * (1 - diep) - 0.7 * diep
    hoogte = cv2.GaussianBlur(hoogte, (0, 0), 3.5)
    gy, gx = np.gradient(hoogte)
    licht = (gx * LICHT[0] + gy * LICHT[1]) * 15                        # helling naar het raam is licht
    tint = 1 + np.clip(licht, -0.32, 0.22) - 0.05 * diep                 # binnenin net wat donkerder (vochtiger zand)
    # binnenin de afdruk: korrel van omgewoeld zand
    korrel = cv2.GaussianBlur(rng.normal(0, 1, (H, B)).astype(np.float32), (0, 0), 1.2) * 0.05 * diep
    return np.clip(doek * (tint + korrel)[..., None], 0, 1)


def zand_op(doek, masker, dichtheid, zaad=8):
    """Losse zandkorrels en kleine plukjes op de tas en het board, met een klein schaduwtje (licht linksboven)."""
    rng = np.random.default_rng(zaad)
    kans = rng.random((H, B)).astype(np.float32) < dichtheid * masker
    plukjes = cv2.GaussianBlur((rng.random((H, B)) < 0.00012 * masker).astype(np.float32), (0, 0), 6)
    plukjes = np.clip(plukjes * 60, 0, 1) * (rng.random((H, B)) < 0.35)
    k = np.clip(cv2.GaussianBlur(kans.astype(np.float32), (0, 0), 0.7) * 2.4 + plukjes, 0, 1)
    sch = cv2.GaussianBlur(cv2.warpAffine(k, np.float32([[1, 0, 1.5], [0, 1, 2]]), (B, H)), (0, 0), 1.0)
    kleur = np.array([0.86, 0.78, 0.62], np.float32) * (0.85 + 0.3 * rng.random((H, B, 1)).astype(np.float32))
    doek = doek * (1 - 0.35 * sch[..., None] * (1 - k[..., None]))
    return doek * (1 - k[..., None]) + kleur * k[..., None]


if __name__ == '__main__':
    ST.B, ST.H = B, H
    _l = ST._licht; ST._licht = lambda h=H, b=B: _l(h, b)
    doek = voetstappen(S2.zand_detail(1.0, zaad=9))
    zandmask = np.zeros((H, B), np.float32)
    k = 1.0
    for handle, cx in (('draagtas-tegel', 760), ('draagtas-golfjes', 1260)):
        rb, rl, bx = HS.staand_los(handle, 1600)
        h, w = rb.shape[:2]
        midden = (cx - bx + w / 2, H / 2 + 30)
        a_b = S2.alfa_op_doek(rb, 1.0, midden, doek)
        doek = S2.slagschaduw(doek, a_b, [(3 * k, 3 * k, 0.5), (14 * k, 12 * k, 0.32), (40 * k, 34 * k, 0.26)])
        doek = ST.leg(doek, rb, breedte=w, midden=midden, hoogte=20 * k, zachtheid=0.9, contact=0.7)
        a_l = S2.alfa_op_doek(rl, 1.0, midden, doek)
        doek = S2.slagschaduw(doek, a_l, [(2 * k, 1.6 * k, 0.6), (7 * k, 6 * k, 0.3)])
        doek = ST.leg(doek, rl, breedte=w, midden=midden, hoogte=3 * k, contact=0.6)
        # zand vooral op de tas (het midden van het board) en wat op de rest
        yy = np.arange(H, dtype=np.float32)[:, None]
        rond_tas = np.exp(-((yy - midden[1]) / 330) ** 2)
        zandmask = np.maximum(zandmask, a_b * (0.06 + 0.94 * rond_tas ** 2))
    doek = zand_op(doek, zandmask, 0.004)
    img = ST.afwerking(doek, korrel=0.005, zaad=12)
    u8 = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    u8.resize((1200, 1500), Image.LANCZOS).save(THEMA / 'tt-foto-stap-3.jpg', quality=84, optimize=True, progressive=True)
    u8.resize((800, 1000), Image.LANCZOS).save(THEMA / 'tt-foto-stap-3-800.jpg', quality=82, optimize=True, progressive=True)
    print('klaar')
