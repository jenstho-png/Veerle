"""Levensechte productfoto's: onze prints, labels en stickers op echte stockfoto's (Unsplash, zie docs/producten/stock/bronnen.json).

Per foto: merkjes van de stockfoto wegpoetsen, stof eventueel omkleuren (schaduwen blijven), print plaatsen die meebuigt
met de plooien (mockup.zet_print), en bijsnijden tot 1600 x 2000. Uitvoer naar docs/producten/beelden/<handle>-<n>.jpg.
"""
import math, pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import mockup as MK  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock'
REF = ROOT / 'docs' / 'producten' / 'referentie'
ART = HIER / 'uit_echt'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
NAVY, CREME = '#22324F', '#F3ECDD'


def foto(naam):
    return MK.laad(STOCK / naam)


def art(naam, kleur=None):
    a = MK.laad_art(naam if isinstance(naam, pathlib.Path) else (REF / naam if (REF / naam).exists() else ART / naam))
    if kleur:
        k = np.array([int(kleur[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
        a = a.copy(); a[..., :3] = k
    return a


def poets(img, x, y, b, h):
    """Merkje van de stockfoto weghalen door de omgeving in te laten lopen."""
    m = np.zeros(img.shape[:2], np.uint8)
    m[int(y - h / 2):int(y + h / 2), int(x - b / 2):int(x + b / 2)] = 255
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    uit = cv2.inpaint(u8, m, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
    # stofstructuur terug in het gepoetste vlak
    ruis = cv2.GaussianBlur(np.random.default_rng(1).normal(0, 0.012, img.shape[:2]).astype(np.float32), (0, 0), 0.8)[..., None]
    zacht = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 3)[..., None]
    return uit + ruis * zacht


def borduur(img, a, cx, cy, breedte, draai=0):
    """Geborduurd: iets verhoogd met licht boven en schaduw onder, en een draadstructuur."""
    h, w = img.shape[:2]
    ah, aw = a.shape[:2]
    s = breedte / aw
    M = cv2.getRotationMatrix2D((aw / 2, ah / 2), draai, s)
    M[0, 2] += cx - aw / 2; M[1, 2] += cy - ah / 2
    laag = cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
    al = laag[..., 3]
    sch = cv2.GaussianBlur(np.roll(np.roll(al, 3, 0), 2, 1), (0, 0), 2.2)
    img = img * (1 - 0.45 * (sch * (1 - al))[..., None])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    draad = 1 + 0.08 * np.sin((xx * 0.7 + yy * 0.7) * 1.9)
    rand = cv2.GaussianBlur(al, (0, 0), 1.5)
    licht = 1 + 0.12 * (np.roll(rand, -2, 0) - np.roll(rand, 2, 0))
    kleur = laag[..., :3] * (draad * licht)[..., None]
    return img * (1 - al[..., None]) + np.clip(kleur, 0, 1) * al[..., None]


def schoon(img, m, kleur=(0.965, 0.962, 0.955)):
    """Packshot: alles buiten het kledingstuk wordt een effen studioachtergrond met een zachte schaduw."""
    a = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5), np.uint8)), (0, 0), 1.5)[..., None]
    sch = cv2.GaussianBlur(np.roll(m, 18, 0), (0, 0), 22)[..., None]
    bg = np.array(kleur, np.float32)[None, None] * (1 - 0.18 * sch)
    return img * a + bg * (1 - a)


def bewaar(img, naam, achter=None, vul=0.86, uitsnede=None, rand=True):
    if uitsnede:
        x0, y0, x1, y1 = uitsnede
        img = img[y0:y1, x0:x1]
    if vul < 1 and rand:
        rand = np.concatenate([img[:6].reshape(-1, 3), img[-6:].reshape(-1, 3), img[:, :6].reshape(-1, 3), img[:, -6:].reshape(-1, 3)])
        kl = achter if achter is not None else np.median(rand, axis=0)
        p = int(max(img.shape[:2]) * 0.06)
        img = cv2.copyMakeBorder(img, p, p, p, p, cv2.BORDER_CONSTANT, value=[float(c) for c in kl])
        achter = kl
    staand = MK.naar_staand(img, achter=achter, vul=vul)
    MK.bewaar(staand, DOEL / f'{naam}.jpg')
    print('foto', naam)


