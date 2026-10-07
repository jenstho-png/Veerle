"""Levensechte productfoto's van de surfponcho in badstof (surfponcho-tegel-1, -2, -3), opgevouwen zoals hij verkocht wordt.

Studiostijl zoals alle productfoto's (stijl.py): recht van boven, echt zand, raamlicht linksboven.

De poncho ligt netjes opgevouwen tot een pakket van 38 x 42 cm en zo'n 5 cm dik:
- de zoom is omhooggeslagen tot vlak onder de schouders, zodat de tegelrand (een rij kleine ruitjes in koraal, baby blue
  en crème met een navy stip, zoals op de vorige poncho-foto's) bovenaan over de hele breedte loopt en om de zijvouwen
  heen verdwijnt; daarboven de open zoom met stiksel;
- de zijkanten zijn naar achteren gevouwen (ronde vouwranden), de onderkant is een vouw; onder de bovenste laag steken
  de lagen eronder hier en daar een paar millimeter uit, zodat je de dikte ziet;
- de capuchon ligt plat naar beneden over het pakket, met middennaad en het kleine geweven TIDE TODE label in de nek.

Badstof: echte lusjes uit een uitsnede van dezelfde Unsplash-foto als docs/producten/stock/handdoek-1.jpg, in hoge
resolutie (docs/producten/stock/badstof-macro-1.jpg, zie bronnen.json). Daarvan wordt alleen het licht en donker van de
lusjes gebruikt; met image quilting (Efros en Freeman: per stukje de best passende kandidaat, naad langs de kleinste
fout) wordt het een naadloos stuk stof zonder herhaling. Die stof wordt via stofcoördinaten afgebeeld, zodat de lusjes
over de ronde vouwen in elkaar schuiven. De randen zijn rafelig op de schaal van de lusjes.

Vorm en licht: per laag een hoogtekaart in cm (ronde vouwranden, zoomrand, capuchon, label); daaruit normalen, het
raamlicht van linksboven, zelfschaduw (stralen naar het licht) en contactschaduw. Daarna ST.leg op het zand,
ST.afwerking en ST.bewaar.

Gebruik: python3 tools/producten/echt_poncho.py [foto1 foto2 foto3]
"""
import pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import stijl as ST      # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
BADSTOF_BRON = STOCK / 'badstof-macro-1.jpg'
BRON_PPC = 55.0                       # lusjes in de bronfoto: ongeveer 55 px per cm
LABEL_PNG = HIER / 'uit_handdoek' / 'label.png'    # navy label met crème TIDE TODE (600 x 288, 5 x 2,4 cm)


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


# garenkleuren (de tegelkleuren zoals in docs/producten/referentie/tegelprint.png)
ZEEBLAUW = hexrgb('#6D94B4')          # zacht zeeblauw badstof (albedo; in beeld na licht ca. #5F86A6)
KORAAL = hexrgb('#C9684A')
BABY = hexrgb('#9BB4D0')
CREME = hexrgb('#F1EBDF')
NAVY = hexrgb('#22324F')
GAREN_DONKER = hexrgb('#4E7393')      # stiksel in iets donkerder blauw garen

# maten van het opgevouwen pakket (cm)
BREED, LANG = 38.0, 42.0
DIK = 5.0                             # dikte van het pakket
R = DIK / 2                           # straal van de vouwranden
YH = 2.7                              # open zoom: zoveel cm onder de bovenkant
ZOOMSTROOK = 1.1                      # effen blauwe zoom tot de tegelrand
TEGEL = 4.0                           # tegelrand: tegels van 4 cm
BAND = (YH + ZOOMSTROOK, YH + ZOOMSTROOK + TEGEL)
STAP_ZOOM = 0.75                      # zoveel dikker is het deel met de omgeslagen zoom
KAP_DIK = 1.15
LABEL_CM = (4.4, 2.1)
LABEL_Y = 2.55                        # bovenkant van het label (cm onder de bovenkant van het pakket)

# licht: raam linksboven, 50 graden hoog
_ld = np.array([-0.62, -0.78], np.float32); _ld /= np.linalg.norm(_ld)
ELEV = np.radians(50)
LICHT3 = np.array([_ld[0] * np.cos(ELEV), _ld[1] * np.cos(ELEV), np.sin(ELEV)], np.float32)


