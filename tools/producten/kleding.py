# Kleding en accessoires. Wordt uitgevoerd binnen producten.py (gebruikt de helpers en P daaruit).
MATEN = ['S', 'M', 'L', 'XL']
IL = json.load(open(ROOT / 'tools' / 'brand2' / 'illustraties.json'))


def lijntekening(naam, cx, cy, w, kleur, dikte=3.4):
    t = IL[naam]; vx, vy, vw, vh = map(float, t['vb'].split()); sc = w / vw
    paden = ''.join(f'<path d="{d if d.startswith("M") else "M" + d}"/>' for d in t['d'])
    return (f'<g transform="translate({cx - w / 2:.1f} {cy - vh * sc / 2:.1f}) scale({sc:.3f})" fill="none" stroke="{kleur}" '
            f'stroke-width="{dikte / sc:.2f}" stroke-linecap="round" stroke-linejoin="round">{paden}</g>')


def boogtekst(tekst, cx, cy, r, kleur, grootte, uid, spatie=4):
    pad = f'M{cx - r:.1f} {cy:.1f} A{r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} {cy:.1f}'
    return (f'<defs><path id="bt{uid}" d="{pad}"/></defs><text font-family="Tide Tode Display" font-size="{grootte:.1f}" letter-spacing="{spatie:.1f}" fill="{kleur}" text-anchor="middle">'
            f'<textPath href="#bt{uid}" startOffset="50%">{tekst}</textPath></text>')


def mono(tekst, x, y, kleur, grootte=9, spatie=2.4):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Courier Prime" font-weight="700" font-size="{grootte:.1f}" letter-spacing="{spatie:.1f}" fill="{kleur}" text-anchor="middle">{tekst}</text>'


VORM = {
    'tee': 'M215 120 L165 140 L95 210 L140 262 L180 230 L180 500 L420 500 L420 230 L460 262 L505 210 L435 140 L385 120 C370 150 340 165 300 165 C260 165 230 150 215 120 Z',
    'long': 'M215 120 L165 140 L125 200 L80 470 L128 480 L180 262 L180 500 L420 500 L420 262 L472 480 L520 470 L475 200 L435 140 L385 120 C370 150 340 165 300 165 C260 165 230 150 215 120 Z',
    'rash': 'M228 124 L188 138 L150 196 L108 470 L150 478 L200 258 L204 500 L396 500 L400 258 L450 478 L492 470 L450 196 L412 138 L372 124 C362 148 338 158 300 158 C262 158 238 148 228 124 Z',
    'hoodie': 'M215 125 L160 145 L118 205 L76 470 L126 480 L178 268 L178 500 L422 500 L422 268 L474 480 L524 470 L482 205 L440 145 L385 125 C370 150 340 160 300 160 C260 160 230 150 215 125 Z',
}
NAAD = {
    'tee': 'M215 120 C230 150 260 165 300 165 C340 165 370 150 385 120',
    'long': 'M215 120 C230 150 260 165 300 165 C340 165 370 150 385 120 M95 455 L128 462 M505 455 L472 462',
    'rash': 'M228 124 C238 148 262 158 300 158 C338 158 362 148 372 124 M150 196 L200 258 M450 196 L400 258',
    'hoodie': 'M215 125 C230 150 260 160 300 160 C340 160 370 150 385 125 M90 455 L128 464 M510 455 L472 464',
}
PLOOI = ('<defs><linearGradient id="plooi" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".08"/>'
         '<stop offset=".3" stop-color="#fff" stop-opacity=".08"/><stop offset=".7" stop-color="#000" stop-opacity="0"/>'
         '<stop offset="1" stop-color="#000" stop-opacity=".1"/></linearGradient></defs>')
MOUW = 'M108 470 L150 478 L162 420 L120 412 Z M492 470 L450 478 L438 420 L480 412 Z'


