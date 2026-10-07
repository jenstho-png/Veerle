"""De afgewerkte draagtas als studiofoto (flat lay van bovenaf), opgebouwd uit echt materiaal.

- Stof: de echte jacquard uit de fabrieksfoto (stof.py), schoon opnieuw gelegd.
- Schouderband: de echte blauwe webbing uit de fabrieksfoto, als textuur langs het pad uit de tekening.
- Afwerking zoals een gestikte tas: omgeslagen zoom met stiksel, band met vierkant kruisstiksel, geweven logolabel.
- Board en studio: glad crème board met licht, schaduw en stringer; effen studiodoek.
"""
import json, math, pathlib, random
import cv2
import numpy as np
from PIL import Image
from scipy.interpolate import PchipInterpolator

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
FAB = ROOT / 'docs' / 'producten' / 'fabriek'
REF = ROOT / 'docs' / 'producten' / 'referentie'
rng = np.random.default_rng(3)

# maten (pixels, board ligt horizontaal, neus links)
CW, CH = 2900, 2320           # canvas (staand straks 2320 x 2900 = 4:5)
WB = 640                      # breedte board
LB = 2420                     # lengte board
BX0, BY = 240, 1300           # neus x, middellijn y
TEGEL = 1.08                  # schaal van de echte tegels (98 x 115 px in de foto)
BAND = round(47 / 98 * 98 * TEGEL)   # bandbreedte, zelfde verhouding tot de tegels als op de foto
DOEK = np.array([0.95, 0.93, 0.895], np.float32)
KLEUR_STOF = 1.28                # verzadiging van de stof (1 = zoals de fabrieksfoto)


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def board_masker():
    t = np.array([0, .015, .05, .12, .25, .42, .58, .75, .88, .96, 1.0])
    f = np.array([0, .26, .5, .72, .9, .995, 1.0, .93, .74, .5, .34])
    spl = PchipInterpolator(t, f)
    xs = np.linspace(0, 1, 600)
    half = spl(xs) * WB / 2
    boven = [(BX0 + x * LB, BY - h) for x, h in zip(xs, half)]
    onder = [(BX0 + x * LB, BY + h) for x, h in zip(xs, half)][::-1]
    pts = np.array(boven + onder, np.float32)
    m = np.zeros((CH, CW), np.uint8)
    cv2.fillPoly(m, [np.round(pts * 4).astype(np.int32)], 1, lineType=cv2.LINE_AA, shift=2)
    return m.astype(np.float32)


def teken_board(m):
    d = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    basis = np.array([0.93, 0.9, 0.82], np.float32)
    rail = 0.78 + 0.22 * smooth(0, WB * 0.2, d)
    licht = 1 + 0.035 * np.clip((BY - yy) / (WB / 2), -1, 1)                 # licht van boven
    glans = 0.035 * np.exp(-((yy - (BY - WB * 0.17)) / (WB * 0.07)) ** 2)      # lange glansstreep
    glans *= 0.6 + 0.4 * cv2.GaussianBlur(rng.random((CH, CW)).astype(np.float32), (0, 0), 60) * 2
    vlek = cv2.GaussianBlur(rng.normal(0, 1, (CH, CW)).astype(np.float32), (0, 0), 18) * 0.06 + cv2.GaussianBlur(rng.normal(0, 1, (CH, CW)).astype(np.float32), (0, 0), 4) * 0.012
    langs = 1 - 0.05 * np.abs((xx - (BX0 + LB * 0.55)) / (LB * 0.5)) ** 2         # neus en staart iets donkerder (rocker)
    korrel = rng.normal(0, 0.006, (CH, CW)).astype(np.float32)
    kleur = basis[None, None] * (rail * licht * langs + vlek + korrel)[..., None] + glans[..., None]
    # stringer
    s = np.exp(-((yy - BY) / 1.3) ** 2) * (d > 18)
    kleur = kleur * (1 - 0.55 * s[..., None]) + np.array([0.6, 0.45, 0.3], np.float32) * 0.55 * s[..., None]
    # rand: dunne donkere lijn en een lichtrandje net binnen
    rand = np.exp(-(d / 2.2) ** 2)
    binnen = np.exp(-((d - 6) / 3) ** 2) * 0.03
    kleur = kleur * (1 - 0.18 * rand[..., None]) + binnen[..., None]
    return np.clip(kleur, 0, 1), d


