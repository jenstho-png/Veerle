"""De draagtas in een echte foto leggen (gebruikt door sfeer.py).

Werkwijze
- Board: gemeten omtrek uit sfeer_meet.py (as c/a, per positie t langs de as de randen lo/hi, balanspunt).
- Huid: vak (stof, zoom, label) in de studiomaat van scene.py (tegel 98 x 115 maal 1,08), plat:
  x langs het board, y dwars (y=0 bij de rail van de lus = korte zijde, y=Hs bij de lange zijde).
  De zichtbare boardbreedte komt overeen met 5,5 tegelhoogtes stof (zoals op de fabrieksfoto).
- Afbeelding huid -> foto: t = balanspunt + x/k, dwars via de echte randen; de laatste 10 % naar de rail
  loopt de stof om de ronding (wordt in beeld samengedrukt), en waar het board smaller is loopt de stof verder om de rail.
- Band: één doorlopend pad in fotocoördinaten (lange rail -> streng over het vak -> uit de rail -> lus -> terug -> lange rail),
  met de echte webbingtextuur (scene.band_textuur) en het ingeweven logo (scene.logo_strook).
  De lus is een kleine fysische simulatie: vaste lengte (uit de studiomaten), zwaartekracht, buigstijfheid, botsing met het board.
- Licht: relatieve belichting van het board in de foto (helderheid per positie dwars en langs, robuust tegen logo's),
  belichting, kleur van het licht, korrel en scherpte van de foto.
"""
import math, pathlib, sys
import cv2
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import scene as SC  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock' / 'lifestyle'
TW, TH = 98 * SC.TEGEL, 115 * SC.TEGEL        # tegelbreedte (langs) en -hoogte (dwars) in de huid
HS = 5.5 * TH                                  # stof over de zichtbare boardbreedte
SMAX = 1.0 + 0.1 * (math.pi / 2 - 1)           # stofmaat tot de railtop, in halve breedtes (vlak tot 0,9 + ronding)
XM, Y0 = SC.CW / 2, 1150.0                     # plek van het vak in het studiocanvas
HALF_LANG, HALF_KORT = 4.48 * TW, 0.54 * 4.48 * TW
STR_LANG, STR_KORT = 3.15 * TW, 1.99 * TW      # strengen bij de lange en korte zijde (studiomaten)
rng = np.random.default_rng(21)


# ---------------------------------------------------------------- board
class Board:
    def __init__(self, naam, lus=-1, stringer=0.0, kort=1.0):
        g = np.load(STOCK / 'maskers' / (pathlib.Path(naam).stem + '.npz'))
        self.c, self.a = g['c'].astype(np.float64), g['a'].astype(np.float64)
        self.n = np.array([-self.a[1], self.a[0]])
        self.tt, self.lo, self.hi = g['tt'], g['lo'], g['hi']
        self.tb = float(g['t_balans'])
        self.zicht = np.asarray(Image.open(STOCK / 'maskers' / (pathlib.Path(naam).stem + '.png')).convert('L')).astype(np.float32) / 255
        self.lus = lus                      # -1: lus uit de lo-rail, +1: uit de hi-rail
        self.stringer = stringer            # s-positie van de stringer (0 = midden van het silhouet)
        i = np.argmin(np.abs(self.tt - self.tb))
        self.W = float(self.hi[i] - self.lo[i])
        # referentie halve breedte: breedste punt over het vak
        span = 0.8 * self.W
        sel = np.abs(self.tt - self.tb) < span
        self.href = float(np.max((self.hi - self.lo)[sel]) / 2)
        self.k = HS / (SMAX * 2 * self.href)        # huidpixels per fotopixel (dwars, in het midden)
        # langs (kort < 1 als het board in de lengte verkort is); teken zo dat huid -> beeld nooit spiegelt
        self.kx = self.k * kort * (-lus)

    def mid(self, t):
        return (np.interp(t, self.tt, self.lo) + np.interp(t, self.tt, self.hi)) / 2

    def half(self, t):
        return (np.interp(t, self.tt, self.hi) - np.interp(t, self.tt, self.lo)) / 2

    def naar_ts(self, P):
        rel = P - self.c
        t = rel @ self.a
        q = rel @ self.n
        s = (q - self.mid(t)) / self.half(t)
        return t, s, q

    def naar_beeld(self, t, s):
        q = self.mid(t) + s * self.half(t)
        return self.c[None] + self.a[None] * np.asarray(t)[..., None] + self.n[None] * np.asarray(q)[..., None]

    # dwarsrichting: s (beeld, -1..1 over het silhouet) <-> sigma (stof, in halve referentiebreedtes)
    def s_naar_sigma(self, t, s):
        st = self.stringer
        sp = np.where(s < st, (s - st) / (1 + st), (s - st) / (1 - st))
        a = np.abs(sp)
        sig = np.where(a <= 0.9, a, 0.9 + 0.1 * np.arcsin(np.clip((a - 0.9) / 0.1, 0, 1)))
        return np.sign(sp) * sig * self.half(t) / self.href

    def sigma_naar_s(self, t, sig):
        x = sig * self.href / self.half(t)
        a = np.abs(x)
        sp = np.where(a <= 0.9, a, 0.9 + 0.1 * np.sin(np.clip((a - 0.9) / 0.1, 0, math.pi / 2)))
        sp = np.sign(x) * sp
        st = self.stringer
        return np.where(sp < 0, st + sp * (1 + st), st + sp * (1 - st)), a <= SMAX

    # huid (X, Y) <-> foto
    def huid_naar_beeld(self, X, Y):
        t = self.tb + (np.asarray(X) - XM) / self.kx
        sig = (2 * (np.asarray(Y) - Y0) / HS - 1) * SMAX * (-self.lus)
        s, op = self.sigma_naar_s(t, sig)
        return self.naar_beeld(t, s), op

    def beeld_naar_huid(self, P):
        t, s, _ = self.naar_ts(P)
        sig = self.s_naar_sigma(t, s) * (-self.lus)
        X = XM + (t - self.tb) * self.kx
        Y = Y0 + (sig / SMAX + 1) * HS / 2
        return X, Y, t, s

    def omtrek(self):
        L = np.stack([self.tt, self.lo], 1); H = np.stack([self.tt, self.hi], 1)
        links = self.c[None] + self.a[None] * self.tt[:, None] + self.n[None] * self.lo[:, None]
        rechts = self.c[None] + self.a[None] * self.tt[:, None] + self.n[None] * self.hi[:, None]
        return np.concatenate([links, rechts[::-1]])