def kledingstuk(vorm, kleur, binnen='', achter=False, extra=''):
    lijn = '#fff' if kleur == NAVY else '#000'
    kap = ''
    if vorm == 'hoodie':
        kap = (f'<path d="M222 128 C205 60 260 30 300 30 C340 30 395 60 378 128 C360 150 240 150 222 128 Z" fill="{kleur}" stroke="{lijn}" stroke-opacity=".18" stroke-width="3"/>'
               + ('' if achter else f'<path d="M248 126 C250 90 350 90 352 126" fill="{lijn}" fill-opacity=".14"/>'))
    zak = ''
    if vorm == 'hoodie' and not achter:
        zak = (f'<path d="M222 400 L378 400 L398 476 L202 476 Z" fill="none" stroke="{lijn}" stroke-opacity=".2" stroke-width="3"/>'
               f'<path d="M286 150 L284 214 M314 150 L316 214" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>')
    naad = '' if achter and vorm != 'rash' else f'<path d="{NAAD[vorm]}" fill="none" stroke="{lijn}" stroke-opacity=".22" stroke-width="5"/>'
    rash = ''
    if vorm == 'rash':
        rash = f'<path d="{"M300 158 L300 500 M204 330 L396 330" if achter else "M204 300 L396 300"}" stroke="{CREME}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="6 6" fill="none"/>'
    return (f'{kap}<path d="{VORM[vorm]}" fill="{kleur}" stroke="{lijn}" stroke-opacity=".18" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="{VORM[vorm]}" fill="url(#plooi)" opacity=".5"/>{naad}{rash}{zak}{extra}{binnen}')


def print_zonsopkomst(cx, cy, w, inkt=NAVY, zon=TERRA):
    s = w / 200
    strepen = ''.join(f'<rect x="{cx - 70 * s:.1f}" y="{cy + (14 + k * 9) * s:.1f}" width="{140 * s:.1f}" height="{3.6 * s:.1f}" fill="{CREME}"/>' for k in range(4))
    golven = ''
    for k in range(3):
        y = cy + (52 + k * 12) * s
        golven += f'<path d="M{cx - 84 * s:.1f} {y:.1f}' + ''.join(f' q{10.5 * s:.1f} {-7 * s:.1f} {21 * s:.1f} 0' for _ in range(8)) + f'" fill="none" stroke="{inkt}" stroke-width="{3.2 * s:.1f}" stroke-linecap="round"/>'
    return (f'<defs><clipPath id="zc"><rect x="{cx - 80 * s:.1f}" y="{cy - 40 * s:.1f}" width="{160 * s:.1f}" height="{86 * s:.1f}"/></clipPath></defs>'
            f'<g clip-path="url(#zc)"><circle cx="{cx}" cy="{cy + 46 * s:.1f}" r="{60 * s:.1f}" fill="{zon}"/>{strepen}</g>{golven}'
            + boogtekst('TIDE TODE', cx, cy + 46 * s, 82 * s, inkt, 30 * s, 'z', spatie=3 * s)
            + mono('HANDEN VRIJ OP WEG NAAR ZEE', cx, cy + 104 * s, inkt, 7 * s, 1.8 * s))


def print_stickers(cx, cy, w):
    S = {x['naam']: x for x in ST.S}
    plek = [('golf', -46, -30, -10, 70), ('zon', 44, -38, 8, 58), ('schelp', -52, 40, 6, 56), ('palm', 4, 8, -4, 64), ('zeester', 52, 44, 12, 52), ('busje', -2, 82, 3, 66)]
    s = w / 200
    o = ''
    for n, x, y, r, gr in plek:
        st = S[n]; vx, vy, vw, vh = map(float, st['vb'].split()); sc = gr * s / max(vw, vh)
        binnen = ST.svg(st, schaduw=False); binnen = binnen[binnen.index('>') + 1:binnen.rindex('</svg>')]
        o += f'<g transform="translate({cx + x * s:.1f} {cy + y * s:.1f}) rotate({r}) scale({sc:.3f}) translate({-(vx + vw / 2):.1f} {-(vy + vh / 2):.1f})">{binnen}</g>'
    return o + mono('TIDE TODE SURF CLUB', cx, cy + 132 * s, CREME, 8 * s, 2.6 * s)


def print_golf(cx, cy, w, inkt=NAVY):
    return lijntekening('golf', cx, cy, w, inkt, 3.2) + mono('HANDEN VRIJ', cx, cy + w * .46, inkt, w * .055, w * .016)


def print_tegel(cx, cy, w):
    h = w * 1.2
    return (f'<defs><clipPath id="tg"><rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w * .06:.1f}"/></clipPath></defs>'
            f'<g clip-path="url(#tg)">{p_tegel(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w / 3)}</g>'
            + logo_g(cx, cy + h / 2 + w * .3, w * .62, CREME))


def print_busje(cx, cy, w, inkt=NAVY):
    return lijntekening('busje', cx, cy, w, inkt, 3) + mono('OP WEG NAAR ZEE', cx, cy + w * .5, inkt, w * .07, w * .02)


def mouwtekst(tekst, x, y, hoek, kleur):
    return f'<text transform="translate({x} {y}) rotate({hoek})" font-family="Courier Prime" font-weight="700" font-size="13" letter-spacing="4" fill="{kleur}">{tekst}</text>'


