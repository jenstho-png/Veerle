# Premium Shopify-website — herbruikbaar opbouw-sjabloon (CREAJT-aanpak)

> Dit is je **master-bestand** voor het bouwen van een premium, custom Shopify-site.
> Plak dit in een **nieuwe code-chat** als je een nieuwe site begint — dan heb je meteen
> de complete aanpak, de bouwstenen, de SEO/GEO-checklist en (belangrijk) de valkuilen.
> Gebaseerd op de BRANTT-build. Vul de `<< … >>`-plekken in per project.

---

## 0. Filosofie
Geen standaard drag-drop-thema, maar een **hand-gebouwde fork van Dawn** met eigen
custom secties in de huisstijl van het merk. Resultaat: snel, uniek, schaalbaar en
sterk vindbaar (SEO + GEO). Alles in **Liquid + CSS**, geen zware page-builders.

**Kernprincipes**
- Premium & rustig: veel witruimte, 1 accentfont voor accentwoorden, consistent kleurensysteem.
- Mobiel-first, getest tot 4K.
- Machine-leesbaar: structured data overal (voor Google én AI-engines).
- Veilig werken: **nooit direct naar het live-thema** — altijd eerst een ongepubliceerd preview-thema.

---

## 1. Projectopzet

### Benodigdheden
- Shopify-store (trial of betaald). Store-handle: `<< store >>.myshopify.com`.
- **Shopify CLI** (`shopify version`, werkt met 3.x/4.x).
- Lokale map voor het thema, bijv. `~/Developer/<< projectnaam >>/theme/`.
- Node + git (optioneel maar handig).

### Thema-basis kiezen
Twee opties:
1. **Dawn-fork** (schoon startpunt): download Dawn, bouw custom `brantt-*`-achtige secties zelf.
2. **Hergebruik de BRANTT-secties** (sneller): kopieer de `sections/`, `snippets/` en
   `assets/section-*.css` uit een bestaande build en herkleur ze. Scheelt dagen werk.

### Koppelen & starten
```bash
# inloggen op de juiste store
shopify theme list --store << store >>.myshopify.com

# thema lokaal binnenhalen (bestaand) of nieuw pushen
shopify theme pull  --store << store >>.myshopify.com --theme <id> --path theme
shopify theme dev   --store << store >>.myshopify.com   # live preview tijdens bouwen
```

---

## 2. ⚠️ Veiligheidsregels (hard geleerd — niet overslaan)

1. **Nooit experimenteel werk direct naar live pushen.** Maak een **ongepubliceerd**
   thema aan en push daar naartoe; preview via `?preview_theme_id=<id>`.
   ```bash
   shopify theme push --store << store >> --unpublished --theme "<< naam >> review"
   shopify theme push --store << store >> --theme <review-id> --only <pad>
   ```
2. **Pull vóór push** van editor-beheerde JSON's. De theme-editor schrijft naar
   `templates/*.json`, `config/settings_data.json` en `sections/*-group.json`. Pull die
   eerst, anders overschrijf je wat in de editor is aangepast.
3. **Shopify stript onbekende block-settings uit editor-JSON.** Zet je een nieuwe
   setting in een sectie-schema én gebruik je 'm in een template-JSON? Push dan in
   **twee stappen**: eerst de **sectie** (`.liquid`), daarna pas de **JSON** apart.
   Anders verdwijnen je nieuwe waarden bij de push.
4. **`max_blocks`** instellen in het schema als je >16 blocks in een sectie zet
   (default-limiet is 16; max 50).
5. **`shopify theme check --fail-level error`** moet **0 errors** geven vóór je live gaat.
   Warnings in Dawn-kernbestanden (bv. `scheme_classes`, `continue`, `facets` complexity)
   zijn bekende false-positives — die laat je met rust.
6. Live pas publiceren ná akkoord op het preview-thema.

---

## 3. Architectuur

```
theme/
├─ assets/        # CSS (section-*.css, header/footer.css), fonts (self-hosted woff2), logo's, placeholders
├─ config/        # settings_schema.json, settings_data.json (kleuren-schema's!)
├─ layout/        # theme.liquid (<head>, SEO, meta), password.liquid
├─ locales/       # vertalingen
├─ sections/      # alle custom <merk>-secties + *-group.json (header/footer groups)
├─ snippets/      # herbruikbare stukjes (icon, headline, placeholder, seo, meta-tags, popup…)
└─ templates/     # *.json per pagina (index, page.*, collection, product, blog, article)
```

### Kleurensysteem (belangrijk)
- **CSS-tokens** in `:root` (in de hoofd-CSS): `--merk-primary`, `--merk-deep`, `--merk-cream`, enz.
- **Shopify color schemes** (`config/settings_data.json`): `scheme-1`…`scheme-5` bepalen
  achtergrond/tekst/knoppen per sectie. Secties krijgen een `color-{{ settings.color_scheme }}`-class.
