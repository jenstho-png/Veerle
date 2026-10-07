"""Zet branding 2 in het thema: logo-snippet, sticker-snippet en favicon.
De variantnamen van tt-logo blijven gelijk, zodat alle bestaande plekken
vanzelf het nieuwe logo krijgen:
  staand  -> gestapeld woordmerk TIDE / TODE
  liggend / woord -> TIDE TODE op één regel
  maan / maan-simpel / maan-simpel-pad -> het board (beeldmerk)
  zegel   -> rond zegel met tekst rondom en het board
  golfje  -> klein golfje (blijft, voor kleine accenten)"""
import json, pathlib, re
import stickers as ST

HIER = pathlib.Path(__file__).parent
THEMA = HIER.parent.parent / 'theme'
L = json.load(open(HIER / 'logo2.json'))
oud = (THEMA / 'snippets' / 'tt-logo.liquid').read_text()
golfje = re.search(r"\{%- when 'golfje' -%\}\s*(<svg.*?</svg>)", oud, re.S).group(1)


def svg(soort, cls):
    l = L[soort]
    return f'<svg class="{cls} {{{{ class }}}}" viewBox="0 0 {l["w"]} {l["h"]}" {{{{ aria }}}}><path fill="currentColor" d="{l["d"]}"/></svg>'


b = L['board']
s = 150 / b['h']
board_in_zegel = f'<path transform="translate({170 - b["w"] * s / 2:.1f} 103) scale({s:.4f})" fill="currentColor" d="{b["d"]}"/>'
zegel = ('<svg class="tt-zegel {{ class }}" viewBox="0 0 340 340" {{ aria }}>'
         '<defs><path id="tt-zb-{{ uid }}" d="M60 170a110 110 0 0 1 220 0"/><path id="tt-zo-{{ uid }}" d="M44 170a126 126 0 0 0 252 0"/></defs>'
         '<circle cx="170" cy="170" r="158" fill="none" stroke="currentColor" stroke-width="3"/>'
         '<text font-family="Courier Prime, monospace" font-weight="700" font-size="30" letter-spacing="9" fill="currentColor"><textPath href="#tt-zb-{{ uid }}" startOffset="50%" text-anchor="middle">TIDE TODE</textPath></text>'
         '<text font-family="Courier Prime, monospace" font-weight="700" font-size="19" letter-spacing="5" fill="currentColor"><textPath href="#tt-zo-{{ uid }}" startOffset="50%" text-anchor="middle">VAN SURFERS VOOR SURFERS</textPath></text>'
         '<circle cx="44" cy="170" r="6" fill="currentColor"/><circle cx="296" cy="170" r="6" fill="currentColor"/>'
         + board_in_zegel + '</svg>')

snippet = f"""{{%- comment -%}}
  Tide-Tode logo (branding 2, gegenereerd door tools/brand2/export_shopify.py, niet met de hand aanpassen).
  Gebruik: {{% render 'tt-logo', variant: 'staand', class: '', label: shop.name %}}
  Varianten: staand (TIDE boven TODE), liggend en woord (op één regel), maan en maan-simpel (het board),
  maan-simpel-pad (alleen het pad van het board, voor binnen een svg), zegel, golfje. Kleur volgt currentColor.
{{%- endcomment -%}}
{{%- liquid
  assign uid = section.id | default: 'tt' | append: variant
  assign aria = 'aria-hidden="true" focusable="false"'
  if label != blank
    assign aria = 'role="img" aria-label="' | append: label | append: '"'
  endif
-%}}
{{%- case variant -%}}
  {{%- when 'staand' -%}}
    {svg('gestapeld', 'tt-lock tt-lock--staand')}
  {{%- when 'maan' or 'maan-simpel' -%}}
    {svg('board', 'tt-board')}
  {{%- when 'maan-simpel-pad' -%}}
    <path fill="currentColor" d="{b['d']}"/>
  {{%- when 'zegel' -%}}
    {zegel}
  {{%- when 'golfje' -%}}
    {golfje}
  {{%- else -%}}
    {svg('liggend', 'tt-lock tt-lock--liggend')}
{{%- endcase -%}}
"""
(THEMA / 'snippets' / 'tt-logo.liquid').write_text(snippet)

# stickers als snippet (getallen afgerond op hele pixels: scheelt de helft in bestandsgrootte)
def kort(s):
    return re.sub(r'(\d+)\.\d+', lambda m: m.group(1), s)


cases = ''
for s_ in ST.S:
    cases += f"  {{%- when '{s_['naam']}' -%}}\n    " + kort(ST.svg(s_)).replace('<svg ', '<svg class="tt-stk {{ class }}" aria-hidden="true" focusable="false" ', 1) + '\n'
(THEMA / 'snippets' / 'tt-stk.liquid').write_text(
    "{%- comment -%}\n  Tide-Tode stickers (gegenereerd door tools/brand2/export_shopify.py).\n"
    f"  Gebruik: {{% render 'tt-stk', naam: 'golf', class: '' %}}\n  Namen: {', '.join(s_['naam'] for s_ in ST.S)}\n{{%- endcomment -%}}\n"
    "{%- case naam -%}\n" + cases + "{%- endcase -%}\n")

