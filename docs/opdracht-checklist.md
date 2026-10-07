# Checklist webshop Tide-Tode (E-commerce vaardigheden blok 5)

Bijgewerkt op woensdag 7 oktober 2026.

- ✅ = klaar in het thema of in deze map
- 🛠 = jij moet het in Shopify instellen (de stappen staan erbij)
- 📝 = voor school, dat doe jij

## 1. Verplichte onderdelen

| Eis | Status | Wat er is / wat jij doet |
|---|---|---|
| Eigen lay-out, geen standaard themalook | ✅ | Eigen secties in de Tide-Tode huisstijl (merkboek), eigen letters, iconen, stickers en tekeningen |
| Geen standaardteksten, ook knoppen en footer | ✅ | Alle teksten zelf geschreven. 🛠 Controleer na publiceren de winkelwagen en het afrekenen: die teksten pas je aan via Online winkel > Thema's > ... > Standaardthemacontent bewerken |
| Minimaal 20 eigen producten | ✅ | 27 producten in `docs/producten/producten.csv`. 🛠 Importeren via Producten > Importeren. 📝 Maak daarna screenshots van de gepubliceerde producten |
| Minstens drie collecties | ✅ | Draagtassen, Surfgear, Kleding en accessoires. 🛠 Aanmaken als automatische collecties op tag, zie `docs/producten/overzicht.md` |
| Privacybeleid, algemene voorwaarden, veelgestelde vragen | ✅ | Teksten in `docs/juridisch/`, FAQ-pagina bestaat al. 🛠 Plakken in Instellingen > Beleid, zie `docs/juridisch/README.md` |
| Herroepingsrecht en modelformulier | ✅ | `docs/juridisch/herroepingsrecht.html`. 🛠 Pagina "Herroepingsrecht" aanmaken met template `page.juridisch` |
| Over ons, retourbeleid en contact | ✅ | Over ons (`page.over-ons`), retourbeleid in `docs/juridisch/`, contactpagina (`page.contact`) |
| Duurzaamheid (extra) | ✅ 🛠 | Blok op de homepage en een eigen pagina (`page.duurzaamheid`): lang meegaan, repareren, verpakking zonder plastic, kleine series, biologisch katoen en drie dingen mee van het strand. Alleen wat echt zo is, geen keurmerken of cijfers. 🛠 Pagina "Duurzaamheid" aanmaken met template `page.duurzaamheid`, de footer linkt er al naar |
| Werkende social links, kanalen in dezelfde stijl | 🛠 | Links invullen in Thema-instellingen > Social media. Profielfoto, highlights en eerste posts staan in `docs/social/`. Vul het account met minstens 9 posts |
| Meta-pixel en Google Analytics | 🛠 | Apps "Facebook & Instagram" en "Google & YouTube" installeren en koppelen |
| Contact: werkend formulier en zichtbare gegevens | ✅ 🛠 | Formulier en gegevens op de contactpagina en in de footer. Gegevens aanpassen in Thema-instellingen > Tide-Tode. Test het formulier zelf |
| Shopify Payments in testmodus, KvK Avans 41104408 | 🛠 | Instellingen > Betalingen > Shopify Payments activeren met KvK 41104408, daarna Testmodus aan. 📝 Screenshot maken |

## 2. Ontwerp en gebruiksvriendelijkheid

| Eis | Status | Toelichting |
|---|---|---|
| Responsief op mobiel, tablet en desktop | ✅ | Getest van 320 tot 3840 pixels breed, nergens horizontaal scrollen |
| Consistent met de merkidentiteit | ✅ | Kleuren, letters en tekeningen uit het merkboek |
| Maximaal twee klikken naar een product | 🛠 | Menu instellen zoals hieronder: Home > Shop > Draagtassen > product |
| Duidelijke call-to-action op elke pagina | ✅ | Elke pagina eindigt met een knop naar de tassen of het formulier |
| Kleuren en letters leesbaar | ✅ | Navy op crème en crème op navy, ruim boven WCAG AA |
| Beeld effectief, niet overweldigend | ✅ | Sfeerfoto's afgewisseld met rustige tekeningen |

