"""Bouwt 'Tide Tode Display': Kavoon (OFL) met een rechte T, als woff2 voor de site.
Kavoon valt onder de SIL Open Font License; afgeleide fonts mogen niet 'Kavoon' heten."""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from shapely.geometry.polygon import orient
from woordmerk import glyf, rechte_t, zacht

HIER = pathlib.Path(__file__).parent
font = TTFont(HIER / 'fonts' / 'Kavoon-Regular.ttf')
cmap = font.getBestCmap()

def zet(teken, vorm):
    pen = TTGlyphPen(None)
    for p in (vorm.geoms if vorm.geom_type == 'MultiPolygon' else [vorm]):
        p = orient(p, sign=-1.0)  # TrueType: buitenkant met de klok mee
        for ring in [p.exterior] + list(p.interiors):
            pts = list(ring.coords)[:-1]
            pen.moveTo(tuple(round(c) for c in pts[0]))
            for pt in pts[1:]:
                pen.lineTo(tuple(round(c) for c in pt))
            pen.closePath()
    naam = cmap[ord(teken)]
    font['glyf'][naam] = pen.glyph()
    font['glyf'][naam].recalcBounds(font['glyf'])

for teken in 'Tt':
    if ord(teken) in cmap:
        g, _ = glyf(font, 'T')
        zet(teken, rechte_t(g))

for rec in font['name'].names:
    s = rec.toUnicode()
    if 'Kavoon' in s:
        rec.string = s.replace('Kavoon', 'Tide Tode Display')
uit = HIER.parent.parent / 'theme' / 'assets'
font.flavor = 'woff2'
font.save(uit / 'tide-tode-display.woff2')
font.flavor = None
font.save(HIER / 'fonts' / 'TideTodeDisplay-Regular.ttf')
print('font klaar')
