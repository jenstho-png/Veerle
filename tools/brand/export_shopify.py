"""Exporteert het Tide-Tode logo en de handgeknipte iconen naar Shopify-snippets.

snippets/tt-logo.liquid  render 'tt-logo', variant: 'woord' | 'maan' | 'maan-simpel' | 'zegel' | 'golfje' | 'liggend' | 'staand'
snippets/tt-icoon.liquid render 'tt-icoon', icoon: 'golf' | 'schelp' | ... (handgeknipt, één kleur)
"""
import json, re, subprocess, sys, pathlib
hier = pathlib.Path(__file__).parent
theme = hier.parent.parent / 'theme'
logo = json.load(open(hier / 'logo.json'))
iconen = json.loads(subprocess.check_output([sys.executable, str(hier / 'icons.py')]))

woord_vb = logo['woord']['viewBox']
woord = f'<path d="{logo["woord"]["d"]}" fill="currentColor"/>'
maan_vol = (f'<defs><mask id="tt-gravure-{{{{ uid }}}}" maskUnits="userSpaceOnUse" x="0" y="0" width="200" height="200"><rect width="200" height="200" fill="#fff"/>'
            f'<path d="{logo["gravure"]}" fill="none" stroke="#000" stroke-width="1.6"/></mask></defs>'
            f'<path d="{logo["sikkel"]}" fill="currentColor" mask="url(#tt-gravure-{{{{ uid }}}})"/><path d="{logo["golfjes"]}" fill="currentColor"/>')
maan_simpel = f'<path d="{logo["sikkel"]}" fill="currentColor"/><path d="{logo["golfjes"]}" fill="currentColor"/>'
z = logo['zegel']
zegel = (f'<circle cx="100" cy="100" r="97" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="100" cy="100" r="62" fill="none" stroke="currentColor"/>'
         f'<path d="{z["boven"]}{z["onder"]}{z["tilde"]}" fill="currentColor"/>'
         f'<svg x="56" y="56" width="88" height="88" viewBox="0 0 200 200">{maan_vol}</svg>')
golfje_sym = re.search(r'<symbol id="golfje" viewBox="([^"]+)">(.*?)</symbol>', iconen['symbols'])
golfje_vb, golfje = golfje_sym.group(1), golfje_sym.group(2)

A = 'aria-hidden="true" focusable="false"'
snippet = f"""{{%- comment -%}}
  Tide-Tode logo als vectorpaden (gegenereerd door tools/brand/export_shopify.py, niet met de hand aanpassen).
  Gebruik: {{% render 'tt-logo', variant: 'liggend', class: '', label: shop.name %}}
  Varianten: woord, maan, maan-simpel, zegel, golfje, liggend, staand.
  De kleur volgt currentColor.
{{%- endcomment -%}}
{{%- liquid
  assign uid = section.id | default: 'tt' | append: variant
  assign aria = 'aria-hidden="true" focusable="false"'
  if label != blank
    assign aria = 'role="img" aria-label="' | append: label | append: '"'
  endif
-%}}
{{%- case variant -%}}
  {{%- when 'woord' -%}}
    <svg class="tt-woord {{{{ class }}}}" viewBox="{woord_vb}" {{{{ aria }}}}>{woord}</svg>
  {{%- when 'maan' -%}}
    <svg class="tt-maan {{{{ class }}}}" viewBox="0 0 200 200" {{{{ aria }}}}>{maan_vol}</svg>
  {{%- when 'maan-simpel' -%}}
    <svg class="tt-maan {{{{ class }}}}" viewBox="0 0 200 200" {{{{ aria }}}}>{maan_simpel}</svg>
  {{%- when 'zegel' -%}}
    <svg class="tt-zegel {{{{ class }}}}" viewBox="0 0 200 200" {{{{ aria }}}}>{zegel}</svg>
  {{%- when 'golfje' -%}}
    <svg class="tt-golfje {{{{ class }}}}" viewBox="{golfje_vb}" {A}>{golfje}</svg>
  {{%- when 'staand' -%}}
    <span class="tt-lock tt-lock--staand {{{{ class }}}}" {{{{ aria }}}}>
      <svg class="tt-maan" viewBox="0 0 200 200" {A}>{maan_vol}</svg>
      <svg class="tt-woord" viewBox="{woord_vb}" {A}>{woord}</svg>
    </span>
  {{%- else -%}}
    <span class="tt-lock tt-lock--liggend {{{{ class }}}}" {{{{ aria }}}}>
      <svg class="tt-maan" viewBox="0 0 200 200" {A}>{maan_simpel}</svg>
      <svg class="tt-woord" viewBox="{woord_vb}" {A}>{woord}</svg>
    </span>
{{%- endcase -%}}
"""
(theme / 'snippets' / 'tt-logo.liquid').write_text(snippet)

cases = ''
for m in re.finditer(r'<symbol id="i-([a-z]+)" viewBox="0 0 64 64">(.*?)</symbol>', iconen['symbols']):
    cases += f"  {{%- when '{m.group(1)}' -%}}\n    <svg class=\"tt-icoon {{{{ class }}}}\" viewBox=\"0 0 64 64\" {A}>{m.group(2)}</svg>\n"
icoon = f"""{{%- comment -%}}
  Handgeknipte Tide-Tode iconen (gegenereerd door tools/brand/export_shopify.py).
  Gebruik: {{% render 'tt-icoon', icoon: 'golf' %}}
  Iconen: {', '.join(k for k, _ in iconen['namen'])}
{{%- endcomment -%}}
{{%- case icoon -%}}
{cases}{{%- endcase -%}}
"""
(theme / 'snippets' / 'tt-icoon.liquid').write_text(icoon)

# favicon (maan, Deep op crème) als data-URI voor als er geen favicon is ingesteld
fav = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><rect width='200' height='200' rx='44' fill='#F5EEDF'/>"
       f"<g transform='translate(18 18) scale(.82)' fill='#1F3F6B'><path d='{logo['sikkel']}'/><path d='{logo['golfjes']}'/></g></svg>")
(theme / 'snippets' / 'tt-favicon.liquid').write_text(
    "{%- comment -%} Favicon met de maan (gegenereerd). Wordt gebruikt als er in de thema-instellingen geen favicon is gekozen. {%- endcomment -%}\n"
    + '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + fav.replace('#', '%23').replace('<', '%3C').replace('>', '%3E').replace('"', "'") + '">\n')
print('tt-logo', len(snippet) // 1024, 'KB · tt-icoon', len(icoon) // 1024, 'KB')
