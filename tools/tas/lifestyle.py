"""Lifestylefoto's: de draagtas op een echt board in een echte foto.

We maken eerst een vlakke 'huid' van de tas (stof, zoom, band) zoals je hem op het board ziet,
vervormen die met perspectief naar het board in de foto en nemen daarna het licht, de kleur en de korrel van de foto over.
"""
import math, pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import scene as SC  # noqa: E402
from stof import lap  # noqa: E402

ASSETS = ROOT / 'theme' / 'assets'
BRON = ROOT / 'docs' / 'producten' / 'stock' / 'bron'   # originele sfeerfoto's (Unsplash), zonder tas
rng = np.random.default_rng(5)


def huid(lengte, breedte, kort=0.6, band_kleur=(0.40, 0.50, 0.62), bandbreedte=None, zaad=4, stof=None):
    """Vlakke tas zoals op de onderkant van het board.
    x = langs het board (0..lengte), y = dwars (0..breedte, rail tot rail). Lange zijde links (y=0)."""
    s = 4
    W, H = int(lengte * s), int(breedte * s)
    rgba = np.zeros((H, W, 4), np.float32)
    # stof, tegels op dezelfde verhouding als op de foto: ~5,5 tegels over de boardbreedte
    if stof is None:
        st = np.asarray(lap(10, 6, zaad=zaad, schaal=1)).astype(np.float32) / 255
    else:
        st = stof
    tegel = H / 5.5
    st = cv2.resize(st, (int(st.shape[1] * tegel / 98), int(st.shape[0] * tegel / 98)), interpolation=cv2.INTER_AREA)
    st = cv2.rotate(st, cv2.ROTATE_90_CLOCKWISE)
    reps = (H // st.shape[0] + 2, W // st.shape[1] + 2, 1)
    st = np.tile(st, reps)[:H, :W]
    # trapezium: lange zijde op y=0, korte op y=H
    l2 = W / 2; k2 = W * kort / 2; xm = W / 2
    poly = np.array([[xm - l2, 0], [xm + l2, 0], [xm + k2, H], [xm - k2, H]], np.float32)
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [poly.astype(np.int32)], 1)
    m = m.astype(np.float32)
    d = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    st = st * (1 - 0.3 * np.exp(-(d / (3 * s / 4)) ** 2))[..., None]
    rgba[..., :3] = st
    rgba[..., 3] = m
    # twee bandstrengen van rail tot rail (de band loopt rondom de tas)
    bb = bandbreedte or H * 47 / 98 / 5.5 * 1.0 * (98 / 98)
    tegel_x = H / 5.5
    for kant in (-1, 1):
        x0 = xm + kant * 3.15 * tegel_x      # op de foto gemeten: +-3,15 tegel bij de lange rand
        x1 = xm + kant * 1.99 * tegel_x      # en +-2 tegels bij de korte rand
        p0, p1 = np.array([x0, -10.0]), np.array([x1, H + 10.0])
        u = (p1 - p0) / np.linalg.norm(p1 - p0); n = np.array([-u[1], u[0]])
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        rel = np.stack([xx - p0[0], yy - p0[1]], -1)
        dw = rel @ n; ln = rel @ u
        bm = np.clip((bb / 2 - np.abs(dw)) / 1.5, 0, 1)
        rib = 1 + 0.05 * np.sin(dw * 2 * np.pi / (2.6 * s / 4)) + rng.normal(0, 0.02, dw.shape)
        kleur = np.array(band_kleur, np.float32)[None, None] * rib[..., None]
        # ingeweven logo
        ls = SC.logo_strook(int(bb), periode=int(bb * 3.6), hoogte=int(bb * 0.27))
        tu = np.clip(dw + bb / 2, 0, ls.shape[0] - 1).astype(np.float32)
        tv = (ln % ls.shape[1]).astype(np.float32)
        t = cv2.remap(ls, tv, tu, cv2.INTER_LINEAR)[..., None]
        kleur = kleur * (1 - t) + np.clip(kleur * 1.28 + 0.04, 0, 1) * t
        # stiksels langs de randen
        a = np.abs(dw)
        steek = ((a > bb / 2 - 5) & (a < bb / 2 - 3.2) & ((ln % 11) < 6)).astype(np.float32) * m
        kleur = kleur * (1 - 0.7 * steek[..., None]) + 0.82 * steek[..., None] * np.array([0.7, 0.77, 0.86], np.float32)
        sch = cv2.GaussianBlur(np.roll(bm, 6, 0), (0, 0), 5) * (1 - bm)
        rgba[..., :3] *= (1 - 0.3 * sch[..., None])
        rgba[..., :3] = rgba[..., :3] * (1 - bm[..., None]) + kleur * bm[..., None]
        rgba[..., 3] = np.maximum(rgba[..., 3], bm)
    # rondingen van het board: naar de rails toe donkerder
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    rond = 0.8 + 0.2 * np.sin(np.clip(yy / H, 0, 1) * np.pi) ** 0.6
    rgba[..., :3] *= rond[..., None]
    return rgba


