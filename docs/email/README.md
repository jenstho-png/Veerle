# E-mailworkflow ActiveCampaign

Twee automatische mails voor Tide Tode:

1. **Welkom** na inschrijving voor de nieuwsbrief, met de code WELKOM10
2. **Verlaten winkelwagen**, een herinnering als iemand niet afrekent

| | Welkom | Verlaten winkelwagen |
|---|---|---|
| Bestand | `welkom.html` | `verlaten-winkelwagen.html` |
| Onderwerp | Welkom bij Tide Tode, hier is je 10% korting | Je winkelwagen staat nog klaar |
| Voorbeeldtekst | Met de code WELKOM10 krijg je 10% korting op je eerste bestelling. | We hebben je spullen bewaard. Afrekenen kan wanneer jij wilt. |
| Afzender | Veerle van Tide Tode, hallo@tidetode.nl | Veerle van Tide Tode, hallo@tidetode.nl |

Reserve-onderwerpen voor een A/B-test:

- Welkom: *Je eerste bestelling 10% goedkoper*
- Winkelwagen: *Nog even wachten met de zee?*

## Over de mails

- Gebouwd met tabellen en inline CSS, 600 pixels breed. Op mobiel schuiven de kolommen onder elkaar.
- Letter: Courier Prime via Google Fonts. Lukt dat niet (bijvoorbeeld in Outlook), dan valt hij terug op Courier New. De Tide Tode Display werkt niet betrouwbaar in mail, daarom zijn de koppen in Courier Prime vet en in hoofdletters.
- Kleuren: navy `#22324F`, crème `#F3ECDD`, terracotta `#C0603E`, baby blue `#BFD3EA`, rose `#EDBDB8` en zand `#E3CFAE`.
- Beelden komen van GitHub (`raw.githubusercontent.com/.../docs/producten/beelden/`). Werken ze niet meer, upload ze dan in ActiveCampaign en vervang de links.
- Vervang overal `WINKEL-URL` door het adres van de winkel, bijvoorbeeld `tide-tode.myshopify.com`. In een teksteditor gaat dat met Zoeken en vervangen.
- `%FIRSTNAME%` en `%UNSUBSCRIBELINK%` zijn tags van ActiveCampaign. Die vult het programma zelf in. Heeft iemand geen voornaam ingevuld? Stel dan bij de tag een standaardwaarde in, of verander *Hoi %FIRSTNAME%,* in *Hoi,*.
- Het adres en de KvK in de voet zijn die van Avans, net als in de winkel.

## Voorbereiding

1. **Shopify koppelen.** Installeer in Shopify de app *ActiveCampaign for Shopify* en log in met je ActiveCampaign-account. Dan komen klanten, bestellingen en verlaten winkelwagens vanzelf in ActiveCampaign.
2. **Lijst maken.** Maak in ActiveCampaign een lijst *Nieuwsbrief Tide Tode*. Stel bij de koppeling in dat klanten die bij Shopify *e-mailmarketing accepteren* op deze lijst komen.
3. **Kortingscode.** Maak in Shopify bij Kortingen de code `WELKOM10`: 10% op de hele bestelling, **één keer per klant**. Zet eventueel ook *alleen voor klanten zonder eerdere bestellingen* aan.
4. **Mails maken.** Ga naar Campagnes of naar de automatisering, kies *Nieuwe e-mail* en dan *Eigen HTML* (Custom HTML). Plak de inhoud van het html-bestand. Vul onderwerp en voorbeeldtekst in uit de tabel hierboven.

## Automatisering 1: Welkom

| Stap | Instelling |
|---|---|
| Trigger | **Abonneert zich op een lijst** (Subscribes to a list): *Nieuwsbrief Tide Tode*. Runs: **één keer** per contact |
| Wachten | Geen. De mail gaat direct, dan is de inschrijving nog vers |
| Actie | **E-mail versturen**: Welkom |
| Einde | Automatisering beëindigen |

