"""Maakt een schone lap van de echte jacquardstof uit de fabrieksfoto.
De band ligt over een deel van de tegels; we knippen de vrije tegels uit en leggen ze opnieuw in een raster."""
import pathlib, random
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).parent.parent.parent
FOTO = ROOT / 'docs' / 'producten' / 'fabriek' / 'fabrieksfoto.jpg'
UIT = ROOT / 'docs' / 'producten' / 'fabriek'
OX, OY = 560, 420           # uitsnede-offset in de foto
TW, TH = 98, 115            # tegelmaat in pixels
KOL = [297, 394, 492, 590]  # tegelnaden in de uitsnede (gemeten)
RIJ = [52, 167, 281, 397]
# tegels die helemaal vrij zijn van de band (kolom, rij)
VRIJ = [(1, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3), (2, 3), (3, 3)]
IN = 3                      # een paar pixels binnen de naad knippen

foto = Image.open(FOTO).convert('RGB')
tegels = [foto.crop((OX + KOL[k] + IN, OY + RIJ[r] + IN, OX + KOL[k] + TW - IN, OY + RIJ[r] + TH - IN)).resize((TW, TH), Image.LANCZOS) for k, r in VRIJ]
for i, t in enumerate(tegels):
    t.save(UIT / f'tegel-{i:02d}.png')


def lap(kolommen, rijen, zaad=7, schaal=2):
    """Een nieuwe lap stof: tegels zonder twee dezelfde naast of onder elkaar."""
    rnd = random.Random(zaad)
    raster = [[None] * kolommen for _ in range(rijen)]
    for r in range(rijen):
        for k in range(kolommen):
            buren = {raster[r - 1][k] if r else None, raster[r][k - 1] if k else None, raster[r - 1][k - 1] if r and k else None, raster[r - 1][k + 1] if r and k + 1 < kolommen else None}
            keuze = [i for i in range(len(tegels)) if i not in buren]
            raster[r][k] = rnd.choice(keuze)
    w, h = TW * schaal, TH * schaal
    doek = Image.new('RGB', (kolommen * w, rijen * h))
    for r in range(rijen):
        for k in range(kolommen):
            doek.paste(tegels[raster[r][k]].resize((w, h), Image.LANCZOS), (k * w, r * h))
    return doek


if __name__ == '__main__':
    lap(10, 6).save(UIT / 'stof-lap.jpg', quality=92)
    print('tegels', len(tegels))
