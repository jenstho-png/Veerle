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
    # in de band: pixel = stof * a + achtergrond * (1 - a); alleen het stofdeel vervangen, de achtergrond blijft echt
    Lk = np.where(band > 0, Lst, L)
    nieuw = np.clip(doel[None, None] * (np.clip(Lk / ref, 0, 1.8) ** gamma)[..., None], 0, 1)
    stof = norm_blur(img, binnen, s)
    rand_uit = np.clip(img + (nieuw - stof) * a[..., None], 0, 1)
    uit = np.where(band[..., None] > 0, rand_uit, nieuw * a[..., None] + img * (1 - a[..., None]))
    return np.where((band[..., None] > 0) | (hard[..., None] > 0), uit, img), a


def vlekken_weg(img, m, k=25, rand=12):
    """Kleine donkere vlekjes (vuil, krasjes) op de stof weghalen; plooien (groot) blijven."""
    L = MK.helderheid(img)
    dicht = cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    dicht = cv2.GaussianBlur(dicht, (0, 0), 2)
    f = np.clip(dicht / np.maximum(L, 1e-3), 1, 1.6)
    f = np.where(f > 1.025, f, 1.0)
    binnen = cv2.erode((m > 0.5).astype(np.uint8), np.ones((2 * rand + 1, 2 * rand + 1), np.uint8)).astype(np.float32)
    f = 1 + (cv2.GaussianBlur(f.astype(np.float32), (0, 0), 1.5) - 1) * zacht(binnen, 4)
    return np.clip(img * f[..., None], 0, 1)


