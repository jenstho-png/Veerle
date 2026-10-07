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
    detail = 1 + np.clip(fijn * 3.2, -0.18, 0.09) + np.clip(midden * 1.5, -0.07, 0.05)
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
    return 0.89 + 0.11 * richting + 0.02 * np.clip(richting, 0, 1)


ZIJ = (21, 15)      # zichtbare zijkant links/rechts en boven/onder (px op het blok), lens recht boven het midden


def wax_blok(soort, b=1450, h=1000, zaad=3, kam=False, gebruikt=False):
    """Pak-blok van boven: bovenvlak met echte korrel en een smalle zichtbare zijkant rondom. Geeft rgb, alpha, d_boven."""
    kleur = hexrgb(EW.SOORTEN[soort]['kleur'])
    sx, sy = ZIJ
    d_buiten = hapjes(rand_afstand((h, b), 0, 0, b - 1, h - 1, 26, zaad), zaad, n=4, diep=3)
    d_boven = hapjes(rand_afstand((h, b), sx, sy, b - 1 - sx, h - 1 - sy, 18, zaad + 5, ruw=0.8), zaad + 9, n=6, diep=3.5)
    if gebruikt:
        # afgesleten kant links: veel rondere hoeken
        links = (np.arange(b, dtype=np.float32)[None, :] < b / 2)
        d_buiten = np.where(links, np.minimum(d_buiten, rand_afstand((h, b), 0, 0, b - 1, h - 1, 110, zaad + 40)), d_buiten)
        d_boven = np.where(links, np.minimum(d_boven, rand_afstand((h, b), sx + 6, sy, b - 1 - sx, h - 1 - sy, 120, zaad + 41, ruw=0.8)), d_boven)
    a = np.clip(d_buiten + 0.5, 0, 1).astype(np.float32)
    boven = np.clip(d_boven + 0.5, 0, 1)
    Lv = wax_vlak(b, h)
    f_boven = Lv * schuine_rand(d_boven, 14, 0.10)
    # zijkant: gesneden wax, korrel uitgerekt langs de rand, iets ruwer
    Lz = cv2.GaussianBlur(Lv, (0, 0), sigmaX=3, sigmaY=3) * (1 + ruis((h, b), 0.03, 1.0, zaad + 3))
    f_zij = Lz * zijlicht(d_boven) * (1 - 0.05 * np.clip(1 - d_buiten / 2.5, 0, 1))   # uiterste randje iets donkerder
    f = f_boven * boven + f_zij * (1 - boven)
    yy, xx = np.mgrid[0:h, 0:b].astype(np.float32)
    if kam:
        # een paar groefjes van een waxkam over een hoek van het blok: smalle geultjes, schaduwkant rechtsonder
        groef = np.zeros((h, b), np.float32)
        rng = np.random.default_rng(zaad + 21)
        for i in range(7):
            y = h * 0.66 + i * 21 + rng.uniform(-2, 2)
            x0, x1 = b * 0.63 + rng.uniform(-30, 10), b * 0.93 + rng.uniform(-20, 15)
            langs = np.clip((xx - x0) / 40, 0, 1) * np.clip((x1 - xx) / 60, 0, 1)
            groef = np.maximum(groef, np.exp(-((yy - y) / 3.2) ** 2) * langs * rng.uniform(0.7, 1.0))
        groef = groef * boven
        gy = np.gradient(cv2.GaussianBlur(groef, (0, 0), 1.0), axis=0)
        f = f * (1 - 0.06 * groef) * (1 + 2.2 * gy * LICHT_NAAR[1] * -1)
    if gebruikt:
        # linkerkant is al over een board gewreven: hoeken rond, vlak licht glimmend met strepen in de wrijfrichting
        slijt = np.clip(1 - xx / (b * 0.32), 0, 1) ** 1.5 * boven
        streep = cv2.GaussianBlur(np.random.default_rng(zaad + 30).normal(0, 1, (h, b)).astype(np.float32), (0, 0), sigmaX=1.2, sigmaY=10)
        streep = streep / (streep.std() + 1e-6)
        f = f * (1 + slijt * (0.035 + 0.03 * streep))
    # wax is satijnmat: heel zacht glanslicht naar het raam toe
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


