"""Levensechte productfoto's van de strandhanddoek in tegelprint (strandhanddoek-tegel-1, -2, -3).

Geen AI: echte stockfoto's van effen handdoeken (Unsplash, zie docs/producten/stock/bronnen.json) met ons eigen ontwerp erop.

Ontwerp (90 x 170 cm, geweven jacquard in twee kleuren):
- de motieven komen uit de echte tegelstof van de draagtas (docs/producten/fabriek/tegel-0*.png). Elke tegel wordt
  4-voudig symmetrisch gemaakt (dat zijn echte tegels ook) en teruggebracht tot twee garens: navy op crème;
- 6 tegels van 14 cm over de breedte en 10 over de lengte, een dun navy kader rond het tegelveld;
- aan beide korte kanten een terracotta band met twee crème biesjes, daarna de franjes;
- een klein geweven navy label met TIDE TODE in de zijzoom.

Werkwijze per foto: de handdoek in de foto krijgt een coördinatenstelsel in centimeters (perspectief per vlak of laag),
het ontwerp wordt via die coördinaten afgebeeld, verschuift mee met de plooien (verplaatsing uit de helderheid),
wordt vermenigvuldigd met de schaduwen van de foto en de stofstructuur komt terug als hoogdoorlaatdetail.

Opnieuw maken: python3 tools/producten/echt_handdoek.py  (het label wordt met Playwright gerenderd)
"""
import pathlib, subprocess, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import mockup as MK  # noqa: E402
import brandbook as BB  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock'
FABRIEK = ROOT / 'docs' / 'producten' / 'fabriek'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
UIT = HIER / 'uit_handdoek'
UIT.mkdir(exist_ok=True)
A = ROOT / 'theme' / 'assets'


