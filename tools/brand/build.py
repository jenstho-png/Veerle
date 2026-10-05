"""Bouwt docs/brandbook/brandbook.html uit het sjabloon, het logo (logo.json, via logo.mjs) en de iconen (icons.py)."""
import json, re, subprocess, sys, pathlib
hier = pathlib.Path(__file__).parent
logo = json.load(open(hier / 'logo.json'))
iconen = json.loads(subprocess.check_output([sys.executable, str(hier / 'icons.py')]))
s = (hier / 'brandbook.template.html').read_text()

x, y, w, h = logo['woord']['viewBox'].split()
vb0 = f'0 0 {w} {h}'  # <use> tekent een symbool vanaf (0,0)
s = re.sub(r'<svg(?![^>]*viewBox)([^>]*)><use href="#logo-woord"', lambda m: f'<svg viewBox="{vb0}"{m.group(1)}><use href="#logo-woord"', s)

tegels = ''.join(f'<div class="icoon"><svg viewBox="0 0 64 64" aria-hidden="true"><use href="#i-{k}"/></svg><span>{n}</span></div>' for k, n in iconen['namen'])
wax = ''
for i, (kleur, label, icoon) in enumerate([('#C4DAF0', 'Koud water', 'golfjes'), ('#F2BDBD', 'Warm water', 'zon'), ('#F2D06B', 'Tropisch', 'koraal')]):
    tx, ty = 18 + i * 105, 22 if i != 1 else 10
    wax += (f'<g transform="translate({tx} {ty})"><rect width="94" height="128" rx="16" fill="{kleur}"/><rect x="30" width="34" height="128" fill="#1F3F6B"/>'
            f'<svg x="29" y="20" width="36" height="36" viewBox="0 0 200 200" style="color:#F5EEDF"><use href="#zegel"/></svg>'
            f'<svg x="7" y="98" width="20" height="20" viewBox="0 0 64 64" style="color:#1F3F6B"><use href="#i-{icoon}"/></svg>'
            f'<text x="47" y="148" text-anchor="middle" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="#1F3F6B">{label}</text></g>')
rep = {
    'WOORD_VB': logo['woord']['viewBox'], 'WOORD_D': logo['woord']['d'], 'WOORD_VB0': vb0,
    'SIKKEL': logo['sikkel'], 'GRAVURE': logo['gravure'], 'GOLFJES': logo['golfjes'],
    'ZEGEL_BOVEN': logo['zegel']['boven'], 'ZEGEL_ONDER': logo['zegel']['onder'], 'ZEGEL_TILDE': logo['zegel']['tilde'],
    'ICONS': iconen['symbols'], 'ICOON_TEGELS': tegels, 'WAX': wax,
}
for k, v in rep.items():
    s = s.replace(f'%%{k}%%', v)
left = re.findall(r'%%[A-Z_0-9]+%%', s)
assert not left, left
out = hier.parent.parent / 'docs' / 'brandbook' / 'brandbook.html'
out.write_text(s)
print(out, len(s) // 1024, 'KB')
