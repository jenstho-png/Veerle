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
    'draagtas-tegel':         dict(deck='#D3E6DF', papier='rose'),                          # mint
    'draagtas-tegel-navy':    dict(deck='#F1EADB', rails='#BFD3EA', papier='baby'),         # crème, babyblauwe rails
    'draagtas-golfjes':       dict(deck='#F1D6CF', papier='zandpapier'),                    # rose
    'draagtas-zonsondergang': dict(deck='#D3E3F1', papier='rose'),                          # lichtblauw
    'draagtas-schelp':        dict(deck='#C9E3E4', papier='creme'),                         # zeeglas
    'draagtas-ruit':          dict(deck='#E4D6C0', lijn='#2A3A58', papier='rose'),          # zand, navy pinline
    'draagtas-duin':          dict(deck='#33476A', potlood=(0.93, 0.9, 0.84), papier='baby'),  # navy
    'draagtas-salie':         dict(deck='#F3DCC8', papier='creme'),                         # perzik
    'draagtas-navy':          dict(deck='#EEC6B6', papier='zandpapier'),                    # koraal
}
NAMEN = {'#D3E6DF': 'mint', '#F1EADB': 'crème met babyblauwe rails', '#F1D6CF': 'rose', '#D3E3F1': 'lichtblauw',
         '#C9E3E4': 'zeeglas', '#E4D6C0': 'zand met navy pinline', '#33476A': 'navy', '#F3DCC8': 'perzik', '#EEC6B6': 'koraal'}
RR = 62.0          # breedte van de railronding (px): hier loopt de deck naar beneden
RH = 58.0          # hoogteverschil over die ronding


def smooth(a, b, x):
    return S.smooth(a, b, x)