def omkleur_masker(img, tol=0.06, zaad=None, verzadiging=False, vullen=True, sluit=41):
    """Kledingstuk = alles wat duidelijk afwijkt van de achtergrondkleur (mediaan van de rand),
    gaten gevuld, en alleen het stuk onder het zaadpunt (of het grootste)."""
    rand = np.concatenate([img[:6].reshape(-1, 3), img[-6:].reshape(-1, 3), img[:, :6].reshape(-1, 3), img[:, -6:].reshape(-1, 3)])
    achter = np.median(rand, axis=0)
    d = np.sqrt(((img - achter[None, None]) ** 2).sum(-1))
    if verzadiging:
        hsv = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
        d = np.maximum(d, (hsv[..., 1] > 90).astype(np.float32))
    stuk = (d > tol * 3).astype(np.uint8)
    stuk = cv2.morphologyEx(stuk, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    stuk = cv2.morphologyEx(stuk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(stuk)
    if n > 1:
        kies = lab[zaad[1], zaad[0]] if zaad else 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        stuk = (lab == kies).astype(np.uint8)
    if not vullen:
        # alleen kleine gaten (glimlichten) dichten, de grote opening blijft open
        dicht = cv2.morphologyEx(stuk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (sluit, sluit)))
        inv = (1 - dicht).astype(np.uint8)
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv)
        for i in range(1, n2):
            if st2[i, cv2.CC_STAT_AREA] < 25000:
                dicht[lab2 == i] = 1
        stuk = dicht
        return cv2.GaussianBlur(stuk.astype(np.float32), (0, 0), 1.2)
    # gaten vullen
    vul = stuk.copy(); ff = np.zeros((stuk.shape[0] + 2, stuk.shape[1] + 2), np.uint8)
    cv2.floodFill(vul, ff, (0, 0), 1)
    stuk = stuk | (1 - vul)
    return cv2.GaussianBlur(stuk.astype(np.float32), (0, 0), 1.2)


