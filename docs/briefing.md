# Briefing: surfboard draagtas (werknaam *Tide-Tode*)

Samenvatting van de intake (Surfbag.docx), vertaald naar keuzes voor de site.

## Het verhaal
- Ontstaan op reizen (Australië, Midden- en Zuid-Amerika, Azië): lange hikes naar afgelegen spots met een log board. De wax schuurt onder je arm, je schouders doen pijn, en op de scooter of fiets moet je met één hand sturen.
- Een dichte boardbag is geen oplossing: daar moet je natte, zanderige plank telkens in.
- Geprobeerd: losse touwtjes, spanbanden, standaardhoezen. Niets hield het vol.
- De oprichter komt uit een ondernemersgezin. In februari 2025 kwam er een vriend bij die net zo gek is op surfen en dezelfde frustratie kende. Dat gaf het extra zetje.

## Product
| | |
|---|---|
| Kernmodel | 1 model in een universele maat (later meer varianten) |
| Boards | Softtops/vollere boards voor beginners én hardboards voor avonturiers |
| Must-haves | Draagcomfort (ergonomisch, gewicht goed verdeeld), sterke en waterbestendige stof, makkelijk mee in het vliegtuig |
| Later | Lussen en karabijnhaken voor extra gear (niet op het instapmodel) |
| Uitstraling product | Robuust, zware stof, no-nonsense, sterke stiksels, messing of donker metaal, maar ook mooi |
| Extra assortiment | Waxblokjes, karabijnhaken, later t-shirts |
| Prijs | Indicatie rond € 40 voor het standaardmodel (kostprijs moet nog berekend worden) |

## Doelgroep
- **Beginners** met een groot board die vanaf hotel of hostel naar het strand lopen of rijden.
- **Gevorderden/avonturiers** die door de bush of over rotsen naar afgelegen spots trekken.
- Overal ter wereld en in Europa: te voet door duinen en bossen, op de fiets, of met de auto op roadtrip.

## Merk & uitstraling → ontwerpkeuzes
| Briefing | In het thema |
|---|---|
| **Wel:** avontuurlijk, kwalitatief, no-nonsense | Stoere koppen (Archivo 800), korte teksten, duidelijke knoppen |
| **Niet:** fragiel, massaal, ingewikkeld | Geen drukke animaties of poespas, veel witruimte |
| "From riders for riders", authentiek | Founder-verhaal prominent op home en Over ons |
| Vrouwelijke touch, Instagram-waardig | Sierlijk accentfont (Fraunces italic) voor *accentwoorden*, afgeronde vormen, fotogalerij |
| Blauw van de zee, rust, *fineline* | Palet diepzee/oceaan/schuim + zand, 1px-lijnen, golf-iconen |
| Messing details op de tas | Messing-accent (#A9834A) voor iconen, hovers en stapnummers |
| Duiken als passie | Galerij "Van verstopte spot tot diep blauw" met plek voor duikbeelden |
| Gevoel: zin om je tas te pakken en te gaan surfen | Hero "Handen vrij, op weg naar de golf", CTA "Pak je tas, de zee wacht" |

## Kleuren (tokens in `theme/assets/surf.css`, schema's in `config/settings_data.json`)
| Schema | Rol | Achtergrond | Tekst |
|---|---|---|---|
| scheme-1 | Zand (standaard) | `#F4EEE4` | `#142029` |
| scheme-2 | Schuim | `#E9F1F3` | `#142029` |
| scheme-3 | Diepzee (donker) | `#0D2433` | `#F4EEE4` |
| scheme-4 | Oceaan | `#1D5A78` | `#FFFFFF` |
| scheme-5 | Wit (kaarten) | `#FFFFFF` | `#142029` |

Accent: getij `#4F97B6`, messing `#A9834A`.

## Lancering
De site gaat pas live als er meerdere modellen klaarliggen. Tot die tijd:
- Kan de store achter het **wachtwoord** blijven en vullen we de site alvast volledig in.
- Staat de **lead-popup** aan (tag `early-access`). Zo bouwt ze vóór de lancering een wachtlijst op.
- De CTA-sectie heeft een modus **"E-mail inschrijving"** voor een pre-launch homepage.

## Openstaande punten (nodig van de klant)
1. **Merknaam** definitief (werknaam Tide-Tode). Daarna winkelnaam in Shopify aanpassen, want de site gebruikt overal `shop.name`. Domein en socials vastleggen.
2. **Logo**: samen ontwerpen, in dezelfde stijl als de site. Tot die tijd toont de header een tekstlogo.
3. **Kostprijs en verkoopprijs** van het kernmodel.
4. **Productspecificaties** voor de PDP: afmetingen, maximale boardlengte, materiaal, gewicht, opgevouwen formaat.
5. **Claims checken**: de standaardteksten noemen "waterbestendig", "opvouwbaar / past in je bagage" en "verzending door heel Europa". Klopt dat?
6. **Foto's**: reisfoto's met board aanleveren (zie `foto-lijst.md`). Productfoto's en surf-footage moeten nog geregeld worden.
7. **Contactgegevens** (e-mail, plaats, KvK) en **social links** invullen in de thema-instellingen.
8. **Reviews**: de sectie `Surf – reviews` staat klaar, maar plaats alleen echte reviews.
