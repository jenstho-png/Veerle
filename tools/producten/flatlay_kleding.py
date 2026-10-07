"""Flat lays van de kleding van Tide Tode: recht van boven, netjes en symmetrisch neergelegd, op papier of zand.

Werkwijze per kledingstuk:
1. echte stockfoto van een blanco kledingstuk, plat van boven gefotografeerd (docs/producten/stock/flatlay, zie bronnen.json);
2. uitknippen: masker op stofstructuur (de achtergrond is glad), GrabCut, en de rand per punt vastgezet op de echte stofrand
   (de sterkste overgang van licht naar schaduw langs de normaal), dan antialiased gevuld: geen halo, geen schaduwrand;
3. symmetrisch maken: de linkerhelft gespiegeld voor mouw en schouder rechts, het midden blijft origineel (geen spiegelnaad);
4. achterkant: de voorste halsuitsnijding dicht met stof van de rug, alleen de rugboord blijft;
5. omkleuren (mockup.kleur_om) en print erin drukken (mockup.zet_print, volgt de plooien);
6. op de ondergrond leggen met stijl.leg (licht linksboven, schaduw rechtsonder) en stijl.afwerking.

Gebruik: python3 tools/producten/flatlay_kleding.py proef
"""
import json, pathlib, sys
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, median_filter, uniform_filter1d

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import stijl as ST  # noqa: E402
import mockup as MK  # noqa: E402
import echt as E  # noqa: E402

FLAT = ROOT / 'docs' / 'producten' / 'stock' / 'flatlay'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
PROEF = ROOT / 'docs' / 'producten' / 'proef'
NAVY, CREME = '#22324F', '#F3ECDD'
CREME_T = '#EEE6D6'