- Koppel ze: de scheme-achtergronden = je tokens. Zo stel je kleuren centraal in.
- Donkere secties afwisselen (bv. primair ↔ diep-accent) geeft diepte.
  Override per sectie kan met `.merk-sectie.color-scheme-3 { background: #xxx !important; }`.

### Accentwoord-systeem
Snippet `headline` splitst op `*`: tekst met `*woord*` rendert dat woord in het
handgeschreven/serif accentfont (`.script`-class). Gebruik overal voor koppen.

### Foto-systeem (placeholder op vaste bestandsnaam)
- Secties hebben een `image_picker` **én** een tekstveld `image_filename` (SEO-naam).
- Is er geen foto gekozen → een `placeholder`-snippet toont een nette vlak met de
  gewenste bestandsnaam. Klant uploadt later in **Content → Bestanden** met die naam.
- Zo bouw je de hele site af vóór de foto's er zijn.

---

## 4. Herbruikbare sectie-bibliotheek (bouwstenen)

| Sectie | Doel | Let op |
|---|---|---|
| **header** (+ `header-group.json`) | Zwevende pill-nav met dropdowns | tab-blocks met `dd1..dd5`, optionele `dd_all_label`; `.item{display:flex;align-items:center}` voor uitlijning |
| **hero** | Pakkende homepage-kop + foto + knoppen | 1×`h1`; accentwoord; whitespace-trim rond leesteken (`on fire?` niet `on fire ?`) |
| **proof / logobalk** | "Deze merken vertrouwen ons" | logo's als mask-silhouet (1 kleur) óf echte kleur (`<img>` + `mix-blend-mode:multiply` om witte rand weg te blenden) |
| **services** | Dienst-kaarten | mobiel evt. swipe-carousel |
| **feature** | Uitgelicht blok met mockup/foto | bv. Instagram-post-mockup |
| **statement** | Grote quote-band | donkere scheme; mag diep-accent-kleur |
| **shop** | Producten | layouts: `grid` (2 naast elkaar, compact óf detailed met beschrijving+voordelen+knop) of `rows` (grote panelen) |
| **faq** | Veelgestelde vragen | **FAQPage JSON-LD** → top voor SEO/AI |
| **reviews** | Google-reviews-stijl | multicolor G-logo + sterren; GEEN fake `aggregateRating` in schema |
| **cta** | Afsluit-call-to-action | stempel + 2 knoppen |
| **pagehero** | Kop voor subpagina's | titel óp foto, scrim eroverheen; subtekst eronder uitlijnen met overlay-padding |
| **portfolio / bubbles / steps / quote / team** | Case-/proces-/team-blokken | |
| **footer** (+ `footer-group.json`) | Menu-kolommen + contact + socials | menu-blocks met `l1..lN`; evt. eigen achtergrondkleur |
| **lead-popup** (snippet) | E-mail capture | `{% form 'customer' %}` → subscriber met **tag**; na ~120s + **exit-intent**; 7-dagen cooldown via `localStorage` |

---

## 5. SEO + GEO checklist (volledig)

> GEO = vindbaar voor AI-engines (ChatGPT, Perplexity, Google AI). Draait om
> **machine-leesbare feiten**: hoe meer kloppende structured data, hoe beter.

**In `layout/theme.liquid` (<head>):**
- [ ] `lang` op `<html>`, `<meta charset>`, viewport, `theme-color`.
- [ ] `robots: index, follow` + `<link rel=canonical>`.
- [ ] Slimme `<title>` (pagina-titel + merknaam + context).
- [ ] **Per-pagina `meta description`** via een `case template.name / page.handle` (schrijf
      unieke zinnen per belangrijke pagina — niet de generieke truncate laten staan).
- [ ] Favicon + apple-touch-icon.
- [ ] Render `meta-tags`-snippet (Open Graph + Twitter cards, met og:image 1200×630).

**Structured data (JSON-LD, in een `seo`-snippet, overal ingeladen):**
- [ ] **Organization / ProfessionalService**: naam, legalName, description, url, email,
      telephone, logo (ImageObject), **foundingDate**, slogan, address (incl. regio),
      **contactPoint**, **sameAs** (socials), **knowsAbout**, en **`makesOffer`** met
      alle diensten → AI kan "wat biedt X" citeren. `@id = {{ shop.url }}/#organization`.