def wikkel_pak(soort, b=1450, h=1000, zaad=5, verschuif=0, **blok):
    """Een pak surfwax van boven: blok met de papieren band om het midden. Geeft RGBA (float32)."""
    rgb, a, d_boven = wax_blok(soort, b, h, **blok)
    sx, sy = ZIJ
    hb = h - 2 * sy                                             # bedrukt deel = bovenvlak
    art = EW.art(f'band-voor-{soort}')[..., :3]
    bb = int(round(hb * art.shape[1] / art.shape[0]))
    x0 = (b - bb) // 2 + int(verschuif)
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
    sch = cv2.GaussianBlur((np.exp(-sch / 4.0) * (sch > 0)).astype(np.float32), (0, 0), 2.0)
    rgb = rgb * (1 - 0.13 * sch[..., None])
    links = np.exp(-np.abs(xg - l_rand - 1.2) / 1.0)
    vol = np.zeros_like(rgb)
    vol[:, x0 - 3:x1 + 3] = cv2.copyMakeBorder(band, 0, 0, 3, 3, cv2.BORDER_REPLICATE)   # snijrand mag een fractie uitwijken
    vol = vol * (1 + 0.05 * links[..., None])
    uit = rgb * (1 - bandm[..., None]) + vol * bandm[..., None]
    # silhouet: waar de band zit loopt het papier recht door tot de onderkant van het blok
    alpha = np.maximum(a, bandm * np.clip(np.minimum(yy, h - 1 - yy) + 0.5, 0, 1))
    return np.dstack([np.clip(uit, 0, 1), alpha]).astype(np.float32)


# ---------- board deck met verse wax ----------
DECK = {'koud': '#F1D9D2', 'koel': '#D3E6DF', 'warm': '#F1EADB'}      # rose, mint en zand deck (zelfde tinten als de tasshoot)
L3 = np.array([LICHT_NAAR[0] * 0.77, LICHT_NAAR[1] * 0.77, 0.64], np.float32)   # raam linksboven, ca. 40 graden hoog
L3 /= np.linalg.norm(L3)


def deck(kleur_hex, stringer_x, zaad=1, B=ST.B, H=ST.H):
    """Close-up van een glassed deck van boven: getinte resin, fijne schuurkrasjes in de lengte, houten stringer onder het glas,
    zachte reflectie van het raam linksboven."""
    rng = np.random.default_rng(zaad)
    kleur = hexrgb(kleur_hex)
    vlek = ruis((H, B), 0.010, 60, zaad)
    fijn = ruis((H, B), 0.005, 0.8, zaad + 1)
    kras = cv2.GaussianBlur(rng.normal(0, 1, (H, B)).astype(np.float32), (0, 0), sigmaX=0.7, sigmaY=14)
    kras = kras / (kras.std() + 1e-6) * 0.005
    img = kleur[None, None] * (1 + vlek + fijn + kras)[..., None]
    # houten stringer (3 mm): lichtbruin met nerf in de lengte, door de resin iets in de deckkleur getrokken
    xx = np.arange(B, dtype=np.float32)[None, :]
    yy = np.arange(H, dtype=np.float32)[:, None]
    rand = ruis((H, 1), 0.6, 40, zaad + 3)
    s = np.clip(14.5 - np.abs(xx - stringer_x - rand), 0, 1)
    nerf = 1 + 0.07 * np.sin((xx - stringer_x) * 1.3 + ruis((H, B), 1.5, 30, zaad + 4)) + ruis((H, B), 0.03, 2, zaad + 5)
    hout = np.array([0.70, 0.54, 0.37], np.float32)[None, None] * nerf[..., None]
    hout = hout * 0.8 + kleur[None, None] * 0.2
    img = img * (1 - s[..., None]) + hout * s[..., None]
    # randjes van de stringer: dun donker lijntje waar het hout aan het schuim grenst
    lijn = np.exp(-((np.abs(xx - stringer_x - rand) - 14.5) / 1.1) ** 2)
    img = img * (1 - 0.12 * lijn[..., None])
    # raamlicht en een zachte reflectie van het raam in het glas
    img = img * ST._licht(H, B)
    refl = np.exp(-(((xx - B * 0.22) / (B * 0.45)) ** 2 + ((yy - H * 0.18) / (H * 0.35)) ** 2))
    img = img + 0.045 * refl[..., None]
    return np.clip(img, 0, 1).astype(np.float32)


