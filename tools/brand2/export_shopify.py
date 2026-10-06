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

# favicon: board op navy
bs = 150 / b['h']
fav = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><rect width='200' height='200' rx='44' fill='%2322324F'/>"
       f"<path transform='translate({100 - b['w'] * bs / 2:.1f} 25) scale({bs:.4f})' fill='%23F3ECDD' d='{b['d']}'/></svg>")
(THEMA / 'snippets' / 'tt-favicon.liquid').write_text(
    "{%- comment -%} Favicon met het board (gegenereerd). Wordt gebruikt als er in de thema-instellingen geen favicon is gekozen. {%- endcomment -%}\n"
    '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + fav.replace('<', '%3C').replace('>', '%3E') + '">\n')
print('snippets klaar')
