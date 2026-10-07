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
| 1 | 01 Ons verhaal (tas, zand) | 02 Handen vrij (tekst, crème) | 03 Truien (product, rose) |
| 2 | 04 Accessoires (product, baby blue) | 05 Negen stoffen (stofdetail, zand) | 06 Logo (navy) |
| 3 | 07 Zo werkt het (twee boards, zand) | 08 T-shirts (product, crème) | 09 Tekeningen (baby blue) |
| 4 | 10 Repareren (tekst, rose) | 11 Stickers (zand) | 12 Strand (product, crème) |

Elke rij heeft een foto, een vlak en een product, en de soorten wisselen af: tasfoto, grote tekst, product op kleur, stof van dichtbij, logo, tekening en stickers. Er staan alleen eigen beelden in, geen stockfoto's.

## Posts en captions

Kopieer de tekst in het blok. De hashtags kun je ook in de eerste reactie zetten.

### 12 `post-12-strand`

1. Surfponcho Tegel
2. Strandhanddoek Tegel
3. Canvas tas

```
Voor na het surfen. Een poncho om je in om te kleden, een handdoek in de tegelprint en een canvas tas voor je natte spullen.

Link in bio.

#tidetode #strand #surfponcho #noordzee #surfen
```

### 11 `post-11-stickers`

1. Losse stickers op zand
2. Het stickervel

```
Voor je board, je laptop of je koelbox.

Zeven vinyl stickers op één vel. Link in bio.

#tidetode #stickers #surfboard #surfen
```

### 10 `post-10-repareren`

1. STUK? WIJ MAKEN HEM, op rose
2. Draagtas Navy van dichtbij
3. Het label en de naad

```
We maken weinig, en dat goed. Stevige stof, sterke naden en een band die jaren meegaat.

Gaat er toch iets stuk, stuur ons een berichtje. Dan repareren we je tas.

#tidetode #repareren #duurzaam #draagtas #surfen
```

### 09 `post-09-tekeningen`

1. Board met golf, op baby blue
2. Twee boards, crème op navy
3. Het grote board met TIDE TODE langs de rand, op zand
4. De vin, op crème

```
Wat er op de achterkant van onze shirts en truien staat. Eerst getekend, dan pas gedrukt.

#tidetode #illustratie #surfen #noordzee
```

### 08 `post-08-t-shirts`

1. T-shirt Golf
2. T-shirt Board
3. T-shirt Klassiek
4. T-shirt Zon

```
De print op de rug, een klein board op de borst.

Zwaar biologisch katoen, ruime rechte pasvorm. €35, link in bio.

#tidetode #surfkleding #tshirt #biologischkatoen #surfstyle
```

### 07 `post-07-zo-werkt-het`

1. Twee boards in hun tas, met voetstappen in het zand
2. OMDOEN: de tas om het board
3. AANTREKKEN: de band van dichtbij
4. DRAGEN: de rand van de tas over het board

```
Zo werkt de draagtas.

Leg de tas om het midden van je board, op het balanspunt. Trek de band aan. Hang de lus over je schouder en loop.

Op het strand haal je hem er in een paar tellen weer af. Past op softtops en hardboards tot ongeveer 9'6".

#tidetode #draagtas #surfboard #longboard #softtop
```

### 06 `post-06-logo`

1. Het logo in crème op navy
2. Het boardje los, op crème
3. Het liggende logo op rose

```
Tide Tode.

#tidetode #surfen #noordzee
```

### 05 `post-05-negen-stoffen`

1. Schelp
2. Salie
3. Zonsondergang
4. Ruit
5. Tegel Navy
6. Duin

```
Eén tas, negen stoffen. Swipe door zes ervan.

Allemaal dezelfde maat, voor softtops en hardboards. Welke past bij jouw board?

€40, link in bio.

#tidetode #draagtas #surfboard #surfbag #surfnederland
```

### 04 `post-04-accessoires`

1. Bucket hat
2. Pet navy
3. Surfwax koud water
4. Karabijnhaak messing
5. Waxkam

```
De kleine dingen voor een dag aan zee.

Pet en bucket hat met ons board geborduurd. Wax voor koud water, een waxkam en een karabijnhaak voor je sleutels.

Link in bio.

#tidetode #surfgear #surfwax #accessoires #surfen
```

### 03 `post-03-truien`

1. Hoodie Twee boards
2. Sweater Boards
3. Longsleeve Zon
4. Longsleeve Vin
5. UV-shirt lange mouw

```
Het water wordt kouder, de ochtenden ook.

Een UV-shirt om in te surfen, en voor erna een hoodie, sweater of longsleeve.

Link in bio.

#tidetode #surfkleding #noordzee #koudwatersurfen #najaar
```

### 02 `post-02-handen-vrij`

1. HANDEN VRIJ OP WEG NAAR ZEE, op crème
2. Draagtas Tegel op het zand
3. Het label en de band van dichtbij
4. De rand van de tas over het board

```
Board erin, tas over je schouder, handen vrij.

Draagtas Tegel, de stof waar het mee begon. €40, link in bio.

#tidetode #draagtas #surfboard #surfbag #handenvrij
```

### 01 `post-01-ons-verhaal`

1. Draagtas Duin om een navy board op het zand, met het label ONS VERHAAL
2. Twee boards in hun tas, met voetstappen ernaast in het zand
3. Draagtas Salie om een rose board

```
Zo begon het.

Op reis liep ik vaak lang naar een verstopte spot, met een longboard onder mijn arm. De wax schuurde en mijn schouders deden pijn. Touwtjes en spanbanden hielden het niet vol.

Dus maakte ik zelf een tas. Eén stuk stof en één band, zodat je handen vrij zijn.

Veerle

#tidetode #onsverhaal #surftrip #surfen #draagtas
```
