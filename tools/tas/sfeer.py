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
