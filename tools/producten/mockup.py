"""Zet een print realistisch op een echte productfoto.

Werkwijze zoals bij professionele mockups:
1. De print volgt de plooien (verplaatsing op basis van de helderheid van de stof).
2. De schaduwen en lichtvlekken van de foto vallen over de print heen.
3. Een beetje van de stofstructuur komt door de print heen, zodat het gedrukt lijkt in plaats van geplakt.
Optioneel kleurt het de stof eerst om (bijvoorbeeld een witte hoodie naar baby blue), met behoud van alle schaduwen.
"""
import cv2
import numpy as np
from PIL import Image


def laad(pad):
    return np.asarray(Image.open(pad).convert('RGB')).astype(np.float32) / 255


def laad_art(pad):
    a = np.asarray(Image.open(pad).convert('RGBA')).astype(np.float32) / 255
    ys, xs = np.where(a[..., 3] > 0.02)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def helderheid(img):
    return img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114


def masker_kledingstuk(img, tolerantie=0.06, zaad=None):
    """Alles wat niet de (effen) achtergrond is. Flood fill vanaf de hoeken."""
    h, w = img.shape[:2]
    u8 = (img * 255).astype(np.uint8)
    m = np.zeros((h + 2, w + 2), np.uint8)
    t = int(tolerantie * 255)
    for x, y in zaad or [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]:
        cv2.floodFill(u8.copy(), m, (x, y), (0, 0, 0), (t, t, t), (t, t, t), cv2.FLOODFILL_MASK_ONLY | (255 << 8) | 4)
    achter = m[1:-1, 1:-1] > 0
    stuk = (~achter).astype(np.uint8)
    stuk = cv2.morphologyEx(stuk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(stuk)
    if n > 1:
        grootste = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        stuk = (lab == grootste).astype(np.uint8)
    return cv2.GaussianBlur(stuk.astype(np.float32), (0, 0), 1.2)


def kleur_om(img, masker, doel_hex, sterkte=1.0):
    """Geef de stof een nieuwe kleur; schaduwen en plooien blijven."""
    doel = np.array([int(doel_hex[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    L = helderheid(img)
    ref = np.median(L[masker > 0.5]) if (masker > 0.5).any() else 0.8
    schaduw = np.clip(L / max(ref, 1e-3), 0, 1.6)[..., None]
    nieuw = np.clip(doel[None, None, :] * schaduw, 0, 1)
    m = (masker * sterkte)[..., None]
    return img * (1 - m) + nieuw * m


def zet_print(img, art, cx, cy, breedte, draai=0.0, verplaatsing=10.0, schaduw_sterkte=0.9, structuur=0.5, dekking=0.97, masker=None):
    """Plaats art (RGBA, 0..1) gecentreerd op (cx, cy) met de gegeven breedte in pixels."""
    h, w = img.shape[:2]
    ah, aw = art.shape[:2]
    schaal = breedte / aw
    M = cv2.getRotationMatrix2D((aw / 2, ah / 2), draai, schaal)
    M[0, 2] += cx - aw / 2
    M[1, 2] += cy - ah / 2
    laag = cv2.warpAffine(art, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    L = helderheid(img)
    Lz = cv2.GaussianBlur(L, (0, 0), 6)
    gebied = laag[..., 3] > 0.05
    gem = Lz[gebied].mean() if gebied.any() else Lz.mean()
    # 1. verplaatsing: de print schuift mee met de plooien
    gx = cv2.Sobel(Lz, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(Lz, cv2.CV_32F, 0, 1, ksize=5)
    norm = max(np.abs(gx).max(), np.abs(gy).max(), 1e-6)
    mx, my = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    laag = cv2.remap(laag, mx + gx / norm * verplaatsing, my + gy / norm * verplaatsing, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    # 2. schaduw en licht van de stof over de print
    Ls = cv2.GaussianBlur(L, (0, 0), 2)
    factor = np.clip(1 + (Ls / max(gem, 1e-3) - 1) * schaduw_sterkte, 0.45, 1.35)[..., None]
    kleur = laag[..., :3] * factor
    # 3. stofstructuur door de print heen
    fijn = (L - cv2.GaussianBlur(L, (0, 0), 1.5))[..., None]
    kleur = np.clip(kleur + fijn * structuur, 0, 1)
    a = laag[..., 3:4] * dekking
    if masker is not None:
        a = a * masker[..., None]
    return img * (1 - a) + kleur * a


def naar_staand(img, achter=None, b=1600, h=2000, vul=0.88):
    """Maak er een 4:5-beeld van: product in het midden, effen aangevulde achtergrond."""
    ih, iw = img.shape[:2]
    if achter is None:
        rand = np.concatenate([img[:8].reshape(-1, 3), img[-8:].reshape(-1, 3), img[:, :8].reshape(-1, 3), img[:, -8:].reshape(-1, 3)])
        achter = np.median(rand, axis=0)
    schaal = min(b * vul / iw, h * vul / ih, b / iw, h / ih) if vul < 1 else max(b / iw, h / ih)
    nw, nh = int(iw * schaal), int(ih * schaal)
    klein = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA if schaal < 1 else cv2.INTER_LANCZOS4)
    doek = np.ones((h, w_ := b, 3), np.float32) * np.array(achter, np.float32)
    x0, y0 = (b - nw) // 2, (h - nh) // 2
    if vul >= 1:
        sx, sy = max(0, -x0), max(0, -y0)
        doek[:] = klein[sy:sy + h, sx:sx + b]
    else:
        # zachte overgang van foto naar aangevulde achtergrond
        m = np.ones((nh, nw), np.float32)
        r = int(min(nw, nh) * 0.04)
        m = cv2.GaussianBlur(cv2.copyMakeBorder(m[r:-r, r:-r], r, r, r, r, cv2.BORDER_CONSTANT, value=0), (0, 0), r / 2)[..., None]
        doek[y0:y0 + nh, x0:x0 + nw] = klein * m + doek[y0:y0 + nh, x0:x0 + nw] * (1 - m)
    return doek


def bewaar(img, pad, max_kb=190):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    q = 88
    while True:
        im.save(pad, quality=q, optimize=True, progressive=True)
        import os
        if os.path.getsize(pad) < max_kb * 1000 or q <= 55:
            break
        q -= 3