def plak(foto, rgba, quad, boardmasker=None, licht=1.0, korrel=0.025, verzadiging=0.85, lus=None):
    """Vervorm rgba naar quad (4 punten in de foto: x0y0, x1y0, x1y1, x0y1 van de huid)."""
    h, w = foto.shape[:2]
    H, W = rgba.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [W, 0], [W, H], [0, H]]), np.float32(quad))
    laag = cv2.warpPerspective(rgba, M, (w, h), flags=cv2.INTER_AREA)
    a = laag[..., 3:4]
    if boardmasker is not None:
        a = a * boardmasker[..., None]
    # licht van de foto: grove helderheid van het board
    L = foto @ np.array([.299, .587, .114], np.float32)
    grof = cv2.GaussianBlur(L, (0, 0), 14)
    ref = np.median(grof[a[..., 0] > 0.5]) if (a > 0.5).any() else grof.mean()
    factor = np.clip(grof / ref, 0.6, 1.25)[..., None] * licht
    kleur = laag[..., :3] * factor
    # kleur en korrel van de foto overnemen
    grijs = kleur @ np.array([.299, .587, .114], np.float32)
    kleur = grijs[..., None] + (kleur - grijs[..., None]) * verzadiging
    # filmlook van de foto: zwart iets opgetild, warm
    kleur = kleur * 0.88 + 0.07
    kleur = kleur * np.array([1.03, 1.0, 0.95], np.float32)
    fotokorrel = foto - cv2.GaussianBlur(foto, (0, 0), 1.2)
    kleur = kleur + fotokorrel * 0.9 + rng.normal(0, korrel, kleur.shape).astype(np.float32) * 0.3
    # zachte schaduw op het board net buiten de tas
    s = cv2.GaussianBlur(a[..., 0], (0, 0), 6)
    uit = foto * (1 - 0.25 * (s - a[..., 0]).clip(0, 1)[..., None])
    if lus is not None:
        lrgb, la = lus
        g2 = lrgb @ np.array([.299, .587, .114], np.float32)
        lrgb = g2[..., None] + (lrgb - g2[..., None]) * verzadiging
        lrgb = (lrgb * 0.86 + 0.05) * np.array([1.03, 1.0, 0.95], np.float32) * licht * 0.9
        lrgb = lrgb + fotokorrel * 0.9
        sch = cv2.GaussianBlur(np.roll(np.roll(la, 7, 0), 5, 1), (0, 0), 5)
        uit = uit * (1 - 0.32 * (sch * (1 - la))[..., None])
        la2 = cv2.GaussianBlur(la, (0, 0), 0.6)[..., None]
        uit = uit * (1 - la2) + lrgb * la2
    a = cv2.GaussianBlur(a, (0, 0), 0.7)[..., None] if a.ndim == 2 else cv2.GaussianBlur(a[..., 0], (0, 0), 0.7)[..., None]
    return np.clip(uit * (1 - a) + kleur * a, 0, 1)


def catmull(punten, n=60):
    P = [punten[0]] + list(punten) + [punten[-1]]
    uit = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.asarray, P[i - 1:i + 3])
        for t in np.linspace(0, 1, n, endpoint=False):
            uit.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    uit.append(np.asarray(punten[-1]))
    return np.array(uit, np.float32)


