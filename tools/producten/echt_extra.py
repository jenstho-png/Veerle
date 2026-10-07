"""Levensechte foto's voor drie producten die nog alleen een tekening hadden: uv-shirt-lange-mouw, surfponcho-tegel en waxkam.

Werkwijze zoals echt.py: echte stockfoto's (Pexels, zie docs/producten/stock/bronnen.json), merkjes wegpoetsen, stof omkleuren
met behoud van schaduw en plooien, en onze prints erop zetten die meebuigen met de stof (mockup.zet_print).
Nieuw hier: tegelbanden om een mouw of langs een zoom (band_cilinder, band_zoom) en een uitgeknipte waxkam die we
recht leggen (perspectief) zodat hij in andere foto's en in een studiofoto kan liggen.

Gebruik: python3 tools/producten/echt_extra.py [uv_shirt] [poncho] [waxkam]
"""
import pathlib, sys
import cv2
import numpy as np

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import mockup as MK  # noqa: E402
import echt as E  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock'
REF = ROOT / 'docs' / 'producten' / 'referentie'
UIT = HIER / 'uit_extra'
UIT.mkdir(exist_ok=True)
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
NAVY, CREME, TERRA = '#22324F', '#F3ECDD', '#C0603E'
ZEEBLAUW = '#5E7F9C'
PROEF = '--proef' in sys.argv          # alleen kleine voorbeelden in uit_extra, niets in beelden


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def foto(naam):
    return MK.laad(STOCK / naam)


def bewaar(img, naam, uitsnede=None):
    """Uitsnede (x0, y0, x1, y1) in 4:5, dan naar 1600 x 2000 en als jpg onder 190 kB."""
    if uitsnede:
        x0, y0, x1, y1 = uitsnede
        img = img[y0:y1, x0:x1]
    staand = MK.naar_staand(img, vul=1.0)
    if PROEF:
        MK.bewaar(cv2.resize(staand, (640, 800), interpolation=cv2.INTER_AREA), UIT / f'proef-{naam}.jpg')
        MK.bewaar(staand, UIT / f'groot-{naam}.jpg')
    else:
        MK.bewaar(staand, DOEL / f'{naam}.jpg')
    print('foto', naam)


def uitsnede45(cx, cy, b, h_img, w_img, breedte):
    """4:5-uitsnede met gegeven breedte rond (cx, cy), binnen het beeld geschoven."""
    hoogte = int(round(breedte * 5 / 4))
    x0 = int(np.clip(cx - breedte / 2, 0, w_img - breedte))
    y0 = int(np.clip(cy - hoogte / 2, 0, h_img - hoogte))
    return x0, y0, x0 + breedte, y0 + hoogte


# ---------- artwork ----------
def art(naam, kleur=None):
    a = MK.laad_art(REF / naam)
    if kleur:
        a = a.copy(); a[..., :3] = hexrgb(kleur)
    return a


def knijp(a, sx=1.0, sy=1.0):
    """Art vervormen (bijvoorbeeld smaller als het lijf van ons wegdraait)."""
    h, w = a.shape[:2]
    return cv2.resize(a, (max(1, int(w * sx)), max(1, int(h * sy))), interpolation=cv2.INTER_AREA)


def tegelstrook(rijen=1, rand=None):
    """Strook uit onze tegelprint: een rij (of meer) tegels, naadloos herhaalbaar in de breedte.
    rand = (kleur, dikte als deel van de hoogte) geeft een smal effen biesje boven en onder."""
    t = MK.laad(REF / 'tegelprint.png') if False else None
    from PIL import Image
    a = np.asarray(Image.open(REF / 'tegelprint.png').convert('RGB')).astype(np.float32) / 255
    n = 6                                        # 6 x 6 tegels in de print
    ts = a.shape[0] / n
    strook = a[:int(round(ts * rijen))]
    if rand:
        kl, d = rand
        h = strook.shape[0]; p = int(h * d)
        strook = np.concatenate([np.ones((p, strook.shape[1], 3), np.float32) * hexrgb(kl), strook,
                                 np.ones((p, strook.shape[1], 3), np.float32) * hexrgb(kl)], 0)
    return np.dstack([strook, np.ones(strook.shape[:2], np.float32)])