def poncho(achter=False):
    o = '<defs><clipPath id="pr"><path d="M93 440 L507 440 L520 520 L80 520 Z"/></clipPath></defs>'
    o += f'<path d="M222 128 C205 60 260 30 300 30 C340 30 395 60 378 128 Z" fill="{ZEE}"/>'
    o += f'<path d="M150 140 L60 300 L130 330 L180 230 Z M450 140 L540 300 L470 330 L420 230 Z" fill="{ZEE}" stroke="#fff" stroke-opacity=".15" stroke-width="3"/>'
    o += f'<path d="M150 140 L450 140 L520 520 L80 520 Z" fill="{ZEE}" stroke="#fff" stroke-opacity=".15" stroke-width="3"/>'
    o += f'<g clip-path="url(#pr)">{p_tegel(80, 440, 520, 520, 40)}</g>'
    if achter:
        o += logo_g(300, 290, 150, CREME)
    else:
        o += '<path d="M248 132 C250 96 350 96 352 132" fill="#000" fill-opacity=".18"/>' + icoon_a(255, 220, 44, CREME)
    return o


def mouwtegels(uid):
    return f'<defs><clipPath id="m{uid}"><path d="{MOUW}"/></clipPath></defs><g clip-path="url(#m{uid})">{p_tegel(100, 400, 500, 490, 22)}</g>'