def rest_tint(img, m, doel_hex, ring=10, hue=(60, 115), smin=18, sterkte=1.0):
    """Restjes van de oude stofkleur (bv. een donker randje van de rand) net buiten het masker
    krijgen de nieuwe tint, met behoud van hun helderheid."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ring + 1, 2 * ring + 1))
    zone = cv2.dilate((m > 0.5).astype(np.uint8), k).astype(bool)
    hsv = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    sel = zone & (hsv[..., 0] >= hue[0]) & (hsv[..., 0] <= hue[1]) & (hsv[..., 1] >= smin)
    a = zacht(sel, 1.0)[..., None] * sterkte
    doel = hexrgb(doel_hex)
    L = MK.helderheid(img)[..., None]
    nieuw = np.clip(doel[None, None] * L / MK.helderheid(doel[None, None])[..., None], 0, 1)
    return img * (1 - a) + nieuw * a


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


def grabcut_poly(img, poly, band=30, iter=5, schaal=0.5):
    """Met de hand getekende omtrek (of lijst van omtrekken), GrabCut beslist alleen in een smalle band rond de lijn."""
    h, w = img.shape[:2]
    p = np.zeros((h, w), np.uint8)
    polys = poly if isinstance(poly[0][0], (list, tuple)) else [poly]
    cv2.fillPoly(p, [np.array(q, np.int32) for q in polys], 1)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * band + 1, 2 * band + 1))
    zeker = cv2.erode(p, k); mogelijk = cv2.dilate(p, k)
    m = np.full((h, w), cv2.GC_BGD, np.uint8)
    m[mogelijk > 0] = cv2.GC_PR_BGD
    m[p > 0] = cv2.GC_PR_FGD
    m[zeker > 0] = cv2.GC_FGD
    u8 = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    sm = cv2.resize(u8, (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
    bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(sm, ms, None, bg, fg, iter, cv2.GC_INIT_WITH_MASK)
    uit = cv2.resize(((ms == 1) | (ms == 3)).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR) > 0.5
    uit = cv2.morphologyEx(uit.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return vul_gaten(cv2.morphologyEx(uit, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)))


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
    omtrek = [(745, 880), (790, 790), (850, 722), (910, 678), (975, 648), (1050, 628), (1118, 613), (1318, 624), (1464, 655),
              (1573, 718), (1636, 827), (1673, 973), (1700, 1040), (1800, 1100), (1890, 1130), (1955, 1150), (1950, 1200),
              (1925, 1250), (1880, 1295), (1830, 1320), (1785, 1300), (1750, 1240), (1725, 1170),
              (1705, 1130), (1600, 1121), (1400, 1113), (1200, 1118), (1000, 1130),
              (900, 1152), (830, 1195), (790, 1250), (752, 1340), (740, 1440), (690, 1478), (570, 1485), (590, 1440),
              (660, 1395), (725, 1320), (740, 1200), (738, 1050)]
    m = grabcut_poly(b, omtrek, band=22)
    m = component(m, (1200, 900)).astype(np.uint8)
    L = MK.helderheid(b)
    ref = float(np.percentile(L[m > 0], 58))
    bron = b.copy()
    b, _ = kleur_rand(b, m, '#F2E6CD', gamma=0.85, ref=ref, rand=4)
    b = rest_tint(b, m, '#F2E6CD', ring=9, hue=(68, 130), smin=8)
    # onderrand van de rand boven het gezicht: een vloeiende lijn (geen trapjes), de zoom crème in de schaduw
    yy, xx = np.mgrid[0:b.shape[0], 0:b.shape[1]].astype(np.float32)
    rand_y = np.interp(xx, [880, 960, 1020, 1080, 1140, 1200, 1260, 1320, 1380, 1440, 1500, 1560, 1620, 1680, 1745],
                       [1165, 1155, 1145, 1140, 1130, 1129, 1131, 1132, 1129, 1136, 1140, 1145, 1147, 1153, 1152])
    binnen_x = ((xx > 880) & (xx < 1745)).astype(np.float32)
    onder = np.clip((yy - rand_y - 1) / 2.0, 0, 1) * (yy < rand_y + 60) * binnen_x
    b = b * (1 - onder[..., None]) + bron * onder[..., None]
    zoom = np.clip(1 - np.abs(yy - (rand_y - 5)) / 7.0, 0, 1) * binnen_x
    b = b * (1 - zoom[..., None]) + kleur(bron, np.ones_like(L), '#F2E6CD', gamma=0.85, ref=ref) * zoom[..., None]
    b = borduur_op(b, L, ref, E.art('icoon-navy.png', NAVY), 1230, 885, 62, draai=-2)
    E.bewaar(b, 'bucket-hat-tegel-2', vul=1.0, uitsnede=(340, 250, 2260, 2650))


# ---------- canvas tas ----------
def tas():
    """Vastgehouden voor de benen (jeans, betonnen muur): witte tas wordt naturel canvas met de busjesprint.
    Strak uitgesneden boven de sneakers (die hebben een merkteken)."""
    t = foto('tote-gedragen-1.jpg')
    s = t.shape[1] / 2400                                   # coördinaten hieronder in de 2400 px-versie
    P = lambda pts: [(int(x * s), int(y * s)) for x, y in pts]
    romp = P([(932, 633), (1000, 628), (1200, 630), (1400, 640), (1480, 647), (1484, 1000), (1481, 1248), (1200, 1245),
              (917, 1236), (925, 900)])
    links = P([(1066, 322), (1098, 322), (1106, 632), (1060, 632)])
    rechts = P([(1300, 322), (1338, 322), (1350, 644), (1304, 644)])
    m = grabcut_poly(t, [romp, links, rechts], band=int(14 * s))
    m = vul_gaten(m & (MK.helderheid(t) > 0.5))                 # de tas is overal licht; donkere randjes (knie) eruit
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    t = vlekken_weg(t, m, k=int(22 * s))
    L = MK.helderheid(t)
    ref = float(np.percentile(L[m > 0], 70))
    t, _ = kleur_rand(t, m, '#E6DCC8', gamma=1.15, ref=ref, rand=int(4 * s))
    # canvas: grovere weefstructuur dan de gladde katoen van de stockfoto
    rng = np.random.default_rng(7)
    korrel = cv2.GaussianBlur(rng.normal(0, 1, t.shape[:2]).astype(np.float32), (0, 0), 1.1)
    t = np.clip(t + (korrel * 0.018 * zacht(m, 2))[..., None], 0, 1)
    rm = zacht(m, 1.2)
    t = MK.zet_print(t, E.art('hoodie-busje-rugprint-los.png'), int(1203 * s), int(905 * s), int(345 * s), verplaatsing=6,
                     schaduw_sterkte=0.85, structuur=0.6, masker=rm)
    E.bewaar(t, 'canvas-tas-2', vul=1.0, uitsnede=tuple(int(v * s) for v in (712, 34, 1696, 1264)))


# ---------- hoodie ----------
def hoodie():
    """Achterkant, gedragen (handen aan de capuchon, buiten bij een amfitheater): witte hoodie wordt baby blue
    met de busjesprint groot op de rug."""
    h = foto('hoodie-wit-rug-2.jpg')
    x0, y0, x1, y1 = 950, 150, 2700, 2000
    deel = h[y0:y1, x0:x1]
    m = np.zeros(h.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = (E.shirt_masker(deel) > 0.5)
    L = MK.helderheid(h)
    ref = float(np.percentile(L[m > 0], 93))
    h, _ = kleur_rand(h, m, BABYBLAUW, gamma=1.1, ref=ref, rand=4)
    h = MK.zet_print(h, E.art('hoodie-busje-rugprint-los.png'), 1835, 1010, 500, draai=-1.5, verplaatsing=9,
                     schaduw_sterkte=0.95, structuur=0.55, masker=zacht(m, 1.2))
    E.bewaar(h, 'hoodie-busje-2', vul=1.0, uitsnede=(965, 70, 2685, 2220))


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
