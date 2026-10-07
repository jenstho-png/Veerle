"""Studiofoto van de draagtas, gemaakt uit de echte fabrieksfoto (fotobewerking, geen AI).

1. Knip board, tas en schouderband uit de foto (vloer, losse mosterdbanden en stickers eruit).
2. Knip de losse bandeinden af bij de onderrand van het vak, zodat de band daar eindigt.
3. Zet alles op een effen studioachtergrond met een zachte schaduw.
4. Optioneel: vervang de stof in het vak door een ander patroon; weefstructuur, plooien en band blijven echt.
"""
import pathlib
import cv2
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).parent.parent.parent
FOTO = ROOT / 'docs' / 'producten' / 'fabriek' / 'fabrieksfoto.jpg'

# gemeten in de fabrieksfoto (2000 x 1126)
PANEEL = np.array([[770, 444], [1243, 444], [1468, 976], [590, 976]], np.float32)   # linksboven, rechtsboven, rechtsonder, linksonder
ONDERRAND = 978          # onder deze lijn hangen de losse bandeinden
UITSNEDE = (430, 0, 1837, 1126)


def laad():
    return cv2.cvtColor(cv2.imread(str(FOTO)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def maskers(img):
    h, w = img.shape[:2]
    hsv = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    H, S, V = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    yy, xx = np.mgrid[0:h, 0:w]
    # board: licht en weinig verzadigd, tussen de rails
    board = (V > 0.62) & (S < 0.32) & (yy > 330) & (yy < 965)
    board = cv2.morphologyEx(board.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    # gaten (stickers, stringer) dichten: vul alles binnen de buitenrand
    cnt, _ = cv2.findContours(board, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    board = np.zeros_like(board)
    if cnt:
        cv2.drawContours(board, [max(cnt, key=cv2.contourArea)], -1, 1, -1)
    # vak met de stof
    paneel = np.zeros((h, w), np.uint8)
    cv2.fillPoly(paneel, [PANEEL.astype(np.int32)], 1)
    # schouderband: blauwgrijs, alleen boven de onderrand van het vak
    band = (H > 95) & (H < 125) & (S > 0.18) & (V > 0.35) & (yy < ONDERRAND)
    band = cv2.morphologyEx(band.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    band = cv2.morphologyEx(band, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(band)
    if n > 1:
        band = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    alles = np.clip(board + paneel + band, 0, 1)
    return board, paneel, band, alles


def kloon(img, doel, bron, zacht=12):
    """Kopieer een stuk board over een sticker heen, met zachte randen."""
    x, y, w, h = doel
    bx, by = bron
    m = np.zeros((h, w), np.float32)
    m[zacht:-zacht, zacht:-zacht] = 1
    m = cv2.GaussianBlur(m, (0, 0), zacht / 2)[..., None]
    img[y:y + h, x:x + w] = img[by:by + h, bx:bx + w] * m + img[y:y + h, x:x + w] * (1 - m)


def studio(img, alles, achter=(0.93, 0.905, 0.86), schaduw=0.28):
    h, w = img.shape[:2]
    a = cv2.GaussianBlur(alles.astype(np.float32), (0, 0), 0.9)
    # achtergrond met een licht verloop zoals een studiodoek
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w * 0.5) / w) ** 2 + ((yy - h * 0.45) / h) ** 2)
    doek = np.array(achter, np.float32)[None, None, :] * (1.03 - 0.12 * r[..., None])
    # zachte schaduw onder het board
    s = cv2.GaussianBlur(alles.astype(np.float32), (0, 0), 22)
    s = np.roll(np.roll(s, 14, axis=0), 8, axis=1)
    contact = cv2.GaussianBlur(alles.astype(np.float32), (0, 0), 4)
    doek = doek * (1 - schaduw * s[..., None]) * (1 - 0.18 * contact[..., None])
    return img * a[..., None] + doek * (1 - a[..., None])


def maak(patroon=None):
    img = laad()
    board, paneel, band, alles = maskers(img)
    kloon(img, (430, 590, 205, 115), (1520, 590))      # ONAMI-sticker
    if patroon is not None:
        img = vervang_stof(img, paneel, band, patroon)
    uit = studio(img, alles)
    x0, y0, x1, y1 = UITSNEDE
    uit = uit[y0:y1, x0:x1]
    uit = cv2.rotate(uit, cv2.ROTATE_90_CLOCKWISE)        # board staand, neus boven
    return uit


def vervang_stof(img, paneel, band, patroon_rgb):
    """Leg een nieuw patroon (vlak, RGB 0..1) in het vak; behoud weefstructuur en licht van de echte stof."""
    h, w = img.shape[:2]
    ph, pw = patroon_rgb.shape[:2]
    bron = np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]])
    M = cv2.getPerspectiveTransform(bron, PANEEL)
    nieuw = cv2.warpPerspective(patroon_rgb, M, (w, h), flags=cv2.INTER_LANCZOS4)
    L = img[..., 0] * .299 + img[..., 1] * .587 + img[..., 2] * .114
    grof = cv2.GaussianBlur(L, (0, 0), 18)
    fijn = L - cv2.GaussianBlur(L, (0, 0), 1.6)
    licht = np.clip(grof / max(np.median(grof[paneel > 0]), 1e-3), 0.75, 1.2)
    stof = np.clip(nieuw * licht[..., None] + fijn[..., None] * 0.9, 0, 1)
    m = cv2.GaussianBlur(paneel.astype(np.float32), (0, 0), 0.8) * (1 - cv2.GaussianBlur(band.astype(np.float32), (0, 0), 0.8))
    return img * (1 - m[..., None]) + stof * m[..., None]


def bewaar(img, pad, breed=1600, hoog=2000, achter=(0.93, 0.905, 0.86)):
    h, w = img.shape[:2]
    schaal = min(breed / w, hoog / h)
    klein = cv2.resize(img, (int(w * schaal), int(h * schaal)), interpolation=cv2.INTER_AREA)
    doek = np.ones((hoog, breed, 3), np.float32) * np.array(achter, np.float32) * 0.985
    y = (hoog - klein.shape[0]) // 2; x = (breed - klein.shape[1]) // 2
    doek[y:y + klein.shape[0], x:x + klein.shape[1]] = klein
    Image.fromarray((np.clip(doek, 0, 1) * 255).astype(np.uint8)).save(pad, quality=90)


if __name__ == '__main__':
    uit = maak()
    bewaar(uit, ROOT / 'docs' / 'producten' / 'fabriek' / 'studio-tegel.jpg')
    print('klaar')