KLEDING = [
    dict(handle='t-shirt-lijn-naar-zee', titel='T-shirt Lijn naar zee', type='T-shirt', prijs='35.00', gram=240, maten=MATEN,
         tekst='<p>Zwaar crème T-shirt met op de rug de lijn naar zee: onze surfspots langs de kust als haltes op één lijn, van Petten tot Domburg. Op de borst een klein board.</p><ul><li>100% biologisch katoen, 240 gram</li><li>Ruime, rechte pasvorm</li><li>Print met inkt op waterbasis</li></ul>',
         seo_tekst='Zwaar crème surf T-shirt met de lijn naar zee op de rug: surfspots van Petten tot Domburg. Biologisch katoen, maten S tot XL.',
         voor=lambda: PLOOI + kledingstuk('tee', CREME, icoon_a(345, 215, 30, NAVY)),
         achter=lambda: PLOOI + kledingstuk('tee', CREME, print_zonsopkomst(300, 260, 190), achter=True),
         voor_bg=ROSE, achter_bg=BABY, alt='Crème T-shirt Lijn naar zee', regel='Elke ochtend weer'),
    dict(handle='t-shirt-getijden', titel='T-shirt Getijden', type='T-shirt', prijs='35.00', gram=240, maten=MATEN,
         tekst='<p>Zwaar navy T-shirt met op de rug de getijden van Scheveningen: hoog en laag water als lijn, met SURF ALS HET WATER KOMT eronder. Op de borst klein ons logo.</p><ul><li>100% biologisch katoen, 240 gram</li><li>Ruime, rechte pasvorm</li><li>Print met inkt op waterbasis</li></ul>',
         seo_tekst='Zwaar navy surf T-shirt met getijdenprint op de rug. Biologisch katoen, ruime pasvorm, maten S tot XL.',
         voor=lambda: PLOOI + kledingstuk('tee', NAVY, logo_g(345, 222, 48, CREME)),
         achter=lambda: PLOOI + kledingstuk('tee', NAVY, print_stickers(300, 262, 200), achter=True),
         voor_bg=BABY, achter_bg=ROSE, alt='Navy T-shirt Getijden', regel='Surf als het water komt'),
    dict(handle='longsleeve-golf', titel='Longsleeve Golf', type='Longsleeve', prijs='45.00', gram=260, maten=MATEN,
         tekst='<p>Crème longsleeve voor koele ochtenden op het strand. Op de rug onze golf, langs de linkermouw staat HANDEN VRIJ.</p><ul><li>100% biologisch katoen, 220 gram</li><li>Ruime pasvorm met boorden aan de mouwen</li><li>Print met inkt op waterbasis</li></ul>',
         seo_tekst='Crème surf longsleeve met golfprint op de rug en tekst op de mouw. Biologisch katoen, maten S tot XL.',
         voor=lambda: PLOOI + kledingstuk('long', CREME, icoon_a(345, 215, 30, NAVY) + mouwtekst('HANDEN VRIJ', 452, 240, 77, NAVY)),
         achter=lambda: PLOOI + kledingstuk('long', CREME, print_golf(300, 270, 220), achter=True),
         voor_bg=BABY, achter_bg=ZAND, alt='Crème longsleeve Golf', regel='Voor de vroege sessie'),
    dict(handle='longsleeve-tegel', titel='Longsleeve Tegel', type='Longsleeve', prijs='45.00', gram=260, maten=MATEN,
         tekst='<p>Navy longsleeve met de tegelprint van onze draagtas groot op de rug. Op de borst een klein tegeltje.</p><ul><li>100% biologisch katoen, 220 gram</li><li>Ruime pasvorm met boorden aan de mouwen</li><li>Print met inkt op waterbasis</li></ul>',
         seo_tekst='Navy surf longsleeve met tegelprint op de rug. Biologisch katoen, maten S tot XL.',
         voor=lambda: PLOOI + kledingstuk('long', NAVY, p_tegel(332, 200, 362, 230, 30)),
         achter=lambda: PLOOI + kledingstuk('long', NAVY, print_tegel(300, 262, 140), achter=True),
         voor_bg=ZAND, achter_bg=BABY, alt='Navy longsleeve Tegel', regel='Dezelfde tegels als de tas'),
    dict(handle='uv-shirt-lange-mouw', titel='UV-shirt lange mouw', type='UV-shirt', prijs='45.00', gram=180, maten=['XS'] + MATEN,
         tekst='<p>Strak UV-shirt om in te surfen. Het beschermt je tegen de zon en tegen schuren van je board en wetsuit. Met platte naden en de tegelprint aan het eind van de mouwen.</p><ul><li>UPF 50+</li><li>Gerecycled polyamide met elastaan</li><li>Droogt snel</li><li>Spoel na het surfen uit met zoet water</li></ul>',
         seo_tekst='UV surfshirt met lange mouw, UPF 50+, sneldrogend en strak. Met tegelprint op de mouwen. Maten XS tot XL.',
         voor=lambda: PLOOI + kledingstuk('rash', NAVY, logo_g(300, 222, 70, CREME), extra=mouwtegels('v')),
         achter=lambda: PLOOI + kledingstuk('rash', NAVY, icoon_a(300, 200, 50, CREME) + mono('TIDE TODE', 300, 252, CREME, 12, 4), achter=True, extra=mouwtegels('a')),
         voor_bg=BABY, achter_bg=ROSE, alt='Navy UV-shirt met lange mouw', regel='Tegen zon en schuren'),
    dict(handle='hoodie-busje', titel='Hoodie Busje', type='Hoodie', prijs='65.00', gram=600, maten=MATEN,
         tekst='<p>Zware baby blue hoodie voor na het surfen. Op de rug het busje met een board op het dak en OP WEG NAAR ZEE eronder. Met buidelzak en koord in de capuchon.</p><ul><li>Biologisch katoen, 400 gram, geruwd aan de binnenkant</li><li>Ruime pasvorm</li><li>Print met inkt op waterbasis</li></ul>',
         seo_tekst='Baby blue surf hoodie met busjesprint op de rug. Zwaar biologisch katoen, maten S tot XL.',
         voor=lambda: PLOOI + kledingstuk('hoodie', BABY, logo_g(345, 228, 46, NAVY)),
         achter=lambda: PLOOI + kledingstuk('hoodie', BABY, print_busje(300, 275, 210), achter=True),
         voor_bg=ROSE, achter_bg=ZAND, alt='Baby blue hoodie Busje', regel='Warm na de sessie'),
    dict(handle='surfponcho-tegel', titel='Surfponcho', type='Poncho', prijs='60.00', gram=900,
         tekst='<p>Badstof poncho om je op het strand of naast de auto om te kleden. Met capuchon, korte wijde mouwen en een rand in tegelprint. Ons logo staat op de rug.</p><ul><li>Katoenen badstof, 350 gram</li><li>Eén maat, voor lengtes van 160 tot 195 cm</li><li>Droogt snel aan de lucht</li></ul>',
         seo_tekst='Surfponcho van katoenen badstof met capuchon en tegelrand. Om je makkelijk om te kleden op het strand. Eén maat.',
         voor=lambda: poncho(), achter=lambda: poncho(True), voor_bg=ZAND, achter_bg=BABY, alt='Zeeblauwe surfponcho met tegelrand', regel='Omkleden zonder gedoe'),
]
for k in KLEDING:
    P.append(dict(handle=k['handle'], titel=k['titel'], type=k['type'], collectie='Kleding en accessoires', prijs=k['prijs'], gram=k['gram'], tags=['kleding'], maten=k.get('maten'),
                  tekst=k['tekst'] + VERZENDING, seo_titel=f"{k['titel']} | Tide Tode", seo_tekst=k['seo_tekst'],
                  beelden=[('pack', lambda k=k: (k['voor'](), '0 0 600 600', 1450, 0), k['voor_bg'], 'Voorkant', k['alt'] + ', voorkant'),
                           ('pack', lambda k=k: (k['achter'](), '0 0 600 600', 1450, 0), k['achter_bg'], 'Achterkant', k['alt'] + ', achterkant met print'),
                           ('sfeer', lambda k=k: (k['achter'](), '0 0 600 600', 1450, 0), k['regel'], k['alt'] + ' als sticker op een foto van de zee')]))

