"""Gear in de vaste studiostijl (stijl.py): recht van boven, gecentreerd, echt zand of naadloos papier, raamlicht linksboven.

Surfwax: het blok is een echte zeepfoto van recht boven (stock/flatlay/zeep-blok-boven-1.jpg, Unsplash), rechtgetrokken
en omgekleurd, zodat de matte korrel, putjes en snijsporen echt zijn. De wikkel is de artwork uit echt_wax.py
(uit_wax/band-voor-<soort>.png) op crème papier met vezel, vlekkerigheid en kreukjes waar hij om de rand vouwt.

Gebruik:
    python3 tools/producten/flatlay_gear.py proef      # docs/producten/proef/gear-proef-1.jpg (surfwax koud, los pak)
"""
import pathlib, sys
import cv2
import numpy as np

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import mockup as MK          # noqa: E402
import stijl as ST           # noqa: E402
import echt_wax as EW        # noqa: E402
import echt as E             # noqa: E402,F401  (karabijnhaak: karabijn, bandlabel, d_ring, gegoten_logo, groter_doek)

FLAT = ROOT / 'docs' / 'producten' / 'stock' / 'flatlay'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
PROEF = ROOT / 'docs' / 'producten' / 'proef'
CREME = '#F3ECDD'
LICHT_NAAR = np.array([-0.62, -0.78], np.float32)     # richting naar het raam (linksboven), in beeldcoordinaten

# bovenvlak van het witte zeepblok op zeep-blok-boven-1.jpg (4500 x 4500): lb, rb, ro, lo
ZEEP_VLAK = [(2408, 1508), (3235, 1240), (3560, 2275), (2722, 2536)]


def ruis(shape, sigma, schaal, zaad):
    r = np.random.default_rng(zaad).normal(0, 1, shape).astype(np.float32)
    if schaal:
        r = cv2.GaussianBlur(r, (0, 0), schaal)
    return r / (r.std() + 1e-6) * sigma


def hexrgb(h):
    return EW.hexrgb(h)


# ---------- wax ----------
def wax_vlak(b, h, inset=0.035):
    """Bovenvlak van het echte zeepblok, rechtgetrokken en liggend gedraaid, als lichtheidsveld (b x h).
    Groot lichtverloop van de stockfoto eruit, de fijne korrel en putjes blijven."""
    img = MK.laad(FLAT / 'zeep-blok-boven-1.jpg')
    q = np.float32(ZEEP_VLAK)
    c = q.mean(0)
    q = c + (q - c) * (1 - 2 * inset)                   # randen en zijvlak van het blok vallen weg
    lang = int(np.linalg.norm(q[1] - q[2]))
    kort = int(np.linalg.norm(q[0] - q[1]))
    # staand blok: lb-rb is de korte kant. Liggend maken: lo -> lb, lb -> rb, rb -> ro, ro -> lo (90 graden tegen de klok in)
    doel = np.float32([[0, kort], [0, 0], [lang, 0], [lang, kort]])
    M = cv2.getPerspectiveTransform(q, doel)
    vlak = cv2.warpPerspective(img, M, (lang, kort), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    vlak = cv2.resize(vlak, (b, h), interpolation=cv2.INTER_CUBIC)
    L = MK.helderheid(vlak)
    groot = cv2.GaussianBlur(L, (0, 0), 70)
    detail = L / np.maximum(groot, 1e-3)
    # de gele vlekjes (zeep) iets dempen, putjes en snijsporen houden
    detail = 1 + np.clip(detail - 1, -0.12, 0.06) * 1.25
    middel = (groot / groot.mean()) ** 0.25           # een beetje van de echte vlekkerigheid
    return (detail * middel).astype(np.float32)


def blok_masker(b, h, r=22, zaad=3):
    """Silhouet van een gesneden blok: afgeronde hoeken, randjes net niet kaarsrecht, een paar kleine hapjes."""
    m = EW.rond_rechthoek((h, b), 0, 0, b - 1, h - 1, r).astype(np.float32)
    d = cv2.distanceTransform((m > 0).astype(np.uint8), cv2.DIST_L2, 5) - cv2.distanceTransform((m == 0).astype(np.uint8), cv2.DIST_L2, 5)
    d = d + ruis((h, b), 1.1, 9, zaad) + ruis((h, b), 0.35, 1.5, zaad + 1)
    rng = np.random.default_rng(zaad)
    for _ in range(5):                                   # kleine hapjes uit de rand
        rand = rng.integers(4)
        x = rng.uniform(0.1, 0.9) * b if rand < 2 else (6 if rand == 2 else b - 6)
        y = rng.uniform(0.1, 0.9) * h if rand >= 2 else (6 if rand == 0 else h - 6)
        yy, xx = np.ogrid[:h, :b]
        d = d - 4.0 * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * rng.uniform(5, 11) ** 2))
    return np.clip(d + 0.5, 0, 1).astype(np.float32), d