**Hoofdmenu** (Online winkel > Navigatie > Hoofdmenu)

- Shop
  - Draagtassen → `/collections/draagtassen`
  - Surfgear → `/collections/surfgear`
  - Kleding en accessoires → `/collections/kleding-en-accessoires`
  - Alles → `/collections/all`
- Maatwijzer → `/pages/maatwijzer`
- Ons verhaal → `/pages/over-ons`
- FAQ → `/pages/veelgestelde-vragen`
- Contact → `/pages/contact`

**Footermenu Service**: Verzending, Retourneren, Herroepingsrecht, Algemene voorwaarden, Privacy.

**Prijsweergave** (Instellingen > Algemeen > Winkelstandaarden > Valuta-opmaak wijzigen)

- HTML zonder valuta: `€{{amount_with_comma_separator}}`
- HTML met valuta: `€{{amount_with_comma_separator}}`

Het thema laat de nullen achter de komma al weg, dus je ziet €40 en €5.

## 3. Snelheid

| Eis | Status | Toelichting |
|---|---|---|
| Laadtijd onder 3 seconden | ✅ 🛠 | Lichte code, lazy loading, lettertypes lokaal. 📝 Meet met PageSpeed Insights en maak een screenshot |
| Afbeeldingen onder 200 kB | ✅ | Alle beelden in het thema en alle productbeelden zijn kleiner dan 190 kB |
| Caching actief | ✅ | Shopify zet alles op een CDN met caching. Noem dat in je reflectie |

## 4. SEO en GEO

| Eis | Status | Toelichting |
|---|---|---|
| Unieke meta-titel en beschrijving per pagina | ✅ 🛠 | Producten: zit in de CSV. Pagina's en collecties: zie de lijst hieronder |
| Korte, beschrijvende URL's | ✅ | Bijvoorbeeld `/products/draagtas-tegel` en `/pages/maatwijzer` |
| Alt-teksten bij alle afbeeldingen | ✅ | In de CSV en in het thema |
| Interne links tussen product en maatwijzer | ✅ | Productpagina linkt naar de maatwijzer, de maatwijzer linkt terug naar de collecties |
| Mobielvriendelijk | ✅ | |
| Reviews zichtbaar, review-app | 🛠 | Installeer Judge.me (gratis). Op de productpagina staat een plek voor app-blokken: Thema aanpassen > Product > sectie Apps > Judge.me toevoegen. Zet ook de sterren in het blok "TT: kopen" |
| Structured data voor Google en AI | ✅ | Product, organisatie en FAQ als JSON-LD |

**Meta-titels en beschrijvingen** (bij elke pagina en collectie onderaan: Zoekmachinevermelding bewerken)

| Pagina | Titel | Beschrijving |
|---|---|---|
| Home (Instellingen > Voorkeuren) | Tide-Tode: draagtassen voor je surfboard | Draagtas voor je surfboard. Board erin, tas over je schouder en je handen zijn vrij. Voor softtops en hardboards. |
| Draagtassen | Surfboard draagtassen in negen prints | Draagtassen voor je surfboard in tegel, golfjes, ruit en meer. Eén maat voor softtops en hardboards. |
| Surfgear | Surfwax, waxkam en karabijnhaken | Surfwax voor koud, koel en warm water, een waxkam, karabijnhaken en stickers van Tide-Tode. |
| Kleding en accessoires | Surfkleding: T-shirts, longsleeves en hoodies | Surfkleding met eigen prints: T-shirts, longsleeves, een UV-shirt, hoodie, poncho en meer. |
| Over ons | Over Tide-Tode: hoe de draagtas begon | Bedacht op surftrips in Australië en Midden-Amerika. Lees waarom Veerle de draagtas voor surfboards maakte. |
| Duurzaamheid | Duurzaamheid bij Tide-Tode | Een tas die jaren meegaat, reparatie in plaats van een nieuwe, verpakking zonder plastic en drie dingen mee van het strand. |
| Veelgestelde vragen | Veelgestelde vragen over de draagtas | Welke boards passen, kan hij mee in het vliegtuig, verzenden en retourneren. Alle antwoorden op een rij. |
| Contact | Contact met Tide-Tode | Vraag over je bestelling of de draagtas? Mail, bel of stuur een bericht. We reageren binnen één werkdag. |
| Maatwijzer | Maatwijzer draagtas en surfkleding | Past je board in de draagtas en welke maat T-shirt, hoodie of UV-shirt kies je? Bekijk de maattabellen. |
| Herroepingsrecht | Herroepingsrecht en modelformulier | 14 dagen bedenktijd bij Tide-Tode. Zo herroep je je bestelling, met het modelformulier. |
| Actie | 10% korting op je eerste draagtas | Vertel wat je van de draagtas vindt en krijg direct 10% korting op je eerste bestelling. |

