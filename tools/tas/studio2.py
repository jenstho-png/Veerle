"""Productfoto's van de draagtas in de gedeelde studiostijl (tools/producten/stijl.py).

Opbouw (alles recht van boven, raamlicht linksboven, schaduw naar rechtsonder):
- board: een echt ogend board met karakter: getinte deck, houten stringer, gebolde rails met
  licht en glans van het raam, potloodmaten en een kleine shapersmarkering bij de staart;
- tas: de stof, band, lus en het label uit scene.py, op dezelfde maten; de stof volgt de bolling
  van het board (zelfde licht, verkorting over de rail) en de band geeft een contactschaduw;
- ondergrond: echt zand of naadloos fotopapier in een merkkleur, via stijl.achtergrond / stijl.leg;
- afwerking: stijl.afwerking (korrel, vignet, warme kleur).

python3 tools/tas/studio2.py [handle ...]  ->  docs/producten/beelden/<handle>-1..4.jpg
"""
import math, pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent / 'producten'))
import scene as S          # noqa: E402
import stijl as ST         # noqa: E402

ROOT = S.ROOT
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
THEMA = ROOT / 'theme' / 'assets'
ZAND_HR = ROOT / 'docs' / 'producten' / 'stock' / 'zand-bovenaf-hr.jpg'
CH, CW, BY, WB = S.CH, S.CW, S.BY, S.WB
XM = S.BX0 + S.LB * 0.5

# Licht in het liggende canvas. Staand (neus boven) valt de schaduw naar rechtsonder (stijl.LICHT);
# staand (px, py) = (CH - y, x), dus liggend dx = dpy, dy = -dpx.
SCH = np.array([ST.LICHT[1], -ST.LICHT[0]], np.float32)          # schaduwrichting liggend (dx, dy)
SCH /= np.linalg.norm(SCH)
ELEV = math.radians(36)
L = np.array([-SCH[0] * math.cos(ELEV), -SCH[1] * math.cos(ELEV), math.sin(ELEV)], np.float32)

# per ontwerp: deckkleur van het board, eventueel getinte rails of een pinline, en het fotopapier
STIJL = {
    'draagtas-tegel':         dict(deck='#D3E6DF', papier='rose'),
    'draagtas-tegel-navy':    dict(deck='#F1EADB', rails='#BFD3EA', papier='zandpapier'),
    'draagtas-golfjes':       dict(deck='#F1D9D2', papier='baby'),
    'draagtas-zonsondergang': dict(deck='#D4E7DB', papier='baby'),
    'draagtas-schelp':        dict(deck='#D6E4F0', papier='creme'),
    'draagtas-ruit':          dict(deck='#F1EADB', lijn='#C2704F', papier='rose'),
    'draagtas-duin':          dict(deck='#F2DCCB', lijn='#B9603F', papier='baby'),
    'draagtas-salie':         dict(deck='#D6E4F0', papier='rose'),
    'draagtas-navy':          dict(deck='#F1D9D2', lijn='#2A3A58', papier='zandpapier'),
}
RR = 42.0          # straal van de rail (px): hier loopt de deck naar beneden


def smooth(a, b, x):
    return S.smooth(a, b, x)


# ---------------------------------------------------------------- board
def vorm():
    """Masker, afstand tot de rand, hoogte en normalen van het board."""
    bm = S.board_masker()
    d = cv2.distanceTransform((bm > 0.5).astype(np.uint8), cv2.DIST_L2, 5).astype(np.float32)
    d = d + (bm - 0.5).clip(0, 0.5)                                   # zachte rand
    q = np.clip(d / RR, 0, 1)
    z = RR * np.sqrt(1 - (1 - q) ** 2) + 14 * smooth(RR, 330, d)       # ronde rail + lichte bolling
    zs = cv2.GaussianBlur(z, (0, 0), 1.6)
    gy, gx = np.gradient(zs)
    gx, gy = np.clip(gx, -6, 6), np.clip(gy, -6, 6)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return bm, d, n


def schaduwering(n, ka=0.56, glans=0.0, k=28):
    """Diffuus licht van het raam, genormaliseerd zodat een vlakke deck 1 is (+ optioneel glans)."""
    kd = 1 - ka
    nl = np.clip(n @ L, 0, 1)
    sh = (ka + kd * nl) / (ka + kd * L[2])
    if glans:
        Hv = L + np.array([0, 0, 1], np.float32); Hv /= np.linalg.norm(Hv)
        sp = np.clip(n @ Hv, 0, 1) ** k * glans
        return sh, sp
    return sh


