"""Studio-productfoto's van de accessoires (pet, bucket hat, canvas tas, strandhanddoek, stickerset).

Eén stijl voor alles (stijl.py): recht van voren of recht van boven, gecentreerd, op naadloos papier of zand,
raamlicht linksboven. Basis is telkens een echte stockfoto van het blanco product op een effen achtergrond
(docs/producten/stock/flatlay/, bronnen in docs/producten/stock/bronnen.json), vrijstaand geknipt.

Gebruik: python3 tools/producten/flatlay_accessoires.py [pet bucket tas handdoek stickers proef]
"""
import pathlib, sys
import cv2
import numpy as np

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import stijl as ST      # noqa: E402
import mockup as MK     # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock' / 'flatlay'
REF = ROOT / 'docs' / 'producten' / 'referentie'
ART = HIER / 'uit_echt'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
PROEF = ROOT / 'docs' / 'producten' / 'proef'
NAVY, CREME = '#22324F', '#F3ECDD'


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def art(pad, kleur=None):
    a = MK.laad_art(pad)
    if kleur:
        a = a.copy(); a[..., :3] = hexrgb(kleur)
    return a


def grabcut(img, rect, schaal=0.35, iter_=8, zeker_achter=None):
    """Product uit een effen studioachtergrond knippen. rect = (x0, y0, x1, y1) ruim om het product."""
    h, w = img.shape[:2]
    sm = cv2.resize((np.clip(img, 0, 1) * 255).astype(np.uint8), (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_AREA)
    sm = cv2.cvtColor(sm, cv2.COLOR_RGB2BGR)
    m = np.zeros(sm.shape[:2], np.uint8)
    x0, y0, x1, y1 = [int(v * schaal) for v in rect]
    bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(sm, m, (x0, y0, x1 - x0, y1 - y0), bg, fg, iter_, cv2.GC_INIT_WITH_RECT)
    fgm = ((m == 1) | (m == 3)).astype(np.float32)
    fgm = cv2.resize(fgm, (w, h), interpolation=cv2.INTER_LINEAR)
    return fgm


def verfijn_rand(masker, img, straal=6):
    """Zachte, nette rand: masker sluiten, gaten vullen, grootste stuk, lichte erosie tegen halo's."""
    m = (masker > 0.5).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    vul = m.copy(); ff = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
    cv2.floodFill(vul, ff, (0, 0), 1)
    m = m | (1 - vul)
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (straal, straal)))
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.1)


# ---------- pet ----------
def pet_basis():
    """Blanco witte snapback recht van voren (Unsplash), vrijstaand en navy gekleurd."""
    img = MK.laad(STOCK / 'pet-wit-voor-1.jpg')
    L = MK.helderheid(img)
    h, w = L.shape
    gc = grabcut(img, (440, 780, 1960, 1790))
    # bol: GrabCut is daar betrouwbaar; onder de klepbovenkant zit slagschaduw die er niet bij hoort
    bol = (gc > 0.5).astype(np.uint8)
    bol[1628:] = 0
    xs = np.where(bol[1585])[0]
    bol[1585:, :xs.min()] = 0; bol[1585:, xs.max() + 1:] = 0     # zijpanelen lopen recht naar beneden
    # knoopje bovenop: GrabCut haakt daar in de achtergrond, dus als nette afgeronde vorm tekenen
    bol[:886] = 0
    knoop = np.zeros_like(bol)
    cv2.rectangle(knoop, (1164, 851), (1238, 895), 1, -1)
    cv2.ellipse(knoop, (1164, 869), (18, 18), 0, 0, 360, 1, -1)
    cv2.ellipse(knoop, (1238, 869), (18, 18), 0, 0, 360, 1, -1)
    cv2.rectangle(knoop, (1146, 869), (1256, 895), 1, -1)
    bol = np.maximum(bol, knoop)
    # gladde omtrek van de bol (de schaduwkant is in de foto rafelig)
    glad = cv2.GaussianBlur(bol.astype(np.float32), (0, 0), 5)
    bol = np.where(np.arange(bol.shape[0])[:, None] < 900, bol, (glad > 0.5).astype(np.uint8))
    bol[1628:] = 0
    # klep: per kolom tot de donkere schaduwlijn eronder, per rij zo breed als het lichte klepvlak
    pts = []
    for x in range(600, 1800, 6):
        col = L[1700:1765, x]
        donker = np.where(col < 0.15)[0]
        pts.append((x, 1700 + (donker[0] if len(donker) else 30) - 1))
    for y in range(1630, 1700, 4):
        xs = np.where(L[y, 400:2000] > 0.78)[0] + 400
        xs = xs[(xs > 560) & (xs < 1840)]
        if len(xs):
            pts += [(xs.min(), y), (xs.max(), y)]
    klep = np.zeros((h, w), np.uint8)
    cv2.fillPoly(klep, [cv2.convexHull(np.array(pts, np.int32))], 1)
    m = verfijn_rand(np.maximum(bol, klep).astype(np.float32), img, straal=5)
    # spiegelen: in de stockfoto valt het licht van rechts, in onze studio van linksboven
    return img[:, ::-1].copy(), m[:, ::-1].copy()


def stof_kleur(img, m, doel_hex, gamma=1.25, glans=0.10):
    """Witte stof naar een donkere kleur: schaduwen worden dieper (gamma), lichte delen krijgen een vleug glans."""
    L = MK.helderheid(img)
    ref = float(np.percentile(L[m > 0.5], 85))
    s = np.clip(L / ref, 0, 1.15)
    doel = hexrgb(doel_hex)
    nieuw = doel[None, None] * (s ** gamma)[..., None] + glans * np.clip(s - 0.92, 0, None)[..., None] * 3
    # fijne weefselstructuur van de stockfoto blijft zichtbaar
    fijn = (L - cv2.GaussianBlur(L, (0, 0), 1.6))[..., None]
    nieuw = np.clip(nieuw + fijn * 0.55, 0, 1)
    return img * (1 - m[..., None]) + nieuw * m[..., None]


