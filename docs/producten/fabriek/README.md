# Productfoto's draagtas

Gemaakt met fotobewerking uit de fabrieksfoto (`fabrieksfoto.jpg`), zonder AI.

- `tools/tas/stof.py`: knipt de tegels die vrij zijn van de band uit de foto en legt er een schone lap van (`stof-lap.jpg`).
- `tools/tas/scene.py`: bouwt de afgewerkte tas op een crème board in een studio (flat lay van bovenaf): echte stof, zoom met stiksel, geweven label, doorlopende nylon band met ingeweven logo en stiksels. Maakt per ontwerp drie beelden in `docs/producten/beelden/` en zet de Tegel-beelden ook in het thema (`tt-product-1` tot en met `3`).
- `tools/tas/lifestyle.py`: zet de tas op een board in bestaande sfeerfoto's (`lifestyle-*.jpg`).

Bandbreedte en kleur zijn gemeten op de fabrieksfoto. Het zijn visualisaties van de afgewerkte tas: vervang ze door echte foto's zodra de tas gestikt is.

Opnieuw maken: `python3 tools/tas/scene.py && python3 tools/tas/lifestyle.py`