def paneel_hoeken():
    xm = BX0 + LB * 0.5
    h = WB * 1.08
    top, bot = BY - h / 2, BY + h / 2
    return np.array([[xm - 255, top], [xm + 255, top], [xm + 440, bot], [xm - 440, bot]], np.float32)


def stoflaag():
    import sys
    sys.path.insert(0, str(HIER))
    from stof import lap
    stof = np.asarray(lap(14, 7, zaad=11, schaal=1)).astype(np.float32) / 255
    stof = cv2.resize(stof, None, fx=TEGEL, fy=TEGEL, interpolation=cv2.INTER_CUBIC)
    return stof


def leg_stof(stof, hoeken):
    """Recht raster, uitgelijnd op de onderrand, geknipt in de trapeziumvorm."""
    laag = np.zeros((CH, CW, 3), np.float32)
    x0 = int(hoeken[3, 0]) - 30
    y1 = int(hoeken[2, 1])
    sh, sw = stof.shape[:2]
    y0 = y1 - sh
    xa, ya = max(x0, 0), max(y0, 0)
    laag[ya:y0 + sh, xa:x0 + sw] = stof[ya - y0:, xa - x0:][:CH - ya, :CW - xa]
    m = np.zeros((CH, CW), np.uint8)
    cv2.fillPoly(m, [np.round(hoeken * 4).astype(np.int32)], 1, lineType=cv2.LINE_AA, shift=2)
    return laag, m.astype(np.float32)