def wax_parels(B, H, gebied, zaad=7, cirkels=190):
    """Hoogteveld van verse surfwax: eerst een basislaag in kruisarcering, daarna in kleine rondjes gewreven, waardoor
    bultjes (wax beads) ontstaan. gebied: 0..1, waar de wax ligt (randen dunner)."""
    rng = np.random.default_rng(zaad)
    # basislaag: korte streken in twee schuine richtingen
    basis = np.zeros((H, B), np.float32)
    for richting in [(1, 1), (1, -1)]:
        r = np.float32(richting) / np.sqrt(2)
        for _ in range(900):
            c = np.float32([rng.uniform(0, B), rng.uniform(0, H)])
            l = rng.uniform(40, 160)
            p0, p1 = c - r * l / 2, c + r * l / 2
            cv2.line(basis, tuple(int(v) for v in p0), tuple(int(v) for v in p1), float(rng.uniform(0.4, 1.0)), int(rng.integers(2, 4)), cv2.LINE_AA)
    basis = cv2.GaussianBlur(basis, (0, 0), 1.6)
    basis = 1 - np.exp(-basis * 0.9)
    # rondjes: bultjes langs kleine cirkels, ze klonteren waar cirkels overlappen
    lagen = {3.5: np.zeros((H, B), np.float32), 6.0: np.zeros((H, B), np.float32), 9.0: np.zeros((H, B), np.float32)}
    ys, xs = np.nonzero(gebied > 0.3)
    for _ in range(cirkels):
        i = rng.integers(len(xs))
        cx, cy = xs[i], ys[i]
        straal = rng.uniform(55, 190)
        n = int(2 * np.pi * straal / rng.uniform(16, 26))
        hoek0 = rng.uniform(0, 2 * np.pi)
        boog = rng.uniform(1.2, 2.0) * np.pi
        for t in np.linspace(0, boog, n):
            x = cx + np.cos(hoek0 + t) * straal + rng.normal(0, 5)
            y = cy + np.sin(hoek0 + t) * straal * rng.uniform(0.85, 1.0) + rng.normal(0, 5)
            if 0 <= x < B and 0 <= y < H:
                k = rng.choice([3.5, 6.0, 9.0], p=[0.45, 0.4, 0.15])
                lagen[k][int(y), int(x)] += rng.uniform(0.6, 1.0)
    bult = np.zeros((H, B), np.float32)
    for sig, l in lagen.items():
        bult += cv2.GaussianBlur(l, (0, 0), sig) * (2 * np.pi * sig ** 2) * 0.55
    bult = 1 - np.exp(-bult * 1.4)
    # binnen het gebied; aan de rand minder bultjes en een dunnere basislaag
    hoogte = (0.28 * basis + bult) * gebied
    return hoogte.astype(np.float32), (basis * gebied).astype(np.float32)


def wax_op_deck(img, hoogte, basis, wax_hex, zaad=7, schaal=7.0):
    """Wax over de deck: doorschijnend, dikker = voller van kleur, satijnglans en kleine schaduwtjes naar rechtsonder."""
    H, B = hoogte.shape
    hz = cv2.GaussianBlur(hoogte, (0, 0), 1.2) * schaal
    gy, gx = np.gradient(hz)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    nl = np.clip(n @ L3, 0, 1)
    dif = (0.45 + 0.55 * nl) / (0.45 + 0.55 * L3[2])
    Hv = L3 + np.float32([0, 0, 1]); Hv /= np.linalg.norm(Hv)
    glans = np.clip(n @ Hv, 0, 1) ** 18 * 0.16
    # schaduwtjes van de bultjes op de deck en op elkaar
    dx, dy = -LICHT_NAAR * 3.0
    verschoven = cv2.warpAffine(hoogte, np.float32([[1, 0, dx], [0, 1, dy]]), (B, H))
    sch = np.clip(verschoven - hoogte, 0, 1)
    sch = cv2.GaussianBlur(sch, (0, 0), 1.5)
    wax = hexrgb(wax_hex)
    wax = wax * 0.85 + 0.15                                               # wax is lichter dan de verpakkingskleur doet vermoeden
    dekking = np.clip(0.10 + 0.8 * hoogte, 0, 0.9)
    # doorschijnend: de deck schemert erdoor, de kleur van de wax zacht verlopen
    kleur = img * (1 - dekking[..., None]) + wax[None, None] * dekking[..., None]
    kleur = cv2.GaussianBlur(kleur, (0, 0), 0.6)
    kleur = kleur * dif[..., None] * (1 - 0.35 * sch[..., None]) + glans[..., None]
    korrel = ruis((H, B), 0.012, 0.8, zaad + 9) * (hoogte > 0.05)
    return np.clip(kleur * (1 + korrel[..., None]), 0, 1)