def borduur(img, a, cx, cy, breedte, draai=0.0, steek=4.2, hoek=12.0, schaduw_bron=None, zaad=3):
    """Geborduurd logo: satijnsteek (glanzende draadjes, schuin), iets bol (licht linksboven, schaduw rechtsonder),
    stof trekt licht rond het borduursel, en de lichtval van het product valt eroverheen.
    schaduw_bron: de helderheid van het product (0..1, 1 = normaal belicht)."""
    h, w = img.shape[:2]
    ah, aw = a.shape[:2]
    s = breedte / aw
    M = cv2.getRotationMatrix2D((aw / 2, ah / 2), draai, s)
    M[0, 2] += cx - aw / 2; M[1, 2] += cy - ah / 2
    laag = cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
    al = laag[..., 3]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rng = np.random.default_rng(zaad)
    # satijnsteek: evenwijdige draadjes, elk met een rond profiel, eigen helderheid en vezelstreepjes in de lengte
    t = np.deg2rad(hoek)
    jit = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 4) * 0.35
    u = (yy * np.cos(t) - xx * np.sin(t)) / steek + jit
    idx = np.floor(u).astype(np.int64)
    frac = u - idx
    profiel = np.sin(np.pi * frac) ** 0.6
    eigen = rng.normal(0, 1, 4096).astype(np.float32)[idx % 4096]
    vezel = rng.normal(0, 1, (h, w)).astype(np.float32)
    vezel = cv2.GaussianBlur(vezel, (0, 0), sigmaX=steek * 1.6, sigmaY=0.5)
    vezel = vezel / (vezel.std() + 1e-6)
    draad = 0.84 + 0.17 * profiel + 0.035 * eigen + 0.025 * vezel
    # glimlicht op de draadjes: sterker waar het licht van linksboven komt
    # bolling van het borduursel
    hoog = cv2.GaussianBlur(al, (0, 0), 2.6)
    gx = cv2.Sobel(hoog, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(hoog, cv2.CV_32F, 0, 1, ksize=3)
    reliëf = 1 - (gx * 0.62 + gy * 0.78) * 0.9            # rand linksboven licht, rechtsonder donker
    kleur = laag[..., :3] * (draad * reliëf)[..., None]
    donker = 1 - MK.helderheid(laag[..., :3])
    kleur = kleur + (0.05 * profiel * donker * reliëf)[..., None]         # glans van het garen, zichtbaar op donker garen
    if schaduw_bron is not None:
        kleur = kleur * np.clip(schaduw_bron, 0.35, 1.2)[..., None]
    # stof: slagschaduw van het borduursel en een licht 'getrokken' rand
    sch = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, 2.5], [0, 1, 3.5]]), (w, h)), (0, 0), 2.4)
    trek = cv2.GaussianBlur(al, (0, 0), 7) * (1 - al)
    img = img * (1 - (0.26 * sch * (1 - al) + 0.05 * trek))[..., None]
    rand = cv2.GaussianBlur(al, (0, 0), 0.7)
    return img * (1 - rand[..., None]) + np.clip(kleur, 0, 1) * rand[..., None]


def sticker_op_vlak(img, st, quad, licht=None, glans=0.06):
    """Vinylsticker op een vlak in perspectief (quad: linksboven, rechtsboven, rechtsonder, linksonder)."""
    h, w = img.shape[:2]
    sh, sw = st.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), np.float32(quad))
    laag = cv2.warpPerspective(st, M, (w, h), flags=cv2.INTER_AREA)
    a = laag[..., 3:4]
    kleur = laag[..., :3]
    if licht is not None:
        kleur = kleur * np.clip(licht, 0.5, 1.15)[..., None]
    # vinyl: een vleugje glans en een haarfijne schaduwrand
    kleur = kleur + glans
    sch = cv2.GaussianBlur(cv2.warpAffine(a[..., 0], np.float32([[1, 0, 1.0], [0, 1, 1.5]]), (w, h)), (0, 0), 1.2)
    img = img * (1 - 0.35 * sch * (1 - a[..., 0]))[..., None]
    return img * (1 - a) + np.clip(kleur, 0, 1) * a


def naad_weg(img, x0, x1, y0, y1, zacht=10):
    """Verticale naad lokaal wegretoucheren (alleen horizontaal uitsmeren, de verticale lichtval blijft)."""
    uit = img.copy()
    stuk = img[y0:y1, x0 - 40:x1 + 40]
    glad = cv2.GaussianBlur(stuk, (0, 0), sigmaX=14, sigmaY=0.01)
    fijn = stuk - cv2.GaussianBlur(stuk, (0, 0), 1.2)
    m = np.zeros(stuk.shape[:2], np.float32); m[:, 40:-40] = 1
    m = cv2.GaussianBlur(m, (0, 0), zacht)[..., None]
    uit[y0:y1, x0 - 40:x1 + 40] = stuk * (1 - m) + (glad + fijn * 0.4) * m
    return uit


