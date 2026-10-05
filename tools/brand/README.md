# Tide-Tode merk-tools

- `logo.mjs`: zet "Tide~Tode" uit Fraunces Italic (Soft 100, Wonk, opsz 144, 600) om naar vectorpaden met een getekend golfje, rekent het beeldmerk uit (de maan die het getij draagt) en zet de ronde tekst van het zegel. Schrijft `logo.json`. De vastgezette Fraunces-instanties staan in `fonts/`.
- `icons.py`: de handgeknipte iconen. Vormen worden opgebouwd uit taps toelopende stroken en uitsnijdingen (shapely) en krijgen daarna een licht onregelmatige rand.
- `brandbook.template.html` + `build.py`: bouwt `docs/brandbook/brandbook.html`.

```bash
cd tools/brand && npm install && pip install shapely && npm run build
```
Fraunces staat onder de SIL Open Font License; het logo als vectorpad gebruiken is toegestaan.
