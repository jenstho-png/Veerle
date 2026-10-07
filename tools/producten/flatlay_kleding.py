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
        a = cv2.GaussianBlur(cv2.morphologyEx((a > 0.5).astype(np.uint8), cv2.MORPH_OPEN, _k(4)).astype(np.float32), (0, 0), 0.9)
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


def kleur_stof(img, a, kleur, sterkte=1.5, fijn_donker=2.4, plooi_donker=2.2):
    m = (a > 0.5).astype(np.float32)
    if not is_donker(kleur):
        img = plooien(img, m, sterkte=sterkte)
        return MK.kleur_om(img, m, kleur, 1.0)
    # donkere stof: plooien en breiwerk zie je vooral als lichte glans op de bolle kanten, niet als donkere schaduw
    img = plooien(img, m, sterkte=plooi_donker, fijn=fijn_donker)
    L = MK.helderheid(img)
    ref = float(np.median(L[m > 0.5]))
    s = L / max(ref, 1e-3)
    doel = hexrgb(kleur)
    nieuw = doel[None, None] * np.clip(s, 0, 1.5)[..., None] ** 1.2 + 0.20 * np.clip(s - 1, 0, None)[..., None]
    nieuw = np.clip(nieuw * 1.03 + 0.008, 0, 1)
    return img * (1 - m[..., None]) + nieuw * m[..., None]


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


