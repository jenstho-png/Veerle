# Social media

Alles in deze map komt uit `tools/social/posts2.py`. Opnieuw maken (na nieuwe productfoto's bijvoorbeeld):

```
python3 tools/social/posts2.py
```

Het script maakt de tekstposts en covers als html, rendert ze met Playwright Chromium en snijdt de studiofoto's vierkant bij. Oude posts in deze map worden daarbij eerst weggehaald.

## Wat er in de map staat

| Bestand | Waarvoor |
|---|---|
| `post-01` tot en met `post-12` | Twaalf vierkante posts (1080 x 1080, jpg) die samen het raster vormen |
| `raster-voorbeeld.jpg` | Zo ziet je profiel eruit als alle twaalf posts staan. Niet posten |
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

Post van 12 naar 01. Dan staat 01 linksboven in je raster, zoals in `raster-voorbeeld.jpg`.
Het raster is opgebouwd in kleuren die elkaar afwisselen: navy, zand, baby blue, crème, rose en terracotta. Twee vlakken met dezelfde kleur staan nooit naast of onder elkaar.

| Rij | Links | Midden | Rechts |
|---|---|---|---|
| 1 | 01 Merk | 02 Draagtas Tegel | 03 T-shirt Board |
| 2 | 04 Onderweg | 05 Drie dingen van het strand | 06 Pet navy |
| 3 | 07 Longsleeve Zon | 08 Draagtas Golfjes | 09 Ons verhaal |
| 4 | 10 Zo werkt de draagtas | 11 Surfwax koud water | 12 Draagtas Zonsondergang |

## Captions

Kopieer de tekst onder elk bestand. De hashtags kun je ook in de eerste reactie zetten.

### 12 `post-12-draagtas-zonsondergang.jpg`

```
De kleuren van de lucht na een avondsessie.

Draagtas Zonsondergang heeft brede strepen in rose, zand, terracotta en crème, met een terracotta band. De warmste van de negen, en mooi op een licht board.

Leg hem om je board, band aan, over je schouder en lopen.

€40, link in bio.

#tidetode #draagtas #surfboard #surfbag #opwegnaarzee #surfen #surfnederland #longboard
```

### 11 `post-11-surfwax-koud.jpg`

```
Noordzee in het najaar? Dan wil je koude wax.

Onze surfwax voor koud water is voor zee onder 14 graden. Hij is zachter, zodat hij ook in de kou goed blijft plakken. Bijenwas en kokosolie, 70 gram, in een papieren wikkel zonder plastic.

Er is ook wax voor koel en warm water.

€5, link in bio.

#tidetode #surfwax #noordzee #koudwatersurfen #surfgear #surfen #surfnederland #winterssurfen
```

### 10 `post-10-zo-werkt-het.jpg`

```
Zo werkt de draagtas.

1 Leg de tas om het midden van je board, op het balanspunt
2 Trek de band aan. Die loopt in één stuk rondom
3 Hang de lus over je schouder en loop

Op het strand haal je hem er in een paar tellen weer af. Je natte, zanderige board mag er gewoon in.

Past op softtops en hardboards tot ongeveer 9'6".

#tidetode #draagtas #surfboard #surfbag #softtop #longboard #surftrip #handenvrij
```

### 09 `post-09-verhaal.jpg`

```
Zo begon het.

Op reis liep ik vaak lang naar een verstopte spot, met een longboard onder mijn arm. De wax schuurde, mijn schouders deden pijn en op de scooter stuurde ik met één hand. Touwtjes, spanbanden en hoezen hielden het niet vol.

Dus maakte ik zelf een tas. Eén stuk stof en één band, zodat je board erin gaat en je handen vrij zijn.

Veerle

#tidetode #onsverhaal #surftrip #surfen #surfboard #draagtas #opwegnaarzee
```

### 08 `post-08-draagtas-golfjes.jpg`

```
Golfjes. Baby blue op navy, met een lichtblauwe band.

Een eenvoudig patroon dat je van ver herkent. En het donkere navy houdt zand en vlekken goed verborgen.

€40, link in bio.

#tidetode #draagtas #surfboard #surfbag #opwegnaarzee #surfen #surfnederland #golfjes
```

### 07 `post-07-longsleeve-zon.jpg`

```
Voor koele ochtenden.

Longsleeve Zon is crème, met op de rug de grote zon en TIDE TODE eromheen. Fijn onder een jas als je in het voorjaar naar de spot fietst.

Biologisch katoen, print met inkt op waterbasis.

€45, link in bio.

#tidetode #surfkleding #longsleeve #biologischkatoen #opwegnaarzee #surfen #surfstyle
```

### 06 `post-06-pet-navy.jpg`

```
Pet navy. Katoen, met ons board in crème geborduurd op de voorkant.

Verstelbaar aan de achterkant, dus één maat. De klepsticker haal je eraf of laat je zitten.

€30, link in bio.

#tidetode #pet #surfkleding #surfstyle #opwegnaarzee #surfen #navy
```

### 05 `post-05-drie-dingen.jpg`

```
Neem drie dingen mee van het strand.

Elke keer dat je gaat surfen. Een dop, een stuk touw of visdraad, een stukje plastic. Het kost je een minuut op de weg terug naar je board.

Doe je mee? Zet een foto in je story en tag ons.

#tidetode #driedingen #schoonstrand #strandopruimen #beachcleanup #noordzee #surfen #duurzaam
```

### 04 `post-04-onderweg.jpg`

```
Geparkeerd, board eruit, tas erom. Op naar de golven.

Voor de stukken waar je board niet zelf heen loopt: door de duinen, over de rotsen of vanaf de bus.

#tidetode #onderweg #surftrip #roadtrip #vanlife #surfboard #draagtas #opwegnaarzee
```

### 03 `post-03-t-shirt-board.jpg`

```
T-shirt Board. Zwaar zandkleurig katoen, met op de borst een klein board.

Draai hem om: op de rug staat ons board zo groot als de rug het toelaat, met TIDE TODE langs de rail. Zoals een shaper zijn naam op een board zet.

100% biologisch katoen, ruime rechte pasvorm. €35, link in bio.

#tidetode #surfkleding #tshirt #biologischkatoen #surfstyle #opwegnaarzee #surfen
```

### 02 `post-02-draagtas-tegel.jpg`

```
Het origineel.

Draagtas Tegel is de stof waar Tide Tode mee begon. Een patchwork van geweven tegels in rood, terracotta, blauw, groen en crème. Het patroon loopt over de hele rol, dus elke tas valt net iets anders.

Eén maat voor softtops en hardboards. €40, link in bio.

#tidetode #draagtas #surfboard #surfbag #opwegnaarzee #surfen #surfnederland #tegels
```

### 01 `post-01-merk.jpg`

```
Tide Tode. Voor de weg naar zee.

Het begon met één draagtas voor je surfboard. Nu maken we ook surfkleding en gear voor onderweg: T-shirts, longsleeves, een hoodie, surfwax en karabijnhaken.

Kijk rond in de shop, link in bio.

#tidetode #opwegnaarzee #surfen #surfboard #surfkleding #surfgear #surfnederland #draagtas
```

## Wat er is veranderd

- De oude posts met het T-shirt Zonsopkomst en de Hoodie busje zijn weg. Die producten bestaan niet meer.
- Alle posts zijn nu vierkant en gebruiken de nieuwe studiofoto's.
- Highlights: Zon en Stranddag zijn vervangen door Kleding, Gear en Strand, zodat het hele assortiment erin past.
- De bio en de Facebook-header noemen nu ook kleding en gear, met de zin "Voor de weg naar zee".
- `tools/social/social.py` en `render.mjs` zijn vervangen door `tools/social/posts2.py`.