def schuine_rand(d, breedte, sterkte):
    """Licht en schaduw van een afgeronde rand (licht linksboven). d = afstand tot de rand, positief binnen."""
    dz = cv2.GaussianBlur(d.astype(np.float32), (0, 0), 1.5)
    gy, gx = np.gradient(dz)
    n = np.hypot(gx, gy) + 1e-6
    naar_buiten = np.stack([-gx / n, -gy / n], -1)
    richting = (naar_buiten * LICHT_NAAR[None, None]).sum(-1)       # +1: rand naar het raam
    profiel = np.clip(1 - dz / breedte, 0, 1) ** 1.6
    return 1 + sterkte * richting * profiel - 0.05 * profiel


def wax_blok(soort, b=1450, h=1000):
    """Los blok wax van boven: echte korrel, omgekleurd naar de waxkleur. Geeft rgb, alpha en randafstand."""
    kleur = hexrgb(EW.SOORTEN[soort]['kleur'])
    Lv = wax_vlak(b, h)
    a, d = blok_masker(b, h)
    f = Lv * schuine_rand(d, 26, 0.16)
    # wax is iets doorschijnend: de fijnste korrel zacht, de putjes blijven
    f = cv2.GaussianBlur(f, (0, 0), 0.6)
    rgb = np.clip(kleur[None, None] * f[..., None] ** 1.1, 0, 1)
    return rgb.astype(np.float32), a, d


def papier(b, h, zaad=11):
    """Licht en structuur van ongecoat crème papier: fijne vezel, langere vezelstreepjes, wat vlekkerigheid."""
    vezel = ruis((h, b), 0.010, 0.7, zaad)
    streep = cv2.GaussianBlur(np.random.default_rng(zaad + 1).normal(0, 1, (h, b)).astype(np.float32), (0, 0), sigmaX=6, sigmaY=0.8)
    streep = streep / (streep.std() + 1e-6) * 0.006
    vlek = ruis((h, b), 0.010, 40, zaad + 2)
    return 1 + vezel + streep + vlek


def kreuk(shape, p0, p1, breedte, sterkte):
    """Een zachte kreuk in het papier: lichte en donkere flank langs de lijn p0-p1."""
    h, b = shape
    yy, xx = np.mgrid[0:h, 0:b].astype(np.float32)
    p0, p1 = np.float32(p0), np.float32(p1)
    v = p1 - p0
    lengte = np.linalg.norm(v)
    t = np.clip(((xx - p0[0]) * v[0] + (yy - p0[1]) * v[1]) / lengte ** 2, 0, 1)
    n = np.array([-v[1], v[0]]) / lengte
    s = (xx - p0[0]) * n[0] + (yy - p0[1]) * n[1]           # afstand dwars op de kreuk, met teken
    langs = np.clip(np.sin(np.pi * t), 0, 1) ** 0.7                         # loopt uit naar de uiteinden
    flank = s / breedte * np.exp(-(s / breedte) ** 2)         # + aan de ene kant, - aan de andere
    kant = float(np.dot(n, LICHT_NAAR))                       # welke flank naar het raam kijkt
    return 1 + sterkte * 2.3 * flank * langs * np.sign(kant if abs(kant) > 1e-3 else 1)