# ---------------------------------------------------------------- board
def vorm():
    """Masker, afstand tot de rand, hoogte en normalen van het board."""
    bm = S.board_masker(aa=True)                                      # zachte (anti-aliased) rand
    d = cv2.distanceTransform((bm > 0.5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE).astype(np.float32)
    q = np.clip(d / RR, 0, 1)
    z = RH * (1 - (1 - q) ** 2.2) + 16 * smooth(RR, 330, d)           # ronde rail + lichte bolling
    zs = cv2.GaussianBlur(z, (0, 0), 4.0)
    gy, gx = np.gradient(zs)
    gx, gy = np.clip(gx, -6, 6), np.clip(gy, -6, 6)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return bm, d, n


def schaduwering(n, ka=0.56, glans=0.0, k=28):
    """Diffuus licht van het raam, genormaliseerd zodat een vlakke deck 1 is (+ optioneel glans)."""
    kd = 1 - ka
    nl = np.clip(n @ L, 0, 1)
    sh = (ka + kd * nl) / (ka + kd * L[2]) * (0.82 + 0.18 * n[..., 2])    # schuin van boven gezien: iets donkerder
    if glans:
        Hv = L + np.array([0, 0, 1], np.float32); Hv /= np.linalg.norm(Hv)
        sp = np.clip(n @ Hv, 0, 1) ** k * glans
        return sh, sp
    return sh


def potlood(beeld, regels, x0, y0, hoogte=17, kleur=(0.30, 0.30, 0.33), dekking=0.62, zaad=5, licht=False):
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
    inkt = np.array(kleur, np.float32) if licht else stuk * np.array(kleur, np.float32)
    beeld[y0:y0 + h, x0:x0 + w] = stuk * (1 - m) + inkt * m
    return beeld


def golfje(beeld, x0, y0, b=34, h=10, kleur=(0.30, 0.30, 0.33), dekking=0.6, licht=False):
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
    inkt = np.array(kleur, np.float32) if licht else stuk * np.array(kleur, np.float32)
    beeld[y0:y0 + hh, x0:x0 + ww] = stuk * (1 - m) + inkt * m
    return beeld


def teken_board(bm, d, n, stijl, zaad=1):
    rng = np.random.default_rng(zaad)
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    deck = np.array(S.hexkleur(stijl['deck']), np.float32)
    # resin-tint is nooit perfect egaal; iets voller waar het glas over de rail dubbel ligt
    vlek = cv2.GaussianBlur(rng.normal(0, 1, (CH // 4, CW // 4)).astype(np.float32), (0, 0), 14)
    vlek = cv2.resize(vlek / (vlek.std() + 1e-6), (CW, CH), interpolation=cv2.INTER_CUBIC) * 0.008
    fijn = cv2.GaussianBlur(rng.normal(0, 1, (CH, CW)).astype(np.float32), (0, 0), 0.8) * 0.006
    # geschuurde finish: heel fijne krasjes in de lengte, nauwelijks zichtbaar
    kras = cv2.GaussianBlur(rng.normal(0, 1, (CH, CW)).astype(np.float32), (0, 0), sigmaX=9, sigmaY=0.7)
    fijn = fijn + kras / (kras.std() + 1e-6) * 0.004
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
    x0 = int(S.BX0 + S.LB * 0.865)                 # buiten de hero-uitsnede, in beeld op foto 2
    font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
    bt = cv2.getTextSize("7'2 x 22 x 2", font, 16 / 22.0, 1)[0][0]
    pk = stijl.get('potlood', (0.30, 0.30, 0.33))
    licht_potlood = np.mean(pk) > 0.5
    if licht_potlood:                               # lichte inkt op een donkere tint: mengen i.p.v. vermenigvuldigen
        kleur = np.clip(kleur, 0, 1)
    kw = dict(kleur=pk, dekking=0.55, licht=licht_potlood)
    kleur = potlood(kleur, [("7'2 x 22 x 2", 0)], x0, int(BY - 40), hoogte=16, **kw)
    kleur = potlood(kleur, [("3/4", 0)], x0 + bt + 4, int(BY - 47), hoogte=10, zaad=6, **kw)
    kleur = potlood(kleur, [("#0412", 0)], x0 + 44, int(BY + 6), hoogte=13, zaad=7, **kw)
    kleur = golfje(kleur, x0 + 4, int(BY + 14), kleur=pk, dekking=0.55, licht=licht_potlood)
    return np.clip(kleur, 0, 1)


def verkort(laag, m, d, alleen_onder=False):
    """De stof loopt over de rail naar beneden: van boven gezien schuift het patroon daar in elkaar."""
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    sn = np.clip(1 - (d + 2.5) / RR, 0, 1)                               # niet oneindig steil op de uiterste rand
    extra = RR * (np.arcsin(sn) - sn)
    teken = np.sign(yy - BY)
    if alleen_onder:
        extra = extra * (yy > BY)
    ys = (yy + teken * extra).astype(np.float32)
    uit = cv2.remap(laag, xx, ys, cv2.INTER_LINEAR)
    um = cv2.remap(m, xx, ys, cv2.INTER_LINEAR)
    # waar de stof steil wegloopt valt het patroon samen: daar iets zachter (zoals de camera het ziet)
    zacht = cv2.GaussianBlur(uit, (0, 0), 1.1)
    w = smooth(12, 2, d)[..., None]
    return uit * (1 - w) + zacht * w, um


def verschuif(m, afstand, blur):
    M = np.float32([[1, 0, SCH[0] * afstand], [0, 1, SCH[1] * afstand]])
    s = cv2.warpAffine(m, M, (m.shape[1], m.shape[0]))
    return cv2.GaussianBlur(s, (0, 0), blur)


def bouw(handle):
    """Liggend canvas: board met tas (RGBA) en de band die naast het board op de grond ligt (RGBA)."""
    stijl = STIJL[handle]
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    bm, d, n = vorm()
    sh_d, spec = schaduwering(n, glans=0.10, k=22)
    board = teken_board(bm, d, n, stijl)
    board = np.clip(board * sh_d[..., None] + spec[..., None], 0, 1)

    # stof: zelfde maten als scene.py, zoom alleen op de echte (schuine) randen van het vak
    hoeken = S.paneel_hoeken()
    stof = S.stoflaag() if handle == 'draagtas-tegel' else S.variant_stof(handle)
    # het vak loopt om de rails naar de onderkant: schuine zijden doortrekken, zodat de verkorting over de rail
    # nog stof vindt (de zomen boven en onder vallen zo buiten het board)
    verder = hoeken.copy()
    for a, b in ((0, 3), (1, 2)):
        r = hoeken[a] - hoeken[b]
        verder[a] = hoeken[a] + r / abs(r[1]) * 90
        verder[b] = hoeken[b] - r / abs(r[1]) * 90
    laag, pm_vol = S.leg_stof(stof, verder)
    laag = S.zoom(laag, pm_vol, verder)
    aa = np.zeros((CH, CW), np.uint8)                                      # zelfde vorm, met zachte rand
    cv2.fillPoly(aa, [np.round(verder * 4).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=2)
    pm_vol = aa.astype(np.float32) / 255
    lum = (laag @ np.array([.299, .587, .114], np.float32))[..., None]
    laag = np.clip((lum + (laag - lum) * S.KLEUR_STOF - 0.5) * 1.07 + 0.505, 0, 1)
    laag, pm = verkort(laag, pm_vol, d)
    pm = pm * bm                                                            # de stof volgt de rail precies
    # stof krijgt hetzelfde licht als de deck, plus wat minder hemellicht waar hij om de rail valt
    sh_s = schaduwering(n, ka=0.6)
    ao = 0.8 + 0.2 * smooth(0, 70, d)
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
    # dikte van de webbing: het randje naar het raam vangt licht, de andere kant is donkerder
    gy, gx = np.gradient(cv2.GaussianBlur(bmk, (0, 0), 1.2))
    naar_licht = -(gx * -SCH[0] + gy * -SCH[1])                      # >0 op de rand die naar het raam kijkt
    bb = np.clip(bb * (1 + 0.9 * np.clip(naar_licht, 0, 0.3) - 1.4 * np.clip(-naar_licht, 0, 0.3))[..., None], 0, 1)
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
    rgba_board = np.dstack([np.clip(beeld, 0, 1), alpha_board]).astype(np.float32)
    rgba_lus = np.dstack([np.clip(bb, 0, 1), b_grond]).astype(np.float32)
    return rgba_board, rgba_lus


def staand(rgba):
    return cv2.rotate(rgba, cv2.ROTATE_90_CLOCKWISE)


# ---------------------------------------------------------------- foto's
_ZAND = {}


def ontruis(img, h=5, hk=14):
    """Kleurruis en de fijnste korrel van de stockfoto temperen (zandkorrels kosten veel bytes)."""
    u8 = cv2.cvtColor((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(cv2.fastNlMeansDenoisingColored(u8, None, h, hk, 5, 15), cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def zand():
    """stijl.achtergrond('zand'), ontruisd zodat de foto onder 190 kB past."""
    if 'z' not in _ZAND:
        _ZAND['z'] = ontruis(ST.achtergrond('zand'))
    return _ZAND['z'].copy()


def bewaar(img, pad, max_kb=190):
    """Altijd 1600 x 2000: eerst de kwaliteit omlaag (tot 44); past het dan nog niet, dan eerst wat
    kleurruis eruit (zoals tools/producten/echt_handdoek.py) en dan verder."""
    pad = pathlib.Path(pad)
    u8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    for h, hk, qs in ((0, 0, range(90, 43, -2)), (2, 8, range(60, 43, -2)), (3, 10, range(56, 39, -2))):
        b = u8 if not h else cv2.cvtColor(cv2.fastNlMeansDenoisingColored(cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), None, h, hk, 5, 15),
                                          cv2.COLOR_BGR2RGB)
        im = Image.fromarray(b)
        for q in qs:
            im.save(pad, quality=q, optimize=True, progressive=True)
            if pad.stat().st_size < max_kb * 1000:
                return f'{q}' + (f' ontruis{h}' if h else '')
    return f'{q} TE GROOT'



def zand_detail(schaal, zaad=0):
    """Zelfde zand als stijl.achtergrond('zand'), maar uit de volle resolutie voor close-ups.
    schaal: vergroting ten opzichte van de hero."""
    img = np.asarray(Image.open(ZAND_HR).convert('RGB')).astype(np.float32) / 255
    k = schaal * ST.B / 1600 * 1.15 / 2.0               # stijl: 1600 px breed x 1.15; deze foto is 2x zo groot
    img = cv2.resize(img, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    rng = np.random.default_rng(zaad)
    y0 = int(rng.integers(0, max(1, img.shape[0] - ST.H)))
    x0 = int(rng.integers(0, max(1, img.shape[1] - ST.B)))
    img = img[y0:y0 + ST.H, x0:x0 + ST.B]
    img = np.clip(img * np.array([1.03, 0.99, 0.92], np.float32) + 0.015, 0, 1)    # zelfde warme zandkleur als stijl
    return ontruis(np.clip(img * ST._licht(), 0, 1), 4, 12)


def alfa_op_doek(rgba, schaal, midden, doek):
    """Zelfde plaatsing als stijl.leg, alleen het masker."""
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, schaal)
    M[0, 2] += midden[0] - w / 2
    M[1, 2] += midden[1] - h / 2
    return cv2.warpAffine(np.ascontiguousarray(rgba[..., 3]), M, (doek.shape[1], doek.shape[0]), flags=cv2.INTER_AREA)


def slagschaduw(doek, a, lagen):
    """Extra schaduw in dezelfde richting als stijl.LICHT: lagen = [(afstand, blur, sterkte), ...]."""
    tot = np.zeros(a.shape, np.float32)
    for afstand, blur, sterkte in lagen:
        dx, dy = ST.LICHT / np.linalg.norm(ST.LICHT) * afstand
        s = cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]))
        tot = np.maximum(tot, cv2.GaussianBlur(s, (0, 0), blur) * sterkte)
    return doek * (1 - tot[..., None] * (1 - a[..., None]))


def uitsnede(rgba, px, py, schaal, marge=160):
    """Stuk van de staande laag rond (px, py), al op schaal (kubisch, geen overshoot), plus waar het op het doek komt."""
    wx, hy = ST.B / (2 * schaal) + marge / schaal, ST.H / (2 * schaal) + marge / schaal
    x0, x1, y0, y1 = int(px - wx), int(px + wx) + 1, int(py - hy), int(py + hy) + 1
    h, w = rgba.shape[:2]
    stuk = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
    ya, yb, xa, xb = max(y0, 0), min(y1, h), max(x0, 0), min(x1, w)
    stuk[ya - y0:yb - y0, xa - x0:xb - x0] = rgba[ya:yb, xa:xb]
    nw, nh = int(round(stuk.shape[1] * schaal)), int(round(stuk.shape[0] * schaal))
    # voorvermenigvuldigd schalen, zodat de randen niet donker of licht worden
    pm = np.dstack([stuk[..., :3] * stuk[..., 3:4], stuk[..., 3]])
    pm = cv2.resize(pm, (nw, nh), interpolation=cv2.INTER_AREA if schaal < 1 else cv2.INTER_CUBIC)
    a = np.clip(pm[..., 3], 0, 1)
    rgb = np.clip(pm[..., :3] / np.maximum(a[..., None], 1e-4), 0, 1)
    sx, sy = nw / stuk.shape[1], nh / stuk.shape[0]
    links = int(round(ST.B / 2 - (px - x0) * sx))
    boven = int(round(ST.H / 2 - (py - y0) * sy))
    return np.dstack([rgb, a]).astype(np.float32), (links + nw / 2, boven + nh / 2)


def foto(doek, rgba_board, rgba_lus, cx, cy, schaal, board_hoogte=20, dof=0.0):
    """Leg lus en board op de ondergrond; (cx, cy) = punt in het liggende canvas dat in het midden komt."""
    px, py = CH - cy, cx                               # dat punt in het staande canvas
    k = schaal / 0.93
    rl, midden = uitsnede(staand(rgba_lus), px, py, schaal)
    rb, _ = uitsnede(staand(rgba_board), px, py, schaal)
    w = rl.shape[1]
    # band op de grond: dikte (licht randje linksboven, donker rechtsonder) en een echte contactschaduw
    a_l = alfa_op_doek(rl, 1.0, midden, doek)
    doek = slagschaduw(doek, a_l, [(1.5 * k, 1.3 * k, 0.55), (5 * k, 5 * k, 0.28)])
    doek = ST.leg(doek, rl, breedte=w, midden=midden, hoogte=1.6 * k, contact=0.6)
    if dof:                                            # close-up: de grond ligt 7 cm lager dan de deck, net onscherp
        doek = cv2.GaussianBlur(doek, (0, 0), dof)
    # board: ligt op zijn bolle onderkant, de rails los van het zand -> donkere spleet en een zachte slagschaduw
    a_b = alfa_op_doek(rb, 1.0, midden, doek)
    doek = slagschaduw(doek, a_b, [(3 * k, 3 * k, 0.5), (14 * k, 12 * k, 0.32), (40 * k, 34 * k, 0.26)])
    doek = ST.leg(doek, rb, breedte=w, midden=midden, hoogte=board_hoogte * k, zachtheid=0.9, contact=0.7)
    return doek


def maak_alles(handle):
    rb, rl = bouw(handle)
    stijl = STIJL[handle]
    hoeken = S.paneel_hoeken()
    pad, _, _ = S.band_pad(hoeken)
    lus_y = pad[:, 1].min() - S.BAND / 2                # buitenkant van de lus
    paneel_y = BY + WB / 2                               # vak loopt tot de rail aan de andere kant
    uit = []
    # 1: hero op zand: de hele tas (vak + lus) groot en in het midden, board loopt boven en onder uit beeld;
    #    scherpgesteld op de deck, het zand 7 cm lager is een fractie zachter
    s1 = ST.B / 1640                                      # ruim: linkerrail met de omslag en de hele lus in beeld
    uit.append(foto(zand(), rb, rl, XM, (lus_y + paneel_y) / 2, s1, dof=1.4))
    # 2: het hele board op fotopapier in een merkkleur
    s2 = 0.76
    uit.append(foto(ST.achtergrond(stijl['papier'], zaad=3), rb, rl, XM, 1080, s2))
    # 3: macro van het geweven label op de stof, met de band en het geweven logo en de rail
    s3 = ST.B / 680
    uit.append(foto(zand_detail(s3 / s1, zaad=1), rb, rl, XM + 60, 930, s3, dof=2.4))
    # 4: de andere rail: het vak met zijn schuine zoom valt om de rail, de band loopt eronderdoor naar de onderkant
    s4 = ST.B / 700
    uit.append(foto(zand_detail(s4 / s1, zaad=2), rb, rl, XM + 380, 1490, s4, dof=2.4))
    for i, img in enumerate(uit, 1):
        q = bewaar(ST.afwerking(img, korrel=0.005, zaad=7 + i), DOEL / f'{handle}-{i}.jpg')
        print(f'  {handle}-{i}.jpg q{q}', (DOEL / f'{handle}-{i}.jpg').stat().st_size // 1000, 'kB')
    if handle == 'draagtas-tegel':
        for i in (1, 2, 3):
            img = np.asarray(Image.open(DOEL / f'{handle}-{i}.jpg')).astype(np.float32) / 255
            bewaar(img, THEMA / f'tt-product-{i}.jpg')
            bewaar(cv2.resize(img, (800, 1000), interpolation=cv2.INTER_AREA), THEMA / f'tt-product-{i}-800.jpg')


if __name__ == '__main__':
    keuze = sys.argv[1:] or list(S.TASSEN)
    for h in keuze:
        maak_alles(h)
        print('klaar', h, 'board', NAMEN[STIJL[h]['deck']], 'papier', STIJL[h]['papier'])
