"""Instagrampost 'de echte': de echte foto van de draagtas op een board (fabrieksfoto), 1080 x 1350.

- de gele spanbanden op de vloer en de sticker van een ander merk worden weggewerkt met vloer- en boardtextuur
  van vlak ernaast;
- extra slides met andere ontwerpen: dezelfde foto, alleen het patroon van de stof is vervangen. Plooien, licht
  en weefstructuur komen uit de echte stof, de band blijft de echte band.

Opnieuw maken: python3 tools/social/echt_post.py
"""
import pathlib
import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FOTO = ROOT / 'docs' / 'producten' / 'fabriek' / 'fabrieksfoto.jpg'
REF = ROOT / 'docs' / 'producten' / 'referentie'
UIT = ROOT / 'docs' / 'social' / 'post-10-de-echte'
X0, B = 595, 901                       # uitsnede 4:5 uit de foto van 2000 x 1126
# hoeken van de stof (in de uitsnede): lb, rb, ro, lo
STOF = np.float32([[176, 437], [714, 437], [884, 986], [-16, 994]])
TEGEL = 100                            # tegelmaat van de echte stof in px


def schoon():
    im = cv2.imread(str(FOTO))
    c = im[:, X0:X0 + B].copy()
    H, W = c.shape[:2]
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    geel = ((hsv[..., 0] > 12) & (hsv[..., 0] < 32) & (hsv[..., 1] > 90) & (hsv[..., 2] > 80)).astype(np.uint8)
    geel = cv2.dilate(cv2.morphologyEx(geel, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), np.ones((7, 7), np.uint8))
    blauw = ((hsv[..., 0] > 95) & (hsv[..., 0] < 125) & (hsv[..., 1] > 50)).astype(np.uint8)
    blauw = cv2.morphologyEx(blauw, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    # alleen de band zelf (grote aaneengesloten vorm), niet de blauwe tegels in de stof
    n, lab, st, _ = cv2.connectedComponentsWithStats(blauw)
    blauw = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 15000]).astype(np.uint8)
    blauw = cv2.morphologyEx(blauw, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # band is ca. 50 px breed: smalle uitlopers (blauwe stukjes van de tegels die eraan vastzitten) eraf
    rond = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    blauw = cv2.morphologyEx(blauw, cv2.MORPH_OPEN, rond)
    geel = geel & (1 - cv2.erode(blauw, np.ones((3, 3), np.uint8)))
    boven = geel.copy(); boven[:200] = 0; boven[400:] = 0
    onder = geel.copy(); onder[:1030] = 0
    sticker = np.zeros((H, W), np.uint8); sticker[590:705, 0:36] = 1
    verboden = boven | onder | sticker | cv2.dilate(blauw, np.ones((9, 9), np.uint8))
    uit = c.copy()

    def vul(m, verschuivingen):
        m = m.astype(bool)
        for dy, dx in verschuivingen:
            bron = np.roll(c, (dy, dx), axis=(0, 1)); bm = np.roll(verboden, (dy, dx), axis=(0, 1))
            ok = m & (bm == 0); uit[ok] = bron[ok]; m &= ~ok

    zij = [(0, 45), (0, -45), (0, 80), (0, -80)]
    vul(boven, [(55, 0), (95, 0), (55, 40), (55, -40), (95, 60), (95, -60)] + zij)
    vul(onder, [(-45, 0), (-60, 0), (-45, 40), (-45, -40)] + zij)
    vul(sticker, [(120, 0), (140, 0)])
    m = np.clip(cv2.GaussianBlur((boven | onder | sticker).astype(np.float32), (0, 0), 1.5) * 1.6, 0, 1)[..., None]
    return (uit * m + c * (1 - m)).astype(np.uint8), blauw


def ander_ontwerp(foto, blauw, handle):
    H, W = foto.shape[:2]
    vorm = np.zeros((H, W), np.uint8)
    cv2.fillPoly(vorm, [np.int32(STOF)], 1)
    vorm = vorm & (1 - cv2.dilate(blauw, np.ones((3, 3), np.uint8)))
    a = cv2.GaussianBlur(vorm.astype(np.float32), (0, 0), 1.2)[..., None]
    # licht en plooien uit de echte stof: helderheid, met de tegelkleuren eruit gemiddeld
    f = foto.astype(np.float32) / 255
    L = f.mean(-1)
    w = vorm.astype(np.float32)
    laag = cv2.GaussianBlur(L * w, (0, 0), 55) / np.maximum(cv2.GaussianBlur(w, (0, 0), 55), 1e-3)
    licht = np.clip(laag / max(float(laag[vorm > 0].mean()), 1e-3), 0.85, 1.12)
    # schaduw van de band op de stof en de zoom langs de rand: uit de foto (smalle donkere randen)
    rand = cv2.GaussianBlur(cv2.erode(vorm, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 3)
    licht = licht * (0.82 + 0.18 * rand)
    # jacquardbinding: fijne schering en inslag met kleine onregelmatigheden (zoals tools/tas/scene.py)
    rng = np.random.default_rng(3)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fijn = (0.06 * np.sin(xx * 2 * np.pi / 2.6) * np.sin(yy * 2 * np.pi / 2.9)
            + cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.6) * 0.025
            + np.repeat(rng.normal(0, 0.02, (H, 1)), W, 1))
    # echte weefstructuur: wat de mediaan (die de randen van het oude patroon houdt) niet volgt
    L8 = (L * 255).astype(np.uint8)
    echt = (L8.astype(np.float32) - cv2.medianBlur(L8, 5).astype(np.float32)) / 255
    fijn = fijn * 0.5 + np.clip(echt, -0.06, 0.06) * 1.6
    pat = cv2.imread(str(REF / f'draagtas-{handle}-stof.png')).astype(np.float32) / 255
    s = TEGEL / (pat.shape[1] / 6)
    pat = cv2.resize(pat, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    pat = cv2.GaussianBlur(pat, (0, 0), 0.9)
    pat = pat * 0.9 + pat.mean((0, 1)) * 0.1                # stof is nooit zo fel als het bestand
    reps = (H // pat.shape[0] + 2, W // pat.shape[1] + 2, 1)
    vlak = np.tile(pat, reps)
    oy, ox = 442 % pat.shape[0], 178 % pat.shape[1]
    vlak = np.roll(vlak, (oy, ox), axis=(0, 1))[:H, :W]
    stof = vlak * licht[..., None] * (1 + fijn[..., None])
    stof = np.clip(stof + rng.normal(0, 0.012, (H, W, 1)).astype(np.float32), 0, 1)   # zelfde ruis als de telefoonfoto
    return np.clip(f * (1 - a) + stof * a, 0, 1) * 255


def bewaar(img, naam):
    img = cv2.resize(img.astype(np.uint8), (1080, 1350), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(str(UIT / naam), img, [cv2.IMWRITE_JPEG_QUALITY, 90])


if __name__ == '__main__':
    UIT.mkdir(parents=True, exist_ok=True)
    foto, blauw = schoon()
    bewaar(foto, 'slide-1.jpg')
    detail = cv2.imread(str(FOTO))[430:1030, 720:1200]
    bewaar(cv2.resize(detail, (1080, 1350), interpolation=cv2.INTER_CUBIC), 'slide-2.jpg')
    for i, h in enumerate(['golfjes', 'tegel-navy', 'zonsondergang'], start=3):
        bewaar(ander_ontwerp(foto, blauw, h), f'slide-{i}.jpg')
    print(UIT)