def _k(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def _vul_gaten(m):
    f = m.copy()
    cv2.floodFill(f, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 1)
    return m | (1 - f)


def _grootste(m):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    return (lab == 1 + st[1:, cv2.CC_STAT_AREA].argmax()).astype(np.uint8) if n > 1 else m


# ---------- uitknippen ----------
def masker_vlak(img, drempel=0.002):
    """Masker voor een kledingstuk op een glad (digitaal schoon) studiovlak met zachte slagschaduw.
    Stof heeft structuur, het vlak en de schaduw niet. Geeft een zacht (antialiased) alfa-kanaal terug."""
    L = img.mean(-1)
    tex = cv2.GaussianBlur(np.abs(L - cv2.GaussianBlur(L, (0, 0), 1.5)), (0, 0), 3)
    m = _grootste((tex > drempel).astype(np.uint8))
    m = _vul_gaten(cv2.morphologyEx(m, cv2.MORPH_CLOSE, _k(7)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, _k(4))
    # GrabCut op helderheid, structuur en randsterkte
    u = img * 255
    Lu = u.mean(-1)
    hp = np.clip(np.abs(Lu - cv2.GaussianBlur(Lu, (0, 0), 1.5)) * 40, 0, 255)
    Lb = cv2.GaussianBlur(Lu, (0, 0), 1)
    gm = np.hypot(cv2.Sobel(Lb, cv2.CV_32F, 1, 0), cv2.Sobel(Lb, cv2.CV_32F, 0, 1))
    f = np.dstack([np.clip((Lu - 200) * 5, 0, 255), cv2.GaussianBlur(hp, (0, 0), 2), np.clip(gm * 4, 0, 255)]).astype(np.uint8)
    g = np.full(m.shape, cv2.GC_BGD, np.uint8)
    g[cv2.dilate(m, _k(7)) > 0] = cv2.GC_PR_BGD
    g[m > 0] = cv2.GC_PR_FGD
    g[cv2.erode(m, _k(20)) > 0] = cv2.GC_FGD
    cv2.grabCut(f, g, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK)
    r = _grootste(((g == 1) | (g == 3)).astype(np.uint8))
    r = cv2.morphologyEx(cv2.morphologyEx(r, cv2.MORPH_OPEN, _k(3)), cv2.MORPH_CLOSE, _k(3))
    return rand_vast(img, r)


def rand_vast(img, m, zoek=(-26, 10)):
    """Zet de omtrek per punt op de echte stofrand: langs de normaal de sterkste daling van licht (stof) naar donker (schaduw).
    Daarna glad en met 8x supersampling gevuld."""
    L = cv2.GaussianBlur(img.mean(-1), (0, 0), 1.0)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = uniform_filter1d(max(cs, key=len)[:, 0, :].astype(np.float32), 15, axis=0, mode='wrap')
    t = np.gradient(c, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-6
    nrm = np.stack([t[:, 1], -t[:, 0]], 1)
    p = c + nrm * 6
    if m[np.clip(p[:, 1].astype(int), 0, m.shape[0] - 1), np.clip(p[:, 0].astype(int), 0, m.shape[1] - 1)].mean() > 0.5:
        nrm = -nrm                                    # normaal naar buiten
    offs = np.arange(zoek[0], zoek[1], 0.5)
    P = c[:, None, :] + nrm[:, None, :] * offs[None, :, None]
    v = map_coordinates(L, [P[..., 1], P[..., 0]], order=1)
    best = offs[np.argmin(np.gradient(v, axis=1), axis=1)]
    best = uniform_filter1d(median_filter(uniform_filter1d(best, 9, mode='wrap'), size=21, mode='wrap'), 7, mode='wrap')
    c2 = c + nrm * (best[:, None] - 0.5)
    S = 8
    groot = np.zeros((m.shape[0] * S, m.shape[1] * S), np.uint8)
    cv2.fillPoly(groot, [np.round(c2 * S).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    return cv2.resize(groot.astype(np.float32) / 255, (m.shape[1], m.shape[0]), interpolation=cv2.INTER_AREA)


def pen_pad(punten, cx, stap=2.0):
    """Linkerhelft van de omtrek (van boven-midden linksom naar onder-midden), gespiegeld tot een gesloten, symmetrisch pad."""
    P = np.array(punten, np.float32)
    spiegel = P[::-1].copy(); spiegel[:, 0] = 2 * cx - spiegel[:, 0]
    pad = np.vstack([P, spiegel[1:-1]])
    uit = []
    for a, b in zip(pad, np.roll(pad, -1, 0)):
        n = max(1, int(np.linalg.norm(b - a) / stap))
        uit.append(a + (b - a) * np.arange(n)[:, None] / n)
    return np.vstack(uit)


def pen_masker(img, punten, cx, zoek=7, glad=5, S=8, snap=True):
    """Uitknippen zoals met het pentool: handmatig gezette punten (linkerhelft), gespiegeld, en per punt binnen +-zoek px
    vastgezet op de echte stofrand. Antialiased gevuld met S x supersampling."""
    c = pen_pad(punten, cx)
    c = uniform_filter1d(c, glad, axis=0, mode='wrap')
    if snap and zoek > 0:
        L = cv2.GaussianBlur(img.mean(-1), (0, 0), 1.0)
        t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-6
        nrm = np.stack([t[:, 1], -t[:, 0]], 1)
        # normaal naar buiten: weg van het zwaartepunt
        if ((c + nrm * 5 - c.mean(0)) ** 2).sum(1).mean() < ((c - c.mean(0)) ** 2).sum(1).mean():
            nrm = -nrm
        offs = np.arange(-zoek, zoek + 0.01, 0.5)
        P = c[:, None, :] + nrm[:, None, :] * offs[None, :, None]
        v = map_coordinates(L, [P[..., 1], P[..., 0]], order=1)
        best = offs[np.argmin(np.gradient(v, axis=1), axis=1)]
        best = uniform_filter1d(median_filter(best, size=15, mode='wrap'), 9, mode='wrap')
        # symmetrisch houden: links en rechts dezelfde correctie
        n = len(best)
        c = c + nrm * (best[:, None] - 0.5)
    groot = np.zeros((img.shape[0] * S, img.shape[1] * S), np.uint8)
    cv2.fillPoly(groot, [np.round(c * S).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    return cv2.resize(groot.astype(np.float32) / 255, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)


def symmetrisch(img, a, cx, band=200, overgang=120):
    """Rechts = gespiegelde linkerhelft (mouw, schouder, zijnaad); het midden blijft origineel zodat er geen spiegelnaad is."""
    H, W = a.shape
    xx = np.arange(W, dtype=np.float32)
    mapx = np.tile(2 * cx - xx, (H, 1)).astype(np.float32)
    mapy = np.tile(np.arange(H, dtype=np.float32)[:, None], (1, W))
    mim = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    ma = cv2.remap(a, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    rechts = (xx >= cx)[None, :]
    A = np.where(rechts, ma, a)
    w = np.clip((cx + band + overgang - xx) / overgang, 0, 1)[None, :] * rechts
    w = w * cv2.erode((a > 0.995).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
    w = cv2.GaussianBlur(w, (0, 0), 3) * rechts
    return np.where(rechts[..., None], img * w[..., None] + mim * (1 - w[..., None]), img), A


def rugkant_tshirt(img, a, cx, hals=(213, 174, 178), boord=(118, 218, 144), verschuif=215, hoek=(211, 226, 118, 205)):
    """Van een voorkant een achterkant maken: de voorste halsuitsnijding (en de boord die je daar ziet) wordt rugstof,
    de rugboord blijft. De punten van de voorboord die boven de schouder uitsteken worden weggeknipt."""
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ecy, ea, eb = hals
    tcy, ta, tb = boord
    onder = ((xx - cx) / ea) ** 2 + ((yy - ecy) / eb) ** 2 < 1
    boven = ((xx - cx) / ta) ** 2 + ((yy - tcy) / tb) ** 2 < 1
    R = cv2.GaussianBlur((onder & ~boven & (yy > ecy - 30)).astype(np.float32), (0, 0), 4)
    img = img * (1 - R[..., None]) + np.roll(img, -verschuif, axis=0) * R[..., None]
    if hoek is None:
        return img, a
    # halspunten wegknippen: bovenrand loopt vloeiend van de rugboord naar de schouder
    y0, y1, d0, d1 = hoek
    dx = np.abs(xx - cx)
    t = np.clip((dx - d0) / (d1 - d0), 0, 1)
    ymin = y0 + (y1 - y0) * t * t * (3 - 2 * t)
    knip = np.clip(yy - ymin + 0.5, 0, 1)
    zone = (dx > d0 - 30) & (dx < d1 + 10)
    A = np.where(zone, np.minimum(a, knip), a)
    # het hoekje tussen boord en schouder dichtmaken
    top = (dx > d0 - 10) & (dx < d0 + 40) & (yy < 262)
    gat = cv2.dilate((top & (knip > 0.01) & (a < 0.98)).astype(np.uint8), np.ones((5, 5), np.uint8))
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    inp = cv2.inpaint(u8, gat * 255, 6, cv2.INPAINT_TELEA).astype(np.float32) / 255
    img = np.where(gat[..., None] > 0, inp, img)
    A = np.where(top, knip, A)
    return img, A


def plooien(img, m, sterkte=1.8, fijn=1.3):
    """Witte stof heeft weinig contrast; na het omkleuren worden plooien te vlak. Versterk de lage frequenties (plooien)
    en een beetje de fijne structuur, ten opzichte van de mediane stoflichtheid."""
    L = MK.helderheid(img)
    ref = float(np.median(L[m > 0.5]))
    grof = cv2.GaussianBlur(L, (0, 0), 6)
    detail = L - grof
    L2 = ref + (grof - ref) * sterkte + detail * fijn
    f = (L2 / np.maximum(L, 1e-3))[..., None]
    return img * (1 - m[..., None]) + np.clip(img * f, 0, 1) * m[..., None]


def inkt(art, breedte, sterkte=0.05, zaad=3):
    """Zeefdrukinkt is niet egaal: een fijne korrel in de dekking (op de schaal van de stof, niet van het artwork)."""
    s = art.shape[1] / breedte                     # artworkpixels per beeldpixel
    r = np.random.default_rng(zaad).normal(0, 1, art.shape[:2]).astype(np.float32)
    r = cv2.GaussianBlur(r, (0, 0), 0.5 * s)
    r = r / (r.std() + 1e-6)
    a = art.copy()
    a[..., 3] = art[..., 3] * np.clip(1 - sterkte * np.clip(r, 0, None), 0, 1)
    return a


# ---------- t-shirt ----------
_CACHE = {}


TEE_PUNTEN = [(1240, 263), (1180, 258), (1130, 245), (1095, 225), (1080, 212), (1040, 224), (950, 262), (870, 295), (800, 346),
              (700, 410), (600, 478), (497, 547), (560, 650), (620, 745), (660, 810), (740, 800), (815, 792), (813, 900),
              (811, 1200), (811, 1490), (830, 1499), (1000, 1500), (1240, 1500)]
TEE_CX = 1240.0


def tshirt_basis():
    """Witte boxy heavyweight tee (Mr Mockup, Pexels), met het pentool uitgeknipt en symmetrisch. Coordinaten in de 2600x1733 bron."""
    if 'tee' not in _CACHE:
        img = MK.laad(FLAT / 'tshirt-wit-boxy-1.jpg')
        a = pen_masker(img, TEE_PUNTEN, TEE_CX)
        img, a = symmetrisch(img, a, TEE_CX)
        _CACHE['tee'] = (img, a, TEE_CX)
    return _CACHE['tee']


# rechterhelft van de sweater (de linkermouw ligt gevouwen over de romp), van boven-midden met de klok mee naar onder-midden
SWEAT_PUNTEN = [(1215, 196), (1300, 186), (1382, 170), (1450, 192), (1502, 198), (1648, 207), (1697, 222), (1752, 250),
                (1801, 302), (1838, 393), (1899, 491), (1942, 601), (2020, 830), (2097, 1031), (2143, 1404), (2178, 1614),
                (2160, 1640), (2073, 1649), (2011, 1638), (1999, 1544), (1957, 1482), (1856, 1311), (1793, 1249), (1782, 1257),
                (1716, 1380), (1650, 1498), (1600, 1510), (1612, 1600), (1617, 1630), (1600, 1641), (1400, 1641), (1215, 1641)]
SWEAT_CX = 1215.0


def sweater_basis():
    """Witte sweater (Mediamodifier, Unsplash): rechterhelft gespiegeld, zodat beide mouwen recht langs de romp liggen.
    Teruggegeven in het coordinatenstelsel van de gespiegelde bron (goede mouw links)."""
    if 'sweat' not in _CACHE:
        img = MK.laad(FLAT / 'sweater-wit-plat-1.jpg')
        W = img.shape[1]
        pen = pen_masker(img, SWEAT_PUNTEN, SWEAT_CX, snap=False)
        # wit kledingstuk op grijs papier en jeans: de rand komt uit de kleur, het pad begrenst en vult gaten
        L = img.mean(-1); sat = img.max(-1) - img.min(-1)
        auto = ((cv2.GaussianBlur(L, (0, 0), 1) > 0.84) & (sat < 0.07)).astype(np.uint8)
        m = (auto & (cv2.dilate((pen > 0.5).astype(np.uint8), _k(14)) > 0)) | cv2.erode((pen > 0.5).astype(np.uint8), _k(30))
        m = _vul_gaten(_grootste(cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, _k(3))))
        a = rand_vast(img, m, zoek=(-4, 4))
        img, a = img[:, ::-1].copy(), a[:, ::-1].copy()
        cx = W - 1 - SWEAT_CX
        img, a = symmetrisch(img, a, cx, band=0, overgang=50)
        _CACHE['sweat'] = (img, a, cx)
    return _CACHE['sweat']


# ---------- gedeelde stappen ----------
UIT_ECHT = HIER / 'uit_echt'
REF = ROOT / 'docs' / 'producten' / 'referentie'
LICHT_INKT = {'creme', 'baby', 'zand', 'rose', 'wit'}


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def is_donker(kleur):
    return float(hexrgb(kleur) @ np.array([0.299, 0.587, 0.114])) < 0.45


def ontwerp(naam, kleur):
    """Rugprint: -licht (navy en terracotta inkt) op lichte stof, -donker (creme inkt) op donkere stof."""
    return E.art(UIT_ECHT / f'ontwerp-{naam}-{"donker" if is_donker(kleur) else "licht"}.png')


def icoon(kleur):
    return E.art(REF / 'icoon-navy.png', CREME if is_donker(kleur) else NAVY)


def neklabel_art(kleur):
    return E.art(UIT_ECHT / ('neklabel-creme.png' if is_donker(kleur) else 'neklabel-navy.png'))


def kleur_stof(img, a, kleur, sterkte=1.8):
    m = (a > 0.5).astype(np.float32)
    img = plooien(img, m, sterkte=sterkte)
    img = MK.kleur_om(img, m, kleur, 1.0)
    if is_donker(kleur):
        # donkere stof: iets matter en een fractie lichter in de plooien, zoals geverfd katoen in zacht licht
        img = img * (1 - m[..., None]) + np.clip(img * 1.04 + 0.012, 0, 1) * m[..., None]
    return img


def druk(img, a, art, cx, cy, breedte, verplaatsing=6, dekking=0.94, structuur=0.9, korrel=0.05):
    m = cv2.erode((a > 0.5).astype(np.float32), np.ones((5, 5), np.uint8))
    return MK.zet_print(img, inkt(art, breedte, korrel), cx, cy, breedte, verplaatsing=verplaatsing, schaduw_sterkte=0.9,
                        structuur=structuur, dekking=dekking, masker=m)


def printmaat(art, breedte, max_hoogte):
    """Breedte van de print in px: de gevraagde breedte, tenzij hij dan te hoog wordt."""
    ah, aw = art.shape[:2]
    return min(breedte, max_hoogte * aw / ah)


def leg_neer(img, a, achtergrond, vulling=0.74, zaad=1, midden=None):
    rgba = ST.vrijstaand(img, a)
    rgba[..., 3] = np.clip((rgba[..., 3] - 0.5) * 1.15 + 0.5, 0, 1)    # vrijstaand blurt het masker licht; rand strak
    doek = ST.achtergrond(achtergrond, zaad=zaad)
    doek = ST.leg(doek, rgba, breedte=ST.B * vulling, midden=midden or (ST.B / 2, ST.H / 2), draai=0, hoogte=4)
    return ST.afwerking(doek)


def tricot(h, w, wale, zaad=4, amp=0.07):
    """Fijne jersey-structuur (rijen V-steekjes) voor macro's: de bronfoto is daar te grof voor."""
    rng = np.random.default_rng(zaad)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    warp = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), wale * 6)
    warp = warp / (warp.std() + 1e-6) * wale * 0.6
    u = (xx + warp) / wale
    q = wale * 0.78
    fx = u - np.floor(u)
    v = (yy + warp * 0.5) / q + np.abs(fx - 0.5) * 0.9
    fy = v - np.floor(v)
    t = np.sin(np.pi * fx) ** 0.8 * (0.62 + 0.38 * np.sin(np.pi * fy) ** 0.6)
    ci, ri = np.floor(u).astype(np.int64), np.floor(v).astype(np.int64)
    var = rng.normal(0, 1, 4096).astype(np.float32)[(ci * 131 + ri * 31) % 4096] * 0.18
    t = t + var * 0.3
    t = cv2.GaussianBlur(t, (0, 0), max(0.5, wale * 0.08))
    t = (t - t.mean()) / (t.std() + 1e-6)
    return t * amp


def macro(img, a, kader, prints, licht_hoek=True, wale_mm=0.85, kader_cm=None, maat=15.0, zaad=4, dof=3.0):
    """Close-up van de eigen compositie op hogere resolutie: het stuk stof (zonder print) wordt vergroot, krijgt echte
    breisteekjes, en de prints worden er op die resolutie opnieuw in gedrukt. Met een beetje scherptediepte."""
    x0, y0, w = kader
    h = w * ST.H / ST.B
    f = ST.B / w
    M = np.float32([[f, 0, -x0 * f], [0, f, -y0 * f]])
    groot = cv2.warpAffine(img, M, (ST.B, ST.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    ga = cv2.warpAffine(a, M, (ST.B, ST.H), flags=cv2.INTER_LINEAR, borderValue=0)
    groot = cv2.GaussianBlur(groot, (0, 0), f * 0.35)                 # vergroting is zacht; geen blokjes
    px_mm = f * maat / 10
    t = tricot(ST.H, ST.B, max(3.0, wale_mm * px_mm), zaad=zaad)
    groot = np.clip(groot * (1 + t[..., None]), 0, 1)
    for art, cx, cy, br, kw in prints:
        groot = MK.zet_print(groot, inkt(art, br * f, 0.04), (cx - x0) * f, (cy - y0) * f, br * f,
                             verplaatsing=kw.get('verplaatsing', 6) * f * 0.6, schaduw_sterkte=0.9,
                             structuur=kw.get('structuur', 1.4), dekking=kw.get('dekking', 0.93), masker=ga)
    # scherptediepte: scherp rond het midden, zacht naar boven en onder
    yy = np.mgrid[0:ST.H, 0:ST.B][0].astype(np.float32)
    d = np.clip((np.abs(yy - ST.H * 0.5) / (ST.H * 0.5) - 0.3) / 0.7, 0, 1) ** 1.4
    vaag = cv2.GaussianBlur(groot, (0, 0), dof)
    groot = groot * (1 - d[..., None]) + vaag * d[..., None]
    groot = np.clip(groot * ST._licht(), 0, 1)
    return ST.afwerking(groot, korrel=0.009)


def bewaar(img, naam):
    DOEL.mkdir(parents=True, exist_ok=True)
    ST.bewaar(img, DOEL / f'{naam}.jpg', max_kb=360)
    print('beeld', naam)


# ---------- t-shirt ----------
TEE_MAAT = 15.0                         # px per cm in de bron (romp 858 px = 57 cm, boxy heavyweight maat M)
TEE_KRAAG = 262                         # bovenkant rugboord in het midden


def tee_voor(kleur):
    img, a, cx = tshirt_basis()
    img = kleur_stof(img, a, kleur)
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # ons neklabel binnen in de rug, net onder de rugboord; de voorboord valt er deels over
    zicht = ((((xx - cx) / 132) ** 2 + ((yy - 212) / 130) ** 2) < 1) & ~((((xx - cx) / 230) ** 2 + ((yy - 26) / 279) ** 2) < 1)
    zicht = cv2.GaussianBlur(zicht.astype(np.float32), (0, 0), 1.2)
    lab = neklabel_art(kleur)
    laag = MK.zet_print(img, lab, cx, 333, 5.6 * TEE_MAAT, verplaatsing=1.5, schaduw_sterkte=0.6, structuur=0.35, dekking=0.9)
    img = img * (1 - zicht[..., None]) + laag * zicht[..., None]
    # klein board op de linkerborst (van de drager: rechts in beeld)
    ic = icoon(kleur)
    hoogte = 8.0 * TEE_MAAT
    br = hoogte * ic.shape[1] / ic.shape[0]
    img = druk(img, a, ic, cx + 9.5 * TEE_MAAT, 222 + 15 * TEE_MAAT, br, verplaatsing=3)
    return img, a, cx, [(ic, cx + 9.5 * TEE_MAAT, 222 + 15 * TEE_MAAT, br, {'verplaatsing': 3})]


def tee_rug(kleur, art):
    img, a, cx = tshirt_basis()
    img, a = rugkant_tshirt(img, a, cx, hals=(215, 172, 200), boord=(26, 230, 279), verschuif=230, hoek=None)
    W = a.shape[1]
    img, a = img[:, ::-1].copy(), a[:, ::-1].copy()      # achterkant: in spiegelbeeld neergelegd
    cx = W - 1 - cx
    img = kleur_stof(img, a, kleur)
    kaal = img.copy()
    br = printmaat(art, 25 * TEE_MAAT, 44 * TEE_MAAT)
    cy = TEE_KRAAG + 7.5 * TEE_MAAT + br * art.shape[0] / art.shape[1] / 2
    img = druk(img, a, art, cx, cy, br)
    return img, a, kaal, (art, cx, cy, br, {})


def tee(handle, kleur, naam, achtergrond):
    art = ontwerp(naam, kleur)
    v, va, cx, _ = tee_voor(kleur)
    bewaar(leg_neer(v, va, achtergrond, vulling=0.90), f'{handle}-1')
    r, ra, kaal, pr = tee_rug(kleur, art)
    bewaar(leg_neer(r, ra, achtergrond, vulling=0.80, zaad=2), f'{handle}-2')
    _, pcx, pcy, br, _ = pr
    ph = br * art.shape[0] / art.shape[1]
    w = min(br * 0.78, 22 * TEE_MAAT)                       # kader van ca. 17 tot 22 cm breed
    kader = (pcx - w / 2, pcy - ph / 2 - w * 0.08, w)
    bewaar(macro(kaal, ra, kader, [pr], maat=TEE_MAAT), f'{handle}-3')


TEES = [('t-shirt-lijn-naar-zee', CREME_T, 'lijn', 'baby'),
        ('t-shirt-op-weg-naar-zee', CREME_T, 'herhaling', 'rose'),
        ('t-shirt-klassiek', '#BCD0E6', 'boog', 'zandpapier'),
        ('t-shirt-board', '#D9C4A0', 'grootboard', 'baby'),
        ('t-shirt-zon', '#26355A', 'zon', 'zandpapier'),
        ('t-shirt-golf', '#E8B4AE', 'golf', 'creme')]


def tees(*welke):
    for handle, kleur, naam, bg in TEES:
        if not welke or handle in welke:
            tee(handle, kleur, naam, bg)


if __name__ == '__main__':
    stap, *rest = sys.argv[1:] or ['tees']
    globals()[stap](*rest)