def zoom(kleur, m, hoeken):
    """Omgeslagen rand: iets donkerder en dikker, met een stiksellijn in crèmegaren."""
    d = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    rol = np.exp(-(d / 3.0) ** 2)
    kleur = kleur * (1 - 0.28 * rol[..., None]) * (1 - 0.06 * smooth(18, 0, d)[..., None])
    # stiksel 13 px binnen de rand, als streepjes
    stik = np.zeros((CH, CW), np.float32)
    binnen = cv2.erode((m > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (27, 27)))
    cnt, _ = cv2.findContours(binnen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for c in cnt:
        c = c[:, 0, :].astype(np.float32)
        lengte = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
        for a in np.arange(0, lengte[-1] - 8, 11):
            i0, i1 = np.searchsorted(lengte, a), np.searchsorted(lengte, a + 7)
            cv2.line(stik, tuple(np.round(c[i0]).astype(int)), tuple(np.round(c[min(i1, len(c) - 1)]).astype(int)), 1, 2, cv2.LINE_AA)
    sch = cv2.GaussianBlur(np.roll(stik, 1, axis=0), (0, 0), 1)
    kleur = kleur * (1 - 0.25 * sch[..., None])
    garen = np.array([0.93, 0.89, 0.8], np.float32)
    return kleur * (1 - 0.85 * stik[..., None]) + garen * 0.85 * stik[..., None]


def band_textuur():
    img = cv2.cvtColor(cv2.imread(str(FAB / 'fabrieksfoto.jpg')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    p0, p1 = np.array([851, 500.]), np.array([751.5, 900.])      # vlak en strak op de stof gemeten: 47 px breed bij een tegel van 98 px
    u = (p1 - p0) / np.linalg.norm(p1 - p0); n = np.array([u[1], -u[0]])
    S, T = np.meshgrid(np.arange(-21, 21, 0.5), np.arange(0, np.linalg.norm(p1 - p0), 0.5), indexing='ij')
    X, Y = p0[0] + u[0] * T + n[0] * S, p0[1] + u[1] * T + n[1] * S
    strook = cv2.remap(img, X.astype(np.float32), Y.astype(np.float32), cv2.INTER_CUBIC)
    # alleen de fijne weefstructuur houden: geen vlekken, geen deuken
    L = strook @ np.array([.299, .587, .114], np.float32)
    fijn = L - cv2.GaussianBlur(L, (0, 0), 3)
    return np.clip(fijn / (np.abs(fijn).std() * 4 + 1e-6), -0.25, 0.25)  # rijen = dwars, kolommen = langs


def band_pad(hoeken):
    """Eén doorlopende band, maten in tegels gemeten op de fabrieksfoto:
    strengen op +-3,15 tegel bij de onderrand en +-2 tegel bij de bovenrand van het vak,
    lus 3,35 tegelhoogtes boven het vak."""
    tw, th = 98 * TEGEL, 115 * TEGEL
    xm = (hoeken[0, 0] + hoeken[1, 0]) / 2
    top_y, bot_y = hoeken[0, 1], hoeken[2, 1]
    voet_y = BY + WB * 0.62

    def langs(dx_onder, dx_boven, y):
        t = (y - bot_y) / (top_y - bot_y)
        return xm + dx_onder + (dx_boven - dx_onder) * t
    voet_l = np.array([langs(-3.15 * tw, -1.99 * tw, voet_y), voet_y])
    voet_r = np.array([langs(3.15 * tw, 1.99 * tw, voet_y), voet_y])
    top_lus = top_y - 3.35 * th
    R = 0.95 * tw
    c = np.array([xm, top_lus + R])

    def raakpunten(v):
        d = v - c; L = np.linalg.norm(d)
        a = math.atan2(d[1], d[0]); b = math.acos(R / L)
        return [a + b, a - b]
    beste = None
    for al in raakpunten(voet_l):
        for ar in raakpunten(voet_r):
            for richting in (1, -1):
                eind = ar
                while (eind - al) * richting <= 0:
                    eind += 2 * math.pi * richting
                while (eind - al) * richting > 2 * math.pi:
                    eind -= 2 * math.pi * richting
                hoeken_boog = np.linspace(al, eind, 200)
                boog = c + R * np.stack([np.cos(hoeken_boog), np.sin(hoeken_boog)], 1)
                score = abs(eind - al) + (0 if boog[:, 1].min() < c[1] - R * 0.98 else 10)
                if beste is None or score < beste[0]:
                    beste = (score, al, eind)
    _, al, ar = beste
    tl = c + R * np.array([math.cos(al), math.sin(al)])
    tr = c + R * np.array([math.cos(ar), math.sin(ar)])
    pts = [voet_l + (tl - voet_l) * t for t in np.linspace(0, 1, 400)]
    pts += [c + R * np.array([math.cos(t), math.sin(t)]) for t in np.linspace(al, ar, 200)[1:]]
    pts += [tr + (voet_r - tr) * t for t in np.linspace(0, 1, 400)[1:]]
    return np.array(pts, np.float32), voet_l, voet_r


def logo_strook(breedte=BAND, periode=170, hoogte=13):
    """Masker met het liggende logo, herhaald langs de band (rijen = dwars, kolommen = langs)."""
    L = json.load(open(ROOT / 'tools' / 'brand2' / 'logo2.json'))['liggend']
    sc = hoogte / L['h']
    m = np.zeros((breedte * 4, periode * 4), np.uint8)
    for ring in L['d'].split('Z'):
        ring = ring.strip()
        if not ring:
            continue
        pts = np.array([[float(v) for v in p.split()] for p in ring.lstrip('M').split('L')], np.float32)
        pts = (pts * sc + np.array([(periode - L['w'] * sc) / 2, (breedte - hoogte) / 2])) * 4
        laag = np.zeros_like(m)
        cv2.fillPoly(laag, [np.round(pts).astype(np.int32)], 1)
        m ^= laag
    return cv2.resize(m.astype(np.float32), (periode, breedte), interpolation=cv2.INTER_AREA)


def teken_band(onder, pad, tex, breedte=BAND, stofmasker=None, kleur_band=(0.56, 0.66, 0.78), tekst_kleur=None):
    """Leg de echte webbingtextuur langs het pad; geeft beeld en masker terug."""
    seg = np.diff(pad, axis=0)
    lengte = np.r_[0, np.cumsum(np.linalg.norm(seg, axis=1))]
    raak = np.r_[seg[:1], seg]; raak /= np.linalg.norm(raak, axis=1)[:, None] + 1e-9
    norm = np.stack([-raak[:, 1], raak[:, 0]], 1)
    th, tw = tex.shape[:2]
    m = np.zeros((CH, CW), np.float32); beeld = np.zeros((CH, CW, 3), np.float32)
    x0, y0 = int(pad[:, 0].min() - breedte), int(pad[:, 1].min() - breedte)
    x1, y1 = int(pad[:, 0].max() + breedte), int(pad[:, 1].max() + breedte)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    pts = np.stack([xx.ravel(), yy.ravel()], 1)
    # dichtstbijzijnde padpunt per pixel (via een fijn gesampled pad)
    from scipy.spatial import cKDTree
    boom = cKDTree(pad)
    afst, idx = boom.query(pts)
    rel = pts - pad[idx]
    dwars = (rel * norm[idx]).sum(1)
    langs = lengte[idx] + (rel * raak[idx]).sum(1)
    binnen = np.abs(dwars) <= breedte / 2
    u = ((dwars / breedte + 0.5) * (th - 1))
    v = (langs * 2) % (2 * tw - 2)
    v = np.where(v > tw - 1, 2 * tw - 2 - v, v)     # gespiegeld herhalen, geen naad
    struct = cv2.remap(tex, v.reshape(yy.shape).astype(np.float32), u.reshape(yy.shape).astype(np.float32), cv2.INTER_LINEAR)
    golf = 1 + 0.03 * np.sin(langs.reshape(yy.shape) / 140.0) + 0.012 * np.sin(langs.reshape(yy.shape) / 37.0 + 1.3)
    kleur = np.array(kleur_band, np.float32)[None, None] * ((1 + 0.16 * struct) * golf)[..., None]
    tekst = logo_strook(breedte)
    tu = (dwars + breedte / 2).reshape(yy.shape).astype(np.float32)
    tv = (langs % tekst.shape[1]).reshape(yy.shape).astype(np.float32)
    t = cv2.remap(tekst, tv, tu, cv2.INTER_LINEAR)[..., None]
    kleur = kleur * (1 - t) + np.clip(kleur * 1.28 + 0.04, 0, 1) * t      # ingeweven, iets lichter blauw
    if tekst_kleur is not None:
        kleur = kleur * (1 - t) + np.array(tekst_kleur, np.float32)[None, None] * ((1 + 0.16 * struct) * golf)[..., None] * t
    # nylon webbing: fijne ribbels in de lengte en een zachte glans
    dw = dwars.reshape(yy.shape)
    rib = 1 + 0.045 * np.sin(dw * 2 * np.pi / 2.2) + 0.015 * np.sin(langs.reshape(yy.shape) * 2 * np.pi / 1.7)
    glans = 0.018 * (1 - np.abs(dw) / (breedte / 2))
    kleur = np.clip(kleur * rib[..., None] + glans[..., None], 0, 1)
    if stofmasker is not None:
        op_stof = stofmasker[y0:y1, x0:x1]
        a = np.abs(dwars).reshape(yy.shape)
        steek = ((a > breedte / 2 - 5.2) & (a < breedte / 2 - 3.4) & ((langs.reshape(yy.shape) % 10) < 6)).astype(np.float32) * op_stof
        steek = cv2.GaussianBlur(steek, (0, 0), 0.5)
        kleur = kleur * (1 - 0.18 * np.roll(steek, 1, 0)[..., None])
        kleur = kleur * (1 - 0.8 * steek[..., None]) + np.array([0.66, 0.74, 0.84], np.float32) * 0.8 * steek[..., None]
    rand = np.clip((breedte / 2 - np.abs(dwars)) / 1.2, 0, 1).reshape(yy.shape)
    kant = np.exp(-((breedte / 2 - np.abs(dwars)) / 1.1) ** 2).reshape(yy.shape)
    kleur = kleur * (1 - 0.12 * kant[..., None])
    m[y0:y1, x0:x1] = rand
    beeld[y0:y1, x0:x1] = kleur
    return beeld, m


def kruisstiksel(kleur, punt, richting, breedte=BAND, garen=(0.62, 0.7, 0.8)):
    u = richting / np.linalg.norm(richting); n = np.array([-u[1], u[0]])
    h = breedte / 2 - 5
    hoek = [punt + n * h, punt + n * h + u * 44, punt - n * h + u * 44, punt - n * h]
    hoek = [tuple(np.round(p).astype(int)) for p in hoek]
    laag = np.zeros(kleur.shape[:2], np.float32)
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)]:
        cv2.line(laag, hoek[a], hoek[b], 1, 2, cv2.LINE_AA)
    g = np.array(garen, np.float32)
    kleur = kleur * (1 - 0.2 * cv2.GaussianBlur(np.roll(laag, 1, 0), (0, 0), 1)[..., None])
    return kleur * (1 - 0.8 * laag[..., None]) + g * 0.8 * laag[..., None]


def label(kleur, midden, b=118, h=74):
    """Geweven label: navy met het crème logo, vastgestikt aan twee kanten."""
    logo = np.asarray(Image.open(REF / 'logo-navy.png').convert('RGBA')).astype(np.float32) / 255
    ys, xs = np.where(logo[..., 3] > 0.05)
    logo = logo[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    lw = int(b * 0.62); lh = int(logo.shape[0] * lw / logo.shape[1])
    logo = cv2.resize(logo, (lw, lh), interpolation=cv2.INTER_AREA)
    x0, y0 = int(midden[0] - b / 2), int(midden[1] - h / 2)
    navy = np.array([0.15, 0.2, 0.31], np.float32)
    weef = 1 + (np.sin(np.arange(b)[None, :] * 2.1) * np.sin(np.arange(h)[:, None] * 2.3)) * 0.04 + rng.normal(0, 0.015, (h, b))
    stuk = navy[None, None] * weef[..., None]
    lx, ly = (b - lw) // 2, (h - lh) // 2
    a = logo[..., 3:4]
    creme = np.array([0.93, 0.9, 0.82], np.float32)
    stuk[ly:ly + lh, lx:lx + lw] = stuk[ly:ly + lh, lx:lx + lw] * (1 - a) + creme * weef[ly:ly + lh, lx:lx + lw, None] * a
    # schaduw onder het label
    m = np.zeros(kleur.shape[:2], np.float32); m[y0:y0 + h, x0:x0 + b] = 1
    s = cv2.GaussianBlur(np.roll(np.roll(m, 3, 0), 2, 1), (0, 0), 2.5)
    kleur = kleur * (1 - 0.35 * s[..., None])
    kleur[y0:y0 + h, x0:x0 + b] = stuk
    for x in (x0 + 5, x0 + b - 6):
        for y in range(y0 + 3, y0 + h - 3, 7):
            cv2.line(kleur, (x, y), (x, y + 4), (0.2, 0.26, 0.38), 1, cv2.LINE_AA)
    return kleur


def variant_stof(handle, tegel=118):
    """Een ander patroon als jacquard: kleur uit ons patroonbestand, weefstructuur uit de echte stof."""
    pat = np.asarray(Image.open(REF / f'{handle}-stof.png').convert('RGB')).astype(np.float32) / 255
    pat = cv2.resize(pat, None, fx=tegel / (pat.shape[1] / 6), fy=tegel / (pat.shape[1] / 6), interpolation=cv2.INTER_AREA)
    echt = stoflaag()
    h, w = echt.shape[:2]
    reps = (int(np.ceil(h / pat.shape[0])) + 1, int(np.ceil(w / pat.shape[1])) + 1, 1)
    vlak = np.tile(pat, reps)[:h, :w]
    # neutrale jacquardbinding: fijne schering en inslag, kleine onregelmatigheden
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    binding = 0.1 * np.sin(xx * 2 * np.pi / 3.1) * np.sin(yy * 2 * np.pi / 3.4) + 0.04 * np.sin((xx + yy) * 2 * np.pi / 6.2)
    garen = np.repeat(rng.normal(0, 0.025, (h, 1)), w, 1) * (0.6 + 0.4 * np.sin(xx / 23.0))   # dikkere en dunnere draden
    ruis = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.7) * 0.03
    vlek = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 30) * 0.03
    return np.clip(vlak * (1 + binding + ruis + vlek + garen)[..., None], 0, 1)