# ---------- druk op stof ----------
def druk_laag(img, laag, **kw):
    """Een volledige RGBA-laag (zelfde maat als img) op de stof drukken met de schaduw- en plooiwerking van mockup.zet_print."""
    h, w = img.shape[:2]
    return MK.zet_print(img, laag, w / 2, h / 2, w, **kw)


def band_cilinder(img, C, n_dir, r, breedte, strook, e=0.15, tegels_per_hoogte=1.0, masker=None, **kw):
    """Tegelband om een mouw (cilinder). C = midden van de band op de as, n_dir = richting dwars over de mouw
    (van links naar rechts in beeld), r = halve mouwbreedte in pixels, breedte = bandbreedte langs de as.
    e = hoe ver we op de mouwopening kijken (ellips); positieve e buigt de band naar de hand toe."""
    h, w = img.shape[:2]
    n = np.array(n_dir, np.float32); n /= np.linalg.norm(n)
    a = np.array([-n[1], n[0]], np.float32)          # langs de as (naar de hand)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rx, ry = xx - C[0], yy - C[1]
    u = (rx * n[0] + ry * n[1]) / r
    sin_t = np.clip(u, -1, 1)
    theta = np.arcsin(sin_t)
    s = rx * a[0] + ry * a[1] - e * r * np.cos(theta)
    sh, sw = strook.shape[:2]
    tegel = sh / tegels_per_hoogte
    # booglengte rond de mouw, in tegels: (theta * r) / breedte tegels
    mx = ((theta + np.pi / 2) * r / breedte * tegel) % sw
    my = (s / breedte + 0.5) * sh
    laag = cv2.remap(strook, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    binnen = (np.abs(u) < 1.0) & (my >= 0) & (my <= sh - 1)
    zacht = np.clip((1 - np.abs(u)) * r / 1.5, 0, 1)
    laag[..., 3] *= binnen * zacht
    if masker is not None:
        laag[..., 3] *= masker
    return druk(img, laag, **kw)


def band_zoom(img, zoom, hoogte, strook, omhoog=(0, -1), masker=None, **kw):
    """Tegelband langs een zoom. zoom = lijst punten (x, y) van links naar rechts langs de onderrand,
    hoogte in pixels (mag een lijst per punt zijn, voor perspectief), omhoog = richting van de zoom het kledingstuk in."""
    h, w = img.shape[:2]
    zoom = np.array(zoom, np.float32)
    # gladde curve door de punten
    t = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(zoom, axis=0), axis=1))])
    tt = np.linspace(0, t[-1], 400)
    px = np.interp(tt, t, zoom[:, 0]); py = np.interp(tt, t, zoom[:, 1])
    k = 15
    px = np.convolve(np.pad(px, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    py = np.convolve(np.pad(py, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    hs = np.interp(tt, t, np.broadcast_to(np.array(hoogte, np.float32), (len(zoom),)))
    om = np.array(omhoog, np.float32); om /= np.linalg.norm(om)
    sh, sw = strook.shape[:2]
    laag = np.zeros((h, w, 4), np.float32)
    lengte = 0.0
    for i in range(len(tt) - 1):
        p0, p1 = np.array([px[i], py[i]]), np.array([px[i + 1], py[i + 1]])
        q0, q1 = p0 + om * hs[i], p1 + om * hs[i + 1]
        seg = np.linalg.norm(p1 - p0)
        u0 = lengte / hs[i] * sh; lengte += seg; u1 = lengte / hs[i + 1] * sh
        # stukje strook (met herhaling) op dit vierhoekje
        bron = np.float32([[u0, sh], [u1, sh], [u1, 0], [u0, 0]])
        doel = np.float32([p0, p1, q1, q0])
        x0, y0 = np.floor(doel.min(0)).astype(int) - 2
        x1, y1 = np.ceil(doel.max(0)).astype(int) + 3
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, w), min(y1, h)
        if x1 <= x0 or y1 <= y0:
            continue
        M = cv2.getPerspectiveTransform(doel - np.float32([x0, y0]), bron)
        gx, gy = np.meshgrid(np.arange(x0, x1, dtype=np.float32) - x0, np.arange(y0, y1, dtype=np.float32) - y0)
        den = M[2, 0] * gx + M[2, 1] * gy + M[2, 2]
        su = (M[0, 0] * gx + M[0, 1] * gy + M[0, 2]) / den
        sv = (M[1, 0] * gx + M[1, 1] * gy + M[1, 2]) / den
        stuk = cv2.remap(strook, (su % sw).astype(np.float32), sv.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        poly = np.zeros((y1 - y0, x1 - x0), np.float32)
        cv2.fillConvexPoly(poly, np.round((doel - np.float32([x0, y0])) * 4).astype(np.int32), 1, lineType=cv2.LINE_AA, shift=2)
        stuk[..., 3] *= np.clip(poly * 1.0, 0, 1) * ((sv >= -0.5) & (sv <= sh + 0.5))
        vak = laag[y0:y1, x0:x1]
        a_n = stuk[..., 3:4]
        vak[..., :3] = vak[..., :3] * (1 - a_n) + stuk[..., :3] * a_n
        vak[..., 3:4] = np.maximum(vak[..., 3:4], a_n)
    if masker is not None:
        laag[..., 3] *= masker
    return druk(img, laag, **kw)


def masker_kleur(img, laag_hsv, hoog_hsv, zaad=None, sluit=9, rect=None):
    """Masker op kleur (OpenCV-HSV, 0..180 / 0..255), dichtgemaakt, eventueel alleen het stuk onder zaad of binnen rect."""
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    hsv = cv2.cvtColor(u8, cv2.COLOR_RGB2HSV)
    m = cv2.inRange(hsv, np.array(laag_hsv, np.uint8), np.array(hoog_hsv, np.uint8))
    if rect:
        r = np.zeros_like(m); x0, y0, x1, y1 = rect; r[y0:y1, x0:x1] = 255; m &= r
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((sluit, sluit), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0).astype(np.uint8))
    if n > 1:
        kies = lab[zaad[1], zaad[0]] if zaad else 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        m = (lab == kies).astype(np.uint8)
    vul = m.copy(); ff = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8); cv2.floodFill(vul, ff, (0, 0), 1)
    m = m | (1 - vul)
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)


def grabcut(img, zeker, mogelijk, schaal=0.35, iter=6):
    """Masker met GrabCut: zeker = zeker kledingstuk, mogelijk = mag erbij horen (de rest is achtergrond)."""
    h, w = img.shape[:2]
    sm = cv2.resize(cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR), (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_AREA)
    m = np.full(sm.shape[:2], cv2.GC_BGD, np.uint8)
    rs = lambda x: cv2.resize(x.astype(np.uint8), (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
    m[rs(mogelijk)] = cv2.GC_PR_FGD
    m[rs(zeker)] = cv2.GC_FGD
    bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.grabCut(sm, m, None, bg, fg, iter, cv2.GC_INIT_WITH_MASK)
    uit = ((m == 1) | (m == 3)).astype(np.float32)
    uit = cv2.resize(uit, (w, h), interpolation=cv2.INTER_LINEAR)
    uit = (uit > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(uit)
    if n > 1:
        uit = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    vul = uit.copy(); ff = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(vul, ff, (0, 0), 1)
    uit = uit | (1 - vul)
    return cv2.GaussianBlur(uit.astype(np.float32), (0, 0), 1.5)


def poly(shape, punten):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.array(punten, np.int32)], 1)
    return m > 0


def kleur_lab(img, m, doel_hex, ref_L=None, chroma=1.0, spreiding=0.6):
    """Omkleuren in Lab: de helderheid schaalt zo dat de mediaan van de stof de doelkleur krijgt, en de kleurtint (a, b)
    schuift naar die van de doelkleur. Licht, schaduw en de natuurlijke ontkleuring in zonlicht blijven zo staan."""
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    lab = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_RGB2Lab)
    doel = cv2.cvtColor(hexrgb(doel_hex)[None, None].astype(np.float32), cv2.COLOR_RGB2Lab)[0, 0]
    sel = m > 0.5
    Lm = np.median(lab[..., 0][sel]) if ref_L is None else ref_L
    am, bm = np.median(lab[..., 1][sel]), np.median(lab[..., 2][sel])
    nieuw = lab.copy()
    nieuw[..., 0] = lab[..., 0] * (doel[0] / Lm)
    # hoe lichter (zon), hoe minder kleur: houd de verhouding van de foto aan
    nieuw[..., 1] = doel[1] * chroma + (lab[..., 1] - am) * spreiding
    nieuw[..., 2] = doel[2] * chroma + (lab[..., 2] - bm) * spreiding
    rgb = np.clip(cv2.cvtColor(nieuw, cv2.COLOR_Lab2RGB), 0, 1)
    mm = m[..., None]
    return img * (1 - mm) + rgb * mm


def druk(img, laag, ref=None, verplaatsing=6.0, schaduw=1.0, structuur=0.5, dekking=0.96, blur=0.0, masker=None):
    """Als mockup.zet_print, maar voor een volledige laag en met een vaste lichtreferentie: ref = helderheid van de stof
    in vol licht. Een print in de schaduw wordt dan net zo donker als de stof eromheen. blur = scherptediepte van de foto."""
    h, w = img.shape[:2]
    if blur > 0:
        laag = cv2.GaussianBlur(laag, (0, 0), blur)
    L = MK.helderheid(img)
    Lz = cv2.GaussianBlur(L, (0, 0), 6)
    gx = cv2.Sobel(Lz, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(Lz, cv2.CV_32F, 0, 1, ksize=5)
    norm = max(np.abs(gx).max(), np.abs(gy).max(), 1e-6)
    mx, my = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    laag = cv2.remap(laag, mx + gx / norm * verplaatsing, my + gy / norm * verplaatsing, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    gebied = laag[..., 3] > 0.05
    if ref is None:
        ref = Lz[gebied].mean() if gebied.any() else Lz.mean()
    Ls = cv2.GaussianBlur(L, (0, 0), 2)
    factor = np.clip(1 + (Ls / max(ref, 1e-3) - 1) * schaduw, 0.15, 1.4)[..., None]
    kleur = laag[..., :3] * factor
    fijn = (L - cv2.GaussianBlur(L, (0, 0), 1.5))[..., None]
    kleur = np.clip(kleur + fijn * structuur, 0, 1)
    a = laag[..., 3:4] * dekking
    if masker is not None:
        a = a * masker[..., None]
    return img * (1 - a) + kleur * a


def plaats(shape, a, cx, cy, breedte, draai=0.0):
    """Art (RGBA) als volledige laag op (cx, cy) met breedte en draaiing."""
    h, w = shape[:2]
    ah, aw = a.shape[:2]
    M = cv2.getRotationMatrix2D((aw / 2, ah / 2), draai, breedte / aw)
    M[0, 2] += cx - aw / 2; M[1, 2] += cy - ah / 2
    return cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def kleur_om(img, m, doel_hex, ref=None, gamma=1.0):
    """Als mockup.kleur_om, maar met een vaste referentiehelderheid (de lichte kant van de stof) zodat
    zonlicht en schaduw van de foto gelijk blijven, en een gamma om het contrast van lichte stof wat te temperen."""
    doel = hexrgb(doel_hex)
    L = MK.helderheid(img)
    if ref is None:
        ref = np.median(L[m > 0.5])
    schaduw = np.clip(L / ref, 0, 2.2) ** gamma
    nieuw = np.clip(doel[None, None] * schaduw[..., None], 0, 1)
    mm = m[..., None]
    return img * (1 - mm) + nieuw * mm


# ---------- UV-shirt ----------
def uv_shirt():
    strook2 = tegelstrook(2)
    borst = art('uv-shirt-lange-mouw-borst-los.png')

    # 1. voorkant, gedragen aan zee (Pexels 20849170)
    s = foto('uvshirt-model-1.jpg')
    s = E.poets(s, 1742, 1785, 104, 132)                  # merklogo op de borst
    s = E.poets(s, 754, 3196, 86, 62)                     # tekst bij de zoom
    kl = masker_kleur(s, (95, 40, 20), (125, 255, 200), zaad=(1300, 2300)) > 0.5
    borstvlak = poly(s.shape, [(1200, 1390), (1300, 1430), (1400, 1500), (1500, 1535), (1580, 1490), (1590, 1400), (1680, 1425), (1780, 1465), (1815, 1505),
                               (1825, 1560), (1828, 1700), (1815, 1850), (1795, 2000), (1700, 2100), (1500, 2150), (1300, 2100), (1200, 1950), (1180, 1600)])
    samen = (kl | borstvlak).astype(np.uint8)
    zeker = cv2.erode(kl.astype(np.uint8), np.ones((15, 15), np.uint8)) | cv2.erode(borstvlak.astype(np.uint8), np.ones((41, 41), np.uint8))
    m = grabcut(s, zeker, cv2.dilate(samen, np.ones((61, 61), np.uint8)))
    m = np.maximum(m, cv2.GaussianBlur(cv2.erode(borstvlak.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2))
    if PROEF:
        cv2.imwrite(str(UIT / 'proef-masker-uv1.jpg'), (m * 255).astype(np.uint8)[::4, ::4])
    L = MK.helderheid(s)
    s = kleur_lab(s, m, NAVY, chroma=0.8)
    licht = np.percentile(MK.helderheid(s)[m > 0.5], 92)
    s = druk(s, plaats(s.shape, knijp(borst, 0.8, 1.0), 1665, 1770, 150, draai=4), ref=licht, verplaatsing=5, schaduw=0.9, masker=m, blur=0.6)
    s = band_cilinder(s, (1880, 2995), (0.995, 0.097), 108, 140, strook2, e=0.12, tegels_per_hoogte=2, masker=m, ref=licht * 0.8, verplaatsing=12, schaduw=1.15, structuur=0.7, blur=2.2)
    bewaar(s, 'uv-shirt-lange-mouw-1', uitsnede=(240, 650, 2400, 3350))

    # 2. dichterbij, borstlogo en de tegelband om de mouw (zelfde fotosessie, Pexels 20849176)
    s = foto('uvshirt-model-2.jpg')
    s = E.poets(s, 1738, 1993, 92, 122)
    kl = masker_kleur(s, (95, 40, 20), (125, 255, 200), zaad=(1300, 2700)) > 0.5
    borstvlak = poly(s.shape, [(1180, 1640), (1300, 1660), (1400, 1690), (1480, 1705), (1575, 1690), (1590, 1600), (1660, 1600), (1760, 1720),
                               (1780, 1820), (1780, 1990), (1758, 2180), (1728, 2390), (1698, 2540), (1500, 2600), (1250, 2600), (1080, 2250),
                               (1100, 1950), (1180, 1720)])
    samen = (kl | borstvlak).astype(np.uint8)
    zeker = cv2.erode(kl.astype(np.uint8), np.ones((15, 15), np.uint8)) | cv2.erode(borstvlak.astype(np.uint8), np.ones((41, 41), np.uint8))
    m = grabcut(s, zeker, cv2.dilate(samen, np.ones((61, 61), np.uint8)))
    m = np.maximum(m, cv2.GaussianBlur(cv2.erode(borstvlak.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2))
    if PROEF:
        cv2.imwrite(str(UIT / 'proef-masker-uv2.jpg'), (m * 255).astype(np.uint8)[::4, ::4])
    s = kleur_lab(s, m, NAVY, chroma=0.8)
    licht = np.percentile(MK.helderheid(s)[m > 0.5], 92)
    s = druk(s, plaats(s.shape, knijp(borst, 0.78, 1.0), 1655, 1985, 165, draai=3), ref=licht, verplaatsing=5, schaduw=0.9, masker=m, blur=0.6)
    s = band_cilinder(s, (1835, 3362), (1.0, 0.035), 116, 145, strook2, e=0.12, tegels_per_hoogte=2, masker=m, ref=licht * 0.8,
                      verplaatsing=12, schaduw=1.15, structuur=0.7, blur=2.0)
    bewaar(s, 'uv-shirt-lange-mouw-2', uitsnede=(760, 1450, 2400, 3500))


if __name__ == '__main__':
    stappen = [a for a in sys.argv[1:] if not a.startswith('--')] or ['uv_shirt', 'poncho', 'waxkam']
    for st in stappen:
        globals()[st]()
