"""Meer productfoto's: dezelfde opgebouwde tas (scene.py) in nieuwe opstellingen.

Stap 1 (lagen): per ontwerp board + tas + band als losse laag (png met transparantie).
Stap 2 (composities): groepsfoto's, collectie-overzicht en flat lays op echte ondergronden (zand, hout, beton),
met schaduw die past bij het licht.
"""
import math, pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import scene as SC  # noqa: E402

LAGEN = ROOT / 'docs' / 'producten' / 'fabriek' / 'lagen'
UIT = ROOT / 'docs' / 'producten' / 'fotos'
STOCK = ROOT / 'docs' / 'producten' / 'stock' / 'lifestyle'
LAGEN.mkdir(parents=True, exist_ok=True)
UIT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(11)


def maak_lagen(keuze=None):
    for h, kleur in SC.TASSEN.items():
        if keuze and h not in keuze:
            continue
        stof = None if h == 'draagtas-tegel' else SC.variant_stof(h)
        beeld, a = SC.maak(stof, band=SC.hexkleur(kleur), los=True)
        ys, xs = np.where(a > 0.01)
        y0, y1, x0, x1 = ys.min() - 4, ys.max() + 5, xs.min() - 4, xs.max() + 5
        rgba = np.dstack([beeld[y0:y1, x0:x1], a[y0:y1, x0:x1]])
        Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').save(LAGEN / f'{h}.png')
        print('laag', h, rgba.shape)


def laad_laag(h):
    return np.asarray(Image.open(LAGEN / f'{h}.png')).astype(np.float32) / 255


def board_midden(laag):
    """Rij van het midden van het board in de laag (de lus valt erbuiten)."""
    rij = (laag[..., 3] > 0.5).sum(1)
    rijen = np.where(rij > rij.max() * 0.55)[0]
    return (rijen.min() + rijen.max()) / 2


