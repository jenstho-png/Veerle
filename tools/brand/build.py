"""Bouwt docs/brandbook/brandbook.html uit het sjabloon, het gegenereerde logo (logo.json) en de merktekens (marks.py)."""
import json, re, subprocess, sys, pathlib
hier = pathlib.Path(__file__).parent
logo = json.load(open(sys.argv[1] if len(sys.argv) > 1 else hier / 'logo.json'))
marks = json.loads(subprocess.check_output([sys.executable, str(hier / 'marks.py')]))
s = (hier / 'brandbook.template.html').read_text()
def nul(v):
    # <use> tekent een symbool vanaf (0,0); de buitenste viewBox begint daarom ook bij 0
    x, y, w, h = v.split()
    return f'0 0 {w} {h}'
vb = {'logo-board': nul(logo['board']['viewBox']), 'logo-caps': nul(logo['flatCaps']['viewBox']), 'logo-woord': nul(logo['flatMixed']['viewBox'])}
# elke <svg> zonder viewBox die alleen een logo-symbool toont, krijgt de viewBox van dat logo (behoudt de verhouding)
def add_vb(m):
    tag, sym = m.group(1), m.group(2)
    return f'<svg viewBox="{vb[sym]}"{tag}><use href="#{sym}"'
s = re.sub(r'<svg(?![^>]*viewBox)([^>]*)><use href="#(logo-board|logo-caps|logo-woord)"', add_vb, s)
rep = {
  'BOARD_VB': logo['board']['viewBox'], 'BOARD_D': logo['board']['boardD'], 'WORD_D': logo['board']['wordD'], 'STROKE': str(logo['board']['stroke']),
  'CAPS_VB': logo['flatCaps']['viewBox'], 'CAPS_D': logo['flatCaps']['d'], 'MIXED_VB': logo['flatMixed']['viewBox'], 'MIXED_D': logo['flatMixed']['d'],
  'SPIRAAL_ICOON': marks['spiraal_icoon'], 'ZON_STRALEN': marks['zon_stralen'], 'ZON_SPIRAAL': marks['zon_spiraal'], 'TT_BALK': marks['tt_balk'],
}
for k, v in rep.items(): s = s.replace(f'%%{k}%%', v)
left = re.findall(r'%%[A-Z_]+%%', s)
assert not left, left
out = hier.parent.parent / 'docs' / 'brandbook' / 'brandbook.html'
out.write_text(s)
print(out, len(s) // 1024, 'KB')
