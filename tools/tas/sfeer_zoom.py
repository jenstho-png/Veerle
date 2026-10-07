"""Controlehulp: uitsnede van een beeld, vergroot, met pixelraster en coördinaten.
python3 tools/tas/sfeer_zoom.py beeld.jpg x0 y0 x1 y1 uit.jpg [rasterstap] [maskerpng]"""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw


def zoom(pad, x0, y0, x1, y1, uit, stap=20, masker=None, max_px=1400):
    img = np.asarray(Image.open(pad).convert('RGB'))
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, img.shape[1]), min(y1, img.shape[0])
    stuk = img[y0:y1, x0:x1].copy()
    if masker:
        m = np.asarray(Image.open(masker).convert('L'))[y0:y1, x0:x1] > 127
        rand = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
        stuk[rand & m] = (255, 0, 255)
    s = max_px / max(stuk.shape[:2])
    groot = Image.fromarray(stuk).resize((int(stuk.shape[1] * s), int(stuk.shape[0] * s)), Image.NEAREST if s > 2 else Image.LANCZOS)
    d = ImageDraw.Draw(groot)
    for x in range((x0 // stap + 1) * stap, x1, stap):
        X = (x - x0) * s
        d.line([(X, 0), (X, groot.height)], fill=(0, 255, 255) if x % (stap * 5) == 0 else (0, 140, 140), width=1)
        if x % (stap * 5) == 0:
            d.text((X + 2, 2), str(x), fill=(255, 255, 0))
    for y in range((y0 // stap + 1) * stap, y1, stap):
        Y = (y - y0) * s
        d.line([(0, Y), (groot.width, Y)], fill=(0, 255, 255) if y % (stap * 5) == 0 else (0, 140, 140), width=1)
        if y % (stap * 5) == 0:
            d.text((2, Y + 2), str(y), fill=(255, 255, 0))
    groot.save(uit, quality=88)


if __name__ == '__main__':
    a = sys.argv
    zoom(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]), a[6], int(a[7]) if len(a) > 7 else 20, a[8] if len(a) > 8 else None)
