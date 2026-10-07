"""Definitief woordmerk (richting 3): Fraunces Italic, Soft 100, opsz 144, gewicht 600, omgezet naar vormen.
De tilde staat iets hoger, als golf tussen de woorden. Schrijft logo3.json (paden + maten)."""
import json, pathlib, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HIER = pathlib.Path(__file__).parent
vf = TTFont(HIER / 'fonts' / 'Fraunces-Italic-VF.ttf')
f = instantiateVariableFont(vf, {'wght': 600, 'opsz': 144, 'SOFT': 100, 'WONK': 0})
f.save(HIER / 'fonts' / 'Fraunces-Italic-Logo.ttf')
gs = f.getGlyphSet(); order = f.getGlyphOrder(); upm = f['head'].unitsPerEm
blob = hb.Blob.from_file_path(str(HIER / 'fonts' / 'Fraunces-Italic-Logo.ttf'))
hbf = hb.Font(hb.Face(blob))
TILDE_OP = 0.1 * upm  # tilde iets omhoog


def regel(tekst, x0=0, y0=0, spatie=0):
    buf = hb.Buffer(); buf.add_str(tekst); buf.guess_segment_properties(); hb.shape(hbf, buf, {'kern': True, 'liga': True})
    pen = SVGPathPen(gs); bp = BoundsPen(gs); x = x0
    for info, pos, ch in zip(buf.glyph_infos, buf.glyph_positions, tekst):
        naam = order[info.codepoint]
        dy = TILDE_OP if ch == '~' else 0
        t = (1, 0, 0, -1, x + pos.x_offset, y0 - pos.y_offset - dy)  # y omlaag in svg
        gs[naam].draw(TransformPen(pen, t)); gs[naam].draw(TransformPen(bp, t))
        x += pos.x_advance + spatie
    return pen.getCommands(), bp.bounds


def maak(regels):
    d = ''; minx = miny = 1e9; maxx = maxy = -1e9
    for tekst, x0, y0 in regels:
        p, (a, b, c, e) = regel(tekst, x0, y0)
        d += p; minx, miny, maxx, maxy = min(minx, a), min(miny, b), max(maxx, c), max(maxy, e)
    return {'d': d, 'vb': f'{minx:.0f} {miny:.0f} {maxx - minx:.0f} {maxy - miny:.0f}', 'w': maxx - minx, 'h': maxy - miny}


lh = upm * 0.86
uit = {'liggend': maak([('Tide~Tode', 0, 0)]),
       'gestapeld': maak([('Tide~', 0, 0), ('Tode', upm * 0.4, lh)])}
json.dump(uit, open(HIER / 'logo3.json', 'w'))
print({k: (round(v['w']), round(v['h'])) for k, v in uit.items()})