def wikkel_pak(soort, b=1450, h=1000, zaad=5):
    """Een pak surfwax van boven: blok met de papieren band in het midden. Geeft RGBA (float32)."""
    rgb, a, d = wax_blok(soort, b, h)
    art = EW.art(f'band-voor-{soort}')[..., :3]
    bb = int(round(h * art.shape[1] / art.shape[0]))          # band zo hoog als het blok, verhouding van de artwork
    x0 = (b - bb) // 2
    x1 = x0 + bb
    art = cv2.resize(art, (bb, h), interpolation=cv2.INTER_AREA)
    creme = hexrgb(CREME)
    # inkt: iets onregelmatig van dikte en een fractie zacht, zoals offset op ongecoat papier
    inkt = np.clip(np.abs(art - creme[None, None]).sum(-1) / 0.4, 0, 1)
    dichtheid = 0.94 + ruis((h, bb), 0.03, 0.8, zaad)
    art = creme[None, None] + (art - creme[None, None]) * (1 - inkt * (1 - dichtheid))[..., None]
    art = cv2.GaussianBlur(art, (0, 0), 0.55)
    # papier: structuur, vouw om de lange randen, kreukjes bij de hoeken van de band
    licht = papier(bb, h, zaad)
    yy = np.arange(h, dtype=np.float32)[:, None]
    boven = np.exp(-yy / 9.0)
    onder = np.exp(-(h - 1 - yy) / 9.0)
    licht = licht * (1 + 0.07 * boven - 0.16 * onder)          # vouw boven vangt licht, vouw onder in de schaduw
    licht = licht * (1 - 0.05 * np.exp(-((yy - 14) / 6) ** 2) - 0.03 * np.exp(-((h - 15 - yy) / 6) ** 2))
    xx = np.arange(bb, dtype=np.float32)[None, :]
    licht = licht * (1 + 0.018 * np.sin(np.pi * xx / bb) - 0.012)   # papier bolt heel licht op het blok
    rng = np.random.default_rng(zaad)
    for (cx, cy, hoek, lengte) in [(18, 30, 62, 95), (bb - 22, 26, 118, 80), (24, h - 28, -58, 110), (bb - 16, h - 34, -122, 70),
                                    (bb * 0.31, 8, 84, 46), (bb * 0.72, h - 8, -95, 52)]:
        r = np.deg2rad(hoek)
        p0 = (cx - np.cos(r) * lengte * 0.15, cy - np.sin(r) * lengte * 0.15)
        p1 = (cx + np.cos(r) * lengte, cy + np.sin(r) * lengte)
        licht = licht * kreuk((h, bb), p0, p1, rng.uniform(2.2, 3.5), rng.uniform(0.035, 0.06))
    band = np.clip(art * licht[..., None], 0, 1)
    # snijrand van de band: niet kaarsrecht, links een randje licht, rechts een dun schaduwrandje op de wax
    rand_x = ruis((h, 1), 0.5, 18, zaad + 7).ravel()
    xg = np.arange(b, dtype=np.float32)[None, :]
    bandm = np.clip(np.minimum(xg - (x0 + rand_x[:, None]) + 0.5, (x1 + rand_x[::-1, None]) - xg + 0.5), 0, 1)
    sch = np.clip(xg - (x1 + rand_x[::-1, None]), 0, None)
    sch = np.exp(-sch / 3.0) * (sch > 0)
    sch = cv2.GaussianBlur(sch.astype(np.float32), (0, 0), 1.2)
    rgb = rgb * (1 - 0.22 * sch[..., None])
    links = np.exp(-np.abs(xg - (x0 + rand_x[:, None]) - 1.2) / 1.0)
    vol = np.zeros_like(rgb)
    vol[:, x0:x1] = band
    vol = vol * (1 + 0.05 * links[..., None])
    uit = rgb * (1 - bandm[..., None]) + vol * bandm[..., None]
    # silhouet: waar de band zit loopt het papier recht door tot de vouw
    alpha = np.maximum(a, bandm * np.clip(np.minimum(yy, h - 1 - yy) + 0.5, 0, 1))
    return np.dstack([np.clip(uit, 0, 1), alpha]).astype(np.float32)


def proef():
    doek = ST.achtergrond('baby')
    pak = wikkel_pak('koud')
    doek = ST.leg(doek, pak, breedte=1180, midden=(800, 1000), draai=0, hoogte=13, contact=0.55)
    PROEF.mkdir(parents=True, exist_ok=True)
    pad = ST.bewaar(ST.afwerking(doek), PROEF / 'gear-proef-1.jpg')
    print('proef', pad)


if __name__ == '__main__':
    for stap in sys.argv[1:] or ['proef']:
        globals()[stap]()