def wax_gebied(B, H, zaad=4):
    """Organische vlek waar de wax ligt: het onderste deel en het midden, schoon deck linksboven."""
    yy, xx = np.mgrid[0:H, 0:B].astype(np.float32)
    basis = 1 / (1 + np.exp(-((yy / H - 0.30) + 0.25 * (xx / B - 0.5)) * 9))
    vorm = basis + ruis((H, B), 0.18, 70, zaad) + ruis((H, B), 0.06, 14, zaad + 1)
    return np.clip((vorm - 0.5) / 0.22 + 0.5, 0, 1).astype(np.float32)


def proef():
    doek = ST.achtergrond('baby')
    pak = wikkel_pak('koud')
    doek = ST.leg(doek, pak, breedte=1180, midden=(800, 1000), draai=0, hoogte=13, contact=0.55)
    PROEF.mkdir(parents=True, exist_ok=True)
    pad = ST.bewaar(ST.afwerking(doek), PROEF / 'gear-proef-1.jpg')
    print('proef', pad)


ACHTER = {'koud': 'baby', 'koel': 'zandpapier', 'warm': 'rose'}


def bewaar(img, naam, map_=DOEL):
    pad = ST.bewaar(ST.afwerking(img), map_ / f'{naam}.jpg')
    print('foto', pad.relative_to(ROOT))
    return pad


def surfwax(soort, shots=(1, 2, 3)):
    if 1 in shots:
        # 1: hero, één pak groot en recht van boven
        doek = ST.achtergrond(ACHTER[soort])
        doek = ST.leg(doek, wikkel_pak(soort), breedte=1320, midden=(800, 1000), hoogte=15, contact=0.6)
        bewaar(doek, f'surfwax-{soort}-1')
    if 2 in shots:
        # 2: het blok uit de wikkel onder het pak, met een paar kamgroefjes
        doek = ST.achtergrond(ACHTER[soort], zaad=2)
        rgb, a, _ = wax_blok(soort, kam=True, zaad=8)
        doek = ST.leg(doek, wikkel_pak(soort), breedte=1000, midden=(800, 655), hoogte=14, contact=0.6)
        doek = ST.leg(doek, np.dstack([rgb, a]).astype(np.float32), breedte=1000, midden=(800, 1365), hoogte=14, contact=0.6)
        bewaar(doek, f'surfwax-{soort}-2')
    if 3 in shots:
        # 3: in gebruik: close-up van de deck, verse wax in rondjes, het pak half uit de wikkel erop
        B, H = ST.B, ST.H
        img = deck(DECK[soort], stringer_x=1030, zaad=3)
        gebied = wax_gebied(B, H, zaad=5)
        hoogte, basis = wax_parels(B, H, gebied, zaad=11)
        img = wax_op_deck(img, hoogte, basis, EW.SOORTEN[soort]['kleur'])
        pak = wikkel_pak(soort, verschuif=200, gebruikt=True, zaad=9)
        img = ST.leg(img, pak, breedte=840, midden=(760, 700), hoogte=22, contact=0.6)
        bewaar(img, f'surfwax-{soort}-3')


if __name__ == '__main__':
    for stap in sys.argv[1:] or ['proef']:
        globals()[stap]()
