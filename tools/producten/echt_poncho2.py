"""Surfponcho Tegel: productfoto's uit een echte foto van een opgevouwen badstof handdoek.

Bron: docs/producten/stock/handdoek-1.jpg (Unsplash, zie bronnen.json). De poncho wordt opgevouwen verkocht, dus een
echte gevouwen badstof foto is de basis. Wat we veranderen:
- kleur: de felblauwe badstof wordt zacht zeeblauw, het witte tafelblad en de muur warm crème (licht en schaduw blijven
  van de foto, ook de blauwe weerkaatsing op het blad);
- de geweven sierband van de handdoek krijgt onze tegelrand: een rij ruitjes in koraal, crème en baby blue met een navy
  stip. Het patroon volgt de band stukje voor stukje (over de voorkant en dan naar achteren over de bovenkant), en het
  weefsel van de echte band blijft zichtbaar;
- een klein geweven TIDE TODE label op de bovenkant.

Foto 1: het hele pakket, staand 4:5. Foto 2: dichterbij op de band en het label. Foto 3: macro van band en badstof.
Gebruik: python3 tools/producten/echt_poncho2.py
"""
import pathlib
import sys

import cv2
import numpy as np

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import stijl as ST  # noqa: E402

BRON = ROOT / 'docs' / 'producten' / 'stock' / 'handdoek-1.jpg'
LABEL = HIER / 'uit_handdoek' / 'label.png'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'

ZEE = np.array([0.40, 0.58, 0.74], np.float32)          # zacht zeeblauw (rgb)
CREME = np.array([0.953, 0.925, 0.867], np.float32)
KORAAL, NAVY, BABY = (0.80, 0.42, 0.30), (0.133, 0.196, 0.31), (0.75, 0.83, 0.92)
CR = (0.95, 0.92, 0.85)

# randen van de geweven band, van voor-onder (u = 0) naar achter (u = 1), in px van de bronfoto
LINKS = [(352, 888), (350, 800), (356, 745), (372, 705), (410, 668), (470, 642), (540, 612), (640, 572), (700, 548)]
RECHTS = [(532, 888), (532, 820), (537, 770), (548, 738), (585, 712), (640, 676), (720, 623), (810, 563), (860, 532)]
# hoeveel langer een stukje in het echt is dan zijn breedte doet vermoeden (bovenkant loopt van je af en is verkort)
VERKORT = [1.0, 1.0, 1.2, 1.6, 2.2, 2.7, 3.0, 3.1]


def rgb(p):
    return cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def lint(lengte_tegels, t=160):
    """De tegelrand als vlak lint: t px per tegel, tegels naast elkaar, dunne navy lijntjes langs beide randen."""
    n = int(np.ceil(lengte_tegels)) + 1
    img = np.zeros((t, n * t, 3), np.float32)
    achter = [KORAAL, CR, BABY]
    ruit = [CR, KORAAL, CR]
    yy, xx = np.mgrid[0:t, 0:t].astype(np.float32)
    for i in range(n):
        k = i % 3
        tegel = np.empty((t, t, 3), np.float32); tegel[:] = achter[k]
        d = np.abs(xx - t / 2) + np.abs(yy - t / 2)
        tegel[d < t * 0.36] = ruit[k]
        tegel[np.hypot(xx - t / 2, yy - t / 2) < t * 0.085] = NAVY
        img[:, i * t:(i + 1) * t] = tegel
    img[:int(t * 0.035)] = NAVY
    img[-int(t * 0.035):] = NAVY
    return cv2.GaussianBlur(img, (0, 0), 1.2)


def band_op_foto(foto):
    """Leg het lint stukje voor stukje op de band. Geeft (beeld, masker)."""
    H, W = foto.shape[:2]
    L, R = np.float32(LINKS), np.float32(RECHTS)
    breed = np.linalg.norm(R - L, axis=1)
    lang = []
    for i in range(len(L) - 1):
        mid = (L[i] + R[i]) / 2; mid2 = (L[i + 1] + R[i + 1]) / 2
        lang.append(np.linalg.norm(mid2 - mid) / ((breed[i] + breed[i + 1]) / 2) * VERKORT[i])
    t = 160
    tex = lint(sum(lang), t)
    uit = np.zeros_like(foto); m = np.zeros((H, W), np.float32)
    u = 0.0
    for i in range(len(L) - 1):
        u1 = u + lang[i]
        bron = np.float32([[u * t, 0], [u * t, t], [u1 * t, t], [u1 * t, 0]])
        doel = np.float32([L[i], R[i], R[i + 1], L[i + 1]])
        M = cv2.getPerspectiveTransform(bron, doel)
        laag = cv2.warpPerspective(tex, M, (W, H), flags=cv2.INTER_LINEAR)
        vak = np.zeros((H, W), np.uint8); cv2.fillPoly(vak, [np.int32(np.round(doel))], 1)
        vak = cv2.dilate(vak, np.ones((3, 3), np.uint8)).astype(np.float32)
        uit = uit * (1 - vak[..., None]) + laag * vak[..., None]
        m = np.maximum(m, vak)
        u = u1
    # zachte rand, de band ligt iets verzonken in de badstof
    m = cv2.GaussianBlur(m, (0, 0), 1.6)
    return uit, m