def kopie_schaal(img, m, schaal):
    if schaal == 1:
        return img, m
    h, w = m.shape
    return (cv2.resize(img, (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_CUBIC),
            cv2.resize(m, (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_LINEAR))


def oorsprong(m):
    """Linksboven van de uitsnede die ST.vrijstaand maakt (om punten op het product terug te vinden)."""
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
    ys, xs = np.where(a > 0.02)
    return xs.min(), ys.min(), xs.max() + 1 - xs.min(), ys.max() + 1 - ys.min()


def midden_voor(m, punt, s, doel=(800, 1000)):
    """Waar ST.leg het product moet neerleggen zodat 'punt' (in fotocoördinaten) op 'doel' in beeld valt."""
    x0, y0, w, h = oorsprong(m)
    return (doel[0] - (punt[0] - x0 - w / 2) * s, doel[1] - (punt[1] - y0 - h / 2) * s)


def opslaan(img, naam, max_kb=195):
    """Afwerking en ST.bewaar zoals overal. Is zand of stof dan nog te zwaar (eis: onder 200 kB), dan eerst minder
    korrel (ruis is duur in jpg), en pas daarna lagere kwaliteit en een fractie zachter."""
    from PIL import Image
    pad = ST.bewaar(ST.afwerking(img), DOEL / f'{naam}.jpg')
    if pad.stat().st_size <= max_kb * 1000:
        print('foto', naam, pad.stat().st_size // 1000, 'kB'); return
    for korrel, zacht in [(0.008, 0), (0.005, 0), (0.003, 0.35), (0.0, 0.5), (0.0, 0.7)]:
        bron = ST.afwerking(img, korrel=korrel)
        if zacht:
            bron = cv2.GaussianBlur(bron, (0, 0), zacht)
        im = Image.fromarray((np.clip(bron, 0, 1) * 255).astype(np.uint8))
        for q in range(80, 57, -3):
            im.save(pad, quality=q, optimize=True, progressive=True)
            if pad.stat().st_size <= max_kb * 1000:
                print('foto', naam, pad.stat().st_size // 1000, 'kB', 'korrel', korrel, 'q', q); return
    print('LET OP te groot', naam, pad.stat().st_size // 1000, 'kB')


def pet_navy_rgba(schaal=1.0):
    """Navy snapback recht van voren: crème geborduurd board-icoon, onze klepsticker op de klep.
    Geeft (rgb, masker, punten) terug op de gevraagde schaal van de stockfoto."""
    img, m = pet_basis()
    img, m = kopie_schaal(img, m, schaal)
    k = schaal
    w = img.shape[1]
    nx = (w / k - 1 - 1200) * k                         # middennaad na spiegelen
    cx, cy, br = nx + 2 * k, 1240 * k, 128 * k
    ico = art(REF / 'icoon-navy.png', CREME)
    hoog = br * ico.shape[0] / ico.shape[1]
    top = cy - hoog / 2
    # in de openingen tussen de strepen van het icoon is geen naad te zien: het icoon ligt eroverheen
    img = naad_weg(img, int(nx - 24 * k), int(nx + 24 * k), int(top + 0.42 * hoog), int(top + 0.86 * hoog), zacht=6 * k)
    L0 = MK.helderheid(img)
    ref = float(np.percentile(L0[m > 0.5], 85))
    licht = cv2.GaussianBlur(L0, (0, 0), 30 * k) / ref        # grove lichtval op de pet, zonder naden
    p = stof_kleur(img, m, NAVY)
    p = borduur(p, ico, cx, cy, br, hoek=3, steek=2.7 * k, schaduw_bron=licht ** 0.6)
    st = MK.laad_art(ART / 'petsticker.png')
    x0, x1, y0, y1 = cx + 170 * k, cx + 560 * k, 1636 * k, 1694 * k
    quad = [(x0 + 7 * k, y0), (x1 - 3 * k, y0), (x1 + 4 * k, y1), (x0, y1)]
    p = sticker_op_vlak(p, st, quad, licht=licht ** 0.5)
    return p, m, {'icoon': (cx, cy), 'sticker': ((x0 + x1) / 2, (y0 + y1) / 2)}


def pet():
    p, m, pt = pet_navy_rgba()
    rgba = ST.vrijstaand(p, m)
    # 1: hero, groot en recht van voren
    opslaan(ST.leg(ST.achtergrond('rose'), rgba, breedte=1420, midden=(800, 1010), hoogte=16), 'pet-navy-1')
    # 2: de hele pet met ruimte eromheen, zoals een packshot
    opslaan(ST.leg(ST.achtergrond('rose', zaad=2), rgba, breedte=1060, midden=(800, 1030), hoogte=14), 'pet-navy-2')
    # 3: detail van borduursel en klepsticker, op dubbele resolutie opgebouwd
    k = 2.0
    p2, m2, pt2 = pet_navy_rgba(schaal=k)
    rgba2 = ST.vrijstaand(p2, m2)
    s = 1.0
    doelpunt = (pt2['icoon'][0] * 0.55 + pt2['sticker'][0] * 0.45, pt2['icoon'][1] * 0.5 + pt2['sticker'][1] * 0.5)
    mid = midden_voor(m2, doelpunt, s, (800, 980))
    opslaan(ST.leg(ST.achtergrond('rose', zaad=3), rgba2, breedte=rgba2.shape[1] * s, midden=mid, hoogte=20), 'pet-navy-3')


# ---------- bucket hat ----------
def bucket_rgba(schaal=1.0):
    """Blanco bucket hat (Unsplash, olijf, studio op wit), omgekleurd naar crème #E9DFCB, navy board-icoon geborduurd."""
    import echt as E
    img = MK.laad(STOCK / 'buckethat-blanco-1.jpg')
    m = E.omkleur_masker(img, 0.06, (800, 640))
    m = verfijn_rand(m, img, straal=3)
    img, m = kopie_schaal(img, m, schaal)
    k = schaal
    L = MK.helderheid(img)
    ref = float(np.percentile(L[m > 0.5], 58))
    s_ = np.clip(L / ref, 0, 1.5)
    doel = hexrgb('#E9DFCB')
    # crème stof: schaduwen iets warmer, de gewassen structuur blijft
    nieuw = doel[None, None] * (s_ ** 0.9)[..., None] * np.array([1.0, 0.985, 0.96], np.float32)
    p = img * (1 - m[..., None]) + np.clip(nieuw, 0, 1) * m[..., None]
    licht = cv2.GaussianBlur(L, (0, 0), 30 * k) / ref
    cx, cy = 800 * k, 600 * k
    p = borduur(p, art(REF / 'icoon-navy.png', NAVY), cx, cy, 78 * k, hoek=3, steek=2.7 * k, schaduw_bron=licht ** 0.8, zaad=5)
    return p, m, {'icoon': (cx, cy)}


def bucket():
    p, m, pt = bucket_rgba()
    rgba = ST.vrijstaand(p, m)
    opslaan(ST.leg(ST.achtergrond('baby'), rgba, breedte=1400, midden=(800, 1000), hoogte=16), 'bucket-hat-tegel-1')
    opslaan(ST.leg(ST.achtergrond('baby', zaad=2), rgba, breedte=1060, midden=(800, 1020), hoogte=14), 'bucket-hat-tegel-2')
    k = 2.0
    p2, m2, pt2 = bucket_rgba(schaal=k)
    rgba2 = ST.vrijstaand(p2, m2)
    s = 1.15
    mid = midden_voor(m2, (pt2['icoon'][0], pt2['icoon'][1] + 140 * k), s, (800, 1000))
    opslaan(ST.leg(ST.achtergrond('baby', zaad=3), rgba2, breedte=rgba2.shape[1] * s, midden=mid, hoogte=20), 'bucket-hat-tegel-3')


# ---------- strandhanddoek ----------
FABRIEK = ROOT / 'docs' / 'producten' / 'fabriek'
BAND = hexrgb('#EEE5D2')          # effen crème zoom aan de korte kanten, zelfde garen als de franjes


def tegel_lap(b, h, tegel_b, zaad=7):
    """Lap van de echte jacquardtegels (fabriek/tegel-*.png, uit de fabrieksfoto), nooit twee dezelfde naast elkaar."""
    import random
    tegels = [MK.laad(FABRIEK / f'tegel-{i:02d}.png') for i in range(10)]
    th, tw = tegels[0].shape[:2]
    tegel_h = int(round(tegel_b * th / tw))
    tegels = [cv2.resize(t, (tegel_b, tegel_h), interpolation=cv2.INTER_CUBIC if tegel_b > tw else cv2.INTER_AREA) for t in tegels]
    kol, rij = b // tegel_b + 2, h // tegel_h + 2
    rnd = random.Random(zaad)
    raster = [[None] * kol for _ in range(rij)]
    doek = np.zeros((rij * tegel_h, kol * tegel_b, 3), np.float32)
    for r in range(rij):
        for k in range(kol):
            buren = {raster[r - 1][k] if r else None, raster[r][k - 1] if k else None,
                     raster[r - 1][k - 1] if r and k else None, raster[r - 1][k + 1] if r and k + 1 < kol else None}
            raster[r][k] = rnd.choice([i for i in range(10) if i not in buren])
            doek[r * tegel_h:(r + 1) * tegel_h, k * tegel_b:(k + 1) * tegel_b] = tegels[raster[r][k]]
    # de tegelfoto's zijn iets donker en rood: naar de echte kleur van de stof bij daglicht
    doek = np.clip(doek * 1.08 + 0.02, 0, 1)
    return doek[:h, :b]


def weefsel(shape, zaad=1, sterkte=0.035, periode=3.2):
    """Fijne platbinding: kruisende draadjes, zichtbaar in de effen zoom."""
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rng = np.random.default_rng(zaad)
    ruis = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.7)
    schering = np.sin(xx / periode * np.pi) * np.sin(yy / periode * np.pi)
    slub = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.6, sigmaY=9) * 2.5
    return 1 + sterkte * (0.6 * schering + 0.5 * ruis + 0.4 * slub)


def franje(b, lengte=88, steek=23, zaad=4, kleur=None):
    """Franjes onder een rand van breedte b: getwijnde koordjes met een knoopje, rafelig eindje. Geeft rgb, alpha."""
    kleur = BAND if kleur is None else kleur
    rng = np.random.default_rng(zaad)
    S = 3                                             # supersampling
    H, W = int((lengte + 30) * S), int((b + 20) * S)
    a = np.zeros((H, W), np.float32)
    lijn = np.zeros((H, W), np.float32)
    for x in np.arange(steek * 0.6, b, steek):
        x0 = (x + rng.normal(0, 2.2) + 10) * S
        L = (lengte + rng.normal(0, 9)) * S
        dx = rng.normal(0, 13) * S
        bocht = rng.normal(0, 8) * S
        t = np.linspace(0, 1, 40)
        px = x0 + dx * t + bocht * np.sin(np.pi * t)
        py = 2 * S + L * t
        pts = np.stack([px, py], 1).astype(np.int32)
        dik = int(max(4, rng.normal(7.0, 0.7)) * S)
        cv2.polylines(a, [pts], False, 1.0, dik, cv2.LINE_AA)
        # twijnlijntjes schuin over het koord
        for tt in np.arange(0.02, 0.93, 4.2 * S / L):
            i = int(tt * 39)
            cx, cy = px[i], py[i]
            cv2.line(lijn, (int(cx - dik * 0.55), int(cy - dik * 0.35)), (int(cx + dik * 0.55), int(cy + dik * 0.35)), 1.0, max(1, S), cv2.LINE_AA)
        # knoopje vlak onder de zoom
        cv2.ellipse(a, (int(px[3]), int(py[3] + 6 * S)), (int(dik * 0.85), int(dik * 0.7)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        # rafelig eindje: een paar losse vezels
        for _ in range(4):
            ex = px[-1] + rng.normal(0, 2.5) * S
            ey = py[-1] + rng.uniform(4, 12) * S
            cv2.line(a, (int(px[-4]), int(py[-4])), (int(ex), int(ey)), 0.8, max(1, S), cv2.LINE_AA)
    a = np.clip(a, 0, 1)
    # rond profiel: midden licht, randen donker; licht van linksboven
    d = cv2.distanceTransform((a > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    prof = np.clip(d / (2.8 * S), 0, 1) ** 0.5
    gx = cv2.Sobel(cv2.GaussianBlur(a, (0, 0), S), cv2.CV_32F, 1, 0); gy = cv2.Sobel(cv2.GaussianBlur(a, (0, 0), S), cv2.CV_32F, 0, 1)
    licht = 0.86 + 0.18 * prof - 0.02 * (gx * 0.6 + gy * 0.8)
    licht = licht * (1 - 0.18 * cv2.GaussianBlur(lijn, (0, 0), 0.6 * S))
    rgb = kleur[None, None] * licht[..., None] * weefsel((H, W), zaad, 0.05, 1.5 * S)[..., None]
    rgb = cv2.resize(rgb, (W // S, H // S), interpolation=cv2.INTER_AREA)
    a = cv2.resize(a, (W // S, H // S), interpolation=cv2.INTER_AREA)
    return np.clip(rgb, 0, 1)[:, 10:10 + b], a[:, 10:10 + b]


def geweven_label(b=150):
    """Klein geweven labeltje: navy met crème TIDE TODE (uit neklabel-creme), ingeweven structuur."""
    tekst = MK.laad_art(ART / 'neklabel-creme.png')
    tekst = tekst[:int(tekst.shape[0] * 0.42)]
    tekst = MK.laad_art_from_array(tekst) if hasattr(MK, 'laad_art_from_array') else tekst
    ys, xs = np.where(tekst[..., 3] > 0.05)
    tekst = tekst[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h = int(b * 0.36)
    lab = np.ones((h, b, 3), np.float32) * hexrgb(NAVY)
    tb = int(b * 0.78)
    th = int(tb * tekst.shape[0] / tekst.shape[1])
    t = cv2.resize(tekst, (tb, th), interpolation=cv2.INTER_AREA)
    y0, x0 = (h - th) // 2, (b - tb) // 2
    al = t[..., 3:4]
    lab[y0:y0 + th, x0:x0 + tb] = lab[y0:y0 + th, x0:x0 + tb] * (1 - al) + t[..., :3] * al
    yy = np.arange(h, dtype=np.float32)[:, None]
    lab = lab * (1 + 0.05 * np.sin(yy * np.pi / 1.3))[..., None] * weefsel((h, b), 9, 0.04, 1.2)[..., None]
    # randjes iets omgerold, stiksel rondom
    rand = np.ones((h, b), np.float32)
    rand[:2] = rand[-2:] = 0.8; rand[:, :2] = rand[:, -2:] = 0.8
    lab = lab * rand[..., None]
    st = np.zeros((h, b), np.float32)
    st[3, 4:-4] = st[-4, 4:-4] = 1; st[3:-3, 3] = st[3:-3, -4] = 1
    st = st * ((np.arange(b)[None] // 3 + np.arange(h)[:, None] // 3) % 2 == 0)
    lab = lab * (1 - 0.5 * st[..., None]) + hexrgb('#1A2840') * 0.5 * st[..., None]
    return np.clip(lab, 0, 1)


def gevouwen_handdoek(B=1120, H=1400, tegel_b=165, zaad=11):
    """Strandhanddoek netjes gevouwen, recht van boven. Boven, links en rechts zijn vouwen (rond), onder komen beide
    korte kanten samen: de effen zoom met franjes en daaronder de tweede laag. Geeft rgba."""
    R = 44                                    # straal van de vouw
    rand = 52                                 # effen zoom
    fl = 92                                   # franjelengte
    totH = H + fl + 30
    rng = np.random.default_rng(zaad)
    # stof met kleine golving
    lap = tegel_lap(B + 2 * R + 40, H + 2 * R + 40, tegel_b, zaad)
    yy, xx = np.mgrid[0:totH, 0:B].astype(np.float32)
    golf_x = cv2.GaussianBlur(rng.normal(0, 1, (totH, B)).astype(np.float32), (0, 0), 60) * 90
    golf_y = cv2.GaussianBlur(rng.normal(0, 1, (totH, B)).astype(np.float32), (0, 0), 60) * 90
    # vouw: het patroon loopt over de ronde rand weg (verkorting)
    def boog(e):
        e = np.clip(e, 0, R)
        return R * np.pi / 2 - R * np.arccos(np.clip(1 - e / R, -1, 1))   # booglengte vanaf de bovenkant van de vouw
    el, er, eb = xx, B - 1 - xx, yy
    ux = xx.copy()
    ux = np.where(el < R, R - boog(el) * 1.0 + 0 * el, ux)
    ux = np.where(er < R, (B - 1) - R + boog(er), ux)
    uy = np.where(eb < R, R - boog(eb), yy)
    lap_w = cv2.remap(lap, ux + 20 + R + golf_x, uy + 20 + R + golf_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # zoom onderaan (bovenste laag), met een geweven randje
    zoom_y0 = H - rand
    zoom = (yy >= zoom_y0) & (yy < H)
    band = BAND[None, None] * weefsel((totH, B), zaad, 0.06, 1.6)[..., None]
    # twee smalle navy streepjes ingeweven in de zoom
    for sy in (zoom_y0 + 12, zoom_y0 + 19):
        streep = np.clip(1.6 - np.abs(yy - sy), 0, 1)[..., None] * zoom[..., None]
        band = band * (1 - streep) + hexrgb(NAVY)[None, None] * weefsel((totH, B), zaad + 5, 0.08, 1.6)[..., None] * streep
    stof = np.where(zoom[..., None], band, lap_w)
    # rijgsteek tussen patroon en zoom
    stof = stof * (1 - 0.18 * np.exp(-((yy - zoom_y0) / 1.6) ** 2))[..., None]
    # hoogteveld voor licht: ronde vouwen boven/links/rechts, iets bol in het midden
    def rond(e):
        e = np.clip(e, 0, R)
        return np.sqrt(np.clip(1 - (1 - e / R) ** 2, 0, 1)) * R
    hoog = np.minimum(np.minimum(rond(el), rond(er)), rond(eb))
    hoog = hoog + cv2.GaussianBlur(rng.normal(0, 1, (totH, B)).astype(np.float32), (0, 0), 70) * 120
    gy_, gx_ = np.gradient(cv2.GaussianBlur(hoog, (0, 0), 2))
    schaduw = 1 - 0.75 * (gx_ * 0.62 + gy_ * 0.78)
    # waar de vouw naar beneden wegdraait valt minder licht op de stof
    schaduw = schaduw * (0.80 + 0.20 * np.clip(np.minimum(np.minimum(el, er), eb) / R, 0, 1) ** 0.5)
    schaduw = np.clip(schaduw, 0.5, 1.12)
    stof = stof * schaduw[..., None]
    # silhouet: rechthoek met heel licht golvende randen
    golf = cv2.GaussianBlur(rng.normal(0, 1, (4, max(B, totH))).astype(np.float32), (0, 0), sigmaX=40, sigmaY=0.01) * 60
    alpha = np.zeros((totH, B), np.float32)
    links = 1.5 + golf[0, :totH][:, None]; rechts = B - 1.5 + golf[1, :totH][:, None]; boven = 1.5 + golf[2, :B][None]
    alpha = np.clip(np.minimum(np.minimum(xx - links, rechts - xx), yy - boven) + 0.5, 0, 1) * (yy < H)
    # tweede laag: steekt onderaan 14 px uit, iets naar rechts, in de schaduw van de bovenste
    l2 = ((yy >= H) & (yy < H + 14) & (xx > 6) & (xx < B - 3)).astype(np.float32)
    band2 = BAND[None, None] * 0.80 * weefsel((totH, B), zaad + 1, 0.06, 1.6)[..., None]
    band2 = band2 * (0.82 + 0.18 * np.clip((yy - H) / 14, 0, 1))[..., None]
    rgb = np.where((alpha > 0)[..., None], stof, band2)
    alpha = np.maximum(alpha, l2)
    # franjes van beide lagen, een beetje verspringend
    for laag_y, z, donker in [(H + 10, zaad + 2, 0.86), (H - 2, zaad + 3, 1.0)]:
        fr, fa = franje(B - 30, lengte=fl, steek=23, zaad=z)
        fr = fr * donker
        y0 = laag_y; x0 = 15
        hh = min(fa.shape[0], totH - y0)
        vlak = fa[:hh] * (1 - (alpha[y0:y0 + hh, x0:x0 + fa.shape[1]] if donker == 1.0 else 0) * 0)
        sub = rgb[y0:y0 + hh, x0:x0 + fa.shape[1]]
        suba = alpha[y0:y0 + hh, x0:x0 + fa.shape[1]]
        if donker < 1.0:
            # onderste franjes alleen waar de bovenste nog niets bedekken: eerst tekenen
            rgb[y0:y0 + hh, x0:x0 + fa.shape[1]] = sub * (1 - vlak[..., None]) + fr[:hh] * vlak[..., None]
            alpha[y0:y0 + hh, x0:x0 + fa.shape[1]] = np.maximum(suba, vlak)
        else:
            # franje-schaduw op de laag eronder, dan de franjes zelf
            sch = cv2.GaussianBlur(np.roll(np.roll(vlak, 3, 0), 2, 1), (0, 0), 2.5)
            rgb[y0:y0 + hh, x0:x0 + fa.shape[1]] = sub * (1 - 0.35 * sch * suba)[..., None]
            rgb[y0:y0 + hh, x0:x0 + fa.shape[1]] = rgb[y0:y0 + hh, x0:x0 + fa.shape[1]] * (1 - vlak[..., None]) + fr[:hh] * vlak[..., None]
            alpha[y0:y0 + hh, x0:x0 + fa.shape[1]] = np.maximum(alpha[y0:y0 + hh, x0:x0 + fa.shape[1]], vlak)
    # geweven label op de zoom, links
    lab = geweven_label(104)
    lh, lw = lab.shape[:2]
    ly, lx = zoom_y0 + 24, 64
    sch = np.zeros((totH, B), np.float32); sch[ly + 2:ly + lh + 2, lx + 2:lx + lw + 2] = 1
    sch = cv2.GaussianBlur(sch, (0, 0), 1.6)
    rgb = rgb * (1 - 0.3 * sch * (1 - 0))[..., None]
    rgb[ly:ly + lh, lx:lx + lw] = lab * schaduw[ly:ly + lh, lx:lx + lw, None]
    return np.dstack([np.clip(rgb, 0, 1), alpha]).astype(np.float32)


def kreukels(B, H, zaad=0):
    """Zachte plooien uit een echte foto van een strandlaken op zand (stock/handdoek2-zand-1.jpg, Unsplash):
    alleen de lichtval van de plooien, strepen en harde zon eruit, zacht gemaakt voor raamlicht."""
    f = MK.laad(ROOT / 'docs' / 'producten' / 'stock' / 'handdoek2-zand-1.jpg')
    L = MK.helderheid(f)[830:2133, 0:1075]
    L = cv2.morphologyEx(L, cv2.MORPH_OPEN, np.ones((15, 3), np.uint8))          # witte streepjes weg
    m = np.zeros(L.shape, np.uint8); m[100:420, 860:1075] = 255                       # zonnebril
    L = cv2.inpaint((np.clip(L, 0, 1) * 255).astype(np.uint8), m, 25, cv2.INPAINT_TELEA).astype(np.float32) / 255
    L = cv2.medianBlur((np.clip(L, 0, 1) * 255).astype(np.uint8), 9).astype(np.float32) / 255
    L = cv2.GaussianBlur(L, (0, 0), 13)
    rel = L / (cv2.GaussianBlur(L, (0, 0), 160) + 1e-3)
    rel = cv2.resize(rel, (B, H), interpolation=cv2.INTER_CUBIC)
    return 1 + np.clip(rel - 1, -0.5, 0.4) * 0.8


def liggende_handdoek(B=1400, H=1700, tegel_b=104, zaad=21):
    """Uitgespreid laken, recht van boven: patroon met zachte plooien, zoom met streepjes, franjes en label onderaan."""
    rand, fl = 58, 96
    totH = H + fl + 30
    rng = np.random.default_rng(zaad)
    kr = kreukels(B, H, zaad)
    gy_, gx_ = np.gradient(cv2.GaussianBlur(kr, (0, 0), 6))
    lap = tegel_lap(B + 80, H + 80, tegel_b, zaad)
    yy, xx = np.mgrid[0:totH, 0:B].astype(np.float32)
    kr_v = np.pad(kr, ((0, totH - H), (0, 0)), mode='edge')
    gx_v = np.pad(gx_, ((0, totH - H), (0, 0)), mode='edge'); gy_v = np.pad(gy_, ((0, totH - H), (0, 0)), mode='edge')
    stof = cv2.remap(lap, xx + 40 + gx_v * 260, yy + 40 + gy_v * 260, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    zoom_y0 = H - rand
    zoom = (yy >= zoom_y0) & (yy < H)
    band = BAND[None, None] * weefsel((totH, B), zaad, 0.06, 1.6)[..., None]
    for sy in (zoom_y0 + 13, zoom_y0 + 20):
        streep = np.clip(1.6 - np.abs(yy - sy), 0, 1)[..., None] * zoom[..., None]
        band = band * (1 - streep) + hexrgb(NAVY)[None, None] * streep
    stof = np.where(zoom[..., None], band, stof)
    stof = stof * (1 - 0.18 * np.exp(-((yy - zoom_y0) / 1.6) ** 2))[..., None]
    stof = stof * kr_v[..., None]
    # label rechts op de zoom
    lab = geweven_label(104)
    lh, lw = lab.shape[:2]
    ly, lx = zoom_y0 + 26, B - 70 - lw
    sch = np.zeros((totH, B), np.float32); sch[ly + 2:ly + lh + 2, lx + 2:lx + lw + 2] = 1
    stof = stof * (1 - 0.3 * cv2.GaussianBlur(sch, (0, 0), 1.6))[..., None]
    stof[ly:ly + lh, lx:lx + lw] = lab * kr_v[ly:ly + lh, lx:lx + lw, None]
    golf = cv2.GaussianBlur(rng.normal(0, 1, (3, max(B, totH))).astype(np.float32), (0, 0), sigmaX=50, sigmaY=0.01) * 70
    alpha = np.clip(np.minimum(np.minimum(xx - 1.5 - golf[0, :totH][:, None], B - 1.5 + golf[1, :totH][:, None] - xx),
                               H - yy + golf[2, :B][None] * 0.3) + 0.5, 0, 1)
    rgb = stof * alpha[..., None]
    fr, fa = franje(B - 30, lengte=fl, steek=23, zaad=zaad + 2)
    y0, x0 = H - 3, 15
    hh = min(fa.shape[0], totH - y0)
    rgb[y0:y0 + hh, x0:x0 + fa.shape[1]] = rgb[y0:y0 + hh, x0:x0 + fa.shape[1]] * (1 - fa[:hh, :, None]) + fr[:hh] * fa[:hh, :, None]
    alpha[y0:y0 + hh, x0:x0 + fa.shape[1]] = np.maximum(alpha[y0:y0 + hh, x0:x0 + fa.shape[1]], fa[:hh])
    return np.dstack([np.clip(rgb, 0, 1), alpha]).astype(np.float32)


def handdoek_macro():
    """Detail: echte macrofoto van een platgeweven laken met getwijnde franjes (Unsplash), naar ons crème garen gekleurd,
    met de navy streepjes en het tegelpatroon evenwijdig aan de zoom, even onscherp als de foto daar is."""
    f = MK.laad(STOCK / 'handdoek-franje-macro-1.jpg')
    h, w = f.shape[:2]
    L = MK.helderheid(f)
    ref = float(np.percentile(L, 92))
    rgb = BAND[None, None] * np.clip(L / ref, 0, 1.2)[..., None] ** 1.05
    # zoomlijn (knoopjes) en loodrecht daarop, het laken in
    P1, P2 = np.array([960., 430.]), np.array([1640., 1420.])
    d = (P2 - P1) / np.linalg.norm(P2 - P1); n = np.array([d[1], -d[0]])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sd = (xx - P1[0]) * n[0] + (yy - P1[1]) * n[1]            # afstand tot de zoom, positief = laken
    langs = (xx - P1[0]) * d[0] + (yy - P1[1]) * d[1]
    # scherpte van de foto per plek (scherptediepte), om de toevoegingen even onscherp te maken
    lap_ = cv2.Laplacian(cv2.GaussianBlur(L, (0, 0), 3.0), cv2.CV_32F)
    scherp = cv2.GaussianBlur(np.abs(lap_), (0, 0), 60)
    lo, hi = np.percentile(scherp, 10), np.percentile(scherp, 97)
    scherp = np.clip((scherp - lo) / (hi - lo), 0, 1) ** 0.7
    begin = 360.0                                              # waar het patroon begint (zelfde verhouding als de zoom op het laken)
    laag = np.zeros((h, w, 3), np.float32); dek = np.zeros((h, w), np.float32)
    # tegelpatroon in de richting van de zoom
    tb = 300
    lap = tegel_lap(3200, 2600, tb, 5)
    u = (langs + 1200) % lap.shape[1]; v = np.clip(sd - begin, 0, None) % lap.shape[0]
    pat = cv2.remap(lap, u.astype(np.float32), v.astype(np.float32), cv2.INTER_LINEAR)
    pm = np.clip((sd - begin) / 3, 0, 1)
    laag = pat; dek = pm
    for off in (begin - 85, begin - 135):
        st = np.clip(11 - np.abs(sd - off), 0, 1)
        laag = laag * (1 - st[..., None]) + hexrgb(NAVY)[None, None] * st[..., None]
        dek = np.maximum(dek, st)
    # onscherp maken naar de scherptediepte: mengen tussen drie vervagingen
    lagen = [np.dstack([laag * dek[..., None], dek])]
    for sg in (4, 12, 28):
        lagen.append(cv2.GaussianBlur(lagen[0], (0, 0), sg))
    t = (1 - scherp) * 3
    i0 = np.clip(np.floor(t).astype(int), 0, 2); fr = (t - i0)[..., None]
    stapel = np.stack(lagen, 0)
    mix = np.take_along_axis(stapel, i0[None, ..., None].repeat(4, -1), 0)[0] * (1 - fr) + \
          np.take_along_axis(stapel, (i0 + 1)[None, ..., None].repeat(4, -1), 0)[0] * fr
    kl = mix[..., :3] / np.maximum(mix[..., 3:4], 1e-3); a = mix[..., 3:4]
    # garen geverfd: kleur maal de licht/donker en structuur van de foto
    schaduw = np.clip(L / ref, 0, 1.2)[..., None]
    rgb = rgb * (1 - a) + kl * schaduw * a
    rgb = np.clip(rgb * np.array([1.04, 1.0, 0.94], np.float32), 0, 1)
    # uitsnede 4:5 rond de knoopjes, naar 1600 x 2000
    x0, y0, cw, ch = 700, 0, 1280, 1600
    uit = cv2.resize(rgb[y0:y0 + ch, x0:x0 + cw], (1600, 2000), interpolation=cv2.INTER_CUBIC)
    return uit


def handdoek():
    fold = gevouwen_handdoek()
    opslaan(ST.leg(ST.achtergrond('zand'), fold, breedte=fold.shape[1], midden=(800, 1000), hoogte=9), 'strandhanddoek-tegel-1')
    lig = liggende_handdoek()
    H = 1700
    top = 1640 - H
    opslaan(ST.leg(ST.achtergrond('zand', zaad=2), lig, breedte=lig.shape[1], midden=(800, top + lig.shape[0] / 2), hoogte=4), 'strandhanddoek-tegel-2')
    opslaan(handdoek_macro(), 'strandhanddoek-tegel-3')


# ---------- canvas tas ----------
def tas_rgba():
    """Blanco naturel canvas tas plat van boven (Unsplash, op grijs), merkje weg, busje 'OP WEG NAAR ZEE' in de stof gedrukt."""
    import echt as E
    img = MK.laad(STOCK / 'tas-naturel-plat-1.jpg')
    stuk = (grabcut(img, (700, 90, 1760, 1530), schaal=0.5, iter_=10) > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(stuk)
    stuk = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    # hengsel: alleen de lichte stof, niet de slagschaduw ernaast
    L = MK.helderheid(img)
    achter = float(np.median(L[:40, :40]))
    hengsel = (cv2.GaussianBlur(L, (0, 0), 1.5) > achter + 0.035).astype(np.uint8)
    hengsel = cv2.morphologyEx(hengsel, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    hengsel = cv2.morphologyEx(hengsel, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    stuk[:490] = stuk[:490] & hengsel[:490]
    # kleine gaatjes dicht, de opening binnen het hengsel blijft open
    inv = (1 - stuk).astype(np.uint8)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n2):
        if st2[i, cv2.CC_STAT_AREA] < 20000:
            stuk[lab2 == i] = 1
    stuk = cv2.erode(stuk, np.ones((3, 3), np.uint8))
    m = cv2.GaussianBlur(stuk.astype(np.float32), (0, 0), 1.1)
    img = E.poets(img, 1576, 1404, 84, 84)
    img = np.clip(img * np.array([1.04, 1.0, 0.90], np.float32) * 1.04, 0, 1)        # naturel, ongebleekt katoen
    body = (m > 0.5).astype(np.float32)
    body[:480] = 0
    img = MK.zet_print(img, MK.laad_art(REF / 'hoodie-busje-rugprint-los.png'), 1214, 930, 520, verplaatsing=6,
                       schaduw_sterkte=0.9, structuur=0.6, dekking=0.95, masker=cv2.GaussianBlur(body, (0, 0), 1))
    return img, m, {'print': (1214, 930)}


def tas():
    p, m, pt = tas_rgba()
    rgba = ST.vrijstaand(p, m)
    opslaan(ST.leg(ST.achtergrond('zand'), rgba, hoogte_px=1720, midden=(800, 1000), hoogte=5), 'canvas-tas-1')
    # 2: op zandpapier, met een gevouwen strandlaken eronder dat er rechtsonder uitpiept
    doek = ST.achtergrond('zandpapier')
    laken = gevouwen_handdoek(B=760, H=980, tegel_b=112, zaad=31)
    doek = ST.leg(doek, laken, breedte=laken.shape[1], midden=(1060, 1290), hoogte=8)
    doek = ST.leg(doek, rgba, hoogte_px=1420, midden=(720, 900), hoogte=5)
    opslaan(doek, 'canvas-tas-2')
    # 3: detail van de print in het canvas
    s = 2.3
    mid = midden_voor(m, (pt['print'][0], pt['print'][1] + 20), s, (800, 1000))
    opslaan(ST.leg(ST.achtergrond('zand', zaad=3), rgba, breedte=rgba.shape[1] * s, midden=mid, hoogte=5), 'canvas-tas-3')


# ---------- stickers ----------
def vinyl(rgba, zaad=1, glans=0.05, hoek=-35):
    """Vinylglans: een brede zachte reflectie van het raam (linksboven) en een heel fijne papier-/vinylstructuur."""
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.deg2rad(hoek)
    u = (xx * np.cos(t) - yy * np.sin(t)) / max(h, w)
    band = np.exp(-((u - 0.15) / 0.22) ** 2) * glans + np.exp(-((u + 0.25) / 0.06) ** 2) * glans * 0.4
    rng = np.random.default_rng(zaad)
    vezel = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.8) * 0.006
    uit = rgba.copy()
    uit[..., :3] = np.clip(rgba[..., :3] * (1 + vezel[..., None]) + band[..., None], 0, 1)
    return uit


def schaal_rgba(a, breedte):
    h, w = a.shape[:2]
    return cv2.resize(a, (int(breedte), int(round(breedte * h / w))), interpolation=cv2.INTER_AREA if breedte < w else cv2.INTER_CUBIC)


def pel(rgba, diepte=0.30):
    """Sticker met de rechteronderhoek een stukje losgetrokken: de omgevouwen flap toont de witte achterkant.
    Geeft rgba en het flapmasker (voor de extra schaduw van de opstaande flap)."""
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    c = (w + h) * (1 - diepte / 2)                       # vouwlijn x + y = c
    a = rgba[..., 3]
    los = (xx + yy > c).astype(np.float32)
    # spiegelen over de lijn x + y = c: (x, y) -> (c - y, c - x)
    mx, my = (c - yy), (c - xx)
    flap_a = cv2.remap(a, mx, my, cv2.INTER_LINEAR, borderValue=0) * (xx + yy < c)
    zacht = np.clip((c - (xx + yy)) / 2.0, 0, 1)
    flap_a = flap_a * zacht
    afstand = (c - (xx + yy)) / np.sqrt(2)                # 0 bij de vouw
    rug = np.clip(0.97 - 0.10 * (afstand / (diepte * w * 0.7)) + 0.03 * np.exp(-(afstand / 6) ** 2), 0.8, 1.0)
    rug_rgb = np.array([0.95, 0.945, 0.935], np.float32)[None, None] * rug[..., None]
    uit = rgba.copy()
    uit[..., 3] = a * (1 - los)
    # waar de sticker al los is, schaduw van de flap op de sticker zelf
    sch = cv2.GaussianBlur(np.roll(np.roll(flap_a, 6, 0), 4, 1), (0, 0), 5)
    uit[..., :3] = uit[..., :3] * (1 - 0.25 * sch * (1 - flap_a))[..., None]
    uit[..., :3] = uit[..., :3] * (1 - flap_a[..., None]) + rug_rgb * flap_a[..., None]
    uit[..., 3] = np.maximum(uit[..., 3], flap_a)
    # vouwlijn iets donker
    vouw = np.exp(-(afstand / 1.5) ** 2) * (flap_a > 0.5)
    uit[..., :3] = uit[..., :3] * (1 - 0.15 * vouw[..., None])
    return uit, flap_a


def leg_met_flap(doek, rgba, flap, breedte, midden, hoogte=2.5):
    """ST.leg plus de extra, verdere schaduw van een opstaande flap."""
    h, w = rgba.shape[:2]
    s = breedte / w
    M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, s)
    M[0, 2] += midden[0] - w / 2; M[1, 2] += midden[1] - h / 2
    f = cv2.warpAffine(flap, M, (doek.shape[1], doek.shape[0]))
    sch = cv2.GaussianBlur(cv2.warpAffine(f, np.float32([[1, 0, 16], [0, 1, 22]]), (doek.shape[1], doek.shape[0])), (0, 0), 12)
    doek = doek * (1 - 0.22 * sch[..., None])
    return ST.leg(doek, rgba, breedte=breedte, midden=midden, hoogte=hoogte)


def stickers():
    # 1: het hele vel recht van boven op crème papier
    vel = MK.laad_art(ART / 'stickervel.png')
    vel = vinyl(vel, 3, 0.045)
    # hoekje rechtsonder komt een fractie omhoog: iets lichter en een zachte schaduwgradiënt
    h, w = vel.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    krul = np.clip(((xx / w) + (yy / h) - 1.72) / 0.28, 0, 1) ** 2
    vel[..., :3] = np.clip(vel[..., :3] * (1 + 0.035 * krul[..., None]), 0, 1)
    opslaan(ST.leg(ST.achtergrond('creme'), vel, breedte=1160, midden=(800, 1000), hoogte=3.5), 'stickerset-1')
    # 2: zes losse stickers netjes in een raster op zandpapier, eentje half losgetrokken
    doek = ST.achtergrond('zandpapier')
    namen = ['zonsondergang', 'zegel', 'tegelcirkel', 'golfrand', 'ovaal', 'pil']
    plekken = [(520, 560), (1080, 560), (520, 1060), (1080, 1060), (520, 1530), (1080, 1530)]
    for i, (naam, (x, y)) in enumerate(zip(namen, plekken)):
        st = vinyl(MK.laad_art(ART / f'sticker-{naam}.png'), 10 + i, 0.05)
        br = 440 if naam not in ('ovaal', 'pil') else 470
        if naam == 'zonsondergang':
            st, flap = pel(st, 0.34)
            doek = leg_met_flap(doek, st, flap, br, (x, y))
        else:
            doek = ST.leg(doek, st, breedte=br, midden=(x, y), hoogte=2.5)
    opslaan(doek, 'stickerset-2')
    # 3: detail, de losgetrokken sticker groot
    doek = ST.achtergrond('zandpapier', zaad=3)
    st = vinyl(MK.laad_art(ART / 'sticker-golfrand.png'), 21, 0.05)
    doek = ST.leg(doek, st, breedte=1000, midden=(1500, 1820), hoogte=2.5)
    st, flap = pel(vinyl(MK.laad_art(ART / 'sticker-zonsondergang.png'), 20, 0.06), 0.34)
    doek = leg_met_flap(doek, st, flap, 1250, (760, 900), hoogte=3)
    opslaan(doek, 'stickerset-3')


def proef():
    PROEF.mkdir(parents=True, exist_ok=True)
    p, m, _ = pet_navy_rgba()
    doek = ST.leg(ST.achtergrond('rose'), ST.vrijstaand(p, m), breedte=1160, midden=(800, 1030), hoogte=14)
    print(ST.bewaar(ST.afwerking(doek), PROEF / 'accessoires-proef-1.jpg', max_kb=400))


if __name__ == '__main__':
    stappen = sys.argv[1:] or ['pet', 'bucket', 'tas', 'handdoek', 'stickers']
    for s in stappen:
        globals()[s]()
