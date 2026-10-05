# Merkstijl voor Shopify

Dit pakket bevat de structuur van de stijl: textuur, letterschaal, ruimte, hoeken, schaduwen en beweging.

- Er staat geen merknaam, logo of eigen kleur in.
- Kleuren en letters komen uit het thema waar je het in zet.
- Alle bestanden en klassen beginnen met `mk-`, zodat niets botst met je thema.
- Gecontroleerd met Shopify Theme Check: 0 fouten en 0 waarschuwingen.

## Wat zit erin

| Map | Bestand | Wat |
|---|---|---|
| assets | `mk-stijl.css` | Alle stijl. Zie het overzicht hieronder. |
| assets | `mk-stijl.js` | Scroll-beweging (vanilla JS, geen libraries). Werkt ook in de thema-editor. |
| assets | `mk-papier-licht.webp/.png` | Papiertextuur voor lichte vlakken: een naadloze tegel van 400×400. |
| assets | `mk-papier-donker.webp/.png` | Korrel voor donkere vlakken. |
| snippets | `mk-stijl.liquid` | Laadt alles in één keer. |
| sections | `mk-intro.liquid` | Grote kop, tekst en knoppen die na elkaar opkomen. |
| sections | `mk-woorden.liquid` | Een zin waarvan de woorden oplichten tijdens het scrollen. |
| sections | `mk-vlak.liquid` | Donker vlak met korrel, tekst en een schermbeeld in een telefoon of laptop. |
| sections | `mk-chaos.liquid` | Losse berichtjes die bij het scrollen in één telefoonscherm opgaan. |

## Installeren

1. Ga in Shopify naar **Online Store › Thema's**. Kies bij je thema **… › Code bewerken**.
2. Upload bij **Assets** de zes bestanden uit `assets/`.
3. Maak bij **Snippets** een nieuw snippet `mk-stijl` en plak de inhoud van `snippets/mk-stijl.liquid` erin.
4. Doe hetzelfde bij **Sections** voor de vier bestanden uit `sections/`. Gebruik dezelfde namen.
5. Open `layout/theme.liquid` en zet vlak voor `</head>`:
   ```liquid
   {% render 'mk-stijl', papier: true, leesbalk: true %}
   ```
   - `papier: true` legt de papiertextuur over de achtergrond van de hele pagina.
   - `leesbalk: true` zet een dun balkje bovenaan dat meeloopt met het scrollen.
   - Laat de opties weg die je niet wilt.
6. Ga naar **Aanpassen** en voeg de secties toe. Ze heten **Merk: intro**, **Merk: oplichtende zin**, **Merk: donker vlak** en **Merk: berichtjes-chaos**.

Werk je met de Shopify CLI, zet dan de mappen in je thema en push alleen die bestanden:
`shopify theme push --only assets/mk-* --only snippets/mk-* --only sections/mk-*`

## Kleuren: komen uit je thema

De stijl leest de kleuren van het **kleurenschema** dat je per sectie kiest:

- **Tekst:** `--color-foreground`.
- **Achtergrond:** `--color-background`.
- **Accent:** `--color-button` en `--color-button-text`. Gebruikt voor accentwoord, knop, icoontjes en leesbalk.

Zachte tinten, lijnen, schaduwen en het donkere vlak worden daaruit berekend. Kies je in Shopify een kleurrijke knopkleur, dan wordt het accentwoord in koppen een mooi verloop. Is je knop zwart, dan is het accent ook zwart en grijs.

Dit werkt direct in Dawn en de andere gratis Shopify-thema's met kleurenschema's (versie 10 of hoger). Gebruik je een thema dat het anders doet, of wil je toch vaste kleuren? Zet dan bij **Thema-instellingen › Aangepaste CSS**:

```css
:root {
  --mk-eigen-tekst: #1b1b1b;
  --mk-eigen-achtergrond: #f6f3ee;
  --mk-eigen-accent: #b05c34;
  --mk-eigen-op-accent: #ffffff;
  --mk-eigen-donker: #163428;   /* kleur van het donkere vlak */
}
```

In de sectie **Merk: donker vlak** kun je de kleur van het vlak ook gewoon kiezen.

## Letters

De stijl neemt de kop- en tekstletter van je thema over (`--font-heading-family` en `--font-body-family`). Koppen staan in dikte 900 met strakke letterafstand. Kies daarom in je thema een koppenletter die een echte black/900 heeft.

Wil je één woord in een handschrift (`mk-handschrift`)? Zet dan `--mk-eigen-font-accent: "Jouw Letter", cursive;` in de aangepaste CSS. Gebruik dat hooguit één keer per pagina.

## Zelf gebruiken in een blok "Aangepaste Liquid"

```html
<h2 class="mk-h2 mk-in">Een kop met een <em>accentwoord</em></h2>
<p class="mk-lead mk-in mk-na-1">Tekst die net na de kop opkomt.</p>
<a class="mk-knop mk-knop--vol mk-in mk-na-2" href="/collections/all">Bekijk alles <span class="mk-pijl">→</span></a>
```

| Klasse | Wat |
|---|---|
| `mk-papier` | Papiertextuur op een licht vlak. |
| `mk-korrel` | Korrel op een donker of gekleurd vlak, onder de inhoud. |
| `mk-vlak` | Donker vlak met een zachte lichtvlek linksboven (combineer met `mk-korrel`). |
| `mk-hero`, `mk-statement`, `mk-h2`, `mk-lead`, `mk-label` | De letterschaal. Een `<em>` in een kop wordt het accentwoord. |
| `mk-knop mk-knop--vol` / `mk-knop--rand` | Ronde knoppen. `mk-pijl` schuift mee bij hover. |
| `mk-kaart`, `mk-optillen` | Kaart met zachte schaduw. Hij komt omhoog bij hover. |
| `mk-in` | Komt één keer op zodra het in beeld komt. Varianten: `mk-in--links`, `--rechts`, `--zoom`, `--vervaag`, `--plop`. |
| `mk-na-1` … `mk-na-4` | 0,1 tot 0,4 seconde later opkomen, voor een rustige volgorde. |
| `mk-telefoon` + `mk-telefoon-scherm` | Telefoon in CSS. Zet er een `<img>` in van 1290×2796. |
| `mk-laptop-rand` + `mk-laptop-scherm` + `mk-laptop-voet` | Laptop in CSS, met een scherm in 16:10. |
| `data-mk-parallax="-0.05"` | Beweegt rustig mee met het scrollen. |
| `data-mk-kantel="9"` | Kantelt zacht mee met de muis. |
| `data-mk-woorden` | Woorden lichten op tijdens het scrollen. |

## Beweging in het kort

- **Curve:** overal dezelfde, `cubic-bezier(0.16, 1, 0.3, 1)`. Die gaat snel van start en loopt heel zacht uit.
- **Opkomen in beeld:** 850 ms. Het blok schuift 48 px omhoog en groeit van 96% naar 100%. Dat gebeurt één keer, nooit opnieuw.
- **Volgorde:** het volgende blok komt 100 ms later.
- **Hover:** 150 ms voor kleur, 350 ms voor optillen.
- **Vastgezette secties:** het scrollen zelf is de tijdlijn. Er zit geen smooth-scroll-library in, het is de gewone scroll van de browser.
- **Minder beweging:** staat bij een bezoeker "minder beweging" aan, dan staat alles meteen stil op de eindstand.
- **Thema-editor:** daar staat alles meteen zichtbaar, zodat je rustig kunt bewerken.

Zie `MERKSTIJL.md` voor de ontwerpregels en wat er juist niet in mag.
