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
    """Bovenvlak van het echte zeepblok, rechtgetrokken en liggend gedraaid, als lichtheidsveld (b x h, rond 1).
    Groot lichtverloop van de stockfoto eruit; korrel, putjes en snijsporen blijven en worden iets aangezet."""
    img = MK.laad(FLAT / 'zeep-blok-boven-1.jpg')
    q = np.float32(ZEEP_VLAK)
    c = q.mean(0)
    q = c + (q - c) * (1 - 2 * inset)                   # randen en zijvlak van het blok vallen weg
    lang = int(np.linalg.norm(q[1] - q[2]))
    kort = int(np.linalg.norm(q[0] - q[1]))
    # staand blok: lb-rb is de korte kant. Liggend maken (90 graden tegen de klok in)
    doel = np.float32([[0, kort], [0, 0], [lang, 0], [lang, kort]])
    M = cv2.getPerspectiveTransform(q, doel)
    vlak = cv2.warpPerspective(img, M, (lang, kort), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    vlak = cv2.resize(vlak, (b, h), interpolation=cv2.INTER_CUBIC)
    L = MK.helderheid(vlak)
    groot = cv2.GaussianBlur(L, (0, 0), 70)
    fijn = (L - cv2.GaussianBlur(L, (0, 0), 2.5)) / groot
    midden = (cv2.GaussianBlur(L, (0, 0), 2.5) - cv2.GaussianBlur(L, (0, 0), 22)) / groot
    # gele zeepvlekjes (donkerder, breed) dempen, putjes en snijsporen aanzetten
    detail = 1 + np.clip(fijn * 2.4, -0.16, 0.08) + np.clip(midden * 1.5, -0.07, 0.05)
    middel = (groot / groot.mean()) ** 0.35
    return (detail * middel).astype(np.float32)


def rand_afstand(shape, x0, y0, x1, y1, r, zaad, ruw=1.0):
    """Getekende afstand tot de rand van een afgeronde rechthoek (positief binnen), met een niet kaarsrechte rand."""
    h, b = shape
    m = EW.rond_rechthoek((h, b), int(x0), int(y0), int(x1), int(y1), r)
    d = cv2.distanceTransform((m > 0).astype(np.uint8), cv2.DIST_L2, 5) - cv2.distanceTransform((m == 0).astype(np.uint8), cv2.DIST_L2, 5)
    return d + ruis((h, b), 1.0 * ruw, 9, zaad) + ruis((h, b), 0.35 * ruw, 1.5, zaad + 1)


def hapjes(d, zaad, n=5, diep=4.0):
    """Een paar kleine hapjes uit de rand, zoals bij met de hand gesneden wax."""
    h, b = d.shape
    rng = np.random.default_rng(zaad)
    yy, xx = np.ogrid[:h, :b]
    for _ in range(n):
        kant = rng.integers(4)
        x = rng.uniform(0.08, 0.92) * b if kant < 2 else (4 if kant == 2 else b - 4)
        y = rng.uniform(0.08, 0.92) * h if kant >= 2 else (4 if kant == 0 else h - 4)
        d = d - diep * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * rng.uniform(5, 12) ** 2))
    return d


def naar_buiten(d, glad=1.5):
    dz = cv2.GaussianBlur(d.astype(np.float32), (0, 0), glad)
    gy, gx = np.gradient(dz)
    n = np.hypot(gx, gy) + 1e-6
    return -gx / n, -gy / n, dz


def schuine_rand(d, breedte, sterkte):
    """Licht en schaduw van een afgeronde rand (licht linksboven). d = afstand tot de rand, positief binnen."""
    nx, ny, dz = naar_buiten(d)
    richting = nx * LICHT_NAAR[0] + ny * LICHT_NAAR[1]                # +1: rand naar het raam
    profiel = np.clip(1 - dz / breedte, 0, 1) ** 1.6
    return 1 + sterkte * richting * profiel - 0.04 * profiel


def zijlicht(d_boven):
    """Licht op de zijvlakken (die je van recht boven net ziet omdat de lens erboven hangt):
    links en boven kijken naar het raam, rechts en onder liggen in de schaduw."""
    nx, ny, _ = naar_buiten(d_boven, glad=8)
    richting = nx * LICHT_NAAR[0] + ny * LICHT_NAAR[1]
    return 0.80 + 0.13 * richting


ZIJ = (17, 12)      # zichtbare zijkant links/rechts en boven/onder (px op het blok), lens recht boven het midden


def wax_blok(soort, b=1450, h=1000, zaad=3):
    """Pak-blok van boven: bovenvlak met echte korrel en een smalle zichtbare zijkant rondom. Geeft rgb, alpha, d_boven."""
    kleur = hexrgb(EW.SOORTEN[soort]['kleur'])
    sx, sy = ZIJ
    d_buiten = hapjes(rand_afstand((h, b), 0, 0, b - 1, h - 1, 26, zaad), zaad, n=4, diep=3)
    d_boven = hapjes(rand_afstand((h, b), sx, sy, b - 1 - sx, h - 1 - sy, 18, zaad + 5, ruw=0.8), zaad + 9, n=6, diep=3.5)
    a = np.clip(d_buiten + 0.5, 0, 1).astype(np.float32)
    boven = np.clip(d_boven + 0.5, 0, 1)
    Lv = wax_vlak(b, h)
    f_boven = Lv * schuine_rand(d_boven, 14, 0.10)
    # zijkant: gesneden wax, korrel uitgerekt langs de rand, iets ruwer
    Lz = cv2.GaussianBlur(Lv, (0, 0), sigmaX=3, sigmaY=3) * (1 + ruis((h, b), 0.03, 1.0, zaad + 3))
    f_zij = Lz * zijlicht(d_boven) * (1 - 0.10 * np.clip(1 - d_buiten / 3, 0, 1))   # uiterste randje iets donkerder
    f = f_boven * boven + f_zij * (1 - boven)
    # wax is satijnmat: heel zacht glanslicht naar het raam toe
    yy, xx = np.mgrid[0:h, 0:b].astype(np.float32)
    f = f * (1.03 - 0.05 * (xx / b * 0.5 + yy / h * 0.5))
    rgb = np.clip(kleur[None, None] * f[..., None] ** 1.1, 0, 1)
    return rgb.astype(np.float32), a, d_boven


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
    s = (xx - p0[0]) * n[0] + (yy - p0[1]) * n[1]
    langs = np.clip(np.sin(np.pi * t), 0, 1) ** 0.7
    flank = s / breedte * np.exp(-(s / breedte) ** 2)
    kant = float(np.dot(n, LICHT_NAAR))
    return 1 + sterkte * 2.3 * flank * langs * np.sign(kant if abs(kant) > 1e-3 else 1)


