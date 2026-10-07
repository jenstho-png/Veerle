"""Zet de png's in docs/producten/beelden om naar jpg onder de 190 kB (eis: beelden onder 200 kB)."""
import pathlib
from PIL import Image
MAP = pathlib.Path(__file__).parent.parent.parent / 'docs' / 'producten' / 'beelden'
for f in sorted(MAP.glob('*.png')):
    im, q, uit = Image.open(f).convert('RGB'), 86, f.with_suffix('.jpg')
    while True:
        im.save(uit, quality=q, optimize=True, progressive=True)
        if uit.stat().st_size < 190_000 or q <= 50:
            break
        q -= 3
    f.unlink()
    if q < 70:
        print('let op', uit.name, q, uit.stat().st_size)
print(len(list(MAP.glob('*.jpg'))), 'jpg, grootste', max(x.stat().st_size for x in MAP.glob('*.jpg')))