# ---------- kleding ----------
def shirt_masker(img, zwart=False):
    """Alleen het shirt: GrabCut voor de persoon/het kledingstuk, daarna huid, haar en jeans eruit (kleur)."""
    h, w = img.shape[:2]
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    hsv = cv2.cvtColor(u8, cv2.COLOR_RGB2HSV)
    L = MK.helderheid(img)
    if zwart:
        stuk = (L < 0.2).astype(np.uint8)
    else:
        s = 0.4
        sm = cv2.resize(cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), (int(w * s), int(h * s)))
        m = np.zeros(sm.shape[:2], np.uint8); bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
        cv2.grabCut(sm, m, (int(sm.shape[1] * .05), int(sm.shape[0] * .03), int(sm.shape[1] * .9), int(sm.shape[0] * .94)), bg, fg, 6, cv2.GC_INIT_WITH_RECT)
        gc = cv2.resize(((m == 1) | (m == 3)).astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
        stof = (hsv[..., 1] < 0.16 * 255) & (L > 0.33) if np.median(L[gc > 0]) > 0.5 else (hsv[..., 2] < 140) & (hsv[..., 0] > 95) & (hsv[..., 0] < 130)
        stuk = (gc & stof).astype(np.uint8)
    stuk = cv2.morphologyEx(stuk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(stuk)
    if n > 1:
        stuk = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    stuk = cv2.morphologyEx(stuk, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
    vul = stuk.copy(); ff = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(vul, ff, (0, 0), 1)
    stuk = stuk | (1 - vul)
    return cv2.GaussianBlur(stuk.astype(np.float32), (0, 0), 1.3)


def neklabel(img, art_naam, cx, cy, breedte, draai=0):
    return MK.zet_print(img, art(art_naam), cx, cy, breedte, draai=draai, verplaatsing=1.5, schaduw_sterkte=0.6, structuur=0.35, dekking=0.92)


CREME_T = '#EEE6D6'


def tshirts():
    # Zonsopkomst, crème. 1: voorkant aan de hanger (heavyweight), klein board op de borst, ons label in de nek
    t = foto('tshirt2-creme-1.jpg')
    t = np.clip(t * np.array([1.0, 0.975, 0.925], np.float32), 0, 1)     # ecru: hele foto iets warmer (shirt en muur zijn even licht)
    t = poets(t, 888, 2116, 110, 100)
    t = poets(t, 820, 762, 170, 44)
    t = neklabel(t, 'neklabel-navy.png', 815, 790, 120, draai=-2)
    t = MK.zet_print(t, art('icoon-navy.png', NAVY), 965, 960, 62, verplaatsing=4)
    bewaar(t, 't-shirt-lijn-naar-zee-1', vul=1.0, uitsnede=(0, 280, 1600, 2280))
    # 2: achterkant, gedragen
    t = foto('tshirt2-wit-rug-1.jpg')
    m = shirt_masker(t)
    t = MK.kleur_om(t, m, CREME_T, 1.0)
    t = MK.zet_print(t, art(ART / 'ontwerp-lijn-licht.png'), 672, 1090, 360, verplaatsing=7, masker=m)
    bewaar(t, 't-shirt-lijn-naar-zee-2', vul=1.0, uitsnede=(0, 200, 1600, 2200))
    # 3: sfeer, zandkleurig op het lijf
    t = foto('tshirt2-creme-2.jpg')
    m = shirt_masker(t)
    t = MK.kleur_om(t, m, CREME_T, 1.0)
    t = MK.zet_print(t, art('icoon-navy.png', NAVY), 905, 360, 36, verplaatsing=3)
    bewaar(t, 't-shirt-lijn-naar-zee-3', vul=1.0)
    # Stickers, navy. 1: voorkant aan de hanger met ons logo op de borst en ons label in de nek
    t = foto('tshirt2-navy-2.jpg')
    m = shirt_masker(t, zwart=True)
    t = poets(t, 795, 233, 80, 40)
    t = MK.kleur_om(t, m, '#26355A', 0.9)
    t = t * (1 - m[..., None]) + (t * 0.82 + 0.03) * m[..., None]          # zachter licht op de stof
    t = neklabel(t, 'neklabel-creme.png', 797, 245, 70)
    t = MK.zet_print(t, art('logo-creme.png'), 880, 395, 92, verplaatsing=3, masker=m)
    bewaar(t, 't-shirt-getijden-1', vul=1.0, uitsnede=(370, 60, 1230, 1067))
    # 2: achterkant op het lijf
    t = foto('tshirt2-model-2.jpg')
    m = shirt_masker(t)
    t = MK.kleur_om(t, m, '#26365A', 1.0)
    t = MK.zet_print(t, art(ART / 'ontwerp-getij-donker.png'), 790, 660, 420, verplaatsing=7, masker=m)
    bewaar(t, 't-shirt-getijden-2', vul=1.0, uitsnede=(0, 0, 1600, 2000))
    # 3: sfeer buiten, echt navy shirt
    t = foto('tshirt2-navy-1.jpg')
    t = MK.zet_print(t, art('logo-creme.png'), 770, 1520, 150, verplaatsing=4, draai=4)
    bewaar(t, 't-shirt-getijden-3', vul=1.0, uitsnede=(0, 397, 1600, 2397))

    # de twee andere nieuwe ontwerpen, ter keuze (docs/producten/ontwerpen)
    KEUZE = ROOT / 'docs' / 'producten' / 'ontwerpen'
    KEUZE.mkdir(exist_ok=True)
    for naam, bron, kleur, kant, cx, cy, br in [('club-creme', 'tshirt2-wit-rug-1.jpg', CREME_T, 'licht', 672, 1090, 380),
                                                ('handen-navy', 'tshirt2-model-2.jpg', '#26365A', 'donker', 790, 660, 420),
                                                ('club-navy', 'tshirt2-model-2.jpg', '#26365A', 'donker', 790, 660, 440),
                                                ('handen-creme', 'tshirt2-wit-rug-1.jpg', CREME_T, 'licht', 672, 1090, 360)]:
        t = foto(bron)
        m = shirt_masker(t)
        t = MK.kleur_om(t, m, kleur, 1.0)
        t = MK.zet_print(t, art(ART / f'ontwerp-{naam.split("-")[0]}-{kant}.png'), cx, cy, br, verplaatsing=7, masker=m)
        staand = MK.naar_staand(t[200:2200] if 'rug' in bron else t[0:2000], vul=1.0)
        MK.bewaar(staand, KEUZE / f'shirt-{naam}.jpg')
        print('keuze', naam)


def sweater_en_longsleeve():
    s = foto('longsleeve-wit-1.jpg')
    s = MK.zet_print(s, art('longsleeve-golf-rugprint-los.png'), 870, 470, 470, verplaatsing=6)
    bewaar(s, 'longsleeve-golf-2', vul=1.0, uitsnede=(250, 40, 1500, 1160))
    s = foto('longsleeve-wit-1.jpg')
    s = MK.zet_print(s, art('longsleeve-golf-borst-los.png'), 1010, 330, 64, verplaatsing=3)
    bewaar(s, 'longsleeve-golf-1', vul=1.0, uitsnede=(250, 40, 1500, 1160))
    # navy longsleeve met de tegelprint (linker kledingstuk op de foto)
    l = foto('longsleeve-zwart-basis-navy-1.jpg')
    m = omkleur_masker(l, 0.08, (322, 470)) * (MK.helderheid(l) < 0.42)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)
    l = MK.kleur_om(l, m, '#26365A', 1.0)
    l = MK.zet_print(l, art('longsleeve-tegel-rugprint-los.png'), 322, 470, 210, verplaatsing=5, masker=m)
    bewaar(l, 'longsleeve-tegel-2', vul=1.0, uitsnede=(20, 60, 600, 1000))


def hoodie():
    h = foto('hoodie-wit-1.jpg')
    m = shirt_masker(h)
    h = MK.kleur_om(h, m, '#BCD0E6', 1.0)
    h = MK.zet_print(h, art('hoodie-busje-borst-los.png'), 965, 500, 96, verplaatsing=3, masker=m)
    bewaar(h, 'hoodie-busje-1', vul=1.0, uitsnede=(420, 120, 1240, 1145))
    bewaar(h, 'hoodie-busje-3', vul=1.0, uitsnede=(800, 380, 1140, 805))      # detail van de borstprint


# ---------- accessoires ----------
def pet():
    p = foto('pet-navy-1.jpg')
    # de klepsticker van de stockpet vervangen door die van ons, in dezelfde stand (perspectief) op de klep
    st = MK.laad_art(ART / 'petsticker.png')
    sh, sw = st.shape[:2]
    doel = np.float32([[944, 958], [1142, 943], [1293, 1090], [1046, 1114]])
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), doel)
    laag = cv2.warpPerspective(st, M, (p.shape[1], p.shape[0]), flags=cv2.INTER_AREA)
    a = laag[..., 3:4]
    oud = cv2.dilate((cv2.warpPerspective(np.ones((sh, sw), np.float32), M, (p.shape[1], p.shape[0])) > 0).astype(np.uint8), np.ones((15, 15), np.uint8))
    p = (cv2.inpaint((np.clip(p, 0, 1) * 255).astype(np.uint8), oud * 255, 7, cv2.INPAINT_TELEA).astype(np.float32) / 255)
    L = MK.helderheid(p)
    licht = cv2.GaussianBlur(L, (0, 0), 25)[..., None] / max(float(np.median(L[oud > 0])), 1e-3)
    sch = cv2.GaussianBlur(np.roll(np.roll(a[..., 0], 3, 0), 2, 1), (0, 0), 2.5)[..., None]
    p = p * (1 - 0.35 * sch)
    p = p * (1 - a) + np.clip(laag[..., :3] * (0.9 + 0.1 * licht), 0, 1) * a
    p = borduur(p, art('icoon-navy.png', CREME), 770, 585, 108, draai=-4)
    bewaar(p, 'pet-navy-1', vul=0.9)


