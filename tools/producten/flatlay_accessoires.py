"""Studio-productfoto's van de accessoires (pet, bucket hat, canvas tas, strandhanddoek, stickerset).

Eén stijl voor alles (stijl.py): recht van voren of recht van boven, gecentreerd, op naadloos papier of zand,
raamlicht linksboven. Basis is telkens een echte stockfoto van het blanco product op een effen achtergrond
(docs/producten/stock/flatlay/, bronnen in docs/producten/stock/bronnen.json), vrijstaand geknipt.

Gebruik: python3 tools/producten/flatlay_accessoires.py [proef|pet ...]
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
    bol[1632:] = 0
    xs = np.where(bol[1585])[0]
    bol[1585:, :xs.min()] = 0; bol[1585:, xs.max() + 1:] = 0     # zijpanelen lopen recht naar beneden
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
    # satijnsteek: evenwijdige draadjes met kleine onregelmatigheid in fase en dikte
    t = np.deg2rad(hoek)
    jit = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 3) * 1.4
    fase = (yy * np.cos(t) + xx * np.sin(t)) / steek * 2 * np.pi + jit
    draad = 0.5 + 0.5 * np.sin(fase)
    draad = 0.80 + 0.30 * draad ** 0.6
    # glimlicht op de draadjes: sterker waar het licht van linksboven komt
    # bolling van het borduursel
    hoog = cv2.GaussianBlur(al, (0, 0), 2.6)
    gx = cv2.Sobel(hoog, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(hoog, cv2.CV_32F, 0, 1, ksize=3)
    reliëf = 1 - (gx * 0.62 + gy * 0.78) * 1.6            # rand linksboven licht, rechtsonder donker
    kleur = laag[..., :3] * (draad * reliëf)[..., None]
    if schaduw_bron is not None:
        kleur = kleur * np.clip(schaduw_bron, 0.35, 1.2)[..., None]
    # stof: slagschaduw van het borduursel en een licht 'getrokken' rand
    sch = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, 2.5], [0, 1, 3.5]]), (w, h)), (0, 0), 2.4)
    trek = cv2.GaussianBlur(al, (0, 0), 7) * (1 - al)
    img = img * (1 - (0.40 * sch * (1 - al) + 0.10 * trek))[..., None]
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


def pet_navy():
    """Navy snapback recht van voren: crème geborduurd board-icoon, onze klepsticker op de klep."""
    img, m = pet_basis()
    L0 = MK.helderheid(img)
    ref = float(np.percentile(L0[m > 0.5], 85))
    licht = cv2.GaussianBlur(L0, (0, 0), 9) / ref        # lichtval op de pet, zonder naden
    p = stof_kleur(img, m, NAVY)
    # middennaad loopt op x = w-1-1200 na spiegelen; voorpaneel ca. y 900-1610
    cx = img.shape[1] - 1 - 1200 + 2
    p = borduur(p, art(REF / 'icoon-navy.png', CREME), cx, 1240, 128, hoek=8, schaduw_bron=licht ** 0.6)
    # klepsticker: recht op de klep, rechts van het midden (gezien vanaf de camera), sterk verkort door de kijkhoek
    st = MK.laad_art(ART / 'petsticker.png')
    x0, x1, y0, y1 = cx + 210, cx + 520, 1640, 1688
    quad = [(x0 + 6, y0), (x1 - 2, y0), (x1 + 4, y1), (x0, y1)]
    p = sticker_op_vlak(p, st, quad, licht=licht ** 0.5)
    return ST.vrijstaand(p, m)


def compositie_pet(rgba):
    doek = ST.achtergrond('rose')
    doek = ST.leg(doek, rgba, breedte=1160, midden=(800, 1030), hoogte=14)
    return ST.afwerking(doek)


def proef():
    PROEF.mkdir(parents=True, exist_ok=True)
    rgba = pet_navy()
    uit = ST.bewaar(compositie_pet(rgba), PROEF / 'accessoires-proef-1.jpg', max_kb=400)
    print(uit)


if __name__ == '__main__':
    stappen = sys.argv[1:] or ['proef']
    for s in stappen:
        globals()[s]()
