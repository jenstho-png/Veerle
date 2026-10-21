# Koppelingen en apps, stap voor stap

Voor de deadline van donderdag 22 oktober 2026, 12:00. Doe het in deze volgorde. Thema: Tide Tode 39.

## 1. ActiveCampaign (begin hiermee, het kost het meeste tijd)

### Account en koppeling met Shopify
1. Ga naar activecampaign.com en start de gratis proefperiode van 14 dagen met het Tide Tode-mailadres.
2. Installeer in Shopify de app **ActiveCampaign for Shopify** en log daarin in met je nieuwe account. Klanten en bestellingen gaan dan vanzelf naar ActiveCampaign.
3. Maak in ActiveCampaign onder **Contacts > Lists** een lijst: `Tide Tode nieuwsbrief`.

### Kortingscode
Maak in Shopify onder **Kortingen** een code: `WELKOM10`, 10% op de bestelling, één keer per klant.

### Formulier en landingspagina
1. In ActiveCampaign: **Website > Forms > Create a form**, type **Inline form**, lijst `Tide Tode nieuwsbrief`.
2. Velden: Voornaam en E-mail. Knoptekst: `Stuur mijn code`. Bedankt-tekst: `Gelukt! Je code staat in je mail.`
3. Klik op **Integrate > Embed** en kopieer de code.
4. In Shopify: **Online winkel > Pagina's > Pagina toevoegen**, titel `Aanmelden`, template `aanmelden`, tekstvak leeg, opslaan.
5. Ga naar **Thema aanpassen**, open de pagina Aanmelden, klik op de sectie **TT: formulier** en plak de code in **Formuliercode**. Het formulier krijgt vanzelf de stijl van de site.
6. Meld je zelf een keer aan met een tweede mailadres. Dat is je binnengekomen reactie voor het verslag.

De landingspagina staat dan op `/pages/aanmelden`.

### Workflow (Automations > Create an automation > Start from scratch)
- **Start:** Subscribes to list `Tide Tode nieuwsbrief`
- **Mail 1:** meteen
- **Wacht:** 2 dagen
- **Mail 2**
- **Wacht:** 3 dagen
- **Als/anders:** heeft de contactpersoon een bestelling geplaatst (Shopify > Has placed order)?
  - Ja: einde
  - Nee: **Mail 3**

Gebruik in de mails de kleuren van de site: navy `#22324F`, crème `#F3ECDD`, baby blue `#BFD3EA`. Zet het logo bovenaan (`docs/social/profielfoto.png` of het logo uit het merkboek) en een productfoto erin.

**Mail 1**
Onderwerp: `Je 10% korting staat klaar`
Voorbeeldtekst: `Board erin, tas om, handen vrij.`

> Hoi %FIRSTNAME%,
>
> Fijn dat je erbij bent. Hier is je code voor 10% korting op je eerste bestelling:
>
> **WELKOM10**
>
> Vul hem in bij het afrekenen. Hij werkt op alles in de shop, ook op de draagtassen.
>
> Knop: **Naar de shop**
>
> Tot snel,
> Veerle van Tide Tode

**Mail 2**
Onderwerp: `Zo draag je je board zonder handen`
Voorbeeldtekst: `Drie stappen, en je bent onderweg.`

> Hoi %FIRSTNAME%,
>
> De draagtas werkt in drie stappen:
>
> 1. Leg de tas om het midden van je board.
> 2. Trek de band aan.
> 3. Hang de lus over je schouder en loop.
>
> Hij past om softtops en hardboards tot ongeveer 9'6". Twijfel je over je board? Op de maatwijzer zie je meteen of hij past.
>
> Knop: **Past mijn board?** (naar `/pages/maatwijzer`)
>
> Veerle

**Mail 3**
Onderwerp: `Nog geen print gekozen?`
Voorbeeldtekst: `Je code werkt nog.`

> Hoi %FIRSTNAME%,
>
> Je kortingscode **WELKOM10** werkt nog. Er zijn negen prints, van Tegel tot Duin. Allemaal dezelfde stevige tas.
>
> Knop: **Kies je ontwerp** (naar `/collections/draagtassen`)
>
> Gaat er ooit iets stuk, dan repareren we hem.
>
> Veerle

