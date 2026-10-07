"""Extra levensechte productfoto's (sfeer, achterkant, in gebruik): onze ontwerpen op echte stockfoto's (Unsplash).

Bronnen staan in docs/producten/stock/bronnen.json. Hergebruikt mockup.py en echt.py (niet aanpassen).
Uitvoer: docs/producten/beelden/<naam>.jpg, 1600 x 2000, onder 190 kB.

    python3 tools/producten/echt_meer.py            # alles
    python3 tools/producten/echt_meer.py pet tas    # alleen deze stappen
"""
import pathlib, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import mockup as MK  # noqa: E402
import echt as E  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock'
REF = ROOT / 'docs' / 'producten' / 'referentie'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
NAVY, CREME, TERRA = '#22324F', '#F3ECDD', '#C0603E'
BABYBLAUW = '#BCD0E6'
CREME_T = '#EEE6D6'          # crème katoen zoals bij de andere crème kleding
NAVY_T = '#26365A'           # navy katoen zoals bij de andere navy kleding
FONT_COURIER = ROOT / 'tools' / 'brand2' / 'fonts' / 'CourierPrime-Bold.ttf'


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def foto(naam):
    return MK.laad(STOCK / naam)


def staand(img, cx, cy, hoogte):
    """4:5-uitsnede rond (cx, cy) met de gegeven hoogte (binnen de foto gehouden)."""
    h, w = img.shape[:2]
    hoogte = min(hoogte, h, int(w * 5 / 4))
    breedte = int(hoogte * 4 / 5)
    x0 = int(np.clip(cx - breedte / 2, 0, w - breedte))
    y0 = int(np.clip(cy - hoogte / 2, 0, h - hoogte))
    return (x0, y0, x0 + breedte, y0 + hoogte)


def kleur(img, masker, doel_hex, gamma=1.0, ref=None, sterkte=1.0):
    """Zoals MK.kleur_om, maar met instelbaar contrast: een witte stof heeft weinig schaduwbereik,
    dus bij omkleuren naar een donkere kleur de schaduw iets aanzetten (gamma > 1)."""
    doel = hexrgb(doel_hex)
    L = MK.helderheid(img)
    if ref is None:
        ref = float(np.median(L[masker > 0.5]))
    sch = np.clip(L / max(ref, 1e-3), 0, 1.8) ** gamma
    nieuw = np.clip(doel[None, None] * sch[..., None], 0, 1)
    m = (masker * sterkte)[..., None]
    return img * (1 - m) + nieuw * m


def norm_blur(x, gewicht, s):
    """Gemiddelde van x alleen over de pixels met gewicht (genormaliseerde convolutie)."""
    g = cv2.GaussianBlur(gewicht.astype(np.float32), (0, 0), s)
    if x.ndim == 3:
        return cv2.GaussianBlur(x * gewicht[..., None], (0, 0), s) / np.maximum(g, 1e-4)[..., None]
    return cv2.GaussianBlur(x * gewicht, (0, 0), s) / np.maximum(g, 1e-4)


def kleur_rand(img, hard, doel_hex, gamma=1.0, ref=None, rand=6):
    """Omkleuren met nette randen: in een smalle band rond de omtrek de dekking schatten uit de helderheid
    (tussen stof en de achtergrond vlak ernaast), zodat er geen lichte of donkere rand overblijft."""
    hard = hard.astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rand + 1, 2 * rand + 1))
    binnen = cv2.erode(hard, k).astype(np.float32)
    buiten = (1 - cv2.dilate(hard, k)).astype(np.float32)
    L = MK.helderheid(img)
    s = rand * 2.5
    Lst = norm_blur(L, binnen, s)
    Lbg = norm_blur(L, buiten, s)
    bg = norm_blur(img, buiten, s)
    a = np.clip((L - Lbg) / np.where(np.abs(Lst - Lbg) < 0.08, np.nan, Lst - Lbg), 0, 1)
    a = np.where(np.isnan(a), hard.astype(np.float32), a)
    band = (1 - binnen) * (1 - buiten)
    a = np.where(band > 0, a, hard.astype(np.float32))
    a = cv2.GaussianBlur(a, (0, 0), 0.6)
    doel = hexrgb(doel_hex)
    if ref is None:
        ref = float(np.median(L[binnen > 0]))
    # in de band de stofkleur van vlak ernaast gebruiken, binnen de echte helderheid
    Lk = np.where(band > 0, Lst, L)
    nieuw = np.clip(doel[None, None] * (np.clip(Lk / ref, 0, 1.8) ** gamma)[..., None], 0, 1)
    bg = np.where(band[..., None] > 0, bg, img)
    uit = nieuw * a[..., None] + bg * (1 - a[..., None])
    return np.where((band[..., None] > 0) | (hard[..., None] > 0), uit, img), a


