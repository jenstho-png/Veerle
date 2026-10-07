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

BREED, LANG = 90.0, 170.0          # cm
TEGEL = 14.0                        # cm per tegel
VELD = (3.0, 15.0, 87.0, 155.0)     # tegelveld u0, v0, u1, v1 in cm
MOTIEVEN = [0, 1, 5, 6, 9, 2]       # tegels uit de stof die als jacquard goed lezen
SPIEGEL = {2: False}                # de molen (tegel 2) is alleen draaisymmetrisch


# ---------- ontwerp ----------
def motief(i, n=480):
    """Tegel uit de echte stof als zachte twee-kleurenkaart (1 = crème, 0 = navy)."""
    t = np.asarray(Image.open(FABRIEK / f'tegel-0{i}.png').convert('RGB')).astype(np.float32) / 255
    L = MK.helderheid(t)
    L = cv2.GaussianBlur(cv2.resize(L, (n, n), interpolation=cv2.INTER_CUBIC), (0, 0), n / 130)
    acc = [np.rot90(L, k) for k in range(4)]
    if SPIEGEL.get(i, True):
        acc += [np.fliplr(a) for a in acc]
    X = cv2.GaussianBlur(np.mean(acc, 0), (0, 0), n / 200)
    th = np.percentile(X, 47)
    return (X - th) / (X.std() + 1e-6)


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
    veld = np.ones((nr * tp, nk * tp), np.float32)
    for r in range(nr):
        for c in range(nk):
            i = MOTIEVEN[(r * 2 + c * 1 + (r // 2)) % len(MOTIEVEN)]
            veld[r * tp:(r + 1) * tp, c * tp:(c + 1) * tp] = _MOT[(i, tp)]
    # zachte rand tussen garens (scherpte past bij de schaal)
    scherp = 0.35 * TEGEL * ppc / 60
    a = np.clip(veld * scherp + 0.5, 0, 1)
    x0, y0 = int(round(u0 * ppc)), int(round(v0 * ppc))
    sub = img[y0:y0 + veld.shape[0], x0:x0 + veld.shape[1]]
    sub[:] = GAREN_NAVY * (1 - a[..., None]) + GAREN_CREME * a[..., None]
    # voegen tussen de tegels: dun navy
    voeg = np.zeros((H, W), np.float32)
    for k in range(nk + 1):
        voeg = np.maximum(voeg, strook(u0 + k * TEGEL - 0.12, u0 + k * TEGEL + 0.12, U) * strook(v0 - 0.12, v1 + 0.12, V))
    for k in range(nr + 1):
        voeg = np.maximum(voeg, strook(v0 + k * TEGEL - 0.12, v0 + k * TEGEL + 0.12, V) * strook(u0 - 0.12, u1 + 0.12, U))
    verf(voeg, GAREN_NAVY)
    # kader rond het veld
    kader = (strook(1.7, 2.2, U) + strook(BREED - 2.2, BREED - 1.7, U)) * strook(13.7, LANG - 13.7, V) \
        + (strook(13.7, 14.2, V) + strook(LANG - 14.2, LANG - 13.7, V)) * strook(1.7, BREED - 1.7, U)
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
