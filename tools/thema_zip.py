"""Maakt een zip van het thema met een volgnummer in de naam (Tide Tode 4, 5, ...), zodat je in Shopify ziet welke versie het is.
Gebruik: python3 tools/thema_zip.py [map voor de zip]"""
import json, pathlib, sys, zipfile
ROOT = pathlib.Path(__file__).parent.parent
TEL = ROOT / 'docs' / 'thema-versie.txt'
nr = int(TEL.read_text().strip()) + 1 if TEL.exists() else 4
schema = ROOT / 'theme' / 'config' / 'settings_schema.json'
d = json.loads(schema.read_text())
d[0]['theme_name'] = f'Tide Tode {nr}'
schema.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
TEL.write_text(f'{nr}\n')
uit = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT) / f'tide-tode-thema-{nr}.zip'
with zipfile.ZipFile(uit, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted((ROOT / 'theme').rglob('*')):
        if f.is_file() and not any(p.startswith('.') for p in f.relative_to(ROOT / 'theme').parts):
            z.write(f, f.relative_to(ROOT / 'theme'))
print(uit)
