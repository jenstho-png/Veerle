"""Strenge controle van templates en sectiegroepen, zoals Shopify die doet bij het uploaden:
bestaat elke sectie, elk blocktype en elke instelling, en past elke waarde bij het type (select-opties, range, checkbox)."""
import json, re, pathlib, sys
T = pathlib.Path(__file__).parent.parent.parent / 'theme'
schemas = {}
for f in (T / 'sections').glob('*.liquid'):
    s = f.read_text()
    if '{% schema %}' in s:
        schemas[f.stem] = json.loads(s.split('{% schema %}')[1].split('{% endschema %}')[0])
fouten = []
for naam, sch in schemas.items():
    # Shopify: namen van secties, blokken en presets maximaal 25 tekens
    for n in [sch.get('name')] + [b.get('name') for b in sch.get('blocks', [])] + [p.get('name') for p in sch.get('presets', [])]:
        if isinstance(n, str) and not n.startswith('t:') and len(n) > 25:
            fouten.append(f'{naam}: naam langer dan 25 tekens: {n}')
    # Shopify: tussenkoppen (type header) maximaal 50 tekens
    for st in sch.get('settings', []) + [x for b in sch.get('blocks', []) for x in b.get('settings', [])]:
        c = st.get('content', '')
        if st.get('type') == 'header' and not c.startswith('t:') and len(c) > 50:
            fouten.append(f'{naam}: tussenkop langer dan 50 tekens: {c}')


def check_settings(waar, defs, waarden):
    d = {x['id']: x for x in defs if 'id' in x}
    for k, v in waarden.items():
        if k not in d:
            fouten.append(f'{waar}: onbekende instelling {k}')
            continue
        st = d[k]; ty = st['type']
        if ty in ('select', 'radio') and v not in [o['value'] for o in st['options']]:
            fouten.append(f'{waar}: {k}={v!r} niet in opties')
        if ty == 'range' and (not isinstance(v, (int, float)) or v < st['min'] or v > st['max'] or (v - st['min']) % st.get('step', 1)):
            fouten.append(f'{waar}: {k}={v!r} buiten range {st["min"]}-{st["max"]} stap {st.get("step", 1)}')
        if ty == 'checkbox' and not isinstance(v, bool):
            fouten.append(f'{waar}: {k}={v!r} geen boolean')
        if ty == 'number' and not isinstance(v, (int, float)):
            fouten.append(f'{waar}: {k}={v!r} geen getal')
        if ty in ('image_picker', 'product', 'collection', 'page', 'url', 'video', 'link_list') and v == '':
            fouten.append(f'{waar}: {k} is een lege string')
        if ty == 'color' and not re.match(r'^#[0-9A-Fa-f]{6}$|^#[0-9A-Fa-f]{3}$|^rgba?\(', str(v)):
            fouten.append(f'{waar}: {k}={v!r} geen kleur')
        if ty == 'text' and isinstance(v, str) and '\n' in v:
            fouten.append(f'{waar}: {k} tekstveld met regeleinde')


for f in sorted(list((T / 'templates').glob('*.json')) + list((T / 'sections').glob('*.json'))):
    t = f.read_text(); m = re.match(r'\s*(/\*.*?\*/)\s*', t, re.S)
    d = json.loads(t[m.end():] if m else t)
    for k, sec in d.get('sections', {}).items():
        sch = schemas.get(sec['type'])
        if sch is None and (T / 'sections' / f"{sec['type']}.liquid").exists():
            continue   # sectie zonder schema (zoals main-404)
        if sch is None:
            fouten.append(f'{f.name}/{k}: sectie {sec["type"]} bestaat niet'); continue
        if f.parent.name == 'templates' and 'templates' in sch and f.stem.split('.')[0] not in sch['templates']:
            fouten.append(f'{f.name}/{k}: {sec["type"]} mag niet in dit template')
        check_settings(f'{f.name}/{k}', sch.get('settings', []), sec.get('settings', {}))
        types = {b['type']: b for b in sch.get('blocks', [])}
        blokken = sec.get('blocks', {})
        if sch.get('max_blocks') and len(blokken) > sch['max_blocks']:
            fouten.append(f'{f.name}/{k}: {len(blokken)} blokken, max {sch["max_blocks"]}')
        for bk, b in blokken.items():
            if b['type'] not in types and '@app' not in types:
                fouten.append(f'{f.name}/{k}/{bk}: blocktype {b["type"]} bestaat niet'); continue
            check_settings(f'{f.name}/{k}/{bk}', types.get(b['type'], {}).get('settings', []), b.get('settings', {}))
        if 'block_order' in sec and set(sec['block_order']) != set(blokken):
            fouten.append(f'{f.name}/{k}: block_order klopt niet met blocks')
    if 'order' in d and set(d['order']) != set(d.get('sections', {})):
        fouten.append(f'{f.name}: order klopt niet met sections')
print('\n'.join(fouten) or 'geen fouten')
sys.exit(1 if fouten else 0)