def macro(img, a, kader, prints, licht_hoek=True, wale_mm=0.85, kader_cm=None, maat=15.0, zaad=4, dof=3.0, achtergrond=None, brei=True):
    """Close-up van de eigen compositie op hogere resolutie: het stuk stof (zonder print) wordt vergroot, krijgt echte
    breisteekjes, en de prints worden er op die resolutie opnieuw in gedrukt. Met een beetje scherptediepte."""
    x0, y0, w = kader
    h = w * ST.H / ST.B
    f = ST.B / w
    M = np.float32([[f, 0, -x0 * f], [0, f, -y0 * f]])
    groot = cv2.warpAffine(img, M, (ST.B, ST.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    ga = cv2.warpAffine(a, M, (ST.B, ST.H), flags=cv2.INTER_CUBIC, borderValue=0)
    ga = np.clip(cv2.GaussianBlur(ga, (0, 0), f * 0.45), 0, 1)
    groot = cv2.GaussianBlur(groot, (0, 0), f * 0.35)                 # vergroting is zacht; geen blokjes
    for art, cx, cy, br, kw in prints:
        # inkt drukken op een gladde versie van de stof (alleen plooien), daarna de fijne stofstructuur gedempt terug
        glad = cv2.GaussianBlur(groot, (0, 0), f * 5)
        geprint = MK.zet_print(glad, inkt(art, br * f, 0.03), (cx - x0) * f, (cy - y0) * f, br * f,
                               verplaatsing=kw.get('verplaatsing', 6) * f * 0.2, schaduw_sterkte=0.9,
                               structuur=0.0, dekking=kw.get('dekking', 0.95), masker=ga)
        ah, aw = art.shape[:2]
        sc = br * f / aw
        Mp = cv2.getRotationMatrix2D((aw / 2, ah / 2), 0, sc)
        Mp[0, 2] += (cx - x0) * f - aw / 2; Mp[1, 2] += (cy - y0) * f - ah / 2
        pa = cv2.warpAffine(art[..., 3], Mp, (ST.B, ST.H), flags=cv2.INTER_LINEAR)[..., None]
        groot = geprint + (groot - glad) * (1 - 0.75 * pa)
    # breisteekjes over stof en inkt samen: de inkt zit in de stof
    px_mm = f * maat / 10
    t = tricot(ST.H, ST.B, max(3.0, wale_mm * px_mm), zaad=zaad, amp=0.035) if brei else np.zeros((ST.H, ST.B), np.float32)
    ruis = cv2.GaussianBlur(np.random.default_rng(zaad + 1).normal(0, 1, (ST.H, ST.B)).astype(np.float32), (0, 0), 1.2)
    t = t + ruis / (ruis.std() + 1e-6) * 0.012
    groot = np.clip(groot * (1 + t[..., None]), 0, 1)
    if achtergrond is not None:
        # de rand van het kledingstuk ligt in beeld: op dezelfde ondergrond, met contactschaduw naar rechtsonder
        doek = ST.achtergrond(achtergrond, zaad=3)
        sch = cv2.GaussianBlur(np.roll(np.roll(ga, int(f * 5), 0), int(f * 4), 1), (0, 0), f * 6)
        doek = doek * (1 - 0.30 * sch[..., None]) / ST._licht()
        groot = doek * (1 - ga[..., None]) + groot * ga[..., None]
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


# waar de macro op de print inzoomt (0 = bovenkant print, 1 = onderkant)
MACRO_FOCUS = {'grootboard': 0.32, 'vin': 0.25}


def tee(handle, kleur, naam, achtergrond):
    art = ontwerp(naam, kleur)
    v, va, cx, _ = tee_voor(kleur)
    bewaar(leg_neer(v, va, achtergrond, vulling=0.90), f'{handle}-1')
    r, ra, kaal, pr = tee_rug(kleur, art)
    bewaar(leg_neer(r, ra, achtergrond, vulling=0.80, zaad=2), f'{handle}-2')
    _, pcx, pcy, br, _ = pr
    ph = br * art.shape[0] / art.shape[1]
    w = br * 1.12                                           # hele printbreedte, bovenste deel
    focus = MACRO_FOCUS.get(naam, 0.0)
    kader = (pcx - w / 2, pcy - ph / 2 + focus * ph - w * 0.10, w)
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



def product(handle, voor, rug, achtergrond, macro_kader, macro_prints, maat, vulling=(0.90, 0.80), macro_img=None, macro_bg=False, brei=True):
    """Drie beelden per product: -1 voorkant groot, -2 achterkant, -3 macro."""
    (v, va), (r, ra) = voor, rug
    bewaar(leg_neer(v, va, achtergrond, vulling=vulling[0]), f'{handle}-1')
    bewaar(leg_neer(r, ra, achtergrond, vulling=vulling[1], zaad=2), f'{handle}-2')
    mi, ma = macro_img
    bewaar(macro(mi, ma, macro_kader, macro_prints, maat=maat, achtergrond=achtergrond if macro_bg else None, brei=brei), f'{handle}-3')


def rugprint_macro_kader(pr, art, naam, maat_breed=1.12):
    _, pcx, pcy, br, _ = pr
    ph = br * art.shape[0] / art.shape[1]
    w = br * maat_breed
    focus = MACRO_FOCUS.get(naam, 0.0)
    return (pcx - w / 2, pcy - ph / 2 + focus * ph - w * 0.10, w)


# ---------- sweater (en daarvan afgeleid: longsleeve en uv-shirt) ----------
SW_MAAT = 18.5                          # px per cm (romp 1095 px = 59 cm)
SW_KRAAG = 198                          # bovenkant rugboord in het midden
SW_ROMP = (637, 1732)                   # zijnaden onder de oksel (gespiegelde bron)


def neklabel_in(img, kleur, cx, cy, breedte, zicht):
    zicht = cv2.GaussianBlur(zicht.astype(np.float32), (0, 0), 1.2)
    laag = MK.zet_print(img, neklabel_art(kleur), cx, cy, breedte, verplaatsing=1.5, schaduw_sterkte=0.6, structuur=0.35, dekking=0.9)
    return img * (1 - zicht[..., None]) + laag * zicht[..., None]


def sweater_voorkant(img, a, cx, kleur, label_y=318):
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    zicht = ((((xx - cx) / 185) ** 2 + ((yy - 200) / 135) ** 2) < 1) & ~((((xx - cx) / 354) ** 2 + (yy / 290) ** 2) < 1)
    img = neklabel_in(img, kleur, cx, label_y, 5.0 * SW_MAAT, zicht)
    ic = icoon(kleur)
    hoogte = 8.0 * SW_MAAT
    br = hoogte * ic.shape[1] / ic.shape[0]
    pos = (cx + 10 * SW_MAAT, SW_KRAAG + 17 * SW_MAAT)
    return druk(img, a, ic, pos[0], pos[1], br, verplaatsing=3), (ic, pos[0], pos[1], br, {'verplaatsing': 3})


def sweater_rugkant(img, a, cx):
    img, a = rugkant_tshirt(img, a, cx, hals=(178, 268, 240), boord=(0, 420, 268), verschuif=330, hoek=None)
    W = a.shape[1]
    return img[:, ::-1].copy(), a[:, ::-1].copy(), W - 1 - cx


def rugprint(img, a, cx, art, maat, kraag, breedte_cm=25, max_cm=40, onder_kraag_cm=10.0, structuur=0.9):
    br = printmaat(art, breedte_cm * maat, max_cm * maat)
    cy = kraag + onder_kraag_cm * maat + br * art.shape[0] / art.shape[1] / 2
    return druk(img, a, art, cx, cy, br, structuur=structuur), (art, cx, cy, br, {})


def longsleeve_basis(smal=1.0):
    """Longsleeve uit de sweater: mouwen en manchetten blijven, de gerimpelde boord gaat eraf; de romp loopt recht door
    tot een gewone zoom met dubbel stiksel. smal < 1 maakt hem nauwer (uv-shirt)."""
    key = ('ls', smal)
    if key in _CACHE:
        return _CACHE[key]
    img, a, cx = sweater_basis()
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    y_knip, y_zoom = 1190.0, 1600.0
    xl, xr = SW_ROMP
    kolom = (xx >= xl) & (xx <= xr)
    romp = np.zeros((H * 4, W * 4), np.uint8)
    cv2.rectangle(romp, (int(xl * 4), int((y_knip - 40) * 4)), (int(xr * 4), int(y_zoom * 4)), 255, -1)
    romp = cv2.GaussianBlur(cv2.resize(romp.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA), (0, 0), 0.7)
    # nieuwe onderkant van de romp, met stof uit de buik (iets samengedrukt zodat er geen mouwrand in zit)
    mapx = (cx + (xx - cx) * 0.66).astype(np.float32)
    mapy = (yy - 290).astype(np.float32)
    bron = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    w = np.clip((yy - y_knip) / 90, 0, 1) * kolom
    w = np.maximum(w, (romp > 0.01) & (a < 0.97))         # ook de hoekjes waar eerst ondergrond zat
    w = cv2.GaussianBlur(w.astype(np.float32), (0, 0), 3)
    img = img * (1 - w[..., None]) + bron * w[..., None]
    # zoom: dubbel stiksel 2,2 cm boven de onderrand, de omgeslagen rand iets lichter, onderrand iets donkerder
    st = y_zoom - 2.2 * SW_MAAT
    steek = (np.exp(-((yy - st) / 1.1) ** 2) + np.exp(-((yy - st - 9) / 1.1) ** 2)) * (np.sin(xx * 0.55) > -0.4)
    zoom = np.clip((yy - st) / 6, 0, 1) * (yy <= y_zoom)
    rand = np.exp(-((y_zoom - yy) / 5) ** 2)
    f = (1 - 0.10 * steek + 0.025 * zoom - 0.10 * rand) * (yy > y_knip)
    f = np.where(kolom & (yy > y_knip), f, 1.0)
    img = img * f[..., None]
    oud = np.where(kolom & (yy > y_knip - 40), 0, a)
    a = np.maximum(oud, romp)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, _k(4))              # geen haarlijn tussen mouw en nieuwe romp
    if smal != 1.0:
        M = np.float32([[smal, 0, cx * (1 - smal)], [0, 1, 0]])
        img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        a = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_AREA)
    _CACHE[key] = (img, a, cx)
    return _CACHE[key]


