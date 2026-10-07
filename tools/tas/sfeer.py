"""Sfeerbeelden: de draagtas op echte boards uit stockfoto's (docs/producten/stock/lifestyle).

1. Board opmeten: tools/tas/sfeer_meet.py (GrabCut + hints in sfeer_hints.json) -> maskers/ en bronnen.json.
2. Tas erop leggen: tools/tas/sfeer_tas.py
   - het vak volgt de echte omtrek van het board (en loopt om de rails, nooit buiten het silhouet),
     midden op het balanspunt (halverwege neus en staart), lengte uit de studiomaten;
   - één doorlopende band: om de lange rail, over het vak, uit de andere rail als lus;
   - staat het board, dan hangt de lus met de zwaartekracht; ligt het board plat, dan ligt de lus plat ernaast;
   - licht, kleur, korrel en scherpte van de foto.
`python3 tools/tas/sfeer.py [naam ...]`
"""
import pathlib, sys
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
sys.path.insert(0, str(HIER))
import scene as SC  # noqa: E402
import sfeer_tas as ST  # noqa: E402

STOCK = ROOT / 'docs' / 'producten' / 'stock' / 'lifestyle'
UIT = ROOT / 'docs' / 'producten' / 'fotos'

# naam: (stockfoto, ontwerp, instellingen voor sfeer_tas.maak)
LIJST = {
    'witte-muur-tegel': ('board-muur-4.jpg', 'draagtas-tegel', dict(lus=1, belicht=1.15, schaduw=(-6, 5, 0.35, 6), lus_schaduw=(-14, 5, 0.3, 5))),
    'oker-muur-ruit': ('board-muur-3.jpg', 'draagtas-ruit', dict(lus=1, belicht=0.85, tint=(1.02, 1.0, 0.96), schaduw=(-4, 5, 0.3, 8), lus_schaduw=(-8, 6, 0.25, 8))),
    'rood-board-golfjes': ('board-zand-1.jpg', 'draagtas-golfjes', dict(lus=1, albedo=0.8, schaduw=(4, 5, 0.3, 6))),
    'zonsondergang-zand': ('board-zand-2.jpg', 'draagtas-zonsondergang', dict(lus=-1, albedo=0.8, tint=(1.04, 1.0, 0.93), schaduw=(2, 4, 0.25, 8))),
    'geel-board-navy': ('board-zand-3.jpg', 'draagtas-navy', dict(lus=1, albedo=0.8, lift=0.04, schaduw=(2, 4, 0.25, 8))),
    'strand-tegel-navy': ('board-persoon-1.jpg', 'draagtas-tegel-navy', dict(lus=-1, albedo=0.85, schaduw=(3, 5, 0.25, 8))),
    'gras-schelp': ('board-gras-1.jpg', 'draagtas-schelp', dict(lus=-1, plat=True, albedo=0.9, tint=(1.04, 1.0, 0.92), schaduw=(6, 6, 0.35, 5), lus_schaduw=(8, 8, 0.45, 5))),
    'kever-salie': ('board-auto-1.jpg', 'draagtas-salie', dict(lus=-1, albedo=0.85, schaduw=(3, 4, 0.3, 6), lus_schaduw=(4, 3, 0.3, 4))),
}


def maak(naam, debug=False):
    bestand, handle, opties = LIJST[naam]
    foto = np.asarray(Image.open(STOCK / bestand).convert('RGB')).astype(np.float32) / 255
    uit = ST.maak(foto, bestand, handle, debug=debug, **opties)
    if debug:
        return uit
    SC.bewaar(uit, UIT / f'sfeer-{naam}.jpg', max_kb=195)
    print('sfeer', naam, (UIT / f'sfeer-{naam}.jpg').stat().st_size // 1000, 'kB')


if __name__ == '__main__':
    keuze = sys.argv[1:] or list(LIJST)
    for n in keuze:
        maak(n)
