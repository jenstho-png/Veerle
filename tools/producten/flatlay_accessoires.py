"""Studio-productfoto's van de accessoires (pet, bucket hat, canvas tas, strandhanddoek, stickerset).

Eén stijl voor alles (stijl.py): recht van voren of recht van boven, gecentreerd, op naadloos papier of zand,
raamlicht linksboven. Basis is telkens een echte stockfoto van het blanco product op een effen achtergrond
(docs/producten/stock/flatlay/, bronnen in docs/producten/stock/bronnen.json), vrijstaand geknipt.

Gebruik: python3 tools/producten/flatlay_accessoires.py [proef|pet ...]
"""
import pathlib, sys
import cv2
import numpy as np

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import stijl as ST      # noqa: E402
import mockup as MK     # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock' / 'flatlay'
REF = ROOT / 'docs' / 'producten' / 'referentie'
ART = HIER / 'uit_echt'
DOEL = ROOT / 'docs' / 'producten' / 'beelden'
PROEF = ROOT / 'docs' / 'producten' / 'proef'
NAVY, CREME = '#22324F', '#F3ECDD'


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def art(pad, kleur=None):
    a = MK.laad_art(pad)
    if kleur:
        a = a.copy(); a[..., :3] = hexrgb(kleur)
    return a


def grabcut(img, rect, schaal=0.35, iter_=8, zeker_achter=None):
    """Product uit een effen studioachtergrond knippen. rect = (x0, y0, x1, y1) ruim om het product."""
    h, w = img.shape[:2]
    sm = cv2.resize((np.clip(img, 0, 1) * 255).astype(np.uint8), (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_AREA)
    sm = cv2.cvtColor(sm, cv2.COLOR_RGB2BGR)
    m = np.zeros(sm.shape[:2], np.uint8)
    x0, y0, x1, y1 = [int(v * schaal) for v in rect]
    bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(sm, m, (x0, y0, x1 - x0, y1 - y0), bg, fg, iter_, cv2.GC_INIT_WITH_RECT)
    fgm = ((m == 1) | (m == 3)).astype(np.float32)
    fgm = cv2.resize(fgm, (w, h), interpolation=cv2.INTER_LINEAR)
    return fgm


def verfijn_rand(masker, img, straal=6):
    """Zachte, nette rand: masker sluiten, gaten vullen, grootste stuk, lichte erosie tegen halo's."""
    m = (masker > 0.5).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    vul = m.copy(); ff = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
    cv2.floodFill(vul, ff, (0, 0), 1)
    m = m | (1 - vul)
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (straal, straal)))
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.1)


# ---------- pet ----------
def pet_basis():
    """Blanco witte snapback recht van voren (Unsplash), vrijstaand en navy gekleurd."""
    img = MK.laad(STOCK / 'pet-wit-voor-1.jpg')
    m = grabcut(img, (440, 780, 1960, 1790))
    return img, m


if __name__ == '__main__':
    stappen = sys.argv[1:] or ['proef']
    for s in stappen:
        globals()[s]()
