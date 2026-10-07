"""Schrijft de tt-secties (webshop-homepage, ronde 3) naar theme/sections.

Opbouw volgt de koopvolgorde: beeld en belofte, bewijs (USP's), direct kopen,
het probleem herkennen, hoe het werkt, droombeeld, voor wie, het verhaal,
vragen, laatste duw. Alle beelden hebben een sfeerfoto uit de assets als
plaatsvervanger tot Veerle eigen foto's uploadt.
"""
import json, pathlib
T = pathlib.Path(__file__).parent.parent.parent / 'theme' / 'sections'
BG = [{"value": v, "label": l} for v, l in [("creme", "Crème"), ("papier", "Papier"), ("zand", "Zand"), ("deep", "Deep"), ("baby", "Baby"), ("rose", "Rose"), ("sunshine", "Sunshine")]]
ICONEN = [{"value": k, "label": n} for k, n in [("tas", "De tas"), ("golf", "Golf"), ("golfjes", "Getij"), ("board", "Board"), ("schelp", "Schelp"), ("zon", "Zon"), ("maan", "Maan"), ("zeester", "Zeester"), ("palmblad", "Palmblad"), ("meeuw", "Meeuw"), ("wax", "Wax"), ("karabijn", "Karabijnhaak"), ("tij", "Spiraal"), ("voeten", "Onderweg")]]
KLEUREN = [{"value": v, "label": l} for v, l in [("sunshine", "Sunshine"), ("rose", "Rose"), ("poppy", "Poppy"), ("baby", "Baby"), ("deep", "Deep"), ("creme", "Crème")]]
KOP_INFO = "Een | is een nieuwe regel. Zet woorden tussen *sterretjes* voor het cursieve accent."


def beeld(prefix, label, fallback, filename, alt):
    return [
        {"type": "header", "content": label},
        {"type": "image_picker", "id": f"{prefix}image", "label": "Foto"},
        {"type": "text", "id": f"{prefix}filename", "label": "Bestandsnaam", "default": filename, "info": "Of upload in Content > Bestanden met precies deze naam. Tot die tijd staat er een sfeerfoto."},
        {"type": "text", "id": f"{prefix}alt", "label": "Alt-tekst", "default": alt},
    ], fallback


def B(prefix, fallback, extra=""):
    return ("{%- render 'tt-beeld', image: section.settings." + prefix + "image, filename: section.settings." + prefix + "filename, fallback: '" + fallback + "', alt: section.settings." + prefix + "alt" + extra + " -%}")


def BB(fallback_setting="fallback", extra=""):
    """beeld uit een block"""
    return ("{%- render 'tt-beeld', image: block.settings.image, filename: block.settings.filename, fallback: block.settings." + fallback_setting + ", alt: block.settings.alt" + extra + " -%}")


def blok_beeld(fallback, filename, alt):
    return [
        {"type": "image_picker", "id": "image", "label": "Foto"},
        {"type": "text", "id": "filename", "label": "Bestandsnaam", "default": filename},
        {"type": "text", "id": "fallback", "label": "Sfeerfoto (asset)", "default": fallback, "info": "Wordt gebruikt zolang er geen eigen foto is."},
        {"type": "text", "id": "alt", "label": "Alt-tekst", "default": alt},
    ]