# ---------- ruis ----------
def ruis2d(h, w, sigma, zaad):
    r = np.random.default_rng(zaad).normal(0, 1, (h, w)).astype(np.float32)
    r = cv2.GaussianBlur(r, (0, 0), sigma)
    return r / (r.std() + 1e-6)


def ruis1d(t_cm, sigma_cm, zaad, lengte=200.0):
    """Gladde 1D-ruis (std 1) als functie van een positie in cm."""
    n = int(lengte / 0.25)
    r = np.random.default_rng(zaad).normal(0, 1, n).astype(np.float32)
    r = cv2.GaussianBlur(r[None], (0, 0), sigmaX=sigma_cm / 0.25, sigmaY=0.01)[0]
    r /= r.std() + 1e-6
    return np.interp(t_cm + lengte / 2, np.arange(n) * 0.25, r).astype(np.float32)


# ---------- badstof ----------
def _mincut(E):
    """Verticale naad met de kleinste fout door E (h x o). Geeft per rij de kolom van de naad."""
    h, o = E.shape
    C = E.copy()
    for r in range(1, h):
        links = np.r_[np.inf, C[r - 1, :-1]]
        rechts = np.r_[C[r - 1, 1:], np.inf]
        C[r] += np.minimum(np.minimum(links, C[r - 1]), rechts)
    pad = np.empty(h, np.int32)
    pad[-1] = int(np.argmin(C[-1]))
    for r in range(h - 2, -1, -1):
        c = pad[r + 1]
        lo, hi = max(0, c - 1), min(o, c + 2)
        pad[r] = lo + int(np.argmin(C[r, lo:hi]))
    return pad


def quilt(bron, h, w, P, O, zaad, kandidaten=48):
    """Image quilting: naadloos vlak van h x w uit de bron, stukjes van P px met O px overlap."""
    rng = np.random.default_rng(zaad)
    st = P - O
    ny, nx = (h - O + st - 1) // st + 1, (w - O + st - 1) // st + 1
    uit = np.zeros((ny * st + O, nx * st + O), np.float32)
    bh, bw = bron.shape
    for i in range(ny):
        for j in range(nx):
            y, x = i * st, j * st
            ys = rng.integers(0, bh - P, kandidaten); xs = rng.integers(0, bw - P, kandidaten)
            kand = np.stack([bron[a:a + P, b:b + P] for a, b in zip(ys, xs)])
            flip = rng.random(kandidaten) < 0.5
            kand[flip] = kand[flip][:, :, ::-1]
            fout = np.zeros(kandidaten, np.float32)
            if j:
                fout += ((kand[:, :, :O] - uit[y:y + P, x:x + O][None]) ** 2).sum((1, 2))
            if i:
                fout += ((kand[:, :O, :] - uit[y:y + O, x:x + P][None]) ** 2).sum((1, 2))
            goed = np.where(fout <= fout.min() * 1.1 + 1e-6)[0]
            stuk = kand[rng.choice(goed)]
            m = np.ones((P, P), np.float32)
            if j:
                pad = _mincut((stuk[:, :O] - uit[y:y + P, x:x + O]) ** 2)
                for r, c in enumerate(pad):
                    m[r, :c] = 0
            if i:
                pad = _mincut(((stuk[:O, :] - uit[y:y + O, x:x + P]) ** 2).T)
                for c, r in enumerate(pad):
                    m[:r, c] = 0
            if i or j:
                m = cv2.GaussianBlur(m, (0, 0), 0.8)
            uit[y:y + P, x:x + P] = uit[y:y + P, x:x + P] * (1 - m) + stuk * m
    return uit[:h, :w]


_BADSTOF = {}