def sweater(handle, kleur, naam, achtergrond):
    img, a, cx = sweater_basis()
    art = ontwerp(naam, kleur)
    v = kleur_stof(img, a, kleur)
    v, _ = sweater_voorkant(v, a, cx, kleur)
    r, ra, rcx = sweater_rugkant(img, a, cx)
    r = kaal = kleur_stof(r, ra, kleur)
    r, pr = rugprint(r, ra, rcx, art, SW_MAAT, SW_KRAAG)
    product(handle, (v, a), (r, ra), achtergrond, rugprint_macro_kader(pr, art, naam), [pr], SW_MAAT, macro_img=(kaal, ra))


def longsleeve(handle, kleur, naam, achtergrond):
    img, a, cx = longsleeve_basis()
    art = ontwerp(naam, kleur)
    v = kleur_stof(img, a, kleur)
    v, _ = sweater_voorkant(v, a, cx, kleur)
    r, ra, rcx = sweater_rugkant(img, a, cx)
    r = kaal = kleur_stof(r, ra, kleur)
    r, pr = rugprint(r, ra, rcx, art, SW_MAAT, SW_KRAAG)
    product(handle, (v, a), (r, ra), achtergrond, rugprint_macro_kader(pr, art, naam), [pr], SW_MAAT, macro_img=(kaal, ra))