## 2. Microsoft Clarity (bijlage 6)

**Waarom:** voor bijlage 6 laat je drie medestudenten over de site lopen. Clarity neemt hun bezoek op: waar ze klikken, hoe ver ze scrollen en waar ze vastlopen (heatmaps en opnames). Die beelden en je conclusies horen in bijlage 6.

1. Ga naar clarity.microsoft.com en log in met een Microsoft- of Google-account.
2. **Add new project**: naam `Tide Tode`, URL van je winkel.
3. Kies bij installeren **Install manually** en kopieer alleen het project-ID (een code van ongeveer tien tekens, ook te vinden onder Settings > Overview).
4. In Shopify: **Thema aanpassen > Thema-instellingen > Tide-Tode > Microsoft Clarity project-ID**, plakken, opslaan.
5. Zet de cookiebanner aan (zie stap 4) en laat je medestudenten op **Accepteren** klikken. Geef ze het winkelwachtwoord en een opdracht, bijvoorbeeld: zoek een tas die bij een softtop van 8 voet past en leg hem in je winkelwagen.
6. Binnen een paar uur staan hun sessies in Clarity onder **Recordings** en **Heatmaps**. Maak daar je screenshots.

## 3. Shopify Payments in testmodus
1. **Instellingen > Betalingen > Shopify Payments activeren**.
2. Vul de bedrijfsgegevens in met KvK `41104408` (Avans).
3. Zet onder **Testmodus** het vinkje aan en sla op.
4. Controleer dat iDEAL, Bancontact en creditcard aan staan.
5. Doe een testbestelling met een testkaart (Shopify toont de nummers in de testmodus). Die bestelling is ook handig voor ActiveCampaign.

## 4. Advertentietools, verzending en cookies
Installeer in de Shopify App Store en koppel je account:

| App | Waarvoor |
|---|---|
| **Facebook & Instagram** (van Meta) | Meta-pixel en je Instagram-shop |
| **TikTok** | TikTok-pixel |
| **Google & YouTube** | Google-tag en Google Analytics |
| **PostNL** | Verzendlabels Nederland |
| **DHL Parcel** (of DHL eCommerce) | Verzendlabels Nederland en België |

Cookiebanner: **Instellingen > Klantprivacy > Cookiebanner** aanzetten, regio Europa, met Weigeren even groot als Accepteren.

Pixels: zet in elke app de **gegevensdeling op Maximaal** (of Verbeterd), dan staat ook de conversietracking aan.

## 5. Reviews met Judge.me
Makkelijk, ongeveer tien minuten.

1. Installeer **Judge.me Product Reviews** (gratis).
2. In Judge.me: klik op **Enable** bij de app-embed. Zet in **Thema aanpassen > App-embeds** Judge.me aan.
3. Ga in **Thema aanpassen** naar een productpagina. Voeg bij het koopblok het blok **Judge.me Star Rating** toe en onderaan een sectie **Apps** met **Judge.me Review Widget**.
4. Laat je drie medestudenten na de Clarity-test een echte review schrijven via het formulier op de productpagina. Zo heb je echte reviews en hoef je er niets voor te verzinnen.

## 6. Juridische pagina's (herinnering)
Maak deze pagina's aan met een leeg tekstvak en het juiste template:

| Titel | Template |
|---|---|
| Verzending | `verzending` |
| Retourneren | `retourneren` |
| Herroepingsrecht | `herroepingsrecht` |
| Algemene voorwaarden | `algemene-voorwaarden` |
| Privacybeleid | `privacy` |
| Cookiebeleid | `cookiebeleid` |
| Bestelling herroepen | `herroepen` |
| Aanmelden | `aanmelden` |

Plak ook het privacybeleid in **Instellingen > Beleid** (tekst uit `docs/juridisch/ingevuld/privacybeleid.html`).

## 7. Social media
1. Maak het Instagram-account aan (zakelijk account) met de bio uit `docs/social/feed-2/README.md`.
2. Post de negen posts uit `docs/social/feed-2`, van 09 naar 01.
3. Vul de link in bij **Thema-instellingen > Social media**. Dan staat het icoon in de footer.