- [ ] **WebSite** met `SearchAction` (sitelinks-zoekbox) + `publisher` → #organization.
- [ ] **BreadcrumbList** op alle niet-home-pagina's.
- [ ] **Product** op productpagina's: name, image, brand, sku, **offers** (price,
      priceCurrency, availability, itemCondition, seller → #organization).
      ⚠️ **Custom PDP-secties missen dit vaak** — zelf toevoegen! Dawn's `main-product` heeft het wél.
- [ ] **FAQPage** op pagina's met FAQ.
- [ ] (Blog) Article/BlogPosting — Dawn's `main-article` levert dit.

**Verboden:** fake `aggregateRating`/sterren in schema zonder échte reviews (Google-straf).

**Semantisch/techniek:**
- [ ] Exact **1 `<h1>`** per pagina; logische h2/h3.
- [ ] Alt-teksten op alle afbeeldingen.
- [ ] Lazy-load afbeeldingen; **self-hosted fonts** met `preload_tag` voor de hoofdfont.
- [ ] Sitemap + robots.txt: doet Shopify automatisch.

---

## 6. Responsive checklist
Test (emulated viewports) op: **320, 390, 768, 1024, 1440, 2560, 3840**.
- [ ] Geen **horizontale overflow**: `document.documentElement.scrollWidth === innerWidth`
      (marquee's/swipers mogen breder zijn mits in een `overflow-x`-container).
- [ ] Nav schakelt netjes naar hamburger onder de breakpoint.
- [ ] Knoppen stapelen, foto's schalen, geen tekst-afkapping op 320px.
- [ ] Content een **max-width** geven (bv. ~1600–2400px) en centreren; gekleurde
      achtergronden lopen **full-width** door, content blijft gecentreerd.

---

## 7. Stappenplan per nieuwe site
1. Store + CLI koppelen; ongepubliceerd preview-thema aanmaken.
2. Thema-basis neerzetten (Dawn-fork of BRANTT-secties hergebruiken).
3. **Huisstijl**: kleuren-tokens + color-schemes, fonts (self-hosted), logo, favicon.
4. **Secties samenstellen** per template: `index.json`, `page.*.json`, `collection.json`,
   `product.json`, `blog.json`, `article.json`.
5. **Content + foto's** (vaste bestandsnamen via placeholder-systeem).
6. **SEO/GEO** invullen (hoofdstuk 5).
7. **Responsive** testen (hoofdstuk 6).
8. `theme check --fail-level error` → 0 errors.
9. Reviewen op preview-thema → akkoord → **publiceren naar live**.

---

## 8. Wat alleen in Shopify-admin kan (niet in code)
- Pagina's aanmaken + het juiste **thema-sjabloon** koppelen (bij `page.<handle>.json`).
- **Collecties** + producten (met prijs/variant → dan wordt availability "InStock").
- **Blog** aanmaken (let op de **handle**, bv. `nieuws`, moet matchen met je menu-links).
- **Navigatie/menu's** als je Shopify-linklists gebruikt (anders via de sectie-blocks).
- **E-mailautomatisering**: Shopify Email of **Flow**, getriggerd op een **tag**
  (bv. lead-popup zet tag `gratis-x` → mail de weggever).
- Betaalmethoden, verzending, domein, taal/markt.

---

## 9. CLI-spiekbriefje
```bash
shopify theme list   --store << store >>
shopify theme pull   --store << store >> --theme <id> --path theme --only templates/index.json
shopify theme push   --store << store >> --theme <id> --only sections/x.liquid   # sectie eerst
shopify theme push   --store << store >> --theme <id> --only templates/index.json # dan de JSON
shopify theme push   --store << store >> --unpublished --theme "<< naam >> review"
shopify theme check  --fail-level error
shopify theme dev    --store << store >>
```
Preview: `https://<< store >>.myshopify.com?preview_theme_id=<id>` (wachtwoord als de store beveiligd is).

---

## 10. Startprompt voor de nieuwe code-chat (kopieer-plak)
> Ik bouw een **premium, custom Shopify-site** voor **<< bedrijf / branche >>**.
> Doel: << doel >>. Huisstijl: << kleuren / sfeer / fonts >>.
> Gebruik de CREAJT-aanpak uit `shopify-premium-opbouw-sjabloon.md`:
> een Dawn-fork met custom secties, centraal kleurensysteem, placeholder-foto-systeem,
> volledige SEO/GEO (structured data), en responsive tot 4K.
> **Veilig werken:** push naar een **ongepubliceerd** preview-thema, nooit direct live;
> pull-vóór-push van editor-JSON's; bij nieuwe block-settings eerst de sectie pushen en
> dan pas de template-JSON. Lever secties één voor één op en laat telkens een preview zien.
> Store: `<< store >>.myshopify.com`.

---

*Opgesteld door CREAJT. Pas de `<< … >>`-velden aan per project; de rest is herbruikbaar.*