# ---------------------------------------------------------------- huid
def hoeken():
    e = 14.0      # stof loopt iets verder om de rail dan het silhouet
    return np.array([[XM - HALF_KORT, Y0 - e], [XM + HALF_KORT, Y0 - e], [XM + HALF_LANG + 0.0, Y0 + HS + e], [XM - HALF_LANG, Y0 + HS + e]], np.float32)


def huid(handle):
    """Vak met stof, zoom en label in het studiocanvas (CH x CW). Geeft rgb en masker."""
    stof = SC.stoflaag() if handle == 'draagtas-tegel' else SC.variant_stof(handle)
    hk = hoeken()
    # de zijden van het trapezium lopen schuin; de rails (y) zijn de evenwijdige zijden
    laag, pm = SC.leg_stof(stof, hk)
    laag = SC.zoom(laag, pm, hk)
    canvas = laag * pm[..., None]
    # stof is nooit helemaal vlak: zachte spanning en kleine golvingen
    H_, W_ = pm.shape
    r = np.random.default_rng(len(handle))
    golf = cv2.GaussianBlur(r.normal(0, 1, (H_ // 8, W_ // 8)).astype(np.float32), (0, 0), 6)
    golf = cv2.resize(golf, (W_, H_), interpolation=cv2.INTER_CUBIC)
    golf = golf / (np.abs(golf).max() + 1e-6)
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    # de band trekt de stof iets aan: net naast de band een lichte kuil
    kuil = np.zeros((H_, W_), np.float32)
    for kant in (-1, 1):
        p0 = np.array([XM + kant * STR_LANG, Y0 + HS]); p1 = np.array([XM + kant * STR_KORT, Y0])
        u = (p1 - p0) / np.linalg.norm(p1 - p0); n = np.array([-u[1], u[0]])
        d = np.abs((xx - p0[0]) * n[0] + (yy - p0[1]) * n[1]) - SC.BAND / 2
        kuil += np.exp(-np.clip(d, 0, None) / 22.0) * (d > 0)
    canvas = canvas * (1 + 0.035 * golf - 0.07 * kuil)[..., None]
    canvas = SC.label(canvas, (XM, Y0 + 75 + 14))
    # label valt binnen het vak, masker blijft pm
    return canvas, pm


# ---------------------------------------------------------------- band
_TEX = None


def band_tex():
    global _TEX
    if _TEX is None:
        _TEX = SC.band_textuur()
    return _TEX


def band(shape, pad, w, kleur, op_stof=None, breed=None, ss=2):
    """Band langs een pad (fotocoördinaten). op_stof: per padpunt 0/1 (stiksels alleen op het vak),
    breed: per padpunt breedtefactor (draaiing). Geeft rgb, alpha, en per pixel de padindex."""
    h, wd = shape
    pad = np.asarray(pad, np.float64)
    # fijn herbemonsteren: ~0.25 px
    seg = np.linalg.norm(np.diff(pad, axis=0), axis=1)
    L = np.r_[0, np.cumsum(seg)]
    m = max(int(L[-1] * 4), 2)
    Ls = np.linspace(0, L[-1], m)
    P = np.stack([np.interp(Ls, L, pad[:, 0]), np.interp(Ls, L, pad[:, 1])], 1)
    stof = np.interp(Ls, L, op_stof) if op_stof is not None else np.zeros(m)
    bf = np.interp(Ls, L, breed) if breed is not None else np.ones(m)
    raak = np.gradient(P, axis=0); raak /= np.linalg.norm(raak, axis=1)[:, None] + 1e-9
    norm = np.stack([-raak[:, 1], raak[:, 0]], 1)
    x0, y0 = int(max(P[:, 0].min() - w, 0)), int(max(P[:, 1].min() - w, 0))
    x1, y1 = int(min(P[:, 0].max() + w + 1, wd)), int(min(P[:, 1].max() + w + 1, h))
    if x1 <= x0 or y1 <= y0:
        return np.zeros((h, wd, 3), np.float32), np.zeros((h, wd), np.float32), np.full((h, wd), -1, np.float32), L
    yy, xx = np.mgrid[y0 * ss:y1 * ss, x0 * ss:x1 * ss].astype(np.float64)
    pts = np.stack([(xx.ravel() + 0.5) / ss - 0.5, (yy.ravel() + 0.5) / ss - 0.5], 1)
    d, idx = cKDTree(P).query(pts, distance_upper_bound=w)
    ok = np.isfinite(d)
    idx = np.where(ok, idx, 0)
    rel = pts - P[idx]
    dw = (rel * norm[idx]).sum(1)
    ln = Ls[idx] + (rel * raak[idx]).sum(1)
    hw = w / 2 * bf[idx]
    a = np.clip((hw - np.abs(dw)) * ss / 1.0 + 0.5, 0, 1) * ok
    # textuur: dwars genormaliseerd op de werkelijke breedte, langs in studiopixels
    f = SC.BAND / w
    tex = band_tex()
    th, tw = tex.shape
    u = np.clip((dw / (2 * hw + 1e-6) + 0.5), 0, 1) * (th - 1)
    v = (ln * f * 2) % (2 * tw - 2)
    v = np.where(v > tw - 1, 2 * tw - 2 - v, v)
    struct = cv2.remap(tex, v.reshape(yy.shape).astype(np.float32), u.reshape(yy.shape).astype(np.float32), cv2.INTER_LINEAR)
    golf = 1 + 0.03 * np.sin(ln * f / 140.0) + 0.012 * np.sin(ln * f / 37.0 + 1.3)
    k = np.array(kleur, np.float32)[None] * ((1 + 0.16 * struct.ravel()) * golf)[:, None]
    # ingeweven logo (op 4x de studiomaat gemaakt voor scherpte)
    LS4 = _logo()
    lh, lw = LS4.shape
    tu = np.clip((dw / (2 * hw + 1e-6) + 0.5) * (lh - 1), 0, lh - 1)
    tv = (ln * f * 4) % lw
    t = cv2.remap(LS4, tv.reshape(yy.shape).astype(np.float32), tu.reshape(yy.shape).astype(np.float32), cv2.INTER_LINEAR).ravel()[:, None]
    k = k * (1 - t) + np.clip(k * 1.28 + 0.04, 0, 1) * t
    # ribbels, glans, randen
    dws = dw * f
    rib = 1 + 0.045 * np.sin(dws * 2 * np.pi / 2.2) + 0.015 * np.sin(ln * f * 2 * np.pi / 1.7)
    glans = 0.018 * (1 - np.abs(dw) / (hw + 1e-6))
    k = np.clip(k * rib[:, None] + glans[:, None], 0, 1)
    kant = np.exp(-((hw - np.abs(dw)) * f / 1.1) ** 2)
    k = k * (1 - 0.12 * kant[:, None])
    # stiksels waar de band op het vak gestikt is
    st = stof[idx]
    ad = np.abs(dw) * f
    hwf = hw * f
    steek = ((ad > hwf - 5.2) & (ad < hwf - 3.4) & (((ln * f) % 10) < 6)).astype(np.float32) * (st > 0.5)
    garen = np.array(kleur, np.float32) * 1.12 + 0.06
    k = k * (1 - 0.75 * steek[:, None]) + np.clip(garen, 0, 1)[None] * 0.75 * steek[:, None]
    rgb_s = k.reshape(yy.shape + (3,)).astype(np.float32)
    a_s = a.reshape(yy.shape).astype(np.float32)
    # terug naar fotoresolutie (premultiplied middelen)
    B, H = x1 - x0, y1 - y0
    pa = cv2.resize(a_s, (B, H), interpolation=cv2.INTER_AREA)
    prgb = cv2.resize(rgb_s * a_s[..., None], (B, H), interpolation=cv2.INTER_AREA) / (pa[..., None] + 1e-6)
    plang = cv2.resize(np.where(a_s > 0.01, Ls[idx].reshape(yy.shape), -1).astype(np.float32), (B, H), interpolation=cv2.INTER_NEAREST)
    rgb = np.zeros((h, wd, 3), np.float32); al = np.zeros((h, wd), np.float32); lang = np.full((h, wd), -1, np.float32)
    rgb[y0:y1, x0:x1] = prgb; al[y0:y1, x0:x1] = pa; lang[y0:y1, x0:x1] = plang
    return rgb, al, lang, L


_LOGO = None


def _logo():
    global _LOGO
    if _LOGO is None:
        _LOGO = SC.logo_strook(SC.BAND * 4, periode=170 * 4, hoogte=13 * 4)
    return _LOGO


# ---------------------------------------------------------------- lus
def studio_lus_huid():
    """Lus zoals in de studio (scene.band_pad): van de strengen bij de korte zijde recht naar een ronde top
    3,35 tegelhoogtes voorbij het vak. Huidcoördinaten, van streng -1 naar streng +1."""
    R = 0.95 * TW
    C = np.array([XM, Y0 - 3.35 * TH + R])
    p1, p2 = np.array([XM - STR_KORT, Y0]), np.array([XM + STR_KORT, Y0])

    def raak(P, teken):
        d = P - C; L = np.linalg.norm(d)
        return math.atan2(d[1], d[0]) + teken * math.acos(R / L)
    beste = None
    for t1 in (-1, 1):
        for t2 in (-1, 1):
            a1, a2 = raak(p1, t1), raak(p2, t2)
            for k in (-1, 0, 1):
                hk = np.linspace(a1, a2 + 2 * math.pi * k, 200)
                boog = C + R * np.stack([np.cos(hk), np.sin(hk)], 1)
                if boog[:, 1].min() > C[1] - R * 0.98:
                    continue
                lengte = abs(hk[-1] - hk[0])
                if beste is None or lengte < beste[0]:
                    beste = (lengte, boog)
    boog = beste[1]
    return np.concatenate([p1 + (boog[0] - p1) * np.linspace(0, 1, 80)[:, None], boog[1:-1],
                           boog[-1] + (p2 - boog[-1]) * np.linspace(0, 1, 80)[:, None]])


def lus_lengte():
    P = studio_lus_huid()
    return float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum())


def _catmull(pts, n=40):
    P = [pts[0]] + list(pts) + [pts[-1]]
    uit = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.asarray, P[i - 1:i + 3])
        for t in np.linspace(0, 1, n, endpoint=False):
            uit.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    uit.append(np.asarray(pts[-1]))
    return np.array(uit, np.float64)


def _herbemonster(P, n):
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    Ls = np.linspace(0, L[-1], n)
    return np.stack([np.interp(Ls, L, P[:, 0]), np.interp(Ls, L, P[:, 1])], 1)


def start_lus(E1, E2, d1, d2, L, w, g):
    """Beginvorm: bovenste streng buitenom naar beneden, U-bocht, binnenom terug naar de onderste."""
    boven_eerst = np.dot(E1, g) <= np.dot(E2, g)
    Eu, El, du, dl = (E1, E2, d1, d2) if boven_eerst else (E2, E1, d2, d1)
    o = (du + dl) / 2; o = o - g * np.dot(o, g); o /= np.linalg.norm(o) + 1e-9
    Rb = 1.25 * w
    binnen = 0.8 * w

    def vorm(D):
        ctrl = [Eu, Eu + (o + g) / 1.414 * 0.8 * w,
                El + o * (binnen + 2 * Rb) + g * (np.dot(Eu - El, g) + 1.6 * w),
                El + o * (binnen + 2 * Rb) + g * (D - Rb),
                El + o * (binnen + Rb) + g * D,
                El + o * binnen + g * (D - Rb),
                El + o * 0.5 * w + g * 0.9 * w, El]
        return _catmull(ctrl, 40)
    lo, hi = 0.0, L
    for _ in range(40):
        D = (lo + hi) / 2
        P = vorm(D)
        lengte = np.linalg.norm(np.diff(P, axis=0), axis=1).sum()
        lo, hi = (D, hi) if lengte < L else (lo, D)
    P = vorm((lo + hi) / 2)
    return P if boven_eerst else P[::-1]


def simuleer_lus(E1, E2, d1, d2, L, w, botsing, g=(0.0, 1.0), stappen=500, min_r=None, n=120, stijf=0.12, iters=25):
    """Hangende lus tussen uittreepunten E1, E2 (beeld), beginrichtingen d1, d2 (naar buiten), vaste lengte L.
    botsing(P) -> (afstand tot board, + = buiten; richting naar buiten). Position-based: lengte, buigstijfheid,
    zwaartekracht, geen zelfdoorsnijding, niet door het board."""
    E1, E2, d1, d2 = map(lambda v: np.asarray(v, np.float64), (E1, E2, d1, d2))
    g = np.asarray(g, np.float64)
    P = _herbemonster(start_lus(E1, E2, d1, d2, L, w, g), n)
    l = L / (n - 1)
    min_r = min_r or 2.0 * w
    vorig = P.copy()
    # alleen het uittreepunt ligt vast: de band gaat om de ronde rail en kan daar alle kanten op
    klem = 0
    klem1 = E1[None]
    klem2 = E2[None]
    rest2 = 2 * l * math.cos(min(l / min_r, 1.0) / 2)
    # bij de rail vouwt de band om (scherpe knik mag), verderop is hij stijf
    booglen = np.arange(1, n - 1) * l
    buig_w = np.clip((np.minimum(booglen, L - booglen) - 0.6 * w) / (1.0 * w), 0, 1)
    gap = int(math.ceil(2.5 * w / l)) + 2
    ii, jj = np.triu_indices(n, gap)
    for it in range(stappen):
        v = np.clip((P - vorig) * 0.9, -0.3 * l, 0.3 * l)
        vorig = P.copy()
        P = P + v + g * 0.02 * l
        for _ in range(iters):
            dlt = P[1:] - P[:-1]
            dist = np.linalg.norm(dlt, axis=1) + 1e-9
            corr = ((dist - l) / dist)[:, None] * dlt * 0.5
            P[:-1] += corr; P[1:] -= corr
            P[0] = E1; P[-1] = E2
            dlt = P[2:] - P[:-2]
            dist = np.linalg.norm(dlt, axis=1) + 1e-9
            doel = np.maximum(dist, rest2) * (1 - stijf) + 2 * l * stijf
            corr = ((dist - doel) / dist)[:, None] * dlt * 0.35 * buig_w[:, None]
            P[:-2] += corr; P[2:] -= corr
            D = P[jj] - P[ii]
            dd = np.linalg.norm(D, axis=1) + 1e-9
            te = dd < w * 1.05
            if te.any():
                c = np.clip((w * 1.05 - dd[te]) / dd[te], 0, 1)[:, None] * D[te] * 0.25
                np.add.at(P, ii[te], -c)
                np.add.at(P, jj[te], c)
            afst, grad = botsing(P)
            binnen = afst < w * 0.5
            P[binnen] += grad[binnen] * np.clip(w * 0.5 - afst[binnen], 0, 2 * l)[:, None]
            P[:klem + 1] = klem1
            P[-klem - 1:] = klem2[::-1]
    if not np.isfinite(P).all():
        raise RuntimeError('lus-simulatie niet stabiel')
    return P


# ---------------------------------------------------------------- belichting
def belichting(foto, B, span=0.85):
    """Relatieve belichting van het board: S(t, s). Gebruikt max(R,G,B) (verzadigde kleuren tellen even licht),
    medianen dwars en langs (robuust tegen logo's), begrensd."""
    V = foto.max(2)
    ts = np.linspace(B.tb - span * B.W, B.tb + span * B.W, 120)
    ss = np.linspace(-0.97, 0.97, 60)
    T, S = np.meshgrid(ts, ss, indexing='ij')
    P = B.naar_beeld(T, S)
    vals = cv2.remap(V, P[..., 0].astype(np.float32), P[..., 1].astype(np.float32), cv2.INTER_LINEAR)
    zm = cv2.remap(B.zicht, P[..., 0].astype(np.float32), P[..., 1].astype(np.float32), cv2.INTER_LINEAR) > 0.5
    vals = np.where(zm, vals, np.nan)
    A = np.nanmedian(vals, 0)                  # per s
    Bt = np.nanmedian(vals, 1)                 # per t
    ok = ~np.isnan(Bt)
    p = np.polyfit(ts[ok], Bt[ok], 1)
    ref = np.nanmedian(vals)
    A = cv2.GaussianBlur(A.reshape(1, -1).astype(np.float32), (0, 0), 1.5).ravel()
    return dict(ts=ts, ss=ss, A=A / np.median(A), p=p, ref=float(ref), tb=B.tb)


def licht_op(L, t, s):
    A = np.interp(s, L['ss'], L['A'])
    lin = np.polyval(L['p'], t) / np.polyval(L['p'], L['tb'])
    return np.clip(A * np.clip(lin, 0.8, 1.2), 0.45, 1.2)


# ---------------------------------------------------------------- samenstellen
def maak(foto, naam, handle, lus=-1, stringer=0.0, kort=1.0, belicht=1.0, tint=(1.0, 1.0, 1.0), verzadiging=0.9,
         lift=0.0, zacht=0.5, korrel=None, schaduw=(6, 8, 0.35, 10), lus_schaduw=None, lus_licht=1.0, ondergrens=None,
         occluder=None, plat=False, debug=False, lus_lengte_factor=1.0, albedo=None):
    """foto: float32 RGB 0..1. Geeft het samengestelde beeld.
    schaduw: (dx, dy, sterkte, zachtheid) van de band op het vak (fotopixels per 300 px boardbreedte).
    lus_schaduw: (dx, dy, sterkte, zachtheid) van de lus op de achtergrond, of None."""
    h, w = foto.shape[:2]
    B = Board(naam, lus=lus, stringer=stringer, kort=kort)
    schaal = B.W / 300.0
    # ---- huid en warp
    rgb, pm = huid(handle)
    yy, xx = np.mgrid[0:h, 0:w]
    # alleen rekenen in de buurt van het vak
    hk = hoeken()
    rand_pts, _ = B.huid_naar_beeld(np.r_[hk[:, 0], XM], np.r_[hk[:, 1], Y0 + HS / 2])
    x0 = int(max(rand_pts[:, 0].min() - B.W, 0)); x1 = int(min(rand_pts[:, 0].max() + B.W, w))
    y0 = int(max(rand_pts[:, 1].min() - B.W, 0)); y1 = int(min(rand_pts[:, 1].max() + B.W, h))
    P = np.stack([xx[y0:y1, x0:x1].ravel(), yy[y0:y1, x0:x1].ravel()], 1).astype(np.float64)
    X, Y, T, S = B.beeld_naar_huid(P)
    blur = max(0.42 * B.k, 0.01)
    rgb_b = cv2.GaussianBlur(rgb, (0, 0), blur); pm_b = cv2.GaussianBlur(pm, (0, 0), blur)
    sh = (y1 - y0, x1 - x0)
    Xr, Yr = X.reshape(sh).astype(np.float32), Y.reshape(sh).astype(np.float32)
    vak = cv2.remap(rgb_b, Xr, Yr, cv2.INTER_LINEAR)
    va = cv2.remap(pm_b, Xr, Yr, cv2.INTER_LINEAR)
    Tm, Sm = T.reshape(sh), S.reshape(sh)
    # randen van het board: stof volgt het silhouet + dikte van de stof (max ~1,5 px)
    afst = (np.abs(Sm) - 1) * B.half(Tm)        # px buiten het silhouet (+)
    dik = float(np.clip(0.004 * B.W, 0.8, 1.6))
    a_rand = np.clip(dik - afst + 0.5, 0, 1)
    zicht = B.zicht[y0:y1, x0:x1]
    # occluders (in de foto voor het board) zijn niet in zicht; omtrek zelf komt uit de gladde fit
    occ = (cv2.erode((zicht < 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & (np.abs(Sm) < 0.995)
    va = va * a_rand * (~occ)
    # ronding naar de rail: stof draait weg van het licht
    sa = np.abs(Sm)
    rond = np.where(sa > 0.82, 0.68 + 0.32 * np.cos(np.clip((sa - 0.82) / 0.18, 0, 1) * math.pi / 2) ** 0.8, 1.0)
    L = belichting(foto, B)
    lichtmap = licht_op(L, Tm, np.clip(Sm, -0.97, 0.97)) * rond
    # ---- band
    w_band = SC.BAND / B.k
    info = band_pad(B, foto.shape[:2], w_band, plat=plat, lengte_factor=lus_lengte_factor, ondergrens=ondergrens)
    kleur = SC.hexkleur(SC.TASSEN[handle])
    # ---- licht voor alles samen
    # belichting t.o.v. de studio: uit de helderheid van het board (als we weten hoe licht het board zelf is), anders handmatig
    E = belicht * (L['ref'] / albedo if albedo else 1.0)
    tint = np.array(tint, np.float32)

    def kleurcorrectie(c, licht):
        c = c * (E * licht)[..., None] * tint
        g = c @ np.array([.299, .587, .114], np.float32)
        c = g[..., None] + (c - g[..., None]) * verzadiging
        return c * (1 - lift) + lift * np.array([1.0, 0.98, 0.95], np.float32) * 0.5

    uit = foto.copy()
    # schaduw van de vakrand (dikte van de stof) op het board
    sub = uit[y0:y1, x0:x1]
    # dikte van de stof met zoom (~3 mm): smalle schaduw naast de vakrand, in de lichtrichting
    ld = np.array(schaduw[:2], np.float64); ld /= np.linalg.norm(ld) + 1e-9
    off = max(0.006 * B.W, 1.0)
    M = np.float32([[1, 0, ld[0] * off], [0, 1, ld[1] * off]])
    sch = cv2.warpAffine(va, M, (va.shape[1], va.shape[0]))
    sch = cv2.GaussianBlur(sch, (0, 0), 0.5 + 0.004 * B.W)
    sub = sub * (1 - 0.45 * np.clip(sch - va, 0, 1) * (zicht > 0.5))[..., None]
    # contactschaduw rondom (stof ligt op het board)
    con = cv2.GaussianBlur(va, (0, 0), 0.8 + 0.01 * B.W)
    sub = sub * (1 - 0.18 * np.clip(con - va, 0, 1) * (zicht > 0.5))[..., None]
    vak_k = kleurcorrectie(vak, lichtmap)
    sub = sub * (1 - va[..., None]) + vak_k * va[..., None]
    uit[y0:y1, x0:x1] = sub
    # board-alpha over het hele beeld (silhouet + stofdikte), en zichtbaarheid (occluders)
    Pall = np.stack([xx.ravel(), yy.ravel()], 1).astype(np.float64)
    Ta, Sa, _ = B.naar_ts(Pall)
    Ta, Sa = Ta.reshape(h, w), Sa.reshape(h, w)
    binnen_lengte = (Ta > B.tt.min()) & (Ta < B.tt.max())
    afst_a = (np.abs(Sa) - 1) * B.half(Ta)
    bord_a = np.clip(dik - afst_a + 0.5, 0, 1) * binnen_lengte          # met stofdikte (voor alles op het board)
    bord_kaal = np.clip(0.5 - afst_a, 0, 1) * binnen_lengte             # kaal silhouet
    occ_a = ((B.zicht < 0.5) & (np.abs(Sa) < 0.99) & binnen_lengte).astype(np.float32)
    if occluder is not None:
        occ_a = np.maximum(occ_a, occluder)
    # strengen over het vak: binnen het silhouet, om beide rails verdwijnend
    kleur_l = np.ones((h, w), np.float32)
    s_rgb = np.zeros((h, w, 3), np.float32); s_a = np.zeros((h, w), np.float32)
    for st_ in info['strengen']:
        r_, a_, _, _ = band((h, w), st_['P'], w_band, kleur, op_stof=np.ones(len(st_['P'])))
        a_ = a_ * bord_a * (1 - occ_a)
        s_rgb = s_rgb * (1 - a_[..., None]) + r_ * a_[..., None]
        s_a = s_a + a_ * (1 - s_a)
    s_rgb = s_rgb / np.maximum(s_a, 1e-6)[..., None]
    l_board = licht_op(L, Ta, np.clip(Sa, -0.97, 0.97)) * np.where(np.abs(Sa) > 0.86, 0.8 + 0.2 * np.clip((1 - np.abs(Sa)) / 0.14, 0, 1), 1.0)
    # lus: komt van achter de rail tevoorschijn
    l_rgb, l_a, l_lang, l_L = band((h, w), info['lus'], w_band, kleur, op_stof=np.zeros(len(info['lus'])), breed=info['lus_breed'])
    l_a = l_a * (1 - bord_kaal) * (1 - (occluder if occluder is not None else 0))
    l_licht = np.interp(np.maximum(l_lang, 0), l_L, info['lus_licht']).astype(np.float32) * lus_licht
    # schaduw van de strengen op vak/board
    d = (int(round(schaduw[0] * schaal)), int(round(schaduw[1] * schaal)))
    bs = cv2.GaussianBlur(np.roll(np.roll(s_a, d[1], 0), d[0], 1), (0, 0), schaduw[3] * schaal * 0.5 + 0.5)
    uit = uit * (1 - schaduw[2] * np.clip(bs - s_a, 0, 1) * bord_kaal * (1 - occ_a))[..., None]
    # schaduw van de lus op de achtergrond (niet op het board dat ervoor staat)
    if lus_schaduw is not None:
        dx, dy, st, zz = lus_schaduw
        ls = cv2.GaussianBlur(np.roll(np.roll(l_a, int(dy * schaal), 0), int(dx * schaal), 1), (0, 0), zz * schaal + 0.5)
        uit = uit * (1 - st * np.clip(ls - l_a, 0, 1) * (1 - bord_kaal) * (1 - occ_a))[..., None]
    uit = uit * (1 - l_a[..., None]) + kleurcorrectie(l_rgb, l_licht) * l_a[..., None]
    uit = uit * (1 - s_a[..., None]) + kleurcorrectie(s_rgb, l_board) * s_a[..., None]
    ba = np.maximum(s_a, l_a)
    pad = np.concatenate([info['strengen'][0]['P'], info['lus'], info['strengen'][1]['P']])
    # ---- camera: scherpte en korrel van de foto op de nieuwe delen
    nieuw = np.zeros((h, w), np.float32)
    nieuw[y0:y1, x0:x1] = va
    nieuw = np.maximum(nieuw, ba)
    if zacht > 0:
        zachter = cv2.GaussianBlur(uit, (0, 0), zacht)
        uit = uit * (1 - nieuw[..., None]) + zachter * nieuw[..., None]
    if korrel is None:
        hp = foto - cv2.GaussianBlur(foto, (0, 0), 1.0)
        sel = B.zicht > 0.5
        korrel = float(np.median(np.abs(hp[sel])) * 1.4826)
    ruis = rng.normal(0, 1, (h, w, 1)).astype(np.float32) * korrel + rng.normal(0, 1, (h, w, 3)).astype(np.float32) * korrel * 0.4
    ruis = cv2.GaussianBlur(ruis, (0, 0), 0.5) * 1.6
    uit = uit + ruis * nieuw[..., None]
    if debug:
        return np.clip(uit, 0, 1), dict(B=B, pad=pad, info=info, va=va, box=(x0, y0, x1, y1), ba=ba)
    return np.clip(uit, 0, 1)


def band_pad(B, shape, w, plat=False, lengte_factor=1.0, ondergrens=None):
    """Strengen (recht over het vak, voorbij beide rails doorgetrokken; worden op het silhouet afgesneden)
    en de lus (begint net achter de rail, hangt of ligt daarbuiten). Beeldcoördinaten."""
    h, wd = shape
    strengen = []
    for kant in (-1, 1):
        xl, xk = XM + kant * STR_LANG, XM + kant * STR_KORT
        Ys = np.linspace(Y0 + HS, Y0, 400)
        Xs = xl + (xk - xl) * (Ys - (Y0 + HS)) / (Y0 - (Y0 + HS))
        Pb, _ = B.huid_naar_beeld(Xs, Ys)
        _, sb, _ = B.naar_ts(Pb)
        vlak = np.abs(sb) <= 0.85
        Pv = Pb[vlak]
        # recht doortrekken (een strak gespannen band over het vlakke dek; de ronding van de rail is maar een paar px)
        d = Pv[-1] - Pv[int(len(Pv) * 0.7)]; d /= np.linalg.norm(d)        # naar de lusrail
        verder = 0.25 * B.W + 2 * w
        Pl = np.concatenate([Pv[0] - d[None] * np.linspace(verder, 0, 60)[:, None], Pv[1:-1],
                             Pv[-1] + d[None] * np.linspace(0, verder, 60)[:, None]])
        # uittreepunt: waar de rechte streng het silhouet aan de luskant kruist
        _, sl, _ = B.naar_ts(Pl)
        na = np.arange(len(Pl)) >= len(Pv)
        buiten = np.where(na & (np.abs(sl) >= 1.0))[0]
        Ep = Pl[buiten[0]] if len(buiten) else Pl[-1]
        strengen.append(dict(P=Pl, E=Ep, d=d))
    L_lus = lus_lengte() / B.k * lengte_factor
    om = np.zeros((h, wd), np.uint8)
    cv2.fillPoly(om, [np.round(B.omtrek() * 4).astype(np.int32)], 1, shift=2)
    if ondergrens is not None:
        om[int(ondergrens):] = 1                               # grond
    dt = cv2.distanceTransform(1 - om, cv2.DIST_L2, 5).astype(np.float32)
    gy, gx = np.gradient(cv2.GaussianBlur(dt, (0, 0), 2))

    def botsing(P):
        x = np.clip(P[:, 0], 0, wd - 1).astype(np.float32); y = np.clip(P[:, 1], 0, h - 1).astype(np.float32)
        d = cv2.remap(dt, x[None], y[None], cv2.INTER_LINEAR)[0]
        g = np.stack([cv2.remap(gx, x[None], y[None], cv2.INTER_LINEAR)[0], cv2.remap(gy, x[None], y[None], cv2.INTER_LINEAR)[0]], 1)
        g /= np.linalg.norm(g, axis=1)[:, None] + 1e-6
        return d, g

    s1, s2 = strengen
    if plat:
        lus = plat_lus(B, w)
    else:
        lus = simuleer_lus(s1['E'], s2['E'], s1['d'], s2['d'], L_lus, w, botsing)
    # de lus begint achter de rail (daar wordt hij door het board afgedekt)
    in1 = s1['E'] - s1['d'] * 0.8 * w; in2 = s2['E'] - s2['d'] * 0.8 * w
    lus = np.concatenate([[in1], lus, [in2]])
    Lu = np.r_[0, np.cumsum(np.linalg.norm(np.diff(lus, axis=0), axis=1))]
    rand_af = np.minimum(Lu, Lu[-1] - Lu) / (2.5 * w)
    # om de rail draait de band: vlak na de rail even smaller en donkerder, daarna plat in beeld
    draai = 1 - 0.25 * np.exp(-(rand_af - 0.45) ** 2 / 0.1) * (0 if plat else 1)
    lus_licht = 0.94 * (0.6 + 0.4 * (draai - draai.min()) / (1 - draai.min() + 1e-6)) if not plat else np.full(len(lus), 0.95)
    return dict(strengen=strengen, lus=lus, lus_breed=draai, lus_licht=lus_licht)


def plat_lus(B, w):
    """Lus die plat naast een liggend board ligt: de studiovorm, in het vlak van het board doorgetrokken."""
    hp = studio_lus_huid()
    t = B.tb + (hp[:, 0] - XM) / B.kx
    sig = (2 * (hp[:, 1] - Y0) / HS - 1) * SMAX * (-B.lus)
    s_in = B.sigma_naar_s(t, sig)[0]
    x = np.abs(sig) * B.href / B.half(t)
    s = np.where(x <= SMAX, s_in, np.sign(sig) * (1 + (x - SMAX)))
    return B.naar_beeld(t, s)
