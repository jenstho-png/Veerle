"""Sfeerbeelden met de tas op echte boards uit stockfoto's (docs/producten/stock/lifestyle).

Per foto: neus, staart (of midden) en breedte van het board uit bronnen.json. Daaruit volgt de omtrek van het board,
het balanspunt (midden) waar de tas zit, en de kant waar de lus uit komt:
- staat het board (rechtop of schuin): de lus hangt met de zwaartekracht naar beneden;
- ligt het board plat (van bovenaf gefotografeerd): de lus ligt plat naast het board.
"""
import json, math, pathlib, sys
import cv2
import numpy as np
from PIL import Image
from scipy.interpolate import PchipInterpolator

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import lifestyle as LS  # noqa: E402
import scene as SC  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock' / 'lifestyle'
UIT = ROOT / 'docs' / 'producten' / 'fotos'
UIT.mkdir(parents=True, exist_ok=True)
BRON = {p['file']: p for p in json.load(open(STOCK / 'bronnen.json'))['photos']}


def omtrek(neus, staart, breedte, lengte_factor=None):
    """Polygoon van het board in de foto (neus spits, staart iets breder afgesneden)."""
    u = staart - neus; L = np.linalg.norm(u); u /= L
    n = np.array([-u[1], u[0]])
    t = np.array([0, .02, .06, .14, .28, .45, .6, .75, .88, .96, 1.0])
    f = np.array([0, .3, .55, .76, .92, 1.0, 1.0, .94, .78, .55, .4])
    spl = PchipInterpolator(t, f)
    ts = np.linspace(0, 1, 160)
    links = [neus + u * L * x + n * breedte / 2 * spl(x) for x in ts]
    rechts = [neus + u * L * x - n * breedte / 2 * spl(x) for x in ts][::-1]
    return np.array(links + rechts, np.float32)


def stof_voor(handle):
    if handle == 'draagtas-tegel':
        return None
    return SC.variant_stof(handle)


def plat_lus(foto, M, W, H, boardbreedte, kleur, breedte):
    """Lus die plat naast een liggend board ligt (zoals in de studiofoto)."""
    xm = W / 2; tg = H / 5.5
    def pt(x, y):
        return cv2.perspectiveTransform(np.float32([[[x, y]]]), M)[0, 0]
    l0, l1 = pt(xm - 3.15 * tg * 0.95, H * 0.8), pt(xm - 1.99 * tg, H)
    r0, r1 = pt(xm + 3.15 * tg * 0.95, H * 0.8), pt(xm + 1.99 * tg, H)
    top = pt(xm, H + 3.35 * tg * 115 / 98)
    rl = pt(xm - 0.9 * tg, H + 3.0 * tg * 115 / 98); rr = pt(xm + 0.9 * tg, H + 3.0 * tg * 115 / 98)
    pad = LS.catmull([l0, l1, rl, top, rr, r1, r0], n=80)
    return LS.band_laag(foto.shape[:2], pad, breedte, kleur)