## 5. Inhoud en functionaliteit

| Eis | Status | Toelichting |
|---|---|---|
| Teksten begrijpelijk en gestructureerd | ✅ | Korte zinnen, gewone woorden, koppen per onderwerp |
| Contactinformatie zichtbaar | ✅ | Contactpagina en footer |
| Alle formulieren werken, zelf getest | 🛠 📝 | Test contactformulier, nieuwsbrief, actiepagina en de pop-up op de live winkel |
| Site wordt regelmatig bijgewerkt | 📝 | Houd een logboek bij in je reflectie |

## 6. Veiligheid, toegankelijkheid en techniek

| Eis | Status | Toelichting |
|---|---|---|
| SSL (https) | ✅ | Shopify regelt dit automatisch |
| Voldoende contrast | ✅ | |
| Google Analytics en Search Console | 🛠 | Google & YouTube-app voor Analytics. Search Console: eigendom toevoegen, verifiëren met de meta-tag en `/sitemap.xml` indienen |
| Conversietracking | 🛠 | Via dezelfde apps (aankoop, winkelwagen, afrekenen worden automatisch gemeten). Controleer in Instellingen > Klantgebeurtenissen |
| Getest in Chrome, Firefox, Safari en Edge | 📝 | Open de site in alle vier en maak per browser een screenshot |

## 7. Werkopdrachten week 2 tot en met 6

| Opdracht | Status |
|---|---|
| Shopify-link in de gedeelde Excel | 📝 |
| Screenshots gepubliceerde producten | 📝 na de import |
| Vier voorbeelden van wetgeving bij concurrenten | 📝 |
| Social media gekoppeld in thema-instellingen | 🛠 📝 |
| Shopify Payments in testmodus | 🛠 📝 |
| Proefbestelling geplaatst | 📝 Gebruik testkaart 4242 4242 4242 4242 en de code WELKOM10 |
| PostNL- en DHL-app | 🛠 📝 |
| Microsoft Clarity, sessies bekeken | 🛠 📝 App "Microsoft Clarity" installeren |
| E-mailworkflow ActiveCampaign, twee momenten | 📝 Bijvoorbeeld: welkom na inschrijving, en een herinnering na een verlaten winkelwagen |
| Landingspagina met reactiemogelijkheid | ✅ Pagina "Actie" met template `page.actie`. 🛠 Kortingscode WELKOM10 aanmaken (Kortingen) |
| Peer review, drie verbeterpunten | 📝 |
| Twee CGI-pitches | 📝 |

## 8 en 9. Reflectiedocument en assessment

📝 Zet de link naar de winkel **en het wachtwoord** in je reflectiedocument (Online winkel > Voorkeuren > Wachtwoordbeveiliging).

## Nog nodig van Veerle

- Echte productfoto's (prompts in `docs/producten/chatgpt-prompts.md`)
- Definitieve prijzen, materialen en maten
- Bedrijfsgegevens als het geen schoolproject meer is (nu staan de KvK en het adres van Avans erin)
- Kortingscode WELKOM10 bevestigen
