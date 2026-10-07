"""Zet de productbeeld-png's om naar jpg onder de 190 kB (eis: foto's onder 200 kB) en ruimt de png's op."""
import glob, os, pathlib, shutil
from PIL import Image
THEMA = pathlib.Path(__file__).parent.parent.parent / 'theme' / 'assets'
DOCS = pathlib.Path(__file__).parent.parent.parent / 'docs' / 'productbeelden'
for f in sorted(THEMA.glob('tt-product-*.png')):
    im, q, uit = Image.open(f).convert('RGB'), 86, f.with_suffix('.jpg')
    while True:
        im.save(uit, quality=q, optimize=True, progressive=True)
        if uit.stat().st_size < 190_000 or q <= 50:
            break
        q -= 3
    f.unlink()
    if '-800' not in uit.name:
        shutil.copy(uit, DOCS / uit.name)
    print(uit.name, q, uit.stat().st_size)