def component(binair, zaad):
    """Alleen het samenhangende stuk onder het zaadpunt (x, y)."""
    n, lab = cv2.connectedComponents(binair.astype(np.uint8))
    k = lab[zaad[1], zaad[0]]
    return (lab == k) if k else np.zeros_like(binair, bool)


def vul_gaten(b):
    b = b.astype(np.uint8)
    v = b.copy(); ff = np.zeros((b.shape[0] + 2, b.shape[1] + 2), np.uint8)
    cv2.floodFill(v, ff, (0, 0), 1)
    return b | (1 - v)


def zacht(b, s=1.2):
    return cv2.GaussianBlur(b.astype(np.float32), (0, 0), s)


def grabcut(img, rect, iter=6, schaal=0.4, voor=None, achter=None):
    """GrabCut binnen rect (x0, y0, x1, y1); voor/achter = lijst met polygonen die zeker wel/niet bij het stuk horen."""
    h, w = img.shape[:2]
    u8 = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    sm = cv2.resize(u8, (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_AREA)
    m = np.zeros(sm.shape[:2], np.uint8)
    x0, y0, x1, y1 = [int(v * schaal) for v in rect]
    m[y0:y1, x0:x1] = cv2.GC_PR_FGD
    for p in voor or []:
        cv2.fillPoly(m, [(np.array(p) * schaal).astype(np.int32)], cv2.GC_FGD)
    for p in achter or []:
        cv2.fillPoly(m, [(np.array(p) * schaal).astype(np.int32)], cv2.GC_BGD)
    bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(sm, m, None, bg, fg, iter, cv2.GC_INIT_WITH_MASK)
    uit = ((m == 1) | (m == 3)).astype(np.float32)
    return cv2.resize(uit, (w, h), interpolation=cv2.INTER_LINEAR) > 0.5


# ---------- pet ----------
def pet():
    """Gedragen: man zet de (witte, 5-panel) pet recht; pet wordt navy met het crème board geborduurd op het voorpand."""
    p = foto('pet-wit-gedragen-1.jpg')
    h, w = p.shape[:2]
    hsv = cv2.cvtColor((p * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    L = MK.helderheid(p)
    wit = (hsv[..., 1] < 40) & (L > 0.5)
    wit[2660:] = False                                   # het witte T-shirt eronder hoort er niet bij
    m = component(cv2.morphologyEx(wit.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), (1300, 1850))
    m = vul_gaten(cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)))
    p, _ = kleur_rand(p, m, '#253252', gamma=1.9, ref=0.86, rand=4)
    p = borduur_op(p, L, 0.86, E.art('icoon-navy.png', CREME), 1288, 1870, 96, draai=7)
    E.bewaar(p, 'pet-navy-2', vul=1.0, uitsnede=staand(p, 1300, 2050, 2600))


# ---------- bucket hat ----------
def bucket():
    """Gedragen tegen een klimopmuur: de (grijsgroene) bucket hat wordt crème met het kleine navy board geborduurd."""
    b = foto('buckethat-gedragen-1.jpg')
    m = grabcut(b, (700, 560, 2000, 1520), voor=[[(800, 800), (1600, 760), (1650, 1080), (800, 1150)]],
                achter=[[(1000, 1250), (1500, 1220), (1550, 1700), (1000, 1700)], [(0, 0), (2400, 0), (2400, 560), (0, 560)]])
    m = vul_gaten(cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8)))
    m = component(m, (1200, 950)).astype(np.uint8)
    L = MK.helderheid(b)
    ref = float(np.percentile(L[m > 0], 70))
    b, _ = kleur_rand(b, m, '#E9DFCB', gamma=0.9, ref=ref, rand=4)
    b = borduur_op(b, L, ref, E.art('icoon-navy.png', NAVY), 1235, 950, 74, draai=-2)
    E.bewaar(b, 'bucket-hat-tegel-2', vul=1.0, uitsnede=(340, 250, 2260, 2650))


def borduur_op(img, L_bron, ref, a, cx, cy, breedte, draai=0, sterkte=0.8):
    """E.borduur, en daarna het licht van de stof (uit de bronfoto) ook over het borduursel."""
    uit = E.borduur(img, a, cx, cy, breedte, draai)
    h, w = img.shape[:2]
    ah, aw = a.shape[:2]
    M = cv2.getRotationMatrix2D((aw / 2, ah / 2), draai, breedte / aw)
    M[0, 2] += cx - aw / 2; M[1, 2] += cy - ah / 2
    al = cv2.warpAffine(a[..., 3], M, (w, h), flags=cv2.INTER_AREA)[..., None]
    licht = np.clip(cv2.GaussianBlur(L_bron, (0, 0), 5) / ref, 0.4, 1.3)[..., None] ** sterkte
    return uit * (1 - al) + np.clip(uit * licht, 0, 1) * al


if __name__ == '__main__':
    stappen = sys.argv[1:] or ['pet']
    for st in stappen:
        globals()[st]()
