"""De echte draagtas (naar de fabrieksfoto): board, tegelpaneel en blauwe schouderband.
lijn() = handgetekende lijnillustratie, sticker() = kleurensticker met witte rand. viewBox 0 0 600 300."""
NAVY, CREME, PAPIER = '#22324F', '#F3ECDD', '#FBF7EF'
TERRA, BLAUW, MOSTERD, ROEST = '#C0603E', '#8FA9C8', '#D9A93B', '#9E3B2E'

BOARD = 'M24 172 C24 120 120 96 300 96 C450 96 540 128 582 170 C540 212 450 244 300 244 C120 244 24 224 24 172 Z'
PANEEL = 'M214 132 L386 132 L418 246 L182 246 Z'
BAND = 'M196 246 L282 30 Q300 8 318 30 L404 246'


def tegels(lijnmodus=False):
    """Tegelpatroon binnen het paneel, als clip."""
    uit = []
    kleuren = [TERRA, BLAUW, CREME, ROEST, BLAUW, TERRA, CREME]
    k = 0
    for r, y in enumerate(range(132, 246, 29)):
        for c, x in enumerate(range(176, 424, 29)):
            if lijnmodus:
                uit.append(f'<path d="M{x + 14.5} {y + 6} L{x + 23} {y + 14.5} L{x + 14.5} {y + 23} L{x + 6} {y + 14.5} Z" fill="none" stroke="{NAVY}" stroke-width="1.6"/>')
            else:
                kl = kleuren[(r * 3 + c) % len(kleuren)]
                uit.append(f'<rect x="{x}" y="{y}" width="29" height="29" fill="{kl}"/>')
                binnen = CREME if kl != CREME else TERRA
                uit.append(f'<path d="M{x + 14.5} {y + 4} L{x + 25} {y + 14.5} L{x + 14.5} {y + 25} L{x + 4} {y + 14.5} Z" fill="{binnen}"/>')
                uit.append(f'<circle cx="{x + 14.5}" cy="{y + 14.5}" r="3.4" fill="{NAVY}"/>')
            k += 1
    if lijnmodus:
        for x in range(176, 424, 29):
            uit.append(f'<line x1="{x}" y1="132" x2="{x}" y2="246" stroke="{NAVY}" stroke-width="1.4"/>')
        for y in range(132, 247, 29):
            uit.append(f'<line x1="170" y1="{y}" x2="430" y2="{y}" stroke="{NAVY}" stroke-width="1.4"/>')
    return ''.join(uit)


def lijn(cls='', kleur=NAVY):
    return f'''<svg class="{cls}" viewBox="0 0 600 300" aria-hidden="true" fill="none" stroke="{kleur}" stroke-linecap="round" stroke-linejoin="round">
  <defs><clipPath id="tl-clip"><path d="{PANEEL}"/></clipPath></defs>
  <path d="{BOARD}" stroke-width="3.4"/>
  <path d="M60 170 L548 170" stroke-width="1.6" opacity=".55"/>
  <path d="{PANEEL}" fill="{PAPIER}" stroke-width="3.2"/>
  <g clip-path="url(#tl-clip)">{tegels(True)}</g>
  <path d="{PANEEL}" stroke-width="3.2"/>
  <path d="{BAND}" stroke-width="16" stroke="{PAPIER}"/>
  <path d="M190 246 L277 28 Q300 0 323 28 L410 246 M204 246 L286 36 Q300 18 314 36 L396 246" stroke-width="2.8"/>
</svg>'''


def sticker(cls='', stijl=''):
    vorm = f'<path d="{BOARD}"/><path d="{PANEEL}"/><path d="{BAND}" fill="none"/>'
    return f'''<svg class="{cls}" style="{stijl}" viewBox="-20 -20 640 300" aria-hidden="true">
  <defs><clipPath id="ts-clip"><path d="{PANEEL}"/></clipPath></defs>
  <g fill="#000" stroke="#000" stroke-width="40" stroke-linejoin="round" opacity=".14" transform="translate(4 7)">{vorm}</g>
  <g fill="#FFFDF8" stroke="#FFFDF8" stroke-width="40" stroke-linejoin="round" stroke-linecap="round">{vorm}</g>
  <path d="{BOARD}" fill="{CREME}" stroke="{NAVY}" stroke-width="3"/>
  <path d="M60 170 L548 170" stroke="{NAVY}" stroke-width="1.6" opacity=".4"/>
  <g clip-path="url(#ts-clip)">{tegels()}</g>
  <path d="{PANEEL}" fill="none" stroke="{NAVY}" stroke-width="3"/>
  <path d="{BAND}" fill="none" stroke="{BLAUW}" stroke-width="15" stroke-linejoin="round"/>
  <path d="{BAND}" fill="none" stroke="{NAVY}" stroke-width="1.4" stroke-dasharray="4 5" opacity=".55"/>
</svg>'''