def maak(patroon=None, band=(0.56, 0.66, 0.78), los=False):
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    r = np.sqrt(((xx - CW * .5) / CW) ** 2 + ((yy - CH * .45) / CH) ** 2)
    beeld = DOEK[None, None] * (1.03 - 0.1 * r[..., None]) + rng.normal(0, 0.004, (CH, CW, 1)).astype(np.float32)
    bm = board_masker()
    # schaduw van het board op het doek
    s1 = cv2.GaussianBlur(np.roll(np.roll(bm, 26, 0), 14, 1), (0, 0), 30)
    s2 = cv2.GaussianBlur(np.roll(bm, 4, 0), (0, 0), 5)
    beeld = beeld * (1 - 0.22 * s1[..., None]) * (1 - 0.25 * s2[..., None])
    bk, bd = teken_board(bm)
    beeld = beeld * (1 - bm[..., None]) + bk * bm[..., None]
    # stof
    hoeken = paneel_hoeken()
    if patroon is None:
        stof = stoflaag()
    else:
        stof = patroon
    laag, pm = leg_stof(stof, hoeken)
    pm = pm * cv2.erode(bm, np.ones((3, 3), np.uint8))
    rail = (0.86 + 0.14 * smooth(0, WB * 0.16, bd))
    laag = laag * rail[..., None] * (1 + 0.025 * np.clip((BY - yy) / (WB / 2), -1, 1))[..., None]
    laag = zoom(laag, pm, hoeken)
    # meer kleur in de stof: iets voller en met wat meer contrast, zoals echte geweven stof in daglicht
    lum = (laag @ np.array([.299, .587, .114], np.float32))[..., None]
    laag = np.clip((lum + (laag - lum) * KLEUR_STOF - 0.5) * 1.07 + 0.505, 0, 1)
    ps = cv2.GaussianBlur(np.roll(np.roll(pm, 5, 0), 3, 1), (0, 0), 4)
    beeld = beeld * (1 - 0.35 * ps[..., None] * (1 - pm[..., None]))
    beeld = beeld * (1 - pm[..., None]) + laag * pm[..., None]
    # label op het vak, midden onder de korte rand
    beeld = label(beeld, ((hoeken[0, 0] + hoeken[1, 0]) / 2, hoeken[0, 1] + 75))
    # schouderband
    pad, sl, sr = band_pad(hoeken)
    tex = band_textuur()
    bb, bmk = teken_band(beeld, pad, tex, stofmasker=pm, kleur_band=band)
    # onder de middellijn verdwijnt de band om de rail naar de onderkant
    zicht = np.where(yy < BY, 1.0, bm)
    bmk = bmk * zicht
    om = 0.7 + 0.3 * smooth(0, 40, bd)
    bb = bb * np.where(yy < BY, 1.0, om)[..., None]
    bs = cv2.GaussianBlur(np.roll(np.roll(bmk, 7, 0), 4, 1), (0, 0), 7) * 0.7 + cv2.GaussianBlur(np.roll(bmk, 2, 0), (0, 0), 1.6) * 0.5
    beeld = beeld * (1 - 0.3 * bs[..., None] * (1 - bmk[..., None]))
    beeld = beeld * (1 - bmk[..., None]) + bb * bmk[..., None]
    # camera: vignet, iets zachter beeld en korrel
    vig = 1 - 0.07 * (((xx - CW / 2) / (CW / 2)) ** 2 + ((yy - CH / 2) / (CH / 2)) ** 2)
    beeld = beeld * vig[..., None]
    beeld = cv2.GaussianBlur(beeld, (0, 0), 0.45)
    beeld = np.clip(beeld + rng.normal(0, 0.008, beeld.shape).astype(np.float32), 0, 1)
    if los:
        # board, tas en band los van de achtergrond (voor nieuwe composities)
        return beeld, np.clip(np.maximum(bm, bmk), 0, 1)
    return beeld