def tegelband(h, w, tegel_px, dx=0, dy=0):
    """Het merk-tegelpatroon (docs/producten/referentie/tegelprint.png, 6 x 6 tegels) als vlak, tegel_px per tegel."""
    t = MK.laad(REF / 'tegelprint.png')
    s = tegel_px * 6 / t.shape[1]
    t = cv2.resize(t, (int(round(t.shape[1] * s)), int(round(t.shape[0] * s))), interpolation=cv2.INTER_AREA)
    reps = (h // t.shape[0] + 2, w // t.shape[1] + 2)
    return np.roll(np.tile(t, (reps[0], reps[1], 1)), (dy, dx), (0, 1))[:h, :w]


def uv_shirt():
    handle, kleur, achtergrond = 'uv-shirt-lange-mouw', '#26355A', 'baby'
    smal = 0.86
    img, a, cx = longsleeve_basis(smal)
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = kleur_stof(img, a, kleur)
    # tegelband op beide manchetten: alles onder de manchetnaad (links gemeten, rechts gespiegeld), mee versmald
    def manchet(x):
        xs = cx + (x - cx) / smal                        # terug naar de bron-x
        xs = np.where(xs > cx, 2 * cx - xs, xs)
        y_naad = 1460 + (xs - 250) / 150 * 37
        return (yy > y_naad) & (xs < 430) & (yy > 1400)
    band = (manchet(xx) & (a > 0.5)).astype(np.float32)
    band = cv2.GaussianBlur(band, (0, 0), 1.0)
    L = MK.helderheid(v)
    ref = float(np.median(L[band > 0.5])) if (band > 0.5).any() else 0.2
    tegels = tegelband(H, W, int(3.2 * SW_MAAT), dx=int(cx) % int(3.2 * SW_MAAT))
    sch = np.clip(L / max(ref, 1e-3), 0.6, 1.3)[..., None]
    fijn = (L - cv2.GaussianBlur(L, (0, 0), 1.5))[..., None]
    print_band = np.clip(tegels * 0.94 * sch + fijn * 0.8, 0, 1)
    v = v * (1 - band[..., None]) + print_band * band[..., None]
    kaal_manchet = v.copy()
    v, ic = sweater_voorkant(v, a, cx, kleur)
    # achterkant: effen, klein logo in de nek
    r, ra, rcx = sweater_rugkant(img, a, cx)
    r = kleur_stof(r, ra, kleur)
    band_r = band[:, ::-1]
    r = r * (1 - band_r[..., None]) + print_band[:, ::-1] * band_r[..., None]
    logo = E.art(REF / 'logo-navy.png', CREME)
    lb = 7 * SW_MAAT * smal
    r = druk(r, ra, logo, rcx, SW_KRAAG + 6.5 * SW_MAAT + lb * logo.shape[0] / logo.shape[1] / 2, lb, verplaatsing=2)
    # macro: manchet met de tegelband, linkermouw
    kader_w = 300
    mx = cx + (330 - cx) * smal                        # midden van de linkermanchet, na versmallen
    kader = (mx - kader_w / 2, 1530 - kader_w * 1.25 / 2, kader_w)
    product(handle, (v, a), (r, ra), achtergrond, kader, [], SW_MAAT, macro_img=(kaal_manchet, a), macro_bg=True)


# ---------- hoodie ----------
# rechterhelft van de blauwe hoodie (philippe wehrli, Unsplash), van boven-midden met de klok mee naar onder-midden
HOOD_PUNTEN = [(1350, 838), (1420, 842), (1480, 850), (1540, 862), (1580, 880), (1600, 905), (1615, 950), (1625, 1000),
               (1640, 1050), (1645, 1100), (1650, 1150), (1655, 1200), (1662, 1250), (1690, 1290), (1750, 1312), (1850, 1350),
               (1950, 1390), (2030, 1440), (2055, 1475), (2100, 1560), (2150, 1650), (2200, 1740), (2250, 1830), (2290, 1900),
               (2302, 1935), (2265, 1980), (2200, 2055), (2140, 2125), (2085, 2190), (2050, 2240), (2045, 2300), (2040, 2400),
               (2025, 2452), (1995, 2470), (1992, 2600), (1985, 2636), (1940, 2638), (1700, 2638), (1350, 2638)]
HOOD_CX = 1350.0
HOOD_MAAT = 22.4                         # px per cm (romp 1390 px = 62 cm)


def hoodie_basis():
    """Blauwe hoodie: de schoenen over de zoom weg (zoomboord en buik aangevuld met stof van de hoodie zelf),
    rechterhelft gespiegeld. Teruggegeven in het stelsel van de gespiegelde bron."""
    if 'hood' in _CACHE:
        return _CACHE['hood']
    img = MK.laad(FLAT / 'hoodie-blauw-plat-1.jpg')
    # de foto is korrelig (hoge iso): eerst ontruisen, anders wordt de korrel bij het omkleuren vlekkerig
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    img = cv2.fastNlMeansDenoisingColored(u8, None, 7, 7, 7, 21).astype(np.float32) / 255
    H, W = img.shape[:2]
    cx = HOOD_CX
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # buik onder de schoen: stof van 200 px hoger
    buik = ((xx >= cx - 40) & (xx < 1800) & (yy >= 2340) & (yy < 2452)).astype(np.float32)
    buik = cv2.GaussianBlur(buik, (0, 0), 4)
    img = img * (1 - buik[..., None]) + np.roll(img, 300, axis=0) * buik[..., None]
    # zoomboord opnieuw opbouwen, recht: boordkleur van de zichtbare rib, met fijne verticale ribbels,
    # een naadschaduw bovenaan en de omslag onderaan iets donkerder
    basis = np.median(img[2485:2595, 1820:1900].reshape(-1, 3), axis=0)
    romp = np.median(img[1700:2200, 1450:1900].reshape(-1, 3), axis=0)
    basis = basis * (0.93 * romp.mean() / max(basis.mean(), 1e-3))
    y_b0, y_b1 = 2440, 2670
    x0 = int(cx) - 60
    bh, bw = y_b1 - y_b0, 2010 - x0
    by, bx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    rng = np.random.default_rng(11)
    streep = cv2.GaussianBlur(rng.normal(0, 1, (1, bw)).astype(np.float32), (0, 0), 1.0)
    ruis = cv2.GaussianBlur(rng.normal(0, 1, (bh, bw)).astype(np.float32), (0, 0), 0.8)
    t = by / (2640 - y_b0)
    rib = (1 + 0.07 * np.sin(2 * np.pi * bx / 7.5) + 0.03 * streep / (streep.std() + 1e-6) + 0.025 * ruis
           - 0.25 * np.exp(-(t / 0.05) ** 2) - 0.14 * np.clip((t - 0.86) / 0.14, 0, 1))
    vlak = basis[None, None] * rib[..., None]
    boord = img.copy()
    boord[y_b0:y_b1, x0:2010] = vlak
    bm = ((xx >= x0) & (xx < 2010) & (yy >= y_b0) & (yy < y_b1)).astype(np.float32)
    bm = cv2.GaussianBlur(bm, (0, 0), 1.5)
    img = img * (1 - bm[..., None]) + boord * bm[..., None]
    a = np.where(yy > 2560, pen_masker(img, HOOD_PUNTEN, cx, snap=False), pen_masker(img, HOOD_PUNTEN, cx, zoek=6))
    img, a = img[:, ::-1].copy(), a[:, ::-1].copy()
    cx = W - 1 - cx
    img, a = symmetrisch(img, a, cx, band=0, overgang=40)
    # garment-dyed vlekken (schaal 10 tot 60 px) eruit: grote plooien en scherpe naden/vouwen blijven
    L = MK.helderheid(img)
    m = (a > 0.5).astype(np.float32)
    ref = float(np.median(L[m > 0.5]))
    grof = cv2.GaussianBlur(L, (0, 0), 60)
    scherp = L - cv2.GaussianBlur(L, (0, 0), 6)
    L2 = grof + scherp * 1.2
    img = img * np.clip(L2 / np.maximum(L, 1e-3), 0.5, 1.8)[..., None] * m[..., None] + img * (1 - m[..., None])
    _CACHE['hood'] = (img, a, cx)
    return _CACHE['hood']


def hoodie_rug(img, a, cx):
    """Achterkant: kap plat met de buitenkant boven, middennaad over de kap, geen buidelzak."""
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # binnenkant van de kap (donker) wordt buitenstof: stof van de borst, op de lichtheid van de kapzijkant
    kap = ((((xx - cx) / 255) ** 2 + ((yy - 1080) / 235) ** 2) < 1) | ((np.abs(xx - cx) < 120) & (yy > 1080) & (yy < 1330))
    kap = cv2.GaussianBlur(kap.astype(np.float32), (0, 0), 10)
    bron = np.roll(img, -600, axis=0)
    L = MK.helderheid(img)
    ref_kap = float(np.median(L[880:1250, int(cx) + 260:int(cx) + 290]))
    ref_bron = float(np.median(L[1500:1800, int(cx) - 200:int(cx) + 200]))
    bron = bron * (0.5 * (ref_kap + ref_bron) / max(ref_bron, 1e-3))
    img = img * (1 - kap[..., None]) + bron * kap[..., None]
    # middennaad over de kap
    naad = np.exp(-((xx - cx) / 2.2) ** 2) * (yy > 850) * (yy < 1320)
    img = img * (1 - 0.18 * naad[..., None])
    # buidelzak weg: stof van boven
    zak = ((np.abs(xx - cx) < 430) & (yy > 1890) & (yy < 2446)).astype(np.float32)
    zak = cv2.GaussianBlur(zak, (0, 0), 8)
    spiegel = cv2.remap(img, xx, (2 * 1880 - yy).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    img = img * (1 - zak[..., None]) + spiegel * zak[..., None]
    img, a = img[:, ::-1].copy(), a[:, ::-1].copy()
    return img, a, W - 1 - cx


def hoodie(handle, kleur, naam, achtergrond):
    img, a, cx = hoodie_basis()
    art = ontwerp(naam, kleur)
    v = kleur_stof(img, a, kleur, fijn_donker=1.3, plooi_donker=1.5)
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # ons label binnen in de kap, achter in de nek
    zicht = ((((xx - cx) / 160) ** 2 + ((yy - 1180) / 120) ** 2) < 1)
    v = neklabel_in(v, kleur, cx, 1215, 5.0 * HOOD_MAAT, zicht)
    ic = icoon(kleur)
    hoogte = 8.0 * HOOD_MAAT
    br = hoogte * ic.shape[1] / ic.shape[0]
    v = druk(v, a, ic, cx + 10 * HOOD_MAAT, 1500 + 7 * HOOD_MAAT, br, verplaatsing=3, structuur=0.3)
    r, ra, rcx = hoodie_rug(img, a, cx)
    r = kaal = kleur_stof(r, ra, kleur, fijn_donker=1.3, plooi_donker=1.5)
    r, pr = rugprint(r, ra, rcx, art, HOOD_MAAT, 1360, breedte_cm=26, max_cm=38, onder_kraag_cm=7, structuur=0.3)
    product(handle, (v, a), (r, ra), achtergrond, rugprint_macro_kader(pr, art, naam), [pr], HOOD_MAAT, macro_img=(kaal, ra),
            vulling=(0.84, 0.78))


def hoodies():
    hoodie('hoodie-twee-boards', '#26355A', 'tweeboards', 'rose')


# ---------- surfponcho (badstof) ----------
PO_MAAT = 20.0                           # px per cm op het werkdoek
PO_B, PO_H = 2600, 3000
PO_CX, PO_NEK = 1300.0, 900.0


def badstof(h, w, schaal=0.75, zaad=5):
    """Echte badstof (lusjes) uit docs/producten/stock/handdoek-1.jpg, met patch-quilting tot een naadloos vlak.
    Geeft de relatieve lichtheid terug (gemiddeld 1)."""
    if ('badstof', h, w) in _CACHE:
        return _CACHE[('badstof', h, w)]
    bron = MK.laad(ROOT / 'docs' / 'producten' / 'stock' / 'handdoek-1.jpg')[720:900, 560:1100]
    L = MK.helderheid(bron)
    L = L / cv2.GaussianBlur(L, (0, 0), 18)                  # alleen de lusjes, geen licht of vouw
    L = cv2.resize(L, (int(L.shape[1] * schaal), int(L.shape[0] * schaal)), interpolation=cv2.INTER_AREA)
    rng = np.random.default_rng(zaad)
    P, O = 96, 28                                             # patch en overlap
    st = P - O
    uit = np.zeros((h + P, w + P), np.float32)
    gew = np.zeros_like(uit)
    ramp = np.minimum(np.minimum(np.arange(P) + 1, P - np.arange(P)) / O, 1).astype(np.float32)
    venster = np.outer(ramp, ramp)
    for y in range(0, h + 1, st):
        for x in range(0, w + 1, st):
            py, px = rng.integers(0, L.shape[0] - P), rng.integers(0, L.shape[1] - P)
            stuk = L[py:py + P, px:px + P]
            if rng.random() < 0.5:
                stuk = stuk[:, ::-1]
            uit[y:y + P, x:x + P] += stuk * venster
            gew[y:y + P, x:x + P] += venster
    uit = (uit / np.maximum(gew, 1e-6))[:h, :w]
    # overlap middelt het contrast weg: terug op het contrast van de bron
    uit = 1 + (uit - uit.mean()) * (L.std() / max(uit.std(), 1e-6))
    _CACHE[('badstof', h, w)] = uit.astype(np.float32)
    return _CACHE[('badstof', h, w)]


def poncho_vorm(kap_boven):
    """Silhouet (cm, oorsprong midden van de hals): T-vorm met korte brede mouwen, capuchon boven."""
    S, cx, y0 = PO_MAAT, PO_CX, PO_NEK
    def p(x, y):
        return (cx + x * S, y0 + y * S)
    rechts = [p(14, 0), p(30, 3), p(54, 7), p(56, 9), p(56.5, 34), p(55, 36.5), p(40, 38), p(37.5, 41), p(37.5, 60),
              p(38, 88), p(37, 90.5), p(0, 90.6)]
    links = [(2 * cx - x, y) for x, y in rechts[::-1]][1:]
    rand = rechts + links[:-1]
    kap = [p(-14, 0)] + [p(19.5 * np.sin(t), -16 - 16.5 * np.cos(t) if kap_boven else -16 - 16.5 * np.cos(t)) for t in np.linspace(-np.pi * 0.62, np.pi * 0.62, 40)] + [p(14, 0)]
    pad = np.array(rand + kap[::-1], np.float32) if False else np.array([p(14, 0)] + rechts[1:] + links[:-1] + kap[1:-1][::-1][::-1], np.float32)
    return pad


def poncho_alpha():
    S = 4
    groot = np.zeros((PO_H * S, PO_B * S), np.uint8)
    cv2.fillPoly(groot, [np.round(poncho_vorm(True) * S).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    a = cv2.resize(groot.astype(np.float32) / 255, (PO_B, PO_H), interpolation=cv2.INTER_AREA)
    return a


def poncho(handle='surfponcho-tegel', kleur='#5E7F9C', achtergrond='zand'):
    H, W, S, cx, y0 = PO_H, PO_B, PO_MAAT, PO_CX, PO_NEK
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    X, Y = (xx - cx) / S, (yy - y0) / S                       # cm
    a = poncho_alpha()
    rng = np.random.default_rng(21)
    # plooien: lage ruis + een paar zachte verticale valplooien in de romp en schuine in de mouwen
    laag = cv2.GaussianBlur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), (0, 0), 6)
    laag = cv2.resize(laag / (laag.std() + 1e-6), (W, H), interpolation=cv2.INTER_CUBIC)
    plooi = np.zeros((H, W), np.float32)
    for xc, br, d in [(-24, 3.5, 0.06), (-9, 2.5, 0.05), (7, 3.0, 0.05), (22, 4.0, 0.06), (31, 2.0, 0.04)]:
        golf = np.exp(-((X - xc - 1.5 * np.sin(Y / 9)) / br) ** 2) * np.clip((Y - 30) / 25, 0, 1)
        plooi += d * (golf - 0.6 * np.exp(-((X - xc - br - 1.5 * np.sin(Y / 9)) / br) ** 2) * np.clip((Y - 30) / 25, 0, 1))
    plooi = plooi + plooi[:, ::-1] * 0.0
    mouw = (np.abs(X) > 38) & (Y > 0) & (Y < 40)
    plooi += 0.05 * np.sin((np.abs(X) * 0.6 + Y) / 3.2) * np.exp(-((np.abs(X) - 47) / 6) ** 2) * mouw
    licht = 1 + 0.035 * laag + plooi
    # randen: omgezoomde bies (1,2 cm) met stiksel, en iets donker waar de dikke stof afrondt
    rand_d = cv2.distanceTransform((a > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / S          # cm tot de rand
    bies = np.clip(1 - rand_d / 1.2, 0, 1)
    stiksel = np.exp(-((rand_d - 1.25) / 0.06) ** 2) * (np.sin((xx + yy) * 0.9) > -0.2)
    licht = licht * (1 - 0.10 * np.exp(-rand_d / 0.35)) * (1 + 0.04 * bies) * (1 - 0.12 * stiksel)
    terry = badstof(H, W)
    terry = 1 + (terry - 1) * 0.9
    basis = hexrgb(kleur)
    stof = basis[None, None] * (licht * terry)[..., None]
    # tegelband aan de zoom (12 cm), ingeweven/gedrukt op de badstof: kleur van de tegels, licht en lusjes van de stof
    band = ((Y > 77.5) & (Y < 89.3)).astype(np.float32) * (np.abs(X) < 36.3)
    band = cv2.GaussianBlur(band, (0, 0), 1.0)
    tegels = tegelband(H, W, int(5.9 * S), dx=int(cx) % int(5.9 * S), dy=int(y0 + 77.5 * S) % int(5.9 * S))
    tegelstof = tegels * (licht * (1 + (terry - 1) * 1.2))[..., None] * 0.95
    stof = stof * (1 - band[..., None]) + tegelstof * band[..., None]
    # naad boven de band
    stof = stof * (1 - 0.15 * np.exp(-((Y - 77.4) / 0.12) ** 2) * (np.abs(X) < 37))[..., None]
    stof = np.clip(stof, 0, 1).astype(np.float32)

    def kap_schaduw(img, binnen):
        # capuchon: dubbele laag, iets schaduw waar hij op de schouders ligt
        rand_kap = np.exp(-((Y - 0.3) / 0.6) ** 2) * (np.abs(X) < 14)
        return img * (1 - 0.18 * rand_kap)[..., None]

    # voorkant: halsopening (rond, 11 cm diep) met de binnenkant van de kap erachter, buidelzak met stiksels, ons label
    voor = stof.copy()
    hals = (X / 12.5) ** 2 + (Y / 10.5) ** 2 < 1
    binnenkap = ((X / 17.5) ** 2 + ((Y + 14) / 15) ** 2 < 1) | hals
    binnen = binnenkap & (Y > -27)
    schaduw_binnen = np.clip(0.55 + 0.35 * ((Y + 27) / 37), 0.45, 0.9)
    bm = cv2.GaussianBlur((binnen & ((X / 13.5) ** 2 + ((Y + 12) / 13.5) ** 2 < 1)).astype(np.float32), (0, 0), 3)
    voor = voor * (1 - bm[..., None] * (1 - schaduw_binnen[..., None]))
    # kaprand (bies) rond de opening
    kr = ((X / 13.5) ** 2 + ((Y + 12) / 13.5) ** 2)
    kaprand = np.exp(-((np.sqrt(kr) - 1) / 0.05) ** 2) * (Y < 10.5)
    voor = voor * (1 + 0.10 * kaprand[..., None]) * (1 - 0.15 * np.exp(-((np.sqrt(kr) - 1.07) / 0.03) ** 2))[..., None]
    zak = (np.abs(X) < 21) & (Y > 50) & (Y < 70)
    zakrand = np.exp(-((np.abs(X) - 21) / 0.15) ** 2) * (Y > 50) * (Y < 70) + np.exp(-((Y - 50) / 0.15) ** 2) * (np.abs(X) < 21)
    zakst = (np.exp(-((np.abs(X) - 20.3) / 0.05) ** 2) * (Y > 50.6) * (Y < 70) +
             np.exp(-((Y - 50.7) / 0.05) ** 2) * (np.abs(X) < 20.3)) * (np.sin((xx + yy) * 0.9) > -0.2)
    voor = voor * (1 - 0.22 * zakrand - 0.12 * zakst)[..., None] * (1 + 0.03 * zak)[..., None]
    voor = neklabel_in(voor.astype(np.float32), NAVY, cx, y0 + 4 * S, 5.5 * S, binnen & (Y > 0) & (Y < 9))
    # achterkant: kap plat naar boven met middennaad, groot creme logo op de rug
    rug = kap_schaduw(stof.copy(), None).astype(np.float32)
    kapnaad = np.exp(-(X / 0.08) ** 2) * (Y < -0.5) * (Y > -32)
    rug = rug * (1 - 0.18 * kapnaad)[..., None]
    logo = E.art(REF / 'logo-navy.png', CREME)
    lb = 34 * S
    ly = y0 + 9 * S + lb * logo.shape[0] / logo.shape[1] / 2
    kaal = rug.copy()
    rug = druk(rug, a, logo, cx, ly, lb, verplaatsing=4, structuur=1.4, dekking=0.92)
    # macro: hoek van de zoom met tegelband en badstof
    kader_w = 32 * S
    kader = (cx + 22 * S - kader_w / 2, y0 + 82 * S - kader_w * 1.25 * 0.55, kader_w)
    product(handle, (voor, a), (rug, a), achtergrond, kader, [], S, vulling=(0.84, 0.80), macro_img=(kaal, a),
            macro_bg=True, brei=False)


def sweaters():
    sweater('sweater-boards', CREME_T, 'tweeboardslos', 'zand')


def longsleeves():
    longsleeve('longsleeve-vin', '#26355A', 'vin', 'zand')
    longsleeve('longsleeve-zon', CREME_T, 'zon', 'baby')


if __name__ == '__main__':
    stap, *rest = sys.argv[1:] or ['tees']
    globals()[stap](*rest)