def bucket():
    b = foto('buckethat-olijf-1.jpg')
    m = omkleur_masker(b, 0.08, (800, 640))
    b = MK.kleur_om(b, m, '#E9DFCB', 1.0)
    b = borduur(b, art('icoon-navy.png', NAVY), 800, 640, 92)
    bewaar(b, 'bucket-hat-tegel-1', vul=0.9)


def tote():
    t = foto('tote-naturel-1.jpg')
    t = poets(t, 1047, 937, 64, 64)
    t = MK.zet_print(t, art('hoodie-busje-rugprint-los.png'), 807, 655, 330, verplaatsing=5)
    bewaar(t, 'canvas-tas-1', vul=1.0, uitsnede=(383, 0, 1237, 1067))


# ---------- gear ----------
WAX = {'koud': '#C9DAEC', 'koel': '#E8D6B5', 'warm': '#F0C9C4'}


def wax():
    for soort, kleur in WAX.items():
        w = foto('wax-zeep-1.jpg')
        m = np.zeros(w.shape[:2], np.float32)
        cv2.fillPoly(m, [np.array([[766, 322], [1015, 533], [822, 752], [585, 537]], np.int32)], 1)
        m = cv2.GaussianBlur(m, (0, 0), 1.5)
        w = MK.kleur_om(w, m, kleur, 0.95)
        w = MK.zet_print(w, art(f'waxlabel-{soort}.png'), 800, 537, 250, draai=-40.3, verplaatsing=1, schaduw_sterkte=0.6, structuur=0.25)
        bewaar(w, f'surfwax-{soort}-1', vul=1.0, uitsnede=(300, 0, 1300, 1067))