def potlood(beeld, regels, x0, y0, hoogte=17, kleur=(0.30, 0.30, 0.33), dekking=0.62, zaad=5):
    """Handgeschreven potlood onder het glas (zoals shapers maten op de stringer zetten)."""
    rng = np.random.default_rng(zaad)
    k = 4
    font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
    sc = hoogte * k / 22.0
    hgt = int(hoogte * 1.9 * k * len(regels)) + 8 * k
    wid = int(max(cv2.getTextSize(t, font, sc, 4)[0][0] for t, _ in regels) + 40 * k)
    laag = np.zeros((hgt, wid), np.uint8)
    y = int(hoogte * 1.3 * k)
    for tekst, dx in regels:
        cv2.putText(laag, tekst, (int(dx * k) + 4 * k, y), font, sc, 255, 4, cv2.LINE_AA)
        y += int(hoogte * 1.75 * k)
    a = cv2.resize(laag.astype(np.float32) / 255, (wid // k, hgt // k), interpolation=cv2.INTER_AREA)
    a = cv2.GaussianBlur(a, (0, 0), 0.45)
    a *= 0.75 + 0.25 * rng.random(a.shape).astype(np.float32)     # grafietkorrel
    h, w = a.shape
    stuk = beeld[y0:y0 + h, x0:x0 + w]
    m = (a * dekking)[..., None]
    beeld[y0:y0 + h, x0:x0 + w] = stuk * (1 - m) + stuk * np.array(kleur, np.float32) / 0.6 * 0.6 * m
    return beeld


def golfje(beeld, x0, y0, b=34, h=10, kleur=(0.30, 0.30, 0.33), dekking=0.6):
    """Klein getekend golfje als shapersteken."""
    k = 4
    laag = np.zeros((h * k + 8 * k, b * k + 8 * k), np.uint8)
    xs = np.linspace(0, b, 80)
    ys = h / 2 + h / 2 * np.sin(xs / b * 2 * np.pi * 1.5) * np.linspace(1, 0.6, 80)
    pts = np.stack([xs + 4, ys + 4], 1) * k
    cv2.polylines(laag, [np.round(pts).astype(np.int32)], False, 255, 5, cv2.LINE_AA)
    a = cv2.resize(laag.astype(np.float32) / 255, (laag.shape[1] // k, laag.shape[0] // k), interpolation=cv2.INTER_AREA)
    hh, ww = a.shape
    stuk = beeld[y0:y0 + hh, x0:x0 + ww]
    m = (a * dekking)[..., None]
    beeld[y0:y0 + hh, x0:x0 + ww] = stuk * (1 - m) + stuk * np.array(kleur, np.float32) * m
    return beeld


def teken_board(bm, d, n, stijl, zaad=1):
    rng = np.random.default_rng(zaad)
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    deck = np.array(S.hexkleur(stijl['deck']), np.float32)
    # resin-tint is nooit perfect egaal; iets voller waar het glas over de rail dubbel ligt
    vlek = cv2.GaussianBlur(rng.normal(0, 1, (CH // 4, CW // 4)).astype(np.float32), (0, 0), 14)
    vlek = cv2.resize(vlek / (vlek.std() + 1e-6), (CW, CH), interpolation=cv2.INTER_CUBIC) * 0.008
    fijn = cv2.GaussianBlur(rng.normal(0, 1, (CH, CW)).astype(np.float32), (0, 0), 0.8) * 0.006
    lum = deck.mean()
    dubbel = 1 + 0.35 * smooth(14, 0, d)
    kleur = (lum + (deck - lum) * dubbel[..., None]) * (1 + vlek + fijn)[..., None]
    if 'rails' in stijl:
        rc = np.array(S.hexkleur(stijl['rails']), np.float32)
        lap = 46 + 3 * np.sin(xx / 97.0) + 2 * np.sin(xx / 31.0 + 1)          # cutlap lijn, licht golvend
        r = smooth(lap + 1.5, lap - 1.5, d)
        kleur = kleur * (1 - r[..., None]) + rc * (1 + vlek + fijn)[..., None] * r[..., None]
    if 'lijn' in stijl:
        lc = np.array(S.hexkleur(stijl['lijn']), np.float32)
        p = np.clip(1 - np.abs(d - 30) / 2.6, 0, 1) ** 0.8 * (d > 20)
        p = p * smooth(0.05, 0.2, (xx - S.BX0) / S.LB) * smooth(0.97, 0.88, (xx - S.BX0) / S.LB)
        kleur = kleur * (1 - 0.9 * p[..., None]) + lc * 0.9 * p[..., None]
    # houten stringer (3 mm) van neus tot staart
    s = np.clip(2.2 - np.abs(yy - BY), 0, 1) * smooth(1, 6, d)
    hout = np.array([0.66, 0.50, 0.34], np.float32) * (0.94 + 0.06 * np.sin(xx / 13.0))[..., None]
    kleur = kleur * (1 - 0.85 * s[..., None]) + hout * 0.85 * s[..., None]
    # potlood bij de staart, naast de stringer; klein shapersteken eronder
    x0 = int(S.BX0 + S.LB * 0.875)
    kleur = potlood(kleur, [("7'2 x 22 x 2", 0)], x0, int(BY - 40), hoogte=16)
    kleur = potlood(kleur, [("3/4", 0)], x0 + 148, int(BY - 48), hoogte=10, zaad=6)
    kleur = potlood(kleur, [("#0412", 0)], x0 + 40, int(BY + 6), hoogte=13, zaad=7)
    kleur = golfje(kleur, x0 + 4, int(BY + 14))
    return np.clip(kleur, 0, 1)


# ---------------------------------------------------------------- tas op het board
def verkort(laag, m, d, alleen_onder=False):
    """De stof loopt over de rail naar beneden: van boven gezien schuift het patroon daar in elkaar."""
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    sn = np.clip(1 - d / RR, 0, 1)
    extra = RR * (np.arcsin(sn) - sn)
    teken = np.sign(yy - BY)
    if alleen_onder:
        extra = extra * (yy > BY)
    ys = (yy + teken * extra).astype(np.float32)
    uit = cv2.remap(laag, xx, ys, cv2.INTER_LINEAR)
    um = cv2.remap(m, xx, ys, cv2.INTER_LINEAR)
    return uit, um


def verschuif(m, afstand, blur):
    M = np.float32([[1, 0, SCH[0] * afstand], [0, 1, SCH[1] * afstand]])
    s = cv2.warpAffine(m, M, (m.shape[1], m.shape[0]))
    return cv2.GaussianBlur(s, (0, 0), blur)


def bouw(handle):
    """Liggend canvas: board met tas (RGBA) en de band die naast het board op de grond ligt (RGBA)."""
    stijl = STIJL[handle]
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    bm, d, n = vorm()
    sh_d, spec = schaduwering(n, glans=0.07)
    board = teken_board(bm, d, n, stijl)
    board = np.clip(board * sh_d[..., None] + spec[..., None], 0, 1)

    # stof: zelfde maten als scene.py, zoom alleen op de echte (schuine) randen van het vak
    hoeken = S.paneel_hoeken()
    stof = S.stoflaag() if handle == 'draagtas-tegel' else S.variant_stof(handle)
    laag, pm_vol = S.leg_stof(stof, hoeken)
    laag = S.zoom(laag, pm_vol, hoeken)
    lum = (laag @ np.array([.299, .587, .114], np.float32))[..., None]
    laag = np.clip((lum + (laag - lum) * S.KLEUR_STOF - 0.5) * 1.07 + 0.505, 0, 1)
    laag, pm = verkort(laag, pm_vol, d)
    overhang = cv2.dilate(bm, np.ones((5, 5), np.uint8))                   # stofdikte net over de rail
    pm = pm * overhang
    # stof krijgt hetzelfde licht als de deck, plus wat minder hemellicht waar hij om de rail valt
    sh_s = schaduwering(n, ka=0.6)
    ao = 0.9 + 0.1 * smooth(0, 55, d)
    laag = laag * (sh_s * ao)[..., None]
    # randje schaduw van de dikke zoom op het board
    ps = verschuif(pm, 2.5, 2.2)
    beeld = board * (1 - 0.28 * ps[..., None] * (1 - pm[..., None]))
    beeld = beeld * (1 - pm[..., None]) + laag * pm[..., None]

    # label, met de schaduw in de lichtrichting
    beeld = S.label(beeld, (XM, hoeken[0, 1] + 75), schaduw=(int(round(SCH[1] * 3)), int(round(SCH[0] * 3))))

    # band
    pad, _, _ = S.band_pad(hoeken)
    tex = S.band_textuur()
    kleur_band = S.hexkleur(S.TASSEN[handle])
    bb, bmk = S.teken_band(beeld, pad, tex, stofmasker=pm, kleur_band=kleur_band)
    bb, bmk = verkort(bb, bmk, d, alleen_onder=True)
    op_board = np.where(yy < BY, 1.0, 0.0) * 0 + bm                         # deel op het board
    zicht = np.where(yy < BY, 1.0, bm)                                       # onder de middellijn: om de rail naar de onderkant
    bmk = bmk * zicht
    sh_b, sp_b = schaduwering(n, ka=0.58, glans=0.035, k=18)
    sh_b = np.where(bm > 0.02, sh_b, 1.0)
    sp_b = np.where(bm > 0.02, sp_b, 0.0)
    bb = np.clip(bb * sh_b[..., None] + sp_b[..., None], 0, 1)

    # band op het board: contactschaduw (scherp) + zachte schaduw
    b_op = bmk * op_board
    bs = verschuif(b_op, 2.0, 1.4) * 0.45 + verschuif(b_op, 6.0, 5.0) * 0.22
    beeld = beeld * (1 - bs[..., None] * (1 - b_op[..., None]))
    beeld = beeld * (1 - b_op[..., None]) + bb * b_op[..., None]
    alpha_board = np.clip(np.maximum(bm, pm), 0, 1)
    alpha_board = np.maximum(alpha_board, b_op)

    # band naast het board (lus): eigen laag, ligt plat op de grond
    b_grond = bmk * (1 - alpha_board)
    rgba_board = np.dstack([beeld, alpha_board]).astype(np.float32)
    rgba_lus = np.dstack([bb, b_grond]).astype(np.float32)
    return rgba_board, rgba_lus


def staand(rgba):
    return cv2.rotate(rgba, cv2.ROTATE_90_CLOCKWISE)


# ---------------------------------------------------------------- foto's
def zand_detail(schaal, zaad=0):
    """Zelfde zand als stijl.achtergrond('zand'), maar uit de volle resolutie voor close-ups."""
    img = np.asarray(Image.open(ZAND_HR).convert('RGB')).astype(np.float32) / 255
    k = schaal * ST.B / 1600 * 1.15 / 2.0               # stijl: 1600 px breed x 1.15; deze foto is 2x zo groot
    img = cv2.resize(img, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    rng = np.random.default_rng(zaad)
    y0 = int(rng.integers(0, max(1, img.shape[0] - ST.H)))
    x0 = int(rng.integers(0, max(1, img.shape[1] - ST.B)))
    img = img[y0:y0 + ST.H, x0:x0 + ST.B]
    img = np.clip(img * np.array([1.03, 0.99, 0.92], np.float32) + 0.015, 0, 1)
    return np.clip(img * ST._licht(), 0, 1)


def foto(doek, rgba_board, rgba_lus, cx, cy, schaal, board_hoogte=20):
    """Leg lus en board op de ondergrond; (cx, cy) = punt in het liggende canvas dat in het midden komt."""
    hb, wb = CW, CH                                    # staand formaat van de lagen
    px, py = CH - cy, cx                               # dat punt in het staande canvas
    midden = (ST.B / 2 + (wb / 2 - px) * schaal, ST.H / 2 + (hb / 2 - py) * schaal)
    doek = ST.leg(doek, staand(rgba_lus), breedte=wb * schaal, midden=midden, hoogte=1.6 * schaal / 0.93, contact=0.6)
    doek = ST.leg(doek, staand(rgba_board), breedte=wb * schaal, midden=midden, hoogte=board_hoogte * schaal / 0.93,
                  zachtheid=0.9, contact=0.7)
    return doek


def maak_alles(handle):
    rb, rl = bouw(handle)
    stijl = STIJL[handle]
    uit = []
    # 1: hero op zand, stringer in het midden, hele lus in beeld
    s1 = ST.B / 1720
    uit.append(foto(ST.achtergrond('zand'), rb, rl, XM, BY, s1))
    # 2: heel board op fotopapier in een merkkleur
    s2 = ST.H / 2900 * 0.97
    uit.append(foto(ST.achtergrond(stijl['papier'], zaad=3), rb, rl, XM, BY - 40, s2))
    # 3: detail van het label en de band met het geweven logo
    s3 = ST.B / 960
    uit.append(foto(zand_detail(s3 / s1, zaad=1), rb, rl, XM + 10, 930, s3))
    # 4: het vak dat over de rail valt en de band die de lus in gaat
    s4 = ST.B / 1000
    uit.append(foto(zand_detail(s4 / s1, zaad=2), rb, rl, XM + 300, 880, s4))
    for i, img in enumerate(uit, 1):
        ST.bewaar(ST.afwerking(img, zaad=7 + i), DOEL / f'{handle}-{i}.jpg')
    if handle == 'draagtas-tegel':
        for i in (1, 2, 3):
            img = np.asarray(Image.open(DOEL / f'{handle}-{i}.jpg')).astype(np.float32) / 255
            ST.bewaar(img, THEMA / f'tt-product-{i}.jpg')
            ST.bewaar(cv2.resize(img, (800, 1000), interpolation=cv2.INTER_AREA), THEMA / f'tt-product-{i}-800.jpg')


if __name__ == '__main__':
    keuze = sys.argv[1:] or list(S.TASSEN)
    for h in keuze:
        maak_alles(h)
        print('klaar', h, STIJL[h]['papier'])