# favicon: icoon C (de tegel) in navy, op transparant
c = L['icoonC']
fav = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-8 -8 {c['w'] + 16} {c['h'] + 16}'><path fill='%2322324F' fill-rule='evenodd' d='{c['d']}'/></svg>"
(THEMA / 'snippets' / 'tt-favicon.liquid').write_text(
    "{%- comment -%} Favicon met het board (gegenereerd). Wordt gebruikt als er in de thema-instellingen geen favicon is gekozen. {%- endcomment -%}\n"
    '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + fav.replace('<', '%3C').replace('>', '%3E') + '">\n')
print('snippets klaar')

# ---------- branding 2, deel 2: iconen B/C, illustraties, tas-sticker, patroon ----------
import illustraties as IL, tas as TAS
# extra varianten in tt-logo: icoon-zon (B) en icoon-tegel (C)
sn = (THEMA / 'snippets' / 'tt-logo.liquid').read_text()
if "'icoon-zon'" not in sn:
    extra = ''
    for var, k in (('icoon-zon', 'icoonB'), ('icoon-tegel', 'icoonC')):
        l = L[k]
        extra += f"  {{%- when '{var}' -%}}\n    <svg class=\"tt-icoon-{var[6:]} {{{{ class }}}}\" viewBox=\"0 0 {l['w']} {l['h']}\" {{{{ aria }}}}><path fill=\"currentColor\" fill-rule=\"evenodd\" d=\"{l['d']}\"/></svg>\n"
    sn = sn.replace("  {%- when 'golfje' -%}", extra + "  {%- when 'golfje' -%}")
    (THEMA / 'snippets' / 'tt-logo.liquid').write_text(sn)

# illustraties
cases = ''
for n in ('parasol', 'golf', 'busje', 'zon'):
    cases += f"  {{%- when '{n}' -%}}\n    " + kort(IL.svg(n, 'currentColor', 3.2)).replace('<svg ', '<svg class="tt-ill {{ class }}" aria-hidden="true" ', 1) + '\n'
cases += "  {%- when 'draagtas' -%}\n    " + TAS.lijn('tt-ill {{ class }}', 'currentColor') + '\n'
(THEMA / 'snippets' / 'tt-ill.liquid').write_text(
    "{%- comment -%}\n  Lijnillustraties (gegenereerd door tools/brand2/export_shopify.py). Kleur volgt currentColor.\n"
    "  Gebruik: {% render 'tt-ill', naam: 'parasol' %}  Namen: parasol, golf, busje, zon, draagtas\n{%- endcomment -%}\n"
    "{%- case naam -%}\n" + cases + "{%- endcase -%}\n")

# tas-sticker toevoegen aan tt-stk
st = (THEMA / 'snippets' / 'tt-stk.liquid').read_text()
if "'draagtas'" not in st:
    st = st.replace("{%- endcase -%}", "  {%- when 'draagtas' -%}\n    " + TAS.sticker('tt-stk tt-stk--tas {{ class }}') + "\n{%- endcase -%}")
    (THEMA / 'snippets' / 'tt-stk.liquid').write_text(st)

# patroon: crème vormen uit de stickers op navy
plek = [('zon', 130, 150, 0.55, 0), ('golf', 520, 170, 0.62, -6), ('schelp', 850, 140, 0.55, 8), ('palm', 140, 520, 0.6, -4),
        ('zeester', 480, 520, 0.6, 14), ('board', 830, 540, 0.55, 10), ('golf', 220, 880, 0.58, -3), ('zon', 600, 900, 0.5, 6),
        ('schelp', 880, 930, 0.45, -12), ('zeester', 110, 1130, 0.4, -10), ('golf', 880, 1130, 0.45, 4), ('zon', 520, 1180, 0.35, 0)]
STK = {s_['naam']: s_ for s_ in ST.S}


def vormen_uit(plek):
    uit = ''
    for naam, x, y, sc, r in plek:
        s_ = STK[naam]; vx, vy, vw, vh = map(float, s_['vb'].split())
        uit += f'<path transform="translate({x} {y}) rotate({r}) scale({sc}) translate({-(vx + vw / 2):.0f} {-(vy + vh / 2):.0f})" d="{kort(s_["vorm"])}"/>'
    return uit


# breed patroon (desktop): vier rijen, verspringend, kleinere vormen
reeks = ['zon', 'golf', 'schelp', 'palm', 'zeester', 'board']
breed = []
for rij in range(4):
    for kol in range(8):
        naam = reeks[(kol + rij * 3) % len(reeks)]
        x = 110 + kol * 200 + (100 if rij % 2 else 0)
        breed.append((naam, x, 110 + rij * 230, 0.36, ((kol * 7 + rij * 11) % 25) - 12))
(THEMA / 'snippets' / 'tt-patroon.liquid').write_text(
    "{%- comment -%} Patroon met de vormen uit de stickers (gegenereerd). Kleur volgt currentColor. Een brede en een staande versie. {%- endcomment -%}\n"
    + f'<svg class="tt-patroon-svg tt-patroon-svg--breed {{{{ class }}}}" viewBox="0 0 1700 920" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="currentColor">{vormen_uit(breed)}</g></svg>'
    + f'<svg class="tt-patroon-svg tt-patroon-svg--staand {{{{ class }}}}" viewBox="0 0 1000 1250" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="currentColor">{vormen_uit(plek)}</g></svg>\n')
print('deel 2 klaar')