def maak(bestand, handle, naam, kant=1, plat=False, lengte_ratio=3.4, licht=1.0, verzadiging=0.85, armen=False):
    info = BRON[bestand]['board']
    foto = np.asarray(Image.open(STOCK / bestand).convert('RGB')).astype(np.float32) / 255
    neus = np.array(info['nose_tip'], np.float32)
    breedte = float(info['width_at_middle_px'])
    if info.get('tail_tip'):
        staart = np.array(info['tail_tip'], np.float32)
        midden = (neus + staart) / 2
    else:
        midden = np.array(info['middle_point'], np.float32)
        staart = neus + (midden - neus) * 2
    u = (neus - midden); u /= np.linalg.norm(u)          # naar de neus
    n = np.array([-u[1], u[0]]) * kant                   # dwars; -n is de kant van de lus
    half_b = breedte / 2 * 0.98
    half_l = 4.48 * (2 * half_b) / 5.5
    c = midden
    quad = [c - u * half_l + n * half_b, c + u * half_l + n * half_b, c + u * half_l - n * half_b, c - u * half_l - n * half_b]
    # boardmasker uit de omtrek
    bm = np.zeros(foto.shape[:2], np.uint8)
    cv2.fillPoly(bm, [np.round(omtrek(neus, staart, breedte)).astype(np.int32)], 1)
    if armen:
        hsv = cv2.cvtColor((foto * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
        huid = ((hsv[..., 0] < 25) & (hsv[..., 1] > 70) & (hsv[..., 2] > 60)).astype(np.uint8)
        huid = cv2.morphologyEx(huid, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        bm = bm * (1 - cv2.dilate(huid, np.ones((5, 5), np.uint8)))
    bm = cv2.GaussianBlur(bm.astype(np.float32), (0, 0), 1.2)
    kleur = SC.hexkleur(SC.TASSEN[handle])
    kleur = tuple(k * 0.9 for k in kleur)
    rgba = LS.huid(half_l * 2, half_b * 2, kort=0.54, band_kleur=kleur, stof=stof_voor(handle), zaad=hash(naam) % 50)
    H, W = rgba.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [W, 0], [W, H], [0, H]]), np.float32(quad))
    bandbreedte = half_b * 2 / 5.5 * 47 / 98
    if plat:
        lus = plat_lus(foto, M, W, H, half_b * 2, kleur, bandbreedte)
    else:
        lus = LS.hangende_lus(foto, M, W, H, half_b * 2, kleur, bandbreedte)
    uit = LS.plak(foto, rgba, quad, bm, licht=licht, verzadiging=verzadiging, lus=lus)
    pad = UIT / f'sfeer-{naam}.jpg'
    LS.bewaar(uit, pad)
    # onder 200 kB
    im = Image.open(pad)
    for q in (86, 82, 78, 74, 70):
        im.save(pad, quality=q, optimize=True, progressive=True)
        if pad.stat().st_size < 190000:
            break
    else:
        im.resize((int(im.width * .8), int(im.height * .8)), Image.LANCZOS).save(pad, quality=78, optimize=True, progressive=True)
    print('sfeer', naam)


LIJST = [
    ('board-muur-1.jpg', 'draagtas-tegel', 'muur-tegel', 1, False),
    ('board-muur-2.jpg', 'draagtas-golfjes', 'muur-golfjes', 1, False),
    ('board-muur-3.jpg', 'draagtas-zonsondergang', 'oker-zonsondergang', -1, False),
    ('board-muur-4.jpg', 'draagtas-ruit', 'witte-muur-ruit', 1, False),
    ('board-muur-5.jpg', 'draagtas-salie', 'gele-muur-salie', 1, False),
    ('board-hek-1.jpg', 'draagtas-schelp', 'bamboe-schelp', -1, False),
    ('board-bus-1.jpg', 'draagtas-tegel-navy', 'busje-tegel-navy', 1, False),
    ('board-bus-2.jpg', 'draagtas-duin', 'busjes-duin', -1, False),
    ('board-auto-1.jpg', 'draagtas-navy', 'kever-navy', 1, False),
    ('board-zand-1.jpg', 'draagtas-tegel', 'zand-tegel', 1, False),
    ('board-zand-2.jpg', 'draagtas-zonsondergang', 'zonsondergang-zand', -1, False),
    ('board-zand-3.jpg', 'draagtas-golfjes', 'geel-board-golfjes', 1, False),
    ('board-persoon-1.jpg', 'draagtas-tegel', 'vasthouden-tegel', -1, False),
    ('board-gras-1.jpg', 'draagtas-schelp', 'gras-schelp', 1, True),
]

if __name__ == '__main__':
    keuze = sys.argv[1:]
    for b, h, naam, kant, plat in LIJST:
        if keuze and naam not in keuze:
            continue
        try:
            maak(b, h, naam, kant=kant, plat=plat, armen='persoon' in b)
        except Exception as e:  # een foto mag mislukken zonder de rest te stoppen
            print('mislukt', naam, e)