def label_op(img, midden, breedte, hoek, verkort, licht=None):
    lab = rgb(LABEL)
    h, w = lab.shape[:2]
    s = breedte / w
    M = cv2.getRotationMatrix2D((w / 2, h / 2), hoek, s)
    M[1] *= verkort
    M[0, 2] += midden[0] - w / 2; M[1, 2] += midden[1] - h / 2 * verkort
    H, W = img.shape[:2]
    laag = cv2.warpAffine(lab, M, (W, H), flags=cv2.INTER_AREA)
    a = cv2.warpAffine(np.ones((h, w), np.float32), M, (W, H), flags=cv2.INTER_AREA)
    # schaduw onder het label (licht linksboven) en het licht van de foto
    sch = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, 3], [0, 1, 4]]), (W, H)), (0, 0), 3)
    img = img * (1 - 0.35 * sch[..., None] * (1 - a[..., None]))
    laag = cv2.GaussianBlur(laag, (0, 0), 1.3)                          # zelfde scherpte als de badstof daar
    if licht is not None:
        # het label ligt op de badstof: de lusjes eronder drukken er een beetje doorheen
        hp = licht - cv2.GaussianBlur(licht, (0, 0), 3)
        laag = laag * np.clip(cv2.GaussianBlur(licht, (0, 0), 10), 0.7, 1.15)[..., None] * (1 + 0.35 * hp[..., None])
    laag = laag * 0.88 + 0.03
    a = cv2.GaussianBlur(a, (0, 0), 0.8)
    return img * (1 - a[..., None]) + laag * a[..., None]


def maak():
    f = rgb(BRON)
    H, W = f.shape[:2]
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    L = 0.25 * r + 0.45 * g + 0.30 * b
    # hoe 'blauw' een pixel is: badstof 1, tafel en muur 0, weerkaatsing ertussenin
    blauw = np.clip((b - r - 0.08) / 0.45, 0, 1)
    blauw = cv2.GaussianBlur(blauw, (0, 0), 1.0)
    # badstof: zacht zeeblauw met het licht en donker van de lusjes (iets minder contrast dan het felle origineel)
    Lb = L / np.median(L[blauw > 0.9])
    stof = ZEE[None, None] * (1 + (Lb[..., None] - 1) * 0.85)
    # tafel en muur: crème met hetzelfde licht
    Lw = L / np.median(L[blauw < 0.05])
    grond = CREME[None, None] * Lw[..., None]
    img = stof * blauw[..., None] + grond * (1 - blauw[..., None])
    # tegelrand op de geweven band, met het weefsel van de echte band
    lint_img, m = band_op_foto(img)
    Lband = L / max(float(np.median(L[m > 0.9])), 1e-3)
    weef = 1 + (Lband - cv2.GaussianBlur(Lband, (0, 0), 6)) * 0.6       # fijne binding
    vorm = cv2.GaussianBlur(Lband, (0, 0), 6)                            # plooi en licht over de vouw
    band = lint_img * (weef * vorm)[..., None]
    band = band * 0.92 + band.mean(-1, keepdims=True) * 0.08            # garen is iets doffer dan het ontwerp
    # scherptediepte van de foto: achterop de handdoek is alles onscherp
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    onscherp = np.clip((690 - yy) / 120, 0, 1)[..., None]
    band = band * (1 - onscherp) + cv2.GaussianBlur(band, (0, 0), 3.5) * onscherp
    m = m * np.clip((blauw - 0.5) * 2, 0, 1)                                                        # niet buiten de handdoek
    img = img * (1 - m[..., None]) + band * m[..., None]
    img = label_op(img, (1120, 660), 128, -7, 0.6, licht=Lb)
    return np.clip(img, 0, 1)


def staand(img):
    """Naar 1600 x 2000: muur boven en tafel onder doorgetrokken."""
    H, W = img.shape[:2]
    extra = 2000 - H
    boven = extra * 2 // 3; onder = extra - boven
    rij = cv2.GaussianBlur(img[:40], (0, 0), 8).mean(0, keepdims=True)
    top = np.repeat(rij, boven, 0)
    # muur wordt naar boven toe iets donkerder, zoals de val-off van het raamlicht
    top = top * np.linspace(0.97, 1.0, boven)[:, None, None]
    bodem = img[-onder:][::-1]
    return np.concatenate([top, img, bodem], 0)


if __name__ == '__main__':
    beeld = maak()
    een = staand(beeld)
    ST.bewaar(ST.afwerking(een), DOEL / 'surfponcho-tegel-1.jpg')
    # 2: dichterbij op band en label
    twee = beeld[380:1180, 250:890]
    twee = cv2.resize(twee, (1600, 2000), interpolation=cv2.INTER_CUBIC)
    ST.bewaar(ST.afwerking(twee), DOEL / 'surfponcho-tegel-2.jpg')
    # 3: macro van de band waar hij over de voorkant naar beneden loopt, met badstof ernaast
    drie = beeld[560:1000, 250:602]
    drie = cv2.resize(drie, (1600, 2000), interpolation=cv2.INTER_CUBIC)
    ST.bewaar(ST.afwerking(drie, korrel=0.008), DOEL / 'surfponcho-tegel-3.jpg')
    print('klaar')