def hexkl(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


NAVY, CREME, TERRA = hexkl('#22324F'), hexkl('#F3ECDD'), hexkl('#C0603E')
# garenkleuren: iets gedempt, zoals geverfd katoen er in daglicht uitziet
GAREN_NAVY = hexkl('#26365A')
GAREN_CREME = hexkl('#EFE6D4')
GAREN_TERRA = hexkl('#BD5E3D')
GAREN_BLAUW = hexkl('#B3C8E3')      # baby blue, het derde garen voor de middentonen

BREED, LANG = 90.0, 170.0          # cm
TEGEL = 16.8                        # cm per tegel: 5 over de breedte, 8 over de lengte
VELD = (3.0, 17.8, 87.0, 152.2)     # tegelveld u0, v0, u1, v1 in cm
KADER_V = VELD[1] - 1.3             # dun navy kader rond het veld
MOTIEVEN = [1, 5, 2, 0, 3]          # tegels uit de stof die als jacquard goed lezen
SPIEGEL = {2: False}                # de molen (tegel 2) is alleen draaisymmetrisch


# ---------- ontwerp ----------
def motief(i, n=480):
    """Tegel uit de echte stof als zachte toonkaart. Geeft (X - drempel navy, X - drempel blauw) in eenheden van de spreiding."""
    t = np.asarray(Image.open(FABRIEK / f'tegel-0{i}.png').convert('RGB')).astype(np.float32) / 255
    L = MK.helderheid(t)
    L = cv2.GaussianBlur(cv2.resize(L, (n, n), interpolation=cv2.INTER_CUBIC), (0, 0), n / 130)
    acc = [np.rot90(L, k) for k in range(4)]
    if SPIEGEL.get(i, True):
        acc += [np.fliplr(a) for a in acc]
    X = cv2.GaussianBlur(np.mean(acc, 0), (0, 0), n / 160)
    X = (X - X.mean()) / (X.std() + 1e-6)
    uit = []
    for pct in (30, 58):
        Y = X - np.percentile(X, pct)
        # spikkels weg: losse vlekjes kleiner dan ca. 3 mm worden opgevuld met de omringende kleur
        for teken in (1, -1):
            m = (teken * Y > 0).astype(np.uint8)
            n_, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
            klein = np.isin(lab, 1 + np.where(st[1:, cv2.CC_STAT_AREA] < (n / 45) ** 2)[0])
            Y = np.where(klein, -teken * np.maximum(np.abs(Y), 0.3), Y)
        uit.append(cv2.GaussianBlur(Y, (0, 0), n / 400))
    return np.dstack(uit)


_MOT = {}


def ontwerp(ppc):
    """Het hele vlak van de handdoek (90 x 170 cm) bij ppc pixels per cm. Geeft RGB (float32)."""
    W, H = int(round(BREED * ppc)), int(round(LANG * ppc))
    u = (np.arange(W, dtype=np.float32) + 0.5) / ppc
    v = (np.arange(H, dtype=np.float32) + 0.5) / ppc
    U, V = np.meshgrid(u, v)
    img = np.empty((H, W, 3), np.float32)
    img[:] = GAREN_CREME
    aa = 0.6 / ppc  # anti-aliasing in cm

    def strook(a, b, x):
        return np.clip((x - a) / aa + 0.5, 0, 1) * np.clip((b - x) / aa + 0.5, 0, 1)

    def verf(m, kl):
        img[:] = img * (1 - m[..., None]) + kl * m[..., None]

    # tegelveld
    u0, v0, u1, v1 = VELD
    tp = int(round(TEGEL * ppc))
    for i in MOTIEVEN:
        if (i, tp) not in _MOT:
            _MOT[(i, tp)] = cv2.resize(motief(i), (tp, tp), interpolation=cv2.INTER_CUBIC)
    nk, nr = int(round((u1 - u0) / TEGEL)), int(round((v1 - v0) / TEGEL))
    veld = np.ones((nr * tp, nk * tp, 2), np.float32)
    for r in range(nr):
        for c in range(nk):
            i = MOTIEVEN[(r * 2 + c * 1 + (r // 2)) % len(MOTIEVEN)]
            veld[r * tp:(r + 1) * tp, c * tp:(c + 1) * tp] = _MOT[(i, tp)]
    # drie garens: navy, baby blue en crème, met een zachte rand (scherpte past bij de schaal)
    k = 3.0 * max(1.0, ppc / 12)
    aN = np.clip(veld[..., 0] * k + 0.5, 0, 1)[..., None]
    aB = np.clip(veld[..., 1] * k + 0.5, 0, 1)[..., None]
    x0, y0 = int(round(u0 * ppc)), int(round(v0 * ppc))
    sub = img[y0:y0 + veld.shape[0], x0:x0 + veld.shape[1]]
    sub[:] = GAREN_NAVY * (1 - aN) + aN * (GAREN_BLAUW * (1 - aB) + GAREN_CREME * aB)
    # voegen tussen de tegels: dun navy
    voeg = np.zeros((H, W), np.float32)
    for k in range(nk + 1):
        voeg = np.maximum(voeg, strook(u0 + k * TEGEL - 0.12, u0 + k * TEGEL + 0.12, U) * strook(v0 - 0.12, v1 + 0.12, V))
    for k in range(nr + 1):
        voeg = np.maximum(voeg, strook(v0 + k * TEGEL - 0.12, v0 + k * TEGEL + 0.12, V) * strook(u0 - 0.12, u1 + 0.12, U))
    verf(voeg, GAREN_NAVY)
    # kader rond het veld
    kv = KADER_V
    kader = (strook(1.7, 2.2, U) + strook(BREED - 2.2, BREED - 1.7, U)) * strook(kv, LANG - kv, V) \
        + (strook(kv, kv + 0.5, V) + strook(LANG - kv - 0.5, LANG - kv, V)) * strook(1.7, BREED - 1.7, U)
    verf(np.clip(kader, 0, 1), GAREN_NAVY)
    # terracotta banden aan de korte kanten, met twee crème biesjes
    for a_, b_ in [(2.0, 9.0), (LANG - 9.0, LANG - 2.0)]:
        verf(strook(a_, b_, V), GAREN_TERRA)
        verf(strook(a_ + 1.2, a_ + 1.55, V) + strook(b_ - 1.55, b_ - 1.2, V), GAREN_CREME)
    return img


# ---------- label ----------
FONTS = ''.join(f"@font-face{{font-family:'{f}';src:url('file://{A / b}') format('woff2');font-weight:{w}}}"
                for f, b, w in [('Courier Prime', 'courierprime-bold.woff2', 700), ('Courier Prime', 'courierprime-regular.woff2', 400),
                                ('Tide Tode Display', 'tide-tode-display.woff2', 400)])


def pagina(naam, b, h, inhoud):
    (UIT / f'{naam}.html').write_text(f'''<!doctype html><meta charset="utf-8"><style>{FONTS}
* {{ margin: 0; box-sizing: border-box; }} html, body {{ width: {b}px; height: {h}px; overflow: hidden; background: transparent; }}
</style><body>{inhoud}</body>''')


def maak_label():
    """Geweven label 5 x 2,4 cm: navy met crème letters (600 x 288 px)."""
    pagina('label', 600, 288, f'''
<div style="position:absolute;inset:0;background:#22324F;display:flex;align-items:center;justify-content:center;gap:26px;color:#F3ECDD">
  {BB.icoon('#F3ECDD', '', 'height:150px;width:auto')}
  <div style="text-align:left">
    <div style="font:400 92px/0.9 'Tide Tode Display';letter-spacing:.04em">TIDE<br>TODE</div>
  </div>
</div>''')
    subprocess.run(['node', str(UIT / 'render.mjs')], check=True)


def label_geweven(ppc_label=None):
    """Het label als geweven stof: lettergaren iets verhoogd, fijne ribbel van de inslag, rafelloze snijrand."""
    a = np.asarray(Image.open(UIT / 'label.png').convert('RGBA')).astype(np.float32) / 255
    rgb = a[..., :3].copy()
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rib = 1 + 0.07 * np.sin(yy * 2 * np.pi / 3.2) + 0.03 * np.sin(xx * 2 * np.pi / 2.4)
    L = MK.helderheid(rgb)
    hoog = cv2.GaussianBlur(L, (0, 0), 1.2)
    reliëf = 1 + 0.5 * (np.roll(hoog, 2, 0) - np.roll(hoog, -2, 0))
    rgb = np.clip(cv2.GaussianBlur(rgb, (0, 0), 0.9) * (rib * reliëf)[..., None], 0, 1)
    rand = np.ones((h, w), np.float32)
    for k in range(6):
        f = 1 - 0.07 * (6 - k)
        rand[k, :] *= f; rand[-1 - k, :] *= f; rand[:, k] *= f; rand[:, -1 - k] *= f
    return np.dstack([rgb * rand[..., None], a[..., 3]])


LABEL_POS = (81.0, 4.3, 5.0, 2.4)    # u, v, breedte, hoogte in cm: plat op de terracotta band gestikt, vlak bij de hoek


def ontwerp_met_label(ppc):
    """Ontwerp plus het geweven label (plat opgestikt, met stiksel en een heel klein beetje dikte)."""
    img = ontwerp(ppc)
    lab = label_geweven()
    u, v, b, h = LABEL_POS
    bw, bh = int(round(b * ppc)), int(round(h * ppc))
    klein = cv2.resize(lab, (bw, bh), interpolation=cv2.INTER_AREA)
    x0, y0 = int(round(u * ppc)), int(round(v * ppc))
    # schaduwtje onder het label (dikte)
    m = np.zeros(img.shape[:2], np.float32)
    m[y0:y0 + bh, x0:x0 + bw] = 1
    sch = cv2.GaussianBlur(np.roll(np.roll(m, max(1, int(ppc * 0.06)), 0), max(1, int(ppc * 0.04)), 1), (0, 0), max(0.8, ppc * 0.06))
    img = img * (1 - 0.35 * (sch * (1 - m))[..., None])
    rgb = klein[..., :3].copy()
    # stiksel: korte navy steekjes rondom, net binnen de rand
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    r = 0.18 * ppc
    rand = ((np.abs(xx - r) < 0.04 * ppc + 0.5) | (np.abs(xx - (bw - 1 - r)) < 0.04 * ppc + 0.5)) & (yy > r) & (yy < bh - 1 - r)
    rand |= ((np.abs(yy - r) < 0.04 * ppc + 0.5) | (np.abs(yy - (bh - 1 - r)) < 0.04 * ppc + 0.5)) & (xx > r) & (xx < bw - 1 - r)
    steek = (np.sin((xx + yy) * 2 * np.pi / (0.35 * ppc)) > -0.2)
    rgb[rand & steek] = rgb[rand & steek] * 0.72
    img[y0:y0 + bh, x0:x0 + bw] = rgb
    lm = np.zeros(img.shape[:2], np.float32)
    lm[y0:y0 + bh, x0:x0 + bw] = 1
    return img, lm


# ---------- afbeelden op een foto ----------
def strepen_weg(img, dikte=31):
    """Lichte geweven streepjes van de stockhanddoek weghalen (dunne lichte lijnen) zonder de plooien te verliezen."""
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (1, dikte))
    uit = np.empty_like(img)
    for c in range(3):
        o = cv2.morphologyEx(img[..., c], cv2.MORPH_OPEN, k)
        o = cv2.GaussianBlur(o, (0, 0), 2.5)
        uit[..., c] = np.minimum(img[..., c], o + 0.012)
    return uit


def weefsel(U, V, sterkte, garen=0.11):
    """Geweven structuur in stofcoördinaten: elke schering- en inslagdraad (ca. 1 mm) is net iets lichter of donkerder,
    met wat ongelijkmatigheid langs de draad (katoen is nooit egaal)."""
    rng = np.random.default_rng(7)
    sch = rng.normal(0, 1, 4096).astype(np.float32)
    ins = rng.normal(0, 1, 4096).astype(np.float32)
    iu = np.mod(np.floor(U / garen).astype(np.int64), 4096)
    iv = np.mod(np.floor(V / garen).astype(np.int64), 4096)
    slub = cv2.resize(rng.normal(0, 1, (256, 256)).astype(np.float32), (1024, 1024), interpolation=cv2.INTER_CUBIC)
    su = np.mod((U * 6).astype(np.int64), 1024); sv = np.mod((V * 1.5).astype(np.int64), 1024)
    langs = 0.6 + 0.4 * slub[np.mod((V * 0.7).astype(np.int64), 1024), np.mod(iu, 1024)]
    t = (0.5 * sch[iu] + 0.35 * ins[iv]) * langs + 0.6 * slub[sv, su]
    return 1 + sterkte * np.clip(t, -2.5, 2.5)


def breng_aan(foto, masker, U, V, ppc, ontw, schoon=None, verplaatsing=0.35, detail=1.0, ref=None, gamma=1.0,
              detail_sigma=1.3, schaduw_sigma=1.6, wrap=False, waas=0.0, weef=0.0, rust=None, mono=False):
    """Ontwerp (bij ppc px/cm) via de coördinaatkaarten U, V (cm) op de foto zetten.

    schoon: de foto zonder de streepjes van de stockhanddoek (voor de schaduw); detail: sterkte van de stofstructuur."""
    schoon = foto if schoon is None else schoon
    L = MK.helderheid(schoon)
    Lz = cv2.GaussianBlur(L, (0, 0), 5)
    gx = cv2.Sobel(Lz, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(Lz, cv2.CV_32F, 0, 1, ksize=5)
    nrm = max(np.percentile(np.abs(gx[masker > 0.5]), 99), np.percentile(np.abs(gy[masker > 0.5]), 99), 1e-6)
    if rust is not None:
        # geen verplaatsing rond voorwerpen op de stof en hun slagschaduw (dat zijn geen plooien)
        w_ = 1 - np.clip(cv2.GaussianBlur(rust, (0, 0), 25) * 2.5, 0, 1)
        gx, gy = gx * w_, gy * w_
    Ud = U + np.clip(gx / nrm, -1.5, 1.5) * verplaatsing
    Vd = V + np.clip(gy / nrm, -1.5, 1.5) * verplaatsing
    mx = (Ud * ppc - 0.5).astype(np.float32)
    my = (Vd * ppc - 0.5).astype(np.float32)
    rand = cv2.BORDER_WRAP if wrap else cv2.BORDER_REPLICATE
    patroon = cv2.remap(ontw, mx, my, cv2.INTER_LINEAR, borderMode=rand)
    if waas:
        # de kleurbewerking van de foto overnemen: opgetilde zwarten in de tint van de stof
        tint = np.median(schoon[masker > 0.5].reshape(-1, 3), axis=0)
        patroon = patroon * (1 - waas) + tint[None, None] * waas
    # schaduw en licht van de foto, per kleurkanaal (warme schaduwen in de zon blijven warm)
    # (mono: alleen de helderheid, voor een gekleurde stockhanddoek zoals rood of turquoise)
    Ps = cv2.GaussianBlur(np.dstack([L] * 3) if mono else schoon, (0, 0), schaduw_sigma)
    if ref is None:
        ref = np.percentile(Ps[masker > 0.5].reshape(-1, 3), 75, axis=0)
    ratio = np.clip(Ps / ref[None, None], 0, 1.5) ** gamma
    kleur = patroon * ratio
    # stofstructuur als hoogdoorlaat (bij mono relatief aan de helderheid van de stockhanddoek)
    Lf = MK.helderheid(schoon)
    fijn = (Lf - cv2.GaussianBlur(Lf, (0, 0), detail_sigma))[..., None]
    if mono:
        fijn = fijn / max(float(ref[0]), 0.2) * 0.75
    donker = 0.55 + 0.45 * MK.helderheid(patroon)[..., None]   # op donker garen valt structuur minder op
    kleur = np.clip(kleur + fijn * detail * 1.6 * donker, 0, 1)
    if weef:
        kleur = kleur * weefsel(U, V, weef)[..., None]
    m = masker[..., None]
    return foto * (1 - m) + kleur * m


def bewaar(img, naam, max_kb=190):
    """JPG onder max_kb. Lukt dat niet met een nette kwaliteit, dan eerst de korrel van de stockfoto wat
    ontruisen (vooral kleurruis; zandkorrels kosten veel bytes) en dan pas de kwaliteit verder omlaag."""
    import io
    u8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    for h, hk in ((0, 0), (3, 10), (4, 12)):
        b = u8 if not h else cv2.cvtColor(cv2.fastNlMeansDenoisingColored(cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), None, h, hk, 5, 15), cv2.COLOR_BGR2RGB)
        im = Image.fromarray(b)
        for q in range(88, 48, -3):
            buf = io.BytesIO()
            im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
            if buf.tell() < max_kb * 1000:
                (DOEL / f'{naam}.jpg').write_bytes(buf.getvalue())
                print('foto', naam, f'q{q} ontruis{h}', buf.tell() // 1000, 'kB')
                return
    raise SystemExit('te groot: ' + naam)


def ontruis(img, h=5, hk=14):
    """Korrel van de stockfoto wat temperen (anders past de foto nooit onder 190 kB)."""
    u8 = cv2.cvtColor((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR)
    d = cv2.fastNlMeansDenoisingColored(u8, None, h, hk, 5, 15)
    return cv2.cvtColor(d, cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def grade(img, warm=0.0, contrast=1.0, licht=1.0):
    uit = img.copy()
    if warm:
        uit[..., 0] *= 1 + warm; uit[..., 2] *= 1 - warm
    uit = (uit - 0.5) * contrast + 0.5
    return np.clip(uit * licht, 0, 1)


def interp(punten, t):
    p = np.array(punten, np.float32)
    return np.interp(t, p[:, 0], p[:, 1]).astype(np.float32)


# ---------- foto 1: packshot, twee gevouwen handdoeken op een stapel ----------
def kleurmasker(img, tint):
    hsv = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    H, S = hsv[..., 0].astype(int), hsv[..., 1].astype(int)
    m = ((S > 70) & ((H < 12) | (H > 160))) if tint == 'rood' else ((S > 70) & (H > 75) & (H < 105))
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    vul = m.copy(); ff = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8); cv2.floodFill(vul, ff, (0, 0), 1)
    return (m | (1 - vul)).astype(np.float32)


def gevouwen_uv(xx, yy, B, C, D, x0, k_mid, h_mid, diepte, voor):
    """Coördinaten op een gevouwen handdoek: bovenvlak van achterrand B tot vouwrug C (diepte cm),
    dan de ronde vouw van C tot onderrand D (boog van voor cm). Langs de lengte groeit de schaal mee met het perspectief
    (hoogte van de vouw als maat). Geeft (s, t) in cm."""
    xs = np.arange(xx.shape[1], dtype=np.float32)
    h = np.maximum(D(xs) - C(xs), 20)
    k = k_mid * h / h_mid                       # px per cm langs de lengte
    s = np.cumsum(1.0 / k) - np.cumsum(1.0 / k)[int(x0)]
    S = np.broadcast_to(s[None, :], xx.shape)
    b, c, d = B(xx), C(xx), D(xx)
    t_boven = diepte * (yy - c) / np.maximum(c - b, 5)          # negatief: naar achteren
    r = np.clip((yy - c) / np.maximum(d - c, 5), 0, 1)
    t_voor = voor * np.arccos(1 - 2 * r) / np.pi
    T = np.where(yy < c, t_boven, t_voor)
    return S.astype(np.float32), T.astype(np.float32)


def foto1():
    f = MK.laad(STOCK / 'handdoek2-gevouwen-1.jpg')
    # witbalans: de koele blauwige studio wordt warm gebroken wit (past bij crème)
    f = np.clip(f * np.array([0.988, 0.947, 0.904], np.float32), 0, 1)
    h, w = f.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ppc = 48
    ontw = ontwerp(ppc)
    uit = f.copy()
    # gemeten op de foto (2400 px breed): achterrand, vouwrug en onderrand per handdoek
    stapel = {
        'rood': dict(B=[(181, 700), (286, 512), (386, 494), (586, 482), (786, 473), (886, 482), (1086, 534), (1286, 584), (1486, 604),
                        (1686, 644), (1886, 669), (2086, 716), (2250, 760)],
                     C=[(181, 700), (300, 640), (400, 600), (600, 690), (800, 735), (1000, 745), (1200, 765), (1400, 800), (1600, 830),
                        (1800, 850), (2000, 860), (2150, 880), (2250, 900)],
                     D=[(181, 740), (286, 834), (386, 875), (486, 908), (586, 938), (686, 954), (786, 979), (886, 1024), (986, 1050),
                        (1086, 1071), (1186, 1100), (1286, 1125), (1386, 1158), (1486, 1174), (1586, 1197), (1686, 1219), (1786, 1249),
                        (1886, 1250), (2000, 1250), (2250, 1250)],
                     u0=34.0, v0=58.0),
        'teal': dict(B=[(135, 1000), (240, 874), (340, 863), (440, 870), (2195, 1100)],
                     C=[(135, 1040), (240, 1000), (340, 1030), (440, 1050), (640, 1080), (840, 1120), (1040, 1170), (1240, 1215),
                        (1440, 1250), (1640, 1290), (1840, 1300), (2040, 1290), (2195, 1280)],
                     D=[(135, 1093), (240, 1202), (340, 1236), (440, 1267), (540, 1295), (640, 1314), (740, 1344), (840, 1383), (940, 1414),
                        (1040, 1455), (1140, 1485), (1240, 1512), (1340, 1540), (1440, 1575), (1540, 1605), (1640, 1634), (1740, 1649),
                        (1840, 1650), (1940, 1640), (2195, 1640)],
                     u0=40.0, v0=96.0),
    }
    rand = np.zeros((h, w), np.float32)
    for naam, g in stapel.items():
        m = cv2.dilate(kleurmasker(f, naam), np.ones((5, 5), np.uint8))
        m = m * (yy <= interp(g['D'], xx) + 4)          # niet de gekleurde weerschijn op de tafel
        rand = np.maximum(rand, m)
        B = lambda x, p=g['B']: interp(p, x)
        C = lambda x, p=g['C']: interp(p, x)
        D = lambda x, p=g['D']: interp(p, x)
        s, t = gevouwen_uv(xx, yy, B, C, D, 1200, 36.0, float(D(np.float32(1200)) - C(np.float32(1200))), 22.0, 10.5)
        U = g['u0'] + s
        V = g['v0'] + t
        mz = cv2.GaussianBlur(m, (0, 0), 1.2)
        uit = breng_aan(uit, mz, U, V, ppc, ontw, schoon=f, verplaatsing=0.25, detail=0.9, mono=True, weef=0.01, waas=0.04, gamma=0.75,
                        ref=np.full(3, np.percentile(MK.helderheid(f)[m > 0.5], 88), np.float32))
    # losse rode en turquoise pluisjes langs de randen en de gekleurde weerschijn op de tafel neutraal maken
    zone = cv2.dilate(rand, np.ones((25, 25), np.uint8)) > 0
    zone |= (yy > 900)
    hsv = cv2.cvtColor((np.clip(uit, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    Hh, Ss = hsv[..., 0].astype(int), hsv[..., 1].astype(int)
    fel = zone & (rand < 0.5) & (Ss > 12) & ((Hh < 12) | (Hh > 160) | ((Hh > 75) & (Hh < 105)))
    fel = cv2.GaussianBlur(fel.astype(np.float32), (0, 0), 1.5)[..., None]
    grijs = MK.helderheid(uit)[..., None] * np.array([1.02, 1.0, 0.96], np.float32)
    uit = uit * (1 - fel) + grijs * fel
    global LAATSTE
    LAATSTE = uit
    bewaar(staand_packshot(uit), 'strandhanddoek-tegel-1')


def staand_packshot(img):
    """Liggend packshot naar 4:5: stapel klein genoeg in beeld, muur boven en tafel onder netjes verlengd."""
    sch = 1500 / 2160
    klein = cv2.resize(img, None, fx=sch, fy=sch, interpolation=cv2.INTER_AREA)
    kh, kw = klein.shape[:2]
    cx = int(1190 * sch)
    klein = klein[:, max(0, cx - 800):max(0, cx - 800) + 1600]
    boven, onder = 470, 2000 - kh - 470
    muur = cv2.GaussianBlur(klein[:40], (0, 0), 8).mean(axis=0, keepdims=True)
    muur = np.repeat(muur, boven, axis=0)
    # tafel: de onderste strook uitrekken (dichterbij is groter, dus dat klopt met het perspectief)
    n = kh - int(1665 * sch)                    # alleen tafel, onder de stapel
    strook = klein[-n:]
    tafel = cv2.resize(strook, (1600, onder + n), interpolation=cv2.INTER_CUBIC)
    rest = klein[:-n]
    return np.concatenate([muur, rest, tafel], axis=0)[:2000]


# ---------- foto 2: op het zand ----------
UITSNEDE_2 = (300, 150, 1600, 1775)   # zonder de voeten rechtsonder; rustig zand rechts houdt het bestand klein

def foto2():
    f = ontruis(MK.laad(STOCK / "handdoek2-zand-1.jpg"), 5, 14)
    h, w = f.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s = 15.5  # px per cm: 90 cm is ca. 1400 px, de linkerzoom valt buiten beeld
    # zoom (franjekant) en zelfkant (rechterrand), gemeten op de foto
    zoom = 836 + 0.013 * xx
    zelf = interp([(0, 1040), (900, 1043), (950, 1045), (1180, 1052), (1260, 1063), (1340, 1068), (1420, 1071), (1500, 1076),
                   (1820, 1078), (1980, 1076), (2133, 1080)], yy)
    U = BREED - (zelf - xx) / s
    V = (yy - zoom) / s
    binnen = ((xx < zelf) & (yy > zoom)).astype(np.float32)
    # bril eruit (ligt bovenop de handdoek)
    hsv = cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    H_, S_, V_ = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    # glazen en montuur (niet de schaduw van de bril: die hoort bij de schaduw op de handdoek)
    bril = ((V_ < 112) | ((S_ > 140) & ((H_ < 12) | (H_ > 168)))).astype(np.uint8)
    bril[:, :850] = 0; bril[:950] = 0; bril[1260:] = 0
    bril = cv2.morphologyEx(bril, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(bril)
    if n > 1:
        bril = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    vul = bril.copy(); ff = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(vul, ff, (0, 0), 1); bril = bril | (1 - vul)
    bril = cv2.dilate(bril, np.ones((3, 3), np.uint8)).astype(np.float32)
    masker = cv2.GaussianBlur(binnen, (0, 0), 1.0) * (1 - cv2.GaussianBlur(bril, (0, 0), 1.0))
    schoon = strepen_weg(f, 61)
    ontw, lm = ontwerp_met_label(s * 1.5)
    uit = breng_aan(f, masker, U, V, s * 1.5, ontw, schoon=schoon, verplaatsing=0.5, detail=0.6, waas=0.12, weef=0.012,
                    rust=cv2.dilate(bril, np.ones((61, 61), np.uint8)))
    global LAATSTE
    LAATSTE = uit
    x0, y0, x1, y1 = UITSNEDE_2
    uit = cv2.resize(uit[y0:y1, x0:x1], (1600, 2000), interpolation=cv2.INTER_AREA if x1 - x0 > 1600 else cv2.INTER_CUBIC)
    bewaar(uit, 'strandhanddoek-tegel-2')


if __name__ == '__main__':
    stappen = sys.argv[1:] or ['label', 'foto1', 'foto2', 'foto3']
    for st in stappen:
        if st == 'label':
            maak_label()
        elif st == 'ontwerp':
            o = ontwerp(8)
            Image.fromarray((o * 255).astype(np.uint8)).save(UIT / 'ontwerp.png')
        else:
            globals()[st]()
