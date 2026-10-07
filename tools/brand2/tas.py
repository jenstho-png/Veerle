"""De echte draagtas: board, tegelpaneel en schouderband, zoals op de productfoto's.
Het paneel zit schuin om het hele board, van de onderste tot de bovenste rail. De band loopt met twee kanten over
het paneel en komt met beide uiteinden uit de bovenste rail, waar hij samen een lus vormt.
lijn() = lijnillustratie, sticker() = kleurensticker met witte rand. viewBox 0 0 600 310."""
NAVY, CREME, PAPIER = '#22324F', '#F3ECDD', '#FBF7EF'
TERRA, BLAUW, MOSTERD, ROEST = '#C0603E', '#8FA9C8', '#D9A93B', '#9E3B2E'

BOARD = 'M24 212 C24 160 120 136 300 136 C450 136 540 168 582 210 C540 252 450 284 300 284 C120 284 24 264 24 212 Z'
# schuin vlak over de hele breedte van het board; wordt op de vorm van het board geknipt
PANEEL = 'M194 292 L406 292 L364 128 L236 128 Z'
# twee banden over het paneel, uit de bovenste rail en samen in een lus
BAND = 'M222 282 L276 54 A24 24 0 0 1 324 54 L378 282'
LABEL = 'M290 142 L310 142 L310 160 L290 160 Z'


def tegels(lijnmodus=False):
    """Tegelpatroon voor het paneel (wordt geknipt op paneel en board)."""
    uit = []
    kleuren = [TERRA, BLAUW, CREME, ROEST, BLAUW, TERRA, CREME]
    xs, ys = range(190, 420, 29), range(120, 300, 29)
    for r, y in enumerate(ys):
        for c, x in enumerate(xs):
            if lijnmodus:
                uit.append(f'<path d="M{x + 14.5} {y + 6} L{x + 23} {y + 14.5} L{x + 14.5} {y + 23} L{x + 6} {y + 14.5} Z" fill="none" stroke="{NAVY}" stroke-width="1.6"/>')
            else:
                kl = kleuren[(r * 3 + c) % len(kleuren)]
                uit.append(f'<rect x="{x}" y="{y}" width="29" height="29" fill="{kl}"/>')
                binnen = CREME if kl != CREME else TERRA
                uit.append(f'<path d="M{x + 14.5} {y + 4} L{x + 25} {y + 14.5} L{x + 14.5} {y + 25} L{x + 4} {y + 14.5} Z" fill="{binnen}"/>')
                uit.append(f'<circle cx="{x + 14.5}" cy="{y + 14.5}" r="3.4" fill="{NAVY}"/>')
    if lijnmodus:
        for x in xs:
            uit.append(f'<line x1="{x}" y1="120" x2="{x}" y2="300" stroke="{NAVY}" stroke-width="1.4"/>')
        for y in ys:
            uit.append(f'<line x1="180" y1="{y}" x2="430" y2="{y}" stroke="{NAVY}" stroke-width="1.4"/>')
    return ''.join(uit)


def _clips(p):
    return (f'<clipPath id="{p}-b"><path d="{BOARD}"/></clipPath>'
            f'<clipPath id="{p}-p"><path d="{PANEEL}"/></clipPath>')


def lijn(cls='', kleur=NAVY):
    return f'''<svg class="{cls}" viewBox="0 0 600 310" aria-hidden="true" fill="none" stroke="{kleur}" stroke-linecap="round" stroke-linejoin="round">
  <defs>{_clips('tl')}</defs>
  <path d="{BOARD}" stroke-width="3.4"/>
  <path d="M60 210 L548 210" stroke-width="1.6" opacity=".55"/>
  <g clip-path="url(#tl-b)"><g clip-path="url(#tl-p)"><rect x="180" y="110" width="260" height="200" fill="{PAPIER}" stroke="none"/>{tegels(True)}</g>
  <path d="{PANEEL}" stroke-width="3.2"/></g>
  <path d="{BOARD}" stroke-width="3.4"/>
  <path d="{LABEL}" fill="{kleur}" stroke-width="2"/>
  <path d="{BAND}" stroke-width="16" stroke="{PAPIER}"/>
  <path d="{BAND}" stroke-width="12" stroke="{kleur}"/>
  <path d="{BAND}" stroke-width="7" stroke="{PAPIER}"/>
</svg>'''


def sticker(cls='', stijl=''):
    vorm = f'<path d="{BOARD}"/><path d="{BAND}" fill="none"/>'
    return f'''<svg class="{cls}" style="{stijl}" viewBox="-20 -6 640 330" aria-hidden="true">
  <defs>{_clips('ts')}</defs>
  <g fill="#000" stroke="#000" stroke-width="40" stroke-linejoin="round" opacity=".14" transform="translate(4 7)">{vorm}</g>
  <g fill="#FFFDF8" stroke="#FFFDF8" stroke-width="40" stroke-linejoin="round" stroke-linecap="round">{vorm}</g>
  <path d="{BOARD}" fill="{CREME}" stroke="{NAVY}" stroke-width="3"/>
  <path d="M60 210 L548 210" stroke="{NAVY}" stroke-width="1.6" opacity=".4"/>
  <g clip-path="url(#ts-b)"><g clip-path="url(#ts-p)">{tegels()}</g><path d="{PANEEL}" fill="none" stroke="{NAVY}" stroke-width="3"/></g>
  <path d="{BOARD}" fill="none" stroke="{NAVY}" stroke-width="3"/>
  <path d="{LABEL}" fill="{NAVY}"/>
  <path d="{BAND}" fill="none" stroke="{NAVY}" stroke-width="18" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="{BAND}" fill="none" stroke="{BLAUW}" stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="{BAND}" fill="none" stroke="{NAVY}" stroke-width="1.4" stroke-dasharray="4 5" opacity=".55"/>
</svg>'''