def wikkel_pak(soort, b=1450, h=1000, zaad=5):
    """Een pak surfwax van boven: blok met de papieren band om het midden. Geeft RGBA (float32)."""
    rgb, a, d_boven = wax_blok(soort, b, h)
    sx, sy = ZIJ
    hb = h - 2 * sy                                             # bedrukt deel = bovenvlak
    art = EW.art(f'band-voor-{soort}')[..., :3]
    bb = int(round(hb * art.shape[1] / art.shape[0]))
    x0 = (b - bb) // 2
    x1 = x0 + bb
    art = cv2.resize(art, (bb, hb), interpolation=cv2.INTER_AREA)
    creme = hexrgb(CREME)
    # inkt: iets onregelmatig van dikte en een fractie zacht, zoals offset op ongecoat papier
    inkt = np.clip(np.abs(art - creme[None, None]).sum(-1) / 0.4, 0, 1)
    dichtheid = 0.94 + ruis((hb, bb), 0.03, 0.8, zaad)
    art = creme[None, None] + (art - creme[None, None]) * (1 - inkt * (1 - dichtheid))[..., None]
    art = cv2.GaussianBlur(art, (0, 0), 0.55)
    vel = np.ones((h, bb, 3), np.float32) * creme
    vel[sy:sy + hb] = art
    # papier: structuur, vouw om de lange randen, zijkanten van het blok in licht en schaduw, kreukjes bij de vouw
    licht = papier(bb, h, zaad)
    yy = np.arange(h, dtype=np.float32)[:, None]
    zij_b = np.clip(sy - yy + 0.5, 0, 1)                         # papier over de bovenzijde (naar het raam)
    zij_o = np.clip(yy - (h - 1 - sy) + 0.5, 0, 1)               # papier over de onderzijde (schaduw)
    licht = licht * (1 + 0.02 * zij_b - 0.24 * zij_o)
    vouw_b = np.exp(-((yy - sy) / 2.2) ** 2)
    vouw_o = np.exp(-((yy - (h - 1 - sy)) / 2.2) ** 2)
    licht = licht * (1 + 0.06 * vouw_b - 0.10 * vouw_o)          # de vouwlijn zelf: boven glimt, onder donker
    licht = licht * (1 - 0.035 * np.exp(-((yy - sy - 9) / 5) ** 2) - 0.03 * np.exp(-((h - 1 - sy - 9 - yy) / 5) ** 2))
    xx = np.arange(bb, dtype=np.float32)[None, :]
    licht = licht * (1 + 0.016 * np.sin(np.pi * xx / bb) - 0.01)  # papier bolt heel licht op het blok
    rng = np.random.default_rng(zaad)
    for (cx, cy, hoek, lengte) in [(18, sy + 20, 62, 95), (bb - 22, sy + 16, 118, 80), (24, h - sy - 18, -58, 110),
                                    (bb - 16, h - sy - 24, -122, 70), (bb * 0.31, sy + 2, 84, 46), (bb * 0.72, h - sy - 2, -95, 52)]:
        r = np.deg2rad(hoek)
        p0 = (cx - np.cos(r) * lengte * 0.15, cy - np.sin(r) * lengte * 0.15)
        p1 = (cx + np.cos(r) * lengte, cy + np.sin(r) * lengte)
        licht = licht * kreuk((h, bb), p0, p1, rng.uniform(2.2, 3.5), rng.uniform(0.035, 0.06))
    band = np.clip(vel * licht[..., None], 0, 1)
    # snijrand van de band: niet kaarsrecht, links een randje licht, rechts een dun schaduwrandje op de wax
    rand_x = ruis((h, 1), 0.5, 18, zaad + 7).ravel()
    xg = np.arange(b, dtype=np.float32)[None, :]
    l_rand = x0 + rand_x[:, None]
    r_rand = x1 + rand_x[::-1, None]
    bandm = np.clip(np.minimum(xg - l_rand + 0.5, r_rand - xg + 0.5), 0, 1)
    sch = np.clip(xg - r_rand, 0, None)
    sch = cv2.GaussianBlur((np.exp(-sch / 3.0) * (sch > 0)).astype(np.float32), (0, 0), 1.2)
    rgb = rgb * (1 - 0.22 * sch[..., None])
    links = np.exp(-np.abs(xg - l_rand - 1.2) / 1.0)
    vol = np.zeros_like(rgb)
    vol[:, x0:x1] = band
    vol = vol * (1 + 0.05 * links[..., None])
    uit = rgb * (1 - bandm[..., None]) + vol * bandm[..., None]
    # silhouet: waar de band zit loopt het papier recht door tot de onderkant van het blok
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
