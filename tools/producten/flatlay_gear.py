"""Gear in de vaste studiostijl (stijl.py): recht van boven, gecentreerd, echt zand of naadloos papier, raamlicht linksboven.

Surfwax (koud op baby, koel op zandpapier, warm op rose):
  -1 hero: een pak groot in beeld; -2 het blok uit de wikkel onder het pak; -3 in gebruik: close-up van een pastel deck
  met stringer, verse wax in rondjes en kruisarcering (bultjes), het pak half uit de wikkel erop.
  Het blok is een echte zeepfoto van recht boven (stock/flatlay/zeep-blok-boven-1.jpg), rechtgetrokken en omgekleurd:
  matte korrel, putjes en snijsporen zijn echt. De wikkel is de artwork uit echt_wax.py (uit_wax/band-voor-<soort>.png)
  op crème papier met vezel, vlekkerigheid, vouw om de rand en kreukjes; de zijkant van het blok is net zichtbaar.
Waxkam (op zand): -1 hero; -2 detail van tanden en ingedrukt logo; -3 naast een pak surfwax.
  Steek van de tanden en de korrel van het plastic komen uit een echte kamfoto (stock/flatlay/kam-plat-voor-1.jpg).
Karabijnhaak messing (zand) en zwart (baby): -1 hero; -2 macro van lus, geweven logo, stiksel en D-ring.
  Haak, D-ring en lus uit echt.py, als vrijstaande laag (op zwart en wit opgebouwd, dekking uit het verschil).

Gebruik:
    python3 tools/producten/flatlay_gear.py                  # alles
    python3 tools/producten/flatlay_gear.py surfwax waxkam karabijn
    python3 tools/producten/flatlay_gear.py proef            # docs/producten/proef/gear-proef-1.jpg
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


def wax_blok(soort, b=1450, h=1000, zaad=3, gebruikt=False):
    """Pak-blok van boven: bovenvlak met echte korrel en een smalle zichtbare zijkant rondom. Geeft rgb, alpha, d_boven."""
    kleur = hexrgb(EW.SOORTEN[soort]['kleur'])
    sx, sy = ZIJ
    d_buiten = hapjes(rand_afstand((h, b), 0, 0, b - 1, h - 1, 26, zaad), zaad, n=4, diep=3)
    d_boven = hapjes(rand_afstand((h, b), sx, sy, b - 1 - sx, h - 1 - sy, 18, zaad + 5, ruw=0.8), zaad + 9, n=6, diep=3.5)
    if gebruikt:
        # afgesleten kant links: veel rondere hoeken
        links = (np.arange(b, dtype=np.float32)[None, :] < b / 2)
        d_buiten = np.where(links, np.minimum(d_buiten, rand_afstand((h, b), 0, 0, b - 1, h - 1, 55, zaad + 40)), d_buiten)
        d_boven = np.where(links, np.minimum(d_boven, rand_afstand((h, b), sx + 4, sy, b - 1 - sx, h - 1 - sy, 60, zaad + 41, ruw=0.8)), d_boven)
    a = np.clip(d_buiten + 0.5, 0, 1).astype(np.float32)
    boven = np.clip(d_boven + 0.5, 0, 1)
    Lv = wax_vlak(b, h)
    f_boven = Lv * schuine_rand(d_boven, 14, 0.10)
    # zijkant: gesneden wax, korrel uitgerekt langs de rand, iets ruwer
    Lz = cv2.GaussianBlur(Lv, (0, 0), sigmaX=3, sigmaY=3) * (1 + ruis((h, b), 0.03, 1.0, zaad + 3))
    f_zij = Lz * zijlicht(d_boven) * (1 - 0.05 * np.clip(1 - d_buiten / 2.5, 0, 1))   # uiterste randje iets donkerder
    f = f_boven * boven + f_zij * (1 - boven)
    yy, xx = np.mgrid[0:h, 0:b].astype(np.float32)
    if gebruikt:
        # linkerkant is al over een board gewreven: hoeken rond, vlak licht glimmend met strepen in de wrijfrichting
        slijt = np.clip(1 - xx / (b * 0.32), 0, 1) ** 1.5 * boven
        streep = cv2.GaussianBlur(np.random.default_rng(zaad + 30).normal(0, 1, (h, b)).astype(np.float32), (0, 0), sigmaX=4, sigmaY=6)
        streep = streep / (streep.std() + 1e-6)
        f = f * (1 + slijt * (0.03 + 0.008 * streep))
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
        for _ in range(1500):
            c = np.float32([rng.uniform(0, B), rng.uniform(0, H)])
            l = rng.uniform(25, 90)
            p0, p1 = c - r * l / 2, c + r * l / 2
            cv2.line(basis, tuple(int(v) for v in p0), tuple(int(v) for v in p1), float(rng.uniform(0.3, 0.8)), int(rng.integers(3, 6)), cv2.LINE_AA)
    basis = cv2.GaussianBlur(basis, (0, 0), 2.6)
    basis = 1 - np.exp(-basis * 0.9)
    # rondjes: bultjes langs kleine cirkels, ze klonteren waar cirkels overlappen
    lagen = {4.5: np.zeros((H, B), np.float32), 7.5: np.zeros((H, B), np.float32), 12.0: np.zeros((H, B), np.float32)}
    ys, xs = np.nonzero(gebied > 0.3)
    for _ in range(cirkels):
        i = rng.integers(len(xs))
        cx, cy = xs[i], ys[i]
        straal = rng.uniform(55, 190)
        n = int(2 * np.pi * straal / rng.uniform(12, 20))
        hoek0 = rng.uniform(0, 2 * np.pi)
        boog = rng.uniform(1.2, 2.0) * np.pi
        for t in np.linspace(0, boog, n):
            x = cx + np.cos(hoek0 + t) * straal + rng.normal(0, 5)
            y = cy + np.sin(hoek0 + t) * straal * rng.uniform(0.85, 1.0) + rng.normal(0, 5)
            if 0 <= x < B and 0 <= y < H:
                k = rng.choice([4.5, 7.5, 12.0], p=[0.4, 0.42, 0.18])
                lagen[k][int(y), int(x)] += rng.uniform(0.6, 1.0)
    bult = np.zeros((H, B), np.float32)
    for sig, l in lagen.items():
        bult += cv2.GaussianBlur(l, (0, 0), sig) * (2 * np.pi * sig ** 2) * 0.55
    bult = 1 - np.exp(-bult * 1.4)
    # binnen het gebied; aan de rand minder bultjes en een dunnere basislaag
    dik = 0.75 + ruis((H, B), 0.25, 45, zaad + 2)
    hoogte = (0.18 * basis + bult * dik) * gebied
    return hoogte.astype(np.float32), (basis * gebied).astype(np.float32)


def wax_op_deck(img, hoogte, basis, wax_hex, zaad=7, schaal=11.0):
    """Wax over de deck: doorschijnend, dikker = voller van kleur, satijnglans en kleine schaduwtjes naar rechtsonder."""
    H, B = hoogte.shape
    hz = cv2.GaussianBlur(hoogte, (0, 0), 1.2) * schaal
    gy, gx = np.gradient(hz)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    nl = np.clip(n @ L3, 0, 1)
    dif = (0.38 + 0.62 * nl) / (0.38 + 0.62 * L3[2])
    Hv = L3 + np.float32([0, 0, 1]); Hv /= np.linalg.norm(Hv)
    glans = np.clip(n @ Hv, 0, 1) ** 9 * 0.07
    # schaduwtjes van de bultjes op de deck en op elkaar
    dx, dy = -LICHT_NAAR * 3.0
    verschoven = cv2.warpAffine(hoogte, np.float32([[1, 0, dx], [0, 1, dy]]), (B, H))
    sch = np.clip(verschoven - hoogte, 0, 1)
    sch = cv2.GaussianBlur(sch, (0, 0), 1.5)
    wax = hexrgb(wax_hex)
    wax = np.clip(wax + (wax - wax.mean()) * 0.6, 0, 1)                                               # wax is lichter dan de verpakkingskleur doet vermoeden
    dekking = np.clip(0.10 + 0.62 * hoogte, 0, 0.72)
    # onder de wax is de deck (en de stringer) iets onscherp
    onder = cv2.GaussianBlur(img, (0, 0), 1.8)
    w = np.clip(hoogte * 3, 0, 1)[..., None]
    img = img * (1 - w) + onder * w
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
    doek = achtergrond('baby')
    pak = wikkel_pak('koud')
    doek = ST.leg(doek, pak, breedte=1180, midden=(800, 1000), draai=0, hoogte=13, contact=0.55)
    PROEF.mkdir(parents=True, exist_ok=True)
    pad = ST.bewaar(ST.afwerking(doek), PROEF / 'gear-proef-1.jpg')
    print('proef', pad)


ACHTER = {'koud': 'baby', 'koel': 'zandpapier', 'warm': 'rose'}


def achtergrond(soort, zaad=1):
    """stijl.achtergrond; het zand iets ontruisd (zandkorrels kosten veel bytes), zoals tools/tas/studio2.py."""
    doek = ST.achtergrond(soort, zaad=zaad)
    if soort == 'zand':
        u8 = cv2.cvtColor((np.clip(doek, 0, 1) * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR)
        doek = cv2.cvtColor(cv2.fastNlMeansDenoisingColored(u8, None, 5, 14, 5, 15), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    return doek


def bewaar(img, naam, map_=DOEL, max_kb=190):
    """1600 x 2000 onder 190 kB: stijl.afwerking, dan de kwaliteit omlaag; past het niet, eerst wat kleurruis eruit."""
    from PIL import Image
    pad = map_ / f'{naam}.jpg'
    u8 = (np.clip(ST.afwerking(img), 0, 1) * 255 + 0.5).astype(np.uint8)
    for h, hk, qs in ((0, 0, range(88, 55, -3)), (2, 8, range(70, 45, -2)), (3, 10, range(56, 39, -2))):
        b = u8 if not h else cv2.cvtColor(cv2.fastNlMeansDenoisingColored(cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), None, h, hk, 5, 15),
                                          cv2.COLOR_BGR2RGB)
        im = Image.fromarray(b)
        for q in qs:
            im.save(pad, quality=q, optimize=True, progressive=True)
            if pad.stat().st_size < max_kb * 1000:
                print('foto', pad.relative_to(ROOT), f'q{q}' + (f' ontruis{h}' if h else ''), pad.stat().st_size // 1000, 'kB')
                return pad
    print('foto', pad.relative_to(ROOT), 'TE GROOT', pad.stat().st_size // 1000, 'kB')
    return pad


def surfwax(soort, shots=(1, 2, 3)):
    if 1 in shots:
        # 1: hero, één pak groot en recht van boven
        doek = achtergrond(ACHTER[soort])
        doek = ST.leg(doek, wikkel_pak(soort), breedte=1320, midden=(800, 1000), hoogte=15, contact=0.6)
        bewaar(doek, f'surfwax-{soort}-1')
    if 2 in shots:
        # 2: het blok uit de wikkel onder het pak
        doek = achtergrond(ACHTER[soort], zaad=2)
        rgb, a, _ = wax_blok(soort, zaad=8)
        doek = ST.leg(doek, wikkel_pak(soort), breedte=1000, midden=(800, 655), hoogte=14, contact=0.6)
        doek = ST.leg(doek, np.dstack([rgb, a]).astype(np.float32), breedte=1000, midden=(800, 1365), hoogte=14, contact=0.6)
        bewaar(doek, f'surfwax-{soort}-2')
    if 3 in shots:
        # 3: in gebruik: close-up van de deck, verse wax in rondjes, het pak half uit de wikkel erop
        B, H = ST.B, ST.H
        img = deck(DECK[soort], stringer_x=1030, zaad=3)
        gebied = wax_gebied(B, H, zaad=5)
        hoogte, basis = wax_parels(B, H, gebied, zaad=11, cirkels=420)
        img = wax_op_deck(img, hoogte, basis, EW.SOORTEN[soort]['kleur'])
        pak = wikkel_pak(soort, verschuif=200, gebruikt=True, zaad=9)
        img = ST.leg(img, pak, breedte=880, midden=(800, 760), hoogte=22, contact=0.6)
        bewaar(img, f'surfwax-{soort}-3')


# ---------- waxkam ----------
# kam-plat-voor-1.jpg (4000 x 5600): plat plastic kammetje recht van voren. Sleufjes (midden) van x 1128 tot 2701,
# steek ca. 75 px; de sleufjes beginnen op y ca. 2752, de tanden eindigen op y ca. 4570.
KAM_X0, KAM_X1 = 1128, 2701
TERRA = '#C0603E'


def kam_textuur(img, b, h, zaad=12, n=48):
    """Korrel van het echte plastic (b x h, rond 1). Het gemiddelde ruisspectrum van veel kleine vlakjes effen plastic
    (links en rechts naast de sleufjes) wordt op nieuwe ruis gezet: dezelfde korrel, zonder naden of herhaling."""
    L = MK.helderheid(img)
    detail = L / np.maximum(cv2.GaussianBlur(L, (0, 0), 8), 1e-3) - 1
    spec = np.zeros((n, n), np.float32)
    tel = 0
    venster = np.outer(np.hanning(n), np.hanning(n)).astype(np.float32)   # geen lekstrepen langs de assen
    for sx0, sx1 in [(1052, 1108), (2722, 2790)]:
        for y in range(2850, 4300 - n, n // 2):
            for x in range(sx0, sx1 - n + 1, 8):
                stuk = detail[y:y + n, x:x + n]
                spec += np.abs(np.fft.fft2((stuk - stuk.mean()) * venster)) ** 2
                tel += 1
    filt = np.sqrt(spec / tel)
    kern = np.real(np.fft.fftshift(np.fft.ifft2(filt))).astype(np.float32)
    kern /= np.sqrt((kern ** 2).sum())
    wit = np.random.default_rng(zaad).normal(0, 1, (h, b)).astype(np.float32)
    korrel = cv2.filter2D(wit, -1, kern, borderType=cv2.BORDER_REFLECT)
    stuk = detail[2850:4300, 1060:1100]
    doel = float(1.4826 * np.median(np.abs(stuk - np.median(stuk))))         # robuust: zonder randjes en stofjes
    korrel = korrel / (korrel.std() + 1e-6) * doel
    return (1 + korrel + ruis((h, b), 0.008, 50, zaad + 1)).astype(np.float32)


def logo_masker(breedte):
    """Liggend Tide Tode-logo uit de wikkel-artwork (navy op crème) als masker."""
    art = EW.art('band-zij-koud')
    stuk = art[80:190, :, :3]
    m = np.clip((0.55 - MK.helderheid(stuk)) / 0.2, 0, 1)
    ys, xs = np.where(m > 0.1)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h = int(round(m.shape[0] * breedte / m.shape[1]))
    return cv2.resize(m, (breedte, h), interpolation=cv2.INTER_AREA)


KAM_SLEUF = [1128, 1199, 1271, 1344, 1420, 1494, 1566, 1639, 1713, 1791, 1870, 1948, 2023, 2106, 2181, 2258, 2329, 2404, 2479, 2554, 2628, 2701]


def waxkam(hoogte_verhouding=0.62, tand_lengte=215, tand_breedte=44):
    """Waxkam met schraper: plat terracotta plastic, tanden onder, rechte schraaprand boven, logo licht in het plastic
    gedrukt. Steek en lichtverloop van de tanden en de korrel van het plastic komen uit de echte kamfoto.
    Geeft RGBA (float32), ca. 16 px per mm."""
    img = MK.laad(FLAT / 'kam-plat-voor-1.jpg')
    hsv = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    S = hsv[..., 1].astype(np.float32)
    W = KAM_X1 - KAM_X0
    H = int(round(W * hoogte_verhouding))
    k = 4                                                     # vorm 4x zo fijn tekenen, dan verkleinen (gladde randen)
    m = np.zeros((H * k, W * k), np.uint8)
    y_wortel = H - tand_lengte
    cv2.rectangle(m, (0, 0), (W * k - 1, (y_wortel + 2) * k), 255, -1)
    r = tand_breedte / 2
    for i in range(len(KAM_SLEUF) - 1):
        c = (KAM_SLEUF[i] + KAM_SLEUF[i + 1]) / 2 - KAM_X0
        x0, x1 = int((c - r) * k), int((c + r) * k)
        cv2.rectangle(m, (x0, y_wortel * k), (x1, int((H - r) * k)), 255, -1)
        cv2.circle(m, (int(c * k), int((H - r) * k)), int(r * k), 255, -1, cv2.LINE_AA)
    # binnenhoeken tussen tand en lijf afronden (spuitgietwerk heeft nooit scherpe hoeken)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13 * k, 13 * k)))
    alpha = cv2.resize(m.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    # afgeronde bovenhoeken en een net niet kaarsrechte buitenrand
    d = rand_afstand((H, W), 0, 0, W - 1, H + 200, 46, 31, ruw=0.6)
    alpha = alpha * np.clip(d + 0.5, 0, 1)
    # licht: echte korrel, rand afgeschuind, punten van de tanden met het echte verloop
    L = kam_textuur(img, W, H)
    L = 1 + (L - 1) * 0.9
    dt = cv2.distanceTransform((alpha > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    L = L * schuine_rand(np.minimum(dt, np.clip(d, 0, None)), 9, 0.15)
    # zachte glans van het raam op het gladde plastic
    yy0, xx0 = np.mgrid[0:H, 0:W].astype(np.float32)
    L = L * (1.03 - 0.06 * (xx0 / W * 0.5 + yy0 / H * 0.5))
    # schraaprand boven: smalle facet die het licht vangt
    yy = np.arange(H, dtype=np.float32)[:, None]
    L = L * (1 + 0.09 * np.exp(-((yy - 9) / 3.5) ** 2) - 0.04 * np.exp(-((yy - 18) / 3) ** 2))
    # logo in het plastic gedrukt (ca. 0,3 mm diep): binnenrand linksboven in de schaduw, rechtsonder licht
    lm = logo_masker(int(W * 0.52))
    lh, lw = lm.shape
    ly = int(y_wortel * 0.48 - lh / 2)
    lx = (W - lw) // 2
    diep = np.zeros((H, W), np.float32)
    diep[ly:ly + lh, lx:lx + lw] = lm
    h_ = -cv2.GaussianBlur(diep, (0, 0), 1.6) * 3.0
    gy, gx = np.gradient(h_)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    relief = np.clip(n @ L3, 0, 1) / L3[2]
    L = L * (1 + (relief - 1) * 0.9) * (1 - 0.035 * cv2.GaussianBlur(diep, (0, 0), 1.0))
    kleur = hexrgb(TERRA)
    rgb = np.clip(kleur[None, None] * (0.93 * np.clip(L, 0.3, 1.3))[..., None] ** 1.05, 0, 1)
    return np.dstack([rgb, alpha]).astype(np.float32)


def waxkam_fotos():
    kam = waxkam()
    # 1: hero, recht van boven, groot in het midden
    doek = achtergrond('zand')
    doek = ST.leg(doek, kam, breedte=1240, midden=(800, 1000), hoogte=7, contact=0.6)
    bewaar(doek, 'waxkam-1')
    # 2: detail van de tanden en het ingedrukte logo
    doek = achtergrond('zand', zaad=3)
    doek = ST.leg(doek, kam, breedte=2700, midden=(1000, 780), hoogte=14, contact=0.6)
    bewaar(doek, 'waxkam-2')
    # 3: naast een pak surfwax (echte maten: pak 85 mm, kam 95 mm)
    doek = achtergrond('zand', zaad=4)
    doek = ST.leg(doek, wikkel_pak('koel'), breedte=930, midden=(800, 640), hoogte=14, contact=0.6)
    doek = ST.leg(doek, kam, breedte=1040, midden=(800, 1400), hoogte=7, contact=0.6)
    bewaar(doek, 'waxkam-3')


# ---------- karabijnhaak ----------
# buitenrand van het metaal langs neus en schroefsluiting (rechtsonder) op karabiner-zilver-1.jpg
KARABIJN_RAND = [(1208, 500), (1203, 600), (1192, 650), (1162, 690), (1132, 730), (1108, 770), (1101, 800),
                 (1045, 858), (987, 914), (967, 935), (902, 994), (860, 1032)]
D_RING = 340          # D-ring: 27 mm breed (binnenmaat voor 25 mm band), draad 2 mm
KARABIJN = {
    # naam: donker metaal, licht metaal, gamma, band, garen (stiksel), tekst (geweven logo), achtergrond
    'messing': ([0.42, 0.29, 0.1], [1.0, 0.88, 0.58], 1.15, '#22324F', '#C0603E', '#DCD3C2', 'zand'),
    'zwart': ([0.05, 0.055, 0.065], [0.62, 0.64, 0.68], 2.2, '#67809F', '#F3ECDD', '#22324F', 'baby'),
}


def karabijn_rgba(naam):
    """De karabijnhaak uit echt.karabijn() (gegoten logo, D-ring, lus van tasband) als vrijstaande laag.
    We bouwen hem twee keer op: op zwart en op wit. Het verschil geeft de dekking; de schaduwen die echt.py op de oude
    witte fotoachtergrond tekende, rekenen we eruit (ze zijn glad), zodat stijl.leg de schaduw van de studio geeft."""
    donker, licht, gamma, band, garen, tekst, _ = KARABIJN[naam]
    k = E.foto('karabiner-zilver-1.jpg')
    m = E.omkleur_masker(k, 0.15, (800, 589), vullen=False, sluit=81)
    L = MK.helderheid(k)
    # het masker neemt rechtsonder van de neus en de schroefsluiting de grijze slagschaduw van de oude fotoachtergrond
    # mee (band van 40 tot 50 px). Gemeten buitenrand van het metaal daar; alles erbuiten hoort niet bij de haak.
    rand = np.float32(KARABIJN_RAND)
    weg = np.zeros_like(m, np.uint8)
    cv2.fillPoly(weg, [np.int32(np.concatenate([rand, (rand + 110)[::-1]]))], 1)
    m = m * (1 - cv2.GaussianBlur(weg.astype(np.float32), (0, 0), 0.8))
    t = np.clip(L, 0, 1) ** gamma
    metaal = np.array(donker)[None, None] + (np.array(licht) - np.array(donker))[None, None] * t[..., None]
    glim = np.clip((L - 0.965) / 0.03, 0, 1)[..., None]
    spec = np.array(licht) * 0.25 + 0.75 if naam == 'messing' else np.array([0.9, 0.92, 0.95])
    metaal = metaal * (1 - glim) + spec[None, None] * glim
    cnts, _ = cv2.findContours((m > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    romp = np.zeros_like(m); cv2.fillPoly(romp, [cv2.convexHull(np.vstack(cnts))], 1)
    romp = cv2.erode(romp, np.ones((9, 9), np.uint8))
    grijs = (L < 0.935) & (cv2.dilate((m > 0.5).astype(np.uint8), np.ones((61, 61), np.uint8)) > 0)
    glans = cv2.morphologyEx((romp * grijs).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)).astype(np.float32)
    # glimlichten die het masker mist horen bij het metaal, maar alleen binnen de buis: de grijze slagschaduw van de
    # oude fotoachtergrond net naast het metaal niet (anders een lichte rand om de haak)
    binnen = cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    binnen = cv2.erode(binnen, np.ones((3, 3), np.uint8)).astype(np.float32)
    zone = np.maximum(m, cv2.GaussianBlur(glans * binnen, (0, 0), 1.2))
    uit = (k * (1 - zone[..., None]) + metaal * zone[..., None]).astype(np.float32)
    uit = E.gegoten_logo(uit, m, 760, 600, 250, 29.2, sterkte=1.0 if naam == 'messing' else 1.4)
    L0, B0, CW_, CH_ = 1350, 250, 3300, 3300
    hm = np.zeros((CH_, CW_), np.float32); hm[B0:B0 + m.shape[0], L0:L0 + m.shape[1]] = np.maximum(m, 0)
    za = np.zeros((CH_, CW_), np.float32); za[B0:B0 + m.shape[0], L0:L0 + m.shape[1]] = zone
    zc = np.zeros((CH_, CW_, 3), np.float32); zc[B0:B0 + m.shape[0], L0:L0 + m.shape[1]] = uit
    # lus recht in het verlengde van de haak (lange as uit het masker), vanaf het verste punt van de onderste bocht
    ys, xs = np.nonzero(m > 0.5)
    pts = np.stack([xs, ys], 1).astype(np.float32)
    mid = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - mid, full_matrices=False)
    r = vt[0] if vt[0][1] > 0 else -vt[0]                 # naar beneden
    proj = (pts - mid) @ r
    eind = pts[proj > proj.max() - 6].mean(0)            # buitenkant van de onderste staaf, op de as
    # binnenkant van de staaf: langs de as terug tot de opening van de haak begint
    t = 0
    while m[int(round(eind[1] - r[1] * t)), int(round(eind[0] - r[0] * t))] > 0.5 or t < 20:
        t += 1
    staaf = t                                             # dikte van de staaf langs de as (px)
    # D-ring door de haak: de boog komt in de opening boven de staaf uit (ca. 3,5 mm), loopt onder de staaf door,
    # en de rechte kant (waar de lus omheen genaaid is) ligt ca. 2,5 mm onder de staaf
    hb = D_RING / 2
    top = eind - r * (staaf + 45)
    Sd = top + r * hb + np.array([L0, B0])
    lagen = []
    for grond in (0.0, 1.0):
        doek = zc * za[..., None] + grond * (1 - za[..., None])
        voor = doek.copy()
        doek = E.d_ring(doek, hm, Sd, r, D_RING, 26, donker, licht)
        if grond == 0.0:
            ring = np.clip((doek - voor).max(-1) / 0.03, 0, 1) * (1 - hm)
        # contactschaduw: waar de staaf over de ring ligt wordt de ring vlak naast de staaf donker
        afst = cv2.distanceTransform((hm < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        ao = ring * np.exp(-afst / 7.0) * 0.55
        doek = doek * (1 - ao[..., None])
        doek = E.bandlabel(doek, tuple(Sd), tuple(r), 1450, 280, band, garen, tekst, buig=0.0, R=13)
        lagen.append(doek)
    P, Wt = lagen
    verschil = (Wt - P).mean(-1)                         # = (1 - dekking) x schaduw op de achtergrond
    zeker_buiten = cv2.erode((verschil > 0.45).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
    sch = cv2.GaussianBlur(verschil * zeker_buiten, (0, 0), 14) / np.maximum(cv2.GaussianBlur(zeker_buiten, (0, 0), 14), 1e-4)
    sch = np.where(zeker_buiten > 0, verschil, np.clip(sch, 0.3, 1))
    a = np.clip(1 - verschil / np.maximum(sch, 1e-3), 0, 1)
    a = np.where(a < 0.03, 0, a)
    kleur = np.clip(P / np.maximum(a[..., None], 1e-3), 0, 1)
    rgba = np.dstack([kleur, a]).astype(np.float32)
    # rechtop draaien: lange as (de lus) recht naar beneden
    hoek = float(np.degrees(np.arctan2(r[0], r[1])))
    return rond_af(roteer(rgba, -hoek)), Sd, r


def rond_af(rgba):
    """Kleur net buiten de rand doortrekken (geen donkere randjes bij het schalen) en bijsnijden op het product."""
    a = rgba[..., 3]
    som = cv2.GaussianBlur(rgba[..., :3] * a[..., None], (0, 0), 3)
    gew = cv2.GaussianBlur(a, (0, 0), 3)[..., None]
    vul = som / np.maximum(gew, 1e-4)
    kleur = np.where(a[..., None] > 0.98, rgba[..., :3], rgba[..., :3] * a[..., None] + vul * (1 - a[..., None]))
    ys, xs = np.where(a > 0.02)
    y0, y1, x0, x1 = max(ys.min() - 4, 0), ys.max() + 5, max(xs.min() - 4, 0), xs.max() + 5
    return np.dstack([np.clip(kleur, 0, 1), a])[y0:y1, x0:x1].astype(np.float32)


def roteer(rgba, hoek):
    """Draai een RGBA-laag (voorvermenigvuldigd, geen randjes) met een doek dat groot genoeg is."""
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), hoek, 1.0)
    c, s_ = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * s_ + w * c) + 2, int(h * c + w * s_) + 2
    M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
    pm = rgba.copy(); pm[..., :3] *= pm[..., 3:4]
    uit = cv2.warpAffine(pm, M, (nw, nh), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
    uit[..., 3] = np.clip(uit[..., 3], 0, 1)
    uit[..., :3] = np.clip(uit[..., :3] / np.maximum(uit[..., 3:4], 1e-4), 0, 1)
    return uit


def karabijn_fotos(naam, rgba=None):
    if rgba is None:
        rgba, _, _ = karabijn_rgba(naam)
    rgba = rond_af(rgba)
    achter = KARABIJN[naam][6]
    h, w = rgba.shape[:2]
    # 1: hero van de haak zelf: groot en in het midden, gegoten logo en schroefsluiting goed te zien;
    #    D-ring en het begin van de lus eronder, de lus loopt onderaan uit beeld
    doek = achtergrond(achter)
    schaal = 1400 / (h * 0.37)                                # haak (ca. 37 procent van de lengte) ca. 1450 px hoog
    midden_laag = h * 0.185                                   # midden van de haak, iets boven het midden van de foto
    doek = ST.leg(doek, rgba, breedte=w * schaal, midden=(800, 870 + (h / 2 - midden_laag) * schaal), hoogte=16, contact=0.55)
    bewaar(doek, f'karabijnhaak-{naam}-1')
    # 2: het hele product van boven: haak, D-ring en de lus van 12 cm, recht onder elkaar
    doek = achtergrond(achter, zaad=2)
    doek = ST.leg(doek, rgba, breedte=w * 1700 / h, midden=(800, 1000), hoogte=9, contact=0.55)
    bewaar(doek, f'karabijnhaak-{naam}-2')
    # 3: macro van de band: geweven logo, stiksel en de D-ring bovenaan
    doek = achtergrond(achter, zaad=5)
    schaal = 2.3 * 1700 / h
    d_y = 0.55 * h
    doek = ST.leg(doek, rgba, breedte=w * schaal, midden=(800, 1000 + (h / 2 - d_y) * schaal), hoogte=16, contact=0.55)
    bewaar(doek, f'karabijnhaak-{naam}-3')
    return rgba


if __name__ == '__main__':
    stappen = sys.argv[1:] or ['surfwax', 'waxkam', 'karabijn']
    for stap in stappen:
        if stap == 'surfwax':
            for soort in ACHTER:
                surfwax(soort)
        elif stap == 'waxkam':
            waxkam_fotos()
        elif stap == 'karabijn':
            for naam in KARABIJN:
                karabijn_fotos(naam)
        else:
            globals()[stap]()