def plaats(doek, laag, cx, cy, schaal, hoek, licht=(0.6, 1.0), zon=0.0, schaduw=0.32, blur=18, contact=0.25, op_board=False):
    """Leg een laag op het doek. hoek in graden (0 = board liggend, neus links).
    licht: richting waarin de schaduw valt (dx, dy). zon > 0 maakt de schaduw scherper en langer (buitenlicht)."""
    H, W = doek.shape[:2]
    lh, lw = laag.shape[:2]
    if op_board:
        # (cx, cy) is het midden van het board, niet van de laag
        dy = (board_midden(laag) - lh / 2) * schaal
        a = math.radians(hoek)
        cx, cy = cx - math.sin(a) * dy, cy - math.cos(a) * dy
    M = cv2.getRotationMatrix2D((lw / 2, lh / 2), hoek, schaal)
    M[0, 2] += cx - lw / 2
    M[1, 2] += cy - lh / 2
    w = cv2.warpAffine(laag, M, (W, H), flags=cv2.INTER_AREA if schaal < 1 else cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = w[..., 3]
    # schaduw: zacht in de studio, scherper en verder weg in de zon
    dx, dy = licht
    afstand = (14 + 30 * zon) * schaal * 2
    sch = np.roll(np.roll(a, int(dy * afstand), 0), int(dx * afstand), 1)
    sch = cv2.GaussianBlur(sch, (0, 0), max(blur * (1 - 0.7 * zon) * schaal * 2, 1.5))
    con = cv2.GaussianBlur(a, (0, 0), 3)
    doek = doek * (1 - schaduw * sch[..., None]) * (1 - contact * con[..., None])
    return doek * (1 - a[..., None]) + w[..., :3] * a[..., None]


def studiodoek(B, H, kleur=SC.DOEK):
    yy, xx = np.mgrid[0:H, 0:W_(B)].astype(np.float32) if False else np.mgrid[0:H, 0:B].astype(np.float32)
    r = np.sqrt(((xx - B * .5) / B) ** 2 + ((yy - H * .42) / H) ** 2)
    return np.array(kleur, np.float32)[None, None] * (1.03 - 0.12 * r[..., None]) + rng.normal(0, 0.004, (H, B, 1)).astype(np.float32)


def W_(b):
    return b


def textuur(naam, B, H):
    """Echte ondergrond uit de stockmap, bijgesneden en geschaald naar B x H."""
    img = np.asarray(Image.open(STOCK / naam).convert('RGB')).astype(np.float32) / 255
    h, w = img.shape[:2]
    s = max(B / w, H / h)
    img = cv2.resize(img, (int(w * s) + 1, int(h * s) + 1), interpolation=cv2.INTER_CUBIC)
    y0, x0 = (img.shape[0] - H) // 2, (img.shape[1] - B) // 2
    return img[y0:y0 + H, x0:x0 + B]


def afwerken(doek, korrel=0.01, warm=(1.0, 1.0, 1.0), vignet=0.08):
    H, B = doek.shape[:2]
    yy, xx = np.mgrid[0:H, 0:B].astype(np.float32)
    v = 1 - vignet * (((xx - B / 2) / (B / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    doek = doek * v[..., None] * np.array(warm, np.float32)
    doek = cv2.GaussianBlur(doek, (0, 0), 0.4)
    return np.clip(doek + rng.normal(0, korrel, doek.shape).astype(np.float32), 0, 1)


def bewaar(img, naam, max_kb=190):
    pad = UIT / f'{naam}.jpg'
    basis = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    for schaal in (1, 0.9, 0.8, 0.72, 0.64):
        im = basis if schaal == 1 else basis.resize((int(basis.width * schaal), int(basis.height * schaal)), Image.LANCZOS)
        for q in (88, 84, 80, 76, 72):
            im.save(pad, quality=q, optimize=True, progressive=True)
            if pad.stat().st_size < max_kb * 1000:
                return pad
    return pad


# ---------- composities ----------
def paar(namen, naam, B=2400, H=1600, achter=SC.DOEK):
    """Twee boards staand naast elkaar, de lussen naar buiten (links neus omlaag, rechts neus omhoog)."""
    doek = studiodoek(B, H, achter)
    laag0 = laad_laag(namen[0])
    schaal = H * 0.94 / laag0.shape[1]
    wb = SC.WB * schaal
    for i, h in enumerate(namen):
        laag = laad_laag(h)
        hoek = 90 if i == 0 else -90                # lus naar links resp. rechts
        cx = B / 2 + (-1 if i == 0 else 1) * (wb / 2 + 45)
        doek = plaats(doek, laag, cx, H / 2 + (12 if i else -8), schaal, hoek + (1.2 if i else -0.8), licht=(0.5, 0.8), op_board=True)
    bewaar(afwerken(doek), naam)


def stapel(namen, naam, B=1600, H=2000, achter=SC.DOEK):
    """Drie boards liggend boven elkaar, elke lus vrij erboven."""
    doek = studiodoek(B, H, achter)
    for i, h in enumerate(namen):
        laag = laad_laag(h)
        schaal = min(B * 0.92 / laag.shape[1], H / len(namen) * 0.98 / laag.shape[0])
        cy = H / len(namen) * (i + 0.5)
        doek = plaats(doek, laag, B / 2 + (i % 2) * 24 - 12, cy, schaal, (-1, 0.8, -0.5)[i % 3], licht=(0.4, 0.9), blur=12)
    bewaar(afwerken(doek), naam)


def collectie(namen, naam, B=2400, H=1600, achter=SC.DOEK):
    """Alle ontwerpen liggend onder elkaar, als in een catalogus."""
    doek = studiodoek(B, H, achter)
    kol, rij = 3, math.ceil(len(namen) / 3)
    cw, ch = B / kol, H / rij
    for i, h in enumerate(namen):
        laag = laad_laag(h)
        schaal = min(cw * 0.95 / laag.shape[1], ch * 0.95 / laag.shape[0])
        cx = cw * (i % kol + 0.5); cy = ch * (i // kol + 0.5)
        doek = plaats(doek, laag, cx, cy, schaal, 0, licht=(0.4, 0.9), blur=12)
    bewaar(afwerken(doek), naam)


def flatlay(h, naam, ondergrond, B=1600, H=2000, hoek=78, zon=0.8, schaduw=0.42, warm=(1.04, 1.0, 0.94), licht=(0.7, 0.9)):
    doek = textuur(ondergrond, B, H)
    laag = laad_laag(h)
    schaal = H * 1.02 / laag.shape[1]
    doek = plaats(doek, laag, B * 0.47, H * 0.5, schaal, hoek, licht=licht, zon=zon, schaduw=schaduw, contact=0.3)
    bewaar(afwerken(doek, korrel=0.012, warm=warm), naam)


if __name__ == '__main__':
    stap = sys.argv[1] if len(sys.argv) > 1 else 'alles'
    if stap in ('lagen', 'alles'):
        maak_lagen(sys.argv[2:] or None)
    if stap in ('composities', 'alles'):
        alle = list(SC.TASSEN)
        for f in UIT.glob('groep-*.jpg'):
            f.unlink()
        paar(['draagtas-tegel', 'draagtas-golfjes'], 'paar-tegel-golfjes')
        paar(['draagtas-schelp', 'draagtas-ruit'], 'paar-schelp-ruit')
        paar(['draagtas-salie', 'draagtas-duin'], 'paar-salie-duin')
        paar(['draagtas-tegel-navy', 'draagtas-zonsondergang'], 'paar-tegelnavy-zonsondergang')
        stapel(['draagtas-tegel', 'draagtas-zonsondergang', 'draagtas-golfjes'], 'stapel-tegel-zonsondergang-golfjes')
        stapel(['draagtas-navy', 'draagtas-schelp', 'draagtas-salie'], 'stapel-navy-schelp-salie')
        collectie(alle, 'collectie-alle-ontwerpen')
        for f in sorted(STOCK.glob('textuur-*.jpg')) if STOCK.exists() else []:
            for h in ('draagtas-tegel', 'draagtas-zonsondergang', 'draagtas-golfjes'):
                flatlay(h, f'flatlay-{f.stem.replace("textuur-", "")}-{h.replace("draagtas-", "")}', f.name)
        print('klaar')