def band_laag(shape, pad, breedte, kleur, draai=False):
    """Band langs een pad in fotocoördinaten: kleur, ribbels, ingeweven logo, stiksels. Geeft (rgb, alpha)."""
    from scipy.spatial import cKDTree
    h, w = shape
    seg = np.diff(pad, axis=0)
    lengte = np.r_[0, np.cumsum(np.linalg.norm(seg, axis=1))]
    raak = np.r_[seg[:1], seg]; raak /= np.linalg.norm(raak, axis=1)[:, None] + 1e-9
    norm = np.stack([-raak[:, 1], raak[:, 0]], 1)
    x0, y0 = int(max(pad[:, 0].min() - breedte, 0)), int(max(pad[:, 1].min() - breedte, 0))
    x1, y1 = int(min(pad[:, 0].max() + breedte, w)), int(min(pad[:, 1].max() + breedte, h))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    pts = np.stack([xx.ravel(), yy.ravel()], 1)
    _, idx = cKDTree(pad).query(pts)
    rel = pts - pad[idx]
    dw = (rel * norm[idx]).sum(1).reshape(yy.shape)
    ln = (lengte[idx] + (rel * raak[idx]).sum(1)).reshape(yy.shape)
    if draai:
        # een hangende band draait: soms zie je hem plat, soms bijna op zijn kant
        tot = lengte[-1]
        c = np.clip(np.abs(np.cos((ln / tot - 0.5) * np.pi * 1.1)) * 1.15, 0, 1)    # plat waar hij op het vak ligt, gedraaid in de bocht
        hw = breedte / 2 * (0.35 + 0.65 * c)
    else:
        c = np.ones_like(dw); hw = breedte / 2
    a = np.clip((hw - np.abs(dw)) / 1.0, 0, 1)
    rand = np.exp(-((hw - np.abs(dw)) / 1.4) ** 2)
    rib = 1 + 0.05 * np.sin(dw * 2 * np.pi / 1.6) + rng.normal(0, 0.02, dw.shape)
    k = np.array(kleur, np.float32)[None, None] * rib[..., None]
    ls = SC.logo_strook(int(round(breedte)), periode=int(breedte * 3.6), hoogte=max(int(breedte * 0.27), 4))
    t = cv2.remap(ls, (ln % ls.shape[1]).astype(np.float32), np.clip(dw + breedte / 2, 0, ls.shape[0] - 1).astype(np.float32), cv2.INTER_LINEAR)[..., None]
    k = k * (1 - t) + np.clip(k * 1.28 + 0.04, 0, 1) * t
    # een band die hangt draait iets: lichtverloop over de lengte
    k = k * (0.62 + 0.38 * c)[..., None] * (1 - 0.35 * rand)[..., None]
    rgb = np.zeros((h, w, 3), np.float32); al = np.zeros((h, w), np.float32)
    rgb[y0:y1, x0:x1] = k; al[y0:y1, x0:x1] = a
    return rgb, al


def hangende_lus(foto, M, W, H, boardbreedte, kleur, breedte):
    """De lus loopt door vanuit de twee strengen op het vak, over de rail, en hangt dan met de zwaartekracht naar beneden.
    Lengte uit de fabrieksfoto: ~10 tegels band buiten het board."""
    xm = W / 2; tg = H / 5.5
    def foto_pt(x, y):
        return cv2.perspectiveTransform(np.float32([[[x, y]]]), M)[0, 0]
    strengen = []
    for kant in (-1, 1):
        x0, x1 = xm + kant * 3.15 * tg, xm + kant * 1.99 * tg
        binnen = foto_pt(x0 + (x1 - x0) * 0.8, H * 0.8)     # op de streng, nog op het vak
        rail = foto_pt(x1, H)                               # waar de streng het board verlaat
        richting = rail - binnen; richting /= np.linalg.norm(richting)
        strengen.append((binnen, rail, richting))
    strengen.sort(key=lambda t: t[1][1])                    # boven eerst
    (b1, e1, d1), (b2, e2, d2) = strengen
    tegel = boardbreedte / 5.5
    neer = np.array([0, 1], np.float32)
    uit = (d1 + d2) / 2; uit[1] = 0; uit /= (np.linalg.norm(uit) + 1e-6)
    diepte = 3.0 * tegel                                    # onderkant lus onder het onderste aanhechtpunt
    onder = e2 + neer * diepte + uit * tegel * 0.55
    pad = catmull([b1, e1,
                   e1 + d1 * tegel * 0.45 + neer * tegel * 0.25,
                   e1 + uit * tegel * 0.95 + neer * (e2[1] - e1[1] + diepte * 0.45),
                   onder,
                   e2 + uit * tegel * 0.35 + neer * diepte * 0.5,
                   e2 + d2 * tegel * 0.3 + neer * tegel * 0.15,
                   e2, b2], n=70)
    return band_laag(foto.shape[:2], pad, breedte, kleur, draai=True)


