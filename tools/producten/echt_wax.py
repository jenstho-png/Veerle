"""Surfwax met verpakking: echte stockfoto's (zie docs/producten/stock/bronnen.json) met onze eigen papieren wikkel.

Verpakking: elk blok wax zit in een papieren wikkel (crème papier, navy druk, een kleurvlak in de kleur van de
watertemperatuur). De wikkel loopt als een brede band om het blok; de uiteinden van de wax blijven zichtbaar.

Stappen:
1. python3 tools/producten/echt_wax.py art     schrijft de html van de wikkels naar tools/producten/uit_wax/
2. node tools/producten/render_wax.mjs          maakt er png's van
3. python3 tools/producten/echt_wax.py          maakt docs/producten/beelden/surfwax-<soort>-1.jpg en -2.jpg

-1: stapel van drie blokken met wikkel op een houten tafel tegen een witte muur (packshot).
-2: één blok rechtop op een tafel met blaadjes, warm licht, met de voorkant van de wikkel (sfeer en detail).
"""
import pathlib, sys
import cv2
import numpy as np

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(ROOT / 'tools' / 'brand2'))
import mockup as MK  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock'
ART = HIER / 'uit_wax'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
NAVY, CREME, TERRA = '#22324F', '#F3ECDD', '#C0603E'

SOORTEN = {
    'koud': dict(kleur='#C9DAEC', label='KOUD WATER', temp='ONDER 14 GRADEN'),
    'koel': dict(kleur='#E8D6B5', label='KOEL WATER', temp='14 TOT 19 GRADEN'),
    'warm': dict(kleur='#F0C9C4', label='WARM WATER', temp='BOVEN 19 GRADEN'),
}


# ---------- artwork ----------
def art_html():
    import brandbook as BB
    A = ROOT / 'theme' / 'assets'
    fonts = ''.join(f"@font-face{{font-family:'{f}';src:url('file://{A / b}') format('woff2');font-weight:{w}}}"
                    for f, b, w in [('Courier Prime', 'courierprime-bold.woff2', 700), ('Courier Prime', 'courierprime-regular.woff2', 400),
                                    ('Tide Tode Display', 'tide-tode-display.woff2', 400)])
    ART.mkdir(exist_ok=True)

    def pagina(naam, b, h, inhoud):
        (ART / f'{naam}.html').write_text(f'''<!doctype html><meta charset="utf-8"><style>{fonts}
* {{ margin: 0; box-sizing: border-box; }} html, body {{ width: {b}px; height: {h}px; overflow: hidden; background: transparent; }}
.c {{ font-family: 'Courier Prime'; font-weight: 700; text-transform: uppercase; color: {NAVY}; }}
</style><body>{inhoud}</body>''')

    def logo(soort, breedte):
        l = BB.LOGO[soort]
        return f'<svg viewBox="0 0 {l["w"]} {l["h"]}" style="width:{breedte}px;height:auto;display:block"><path fill="{NAVY}" fill-rule="evenodd" d="{l["d"]}"/></svg>'

    for s, d in SOORTEN.items():
        # zijkant van de wikkel (wat je ziet van een blok in de stapel): 1330 x 460
        pagina(f'band-zij-{s}', 1330, 460, f'''
<div style="position:absolute;inset:0;background:{CREME}">
  <div style="position:absolute;left:0;right:0;top:92px;display:flex;justify-content:center">{logo('liggend', 560)}</div>
  <div class="c" style="position:absolute;left:0;right:0;top:200px;text-align:center;font-size:30px;letter-spacing:.42em;padding-left:.42em">SURF WAX</div>
  <div style="position:absolute;left:50%;top:268px;transform:translateX(-50%);background:{d['kleur']};border-radius:40px;padding:16px 40px 14px 50px">
    <div class="c" style="font-size:32px;letter-spacing:.32em;white-space:nowrap">{d['label']}</div></div>
  <div class="c" style="position:absolute;left:60px;top:376px;font-size:22px;letter-spacing:.3em;font-weight:400">70 GRAM</div>
  <div class="c" style="position:absolute;right:60px;top:376px;font-size:22px;letter-spacing:.3em;font-weight:400">{d['temp']}</div>
</div>''')
        # voorkant van de wikkel (grote kant van het blok): 1080 x 1030
        pagina(f'band-voor-{s}', 1080, 1030, f'''
<div style="position:absolute;inset:0;background:{CREME}">
  <div class="c" style="position:absolute;left:0;right:0;top:92px;text-align:center;font-size:30px;letter-spacing:.46em;padding-left:.46em">SURF WAX</div>
  <div style="position:absolute;left:0;right:0;top:170px;display:flex;justify-content:center">{logo('gestapeld', 520)}</div>
  <div style="position:absolute;left:0;right:0;top:640px;height:150px;background:{d['kleur']};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">
    <div class="c" style="font-size:44px;letter-spacing:.34em;padding-left:.34em">{d['label']}</div>
    <div class="c" style="font-size:24px;letter-spacing:.34em;padding-left:.34em;font-weight:400">{d['temp']}</div></div>
  <div class="c" style="position:absolute;left:70px;bottom:92px;font-size:22px;letter-spacing:.28em;font-weight:400">BIJENWAS EN KOKOSOLIE</div>
  <div class="c" style="position:absolute;right:70px;bottom:92px;font-size:22px;letter-spacing:.28em;font-weight:400">70 GRAM</div>
</div>''')
    print('html klaar in', ART)


