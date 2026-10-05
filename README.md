# Surfboard draagtas: premium Shopify-thema

Custom Shopify-site voor een nieuw surfmerk (werknaam **Tide-Tode**). Het merk maakt een draagtas voor je surfboard: handen vrij op weg naar de golf.
Gebouwd volgens de CREAJT-aanpak (`docs/shopify-premium-opbouw-sjabloon.md`): een Dawn-fork (v16) met eigen `surf-*`-secties, een centraal kleurensysteem, placeholder-foto's op vaste bestandsnamen, volledige SEO/GEO en responsive tot 4K.

## Mappen
```
theme/            Shopify-thema (Dawn 16 + surf-laag)
  assets/surf.css   huisstijl: tokens, fonts, alle surf-secties
  assets/surf.js    header, mobiel menu, scroll-reveal, lead-popup
  sections/surf-*   header, hero, USP-band, verhaal, voordelen, product, stappen,
                    statement, fotogalerij, reviews, FAQ, call-to-action, paginakop, footer
  snippets/surf-*   headline (*accentwoord*), image (placeholder), icon, seo (JSON-LD),
                    meta-description, lead-popup
docs/             briefing, foto-lijst, opbouw-sjabloon
tools/preview/    ruwe lokale preview + screenshots (liquidjs), los van Shopify
```

## Pagina's (templates)
| Template | Admin-handle | Secties |
|---|---|---|
| `index.json` | (home) | hero · USP-band · verhaal · voordelen · product · stappen · statement · galerij · FAQ · CTA |
| `page.over-ons.json` | `over-ons` | paginakop · 2× verhaal · statement · galerij · CTA |
| `page.veelgestelde-vragen.json` | `veelgestelde-vragen` | FAQ (h1 + FAQPage-schema) · CTA |
| `page.contact.json` | `contact` | paginakop · Dawn-contactformulier |
| `product.json` | – | Dawn main-product (incl. Product-schema) · voordelen · FAQ · gerelateerd |
| `collection.json` | – | paginakop · Dawn-productgrid |

## Aan de slag
```bash
shopify theme push --store <store>.myshopify.com --path theme --unpublished --theme "Surf review"
shopify theme dev  --store <store>.myshopify.com --path theme
shopify theme check --path theme --fail-level error   # moet 0 errors geven (nu: 0)
```
Volg de veiligheidsregels uit het sjabloon (hoofdstuk 2): nooit direct live pushen, editor-JSON's eerst pullen, en bij nieuwe block-settings eerst de sectie pushen en daarna pas de JSON.

**In Shopify-admin:**
1. Pagina's `Over ons` (handle `over-ons`, sjabloon *over-ons*), `Veelgestelde vragen` (`veelgestelde-vragen`) en `Contact` aanmaken.
2. Product aanmaken en koppelen in de homepage-sectie **Surf – product**.
3. Thema-instellingen → **Surf – merk & SEO** (e-mail, plaats, oprichtingsdatum) en **Sociale media** invullen.
4. Shopify Flow/Email: welkomstmail op klant-tag `early-access` (lead-popup).
5. Foto's uploaden volgens `docs/foto-lijst.md`.

## Lokale preview (zonder store)
```bash
cd tools/preview && npm install && npm run shots   # → tools/preview/out/*.png
```
Dit is een benadering met shims voor Shopify-filters, alleen bedoeld voor een snelle visuele check. De echte preview is `shopify theme dev`.

## Open punten
Zie `docs/briefing.md` → *Openstaande punten*: merknaam, logo, prijs, productspecs, claims, foto's en contactgegevens.