def portret(beeld, b=1600, h=2000):
    staand = cv2.rotate(beeld, cv2.ROTATE_90_CLOCKWISE)     # neus boven
    return cv2.resize(staand, (b, h), interpolation=cv2.INTER_AREA)


def uitsnede(beeld, cx, cy, b, h, B=1600, H=2000):
    st = cv2.rotate(beeld, cv2.ROTATE_90_CLOCKWISE)
    # in het staande beeld: x = CH - y_liggend, y = x_liggend
    x, y = CH - cy, cx
    stuk = st[int(y - h / 2):int(y + h / 2), int(x - b / 2):int(x + b / 2)]
    groot = cv2.resize(stuk, (B, H), interpolation=cv2.INTER_CUBIC)
    zacht = cv2.GaussianBlur(groot, (0, 0), 1.2)
    return np.clip(groot + (groot - zacht) * 0.6, 0, 1)


def bewaar(img, pad, max_kb=190):
    """jpg onder de max_kb: eerst kwaliteit omlaag tot 72, daarna iets kleiner (Shopify verkleint toch)."""
    basis = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    for schaal in (1, 0.9, 0.8, 0.72, 0.64):
        im = basis if schaal == 1 else basis.resize((int(basis.width * schaal), int(basis.height * schaal)), Image.LANCZOS)
        for q in (88, 84, 80, 76, 72):
            im.save(pad, quality=q, optimize=True, progressive=True)
            if pad.stat().st_size < max_kb * 1000:
                return


