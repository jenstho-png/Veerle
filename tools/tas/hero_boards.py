"""Vrijstaande boards met draagtas voor de homepage-hero (rechtop, zonder achtergrond).

Zelfde opbouw als de productfoto's (studio2.bouw): board, stof, label en band. De lus van de band hangt naast het board.
Schrijft theme/assets/tt-hero-board-1..3.webp (met transparantie).
Gebruik: python3 tools/tas/hero_boards.py
"""
import pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER))
import studio2 as S2  # noqa: E402

THEMA = HIER.parent.parent / 'theme' / 'assets'
KEUZE = ['draagtas-golfjes', 'draagtas-tegel', 'draagtas-zonsondergang']


def los(handle, hoogte=1100):
    rb, rl = S2.bouw(handle)
    # alleen het board met de tas erom: de lus ligt in de productfoto plat naast het board en zou bij een staand
    # board opzij uitsteken
    rgba = rb
    rgba = cv2.rotate(rgba, cv2.ROTATE_90_COUNTERCLOCKWISE)            # neus omhoog
    ys, xs = np.where(rgba[..., 3] > 0.01)
    rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = hoogte / rgba.shape[0]
    rgba = cv2.resize(rgba, (round(rgba.shape[1] * s), hoogte), interpolation=cv2.INTER_AREA)
    return Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA')


if __name__ == '__main__':
    for i, h in enumerate(KEUZE, 1):
        im = los(h)
        p = THEMA / f'tt-hero-board-{i}.webp'
        im.save(p, 'WEBP', quality=86, method=6)
        print(p.name, im.size, p.stat().st_size // 1000, 'kB')