def laad(naam):
    return np.asarray(Image.open(BRON / naam).convert('RGB')).astype(np.float32) / 255


def bewaar(img, pad, kwaliteit=86):
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(pad, quality=kwaliteit, optimize=True, progressive=True)


def busje():
    foto = laad('busje.jpg')
    neus, staart = np.array([420, 330], np.float32), np.array([150, 1270], np.float32)
    u = neus - staart; u /= np.linalg.norm(u)
    n = np.array([-u[1], u[0]])
    c = (neus + staart) / 2                 # balanspunt: midden van het board
    half_b = 128
    half_l = 4.48 * (2 * half_b) / 5.5      # lange rand 9 tegels, board ~5,5 tegels breed
    quad = [c - u * half_l + n * half_b, c + u * half_l + n * half_b, c + u * half_l - n * half_b, c - u * half_l - n * half_b]
    bm = np.zeros(foto.shape[:2], np.uint8)
    rand = np.array([[455, 330], [470, 420], [455, 600], [415, 830], [360, 980], [300, 1100], [240, 1270], [80, 1270], [95, 1050], [150, 840], [215, 620], [290, 440], [380, 340]], np.int32)
    cv2.fillPoly(bm, [rand], 1)
    bm = cv2.GaussianBlur(bm.astype(np.float32), (0, 0), 1.5)
    rgba = huid(half_l * 2, half_b * 2, kort=0.54, band_kleur=(0.40, 0.49, 0.6))
    H, W = rgba.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [W, 0], [W, H], [0, H]]), np.float32(quad))
    lus = hangende_lus(foto, M, W, H, half_b * 2, (0.40, 0.49, 0.6), half_b * 2 / 5.5 * 47 / 98)
    return plak(foto, rgba, quad, bm, verzadiging=0.78, lus=lus)


def knuffel():
    foto = laad('knuffel.jpg')
    u = np.array([0.0, -1.0], np.float32); n = np.array([1.0, 0.0], np.float32)
    neus_y, staart_y = 141, 1382
    c = np.array([492, (neus_y + staart_y) / 2], np.float32)   # balanspunt
    half_b = 160
    half_l = 4.48 * (2 * half_b) / 5.5
    quad = [c - u * half_l + n * half_b, c + u * half_l + n * half_b, c + u * half_l - n * half_b, c - u * half_l - n * half_b]
    bm = np.zeros(foto.shape[:2], np.uint8)
    rand = np.array([[348, 420], [636, 420], [650, 600], [652, 900], [646, 1110], [336, 1110], [330, 900], [334, 600]], np.int32)
    cv2.fillPoly(bm, [rand], 1)
    # armen en handen blijven voor de tas: huid en shirt zijn veel verzadigder of donkerder dan het board
    hsv = cv2.cvtColor((foto * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    arm = ((hsv[..., 1] > 140) | (hsv[..., 2] < 35)).astype(np.uint8)
    arm = cv2.morphologyEx(arm, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    arm = cv2.morphologyEx(arm, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    arm = cv2.dilate(arm, np.ones((3, 3), np.uint8))
    bm = bm * (1 - arm)
    bm = cv2.GaussianBlur(bm.astype(np.float32), (0, 0), 1.2)
    rgba = huid(half_l * 2, half_b * 2, kort=0.54, band_kleur=(0.40, 0.49, 0.6), zaad=9)
    H, W = rgba.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [W, 0], [W, H], [0, H]]), np.float32(quad))
    lus = hangende_lus(foto, M, W, H, half_b * 2, (0.40, 0.49, 0.6), half_b * 2 / 5.5 * 47 / 98)
    return plak(foto, rgba, quad, bm, licht=0.93, verzadiging=0.62, lus=lus)

if __name__ == '__main__':
    DOEL = ROOT / 'docs' / 'producten' / 'fabriek'
    bewaar(busje(), DOEL / 'lifestyle-busje.jpg')
    bewaar(knuffel(), DOEL / 'lifestyle-knuffel.jpg')
    print('klaar')