def gegoten_logo(img, m, cx, cy, lengte, hoek, sterkte=1.0):
    """Liggend logo in reliëf in het metaal gegoten: zelfde metaal, alleen licht en schaduw van de verhoging."""
    sys.path.insert(0, str(ROOT / 'tools' / 'tas'))
    import scene as SC
    hoogte = 34
    strook = SC.logo_strook(breedte=hoogte + 8, periode=int(lengte * 1.15), hoogte=hoogte)
    h, w = img.shape[:2]
    sh, sw = strook.shape
    M = cv2.getRotationMatrix2D((sw / 2, sh / 2), hoek, 1.0)
    M[0, 2] += cx - sw / 2; M[1, 2] += cy - sh / 2
    a = cv2.warpAffine(strook, M, (w, h), flags=cv2.INTER_LINEAR) * m
    hoog = cv2.GaussianBlur(a, (0, 0), 1.3)
    gx = cv2.Sobel(hoog, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(hoog, cv2.CV_32F, 0, 1, ksize=3)
    licht = (gx * 0.6 + gy * 0.8) * 0.45 * sterkte              # licht van linksboven: bovenrand licht, onderrand schaduw
    mat = cv2.GaussianBlur(img, (0, 0), 2.5)                     # gegoten vlak is iets matter dan het gepolijste staal
    uit = img * (1 - 0.4 * a[..., None]) + (mat * 0.95 + 0.08) * 0.4 * a[..., None]
    return np.clip(uit * (1 - np.clip(licht, None, 0)[..., None] * -0.9) + 0.35 * np.clip(licht, 0, None)[..., None], 0, 1)


def bandlabel(img, start, richting, lengte, breedte, kleur_hex, steek_hex, tekst_hex=None, buig=0.0, R=47):
    """Sleutelhanger van tasband: een lus webbing, plat dubbelgevouwen, om de onderkant van de karabijnhaak genaaid.
    Zelfde nylon en herhaald geweven logo als de draagband, met een stiksel in het midden over de hele lengte."""
    sys.path.insert(0, str(ROOT / 'tools' / 'tas'))
    import scene as SC
    h, w = img.shape[:2]
    SC.CH, SC.CW = h + 800, w + 800
    r = np.array(richting, np.float32); r /= np.linalg.norm(r)
    n = np.array([-r[1], r[0]])
    st = np.array(start, np.float32)
    terug = R + 10
    ts = np.linspace(-terug, lengte, 700)
    pad = np.array([st + r * t + n * buig * (max(t, 0) / lengte) ** 2 * lengte for t in ts], np.float32)
    tex = SC.band_textuur()
    tex = cv2.resize(tex, (tex.shape[1] * breedte // tex.shape[0], breedte))
    oud = SC.logo_strook
    SC.logo_strook = lambda b: np.roll(oud(b, periode=780, hoogte=int(b * 0.2)), 130, axis=1)
    beeld, a = SC.teken_band(None, pad, tex, breedte=breedte, kleur_band=SC.hexkleur(kleur_hex), tekst_kleur=SC.hexkleur(tekst_hex) if tekst_hex else None)
    SC.logo_strook = oud
    beeld, a = beeld[:h, :w], a[:h, :w]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # coördinaten langs en dwars op het (gebogen) pad
    from scipy.spatial import cKDTree
    pts = np.stack([xx.ravel(), yy.ravel()], 1)
    raak = np.gradient(pad, axis=0); raak /= np.linalg.norm(raak, axis=1)[:, None]
    nor = np.stack([-raak[:, 1], raak[:, 0]], 1)
    _, idx = cKDTree(pad).query(pts)
    relp = pts - pad[idx]
    langs = (ts[idx] + (relp * raak[idx]).sum(1)).reshape(h, w).astype(np.float32)
    dwars = (relp * nor[idx]).sum(1).reshape(h, w).astype(np.float32)
    # vouw aan het eind: afgerond, licht op de bolling en donker vlak ervoor
    hoek = breedte * 0.12
    voorbij = np.clip(langs - (lengte - hoek), 0, None)
    rond = np.sqrt(voorbij ** 2 + np.clip(np.abs(dwars) - (breedte / 2 - hoek), 0, None) ** 2)
    a = a * np.clip(hoek - rond + 0.5, 0, 1) * np.clip((lengte - langs) / 1.0 + 1, 0, 1)
    vouw = np.clip((langs - (lengte - 46)) / 46, 0, 1)
    beeld = beeld * (1 - 0.28 * vouw ** 2)[..., None] * (1 + 0.1 * np.exp(-((langs - (lengte - 40)) / 12) ** 2))[..., None]
    # om de staaf (dikte ca. 94 px, start = hart van de staaf): de band vouwt er rond omheen.
    # Achterrand van de lus volgt de bovenkant van de staaf; daar draait hij weg naar achteren.
    a = a * np.clip((langs + R - 2 + 6 * (dwars / (breedte / 2)) ** 2) / 1.5, 0, 1)
    hoekje = np.clip((langs + R) / (2 * R), 0, 1)                      # 0 = achterkant, 1 = voorkant van de staaf
    cil = np.where(langs < R, 0.62 + 0.5 * np.sin(np.pi * hoekje) * (1 - 0.25 * hoekje) + 0.12 * np.exp(-((langs + 10) / 14) ** 2), 1.0)
    # van de staaf naar de tafel: korte schuine helling, iets donkerder, met een vouwlijn waar hij de tafel raakt
    hl = 18 + R * 0.6
    helling = np.clip((langs - R) / hl, 0, 1)
    cil = cil * np.where((langs >= R) & (langs < R + hl), 0.86 + 0.14 * helling, 1.0)
    cil = cil * (1 - 0.15 * np.exp(-((langs - R - hl) / 6) ** 2))
    beeld = beeld * cil[..., None]
    # dubbele laag: de onderste laag piept langs de randen (vanaf de tafel)
    rand_onder = ((np.abs(dwars) > breedte / 2 - 3.5) & (langs > R + hl)).astype(np.float32)
    beeld = beeld * (1 - 0.3 * cv2.GaussianBlur(rand_onder, (0, 0), 0.8))[..., None]
    # de staaf verdwijnt aan beide kanten in de lus: schaduw op het metaal vlak naast de band
    naast = np.clip(np.abs(dwars) - breedte / 2, 0, None)
    ao = np.exp(-naast / 6) * (np.abs(langs) < R + 2) * (naast > 0)
    img = img * (1 - 0.55 * ao[..., None])
    # stiksels: twee rijen dwars net onder de staaf, en een rij in het midden over de lengte
    def lijn(d, dik=2.6):
        return np.clip(dik - np.abs(d), 0, 1)
    y0 = R + hl + 40
    dwars_rij = np.maximum(lijn(langs - y0), lijn(langs - y0 - 13)) * (np.abs(dwars) < breedte / 2 - 14) * (np.sin(dwars * 0.42) > -0.3)
    midden = lijn(dwars, 3.0) * (langs > y0 + 13) * (langs < lengte - 30) * ((langs % 22) < 13)
    st_m = np.clip(np.maximum(dwars_rij, midden), 0, 1) * a
    g = np.array(SC.hexkleur(steek_hex), np.float32)
    beeld = beeld * (1 - 0.35 * np.roll(st_m, 2, 0)[..., None])
    beeld = beeld * (1 - st_m[..., None]) + g * st_m[..., None]
    # schaduw op tafel
    plat = a * (langs > R + hl)
    sch = cv2.GaussianBlur(np.roll(np.roll(plat, 12, 0), 7, 1), (0, 0), 10)
    hoog = cv2.GaussianBlur(np.roll(np.roll(a * (langs <= R + hl), 16, 0), 10, 1), (0, 0), 10)
    uit = img * (1 - 0.3 * sch[..., None]) * (1 - 0.22 * hoog[..., None])
    return uit * (1 - a[..., None]) + beeld * a[..., None]


def d_ring(img, onder_masker, S, richting, breedte, draad, kleur_d, kleur_l):
    """Metalen D-ring: rechte kant bij S (dwars op de band), boog richting de karabijnhaak.
    Ligt plat op tafel, onder de karabijnhaak door (onder_masker = waar de haak ligt)."""
    h, w = img.shape[:2]
    r = np.array(richting, np.float32); r /= np.linalg.norm(r); n = np.array([-r[1], r[0]])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rel = np.stack([xx - S[0], yy - S[1]], -1)
    u = rel @ n; v = -(rel @ r)                     # u dwars, v omhoog naar de haak
    hb = breedte / 2
    # afstand tot de middellijn: recht stuk (v=0, |u|<=hb) en halve cirkel (straal hb) erboven
    d_recht = np.where(np.abs(u) <= hb, np.abs(v), np.hypot(np.abs(u) - hb, v))
    d_boog = np.where(v >= 0, np.abs(np.hypot(u, v) - hb), 1e9)
    d = np.minimum(d_recht, d_boog)
    t = draad / 2
    a = np.clip(t - d + 0.5, 0, 1)
    nz = np.sqrt(np.clip(1 - (d / t) ** 2, 0, 1))
    # richting van de buis-normaal in het vlak, voor het glimlicht (licht van linksboven)
    gy, gx = np.gradient(d)
    lic = np.clip(-(gx * -0.6 + gy * -0.8), -1, 1) * np.sqrt(np.clip(1 - nz ** 2, 0, 1))
    hel = np.clip(0.25 + 0.55 * nz + 0.35 * lic, 0, 1) ** 1.2
    kl = np.array(kleur_d)[None, None] + (np.array(kleur_l) - np.array(kleur_d))[None, None] * hel[..., None]
    kl = kl + 0.35 * np.clip(nz - 0.8, 0, 1)[..., None] * (lic > 0)[..., None]
    sch = cv2.GaussianBlur(np.roll(np.roll(a, 9, 0), 6, 1), (0, 0), 6)
    zicht = a * (1 - onder_masker)
    img = img * (1 - 0.35 * sch * (1 - onder_masker))[..., None]
    return img * (1 - zicht[..., None]) + np.clip(kl, 0, 1) * zicht[..., None]


def groter_doek(img, links, boven, B, H):
    """Foto op een groter doek met dezelfde achtergrond, zodat er ruimte is (randen zacht in elkaar overlopen)."""
    h, w = img.shape[:2]
    rand = np.concatenate([img[:10].reshape(-1, 3), img[-10:].reshape(-1, 3), img[:, :10].reshape(-1, 3), img[:, -10:].reshape(-1, 3)])
    kl = np.median(rand, axis=0)
    doek = np.ones((H, B, 3), np.float32) * kl
    rng = np.random.default_rng(5)
    doek += cv2.GaussianBlur(rng.normal(0, 0.006, (H, B)).astype(np.float32), (0, 0), 1.0)[..., None]
    m = np.ones((h, w), np.float32); r = 160
    m = cv2.GaussianBlur(cv2.copyMakeBorder(m[r:-r, r:-r], r, r, r, r, cv2.BORDER_CONSTANT, value=0), (0, 0), r / 2.5)[..., None]
    doek[boven:boven + h, links:links + w] = img * m + doek[boven:boven + h, links:links + w] * (1 - m)
    return doek


def karabijn():
    k = foto('karabiner-zilver-1.jpg')
    m = omkleur_masker(k, 0.15, (800, 589), vullen=False, sluit=81)
    L = MK.helderheid(k)
    uitsnede = (290, 380, 1266, 1600)
    for naam, donker, licht, gamma, band, garen, tekst in [
            ('messing', [0.42, 0.29, 0.1], [1.0, 0.88, 0.58], 1.15, '#22324F', '#C0603E', '#DCD3C2'),
            ('zwart', [0.05, 0.055, 0.065], [0.62, 0.64, 0.68], 2.2, '#67809F', '#F3ECDD', '#22324F')]:
        t = np.clip(L, 0, 1) ** gamma
        metaal = np.array(donker)[None, None] + (np.array(licht) - np.array(donker))[None, None] * t[..., None]
        # glimlichten (helderder dan de achtergrond) blijven licht met een zweem van het metaal
        glim = np.clip((L - 0.965) / 0.03, 0, 1)[..., None]
        spec = np.array(licht) * 0.25 + 0.75 if naam == 'messing' else np.array([0.9, 0.92, 0.95])
        metaal = metaal * (1 - glim) + spec[None, None] * glim
        # zelfde lichtheid als de achtergrond = achtergrond: daar niets doen
        # glimlichten binnen de omtrek van de haak horen ook bij het metaal
        cnts, _ = cv2.findContours((m > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        romp = np.zeros_like(m); cv2.fillPoly(romp, [cv2.convexHull(np.vstack(cnts))], 1)
        romp = cv2.erode(romp, np.ones((9, 9), np.uint8))
        grijs = (L < 0.935) & (cv2.dilate((m > 0.5).astype(np.uint8), np.ones((61, 61), np.uint8)) > 0)
        glans = (romp * grijs).astype(np.uint8)
        glans = cv2.morphologyEx(glans, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)).astype(np.float32)
        zone = np.maximum(m, cv2.GaussianBlur(glans, (0, 0), 1.2))[..., None]
        uit = (k * (1 - zone) + metaal * zone).astype(np.float32)
        uit = gegoten_logo(uit, m, 760, 600, 250, 29.2, sterkte=1.0 if naam == 'messing' else 1.4)
        # karabijnhaak ca. 7 cm lang (880 px), band 25 mm breed en de dubbelgevouwen lus 12 cm lang
        L0, B0 = 360, 300
        groot = groter_doek(uit, L0, B0, 2600, 3250)
        hm = np.zeros(groot.shape[:2], np.float32); hm[B0:B0 + m.shape[0], L0:L0 + m.shape[1]] = m
        hm = np.maximum(hm, 0)
        r = np.array([-0.215, 0.977]); C = np.array([592 + L0, 1068 + B0])
        Sd = C + r * 150                                   # rechte kant van de D-ring, 15 mm onder de staaf
        groot = d_ring(groot, hm, Sd, r, 300, 26, donker, licht)
        groot = bandlabel(groot, tuple(Sd), tuple(r), 1450, 280, band, garen, tekst, buig=0.09, R=13)
        bewaar(groot, f'karabijnhaak-{naam}-1', vul=1.0, uitsnede=(170, 540, 2090, 2940))


def handdoek():
    h = foto('handdoek-1.jpg')
    m = omkleur_masker(h, 0.1, (1000, 600))
    # tegelpatroon (zelfde als de tas) als vlak, licht schuin zoals de bovenkant van de handdoek
    # tegels rechtstreeks tekenen met numpy (geen svg-renderer nodig)
    H_, W_ = h.shape[:2]
    pat = np.zeros((H_, W_, 3), np.float32)
    kl = np.array([[0.75, 0.38, 0.24], [0.56, 0.66, 0.78], [0.95, 0.93, 0.87], [0.62, 0.23, 0.18]], np.float32)
    t = 120
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    # schuin raster dat de bovenkant volgt
    u = (xx * 0.97 + yy * 0.25) / t; v = (-xx * 0.12 + yy * 1.25) / t
    ci, ri = np.floor(u).astype(int), np.floor(v).astype(int)
    idx = (ri * 3 + ci) % 7
    keuze = np.array([0, 1, 2, 3, 1, 0, 2])[idx]
    pat = kl[keuze]
    fu, fv = u - ci - 0.5, v - ri - 0.5
    ruit = (np.abs(fu) + np.abs(fv)) < 0.36
    binnen = np.where((keuze == 2)[..., None], kl[0][None, None], kl[2][None, None])
    pat = np.where(ruit[..., None], binnen, pat)
    stip = (fu ** 2 + fv ** 2) < 0.012
    pat = np.where(stip[..., None], np.array([0.13, 0.2, 0.31], np.float32)[None, None], pat)
    L = MK.helderheid(h)
    ref = np.median(L[m > 0.5])
    schaduw = np.clip(L / ref, 0, 1.4)[..., None]
    fijn = (L - cv2.GaussianBlur(L, (0, 0), 1.2))[..., None]
    nieuw = np.clip(pat * schaduw ** 1.15 + fijn * 2.2, 0, 1)
    uit = h * (1 - m[..., None]) + nieuw * m[..., None]
    bewaar(uit, 'strandhanddoek-tegel-1', vul=0.92, rand=False)


# ---------- stickers ----------
def stickers():
    vel = MK.laad_art(ART / 'stickervel.png')
    hout = MK.laad(STOCK / 'lifestyle' / 'textuur-hout-2.jpg')
    hout = cv2.resize(hout, (1600, int(hout.shape[0] * 1600 / hout.shape[1])))[:2000] if hout.shape[1] != 1600 else hout[:2000]
    if hout.shape[0] < 2000:
        hout = cv2.resize(hout, (int(hout.shape[1] * 2000 / hout.shape[0]), 2000))[:, :1600]
    # vel licht schuin, met de schaduw en het licht van een tafel bij het raam
    h, w = vel.shape[:2]
    s = 1160 / w
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -4, s)
    M[0, 2] += 800 - w / 2; M[1, 2] += 990 - h / 2
    laag = cv2.warpAffine(vel, M, (1600, 2000), flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
    a = laag[..., 3:4]
    sch = cv2.GaussianBlur(np.roll(np.roll(a[..., 0], 14, 0), 10, 1), (0, 0), 14)
    doek = hout * (1 - 0.35 * sch[..., None])
    yy, xx = np.mgrid[0:2000, 0:1600].astype(np.float32)
    licht = (1.06 - 0.12 * (xx / 1600) - 0.06 * (yy / 2000))[..., None]
    papier = laag[..., :3] * licht + np.random.default_rng(3).normal(0, 0.008, laag[..., :3].shape).astype(np.float32)
    uit = doek * (1 - a) + papier * a
    MK.bewaar(np.clip(uit * licht ** 0.3, 0, 1), DOEL / 'stickerset-1.jpg')
    print('foto stickerset-1')
    # stickers geplakt op een board (wit fishboard tegen een betonmuur)
    b = MK.laad(STOCK / 'lifestyle' / 'board-muur-1.jpg')
    b = poets(b, 770, 1003, 240, 110)
    for naam, x, y, br, d in [('zegel', 770, 1000, 320, -8), ('golfrand', 900, 1420, 260, 10), ('pil', 760, 1700, 380, -4)]:
        st = MK.laad_art(ART / f'sticker-{naam}.png')
        b = MK.zet_print(b, st, x, y, br, draai=d, verplaatsing=1, schaduw_sterkte=0.35, structuur=0.04, dekking=1.0)
        # dun schaduwrandje van de sticker
    MK.bewaar(MK.naar_staand(b, vul=1.0), DOEL / 'stickerset-2.jpg')
    print('foto stickerset-2')


if __name__ == '__main__':
    # wax en handdoek hebben eigen scripts (echt_wax.py, echt_handdoek.py)
    stappen = sys.argv[1:] or ['tshirts', 'hoodie', 'pet', 'bucket', 'tote', 'karabijn', 'stickers']
    # longsleeves: echt_meer.py; uv-shirt, poncho en waxkam: echt_extra.py
    for st in stappen:
        try:
            globals()[st]()
        except Exception as e:
            import traceback; traceback.print_exc()
            print('mislukt', st, e)
