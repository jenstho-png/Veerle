# Social media

De Instagram-posts zijn carrousels: staand 4:5 (1080 x 1350, jpg), met 3 tot 6 slides per post. Elke post heeft een eigen map met `slide-1.jpg`, `slide-2.jpg` enzovoort. Upload de slides in die volgorde.

De foto's doen het werk. Op de meeste slides staat geen tekst, en waar wel staat er hooguit één korte regel.

Opnieuw maken (na nieuwe productfoto's bijvoorbeeld):

```
python3 tools/social/carrousels.py
```

Dat script snijdt de foto's bij tot 4:5, zet waar nodig de tekst erop (gerenderd met Playwright Chromium) en maakt `raster-voorbeeld.jpg`. Oude posts in deze map worden eerst weggehaald. Profielfoto, highlights en Facebook-header komen uit `python3 tools/social/posts2.py`.

## Wat er in de map staat

| Bestand | Waarvoor |
|---|---|
| `post-01-...` tot en met `post-12-...` | Twaalf carrousels, elk een map met slides (1080 x 1350, jpg) |
| `raster-voorbeeld.jpg` | Zo ziet je profiel eruit met de eerste slide van elke post. Niet posten |
| `profielfoto.png` | Voor Instagram, TikTok, Facebook en Pinterest. Instagram maakt hem rond |
| `highlight-*.png` | Covers voor de highlights: Tassen, Kleding, Gear, Onderweg, Strand en Info |
| `facebook-header.png` | Omslagfoto voor Facebook (1640 x 624). Logo en tekst staan in het midden, zodat niets wegvalt op mobiel |

## Profiel

**Naam:** Tide Tode

**Bio:**

```
Voor de weg naar zee
Draagtassen voor je surfboard, surfkleding en gear
Board erin, tas over je schouder, handen vrij
```

Zet de link naar de winkel eronder.

**Highlights**, van links naar rechts:

| Highlight | Cover | Wat erin komt |
|---|---|---|
| TASSEN | `highlight-tassen.png` | De negen draagtassen, hoe je hem omdoet |
| KLEDING | `highlight-kleding.png` | T-shirts, longsleeves, hoodie, sweater, UV-shirt, poncho, pet en bucket hat |
| GEAR | `highlight-gear.png` | Surfwax, waxkam, karabijnhaken, stickers |
| ONDERWEG | `highlight-onderweg.png` | Foto's en filmpjes van onderweg naar de spot |
| STRAND | `highlight-strand.png` | Drie dingen mee van het strand, reparaties, verpakking |
| INFO | `highlight-info.png` | Verzending, retour, maatwijzer, contact |

## Volgorde van posten

Post van 12 naar 01. Dan staat 01 linksboven in je raster, zoals in `raster-voorbeeld.jpg`. Twaalf posts maken vier volle rijen.
De eerste slides wisselen af in kleur: zand, crème, rose en baby blue. Twee vlakken met dezelfde kleur staan nooit naast of onder elkaar.

| Rij | Links | Midden | Rechts |
|---|---|---|---|
| 1 | 01 Ons verhaal | 02 Draagtas Tegel | 03 T-shirts |
| 2 | 04 Accessoires | 05 Alle draagtassen | 06 Surfwax |
| 3 | 07 Zo werkt het | 08 Najaar | 09 Draagtas Zonsondergang |
| 4 | 10 Op het board | 11 Logo | 12 Tekeningen |

## Posts en captions

Kopieer de tekst in het blok. De hashtags kun je ook in de eerste reactie zetten.

### 12 `post-12-tekeningen`

1. Het grote board met TIDE TODE langs de rand, op zandkleurig papier
2. Twee boards naast elkaar, crème op navy
3. Board met golf, op baby blue
4. De vin, op crème

```
Wat er op de achterkant van onze shirts en truien staat. Eerst getekend, dan pas gedrukt.

#tidetode #illustratie #surfen #noordzee
```

### 11 `post-11-logo`

1. Het logo in crème op navy
2. Het boardje los, op crème
3. Het liggende logo op rose

```
Tide Tode.

#tidetode #surfen #noordzee
```

### 10 `post-10-op-het-board`

1. Tegel om een rood board op het strand
2. Tegel om een board tegen een betonnen muur
3. Zonsondergang om een fish tegen een lemen muur
4. Ruit om een zwart board bij een witte muur
5. Salie om een board bij een gele muur

```
Om elk board. Van een rode longboard tot een kleine fish.

#tidetode #draagtas #surfboard #surfbag #surfen
```

### 09 `post-09-draagtas-zonsondergang`

1. Op rose papier, met het label ZONSONDERGANG
2. Op het zand
3. Het label en de band van dichtbij
4. De rand van de tas over het board

```
Draagtas Zonsondergang.

Brede strepen in rose, zand, terracotta en crème, met een terracotta band. De kleuren van de lucht na een avondsessie.

€40, link in bio.

#tidetode #draagtas #surfboard #surfbag #surfen
```

### 08 `post-08-najaar`

1. UV-shirt lange mouw, met het label NAJAAR
2. Hoodie Twee boards
3. Sweater Boards
4. Longsleeve Vin
5. Longsleeve Zon
6. Surfponcho

```
Het water wordt kouder, de ochtenden ook.

UV-shirt om in te surfen, en voor erna een hoodie, sweater, longsleeve of de poncho om je naast de auto om te kleden.

Swipe door de zes. Alles in de shop, link in bio.

#tidetode #surfkleding #noordzee #koudwatersurfen #najaar
```

### 07 `post-07-zo-werkt-het`

1. OMDOEN: de tas om het board, op het zand
2. AANTREKKEN: de band van dichtbij
3. DRAGEN: met het board in je armen aan zee
4. LOPEN: het duinpad naar het strand

```
Zo werkt de draagtas.

Leg de tas om het midden van je board, op het balanspunt. Trek de band aan. Hang de lus over je schouder en loop.

Op het strand haal je hem er in een paar tellen weer af. Past op softtops en hardboards tot ongeveer 9'6".

#tidetode #draagtas #surfboard #longboard #softtop
```

### 06 `post-06-surfwax`

1. Koud water, met het label KOUD
2. De wax op een board
3. Koel water, met het label KOEL
4. Warm water, met het label WARM
5. De waxkam

```
Drie soorten wax, voor drie temperaturen.

Koud onder 14 graden, koel van 14 tot 19, warm daarboven. In het najaar op de Noordzee pak je koud.

Bijenwas en kokosolie, 70 gram, €5. De waxkam is €6.

#tidetode #surfwax #noordzee #surfgear #surfen
```

### 05 `post-05-alle-draagtassen`

1. Salie, met het label NEGEN STOFFEN
2. Ruit
3. Tegel Navy
4. Schelp
5. Duin
6. Navy

```
Eén tas, negen stoffen. Hier zie je er zes. Tegel, Golfjes en Zonsondergang komen in andere posts langs.

Allemaal dezelfde maat, voor softtops en hardboards. Welke past bij jouw board?

€40, link in bio.

#tidetode #draagtas #surfboard #surfbag #surfnederland
```

### 04 `post-04-accessoires`

1. Pet navy
2. Bucket hat
3. Karabijnhaak messing
4. Strandhanddoek tegel
5. Canvas tas
6. Stickerset

Geen tekst op de slides.

```
De kleine dingen voor een dag aan zee.

Pet en bucket hat met ons board geborduurd. Een karabijnhaak voor je sleutels, een strandhanddoek in de tegelprint, een canvas tas voor je wetsuit en lunch, en een vel stickers.

Link in bio.

#tidetode #strand #surfgear #accessoires #surfen
```

### 03 `post-03-t-shirts`

1. T-shirt Golf, met het label T-SHIRTS
2. T-shirt Board
3. T-shirt Klassiek
4. T-shirt Zon
5. T-shirt Lijn naar zee
6. T-shirt Op weg naar zee

```
Zes T-shirts, allemaal met de print op de rug en een klein board op de borst.

Zwaar biologisch katoen, ruime rechte pasvorm. Lijn naar zee heeft onze spots van Petten tot Domburg erop.

€35, link in bio.

#tidetode #surfkleding #tshirt #biologischkatoen #surfstyle
```

### 02 `post-02-draagtas-tegel`

1. Op het zand, met het label DRAAGTAS TEGEL
2. Het label en de band van dichtbij
3. De rand van de tas over het board
4. Op rose papier

```
Draagtas Tegel, de stof waar het mee begon.

Geweven tegels in rood, terracotta, blauw, groen en crème. Het patroon loopt over de hele rol, dus elke tas valt net iets anders.

€40, link in bio.

#tidetode #draagtas #surfboard #surfbag #tegels
```

### 01 `post-01-ons-verhaal`

1. De tas om een board tegen het busje, met het label ZO BEGON HET
2. Het pad door de duinen
3. Voeten in het zand
4. Het strand bij zonsondergang, met Veerle in handschrift

```
Zo begon het.

Op reis liep ik vaak lang naar een verstopte spot, met een longboard onder mijn arm. De wax schuurde en mijn schouders deden pijn. Touwtjes en spanbanden hielden het niet vol.

Dus maakte ik zelf een tas. Eén stuk stof en één band, zodat je handen vrij zijn.

Veerle

#tidetode #onsverhaal #surftrip #surfen #draagtas
```

## Wat er is veranderd

- De twaalf vierkante posts zijn vervangen door negen carrousels in 4:5. Dat formaat neemt op Instagram meer ruimte in het scherm in.
- Bijna geen tekst meer op de beelden. De uitleg staat in de caption.
- Elke post heeft nu een eigen map met slides.
- Het handschrift staat maar op één slide in de hele set: de naam Veerle in post 01.
- `tools/social/carrousels.py` maakt de posts. `tools/social/posts2.py` maakt alleen nog profielfoto, highlights en Facebook-header.
