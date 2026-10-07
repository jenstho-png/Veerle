# Wat je nog in Shopify doet

Bijgewerkt op woensdag 7 oktober 2026. Thema: Tide Tode 36.

## A1 en A6. Beleid invullen (verzending, retour, voorwaarden, privacy)

De teksten zijn klaar in `docs/juridisch/ingevuld/`. Open elk bestand in je browser, selecteer alles en kopieer.

1. Ga naar **Instellingen > Beleid**.
2. Plak bij elk beleid de tekst uit het bijbehorende bestand.

| Beleid in Shopify | Bestand |
|---|---|
| Verzendbeleid | `verzendbeleid.html` |
| Restitutiebeleid (retour) | `retourbeleid.html` |
| Servicevoorwaarden | `algemene-voorwaarden.html` |
| Privacybeleid | `privacybeleid.html` (vervangt de lange standaardtekst van Shopify) |

3. Klik op **Opslaan**.

Zolang een beleid leeg is, verbergt het thema de link ernaartoe in de footer en in het blok "Meer informatie". Er staan dus geen links meer die een 404 geven. Zodra je de tekst plakt, komt de link vanzelf terug.

## A2. Herroepingsrecht

De pagina laat nu altijd de herroepingstekst zien, ook als de pagina in Shopify leeg is. Je hoeft niets te doen. Maak alleen de pagina aan als die nog niet bestaat: **Online winkel > Pagina's**, titel "Herroepingsrecht", template `page.juridisch`.

## A3. Social media

1. Maak het Instagram-account en het TikTok-account van Tide Tode aan.
2. Gebruik de bio, de highlights en de posts uit `docs/social/README.md`. De posts staan klaar in `docs/social/post-01` tot en met `post-12`.
3. Vul de links in bij **Online winkel > Thema's > Aanpassen > Thema-instellingen > Social media**.

De iconen verschijnen dan vanzelf in de footer.

## A4. Advertentietools

Installeer via de Shopify App Store en koppel je account:

- **Facebook & Instagram** (Meta-pixel)
- **TikTok**
- **Google & YouTube** (Google-tag)

Zet ook de cookiemelding aan: **Instellingen > Klantprivacy > Cookiebanner**, met Weigeren even groot als Accepteren. Het privacybeleid noemt deze tools al.

## A5. Microsoft Clarity

1. Maak een gratis project op clarity.microsoft.com met de URL van je winkel.
2. Kopieer het project-ID (Settings > Overview, een code van ongeveer tien tekens).
3. Plak het in **Thema-instellingen > Tide-Tode > Microsoft Clarity project-ID**.

Clarity laadt pas als een bezoeker analytische cookies accepteert. Laat je drie medestudenten dus op "Accepteren" klikken. Na een dag zie je hun sessies en heatmaps in Clarity voor bijlage 6.

## A7. Reviews

1. Installeer **Judge.me Product Reviews** (gratis) uit de App Store.
2. Ga naar **Thema aanpassen > Producten > Standaardproduct**, klik bij het koopblok op **Blok toevoegen > Apps** en kies de Judge.me-sterren. Voeg onderaan ook een sectie **Apps** toe met de Judge.me-reviewwidget.
3. Zet bij een paar producten een review (in Judge.me kun je reviews met de hand toevoegen).

## Klein. Titel en deelafbeelding

- De home heet nu "Tide Tode, draagtas voor je surfboard" in de zoekresultaten en de browsertab.
- Plak je een link in WhatsApp, dan komt er een afbeelding mee: de drie boards op het zand met het logo.
- Wil je het zelf instellen, dan kan dat bij **Online winkel > Voorkeuren**.
