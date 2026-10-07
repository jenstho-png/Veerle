"""Eén fotostijl voor alle productfoto's van Tide Tode (zelfde als de draagtassen).

Alles is 'geshoot' in dezelfde studio-opstelling:
- recht van boven (flat lay) of recht van voren, nooit scheef of in een scène met mensen;
- ondergrond: echt zand, of naadloos fotopapier in een merkkleur;
- licht: groot raam linksboven, zachte schaduw naar rechtsonder, lichte val-off naar de hoeken;
- afwerking: dezelfde lichte korrel, vignet en warme kleur.

Gebruik:
    import stijl as ST
    doek = ST.achtergrond('rose')                       # of 'zand', 'baby', 'zandpapier', 'creme', 'navy'
    doek = ST.leg(doek, product_rgba, breedte=1100, midden=(800, 1000), draai=0, hoogte=6)
    ST.bewaar(ST.afwerking(doek), pad)
product_rgba: float32 0..1, HxWx4, vrijstaand (achtergrond weg), recht gefotografeerd.
"""
import pathlib
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
B, H = 1600, 2000
PAPIER = {
    'rose': (0.929, 0.741, 0.722),       # #EDBDB8
    'baby': (0.749, 0.827, 0.918),       # #BFD3EA
    'zandpapier': (0.890, 0.812, 0.682),  # #E3CFAE
    'creme': (0.953, 0.925, 0.867),      # #F3ECDD
    'navy': (0.133, 0.196, 0.310),       # #22324F
}
LICHT = np.array([0.62, 0.78])           # schaduw valt naar rechtsonder (dx, dy)
ZAND = ROOT / 'docs' / 'producten' / 'stock' / 'lifestyle' / 'textuur-zand-1.jpg'


def _ruis(shape, sigma, schaal, zaad):
    r = np.random.default_rng(zaad).normal(0, 1, shape).astype(np.float32)
    r = cv2.GaussianBlur(r, (0, 0), schaal)
    return r / (r.std() + 1e-6) * sigma


def _licht(h=H, b=B):
    """Raamlicht linksboven: lichter daar, zachte val-off naar rechtsonder en de hoeken."""
    yy, xx = np.mgrid[0:h, 0:b].astype(np.float32)
    g = 1.04 - 0.10 * ((xx / b) * 0.45 + (yy / h) * 0.55)
    r = ((xx - b * .42) / b) ** 2 + ((yy - h * .40) / h) ** 2
    return (g - 0.10 * r)[..., None]


def achtergrond(soort='zand', zaad=1):
    if soort == 'zand':
        img = np.asarray(Image.open(ZAND).convert('RGB')).astype(np.float32) / 255
        h, w = img.shape[:2]
        s = max(B / w, H / h) * 1.15
        img = cv2.resize(img, (int(w * s) + 1, int(h * s) + 1), interpolation=cv2.INTER_CUBIC)
        y0, x0 = (img.shape[0] - H) // 2, (img.shape[1] - B) // 2
        img = img[y0:y0 + H, x0:x0 + B]
        # warm zandkleur, niet grijs
        img = np.clip(img * np.array([1.03, 0.99, 0.92], np.float32) + 0.015, 0, 1)
        return np.clip(img * _licht(), 0, 1)
    kleur = np.array(PAPIER[soort], np.float32)
    vezel = _ruis((H, B), 0.006, 1.2, zaad) + _ruis((H, B), 0.0035, 22, zaad + 1)
    doek = kleur[None, None] * (1 + vezel[..., None])
    return np.clip(doek * _licht(), 0, 1)


def leg(doek, rgba, breedte=None, hoogte_px=None, midden=(B / 2, H / 2), draai=0.0, hoogte=6.0, zachtheid=1.0, contact=0.45):
    """Leg een vrijstaand product op de ondergrond.
    hoogte: hoe ver het product boven de ondergrond 'zweeft' (px op 1600 breed): bepaalt de afstand en zachtheid van de schaduw.
    Plat liggende stof: 3 tot 6. Een pet of tas: 12 tot 25."""
    h, w = rgba.shape[:2]
    s = (breedte / w) if breedte else (hoogte_px / h)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), draai, s)
    M[0, 2] += midden[0] - w / 2
    M[1, 2] += midden[1] - h / 2
    laag = cv2.warpAffine(rgba, M, (doek.shape[1], doek.shape[0]), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4,
                          borderValue=(0, 0, 0, 0))
    a = laag[..., 3]
    # zachte slagschaduw van het raamlicht + donkere contactschaduw direct onder de rand
    dx, dy = LICHT * hoogte * 2.2
    sch = cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]))
    sch = cv2.GaussianBlur(sch, (0, 0), max(2.0, hoogte * 2.4 * zachtheid))
    con = cv2.GaussianBlur(a, (0, 0), 2.2 + hoogte * 0.25)
    doek = doek * (1 - 0.30 * sch[..., None]) * (1 - contact * 0.5 * con[..., None] * (1 - a[..., None]))
    # het product krijgt hetzelfde raamlicht als de ondergrond
    licht = _licht(doek.shape[0], doek.shape[1])
    prod = np.clip(laag[..., :3] * (0.94 + 0.06 * licht / 1.04), 0, 1)
    return doek * (1 - a[..., None]) + prod * a[..., None]


def afwerking(img, korrel=0.011, zaad=7):
    h, b = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:b].astype(np.float32)
    vig = 1 - 0.06 * (((xx - b / 2) / (b / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    img = img * vig[..., None] * np.array([1.012, 1.0, 0.985], np.float32)
    img = cv2.GaussianBlur(img, (0, 0), 0.35)
    k = np.random.default_rng(zaad).normal(0, korrel, (h, b, 1)).astype(np.float32)
    return np.clip(img + k, 0, 1)


def vrijstaand(img, masker):
    """Product uit een foto knippen: rgb + zacht masker -> rgba, bijgesneden op het product."""
    a = cv2.GaussianBlur(masker.astype(np.float32), (0, 0), 0.8)
    ys, xs = np.where(a > 0.02)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return np.dstack([img[y0:y1, x0:x1], a[y0:y1, x0:x1]]).astype(np.float32)


def bewaar(img, pad, max_kb=190):
    pad = pathlib.Path(pad)
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    for q in (88, 85, 82, 79, 76, 73, 70):
        im.save(pad, quality=q, optimize=True, progressive=True)
        if pad.stat().st_size < max_kb * 1000:
            break
    return pad


if __name__ == '__main__':
    # proefvel van de ondergronden
    uit = pathlib.Path('/tmp') / 'stijl-proef'
    uit.mkdir(exist_ok=True)
    for s in ['zand', 'rose', 'baby', 'zandpapier', 'creme', 'navy']:
        bewaar(afwerking(achtergrond(s)), uit / f'{s}.jpg')
    print(uit)