def hexkleur(hx):
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))


# bandkleur per ontwerp (zelfde als in tools/producten/producten.py)
# dusty blue gemeten op de foto, op studiolicht gebracht
BLAUW, NAVY_B, BABY_B, TERRA_B, ROSE_B = '#67809F', '#2A3A58', '#B5CBE4', '#B9603F', '#E3AFA9'
TASSEN = {'draagtas-tegel': BLAUW, 'draagtas-tegel-navy': NAVY_B, 'draagtas-golfjes': BABY_B, 'draagtas-zonsondergang': TERRA_B,
          'draagtas-schelp': ROSE_B, 'draagtas-ruit': NAVY_B, 'draagtas-duin': TERRA_B, 'draagtas-salie': NAVY_B, 'draagtas-navy': BLAUW}

if __name__ == '__main__':
    import sys
    DOEL = ROOT / 'docs' / 'producten' / 'beelden'
    THEMA = ROOT / 'theme' / 'assets'
    keuze = sys.argv[1:] or list(TASSEN)
    for h in keuze:
        beeld = maak(None if h == 'draagtas-tegel' else variant_stof(h), band=hexkleur(TASSEN[h]))
        xm = BX0 + LB * 0.5
        # stringer altijd in het midden van het beeld
        bewaar(uitsnede(beeld, xm, BY, 1720, 2150), DOEL / f'{h}-1.jpg')
        bewaar(portret(beeld), DOEL / f'{h}-2.jpg')
        # detail: label en het hele handvat
        bewaar(uitsnede(beeld, xm, 790, 1080, 1350), DOEL / f'{h}-3.jpg')
        if h == 'draagtas-tegel':
            for n in (1, 2, 3):
                src = DOEL / f'{h}-{n}.jpg'
                img = np.asarray(Image.open(src)).astype(np.float32) / 255
                bewaar(img, THEMA / f'tt-product-{n}.jpg')
                bewaar(cv2.resize(img, (800, 1000), interpolation=cv2.INTER_AREA), THEMA / f'tt-product-{n}-800.jpg')
        print('klaar', h)
