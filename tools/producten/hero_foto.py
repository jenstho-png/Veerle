"""Herofoto van de homepage: een longboard met de draagtas Tegel op het strand.

Bron: docs/producten/fotos/sfeer-geel-board-golfjes.jpg (stockfoto van het strand met een board, de draagtas erop).
- het gele board wordt crème (geen geel naast het blauw van de band), het logo van een ander merk gaat eraf;
- het vak van de tas krijgt de echte tegelstof (docs/producten/fabriek/stof-lap.jpg) met het licht van de foto;
- links wordt de foto verlengd (zee, lucht en zand lopen horizontaal door), zodat het board rechts staat en het logo
  links vrij ruimte heeft.
Schrijft theme/assets/tt-foto-hero-home.jpg en -800.jpg.
Gebruik: python3 tools/producten/hero_foto.py
"""
import pathlib
import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BRON = ROOT / 'docs' / 'producten' / 'fotos' / 'sfeer-geel-board-golfjes.jpg'
STOF = ROOT / 'docs' / 'producten' / 'fabriek' / 'stof-lap.jpg'
A = ROOT / 'theme' / 'assets'
PANEEL = np.float32([[726, 466], [873, 420], [873, 650], [726, 605]])
BANDEN = [np.float32([[726, 476], [872, 455], [872, 469], [726, 493]]),
          np.float32([[726, 582], [872, 601], [872, 620], [726, 602]])]


def board_creme(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    box = np.zeros(H.shape, bool); box[120:960, 680:940] = True
    geel = ((H > 10) & (H < 32) & (S > 200) & box).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(geel)
    kern = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 800]).astype(np.uint8)
    kern = cv2.morphologyEx(kern, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    rand = cv2.dilate(kern, np.ones((7, 7), np.uint8)) & ((H > 8) & (H < 36) & (S > 70)).astype(np.uint8)
    dek = np.where(kern > 0, 1.0, np.clip((S - 70) / 130, 0, 1)) * np.maximum(kern, rand)
    dek = cv2.GaussianBlur(dek.astype(np.float32), (0, 0), 0.6)
    L = V / 255; Lm = np.median(L[kern > 0])
    doel = np.array([226, 238, 236], np.float32) / 255
    nieuw = np.clip(doel[None, None] * (0.88 * L[..., None] / Lm), 0, 1) * 255
    uit = (im * (1 - dek[..., None]) + nieuw * dek[..., None]).astype(np.uint8)
    lm = np.zeros(H.shape, np.uint8); cv2.circle(lm, (800, 419), 16, 1, -1)
    return cv2.inpaint(uit, lm, 6, cv2.INPAINT_TELEA)


def tegel_tas(im):
    h, w = im.shape[:2]
    vak = np.zeros((h, w), np.uint8); cv2.fillPoly(vak, [np.int32(PANEEL)], 1)
    band = np.zeros((h, w), np.uint8)
    for b in BANDEN: cv2.fillPoly(band, [np.int32(b)], 1)
    # het oude vak loopt overal een paar pixels verder dan de getekende hoeken: navy randjes ook meenemen
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    navy = ((hsv[..., 2] < 110) & (hsv[..., 0] > 95) & (hsv[..., 0] < 130)).astype(np.uint8)
    golf = ((hsv[..., 2] > 150) & (hsv[..., 1] < 70)).astype(np.uint8)
    om = cv2.dilate(vak, np.ones((9, 9), np.uint8))
    vak = np.maximum(vak, om & cv2.dilate(navy, np.ones((3, 3), np.uint8)) & cv2.dilate(vak | navy, np.ones((3, 3), np.uint8)))
    m = (vak & (1 - band)).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 0.7)
    # stof: tegels van ca. 36 px, recht op het board, schuin vak volgt de bovenrand
    stof = cv2.imread(str(STOF))
    s = 36 / 196
    stof = cv2.resize(stof, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    vlak = np.zeros_like(im)
    x0, y0 = 725, 420
    ph, pw = stof.shape[:2]
    vlak[y0:y0 + ph, x0:x0 + pw] = stof[:min(ph, h - y0), :min(pw, w - x0)]
    # licht van de foto: helderheid van het oude vak, met het golfpatroon eruit gemiddeld
    L = im.mean(-1).astype(np.float32)
    vm = cv2.erode(vak, np.ones((5, 5), np.uint8)).astype(np.float32)
    laag = cv2.GaussianBlur(L * vm, (0, 0), 18) / np.maximum(cv2.GaussianBlur(vm, (0, 0), 18), 1e-3)
    licht = np.clip(laag / max(float(laag[vm > 0].mean()), 1e-3), 0.85, 1.12)
    tas = vlak.astype(np.float32) * licht[..., None]
    # zelfde waas en zachtheid als de foto
    tas = tas * 0.86 + 255 * 0.06
    tas = cv2.GaussianBlur(tas, (0, 0), 0.6)
    tas += np.random.default_rng(2).normal(0, 3, tas.shape)
    return np.clip(im * (1 - m[..., None]) + tas * m[..., None], 0, 255).astype(np.uint8)


def breder(im):
    """Niet verlengen (dat gaf naden): de foto zelf, iets groter voor scherpe weergave op brede schermen."""
    return cv2.resize(im, (2400, round(2400 * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_CUBIC)


if __name__ == '__main__':
    im = cv2.imread(str(BRON))
    im = tegel_tas(board_creme(im))
    cv2.imwrite('/tmp/hero-zoom.jpg', im[380:700, 650:950])
    b = breder(im)
    cv2.imwrite(str(A / 'tt-foto-hero-home.jpg'), b, [cv2.IMWRITE_JPEG_QUALITY, 84, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])
    cv2.imwrite(str(A / 'tt-foto-hero-home-800.jpg'), cv2.resize(b, (1280, round(1280 * b.shape[0] / 2400)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 82])
    print('klaar')
