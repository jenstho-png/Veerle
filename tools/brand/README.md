# Tide-Tode merk-tools

- `logo.mjs`: zet "Tide~Tode" uit Fraunces Italic (Soft 100, Wonk, opsz 144, 600) om naar vectorpaden met een getekend golfje, rekent het beeldmerk uit (de maan die het getij draagt) en zet de ronde tekst van het zegel. Schrijft `logo.json`. De vastgezette Fraunces-instanties staan in `fonts/`.
- `icons.py`: de handgeknipte iconen. Vormen worden opgebouwd uit taps toelopende stroken en uitsnijdingen (shapely) en krijgen daarna een licht onregelmatige rand.
- `brandbook.template.html` + `build.py`: bouwt `docs/brandbook/brandbook.html`.
- `richtingen.py` + `build_richtingen.py`: drie extra logorichtingen (Handen vrij, De weg naar de spot, Het golfje), elk met eigen beeldmerk en lettertype, plus de vergelijkingspagina `docs/brandbook/logorichtingen.html`. Letters gaan via fontTools naar vectorpaden; de vastgezette lettertypes staan in `fonts/`.

```bash
cd tools/brand && npm install && pip install shapely fonttools brotli && npm run build && python3 richtingen.py && python3 build_richtingen.py
```
Fraunces staat onder de SIL Open Font License; het logo als vectorpad gebruiken is toegestaan.