**Voorwaarden**

- Alleen contacten die zelf hebben ingeschreven (dubbele opt-in aanzetten bij de lijst is het netst voor de AVG).
- Heeft iemand al eerder besteld, dan heeft de code geen zin. Zet direct na de trigger een **Als/Anders**: *Totaal aantal bestellingen* (Shopify) is 0. Ja: welkomstmail. Nee: einde.
- Zet de trigger op één keer, zodat iemand die zich opnieuw inschrijft de code niet nog eens krijgt.

**Mogelijke uitbreiding** (niet verplicht): wacht 3 dagen, controleer met Als/Anders of het contact een bestelling heeft geplaatst. Nee: stuur een korte herinnering aan WELKOM10.

## Automatisering 2: Verlaten winkelwagen

| Stap | Instelling |
|---|---|
| Trigger | **Verlaat winkelwagen** (Abandons cart), winkel: Tide Tode. Wachttijd in de trigger: **1 uur** (aanbevolen door ActiveCampaign). Runs: **telkens** |
| Wachten | Geen extra wachttijd. Het uur zit al in de trigger |
| Voorwaarde | **Als/Anders**: heeft het contact sinds de trigger een bestelling geplaatst? Ja: einde. Nee: verder |
| Actie | **E-mail versturen**: Verlaten winkelwagen |
| Doel (Goal) | **Plaatst een bestelling** (Makes a purchase). Zodra iemand afrekent, springt hij uit de automatisering |
| Einde | Automatisering beëindigen |

**Voorwaarden**

- Werkt alleen als iemand bij het afrekenen zijn e-mailadres heeft ingevuld. Anders weet Shopify niet naar wie de mail moet.
- Stuur hem alleen naar contacten die toestemming gaven voor e-mailmarketing (vinkje bij het afrekenen). Zet dat vinkje in Shopify aan: Instellingen > Afrekenen > Marketingopties.
- Het productblok in de mail is een voorbeeld met de Draagtas Tegel. Haal in de editor van ActiveCampaign het blok tussen `PRODUCTBLOK BEGIN` en `PRODUCTBLOK EIND` weg en zet daar het inhoudsblok **Abandoned cart** neer. Dat vult de echte producten uit de winkelwagen in. Gebruik je alleen Eigen HTML, laat het voorbeeld dan weg en houd alleen de knop.
- De knop gaat naar `/cart`. Wil je dat de klant direct op zijn eigen winkelwagen uitkomt, gebruik dan de link die het Abandoned cart-blok meegeeft.
- Geen korting in deze mail. Zo leer je klanten niet aan om te wachten tot er een code komt.

## Zo test je het

1. Schrijf je in met een eigen adres via de pop-up of de footer. Binnen een paar minuten moet de welkomstmail binnen zijn.
2. Zet een product in de winkelwagen, vul bij het afrekenen je e-mailadres in, vink marketing aan en sluit het venster. Na ongeveer een uur moet de herinnering komen.
3. Reken daarna wel af met testkaart 4242 4242 4242 4242 en WELKOM10. Controleer of je uit de automatisering bent gegaan.
4. Maak screenshots van de automatiseringen en van beide mails voor je verslag.

## Bronnen

- ActiveCampaign, *Abandoned cart overview*: https://help.activecampaign.com/hc/en-us/articles/360001045964-Abandoned-cart-overview
- ActiveCampaign, *How do I create an abandoned cart automation?*: https://help.activecampaign.com/hc/en-us/articles/360001046024-How-do-I-create-an-abandoned-cart-automation
- ActiveCampaign, *Connect your Shopify store to ActiveCampaign*: https://help.activecampaign.com/hc/en-us/articles/115000202150-Connect-your-Shopify-store-to-ActiveCampaign

De namen van knoppen en menu's in ActiveCampaign veranderen soms. Kijk bij twijfel in de helpartikelen hierboven.
