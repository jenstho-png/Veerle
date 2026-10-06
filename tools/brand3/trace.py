"""Zet de golf en het board-icoon uit het gekozen logobeeld (bron-logo.webp) om naar SVG-paden."""
import json, numpy as np, potrace
from PIL import Image
im = Image.open('bron-logo.webp').convert('L')
def trek(box, schaal=4, alleen_grootste=False):
    c = im.crop(box); c = c.resize((c.width*schaal, c.height*schaal), Image.LANCZOS)
    a = np.array(c) >= 110
    bm = potrace.Bitmap(a); p = bm.trace(turdsize=40, alphamax=1.1, opticurve=True, opttolerance=0.3)
    d = []
    curves = list(p)
    if alleen_grootste:
        opp = lambda cv: (max(s.end_point.x for s in cv)-min(s.end_point.x for s in cv))*(max(s.end_point.y for s in cv)-min(s.end_point.y for s in cv))
        curves = [max(curves, key=opp)]
    for cv in curves:
        xs=[s.end_point.x for s in cv]; ys=[s.end_point.y for s in cv]
        if (max(xs)-min(xs))*(max(ys)-min(ys)) < (40*schaal)**2: continue  # losse stukjes van naburige letters
        s = cv.start_point; d.append(f'M{s.x/schaal:.2f} {s.y/schaal:.2f}')
        for seg in cv:
            if seg.is_corner: d.append(f'L{seg.c.x/schaal:.2f} {seg.c.y/schaal:.2f}L{seg.end_point.x/schaal:.2f} {seg.end_point.y/schaal:.2f}')
            else: d.append(f'C{seg.c1.x/schaal:.2f} {seg.c1.y/schaal:.2f} {seg.c2.x/schaal:.2f} {seg.c2.y/schaal:.2f} {seg.end_point.x/schaal:.2f} {seg.end_point.y/schaal:.2f}')
        d.append('Z')
    return {'d': ''.join(d), 'w': box[2]-box[0], 'h': box[3]-box[1]}
uit = {'golf': trek((646, 160, 906, 300), alleen_grootste=True), 'icoon': trek((312, 622, 638, 922))}
json.dump(uit, open('sporen.json','w')); print({k:(v['w'],v['h'],len(v['d'])) for k,v in uit.items()})