# ---------- hulpjes ----------
def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def L(img):
    return MK.helderheid(img)


def poets(img, rechthoeken, straal=7, ruis=0.006):
    """Tekst van de stockfoto weghalen (Telea inpaint) en een beetje korrel terugzetten."""
    m = np.zeros(img.shape[:2], np.uint8)
    for x0, y0, x1, y1 in rechthoeken:
        m[y0:y1, x0:x1] = 255
    return poets_masker(img, m, straal, ruis)


def poets_masker(img, m, straal=7, ruis=0.006):
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    uit = cv2.inpaint(u8, m, straal, cv2.INPAINT_TELEA).astype(np.float32) / 255
    k = cv2.GaussianBlur(np.random.default_rng(3).normal(0, ruis, img.shape[:2]).astype(np.float32), (0, 0), 0.7)[..., None]
    z = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 2)[..., None]
    return uit * z + img * (1 - z) + k * z


def art(naam):
    a = MK.laad_art(ART / f'{naam}.png')
    return a


def druk(img, a, quad, wit, blur=0.7, structuur=0.5, rand=0.8, licht=None, korrel=0.008):
    """Druk art (RGBA) in perspectief op het vlak quad (lb, rb, ro, lo) van wit papier.
    Kleur = inkt x licht van de foto (vermenigvuldigen), plus de fijne papierstructuur."""
    h, w = img.shape[:2]
    quad = np.float32(quad)
    doelb = max(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[2] - quad[3]))
    s = doelb / a.shape[1]
    if s < 1:
        a = cv2.resize(a, (int(a.shape[1] * s * 1.5), int(a.shape[0] * s * 1.5)), interpolation=cv2.INTER_AREA)
    ah, aw = a.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [aw, 0], [aw, ah], [0, ah]]), quad)
    laag = cv2.warpPerspective(a, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    Lb = L(img) if licht is None else licht
    lichtf = np.clip(cv2.GaussianBlur(Lb, (0, 0), 1.5) / wit, 0, 1.08)[..., None]
    fijn = (Lb - cv2.GaussianBlur(Lb, (0, 0), 1.6))[..., None]
    kleur = laag[..., :3] * lichtf + fijn * structuur
    if blur:
        kleur = cv2.GaussianBlur(kleur, (0, 0), blur)
    kleur = kleur + cv2.GaussianBlur(np.random.default_rng(7).normal(0, korrel, (h, w)).astype(np.float32), (0, 0), 0.6)[..., None]
    al = laag[..., 3]
    if rand:
        al = cv2.GaussianBlur(al, (0, 0), rand)
    al = al[..., None]
    return np.clip(img * (1 - al) + kleur * al, 0, 1)


def vlak(kleur_hex, b=400, h=200):
    a = np.ones((h, b, 4), np.float32)
    a[..., :3] = hexrgb(kleur_hex)
    return a


def wax_kleur(img, m, kleur_hex, glad=0, gamma=0.75, vlak=0, laag=0.5):
    """Blok wax omkleuren met behoud van licht en vorm. glad (oneven) strijkt korrel en vlekjes weg,
    gamma < 1 dempt het verschil tussen lichte en donkere kant zodat de kleur niet uitbijt."""
    bron = img
    if glad:
        u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        u8 = cv2.medianBlur(u8, glad)
        bron = cv2.bilateralFilter(u8, 0, 25, 5).astype(np.float32) / 255
    Lb = L(bron)
    if vlak:
        # korrel helemaal weg: licht alleen uit het blok zelf, sterk verzacht, plus wat fijne korrel van wax
        mb = cv2.GaussianBlur(m, (0, 0), vlak)
        Lz = cv2.GaussianBlur(Lb * m, (0, 0), vlak) / np.maximum(mb, 1e-4)
        k = cv2.GaussianBlur(np.random.default_rng(5).normal(0, 0.012, Lb.shape).astype(np.float32), (0, 0), 1.2)
        Lb = Lz + k
    ref = np.percentile(Lb[m > 0.5], 60) if (m > 0.5).any() else 0.7
    f = np.clip(np.maximum(Lb / ref, 1e-3) ** gamma, laag, 1.1)[..., None]
    nieuw = np.clip(hexrgb(kleur_hex)[None, None] * f, 0, 1)
    mm = m[..., None]
    return img * (1 - mm) + nieuw * mm


def tint(img, m, kleur_hex, wit):
    """Wit papier crème maken: inkt x licht, alleen waar m (zacht masker) is."""
    licht = np.clip(L(img) / wit, 0, 1.08)[..., None]
    nieuw = hexrgb(kleur_hex)[None, None] * licht
    mm = m[..., None]
    return img * (1 - mm) + nieuw * mm


def rond_rechthoek(shape, x0, y0, x1, y1, r):
    m = np.zeros(shape, np.uint8)
    cv2.rectangle(m, (x0 + r, y0), (x1 - r, y1), 1, -1)
    cv2.rectangle(m, (x0, y0 + r), (x1, y1 - r), 1, -1)
    for cx, cy in [(x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)]:
        cv2.circle(m, (cx, cy), r, 1, -1)
    return m


def bewaar(img, naam, x0, y0, b, rechts=0):
    """Uitsnede in 4:5 (b breed) en opslaan als 1600 x 2000 onder 190 kB.
    rechts: zoveel pixels muur en tafel rechts bijspiegelen (met een zachte naad)."""
    h = int(round(b * 1.25))
    if rechts:
        w = img.shape[1]
        img = np.concatenate([img, img[:, w - rechts:w][:, ::-1]], 1)
    uit = img[y0:y0 + h, x0:x0 + b]
    uit = cv2.resize(uit, (1600, 2000), interpolation=cv2.INTER_AREA if b > 1600 else cv2.INTER_CUBIC)
    MK.bewaar(uit, DOEL / f'{naam}.jpg')
    print('foto', naam)


# ---------- -1: stapel van drie blokken ----------
# banden (voorkant, lb rb ro lo) en de zichtbare uiteinden van de blokken, gemeten op wax2-stapel-1.jpg (2400 x 3598)
STAPEL_BANDEN = [
    [(1181, 2394), (2072, 2394), (2073, 2705), (1181, 2705)],
    [(1200, 2706), (2095, 2706), (2096, 2998), (1200, 2998)],
    [(1178, 2999), (2064, 2999), (2071, 3292), (1179, 3292)],
]
STAPEL_TEKST = [(1240, 2318, 1990, 2432), (1170, 3275, 1200, 3300), (1330, 2505, 1910, 2585), (1400, 2748, 1905, 2820), (1330, 3140, 1910, 3215)]
STAPEL_BLOKKEN = [((1085, 2320, 2200, 2706), (1183, 2072)), ((1085, 2700, 2210, 3000), (1202, 2095)), ((1085, 2995, 2200, 3300), (1180, 2068))]


_CACHE = {}


def stapel_masker(img):
    if 'stapel' in _CACHE:
        return _CACHE['stapel']
    sub = (np.clip(img[2200:3400, 1000:2300], 0, 1) * 255).astype(np.uint8)[..., ::-1].copy()
    m = np.full(sub.shape[:2], cv2.GC_BGD, np.uint8)
    m[2320 - 2200:3300 - 2200, 1085 - 1000:2200 - 1000] = cv2.GC_PR_FGD
    m[2400 - 2200:3280 - 2200, 1190 - 1000:2060 - 1000] = cv2.GC_FGD
    cv2.grabCut(sub, m, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
    vol = np.zeros(img.shape[:2], np.uint8)
    vol[2200:3400, 1000:2300] = ((m == 1) | (m == 3)).astype(np.uint8)
    # het crème blok in het midden lijkt te veel op de muur: rechts met de hand
    vol |= rond_rechthoek(vol.shape, 2094, 2711, 2196, 2990, 12)
    _CACHE['stapel'] = vol
    return vol


def stapel(soort):
    d = SOORTEN[soort]
    img = MK.laad(STOCK / 'wax2-stapel-1.jpg')
    vol = stapel_masker(img)
    # 1. blokken in de waxkleur (alleen de uiteinden naast de band)
    for (x0, y0, x1, y1), (bl, br) in STAPEL_BLOKKEN:
        m = np.zeros(vol.shape, np.uint8)
        m[y0:y1, x0:bl + 3] = 1
        m[y0:y1, br - 3:x1] = 1
        m = cv2.dilate((m & vol), np.ones((3, 3), np.uint8)).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 1.6)
        img = wax_kleur(img, m, d['kleur'], glad=15 if y0 > 2900 else 5, laag=0.62)
    # 2. oude tekst van de wikkels weg
    img = poets(img, STAPEL_TEKST)
    # 3. onze wikkel erop: crème papier met druk
    zij = art(f'band-zij-{soort}')
    for i, q in enumerate(STAPEL_BANDEN):
        img = druk(img, zij, q, wit=0.955, blur=1.1)
    # bovenkant van de bovenste wikkel (onscherp): alleen crème papier
    m = np.zeros(img.shape[:2], np.float32)
    m[2342:2402, 1186:2068] = 1
    m = cv2.GaussianBlur(m, (0, 0), 3.5)
    img = tint(img, m, CREME, wit=0.95)
    return img


if __name__ == '__main__':
    if sys.argv[1:2] == ['art']:
        art_html(); sys.exit()
    stappen = sys.argv[1:] or ['stapel', 'blok']
    for soort in SOORTEN:
        if 'stapel' in stappen:
            bewaar(stapel(soort), f'surfwax-{soort}-1', 728, 1298, 1840, rechts=168)