ACCESSOIRES = [
    dict(handle='pet-navy', titel='Pet navy', type='Pet', prijs='30.00', gram=90,
         tekst='<p>Navy pet van katoen met ons board-icoon geborduurd op de voorkant. Verstelbaar aan de achterkant, één maat.</p>',
         seo_tekst='Navy katoenen pet met geborduurd Tide Tode icoon. Verstelbaar, één maat.',
         svg=lambda: (pet(NAVY), '0 0 600 600', 1600, 0), achter=ROSE, label='Navy', alt='Navy pet met het geborduurde board-icoon', regel='Zon in je ogen'),
    dict(handle='bucket-hat-tegel', titel='Bucket hat', type='Hoed', prijs='30.00', gram=90,
         tekst='<p>Crème bucket hat van gewassen katoen met ons board-icoon geborduurd op de voorkant. Eén maat.</p>',
         seo_tekst='Crème bucket hat van gewassen katoen met geborduurd Tide Tode icoon. Eén maat.',
         svg=lambda: (bucket('b'), '0 0 600 600', 1600, 0), achter=BABY, label='Crème', alt='Crème bucket hat met geborduurd board-icoon', regel='Voor lange stranddagen'),
    dict(handle='strandhanddoek-tegel', titel='Strandhanddoek tegel', type='Handdoek', prijs='45.00', gram=600,
         tekst='<p>Grote strandhanddoek van katoen in onze tegelprint, met franjes aan de korte kant. 90 bij 170 cm.</p>',
         seo_tekst='Katoenen strandhanddoek in de Tide Tode tegelprint, 90 bij 170 cm.',
         svg=lambda: (handdoek('h'), '0 0 600 600', 1500, -4), achter=ZAND, label='Tegelprint', alt='Strandhanddoek in tegelprint met franjes', regel='Na de sessie'),
    dict(handle='canvas-tas', titel='Canvas tas', type='Tas', prijs='20.00', gram=250,
         tekst='<p>Stevige canvas tas met ons busje erop en OP WEG NAAR ZEE eronder. Voor je handdoek, wetsuit en lunch. 38 bij 42 cm.</p>',
         seo_tekst='Canvas tas met busjesprint voor handdoek, wetsuit en lunch. 38 bij 42 cm.',
         svg=lambda: (tote(), '0 0 600 600', 1300, 0), achter=ROSE, label='Canvas', alt='Canvas tas met het busje en OP WEG NAAR ZEE', regel='Alles mee naar het strand'),
]
for k in ACCESSOIRES:
    P.append(dict(handle=k['handle'], titel=k['titel'], type=k['type'], collectie='Kleding en accessoires', prijs=k['prijs'], gram=k['gram'], tags=['accessoires'],
                  tekst=k['tekst'] + VERZENDING, seo_titel=f"{k['titel']} | Tide Tode", seo_tekst=k['seo_tekst'],
                  beelden=[('pack', k['svg'], k['achter'], k['label'], k['alt']), ('sfeer', k['svg'], k['regel'], k['alt'] + ' als sticker op een foto van de zee')]))

# losse printbestanden (zelfde artwork als op de kleding), voor de referentie bij ChatGPT
PRINTS = {
    't-shirt-lijn-naar-zee': [('rugprint', lambda: print_zonsopkomst(300, 250, 380), CREME), ('borst', lambda: icoon_a(300, 300, 300, NAVY), CREME)],
    't-shirt-getijden': [('rugprint', lambda: print_stickers(300, 240, 330), NAVY), ('borst', lambda: logo_g(300, 300, 420, CREME), NAVY)],
    'longsleeve-golf': [('rugprint', lambda: print_golf(300, 270, 460), CREME), ('borst', lambda: icoon_a(300, 300, 300, NAVY), CREME)],
    'longsleeve-tegel': [('rugprint', lambda: print_tegel(300, 250, 260), NAVY)],
    'uv-shirt-lange-mouw': [('borst', lambda: logo_g(300, 300, 420, CREME), NAVY)],
    'hoodie-busje': [('rugprint', lambda: print_busje(300, 270, 440), BABY), ('borst', lambda: logo_g(300, 300, 420, NAVY), BABY)],
    'surfponcho-tegel': [('rugprint', lambda: logo_g(300, 300, 420, CREME), ZEE)],
}