def bg(default):
    return {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": default}


def kop(default, label="Kop"):
    return {"type": "text", "id": "heading", "label": label, "info": KOP_INFO, "default": default}


def schrijf(naam, body, schema):
    (T / f'{naam}.liquid').write_text(body.strip() + "\n\n{% schema %}\n" + json.dumps(schema, indent=2, ensure_ascii=False) + "\n{% endschema %}\n")


PRIJS = """{%- liquid
  assign p = section.settings.product
  if p == blank and template.name == 'product' and product != blank
    assign p = product
  endif
  if p == blank
    assign p = settings.tt_product
  endif
  assign v = p.selected_or_first_available_variant
-%}"""
PRODUCT = PRIJS.replace("\n  assign v = p.selected_or_first_available_variant", "")

# ---------- HERO: volle foto, grote belofte, productkaartje ----------
s, fb = beeld('', 'Foto', 'tt-foto-hero', 'tide-tode-hero.jpg', 'Surfer loopt met board over het strand naar zee')
schrijf('tt-hero', PRIJS + """
<section class="tt tt-hero{% if section.settings.pagina %} tt-hero--pagina{% endif %}" id="tt-hero-{{ section.id }}">
  <div class="tt-hero__foto">""" + B('', fb, ", sizes: '100vw', loading: 'eager'") + """</div>
  <div class="tt-hero__inhoud tt-wrap">
    {%- if section.settings.poster -%}
    <div class="tt-hero__poster">
      <div class="tt-hero__links">
        <div class="tt-hero__icoon tt-in" style="--d: .1s" aria-hidden="true">{%- render 'tt-logo', variant: 'maan' -%}</div>
        <h1 class="tt-hero__logo tt-in" style="--d: .2s">{%- render 'tt-logo', variant: 'staand' -%}<span class="visually-hidden">{{ section.settings.heading | replace: '|', ' ' | remove: '*' }}</span></h1>
        {%- if section.settings.hand != blank -%}<p class="tt-hero__hand tt-in" style="--d: .5s">{{ section.settings.hand }}</p>{%- endif -%}
      </div>
      <div class="tt-hero__rechts tt-in" style="--d: .7s">
        {%- if section.settings.text != blank -%}<p>{{ section.settings.text }}</p>{%- endif -%}
        <div class="tt-knoppen">
          {%- if section.settings.btn_label != blank -%}
            <a class="tt-knop tt-knop--licht" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}<span aria-hidden="true">→</span></a>
          {%- endif -%}
          {%- if section.settings.link_label != blank -%}<a class="tt-link" href="{{ section.settings.link_url | default: '#tt-verhaal' }}">{{ section.settings.link_label }}</a>{%- endif -%}
        </div>
        {%- if section.settings.est != blank -%}<div class="tt-hero__est" aria-hidden="true"><span>est.</span><span>{{ section.settings.est }}</span></div>{%- endif -%}
      </div>
    </div>
    {%- else -%}
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h1', class: 'tt-kop--xl' -%}
    <div class="tt-hero__onder">
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in" style="--d: .7s">{{ section.settings.text }}</p>{%- endif -%}
      <div class="tt-knoppen tt-in" style="--d: .85s">
        {%- if section.settings.btn_label != blank -%}
          <a class="tt-knop tt-knop--licht" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}<span aria-hidden="true">→</span></a>
        {%- endif -%}
        {%- if section.settings.link_label != blank -%}<a class="tt-link" href="{{ section.settings.link_url | default: '#tt-verhaal' }}">{{ section.settings.link_label }}</a>{%- endif -%}
      </div>
    </div>
    {%- endif -%}
  </div>
  {%- if section.settings.kaart and p != blank -%}
    <a class="tt-hero__kaart tt-in" style="--d: 1.1s" href="{{ p.url }}">
      <span class="tt-hero__kaart-beeld">{%- if p.featured_media -%}{{ p.featured_media | image_url: width: 240 | image_tag: loading: 'eager', alt: p.title }}{%- else -%}{% render 'tt-logo', variant: 'maan-simpel' %}{%- endif -%}</span>
      <span><strong>{{ p.title }}</strong><span>{{ v.price | money }}</span></span>
      <span class="tt-hero__kaart-pijl" aria-hidden="true">→</span>
    </a>
  {%- endif -%}
</section>
""", {
    "name": "TT: hero", "tag": "div",
    "settings": [
        {"type": "checkbox", "id": "pagina", "label": "Lagere versie (voor subpagina's)", "default": False},
        {"type": "checkbox", "id": "poster", "label": "Posterversie: het grote logo als kop", "default": True, "info": "De kop hieronder staat dan onzichtbaar in de pagina (voor Google en schermlezers)."},
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        kop("Je board op je rug,|je handen vrij."),
        {"type": "text", "id": "hand", "label": "Handgeschreven regel (posterversie)", "default": "Handen vrij, op weg naar zee"},
        {"type": "text", "id": "est", "label": "Jaartal rechtsonder (posterversie)", "default": "2025"},
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Een draagtas voor je surfboard, bedacht op surftrips in Australië en Midden-Amerika. Voor de wandeling door de duinen, de fiets naar het strand en de scooter naar een spot verderop."},
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Bekijk de draagtas"},
        {"type": "url", "id": "btn_link", "label": "Knop-link", "info": "Leeg = het product."},
        {"type": "text", "id": "link_label", "label": "Tweede link", "default": "Hoe het begon"},
        {"type": "url", "id": "link_url", "label": "Tweede link: adres"},
        {"type": "checkbox", "id": "kaart", "label": "Productkaartje rechts", "default": False},
    ] + s,
    "presets": [{"name": "TT: hero"}]})

# ---------- USP-strook ----------
schrijf('tt-usp', """
<section class="tt tt-usp tt-bg--{{ section.settings.bg }}" aria-label="Waarom deze tas">
  <div class="tt-usp__spoor" data-tt-usp>
    {%- for n in (1..2) -%}
      <ul class="tt-usp__lijst"{% if n == 2 %} aria-hidden="true"{% endif %}>
        {%- for block in section.blocks -%}
          <li {{ block.shopify_attributes }}>{% render 'tt-icoon', icoon: block.settings.icoon %}<span>{{ block.settings.tekst }}</span></li>
        {%- endfor -%}
      </ul>
    {%- endfor -%}
  </div>
</section>
""", {
    "name": "TT: voordelen-strook", "tag": "div", "max_blocks": 6,
    "settings": [bg("deep"), {"type": "checkbox", "id": "zegel", "label": "Zegel tonen (half over de foto erboven)", "default": True}],
    "blocks": [{"type": "usp", "name": "Voordeel", "settings": [
        {"type": "select", "id": "icoon", "label": "Icoon", "options": ICONEN, "default": "golf"},
        {"type": "text", "id": "tekst", "label": "Tekst", "default": "Handen vrij"}]}],
    "presets": [{"name": "TT: voordelen-strook", "blocks": [
        {"type": "usp", "settings": {"icoon": "voeten", "tekst": "Handen vrij, ook op de scooter"}},
        {"type": "usp", "settings": {"icoon": "board", "tekst": "Past op softtop én hardboard"}},
        {"type": "usp", "settings": {"icoon": "golf", "tekst": "Sterke, waterbestendige stof"}},
        {"type": "usp", "settings": {"icoon": "tas", "tekst": "Makkelijk mee in het vliegtuig"}}]}]})

# ---------- KOPEN: galerij + koopblok ----------
s1, fb1 = beeld('', 'Productfoto 1 (zolang het product geen foto\'s heeft)', 'tt-product-1', 'tide-tode-draagtas-1.jpg', 'De Tide-Tode draagtas met board')
s2, fb2 = beeld('b2_', 'Productfoto 2', 'tt-product-2', 'tide-tode-draagtas-2.jpg', 'De tegelstof van de draagtas van dichtbij')
schrijf('tt-koop', PRIJS + """
{%- liquid
  assign pdp = false
  if template.name == 'product' and product != blank and section.settings.product == blank
    assign pdp = true
  endif
-%}
<section class="tt tt-koop tt-bg--{{ section.settings.bg }}" id="tt-koop-{{ section.id }}" data-tt-koop>
  <div class="tt-wrap tt-koop__grid">
    <div class="tt-koop__galerij-wrap">
    <div class="tt-koop__galerij" data-tt-galerij>
      {%- assign media = p.media | where: 'media_type', 'image' -%}
      {%- assign max = 4 -%}{%- if pdp -%}{%- assign max = 12 -%}{%- endif -%}
      {%- if media.size > 0 -%}
        {%- for m in media limit: max -%}
          <div class="tt-koop__foto tt-onthul"{% if forloop.first %}{% endif %}>{%- if forloop.first -%}{%- render 'tt-sticker', tekst: section.settings.sticker, kleur: 'poppy', vorm: 'rond', class: 'tt-sticker--rechtsboven' -%}{%- endif -%}{{ m.preview_image | image_url: width: 1800 | image_tag: loading: 'lazy', sizes: '(min-width: 990px) 55vw, 100vw', widths: '600, 900, 1200, 1800', alt: m.alt | default: p.title, class: 'tt-beeld__img' }}</div>
        {%- endfor -%}
      {%- else -%}
        <div class="tt-koop__foto tt-onthul">{%- render 'tt-sticker', tekst: section.settings.sticker, kleur: 'poppy', vorm: 'rond', class: 'tt-sticker--rechtsboven' -%}""" + B('', fb1, ", sizes: '(min-width: 990px) 55vw, 100vw'") + """</div>
        <div class="tt-koop__foto tt-onthul">""" + B('b2_', fb2, ", sizes: '(min-width: 990px) 55vw, 100vw'") + """</div>
        {%- if section.settings.extra_beelden -%}
          {%- for n in (3..7) -%}
            {%- assign naam = 'tt-product-' | append: n -%}
            {%- case n -%}
              {%- when 3 -%}{%- assign alt_n = 'Het tegelvak van de draagtas om het midden van het board' -%}
              {%- when 4 -%}{%- assign alt_n = 'De dusty blue schouderband van de draagtas' -%}
              {%- when 5 -%}{%- assign alt_n = 'Tekening van de draagtas met genummerde onderdelen' -%}
              {%- when 6 -%}{%- assign alt_n = 'De draagtas als sticker op een zwart-witfoto van de zee' -%}
              {%- else -%}{%- assign alt_n = 'De kleuren van de tegelstof: terracotta, dusty blue, mosterd, roest, crème en navy' -%}
            {%- endcase -%}
            <div class="tt-koop__foto tt-onthul">{%- render 'tt-beeld', fallback: naam, alt: alt_n, sizes: '(min-width: 990px) 55vw, 100vw' -%}</div>
          {%- endfor -%}
        {%- endif -%}
      {%- endif -%}
    </div>
    {%- liquid
      assign aantal = media.size
      if aantal > max
        assign aantal = max
      endif
      if aantal == 0
        assign aantal = 2
        if section.settings.extra_beelden
          assign aantal = 7
        endif
      endif
    -%}
    {%- if section.settings.stickers -%}<div class="tt-stickers tt-stickers--koop" aria-hidden="true">{% render 'tt-stk', naam: 'draagtas' %}</div>{%- endif -%}
    <p class="tt-koop__teller" aria-hidden="true"><span data-tt-teller>1</span> / {{ aantal }}</p>
    </div>
    <div class="tt-koop__info">
      <div class="tt-koop__plak">
        {%- if pdp -%}
          <h1 class="tt-kop tt-kop--m">{{ p.title | escape }}</h1>
        {%- else -%}
          {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
        {%- endif -%}
        <p class="tt-koop__prijs tt-in">
          {%- if p != blank -%}
            <span>{{ v.price | money }}</span>
            {%- if v.compare_at_price > v.price -%}<s>{{ v.compare_at_price | money }}</s>{%- endif -%}
          {%- else -%}<span>{{ section.settings.prijs_tekst }}</span>{%- endif -%}
        </p>
        {%- if pdp and p.description != blank -%}
          <div class="tt-koop__pitch tt-koop__beschrijving tt-in">{{ p.description }}</div>
        {%- elsif section.settings.text != blank -%}
          <p class="tt-koop__pitch tt-in">{{ section.settings.text }}</p>
        {%- endif -%}
        <ul class="tt-koop__punten tt-in">
          {%- for block in section.blocks -%}{%- if block.type == 'punt' -%}<li {{ block.shopify_attributes }}><span class="tt-koop__vinkje" aria-hidden="true"></span>{{ block.settings.tekst }}</li>{%- endif -%}{%- endfor -%}
        </ul>
        {%- if p != blank and v.available and section.settings.voorraad != blank -%}<p class="tt-koop__voorraad tt-in"><span class="tt-koop__stip" aria-hidden="true"></span>{{ section.settings.voorraad }}</p>{%- endif -%}
        <div class="tt-koop__form tt-in">
          {%- if p != blank -%}
            {%- form 'product', p, class: 'tt-koop__formulier', data-tt-form: '' -%}
              {%- unless p.has_only_default_variant -%}
                {%- for option in p.options_with_values -%}
                  <fieldset class="tt-koop__optie">
                    <legend>{{ option.name }}</legend>
                    {%- for value in option.values -%}
                      <label><input type="radio" name="tt-optie-{{ forloop.parentloop.index }}" value="{{ value | escape }}"{% if option.selected_value == value %} checked{% endif %}><span>{{ value }}</span></label>
                    {%- endfor -%}
                  </fieldset>
                {%- endfor -%}
                <script type="application/json" data-tt-varianten>{{ p.variants | json }}</script>
              {%- endunless -%}
              <input type="hidden" name="id" value="{{ v.id }}" data-tt-variant>
              <button type="submit" class="tt-knop tt-knop--vol"{% unless v.available %} disabled{% endunless %} data-tt-koopknop>
                <span data-tt-knoptekst>{% if v.available %}In winkelwagen{% else %}Uitverkocht{% endif %}</span>
              </button>
              {%- if section.settings.snel_betalen -%}<div class="tt-koop__snel">{{ form | payment_button }}</div>{%- endif -%}
            {%- endform -%}
          {%- else -%}
            <a class="tt-knop tt-knop--vol" href="{{ routes.all_products_collection_url }}"><span>Bekijk de tas</span></a>
          {%- endif -%}
        </div>
        <ul class="tt-koop__vertrouwen tt-in">
          {%- if section.settings.v1 != blank -%}<li>{% render 'tt-icoon', icoon: 'voeten' %}{{ section.settings.v1 }}</li>{%- endif -%}
          {%- if section.settings.v2 != blank -%}<li>{% render 'tt-icoon', icoon: 'tij' %}{{ section.settings.v2 }}</li>{%- endif -%}
          {%- if section.settings.v3 != blank -%}<li>{% render 'tt-icoon', icoon: 'schelp' %}{{ section.settings.v3 }}</li>{%- endif -%}
        </ul>
        {%- if section.settings.betaal_iconen and shop.enabled_payment_types.size > 0 -%}
          <ul class="tt-koop__betaal tt-in" aria-label="Betaalmethoden">{%- for type in shop.enabled_payment_types -%}<li>{{ type | payment_type_svg_tag }}</li>{%- endfor -%}</ul>
        {%- endif -%}
        <div class="tt-koop__details tt-in">
          {%- for block in section.blocks -%}{%- if block.type == 'detail' -%}
            <details {{ block.shopify_attributes }}><summary>{{ block.settings.titel }}<i aria-hidden="true"></i></summary><div>{{ block.settings.tekst }}</div></details>
          {%- endif -%}{%- endfor -%}
        </div>
      </div>
    </div>
  </div>
  {%- if pdp -%}
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": {{ p.title | json }},
        "url": {{ request.origin | append: p.url | json }},
        {%- if p.featured_media -%}"image": [{{ p.featured_media | image_url: width: 1920 | prepend: 'https:' | json }}],{%- endif -%}
        "description": {{ p.description | strip_html | strip_newlines | json }},
        {%- if v.sku != blank -%}"sku": {{ v.sku | json }},{%- endif -%}
        "brand": { "@type": "Brand", "name": {{ p.vendor | default: shop.name | json }} },
        "offers": [
          {%- for variant in p.variants -%}
            {
              "@type": "Offer",
              {%- if variant.sku != blank -%}"sku": {{ variant.sku | json }},{%- endif -%}
              "availability": "http://schema.org/{% if variant.available %}InStock{% else %}OutOfStock{% endif %}",
              "itemCondition": "https://schema.org/NewCondition",
              "price": {{ variant.price | divided_by: 100.00 | json }},
              "priceCurrency": {{ cart.currency.iso_code | json }},
              "url": {{ request.origin | append: variant.url | json }},
              "seller": { "@id": {{ shop.url | append: '/#organization' | json }} }
            }{% unless forloop.last %},{% endunless %}
          {%- endfor -%}
        ]
      }
    </script>
  {%- endif -%}
  {%- if p != blank -%}
    <div class="tt-balk" data-tt-balk aria-hidden="true">
      <span class="tt-balk__naam">{{ p.title }}<span>{{ v.price | money }}</span></span>
      <button type="button" class="tt-knop" tabindex="-1" data-tt-balkknop>In winkelwagen</button>
    </div>
  {%- endif -%}
</section>
""", {
    "name": "TT: kopen", "tag": "div", "max_blocks": 12,
    "settings": [
        bg("creme"),
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = op de productpagina het product van die pagina, elders het product uit Thema-instellingen > Tide-Tode."},
        kop("De Tide Tode draagtas"),
        {"type": "textarea", "id": "text", "label": "Korte pitch", "default": "Voor iedereen die zijn board een eind moet dragen. Je schuift je board in de tas en hangt hem over je schouder. Het gewicht zit verdeeld over je schouders en de wax blijft van je arm af."},
        {"type": "text", "id": "prijs_tekst", "label": "Tekst als er nog geen product is", "default": "Binnenkort"},
        {"type": "text", "id": "sticker", "label": "Sticker op de eerste foto", "default": ""},
        {"type": "checkbox", "id": "stickers", "label": "Sticker bij de foto's", "default": True},
        {"type": "checkbox", "id": "snel_betalen", "label": "Snelle betaalknoppen tonen (Shop Pay, Apple Pay, enz.)", "default": False},
        {"type": "text", "id": "voorraad", "label": "Voorraadregel (als hij op voorraad is)", "default": "Op voorraad, binnen 2 werkdagen verstuurd"},
        {"type": "checkbox", "id": "betaal_iconen", "label": "Betaalmethoden tonen onder de knop", "default": True},
        {"type": "checkbox", "id": "extra_beelden", "label": "Getekende productbeelden tonen zolang het product geen foto's heeft", "default": True},
        {"type": "header", "content": "Vertrouwen onder de knop"},
        {"type": "text", "id": "v1", "label": "Regel 1", "default": "Verzending door heel Europa"},
        {"type": "text", "id": "v2", "label": "Regel 2", "default": "14 dagen bedenktijd"},
        {"type": "text", "id": "v3", "label": "Regel 3", "default": "Veilig betalen met iDEAL en kaart"},
    ] + s1 + s2,
    "blocks": [
        {"type": "punt", "name": "Voordeel", "settings": [{"type": "text", "id": "tekst", "label": "Tekst", "default": "Handen vrij"}]},
        {"type": "detail", "name": "Uitklapper", "settings": [{"type": "text", "id": "titel", "label": "Titel", "default": "Materiaal"}, {"type": "richtext", "id": "tekst", "label": "Tekst", "default": "<p>Tekst</p>"}]},
    ],
    "presets": [{"name": "TT: kopen", "blocks": [
        {"type": "punt", "settings": {"tekst": "Past op softtops en vollere boards én op hardboards"}},
        {"type": "punt", "settings": {"tekst": "Gewicht goed verdeeld over je rug, niet op één schouder"}},
        {"type": "punt", "settings": {"tekst": "Je natte board hoeft niet vol zand in een dichte hoes"}},
        {"type": "detail", "settings": {"titel": "Wat past erin", "tekst": "<p>Eén universele maat. Van de grote softtop waar je op leert surfen tot je hardboard voor de verstopte spot.</p>"}},
        {"type": "detail", "settings": {"titel": "Materiaal", "tekst": "<p>Zware, waterbestendige stof en sterke stiksels. Gemaakt om jaren mee te gaan, niet voor één zomer.</p>"}},
        {"type": "detail", "settings": {"titel": "Verzending en retour", "tekst": "<p>We versturen door heel Europa. Past hij toch niet bij je? Je hebt 14 dagen bedenktijd.</p>"}}]}]})

# ---------- PROBLEEM: tekst die volloopt, met losse foto's ----------
s1, fb1 = beeld('', 'Foto links', 'tt-foto-probleem-1', 'tide-tode-sjouwen.jpg', 'Board onder de arm op weg naar het strand')
s2, fb2 = beeld('b2_', 'Foto rechts', 'tt-foto-probleem-2', 'tide-tode-onderweg.jpg', 'Onderweg naar de spot')
schrijf('tt-probleem', """
<section class="tt tt-probleem tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap tt-probleem__grid">
    <div class="tt-probleem__foto tt-onthul">""" + B('', fb1, ", sizes: '(min-width: 990px) 40vw, 100vw'") + """</div>
    <blockquote class="tt-probleem__citaat">
      <p class="tt-probleem__tekst" data-tt-vul>{{ section.settings.tekst | escape | replace: '*', '' }}</p>
      {%- if section.settings.slot != blank -%}<footer class="tt-probleem__naam tt-in">{{ section.settings.slot }}</footer>{%- endif -%}
    </blockquote>
  </div>
</section>
""", {
    "name": "TT: het probleem", "tag": "div",
    "settings": [
        bg("creme"),
        {"type": "text", "id": "sticker", "label": "Sticker op de linkerfoto", "default": ""},
        {"type": "textarea", "id": "tekst", "label": "Tekst die volloopt", "default": "Op mijn reizen liep ik vaak een uur naar een spot, met een longboard onder mijn arm. De wax schuurde, mijn schouders deden pijn en op de scooter stuurde ik met één hand. Een dichte boardbag was ook niks: daar moet je je natte, zanderige board elke keer weer in."},
        {"type": "text", "id": "slot", "label": "Slotzin", "info": KOP_INFO, "default": "Veerle, oprichter"},
    ] + s1 + s2,
    "presets": [{"name": "TT: het probleem"}]})

# ---------- ZO WERKT HET ----------
schrijf('tt-zo', """
<section class="tt tt-zo tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    <div class="tt-zo__kop">{%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}</div>
    <ol class="tt-zo__stappen">
      {%- for block in section.blocks -%}
        <li class="tt-zo__stap" {{ block.shopify_attributes }} style="--d: {{ forloop.index0 | times: 0.12 }}s">
          {%- if section.settings.stijl == 'illustratie' and block.settings.ill != blank -%}
            <div class="tt-zo__ill tt-in tt-teken"><span class="tt-zo__nr">{{ forloop.index }}</span>{%- render 'tt-ill', naam: block.settings.ill -%}</div>
          {%- else -%}
            <div class="tt-zo__foto tt-onthul">""" + BB(extra=", sizes: '(min-width: 990px) 30vw, 80vw'") + """<span class="tt-zo__nr">{{ forloop.index }}</span></div>
          {%- endif -%}
          {%- if block.settings.icoon != blank -%}<span class="tt-zo__icoon tt-zo__icoon--{{ forloop.index }}">{% render 'tt-icoon', icoon: block.settings.icoon %}</span>{%- endif -%}
          <h3>{{ block.settings.titel }}</h3>
          <p>{{ block.settings.tekst }}</p>
        </li>
      {%- endfor -%}
    </ol>
  </div>
</section>
""", {
    "name": "TT: zo werkt het", "tag": "div", "max_blocks": 4,
    "settings": [bg("zand"), kop("Zo werkt hij"), {"type": "select", "id": "stijl", "label": "Beeld per stap", "options": [{"value": "illustratie", "label": "Getekende illustratie"}, {"value": "foto", "label": "Foto"}], "default": "illustratie"}],
    "blocks": [{"type": "stap", "name": "Stap", "settings": [
        {"type": "text", "id": "titel", "label": "Titel", "default": "Stap"},
        {"type": "textarea", "id": "tekst", "label": "Tekst", "default": ""},
        {"type": "select", "id": "icoon", "label": "Icoon", "options": [{"value": "", "label": "Geen"}] + ICONEN, "default": ""},
        {"type": "select", "id": "ill", "label": "Illustratie", "options": [{"value": v, "label": l} for v, l in [("draagtas", "De draagtas"), ("golf", "Golf"), ("parasol", "Parasol"), ("busje", "Busje"), ("zon", "Zon")]], "default": "draagtas"}] + blok_beeld('tt-foto-stap-1', '', '')}],
    "presets": [{"name": "TT: zo werkt het", "blocks": [
        {"type": "stap", "settings": {"ill": "draagtas", "titel": "Schuif je board in de tas", "tekst": "Softtop of hardboard, nat of droog. Je hoeft hem niet eerst schoon te maken.", "fallback": "tt-foto-stap-1", "filename": "tide-tode-stap-1.jpg", "alt": "Surfboard in het zand"}},
        {"type": "stap", "settings": {"ill": "golf", "titel": "Hang hem over je schouder", "tekst": "De brede schouderband draagt het gewicht. Je handen zijn vrij voor je stuur, je spullen of een rots om je aan vast te houden.", "fallback": "tt-foto-stap-2", "filename": "tide-tode-stap-2.jpg", "alt": "Surfer met de tas over de schouder"}},
        {"type": "stap", "settings": {"ill": "busje", "titel": "Op naar de spot", "tekst": "Lopend door de duinen, op de fiets of achterop de scooter. Op het strand haal je hem er zo weer uit.", "fallback": "tt-foto-stap-3", "filename": "tide-tode-stap-3.jpg", "alt": "Surfer loopt met board naar zee"}}]}]})

# ---------- MOOD: Pinterest-muur ----------
schrijf('tt-muur', """
<section class="tt tt-muur tt-bg--{{ section.settings.bg }}">
  <div class="tt-muur__kop tt-wrap">
    {%- if section.settings.stickers -%}<div class="tt-stickers tt-stickers--muur1" aria-hidden="true">{% render 'tt-stk', naam: 'schelp' %}</div><div class="tt-stickers tt-stickers--muur2" aria-hidden="true">{% render 'tt-stk', naam: 'zeester' %}</div>{%- endif -%}
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
    {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
  </div>
  <div class="tt-wrap">
    <div class="tt-muur__raster">
      {%- for block in section.blocks -%}
        <figure class="tt-muur__item" {{ block.shopify_attributes }}>
          <div class="tt-onthul">""" + BB(extra=", sizes: '(min-width: 990px) 30vw, 46vw'") + """</div>
          {%- if block.settings.onderschrift != blank -%}<figcaption>{{ block.settings.onderschrift }}</figcaption>{%- endif -%}
        </figure>
      {%- endfor -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: fotomuur", "tag": "div", "max_blocks": 12,
    "settings": [bg("creme"), kop("Onderweg naar het water"), {"type": "checkbox", "id": "stickers", "label": "Stickers bij de kop", "default": True},
                 {"type": "textarea", "id": "text", "label": "Tekst", "default": "Australië, Midden-Amerika, Azië of de duinen om de hoek. De mooiste spots liggen vaak niet naast de parkeerplaats."}],
    "blocks": [{"type": "foto", "name": "Foto", "settings": [
        {"type": "select", "id": "vorm", "label": "Vorm", "options": [{"value": "staand", "label": "Staand"}, {"value": "hoog", "label": "Hoog"}, {"value": "vierkant", "label": "Vierkant"}, {"value": "boog", "label": "Boog"}, {"value": "liggend", "label": "Liggend"}], "default": "staand"},
        {"type": "text", "id": "onderschrift", "label": "Onderschrift"},
        {"type": "text", "id": "sticker", "label": "Sticker"},
        {"type": "select", "id": "sticker_kleur", "label": "Stickerkleur", "options": KLEUREN, "default": "sunshine"},
        {"type": "select", "id": "sticker_icoon", "label": "Stickericoon", "options": [{"value": "", "label": "Geen"}] + ICONEN, "default": ""}] + blok_beeld('tt-foto-mood-1', '', '')}],
    "presets": [{"name": "TT: fotomuur", "blocks": [
        {"type": "foto", "settings": {"vorm": "hoog", "fallback": "tt-foto-mood-1", "onderschrift": "de hike naar de spot", "alt": "Pad door de duinen naar zee"}},
        {"type": "foto", "settings": {"vorm": "vierkant", "fallback": "tt-foto-mood-2", "alt": "Boards in het zand"}},
        {"type": "foto", "settings": {"vorm": "boog", "fallback": "tt-foto-mood-3", "onderschrift": "zonsondergang", "alt": "Zee bij zonsondergang"}},
        {"type": "foto", "settings": {"vorm": "liggend", "fallback": "tt-foto-mood-4", "alt": "Rustige golven"}},
        {"type": "foto", "settings": {"vorm": "staand", "fallback": "tt-foto-mood-5", "onderschrift": "op weg naar zee", "alt": "Surfer op weg naar zee"}},
        {"type": "foto", "settings": {"vorm": "hoog", "fallback": "tt-foto-mood-6", "alt": "Board tegen een muur"}},
        {"type": "foto", "settings": {"vorm": "staand", "fallback": "tt-foto-mood-7", "onderschrift": "van surfers voor surfers", "alt": "Surfers op het strand"}},
        {"type": "foto", "settings": {"vorm": "boog", "fallback": "tt-foto-mood-8", "alt": "Kust van bovenaf"}},
        {"type": "foto", "settings": {"vorm": "vierkant", "fallback": "tt-foto-mood-9", "onderschrift": "door de duinen", "alt": "Hek tussen het duingras"}}]}]})

# ---------- VOOR WIE ----------
schrijf('tt-wie', """
<section class="tt tt-wie tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l tt-wie__kop' -%}
    <div class="tt-wie__grid">
      {%- for block in section.blocks -%}
        <a class="tt-wie__kaart" href="{{ block.settings.link | default: routes.all_products_collection_url }}" {{ block.shopify_attributes }}>
          <div class="tt-wie__foto"><div class="tt-onthul">""" + BB(extra=", sizes: '(min-width: 750px) 48vw, 100vw'") + """</div>{%- render 'tt-sticker', tekst: block.settings.sticker, kleur: block.settings.sticker_kleur, vorm: 'rond', icoon: block.settings.sticker_icoon, class: 'tt-sticker--rechtsboven' -%}</div>
          <div class="tt-wie__tekst">
            <h3>{{ block.settings.titel }}</h3>
            <p>{{ block.settings.tekst }}</p>
            <span class="tt-link">{{ block.settings.knop }}</span>
          </div>
        </a>
      {%- endfor -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: voor wie", "tag": "div", "max_blocks": 3,
    "settings": [bg("zand"), kop("Voor beginners en avonturiers")],
    "blocks": [{"type": "kaart", "name": "Kaart", "settings": [
        {"type": "text", "id": "titel", "label": "Titel", "default": "Titel"},
        {"type": "textarea", "id": "tekst", "label": "Tekst"},
        {"type": "text", "id": "knop", "label": "Linktekst", "default": "Bekijk de draagtas"},
        {"type": "url", "id": "link", "label": "Link"},
        {"type": "text", "id": "sticker", "label": "Sticker"},
        {"type": "select", "id": "sticker_kleur", "label": "Stickerkleur", "options": KLEUREN, "default": "sunshine"},
        {"type": "select", "id": "sticker_icoon", "label": "Stickericoon", "options": [{"value": "", "label": "Geen"}] + ICONEN, "default": ""}] + blok_beeld('tt-foto-beginner', '', '')}],
    "presets": [{"name": "TT: voor wie", "blocks": [
        {"type": "kaart", "settings": {"titel": "Als je leert surfen", "tekst": "Een grote softtop, een lange wandeling van hostel of hotel naar het strand. Met de tas loop je ontspannen en heb je je handen vrij.", "knop": "Bekijk de draagtas", "fallback": "tt-foto-beginner", "filename": "tide-tode-beginner.jpg", "alt": "Beginner met een softtop op het strand"}},
        {"type": "kaart", "settings": {"titel": "Als je de rustige spots opzoekt", "tekst": "Door de bush, over rotsen, achterop de scooter. Jouw board hangt veilig op je rug, jij houdt je handen vrij om te klimmen.", "knop": "Bekijk de draagtas", "fallback": "tt-foto-avontuur", "filename": "tide-tode-avontuur.jpg", "alt": "Surfer klimt over rotsen naar een afgelegen spot"}}]}]})

# ---------- VERHAAL ----------
s, fb = beeld('', 'Foto', 'tt-foto-verhaal', 'tide-tode-verhaal.jpg', 'Op reis met een surfboard')
schrijf('tt-verhaal', """
<section class="tt tt-verhaal tt-bg--{{ section.settings.bg }}" id="tt-verhaal">
  <div class="tt-wrap tt-verhaal__grid">
    <div class="tt-verhaal__foto">{%- if section.settings.stickers -%}<div class="tt-stickers tt-stickers--verhaal" aria-hidden="true">{% render 'tt-stk', naam: 'zon' %}</div>{%- endif -%}<div class="tt-onthul">""" + B('', fb, ", sizes: '(min-width: 990px) 42vw, 90vw'") + """</div></div>
    <div class="tt-verhaal__tekst">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
      <div class="tt-verhaal__body tt-in">{{ section.settings.text }}</div>
      {%- if section.settings.naam != blank -%}<p class="tt-handtekening tt-in">{{ section.settings.naam }}</p>{%- endif -%}
      {%- if section.settings.link_label != blank -%}<a class="tt-link tt-in" href="{{ section.settings.link | default: '/pages/over-ons' }}">{{ section.settings.link_label }}</a>{%- endif -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: het verhaal", "tag": "div",
    "settings": [
        bg("deep"),
        kop("“Dit moet stukken|comfortabeler kunnen.”"),
        {"type": "richtext", "id": "text", "label": "Tekst", "default": "<p>Losse touwtjes, spanbanden, standaardhoezen: ik heb het allemaal geprobeerd. Niets hield het lang vol.</p><p>In februari 2025 kwam er een vriend bij die net zo gek is op surfen en precies dezelfde frustratie kende. Toen zijn we de tas gewoon zelf gaan maken. Robuust, van zware stof, en mooi genoeg om mee te nemen op reis.</p>"},
        {"type": "text", "id": "naam", "label": "Ondertekening", "default": "Veerle"},
        {"type": "checkbox", "id": "stickers", "label": "Sticker bij de foto", "default": True},
        {"type": "text", "id": "link_label", "label": "Link", "default": "Lees het hele verhaal"},
        {"type": "url", "id": "link", "label": "Link-adres"},
    ] + s,
    "presets": [{"name": "TT: het verhaal"}]})

# ---------- SLOT ----------
s, fb = beeld('', 'Foto', 'tt-foto-slot', 'tide-tode-slot.jpg', 'Zee bij zonsondergang')
schrijf('tt-slot', PRODUCT + """
<section class="tt tt-slot">
  <div class="tt-slot__foto">""" + B('', fb, ", sizes: '100vw'") + """</div>
  <div class="tt-slot__inhoud tt-wrap">
    <div class="tt-slot__maan tt-in">{% render 'tt-logo', variant: 'maan' %}</div>
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--xl' -%}
    <div class="tt-knoppen tt-in">
      <a class="tt-knop tt-knop--licht" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}<span aria-hidden="true">→</span></a>
    </div>
  </div>
</section>
""", {
    "name": "TT: slot", "tag": "div",
    "settings": [
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        kop("Tot in|het water"),
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Bestel de draagtas"},
        {"type": "url", "id": "btn_link", "label": "Knop-link"},
    ] + s,
    "presets": [{"name": "TT: slot"}]})

# ---------- MERK: de maan draagt het getij ----------
schrijf('tt-merk', """
<section class="tt tt-merk tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap tt-merk__wrap">
    <div class="tt-merk__maan">{% render 'tt-logo', variant: 'maan' %}</div>
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
    {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    {%- if section.settings.maan_vandaag -%}
      <div class="tt-maanstand tt-in" data-tt-maanstand hidden>
        <svg class="tt-maanstand__beeld" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" class="tt-maanstand__donker"/><path class="tt-maanstand__licht" d=""/></svg>
        <div class="tt-maanstand__tekst">
          <p class="tt-maanstand__kop">De maan vanavond: <strong data-tt-maan-naam></strong></p>
          <p data-tt-maan-info></p>
        </div>
      </div>
    {%- endif -%}
    <ul class="tt-merk__iconen tt-in" aria-hidden="true">
      {%- assign lijst = section.settings.iconen | split: ',' -%}
      {%- for i in lijst -%}<li>{% render 'tt-icoon', icoon: i %}</li>{%- endfor -%}
    </ul>
  </div>
  <div class="tt-merk__woord" aria-hidden="true">
    <div class="tt-merk__spoor" data-tt-schuif>
      {%- for n in (1..3) -%}{% render 'tt-logo', variant: 'woord' %}<span class="tt-merk__tussen">{% render 'tt-logo', variant: 'maan-simpel' %}</span>{%- endfor -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: merk", "tag": "div",
    "settings": [
        bg("deep"),
        kop("Waarom er een maan|in ons logo staat"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "De maan trekt aan de zee en maakt zo eb en vloed, in het Engels de tide. Ze draagt als het ware de zee. Wij dragen je board. Vandaar de maan, met drie golfjes in haar arm."},
        {"type": "text", "id": "iconen", "label": "Iconen (komma's, zonder spaties)", "default": ""},
        {"type": "checkbox", "id": "maan_vandaag", "label": "Maanstand van vandaag tonen", "default": True, "info": "Berekend in de browser: de stand van de maan vanavond, en of het springtij is."},
    ],
    "presets": [{"name": "TT: merk"}]})

# ---------- PAST JOUW BOARD? ----------
schrijf('tt-check', PRODUCT + """
{%- if section.settings.bevestigd or request.design_mode -%}
<section class="tt tt-check tt-bg--{{ section.settings.bg }}" data-tt-check data-min="{{ section.settings.min_inch }}" data-max="{{ section.settings.max_inch }}">
  <div class="tt-wrap tt-check__grid">
    <div class="tt-check__tekst">
      {%- unless section.settings.bevestigd -%}<p class="tt-check__let-op">Alleen zichtbaar in de editor: vul de echte maten in en zet 'Maten zijn bevestigd' aan.</p>{%- endunless -%}
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
      <div class="tt-check__invoer tt-in">
        <label class="tt-check__label" for="tt-check-{{ section.id }}">Lengte van je board</label>
        <output class="tt-check__waarde" for="tt-check-{{ section.id }}" data-tt-check-waarde>7'0"</output>
        <input class="tt-check__schuif" id="tt-check-{{ section.id }}" type="range" min="48" max="132" step="1" value="{{ section.settings.start_inch }}" data-tt-check-schuif aria-describedby="tt-check-uit-{{ section.id }}">
        <div class="tt-check__schaal" aria-hidden="true"><span>4'0"</span><span>7'6"</span><span>11'0"</span></div>
      </div>
      <div class="tt-check__uitkomst tt-in" id="tt-check-uit-{{ section.id }}" aria-live="polite">
        <p class="tt-check__antwoord" data-tt-check-antwoord></p>
        <p class="tt-check__uitleg" data-tt-check-uitleg></p>
      </div>
      <div class="tt-knoppen tt-in">
        <a class="tt-knop" href="{% if p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}" data-tt-check-knop>{{ section.settings.btn_label }}<span aria-hidden="true">→</span></a>
      </div>
    </div>
    <div class="tt-check__beeld" aria-hidden="true">
      <svg viewBox="0 0 200 560" class="tt-check__svg">
        <line x1="20" x2="180" class="tt-check__maxlijn" data-tt-check-maxlijn/>
        <text x="182" class="tt-check__maxtekst" data-tt-check-maxtekst text-anchor="end"></text>
        <g data-tt-check-board>
          <path class="tt-check__board" d=""/>
          <line class="tt-check__stringer" x1="100" x2="100"/>
          <rect class="tt-check__band" x="52" width="96" height="16" rx="5"/>
          <rect class="tt-check__band" x="52" width="96" height="16" rx="5"/>
        </g>
      </svg>
    </div>
  </div>
</section>
{%- endif -%}
""", {
    "name": "TT: past mijn board?", "tag": "div",
    "settings": [
        bg("zand"),
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        kop("Past mijn board erin?"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Schuif naar de lengte van je board en zie meteen of hij in de tas past."},
        {"type": "header", "content": "Maten van de tas"},
        {"type": "checkbox", "id": "bevestigd", "label": "Maten zijn bevestigd", "default": False, "info": "Pas als dit aan staat, zien bezoekers de checker. Zo komt er nooit een verkeerd antwoord online."},
        {"type": "range", "id": "min_inch", "label": "Kortste board (inch)", "min": 48, "max": 96, "step": 1, "default": 66, "info": "12 inch = 1 voet. 66 = 5 voet 6 inch."},
        {"type": "range", "id": "max_inch", "label": "Langste board (inch)", "min": 72, "max": 132, "step": 1, "default": 114, "info": "114 = 9 voet 6 inch."},
        {"type": "range", "id": "start_inch", "label": "Startwaarde schuif (inch)", "min": 48, "max": 132, "step": 1, "default": 84},
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Bekijk de draagtas"},
    ],
    "presets": [{"name": "TT: past mijn board?"}]})

# ---------- SURFCHECK: hoe is de zee vandaag? ----------
schrijf('tt-surfcheck', """
{%- capture spots -%}[{%- for block in section.blocks -%}{"naam":{{ block.settings.naam | json }},"lat":{{ block.settings.lat | plus: 0 }},"lon":{{ block.settings.lon | plus: 0 }}}{% unless forloop.last %},{% endunless %}{%- endfor -%}]{%- endcapture -%}
<section class="tt tt-surfcheck tt-bg--{{ section.settings.bg }}" data-tt-surfcheck data-sleutel="{{ settings.tt_meteo_key | escape }}" id="surfcheck">
  <script type="application/json" data-tt-spots>{{ spots }}</script>
  <div class="tt-wrap">
    <div class="tt-surfcheck__kop">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </div>
    <div class="tt-surfcheck__spots tt-in" role="tablist" aria-label="Kies je spot">
      {%- for block in section.blocks -%}
        <button type="button" role="tab" class="tt-surfcheck__spot" data-tt-spot="{{ forloop.index0 }}" aria-selected="{% if forloop.first %}true{% else %}false{% endif %}" {{ block.shopify_attributes }}>{{ block.settings.naam }}</button>
      {%- endfor -%}
    </div>
    <div class="tt-surfcheck__paneel tt-in" aria-live="polite" data-tt-paneel>
      <div class="tt-surfcheck__oordeel">
        <p class="tt-surfcheck__zin" data-tt-oordeel>Even kijken naar de zee</p>
        <p class="tt-surfcheck__tijd" data-tt-tijd></p>
      </div>
      <dl class="tt-surfcheck__cijfers">
        <div><dt>{% render 'tt-icoon', icoon: 'golf' %}Golven</dt><dd data-tt-golf></dd><span data-tt-golf-extra></span></div>
        <div data-tt-windblok><dt>{% render 'tt-icoon', icoon: 'meeuw' %}Wind</dt><dd data-tt-wind></dd><span data-tt-wind-extra></span></div>
        <div><dt>{% render 'tt-icoon', icoon: 'schelp' %}Water</dt><dd data-tt-water></dd><span data-tt-water-extra></span></div>
        <div><dt>{% render 'tt-icoon', icoon: 'golfjes' %}Getij</dt><dd data-tt-getij></dd><span data-tt-getij-extra></span></div>
      </dl>
      <div class="tt-surfcheck__curve" aria-hidden="true">
        <svg viewBox="0 0 600 120" preserveAspectRatio="none"><path class="tt-surfcheck__vlak" data-tt-curve-vlak d=""/><path class="tt-surfcheck__lijn" data-tt-curve d=""/><line class="tt-surfcheck__nu" data-tt-nu y1="0" y2="120"/></svg>
        <div class="tt-surfcheck__uren"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span></div>
      </div>
      <div class="tt-surfcheck__onder">
        <p class="tt-surfcheck__bron">Indicatie van Open-Meteo. Check altijd zelf de omstandigheden ter plekke.</p>
        {%- if section.settings.btn_label != blank -%}<a class="tt-link" href="{% if settings.tt_product != blank %}{{ settings.tt_product.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}</a>{%- endif -%}
      </div>
    </div>
  </div>
</section>
""", {
    "name": "TT: surfcheck", "tag": "div", "max_blocks": 8,
    "settings": [
        bg("deep"),
        kop("De zee van vandaag"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Golven, wind, watertemperatuur en getij voor een paar spots waar we graag komen."},
        {"type": "text", "id": "btn_label", "label": "Link onder de check", "default": "Bekijk de draagtas"},
    ],
    "blocks": [{"type": "spot", "name": "Spot", "settings": [
        {"type": "text", "id": "naam", "label": "Naam", "default": "Spot"},
        {"type": "text", "id": "lat", "label": "Breedtegraad", "default": "52.11", "info": "Rechtsklik op de plek in Google Maps om de coördinaten te kopiëren. Kies een punt net in zee."},
        {"type": "text", "id": "lon", "label": "Lengtegraad", "default": "4.27"}]}],
    "presets": [{"name": "TT: surfcheck", "blocks": [
        {"type": "spot", "settings": {"naam": "Scheveningen", "lat": "52.11", "lon": "4.26"}},
        {"type": "spot", "settings": {"naam": "Zandvoort", "lat": "52.37", "lon": "4.50"}},
        {"type": "spot", "settings": {"naam": "Domburg", "lat": "51.57", "lon": "3.47"}},
        {"type": "spot", "settings": {"naam": "Hossegor", "lat": "43.66", "lon": "-1.46"}},
        {"type": "spot", "settings": {"naam": "Ericeira", "lat": "38.97", "lon": "-9.43"}},
        {"type": "spot", "settings": {"naam": "Canggu, Bali", "lat": "-8.66", "lon": "115.12"}}]}]})

# ---------- VERGELIJKEN ----------
schrijf('tt-vergelijk', """
<section class="tt tt-vergelijk tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    <div class="tt-vergelijk__kop">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </div>
    <div class="tt-vergelijk__scroll tt-in">
      <table class="tt-vergelijk__tabel">
        <thead>
          <tr>
            <td></td>
            <th scope="col" class="tt-vergelijk__wij"><span class="tt-vergelijk__logo">{% render 'tt-logo', variant: 'maan-simpel' %}</span>{{ section.settings.kol1 }}</th>
            <th scope="col">{{ section.settings.kol2 }}</th>
            <th scope="col">{{ section.settings.kol3 }}</th>
            <th scope="col">{{ section.settings.kol4 }}</th>
          </tr>
        </thead>
        <tbody>
          {%- for block in section.blocks -%}
            <tr {{ block.shopify_attributes }}>
              <th scope="row">{{ block.settings.punt }}</th>
              {%- assign waarden = block.settings.wij | append: ',' | append: block.settings.arm | append: ',' | append: block.settings.banden | append: ',' | append: block.settings.hoes | split: ',' -%}
              {%- for w in waarden -%}
                <td class="tt-vergelijk__cel tt-vergelijk__cel--{{ w }}{% if forloop.first %} tt-vergelijk__wij{% endif %}">
                  {%- case w -%}
                    {%- when 'ja' -%}<span class="tt-vergelijk__teken" aria-hidden="true">✓</span><span class="visually-hidden">ja</span>
                    {%- when 'deels' -%}<span class="tt-vergelijk__teken" aria-hidden="true">~</span><span class="visually-hidden">deels</span>
                    {%- else -%}<span class="tt-vergelijk__teken" aria-hidden="true">✕</span><span class="visually-hidden">nee</span>
                  {%- endcase -%}
                </td>
              {%- endfor -%}
            </tr>
          {%- endfor -%}
        </tbody>
      </table>
    </div>
    <p class="tt-vergelijk__uitleg tt-in"><span>✓ ja</span><span>~ deels</span><span>✕ nee</span></p>
  </div>
</section>
""", {
    "name": "TT: vergelijken", "tag": "div", "max_blocks": 10,
    "settings": [
        bg("creme"),
        kop("Tas, arm, spanband of boardbag"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Zo verhoudt de tas zich tot wat de meeste surfers nu doen."},
        {"type": "text", "id": "kol1", "label": "Kolom 1", "default": "Tide-Tode"},
        {"type": "text", "id": "kol2", "label": "Kolom 2", "default": "Onder je arm"},
        {"type": "text", "id": "kol3", "label": "Kolom 3", "default": "Touwtjes of spanbanden"},
        {"type": "text", "id": "kol4", "label": "Kolom 4", "default": "Boardbag"},
    ],
    "blocks": [{"type": "rij", "name": "Rij", "settings": [
        {"type": "text", "id": "punt", "label": "Punt", "default": "Punt"}] + [
        {"type": "select", "id": k, "label": l, "options": [{"value": "ja", "label": "Ja"}, {"value": "deels", "label": "Deels"}, {"value": "nee", "label": "Nee"}], "default": "ja" if k == "wij" else "nee"}
        for k, l in [("wij", "Kolom 1"), ("arm", "Kolom 2"), ("banden", "Kolom 3"), ("hoes", "Kolom 4")]]}],
    "presets": [{"name": "TT: vergelijken", "blocks": [
        {"type": "rij", "settings": {"punt": "Allebei je handen vrij", "wij": "ja", "arm": "nee", "banden": "deels", "hoes": "deels"}},
        {"type": "rij", "settings": {"punt": "Geen wax op je arm", "wij": "ja", "arm": "nee", "banden": "deels", "hoes": "ja"}},
        {"type": "rij", "settings": {"punt": "Gewicht verdeeld over je rug", "wij": "ja", "arm": "nee", "banden": "nee", "hoes": "nee"}},
        {"type": "rij", "settings": {"punt": "Nat en zanderig board meteen mee", "wij": "ja", "arm": "ja", "banden": "ja", "hoes": "nee"}},
        {"type": "rij", "settings": {"punt": "Veilig op de fiets of scooter", "wij": "ja", "arm": "nee", "banden": "deels", "hoes": "deels"}},
        {"type": "rij", "settings": {"punt": "Klein mee in je reisbagage", "wij": "ja", "arm": "ja", "banden": "ja", "hoes": "nee"}}]}]})

# ---------- DETAILS: close-ups van de tas ----------
schrijf('tt-detail', """
{%- liquid
  assign heeft = false
  for block in section.blocks
    if block.settings.image != blank
      assign heeft = true
    elsif block.settings.filename != blank and images[block.settings.filename] != blank
      assign heeft = true
    endif
  endfor
-%}
{%- if heeft or request.design_mode -%}
<section class="tt tt-detail tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    <div class="tt-detail__kop">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </div>
    <div class="tt-detail__grid">
      {%- for block in section.blocks -%}
        {%- assign img = block.settings.image -%}
        {%- if img == blank and block.settings.filename != blank -%}{%- assign img = images[block.settings.filename] -%}{%- endif -%}
        {%- if img != blank or request.design_mode -%}
          <figure class="tt-detail__item" {{ block.shopify_attributes }}>
            <div class="tt-detail__foto tt-onthul">{%- render 'tt-beeld', image: img, filename: block.settings.filename, alt: block.settings.titel, sizes: '(min-width: 990px) 25vw, 50vw' -%}</div>
            <figcaption><strong>{{ block.settings.titel }}</strong>{%- if block.settings.tekst != blank -%}<span>{{ block.settings.tekst }}</span>{%- endif -%}</figcaption>
          </figure>
        {%- endif -%}
      {%- endfor -%}
    </div>
  </div>
</section>
{%- endif -%}
""", {
    "name": "TT: details van de tas", "tag": "div", "max_blocks": 8,
    "settings": [{"type": "paragraph", "content": "Bezoekers zien deze sectie pas als er minstens één foto in staat."}, bg("creme"), kop("De details"),
                 {"type": "textarea", "id": "text", "label": "Tekst", "default": "Robuust, van zware stof, en gemaakt om jaren mee op reis te gaan."}],
    "blocks": [{"type": "detail", "name": "Detail", "settings": [
        {"type": "image_picker", "id": "image", "label": "Foto (close-up, vierkant)"},
        {"type": "text", "id": "filename", "label": "Bestandsnaam", "info": "Of upload in Content > Bestanden met precies deze naam."},
        {"type": "text", "id": "titel", "label": "Titel", "default": "Detail"},
        {"type": "text", "id": "tekst", "label": "Tekst"}]}],
    "presets": [{"name": "TT: details van de tas", "blocks": [
        {"type": "detail", "settings": {"titel": "Zware stof", "tekst": "Waterbestendig en gemaakt voor nat, zand en zout.", "filename": "tide-tode-detail-stof.jpg"}},
        {"type": "detail", "settings": {"titel": "Sterke stiksels", "tekst": "Stevig gestikt op de plekken waar de tas het zwaarst draagt.", "filename": "tide-tode-detail-stiksels.jpg"}},
        {"type": "detail", "settings": {"titel": "De schouderband", "tekst": "Breed, zodat hij niet in je schouder snijdt.", "filename": "tide-tode-detail-schouderband.jpg"}},
        {"type": "detail", "settings": {"titel": "De tegelprint", "tekst": "Geweven in terracotta, dusty blue en mosterd.", "filename": "tide-tode-detail-print.jpg"}}]}]})

# ---------- RASTER: fotogrid met tekstvakken (zoals het merkboek) ----------
schrijf('tt-raster', """
<section class="tt tt-raster" aria-label="{{ section.settings.label | escape }}">
  <div class="tt-raster__grid">
    {%- for block in section.blocks -%}
      {%- case block.type -%}
        {%- when 'foto' -%}
          <div class="tt-raster__vak tt-raster__vak--foto tt-onthul" {{ block.shopify_attributes }}>""" + BB(extra=", sizes: '(min-width: 750px) 33vw, 50vw'") + """</div>
        {%- when 'tekst' -%}
          <div class="tt-raster__vak tt-raster__vak--tekst" {{ block.shopify_attributes }}>
            <h3 class="tt-raster__hand">{{ block.settings.titel }}</h3>
            <p class="tt-raster__regels">{{ block.settings.regels | newline_to_br }}</p>
            {%- if block.settings.link_label != blank -%}<a class="tt-link" href="{{ block.settings.link | default: routes.all_products_collection_url }}">{{ block.settings.link_label }}</a>{%- endif -%}
          </div>
        {%- when 'logo' -%}
          <div class="tt-raster__vak tt-raster__vak--logo" {{ block.shopify_attributes }} data-tt-kantel>
            {%- render 'tt-logo', variant: block.settings.icoon -%}
            {%- render 'tt-logo', variant: 'staand' -%}
            <p class="tt-raster__onder">{{ block.settings.onder }}</p>
          </div>
      {%- endcase -%}
    {%- endfor -%}
  </div>
</section>
""", {
    "name": "TT: fotoraster", "tag": "div", "max_blocks": 12,
    "settings": [{"type": "text", "id": "label", "label": "Naam voor schermlezers", "default": "Sfeer en het merk"}],
    "blocks": [
        {"type": "foto", "name": "Foto", "settings": blok_beeld('tt-foto-mood-1', '', '')},
        {"type": "tekst", "name": "Tekstvak", "settings": [
            {"type": "text", "id": "titel", "label": "Titel (handgeschreven)", "default": "De Draagtas"},
            {"type": "textarea", "id": "regels", "label": "Regels (één per regel)", "default": "Zware stof\nBrede schouderband\nSofttop en hardboard"},
            {"type": "text", "id": "link_label", "label": "Link"},
            {"type": "url", "id": "link", "label": "Link-adres"}]},
        {"type": "logo", "name": "Logo", "settings": [
            {"type": "select", "id": "icoon", "label": "Icoon", "options": [{"value": "maan", "label": "A, het board"}, {"value": "icoon-zon", "label": "B, zon en zee"}, {"value": "icoon-tegel", "label": "C, de tegel"}], "default": "maan"},
            {"type": "text", "id": "onder", "label": "Regel eronder", "default": "Est 2025"}]},
    ],
    "presets": [{"name": "TT: fotoraster", "blocks": [
        {"type": "foto", "settings": {"fallback": "tt-foto-stap-3", "alt": "Surfer loopt met een geel board over het strand"}},
        {"type": "tekst", "settings": {"titel": "De Draagtas", "regels": "Zware stof\nBrede schouderband\nSofttop en hardboard", "link_label": "Bekijk de draagtas"}},
        {"type": "foto", "settings": {"fallback": "tt-foto-beginner", "alt": "Surfster met board onder een roze lucht"}},
        {"type": "logo", "settings": {"icoon": "maan", "onder": "Est 2025"}},
        {"type": "foto", "settings": {"fallback": "tt-foto-mood-5", "alt": "Twee surfers lopen de zee in"}},
        {"type": "logo", "settings": {"icoon": "icoon-zon", "onder": "Handen vrij"}},
        {"type": "foto", "settings": {"fallback": "tt-foto-mood-6", "alt": "Surfboard tegen een busje in de duinen"}},
        {"type": "tekst", "settings": {"titel": "Het Verhaal", "regels": "Bedacht in Australië\nGemaakt voor onderweg\nVan surfers voor surfers", "link_label": "Lees het verhaal", "link": "/pages/over-ons"}},
        {"type": "foto", "settings": {"fallback": "tt-foto-stap-1", "alt": "Wit surfboard rechtop in het zand"}}]}]})

# ---------- STICKERS OP ZEE ----------
s, fb = beeld('', 'Achtergrondfoto', 'tt-foto-zee-zw', 'tide-tode-stickers-zee.jpg', 'Zee in zwart-wit')
schrijf('tt-stickerzee', """
<section class="tt tt-stickerzee" aria-label="{{ section.settings.hand | escape }}">
  <div class="tt-stickerzee__foto">""" + B('', fb, ", sizes: '100vw'") + """</div>
  <div class="tt-stickerzee__stickers" aria-hidden="true">
    <span class="sz sz--tas" data-tt-snelheid="0.35">{% render 'tt-stk', naam: 'draagtas' %}</span>
    <span class="sz sz--zon" data-tt-snelheid="0.6">{% render 'tt-stk', naam: 'zon' %}</span>
    <span class="sz sz--schelp" data-tt-snelheid="0.5">{% render 'tt-stk', naam: 'schelp' %}</span>
    <span class="sz sz--ster" data-tt-snelheid="0.75">{% render 'tt-stk', naam: 'zeester' %}</span>
    <span class="sz sz--golf" data-tt-snelheid="0.25">{% render 'tt-stk', naam: 'golf' %}</span>
    <span class="sz sz--palm" data-tt-snelheid="0.55">{% render 'tt-stk', naam: 'palm' %}</span>
  </div>
  <div class="tt-stickerzee__tekst">
    <p class="tt-stickerzee__hand">{{ section.settings.hand }}</p>
    {%- if section.settings.label != blank -%}<p class="tt-stickerzee__label">{{ section.settings.label }}</p>{%- endif -%}
  </div>
</section>
""", {
    "name": "TT: stickers op zee", "tag": "div",
    "settings": [
        {"type": "text", "id": "hand", "label": "Handgeschreven regel", "default": "Handen vrij, op weg naar zee"},
        {"type": "text", "id": "label", "label": "Kleine regel", "default": "Van surfers, voor surfers"},
    ] + s,
    "presets": [{"name": "TT: stickers op zee"}]})

# ---------- KAART: het verhaal als drukwerk ----------
schrijf('tt-kaart', """
<section class="tt tt-kaart tt-bg--{{ section.settings.bg }}" id="tt-verhaal">
  <div class="tt-wrap tt-kaart__grid">
    <div class="tt-kaart__navy tt-in" data-tt-kantel>
      <div class="tt-kaart__logo">{%- render 'tt-logo', variant: 'liggend' -%}</div>
      <div class="tt-kaart__body">
        {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
        <div class="tt-kaart__tekst">{{ section.settings.text }}</div>
      </div>
      <dl class="tt-kaart__gegevens">
        {%- for block in section.blocks -%}<div {{ block.shopify_attributes }}><dt>{{ block.settings.label }}</dt><dd>{{ block.settings.waarde }}</dd></div>{%- endfor -%}
      </dl>
    </div>
    <div class="tt-kaart__creme tt-in tt-teken" style="--d: .2s" data-tt-kantel>
      {%- render 'tt-ill', naam: section.settings.ill -%}
      {%- if section.settings.naam != blank -%}<p class="tt-handtekening">{{ section.settings.naam }}</p>{%- endif -%}
      {%- if section.settings.link_label != blank -%}<a class="tt-link" href="{{ section.settings.link | default: '/pages/over-ons' }}">{{ section.settings.link_label }}</a>{%- endif -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: verhaal als kaart", "tag": "div", "max_blocks": 4,
    "settings": [
        bg("creme"),
        kop("“Dit moet stukken|comfortabeler kunnen.”"),
        {"type": "richtext", "id": "text", "label": "Tekst", "default": "<p>Op hikes naar afgelegen surfspots sjouwde ik een longboard mee dat nergens lekker vast te houden is. Losse touwtjes, spanbanden en standaardhoezen hielden het geen van allen vol.</p><p>In februari 2025 kwam er een vriend bij die precies dezelfde frustratie kende. Toen zijn we de tas gewoon zelf gaan maken.</p>"},
        {"type": "select", "id": "ill", "label": "Illustratie", "options": [{"value": v, "label": l} for v, l in [("parasol", "Parasol"), ("draagtas", "De draagtas"), ("busje", "Busje"), ("golf", "Golf"), ("zon", "Zon")]], "default": "parasol"},
        {"type": "text", "id": "naam", "label": "Ondertekening", "default": "Veerle"},
        {"type": "text", "id": "link_label", "label": "Link", "default": "Lees het hele verhaal"},
        {"type": "url", "id": "link", "label": "Link-adres"},
    ],
    "blocks": [{"type": "regel", "name": "Gegeven", "settings": [
        {"type": "text", "id": "label", "label": "Label", "default": "Plaats"},
        {"type": "text", "id": "waarde", "label": "Waarde (handgeschreven)", "default": "Nederland"}]}],
    "presets": [{"name": "TT: verhaal als kaart", "blocks": [
        {"type": "regel", "settings": {"label": "Bedacht", "waarde": "in Australië"}},
        {"type": "regel", "settings": {"label": "Sinds", "waarde": "2025"}},
        {"type": "regel", "settings": {"label": "Voor", "waarde": "surfers overal"}}]}]})

# ---------- PATROON met afsluiter ----------
schrijf('tt-patroon', PRODUCT + """
<section class="tt tt-patroon">
  <div class="tt-patroon__vormen" aria-hidden="true" data-tt-snelheid="0.22">{%- render 'tt-patroon' -%}</div>
  <div class="tt-patroon__inhoud">
    <div class="tt-patroon__logo">{%- render 'tt-logo', variant: 'staand', label: shop.name -%}</div>
    {%- if section.settings.hand != blank -%}<p class="tt-patroon__hand">{{ section.settings.hand }}</p>{%- endif -%}
    {%- if section.settings.btn_label != blank -%}<a class="tt-knop tt-knop--licht" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}<span aria-hidden="true">→</span></a>{%- endif -%}
  </div>
</section>
""", {
    "name": "TT: patroon", "tag": "div",
    "settings": [
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        {"type": "text", "id": "hand", "label": "Handgeschreven regel", "default": "Tot in het water"},
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Bestel de draagtas"},
        {"type": "url", "id": "btn_link", "label": "Knop-link"},
    ],
    "presets": [{"name": "TT: patroon"}]})

# ---------- SPECS: de tas uitgelegd, met genummerde tekening ----------
schrijf('tt-specs', """
<section class="tt tt-specs tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    <div class="tt-specs__kop">
      {%- if section.settings.hand != blank -%}<p class="tt-specs__hand tt-in">{{ section.settings.hand }}</p>{%- endif -%}
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
    </div>
    <div class="tt-specs__grid">
      <figure class="tt-specs__beeld tt-teken tt-in"><div class="tt-specs__vlak">
        {%- render 'tt-ill', naam: 'draagtas' -%}
        {%- assign n = 0 -%}
        {%- for block in section.blocks -%}{%- if block.type == 'punt' -%}{%- assign n = n | plus: 1 -%}
          <span class="tt-specs__punt" style="left: {{ block.settings.x }}%; top: {{ block.settings.y }}%; --d: {{ n | times: 0.15 | plus: 0.6 }}s" aria-hidden="true">{{ n }}</span>
        {%- endif -%}{%- endfor -%}
      </div></figure>
      <ol class="tt-specs__uitleg">
        {%- for block in section.blocks -%}{%- if block.type == 'punt' -%}
          <li class="tt-in" style="--d: {{ forloop.index0 | times: 0.1 }}s" {{ block.shopify_attributes }}><h3>{{ block.settings.titel }}</h3><p>{{ block.settings.tekst }}</p></li>
        {%- endif -%}{%- endfor -%}
      </ol>
    </div>
    <div class="tt-specs__kaart tt-in" data-tt-kantel>
      <div class="tt-specs__kaartkop">{%- render 'tt-logo', variant: 'maan' -%}<p>{{ section.settings.kaart_titel }}</p></div>
      <dl>
        {%- for block in section.blocks -%}{%- if block.type == 'spec' -%}
          <div {{ block.shopify_attributes }}><dt>{{ block.settings.label }}</dt><dd>{{ block.settings.waarde }}</dd></div>
        {%- endif -%}{%- endfor -%}
      </dl>
    </div>
  </div>
</section>
""", {
    "name": "TT: de tas uitgelegd", "tag": "div", "max_blocks": 16,
    "settings": [
        bg("papier"),
        {"type": "text", "id": "hand", "label": "Handgeschreven regel", "default": "De details"},
        kop("Zo zit hij|in elkaar"),
        {"type": "text", "id": "kaart_titel", "label": "Titel van de kaart", "default": "Specificaties"},
    ],
    "blocks": [
        {"type": "punt", "name": "Genummerd punt", "settings": [
            {"type": "text", "id": "titel", "label": "Titel", "default": "Onderdeel"},
            {"type": "textarea", "id": "tekst", "label": "Tekst", "default": ""},
            {"type": "range", "id": "x", "label": "Positie op de tekening (links)", "min": 0, "max": 100, "step": 1, "unit": "%", "default": 50},
            {"type": "range", "id": "y", "label": "Positie op de tekening (boven)", "min": 0, "max": 100, "step": 1, "unit": "%", "default": 50}]},
        {"type": "spec", "name": "Specificatie", "settings": [
            {"type": "text", "id": "label", "label": "Label", "default": "Maat"},
            {"type": "text", "id": "waarde", "label": "Waarde", "default": ""}]},
    ],
    "presets": [{"name": "TT: de tas uitgelegd", "blocks": [
        {"type": "punt", "settings": {"titel": "Schouderband", "tekst": "Breed en stevig. Je hangt de tas over één schouder of schuin over je rug.", "x": 50, "y": 8}},
        {"type": "punt", "settings": {"titel": "Tegelstof", "tekst": "Stevige geweven stof met ons tegelpatroon. Zand klop je er zo af.", "x": 50, "y": 70}},
        {"type": "punt", "settings": {"titel": "Je board", "tekst": "Softtop of hardboard, kort of lang. Nat en vol zand mag gewoon.", "x": 88, "y": 50}},
        {"type": "spec", "settings": {"label": "Maat", "waarde": "Eén universele maat"}},
        {"type": "spec", "settings": {"label": "Past op", "waarde": "Softtops en hardboards"}},
        {"type": "spec", "settings": {"label": "Stof", "waarde": "Geweven jacquard met tegelprint"}},
        {"type": "spec", "settings": {"label": "Print", "waarde": "Tegels in terracotta, dusty blue en mosterd"}},
        {"type": "spec", "settings": {"label": "Dragen", "waarde": "Over je schouder of op je rug"}},
        {"type": "spec", "settings": {"label": "Onderhoud", "waarde": "Uitspoelen met zoet water en laten drogen"}}]}]})

# ---------- KAARTEN: drie gekleurde kaarten met een tekening ----------
schrijf('tt-kaarten', """
<section class="tt tt-kaarten tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    {%- if section.settings.heading != blank -%}<div class="tt-kaarten__kop">{%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}</div>{%- endif -%}
    <div class="tt-kaarten__grid">
      {%- for block in section.blocks -%}
        <article class="tt-kaarten__kaart tt-kaarten__kaart--{{ block.settings.kleur }} tt-in tt-teken" style="--d: {{ forloop.index0 | times: 0.12 }}s" data-tt-kantel {{ block.shopify_attributes }}>
          <div class="tt-kaarten__ill">{%- render 'tt-ill', naam: block.settings.ill -%}</div>
          <h3>{{ block.settings.titel }}</h3>
          <p>{{ block.settings.tekst }}</p>
        </article>
      {%- endfor -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: drie kaarten", "tag": "div", "max_blocks": 4,
    "settings": [bg("creme"), kop("Goed om te weten")],
    "blocks": [{"type": "kaart", "name": "Kaart", "settings": [
        {"type": "select", "id": "kleur", "label": "Kleur", "options": [{"value": v, "label": l} for v, l in [("baby", "Baby"), ("rose", "Rose"), ("zand", "Zand"), ("papier", "Papier")]], "default": "baby"},
        {"type": "select", "id": "ill", "label": "Tekening", "options": [{"value": v, "label": l} for v, l in [("busje", "Busje"), ("golf", "Golf"), ("zon", "Zon"), ("parasol", "Parasol"), ("draagtas", "De draagtas"), ("tas", "Board met banden")]], "default": "busje"},
        {"type": "text", "id": "titel", "label": "Titel", "default": "Titel"},
        {"type": "textarea", "id": "tekst", "label": "Tekst", "default": ""}]}],
    "presets": [{"name": "TT: drie kaarten", "blocks": [
        {"type": "kaart", "settings": {"kleur": "baby", "ill": "busje", "titel": "Verzending", "tekst": "We versturen door heel Europa. Je krijgt een track and trace zodra hij onderweg is."}},
        {"type": "kaart", "settings": {"kleur": "rose", "ill": "golf", "titel": "14 dagen bedenktijd", "tekst": "Past hij toch niet bij je board? Stuur hem binnen 14 dagen terug, ongebruikt en met label."}},
        {"type": "kaart", "settings": {"kleur": "zand", "ill": "zon", "titel": "Gemaakt om mee te gaan", "tekst": "Sterke stiksels en zware stof. Voor jaren aan surftrips, niet voor één zomer."}}]}]})

print('klaar')

