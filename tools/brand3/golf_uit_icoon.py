"""Haalt de golf los uit het board-en-golf-icoon (de breedste vorm) en slaat hem op als pad."""
import json, numpy as np, potrace
from PIL import Image
im = Image.open('bron-logo.webp').convert('L')
box = (312, 622, 638, 922); S = 4
c = im.crop(box).resize(((box[2] - box[0]) * S, (box[3] - box[1]) * S), Image.LANCZOS)
p = potrace.Bitmap(np.array(c) >= 110).trace(turdsize=40, alphamax=1.1, opticurve=True, opttolerance=0.3)
def breedte(cv):
    xs = [s.end_point.x for s in cv]; return max(xs) - min(xs)
golf = max(p, key=breedte)
d = [f'M{golf.start_point.x/S:.2f} {golf.start_point.y/S:.2f}']
pts = []
for seg in golf:
    if seg.is_corner:
        d.append(f'L{seg.c.x/S:.2f} {seg.c.y/S:.2f}L{seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}'); pts += [seg.c, seg.end_point]
    else:
        d.append(f'C{seg.c1.x/S:.2f} {seg.c1.y/S:.2f} {seg.c2.x/S:.2f} {seg.c2.y/S:.2f} {seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}'); pts += [seg.end_point]
d.append('Z')
xs = [q.x / S for q in pts]; ys = [q.y / S for q in pts]
json.dump({'d': ''.join(d), 'bbox': [min(xs), min(ys), max(xs), max(ys)]}, open('golf-icoon.json', 'w'))
print('golf', [round(v) for v in (min(xs), min(ys), max(xs), max(ys))])
