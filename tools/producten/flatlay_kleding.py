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


def tshirt_basis():
    """Witte flat-lay tee (mockupbee, Unsplash), uitgeknipt en symmetrisch. Coördinaten in de 2400x1600 bron."""
    if 'tee' not in _CACHE:
        img = MK.laad(FLAT / 'tshirt-wit-plat-1.jpg')
        a = masker_vlak(img)
        cx = 1191.5                                   # hart van hals en romp (gemeten op de bron)
        img, a = symmetrisch(img, a, cx)
        _CACHE['tee'] = (img, a, cx)
    return _CACHE['tee']


def tshirt_rug(kleur, print_art, breedte_frac=0.50, top_y=330):
    """Achterkant: rugboord, rugprint hoog en gecentreerd. breedte_frac = printbreedte / rompbreedte (28 cm op 56 cm)."""
    img, a, cx = tshirt_basis()
    img, a = rugkant_tshirt(img, a, cx)
    # achterkant ligt in spiegelbeeld (linkermouw rechts); eerst spiegelen, dan pas drukken
    W = a.shape[1]
    img, a = img[:, ::-1].copy(), a[:, ::-1].copy()
    cx = W - 1 - cx
    m = (a > 0.5).astype(np.float32)
    img = plooien(img, m)
    img = MK.kleur_om(img, m, kleur, 1.0)
    romp = 1565 - 827                                 # rompbreedte op borsthoogte (px in de bron)
    br = romp * breedte_frac
    ah, aw = print_art.shape[:2]
    cy = top_y + br * ah / aw / 2
    img = MK.zet_print(img, inkt(print_art, br), cx, cy, br, verplaatsing=6, schaduw_sterkte=0.9, structuur=0.9, dekking=0.94,
                       masker=cv2.erode(m, np.ones((5, 5), np.uint8)))
    return img, a


def leg_neer(img, a, achtergrond, vulling=0.74, zaad=1):
    rgba = ST.vrijstaand(img, a)
    # vrijstaand blurt het masker licht; houd de rand strak
    rgba[..., 3] = np.clip((rgba[..., 3] - 0.5) * 1.15 + 0.5, 0, 1)
    doek = ST.achtergrond(achtergrond, zaad=zaad)
    doek = ST.leg(doek, rgba, breedte=ST.B * vulling, midden=(ST.B / 2, ST.H / 2), draai=0, hoogte=4)
    return ST.afwerking(doek)


def proef():
    PROEF.mkdir(parents=True, exist_ok=True)
    img, a = tshirt_rug(CREME_T, E.art(E.ART / 'ontwerp-lijn-licht.png'))
    uit = leg_neer(img, a, 'baby')
    ST.bewaar(uit, PROEF / 'kleding-proef-1.jpg', max_kb=400)
    print('proef', PROEF / 'kleding-proef-1.jpg')


if __name__ == '__main__':
    for stap in sys.argv[1:] or ['proef']:
        globals()[stap]()