def badstof(h, w, ppc, zaad):
    """Relatieve lichtheid van de lusjes (gemiddeld 1) als vlak van h x w px bij ppc px per cm."""
    sleutel = (h, w, round(ppc, 2), zaad)
    if sleutel in _BADSTOF:
        return _BADSTOF[sleutel]
    img = np.asarray(Image.open(BADSTOF_BRON).convert('RGB')).astype(np.float32) / 255
    G = img[..., 1]                                     # groen kanaal draagt het meeste detail van de blauwe lusjes
    rel = G / cv2.GaussianBlur(G, (0, 0), BRON_PPC * 0.8)   # geen licht of bolling, alleen lusjes en plukjes
    s = ppc / BRON_PPC
    rel = cv2.resize(rel, (int(rel.shape[1] * s), int(rel.shape[0] * s)),
                     interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    P = int(round(2.4 * ppc)); O = max(6, P // 4)
    t = quilt(rel, h, w, P, O, zaad)
    t = 1 + (t - t.mean()) * (rel.std() / max(t.std(), 1e-6))
    _BADSTOF[sleutel] = t.astype(np.float32)
    return _BADSTOF[sleutel]


def bemonster(tex, U, V, ppc, du=0.0, dv=0.0):
    return cv2.remap(tex, ((U + du) * ppc).astype(np.float32), ((V + dv) * ppc).astype(np.float32),
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------- vormen ----------
def rolprofiel(e, r, top):
    """Hoogte (cm) van een ronde vouwrand: e = afstand tot de buitenrand (cm), r = straal, top = hoogte bovenop."""
    e = np.clip(e, 0, r)
    return top - r + np.sqrt(np.clip(r * r - (r - e) ** 2, 0, None))


def rol_uv(e, r):
    """Verschuiving van de stofcoördinaat op een ronde rand: van boven gezien schuift de stof in elkaar."""
    e = np.clip(e, 0, r)
    phi = np.arcsin(np.clip(1 - e / r, -1, 1))
    return r - r * phi - e


def afgeronde_afstand(el, er, et, eb, rc):
    """Afstand tot de rand van een rechthoek met afgeronde hoeken (straal rc), positief binnen."""
    qx = np.maximum(rc - np.minimum(el, er), 0)
    qy = np.maximum(rc - np.minimum(et, eb), 0)
    hoek = (qx > 0) & (qy > 0)
    return np.where(hoek, rc - np.hypot(qx, qy), np.minimum(np.minimum(el, er), np.minimum(et, eb)))


def tegelrand(U, V, ppc, tex):
    """Albedo en dekking van de tegelrand: rij tegels van TEGEL cm, ruit met stip, ingeweven in de badstof.
    De randjes van de vormen volgen de lusjes (geen strakke drukrand)."""
    gy, gx = np.gradient(cv2.GaussianBlur(tex, (0, 0), max(0.6, ppc * 0.03)))
    k = 0.10 * ppc                            # ca. 1 mm verschuiving per eenheid helling: lusjes over de rand
    Uu = U + gx * k / max(ppc * 0.02, 1)
    Vv = V + gy * k / max(ppc * 0.02, 1)
    v0, v1 = BAND
    i = np.floor(Uu / TEGEL).astype(np.int64)
    fu = Uu / TEGEL - i - 0.5
    fv = (Vv - v0) / TEGEL - 0.5
    # kleurvolgorde zoals de tegelprint: nooit twee dezelfde naast elkaar
    volg = np.array([0, 1, 2, 0, 1, 0, 2, 1, 2, 0, 1, 2, 0, 2, 1], np.int64)
    soort = volg[np.mod(i, len(volg))]
    grond = np.where((soort == 0)[..., None], KORAAL, np.where((soort == 1)[..., None], BABY, CREME))
    ruit_kl = np.where((soort == 2)[..., None], KORAAL, CREME)
    aa = 1.0 / (TEGEL * ppc) * 1.2
    ruit = np.clip((0.37 - (np.abs(fu) + np.abs(fv))) / aa + 0.5, 0, 1)[..., None]
    stip = np.clip((0.125 - np.hypot(fu, fv)) / aa + 0.5, 0, 1)[..., None]
    kl = grond * (1 - ruit) + ruit_kl * ruit
    kl = kl * (1 - stip) + NAVY * stip
    dek = np.clip((Vv - v0) * ppc + 0.5, 0, 1) * np.clip((v1 - Vv) * ppc + 0.5, 0, 1)
    return kl.astype(np.float32), dek.astype(np.float32)


def stiksel(afstand_cm, langs_cm, ppc, breedte=0.045, steek=0.32):
    """Gestikte lijn: afstand tot de lijn (cm) en positie langs de lijn (cm) -> dekking van de steekjes."""
    lijn = np.exp(-(afstand_cm / breedte) ** 2)
    steken = np.clip((np.cos(langs_cm / steek * 2 * np.pi) + 0.35) * 2.0, 0, 1)
    return (lijn * steken).astype(np.float32)


def label_textuur(ppc):
    """Het geweven label op schaal: fijne inslagribbel, letters iets bol, randjes omgevouwen."""
    a = np.asarray(Image.open(LABEL_PNG).convert('RGB')).astype(np.float32) / 255
    lb, lh = int(round(LABEL_CM[0] * ppc * 2)), int(round(LABEL_CM[1] * ppc * 2))   # dubbele resolutie
    img = cv2.resize(a, (lb, lh), interpolation=cv2.INTER_AREA)
    # alleen het merk, zonder de ruime navy marge van de render: iets inzoomen
    yy, xx = np.mgrid[0:lh, 0:lb].astype(np.float32)
    L = img.mean(2)
    hoog = cv2.GaussianBlur(L, (0, 0), max(0.8, ppc * 0.02))
    rel = 1 + 0.6 * (np.roll(hoog, 1, 0) - np.roll(hoog, -1, 0))
    rib = 1 + 0.06 * np.sin(yy * 2 * np.pi / max(2.2, 0.05 * ppc * 2)) + 0.025 * np.sin(xx * 2 * np.pi / max(2.0, 0.04 * ppc * 2))
    img = np.clip(cv2.GaussianBlur(img, (0, 0), max(0.6, ppc * 0.012)) * (rel * rib)[..., None], 0, 1)
    # glans van polyester damast: heel licht
    img = np.clip(img * 1.02 + 0.01, 0, 1)
    return img


# ---------- het pakket ----------
def poncho_lagen(X, Y, ppc, kap='op', zaad=1):
    """Alle lagen van de opgevouwen poncho in cm-coördinaten X, Y (bovenkant pakket y = 0, links x = 0).
    Geeft een lijst van lagen (onder naar boven): dict(alpha, z, rgb, tex)."""
    h, w = X.shape
    lagen = []
    # buitenrand met een heel klein beetje golving (gevouwen stof is nooit messcherp)
    xL = 0.0 + 0.16 * ruis1d(Y, 5, zaad + 1)
    xR = BREED + 0.16 * ruis1d(Y, 5, zaad + 2)
    yT = 0.0 + 0.12 * ruis1d(X, 6, zaad + 3)
    yB = LANG + 0.18 * ruis1d(X, 5, zaad + 4)
    el, er, et, eb = X - xL, xR - X, Y - yT, yB - Y
    rc = 2.6
    e = afgeronde_afstand(el, er, et, eb, rc)
    tex_kader = lambda z: badstof(h, w, ppc, zaad * 10 + z)    # noqa: E731

    # rafelige rand: de lusjes steken een fractie uit (sterkte in px)
    def dekking(e_cm, tex, rafel=0.09):
        return np.clip(e_cm * ppc + 0.5 + (tex - 1) / 0.18 * rafel * ppc, 0, 1).astype(np.float32)

    # 1. onderste lagen die hier en daar uitsteken (de dikte van het pakket)
    uit_l = np.clip(0.25 + 0.22 * ruis1d(Y, 7, zaad + 11), 0, 0.5)
    uit_r = np.clip(0.12 + 0.20 * ruis1d(Y, 7, zaad + 12), 0, 0.45)
    uit_b = np.clip(0.22 + 0.22 * ruis1d(X, 7, zaad + 13), 0, 0.5)
    e2 = afgeronde_afstand(el + uit_l, er + uit_r, et + 0.0, eb + uit_b, rc + 0.3)
    r2 = DIK * 0.42
    z2 = rolprofiel(e2, r2, DIK - 1.1)
    U2 = X + rol_uv(el + uit_l, r2) - rol_uv(er + uit_r, r2)
    V2 = Y - rol_uv(eb + uit_b, r2)
    t2 = bemonster(tex_kader(2), U2, V2, ppc, 3.0, 5.0)
    lagen.append(dict(alpha=dekking(e2, t2), z=z2, rgb=np.broadcast_to(ZEEBLAUW, (h, w, 3)).copy(), tex=t2))

    # 2. het pakket zelf, met de omgeslagen zoom en de tegelrand bovenaan
    z = rolprofiel(e, R, DIK)
    bol = 0.22 * ruis2d(h, w, 5.0 * ppc, zaad + 21) + 0.10 * ruis2d(h, w, 1.6 * ppc, zaad + 22)
    z = z + bol * np.clip(e / R, 0, 1)
    U = X + rol_uv(el, R) - rol_uv(er, R)
    V = Y + rol_uv(et, R) - rol_uv(eb, R)
    t = bemonster(tex_kader(1), U, V, ppc)
    # de stof boven de open zoom is een andere laag (lager, andere lusjes)
    d_zoom = Y - (YH + 0.10 * ruis1d(X, 4, zaad + 31))          # cm onder de zoomrand
    hem = np.sqrt(np.clip(1 - (1 - np.clip(d_zoom / 0.45, 0, 1)) ** 2, 0, 1))
    z = np.minimum(z, DIK - STAP_ZOOM + STAP_ZOOM * hem + bol * 0.5)
    boven = np.clip(-d_zoom * ppc + 0.5, 0, 1)
    t_b = bemonster(tex_kader(3), U, V, ppc, 7.0, 2.0)
    t = t * (1 - boven) + t_b * boven
    rgb = np.broadcast_to(ZEEBLAUW, (h, w, 3)).copy()
    kl, dek = tegelrand(U, V, ppc, t)
    dek = dek * (1 - boven)
    rgb = rgb * (1 - dek[..., None]) + kl * dek[..., None]
    # stiksel van de zoom, en de zoomrand zelf iets donkerder waar hij omkrult
    st = stiksel(d_zoom - 0.85, U, ppc) * (1 - boven)
    rgb = rgb * (1 - 0.55 * st[..., None]) + GAREN_DONKER * 0.55 * st[..., None]
    lagen.append(dict(alpha=dekking(e, t), z=z.astype(np.float32), rgb=rgb, tex=t, zoomrand=d_zoom))

    # 3. de capuchon
    if kap == 'op':
        xc = BREED / 2 + 0.05 * ruis1d(Y, 8, zaad + 41)
        # halve breedte: 10 cm in de nek, 11 cm op de breedste plek, ronde punt op 20 cm
        yk = np.array([-6, 0, 4, 9, 12, 15, 17, 18.5, 19.6, 20.2], np.float32)
        hk = np.array([10.0, 10.0, 10.6, 11.0, 10.8, 9.6, 8.0, 6.1, 3.8, 0.0], np.float32)
        hw = np.interp(Y, yk, hk, right=0.0) + 0.12 * ruis1d(Y, 3, zaad + 42)
        S = 4
        mask_ss = np.zeros((h * S, w * S), np.uint8)
        # rand als veelhoek op hoge resolutie, dan afstand tot de rand
        ys = np.linspace(-6, 20.2, 400)
        hwp = np.interp(ys, yk, hk)
        cx_p = BREED / 2
        pts = np.concatenate([np.stack([cx_p + hwp, ys], 1), np.stack([cx_p - hwp, ys], 1)[::-1]])
        x0, y0 = X[0, 0] - 0.5 / ppc, Y[0, 0] - 0.5 / ppc
        pts_px = ((pts - [x0, y0]) * ppc * S).astype(np.int32)
        cv2.fillPoly(mask_ss, [pts_px], 1, lineType=cv2.LINE_8)
        dist = cv2.distanceTransform(mask_ss, cv2.DIST_L2, 5)
        dist = cv2.resize(dist, (w, h), interpolation=cv2.INTER_AREA) / (ppc * S)
        golf = 0.10 * ruis2d(h, w, 2.5 * ppc, zaad + 43)
        e_k = dist + golf - 0.02
        onder = cv2.GaussianBlur(np.minimum(rolprofiel(e, R, DIK) + bol, DIK + 0.3), (0, 0), 0.9 * ppc)
        rk = KAP_DIK * 0.5
        zk = onder + rolprofiel(e_k, rk, KAP_DIK) - (KAP_DIK - rk) * 0
        zk = np.where(e_k > 0, zk, onder + KAP_DIK - rk)
        # middennaad (ondiepe groef) met twee stiksels; lichte plooitjes vanuit de nek
        dx = X - xc
        zk = zk - 0.14 * np.exp(-(dx / 0.2) ** 2) * (Y > 0.5)
        plooi = np.zeros_like(X)
        for (ax, ay, hoek, lengte, diep) in [(-5.5, 1.0, 1.15, 8, 0.16), (6.0, 1.2, 2.0, 7, 0.14), (-8.5, 6, 1.35, 6, 0.10),
                                             (8.0, 9, 1.75, 6, 0.09), (-2.5, 13.5, 1.45, 5, 0.07)]:
            ux, uy = np.cos(hoek), np.sin(hoek)
            px, py = dx - ax, Y - ay
            langs = px * ux + py * uy
            dwars = -px * uy + py * ux
            plooi += diep * np.exp(-(dwars / 0.55) ** 2) * np.exp(-((langs - lengte / 2) / (lengte / 2)) ** 4)
        zk = zk + plooi * np.clip(e_k / 0.8, 0, 1)
        Uk = X + 61.0; Vk = Y + 47.0
        tk = bemonster(tex_kader(4), Uk, Vk, ppc)
        rgbk = np.broadcast_to(ZEEBLAUW, (h, w, 3)).copy()
        naad = (stiksel(np.abs(dx) - 0.38, Y, ppc) * (Y > 1.0) * (Y < 19.4)).astype(np.float32)
        rgbk = rgbk * (1 - 0.5 * naad[..., None]) + GAREN_DONKER * 0.5 * naad[..., None]
        ak = dekking(e_k, tk, 0.07) * np.clip(e * ppc + 0.5, 0, 1)
        lagen.append(dict(alpha=ak.astype(np.float32), z=zk.astype(np.float32), rgb=rgbk, tex=tk))

        # 4. het geweven label in de nek, plat op de capuchon gestikt (korte kanten omgevouwen en vastgestikt)
        lb, lh = LABEL_CM
        lx0, ly0 = BREED / 2 - lb / 2, LABEL_Y
        lab = label_textuur(ppc)
        Lh, Lw = lab.shape[:2]
        su = ((X - lx0) / lb * Lw).astype(np.float32); sv = ((Y - ly0) / lh * Lh).astype(np.float32)
        rgbl = cv2.remap(lab, su, sv, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        el_ = np.minimum(X - lx0, lx0 + lb - X); et_ = np.minimum(Y - ly0, ly0 + lh - Y)
        al = (np.clip(el_ * ppc + 0.5, 0, 1) * np.clip(et_ * ppc + 0.5, 0, 1)).astype(np.float32)
        # omgevouwen uiteinden: vouwlijn 0,3 cm van de korte kant en een rij navy steekjes
        vouw = np.exp(-((el_ - 0.30) / 0.03) ** 2)
        st = stiksel(el_ - 0.16, Y, ppc, 0.03, 0.18)
        rgbl = rgbl * (1 - 0.35 * vouw[..., None])
        rgbl = rgbl * (1 - 0.6 * st[..., None]) + hexrgb('#1A2840') * 0.6 * st[..., None]
        # lange randjes iets omgerold (donkerder)
        rgbl = rgbl * (1 - 0.25 * np.exp(-np.clip(et_, 0, None) / 0.05))[..., None]
        zl = zk + 0.06 + 0.04 * np.clip(et_ / 0.2, 0, 1) - 0.03 * vouw
        lagen.append(dict(alpha=al, z=zl.astype(np.float32), rgb=rgbl.astype(np.float32), tex=np.ones((h, w), np.float32),
                          vlak=True))
    return lagen


def belicht(lagen, ppc, schaduw=0.55):
    """Lagen samenvoegen tot rgba: licht per laag (normalen), dan zelfschaduw en contactschaduw op de samengestelde hoogte."""
    h, w = lagen[0]['z'].shape
    rgb = np.zeros((h, w, 3), np.float32)
    a = np.zeros((h, w), np.float32)
    Z = np.zeros((h, w), np.float32)
    for lg in lagen:
        z = cv2.GaussianBlur(lg['z'], (0, 0), max(0.6, ppc * 0.02))
        gy, gx = np.gradient(z)
        gx, gy = gx * ppc, gy * ppc
        m = np.hypot(gx, gy)
        k = np.minimum(1, 6.0 / np.maximum(m, 1e-6))          # bijna verticaal aan de buitenrand
        gx, gy = gx * k, gy * k
        n = np.dstack([-gx, -gy, np.ones_like(gx)])
        n /= np.linalg.norm(n, axis=2, keepdims=True)
        nl = np.clip((n * LICHT3).sum(2), 0, None)
        nz = n[..., 2]
        # raamlicht + hemel van boven + wat terugkaatsing van het zand
        s = 0.30 + 0.25 * nz + 0.45 * nl / LICHT3[2] + 0.13 * (1 - nz)
        tex = lg['tex']
        if lg.get('vlak'):
            kleur = lg['rgb'] * s[..., None]
        else:
            # in de dalletjes van de badstof valt minder licht; op de schaduwkant tellen de lusjes zwaarder
            kleur = lg['rgb'] * (s * tex ** (1.0 + 0.6 * (1 - s)))[..., None]
        al = lg['alpha']
        rgb = rgb * (1 - al[..., None]) + kleur * al[..., None]
        Z = Z * (1 - al) + lg['z'] * al
        a = np.maximum(a, al)
    # zelfschaduw: kijk vanuit elk punt richting het raam of er iets hogers in de weg zit
    tanE = np.tan(ELEV)
    blok = np.zeros((h, w), np.float32)
    stap = max(1.0, ppc * 0.04)
    for k in np.arange(stap, 2.2 * ppc, stap):
        M = np.float32([[1, 0, -k * _ld[0]], [0, 1, -k * _ld[1]]])
        Zs = cv2.warpAffine(Z, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        # warpAffine: punt p krijgt Z(p - verschuiving) = Z(p + k * richting naar het raam)
        blok = np.maximum(blok, np.clip((Zs - Z - (k / ppc) * tanE) / 0.25, 0, 1))
    blok = cv2.GaussianBlur(blok, (0, 0), 0.22 * ppc)
    ao = 1 - 0.30 * np.clip((cv2.GaussianBlur(Z, (0, 0), 0.7 * ppc) - Z) / 0.5, 0, 1)
    rgb = rgb * ((1 - schaduw * blok) * ao)[..., None]
    return np.dstack([np.clip(rgb, 0, 1), a]).astype(np.float32), Z


def op_zand(rgba, Z, ppc, zaad=1, hoogte_cm=1.1):
    """Op het zand leggen met ST.leg (zachte slagschaduw rechtsonder), plus de donkere kier waar de ronde vouw het zand raakt."""
    doek = ST.achtergrond('zand', zaad=zaad)
    if doek.shape[:2] != rgba.shape[:2]:
        doek = cv2.resize(doek, (rgba.shape[1], rgba.shape[0]), interpolation=cv2.INTER_CUBIC)
    a = rgba[..., 3]
    off = 0.25 * ppc
    M = np.float32([[1, 0, -_ld[0] * off], [0, 1, -_ld[1] * off]])
    kier = cv2.GaussianBlur(cv2.warpAffine(a, M, (a.shape[1], a.shape[0])), (0, 0), 0.22 * ppc)
    ring = cv2.GaussianBlur(a, (0, 0), 0.12 * ppc)
    doek = doek * (1 - (0.42 * kier + 0.25 * ring) * (1 - a))[..., None]
    schaal = rgba.shape[1] / ST.B
    hoogte = hoogte_cm * ppc / 2.2 / schaal
    uit = ST.leg(doek, rgba, breedte=rgba.shape[1], midden=(rgba.shape[1] / 2, rgba.shape[0] / 2), hoogte=hoogte,
                 zachtheid=1.0, contact=0.6)
    return uit


def raster(ppc, cx_cm, cy_cm, b=ST.B, h=ST.H):
    """cm-coördinaten van elk pixel; (cx_cm, cy_cm) komt in het midden van het beeld."""
    xs = cx_cm + (np.arange(b, dtype=np.float32) + 0.5 - b / 2) / ppc
    ys = cy_cm + (np.arange(h, dtype=np.float32) + 0.5 - h / 2) / ppc
    return np.meshgrid(xs, ys)


def bewaar(img, naam):
    pad = ST.bewaar(ST.afwerking(img), DOEL / f'{naam}.jpg')
    kb = pad.stat().st_size / 1000
    if kb >= 190:
        # te zwaar (zandkorrel en lusjes kosten veel bytes): minder korrel in de afwerking
        for korrel in (0.008, 0.005, 0.003):
            pad = ST.bewaar(ST.afwerking(img, korrel=korrel), pad)
            kb = pad.stat().st_size / 1000
            if kb < 190:
                break
    print('foto', naam, f'{kb:.0f} kB')
    return pad


# ---------- de drie foto's ----------
def foto1():
    """Packshot: het opgevouwen pakket met de capuchon erop, midden op het zand."""
    ppc = 28.5
    X, Y = raster(ppc, BREED / 2, LANG / 2 + 0.3)
    rgba, Z = belicht(poncho_lagen(X, Y, ppc, 'op', zaad=1), ppc)
    bewaar(op_zand(rgba, Z, ppc, zaad=1), 'surfponcho-tegel-1')


if __name__ == '__main__':
    for stap in sys.argv[1:] or ['foto1', 'foto2', 'foto3']:
        globals()[stap]()
