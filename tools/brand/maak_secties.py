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


def zonder_lege_defaults(schema):
    """Shopify weigert een sectie met een lege standaardwaarde (default: ''), dus die laten we weg."""
    for lijst in [schema.get('settings', [])] + [b.get('settings', []) for b in schema.get('blocks', [])]:
        for st in lijst:
            if st.get('default') == '':
                del st['default']
    return schema


#: secties die op de productpagina alleen bij bepaalde producttypes horen
NIET_TOONBAAR = {'tt-koop', 'tt-hero', 'tt-collectie', 'tt-collecties', 'tt-contact', 'tt-tekst', 'tt-maattabel'}
TOON_OPTIES = [{"value": v, "label": l} for v, l in [
    ("alle", "Altijd"), ("draagtas", "Alleen draagtassen"), ("kleding", "Alleen kleding"),
    ("accessoires", "Alleen accessoires"), ("surfgear", "Alleen surfgear"), ("anders", "Alles behalve draagtassen")]]
TOON_SETTING = {"type": "select", "id": "toon", "label": "Tonen op de productpagina bij", "options": TOON_OPTIES, "default": "alle",
                "info": "Alleen op productpagina's. Elders staat de sectie er altijd."}
# Liquid: zet tt_zie op false als de sectie niet bij dit producttype hoort
TOON_LIQUID = """{%- assign tt_zie = true -%}
{%- if template.name == 'product' and product != blank -%}
  {%- capture tt_groep -%}{%- render 'tt-groep', type: product.type -%}{%- endcapture -%}
  {%- assign tt_groep = tt_groep | strip -%}
  {%- assign tt_toon = section.settings.toon | default: 'alle' -%}
  {%- if tt_toon == 'anders' -%}
    {%- if tt_groep == 'draagtas' -%}{%- assign tt_zie = false -%}{%- endif -%}
  {%- elsif tt_toon != 'alle' and tt_toon != tt_groep -%}
    {%- assign tt_zie = false -%}
  {%- endif -%}
{%- endif -%}
"""


def schrijf(naam, body, schema):
    schema = zonder_lege_defaults(schema)
    if naam not in NIET_TOONBAAR:
        schema.setdefault('settings', []).append(TOON_SETTING)
        body = TOON_LIQUID + "{%- if tt_zie -%}\n" + body.strip() + "\n{%- endif -%}"
    for x in [schema] + schema.get('blocks', []) + schema.get('presets', []):
        assert len(x.get('name', '')) <= 25, f"naam te lang voor Shopify: {x.get('name')}"
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
s, fb = beeld('', 'Foto', 'tt-foto-hero', 'tide-tode-hero.jpg', 'Avondlicht op een leeg strand')
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
      <span><strong>{{ p.title }}</strong><span>{{ v.price | money_without_trailing_zeros }}</span></span>
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

# ---------- KOPEN: galerij + koopblok (homepage en productpagina, voor elk producttype) ----------
s1, fb1 = beeld('', 'Productfoto 1 (zolang het product geen foto\'s heeft)', 'tt-product-1', 'tide-tode-draagtas-1.jpg', 'De Tide-Tode draagtas met board')
s2, fb2 = beeld('b2_', 'Productfoto 2', 'tt-product-2', 'tide-tode-draagtas-2.jpg', 'De tegelstof van de draagtas van dichtbij')
TOON_BLOK = {"type": "select", "id": "toon", "label": "Tonen bij", "options": TOON_OPTIES, "default": "alle"}
# Liquid: zie = of dit blok bij de productgroep hoort
BLOK_ZIE = """{%- assign b_toon = block.settings.toon | default: 'alle' -%}{%- assign zie = false -%}{%- if b_toon == 'alle' or b_toon == groep -%}{%- assign zie = true -%}{%- elsif b_toon == 'anders' and groep != 'draagtas' -%}{%- assign zie = true -%}{%- endif -%}"""
DIA = """<figure class="tt-koop__foto tt-onthul" data-tt-dia{% if m %} data-media-id="{{ m.id }}"{% endif %}>
            <button type="button" class="tt-koop__zoom" data-tt-zoom aria-label="Foto {{ forloop.index }} groot bekijken">"""
schrijf('tt-koop', PRIJS + """
{%- liquid
  assign pdp = false
  if template.name == 'product' and product != blank and section.settings.product == blank
    assign pdp = true
  endif
  assign groep = 'draagtas'
  if p != blank
    capture groep
      render 'tt-groep', type: p.type
    endcapture
    assign groep = groep | strip
  endif
  assign media = p.media | where: 'media_type', 'image'
  assign max = 4
  if pdp
    assign max = 12
  endif
  assign aantal = media.size | default: 0
  if aantal > max
    assign aantal = max
  endif
  assign tekening = false
  if aantal == 0 and groep == 'draagtas'
    assign tekening = true
    assign aantal = 2
    if section.settings.extra_beelden
      assign aantal = 7
    endif
  endif
  assign leeg = false
  if aantal == 0
    assign leeg = true
    assign aantal = 1
  endif
-%}
<section class="tt tt-koop tt-bg--{{ section.settings.bg }} tt-koop--{{ groep }}" id="tt-koop-{{ section.id }}" data-tt-koop>
  <div class="tt-wrap tt-koop__grid">
    <div class="tt-koop__media">
      <div class="tt-koop__galerij tt-koop__galerij--{{ aantal | at_most: 4 }}" data-tt-galerij aria-label="Foto's" tabindex="-1">
        {%- if tekening -%}
          {%- for n in (1..aantal) -%}
            {%- assign m = nil -%}
            """ + DIA + """
              {%- case n -%}
                {%- when 1 -%}""" + B('', fb1, ", sizes: '(min-width: 990px) 55vw, 88vw', loading: 'eager'") + """
                {%- when 2 -%}""" + B('b2_', fb2, ", sizes: '(min-width: 990px) 28vw, 88vw'") + """
                {%- else -%}
                  {%- assign naam = 'tt-product-' | append: n -%}
                  {%- case n -%}
                    {%- when 3 -%}{%- assign alt_n = 'Het tegelvak van de draagtas om het midden van het board' -%}
                    {%- when 4 -%}{%- assign alt_n = 'De dusty blue schouderband van de draagtas' -%}
                    {%- when 5 -%}{%- assign alt_n = 'Tekening van de draagtas met genummerde onderdelen' -%}
                    {%- when 6 -%}{%- assign alt_n = 'De draagtas als sticker op een zwart-witfoto van de zee' -%}
                    {%- else -%}{%- assign alt_n = 'De kleuren van de tegelstof: terracotta, dusty blue, roest, crème en navy' -%}
                  {%- endcase -%}
                  {%- render 'tt-beeld', fallback: naam, alt: alt_n, sizes: '(min-width: 990px) 28vw, 88vw' -%}
              {%- endcase -%}
            </button>
          </figure>
          {%- endfor -%}
        {%- elsif leeg -%}
          <figure class="tt-koop__foto tt-koop__foto--leeg" data-tt-dia>
            <span class="tt-beeld__leeg" role="img" aria-label="{{ p.title | default: shop.name | escape }}">{%- render 'tt-logo', variant: 'maan-simpel' -%}</span>
            <figcaption>Foto volgt</figcaption>
          </figure>
        {%- else -%}
          {%- for m in media limit: max -%}
            {%- liquid
              assign alt_m = m.alt | default: p.title | escape
              assign laad = 'lazy'
              if forloop.first
                assign laad = 'eager'
              endif
              assign maten = '(min-width: 990px) 28vw, 88vw'
              if forloop.first
                assign maten = '(min-width: 990px) 55vw, 88vw'
              endif
              assign groot = m.preview_image | image_url: width: 2000
            -%}
            """ + DIA + """
              {%- if forloop.first and pdp -%}
                {{ m.preview_image | image_url: width: 1800 | image_tag: loading: laad, fetchpriority: 'high', sizes: maten, widths: '600, 900, 1200, 1800', alt: alt_m, class: 'tt-beeld__img tt-koop__eerste', data-groot: groot }}
              {%- else -%}
                {{ m.preview_image | image_url: width: 1800 | image_tag: loading: laad, sizes: maten, widths: '600, 900, 1200, 1800', alt: alt_m, class: 'tt-beeld__img', data-groot: groot }}
              {%- endif -%}
            </button>
          </figure>
          {%- endfor -%}
        {%- endif -%}
      </div>
      {%- if section.settings.stickers and groep == 'draagtas' -%}<div class="tt-stickers tt-stickers--koop" aria-hidden="true">{% render 'tt-stk', naam: 'draagtas' %}</div>{%- endif -%}
      {%- if aantal > 1 -%}
        <div class="tt-koop__voortgang" aria-hidden="true"><span data-tt-voortgang></span></div>
        <p class="tt-koop__teller" aria-hidden="true"><span data-tt-teller>1</span> / {{ aantal }}</p>
        {%- unless tekening -%}
          <ol class="tt-koop__duimen" aria-label="Kies een foto">
            {%- for m in media limit: max -%}
              <li><button type="button" data-tt-duim aria-current="{% if forloop.first %}true{% else %}false{% endif %}" aria-label="Foto {{ forloop.index }}">{{ m.preview_image | image_url: width: 160 | image_tag: loading: 'lazy', alt: '', sizes: '80px', widths: '80, 160' }}</button></li>
            {%- endfor -%}
          </ol>
        {%- endunless -%}
      {%- endif -%}
    </div>
    <div class="tt-koop__info">
      <div class="tt-koop__plak">
        {%- if p.type != blank -%}<p class="tt-koop__label tt-in">{{ p.type }}</p>{%- elsif section.settings.label != blank -%}<p class="tt-koop__label tt-in">{{ section.settings.label }}</p>{%- endif -%}
        {%- if pdp -%}
          {%- assign titel_kop = p.title | escape -%}
          {%- render 'tt-kop', text: titel_kop, tag: 'h1', class: 'tt-kop--m' -%}
        {%- else -%}
          {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
        {%- endif -%}
        <p class="tt-koop__prijs tt-in">
          {%- if p != blank and v != blank -%}
            <span data-tt-prijs-nu>{{ v.price | money_without_trailing_zeros }}</span>
            <s data-tt-prijs-was{% unless v.compare_at_price > v.price %} hidden{% endunless %}>{{ v.compare_at_price | money_without_trailing_zeros }}</s>
            <small>Inclusief btw</small>
          {%- else -%}<span>{{ section.settings.prijs_tekst }}</span>{%- endif -%}
        </p>
        {%- if pdp and p.description != blank -%}
          {%- assign pitch = p.description | split: '</p>' | first | strip_html | strip -%}
          {%- if pitch != blank -%}<p class="tt-koop__pitch tt-in">{{ pitch }}</p>{%- endif -%}
        {%- elsif section.settings.text != blank -%}
          <p class="tt-koop__pitch tt-in">{{ section.settings.text }}</p>
        {%- endif -%}
        {%- for block in section.blocks -%}{%- if block.type == '@app' -%}<div class="tt-koop__app">{% render block %}</div>{%- endif -%}{%- endfor -%}
        {%- capture punten -%}
          {%- for block in section.blocks -%}{%- if block.type == 'punt' -%}""" + BLOK_ZIE + """{%- if zie -%}<li {{ block.shopify_attributes }}><span class="tt-koop__vinkje" aria-hidden="true"></span>{{ block.settings.tekst }}</li>{%- endif -%}{%- endif -%}{%- endfor -%}
        {%- endcapture -%}
        {%- if punten != blank -%}<ul class="tt-koop__punten tt-in">{{ punten }}</ul>{%- endif -%}
        <div class="tt-koop__form tt-in">
          {%- if p != blank and v != blank -%}
            {%- form 'product', p, class: 'tt-koop__formulier', data-tt-form: '', novalidate: 'novalidate' -%}
              {%- unless p.has_only_default_variant -%}
                {%- for option in p.options_with_values -%}
                  {%- assign on = option.name | downcase -%}
                  <fieldset class="tt-koop__optie{% if on == 'maat' or on == 'size' %} tt-koop__optie--maat{% endif %}">
                    <legend><span>{{ option.name }}</span> <span class="tt-koop__gekozen" data-tt-gekozen>{{ option.selected_value }}</span>
                      {%- if on == 'maat' or on == 'size' -%}
                        {%- if section.settings.maatwijzer != blank -%}<a class="tt-koop__maatlink" href="{{ section.settings.maatwijzer }}">{{ section.settings.maatwijzer_label }}</a>{%- endif -%}
                      {%- endif -%}
                    </legend>
                    <div class="tt-koop__pillen">
                      {%- for value in option.values -%}
                        <label><input type="radio" name="tt-optie-{{ section.id }}-{{ forloop.parentloop.index }}" value="{{ value | escape }}"{% if option.selected_value == value %} checked{% endif %}><span>{{ value }}</span></label>
                      {%- endfor -%}
                    </div>
                  </fieldset>
                {%- endfor -%}
                <script type="application/json" data-tt-varianten>{{ p.variants | json }}</script>
              {%- endunless -%}
              <input type="hidden" name="id" value="{{ v.id }}" data-tt-variant>
              <div class="tt-koop__rij">
                {%- if section.settings.aantal -%}
                  <div class="tt-koop__aantal">
                    <button type="button" data-tt-aantal="-1" aria-label="Eén minder">−</button>
                    <label class="visually-hidden" for="tt-aantal-{{ section.id }}">Aantal</label>
                    <input id="tt-aantal-{{ section.id }}" type="number" name="quantity" value="1" min="1" inputmode="numeric">
                    <button type="button" data-tt-aantal="1" aria-label="Eén meer">+</button>
                  </div>
                {%- endif -%}
                <button type="submit" class="tt-knop tt-knop--vol tt-koop__knop"{% unless v.available %} disabled{% endunless %} data-tt-koopknop>
                  <span class="tt-koop__knoptekst" data-tt-knoptekst>{% if v.available %}In winkelwagen{% else %}Uitverkocht{% endif %}</span>
                  <span class="tt-koop__laden" aria-hidden="true"><i></i><i></i><i></i></span>
                  <svg class="tt-koop__vink" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>
                </button>
              </div>
              <p class="tt-koop__fout" role="alert" data-tt-fout hidden></p>
              {%- if section.settings.snel_betalen -%}<div class="tt-koop__snel">{{ form | payment_button }}</div>{%- endif -%}
            {%- endform -%}
          {%- else -%}
            <a class="tt-knop tt-knop--vol" href="{{ routes.all_products_collection_url }}"><span>Bekijk de shop</span></a>
          {%- endif -%}
        </div>
        {%- if p != blank and v.available and section.settings.voorraad != blank -%}<p class="tt-koop__voorraad tt-in"><span class="tt-koop__stip" aria-hidden="true"></span>{{ section.settings.voorraad }}</p>{%- endif -%}
        <ul class="tt-koop__vertrouwen tt-in">
          {%- if section.settings.v1 != blank -%}<li>{% render 'tt-icoon', icoon: 'voeten' %}<span>{{ section.settings.v1 }}</span></li>{%- endif -%}
          {%- if section.settings.v2 != blank -%}<li>{% render 'tt-icoon', icoon: 'tij' %}<span>{{ section.settings.v2 }}</span></li>{%- endif -%}
          {%- if section.settings.v3 != blank -%}<li>{% render 'tt-icoon', icoon: 'schelp' %}<span>{{ section.settings.v3 }}</span></li>{%- endif -%}
        </ul>
        {%- if section.settings.betaal_iconen and shop.enabled_payment_types.size > 0 -%}
          <ul class="tt-koop__betaal tt-in" aria-label="Betaalmethoden">{%- for type in shop.enabled_payment_types -%}<li>{{ type | payment_type_svg_tag }}</li>{%- endfor -%}</ul>
        {%- endif -%}
        <div class="tt-koop__details tt-in">
          {%- if pdp and p.description != blank -%}
            {%- comment -%} de eerste alinea staat al bovenaan als pitch {%- endcomment -%}
            {%- assign eerste = p.description | split: '</p>' | first | append: '</p>' -%}
            {%- assign rest = p.description | remove_first: eerste | strip -%}
            {%- if rest != blank -%}
              <details open><summary>{{ section.settings.beschrijving_titel }}<i aria-hidden="true"></i></summary><div class="tt-koop__beschrijving">{{ rest }}</div></details>
            {%- endif -%}
          {%- endif -%}
          {%- for block in section.blocks -%}{%- if block.type == 'detail' -%}""" + BLOK_ZIE + """{%- if zie -%}
            <details {{ block.shopify_attributes }}><summary>{{ block.settings.titel }}<i aria-hidden="true"></i></summary><div>{{ block.settings.tekst }}</div></details>
          {%- endif -%}{%- endif -%}{%- endfor -%}
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
  {%- if p != blank and v != blank -%}
    <div class="tt-balk" data-tt-balk aria-hidden="true">
      {%- if p.featured_media -%}<span class="tt-balk__beeld">{{ p.featured_media | image_url: width: 120 | image_tag: loading: 'lazy', alt: '' }}</span>{%- endif -%}
      <span class="tt-balk__naam">{{ p.title }}<span>{{ v.price | money_without_trailing_zeros }}</span></span>
      <button type="button" class="tt-knop" tabindex="-1" data-tt-balkknop{% unless v.available %} disabled{% endunless %}>In winkelwagen</button>
    </div>
  {%- endif -%}
</section>
""", {
    "name": "TT: kopen", "tag": "div", "max_blocks": 16,
    "settings": [
        bg("creme"),
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = op de productpagina het product van die pagina, elders het product uit Thema-instellingen > Tide-Tode."},
        {"type": "text", "id": "label", "label": "Klein label boven de kop", "default": "Draagtas"},
        kop("De Tide Tode draagtas"),
        {"type": "textarea", "id": "text", "label": "Korte pitch", "default": "Een draagtas voor je surfboard. Je schuift je board erin en hangt de tas over je schouder. Zo heb je je handen vrij en blijft de wax van je arm af."},
        {"type": "text", "id": "prijs_tekst", "label": "Tekst zonder product", "default": "Binnenkort"},
        {"type": "checkbox", "id": "stickers", "label": "Sticker bij de foto's", "default": True},
        {"type": "checkbox", "id": "aantal", "label": "Aantal kiezen", "default": True},
        {"type": "checkbox", "id": "snel_betalen", "label": "Snelle betaalknoppen tonen (Shop Pay, Apple Pay, enz.)", "default": False},
        {"type": "text", "id": "voorraad", "label": "Voorraadregel (als hij op voorraad is)", "default": "Op voorraad, binnen 2 werkdagen verstuurd"},
        {"type": "checkbox", "id": "betaal_iconen", "label": "Betaalmethoden tonen onder de knop", "default": True},
        {"type": "text", "id": "beschrijving_titel", "label": "Titel van de productomschrijving", "default": "Over dit product"},
        {"type": "header", "content": "Maatwijzer bij kleding"},
        {"type": "text", "id": "maatwijzer_label", "label": "Link bij de maten", "default": "Maatwijzer"},
        {"type": "text", "id": "maatwijzer", "label": "Adres maatwijzer", "default": "/pages/maatwijzer"},
        {"type": "checkbox", "id": "extra_beelden", "label": "Getekende productbeelden tonen zolang de draagtas geen foto's heeft", "default": True},
        {"type": "header", "content": "Vertrouwen onder de knop"},
        {"type": "text", "id": "v1", "label": "Regel 1", "default": "Verzending door heel Europa"},
        {"type": "text", "id": "v2", "label": "Regel 2", "default": "14 dagen bedenktijd"},
        {"type": "text", "id": "v3", "label": "Regel 3", "default": "Veilig betalen met iDEAL en kaart"},
    ] + s1 + s2,
    "blocks": [
        {"type": "punt", "name": "Voordeel", "settings": [{"type": "text", "id": "tekst", "label": "Tekst", "default": "Handen vrij"}, TOON_BLOK]},
        {"type": "@app"},
        {"type": "detail", "name": "Uitklapper", "settings": [{"type": "text", "id": "titel", "label": "Titel", "default": "Materiaal"}, {"type": "richtext", "id": "tekst", "label": "Tekst", "default": "<p>Tekst</p>"}, TOON_BLOK]},
    ],
    "presets": [{"name": "TT: kopen", "blocks": [
        {"type": "punt", "settings": {"tekst": "Past op softtops en vollere boards én op hardboards", "toon": "draagtas"}},
        {"type": "punt", "settings": {"tekst": "Brede schouderband, je handen blijven vrij", "toon": "draagtas"}},
        {"type": "punt", "settings": {"tekst": "Je natte board mag er gewoon in", "toon": "draagtas"}},
        {"type": "detail", "settings": {"titel": "Wat past erin", "tekst": "<p>Eén maat voor softtops en hardboards. In de <a href=\"/pages/maatwijzer\">maatwijzer</a> zie je welke boards passen.</p>", "toon": "draagtas"}},
        {"type": "detail", "settings": {"titel": "Materiaal", "tekst": "<p>Zware, waterbestendige stof en sterke stiksels.</p>", "toon": "draagtas"}},
        {"type": "detail", "settings": {"titel": "Verzending en retour", "tekst": "<p>We versturen door heel Europa. Je hebt 14 dagen bedenktijd.</p>"}}]}]})

# ---------- PROBLEEM: tekst die volloopt, met losse foto's ----------
s1, fb1 = beeld('', 'Foto links', 'tt-foto-probleem-1', 'tide-tode-sjouwen.jpg', 'Zandpad door de duinen naar het strand')
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
        {"type": "stap", "settings": {"ill": "busje", "titel": "Op naar de spot", "tekst": "Lopend door de duinen, op de fiets of achterop de scooter. Op het strand haal je hem er zo weer uit.", "fallback": "tt-foto-stap-3", "filename": "tide-tode-stap-3.jpg", "alt": "De negen ontwerpen van de draagtas"}}]}]})

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
        {"type": "kaart", "settings": {"titel": "Als je leert surfen", "tekst": "Een grote softtop, een lange wandeling van hostel of hotel naar het strand. Met de tas loop je ontspannen en heb je je handen vrij.", "knop": "Bekijk de draagtas", "fallback": "tt-foto-beginner", "filename": "tide-tode-beginner.jpg", "alt": "Surfer houdt een board met de Tide-Tode draagtas vast bij de zee"}},
        {"type": "kaart", "settings": {"titel": "Als je de rustige spots opzoekt", "tekst": "Door de bush, over rotsen, achterop de scooter. Je board hangt over je schouder, zodat je je handen vrij hebt om te klimmen.", "knop": "Bekijk de draagtas", "fallback": "tt-foto-avontuur", "filename": "tide-tode-avontuur.jpg", "alt": "Board met de Tide-Tode draagtas tegen een busje in de duinen"}}]}]})

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
      {%- if section.settings.link2_label != blank -%}<a class="tt-link" href="{{ section.settings.link2_url | default: routes.all_products_collection_url }}">{{ section.settings.link2_label }}</a>{%- endif -%}
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
        {"type": "text", "id": "link2_label", "label": "Tweede link", "default": "Of bekijk de hele shop"},
        {"type": "text", "id": "link2_url", "label": "Tweede link (adres)", "default": "/collections/all"},
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
          <path class="tt-check__paneel" d=""/>
          <path class="tt-check__schouder" d=""/>
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
        {%- if section.settings.btn_label != blank -%}<a class="tt-link" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif settings.tt_product != blank %}{{ settings.tt_product.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}</a>{%- endif -%}
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
        {"type": "text", "id": "btn_label", "label": "Link onder de check", "default": "Welke wax past bij dit water"},
        {"type": "text", "id": "btn_link", "label": "Link (adres)", "default": "/collections/surfgear"},
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
        {"type": "rij", "settings": {"punt": "Makkelijk over je schouder", "wij": "ja", "arm": "nee", "banden": "nee", "hoes": "nee"}},
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
    "settings": [{"type": "paragraph", "content": "Bezoekers zien deze sectie pas als er minstens één foto in staat."}, bg("creme"), kop("Details"),
                 {"type": "textarea", "id": "text", "label": "Tekst", "default": "De stof, de stiksels en de schouderband van dichtbij."}],
    "blocks": [{"type": "detail", "name": "Detail", "settings": [
        {"type": "image_picker", "id": "image", "label": "Foto (close-up, vierkant)"},
        {"type": "text", "id": "filename", "label": "Bestandsnaam", "info": "Of upload in Content > Bestanden met precies deze naam."},
        {"type": "text", "id": "titel", "label": "Titel", "default": "Detail"},
        {"type": "text", "id": "tekst", "label": "Tekst"}]}],
    "presets": [{"name": "TT: details van de tas", "blocks": [
        {"type": "detail", "settings": {"titel": "Zware stof", "tekst": "Waterbestendig en gemaakt voor nat, zand en zout.", "filename": "tide-tode-detail-stof.jpg"}},
        {"type": "detail", "settings": {"titel": "Sterke stiksels", "tekst": "Stevig gestikt op de plekken waar de tas het zwaarst draagt.", "filename": "tide-tode-detail-stiksels.jpg"}},
        {"type": "detail", "settings": {"titel": "De schouderband", "tekst": "Breed, zodat hij niet in je schouder snijdt.", "filename": "tide-tode-detail-schouderband.jpg"}},
        {"type": "detail", "settings": {"titel": "De tegelprint", "tekst": "Geweven in terracotta, dusty blue, roest en crème.", "filename": "tide-tode-detail-print.jpg"}}]}]})

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
        {"type": "foto", "settings": {"fallback": "tt-foto-stap-3", "alt": "Alle negen draagtassen naast elkaar"}},
        {"type": "tekst", "settings": {"titel": "De Draagtas", "regels": "Zware stof\nBrede schouderband\nSofttop en hardboard", "link_label": "Bekijk de draagtas"}},
        {"type": "foto", "settings": {"fallback": "tt-foto-beginner", "alt": "Board in de Tide-Tode draagtas bij de zee"}},
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
    <div class="tt-knoppen tt-patroon__knoppen">
    {%- if section.settings.btn_label != blank -%}<a class="tt-knop tt-knop--licht" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}<span aria-hidden="true">→</span></a>{%- endif -%}
    {%- if section.settings.link2_label != blank -%}<a class="tt-link" href="{{ section.settings.link2_url | default: routes.all_products_collection_url }}">{{ section.settings.link2_label }}</a>{%- endif -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: patroon", "tag": "div",
    "settings": [
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        {"type": "text", "id": "hand", "label": "Handgeschreven regel", "default": ""},
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Bestel de draagtas"},
        {"type": "url", "id": "btn_link", "label": "Knop-link"},
        {"type": "text", "id": "link2_label", "label": "Tweede link", "default": "Of bekijk de hele shop"},
        {"type": "text", "id": "link2_url", "label": "Tweede link (adres)", "default": "/collections/all"},
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
        {"type": "text", "id": "hand", "label": "Handgeschreven regel", "default": ""},
        kop("Productinformatie"),
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
        {"type": "spec", "settings": {"label": "Print", "waarde": "Tegels in terracotta, dusty blue, roest en crème"}},
        {"type": "spec", "settings": {"label": "Dragen", "waarde": "Over je schouder of schuin over je rug"}},
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
          {%- if block.settings.link_label != blank -%}<a class="tt-link tt-kaarten__link" href="{{ block.settings.link | default: routes.all_products_collection_url }}">{{ block.settings.link_label }}</a>{%- endif -%}
        </article>
      {%- endfor -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: drie kaarten", "tag": "div", "max_blocks": 4,
    "settings": [bg("creme"), kop("Service")],
    "blocks": [{"type": "kaart", "name": "Kaart", "settings": [
        {"type": "select", "id": "kleur", "label": "Kleur", "options": [{"value": v, "label": l} for v, l in [("baby", "Baby"), ("rose", "Rose"), ("zand", "Zand"), ("papier", "Papier")]], "default": "baby"},
        {"type": "select", "id": "ill", "label": "Tekening", "options": [{"value": v, "label": l} for v, l in [("busje", "Busje"), ("golf", "Golf"), ("zon", "Zon"), ("parasol", "Parasol"), ("draagtas", "De draagtas"), ("tas", "Board met banden")]], "default": "busje"},
        {"type": "text", "id": "titel", "label": "Titel", "default": "Titel"},
        {"type": "textarea", "id": "tekst", "label": "Tekst", "default": ""},
        {"type": "text", "id": "link_label", "label": "Link"},
        {"type": "text", "id": "link", "label": "Link (adres)"}]}],
    "presets": [{"name": "TT: drie kaarten", "blocks": [
        {"type": "kaart", "settings": {"kleur": "baby", "ill": "busje", "titel": "Verzending", "tekst": "We versturen door heel Europa. Je krijgt een track and trace zodra hij onderweg is."}},
        {"type": "kaart", "settings": {"kleur": "rose", "ill": "golf", "titel": "14 dagen bedenktijd", "tekst": "Past hij toch niet bij je board? Stuur hem binnen 14 dagen terug, ongebruikt en met label."}},
        {"type": "kaart", "settings": {"kleur": "zand", "ill": "zon", "titel": "Garantie", "tekst": "Gaat er iets stuk door een fout in de stof of de stiksels? Dan repareren of vervangen we hem."}}]}]})

# ---------- CONTACT: formulier, zo bereik je ons, en de gegevens ----------
GEGEVENS = """
      <dl class="tt-gegevens">
        {%- if settings.tt_email != blank -%}<div><dt>E-mail</dt><dd><a href="mailto:{{ settings.tt_email }}">{{ settings.tt_email }}</a></dd></div>{%- endif -%}
        {%- if settings.tt_telefoon != blank -%}<div><dt>Telefoon</dt><dd><a href="tel:{{ settings.tt_telefoon | remove: ' ' }}">{{ settings.tt_telefoon }}</a></dd></div>{%- endif -%}
        {%- if settings.tt_adres != blank -%}<div><dt>Adres</dt><dd>{{ settings.tt_bedrijf }}<br>{{ settings.tt_adres | newline_to_br }}</dd></div>{%- endif -%}
        {%- if settings.tt_kvk != blank -%}<div><dt>KvK</dt><dd>{{ settings.tt_kvk }}</dd></div>{%- endif -%}
        {%- if settings.tt_btw != blank -%}<div><dt>Btw</dt><dd>{{ settings.tt_btw }}</dd></div>{%- endif -%}
      </dl>"""

schrijf('tt-contact', """
{%- assign form_id = 'tt-contact-' | append: section.id -%}
<section class="tt tt-contact tt-bg--{{ section.settings.bg }}{% unless section.settings.gegevens %} tt-contact--smal{% endunless %}" id="contact">
  <div class="tt-wrap">
    <header class="tt-contact__kop">
      {%- if section.settings.label != blank -%}<p class="tt-col__label tt-in">{{ section.settings.label }}</p>{%- endif -%}
      {%- if section.settings.h1 -%}
        {%- assign titel = section.settings.heading | default: page.title -%}
        {%- render 'tt-kop', text: titel, tag: 'h1', class: 'tt-kop--l' -%}
      {%- else -%}
        {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- endif -%}
      {%- if section.settings.text != blank -%}<p class="tt-contact__intro tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </header>
    <div class="tt-contact__grid">
      <div class="tt-contact__formkaart tt-in">
        {%- form 'contact', id: form_id, class: 'tt-form' -%}
          {%- if form.posted_successfully? -%}
            <div class="tt-form__ok" role="status" tabindex="-1" autofocus>
              <span class="tt-form__okicoon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span>
              <div>
                <p class="tt-form__oktitel">{{ section.settings.ok_titel }}</p>
                <p>{{ section.settings.ok }}</p>
              </div>
            </div>
          {%- else -%}
            {%- if form.errors -%}
              <div class="tt-form__fout" role="alert">
                <p class="tt-form__fouttitel">Dat ging niet goed</p>
                {{ form.errors | default_errors }}
              </div>
            {%- endif -%}
            <p class="tt-form__titel">{{ section.settings.form_titel }}</p>
            <input type="hidden" name="contact[Pagina]" value="{{ section.settings.bron | default: page.title | escape }}">
            <div class="tt-form__rij">
              <label class="tt-veld"><span>Naam</span><input type="text" name="contact[Naam]" autocomplete="name" value="{{ form.name }}" placeholder="Je naam" required></label>
              <label class="tt-veld"><span>E-mail</span><input type="email" name="contact[email]" autocomplete="email" spellcheck="false" autocapitalize="off" value="{{ form.email }}" placeholder="jij@voorbeeld.nl" required{% if form.errors contains 'email' %} aria-invalid="true"{% endif %}></label>
            </div>
            {%- if section.settings.extra -%}
            <div class="tt-form__rij">
              <label class="tt-veld"><span>Telefoon <em>niet verplicht</em></span><input type="tel" name="contact[Telefoon]" autocomplete="tel" value="{{ form.phone }}"></label>
              <label class="tt-veld"><span>Bestelnummer <em>niet verplicht</em></span><input type="text" name="contact[Bestelnummer]" placeholder="#1001"></label>
            </div>
            {%- endif -%}
            <label class="tt-veld"><span>{{ section.settings.bericht_label }}</span><textarea name="contact[Bericht]" rows="6" placeholder="{{ section.settings.bericht_hint | escape }}" required>{{ form.body }}</textarea></label>
            <div class="tt-form__onder">
              <button type="submit" class="tt-knop"><span>{{ section.settings.knop }}</span><span aria-hidden="true">→</span></button>
              {%- if settings.tt_reactietijd != blank -%}<p class="tt-form__tijd">{{ settings.tt_reactietijd }}</p>{%- endif -%}
            </div>
          {%- endif -%}
        {%- endform -%}
      </div>
      {%- if section.settings.gegevens -%}
      <aside class="tt-contact__zij">
        <ul class="tt-contact__wegen">
          {%- if settings.tt_email != blank -%}
            <li class="tt-in"><a class="tt-contact__weg" href="mailto:{{ settings.tt_email }}">
              <span class="tt-contact__wegicoon tt-contact__wegicoon--baby">{% render 'tt-icoon', icoon: 'meeuw' %}</span>
              <span><span class="tt-contact__weglabel">Mail ons</span><span class="tt-contact__wegwaarde">{{ settings.tt_email }}</span></span>
            </a></li>
          {%- endif -%}
          {%- if settings.tt_telefoon != blank -%}
            <li class="tt-in"><a class="tt-contact__weg" href="tel:{{ settings.tt_telefoon | remove: ' ' }}">
              <span class="tt-contact__wegicoon tt-contact__wegicoon--rose">{% render 'tt-icoon', icoon: 'schelp' %}</span>
              <span><span class="tt-contact__weglabel">Bel of app</span><span class="tt-contact__wegwaarde">{{ settings.tt_telefoon }}</span></span>
            </a></li>
          {%- endif -%}
          {%- if settings.social_instagram_link != blank -%}
            <li class="tt-in"><a class="tt-contact__weg" href="{{ settings.social_instagram_link }}" target="_blank" rel="noopener">
              <span class="tt-contact__wegicoon tt-contact__wegicoon--zand">{% render 'tt-icoon', icoon: 'zon' %}</span>
              <span><span class="tt-contact__weglabel">Stuur een DM</span><span class="tt-contact__wegwaarde">Instagram</span></span>
            </a></li>
          {%- endif -%}
        </ul>
        <div class="tt-contact__kaart tt-in">
          <div class="tt-contact__kaartkop">
            <p class="tt-contact__kaarttitel">{{ section.settings.kaart_titel }}</p>
            {%- if settings.tt_reactietijd != blank -%}<p class="tt-contact__tijd">{{ settings.tt_reactietijd }}</p>{%- endif -%}
          </div>""" + GEGEVENS + """
          <ul class="tt-contact__social">
            {%- if settings.social_tiktok_link != blank -%}<li><a href="{{ settings.social_tiktok_link }}" target="_blank" rel="noopener">TikTok</a></li>{%- endif -%}
            {%- if settings.social_pinterest_link != blank -%}<li><a href="{{ settings.social_pinterest_link }}" target="_blank" rel="noopener">Pinterest</a></li>{%- endif -%}
            {%- if settings.social_facebook_link != blank -%}<li><a href="{{ settings.social_facebook_link }}" target="_blank" rel="noopener">Facebook</a></li>{%- endif -%}
          </ul>
        </div>
        {%- if section.settings.ill != 'geen' -%}
          <figure class="tt-contact__ill tt-in tt-teken" aria-hidden="true">
            {%- render 'tt-ill', naam: section.settings.ill -%}
            {%- if section.settings.hand != blank -%}<figcaption>{{ section.settings.hand }}</figcaption>{%- endif -%}
          </figure>
        {%- endif -%}
      </aside>
      {%- endif -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: contact", "tag": "div",
    "settings": [
        bg("creme"),
        {"type": "text", "id": "label", "label": "Klein label boven de kop", "default": "Contact"},
        {"type": "checkbox", "id": "h1", "label": "Kop is de paginatitel (h1)", "default": True},
        {"type": "text", "id": "heading", "label": "Kop", "default": "Vraag het ons gewoon"},
        {"type": "textarea", "id": "text", "label": "Intro", "default": "Vraag over je bestelling, je board of de tas? Stuur ons een bericht. Je krijgt antwoord van ons zelf."},
        {"type": "text", "id": "form_titel", "label": "Titel boven het formulier", "default": "Stuur een bericht"},
        {"type": "text", "id": "bericht_label", "label": "Label berichtveld", "default": "Bericht"},
        {"type": "text", "id": "bericht_hint", "label": "Voorbeeldtekst in het berichtveld", "default": "Waar kunnen we je mee helpen?"},
        {"type": "checkbox", "id": "extra", "label": "Telefoon en bestelnummer vragen", "default": True},
        {"type": "text", "id": "knop", "label": "Knop", "default": "Verstuur"},
        {"type": "text", "id": "ok_titel", "label": "Titel bevestiging", "default": "Bericht verstuurd"},
        {"type": "text", "id": "ok", "label": "Bevestiging", "default": "Bedankt, we reageren binnen één werkdag."},
        {"type": "text", "id": "bron", "label": "Bron in de e-mail (leeg = paginatitel)"},
        {"type": "checkbox", "id": "gegevens", "label": "Contactwegen en gegevens tonen", "default": True},
        {"type": "text", "id": "kaart_titel", "label": "Titel gegevenskaart", "default": "Gegevens"},
        {"type": "select", "id": "ill", "label": "Tekening", "options": [{"value": v, "label": l} for v, l in [("geen", "Geen"), ("parasol", "Parasol"), ("busje", "Busje"), ("golf", "Golf"), ("zon", "Zon"), ("draagtas", "De draagtas")]], "default": "busje"},
        {"type": "text", "id": "hand", "label": "Handgeschreven regel bij de tekening", "default": "Tot snel"},
    ],
    "presets": [{"name": "TT: contact"}]})

# ---------- TEKSTPAGINA: juridische pagina's en andere lange teksten ----------
schrijf('tt-tekst', """
{%- liquid
  assign inhoud = page.content | replace: '[EMAIL]', settings.tt_email | replace: '[TELEFOON]', settings.tt_telefoon | replace: '[KVK]', settings.tt_kvk | replace: '[BTW]', settings.tt_btw | replace: '[BEDRIJF]', settings.tt_bedrijf
  assign adres = settings.tt_adres | newline_to_br
  assign inhoud = inhoud | replace: '[ADRES]', adres
-%}
<section class="tt tt-tekst tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap tt-tekst__grid">
    <header class="tt-tekst__kop">
      {%- if section.settings.label != blank -%}<p class="tt-tekst__label">{{ section.settings.label }}</p>{%- endif -%}
      <h1 class="tt-kop tt-kop--l">{{ page.title }}</h1>
      {%- if section.settings.datum != blank -%}<p class="tt-tekst__datum">Laatst bijgewerkt op {{ section.settings.datum }}</p>{%- endif -%}
    </header>
    <div class="tt-tekst__inhoud rte">{{ inhoud }}</div>
    <aside class="tt-tekst__zij">
      <div class="tt-tekst__kaart">
        <p class="tt-tekst__kaarttitel">{{ settings.tt_bedrijf }}</p>""" + GEGEVENS + """
      </div>
      {%- if section.blocks.size > 0 -%}
      <nav class="tt-tekst__links" aria-label="Meer informatie">
        <p class="tt-tekst__kaarttitel">Meer informatie</p>
        <ul>{%- for block in section.blocks -%}<li {{ block.shopify_attributes }}><a href="{{ block.settings.link }}"{% if block.settings.link == request.path %} aria-current="page"{% endif %}>{{ block.settings.label }}</a></li>{%- endfor -%}</ul>
      </nav>
      {%- endif -%}
    </aside>
  </div>
</section>
""", {
    "name": "TT: tekstpagina", "tag": "div",
    "settings": [
        bg("papier"),
        {"type": "text", "id": "label", "label": "Label boven de titel", "default": ""},
        {"type": "text", "id": "datum", "label": "Laatst bijgewerkt", "default": "7 oktober 2026"},
        {"type": "paragraph", "content": "In de paginatekst worden [BEDRIJF], [EMAIL], [TELEFOON], [ADRES], [KVK] en [BTW] vervangen door de gegevens uit Thema-instellingen > Tide-Tode."},
    ],
    "blocks": [{"type": "link", "name": "Link", "settings": [
        {"type": "text", "id": "label", "label": "Tekst", "default": "Link"},
        {"type": "text", "id": "link", "label": "Adres", "default": "/pages/contact"}]}],
    "presets": [{"name": "TT: tekstpagina", "blocks": [
        {"type": "link", "settings": {"label": "Verzenden", "link": "/policies/shipping-policy"}},
        {"type": "link", "settings": {"label": "Retourneren", "link": "/policies/refund-policy"}},
        {"type": "link", "settings": {"label": "Herroepingsrecht", "link": "/pages/herroepingsrecht"}},
        {"type": "link", "settings": {"label": "Algemene voorwaarden", "link": "/policies/terms-of-service"}},
        {"type": "link", "settings": {"label": "Privacybeleid", "link": "/policies/privacy-policy"}},
        {"type": "link", "settings": {"label": "Veelgestelde vragen", "link": "/pages/veelgestelde-vragen"}},
        {"type": "link", "settings": {"label": "Contact", "link": "/pages/contact"}}]}]})

# ---------- MAATTABEL ----------
schrijf('tt-maattabel', """
{%- assign koppen = section.settings.kolommen | split: '|' -%}
<section class="tt tt-maat tt-bg--{{ section.settings.bg }}" id="{{ section.settings.anker | default: section.id }}">
  <div class="tt-wrap">
    <div class="tt-maat__kop">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
      {%- if section.settings.text != blank -%}<p>{{ section.settings.text }}</p>{%- endif -%}
    </div>
    <div class="tt-maat__wrap">
      <table class="tt-maat__tabel">
        <thead><tr>{%- for k in koppen -%}<th scope="col">{{ k }}</th>{%- endfor -%}</tr></thead>
        <tbody>
          {%- for block in section.blocks -%}
            {%- assign cellen = block.settings.cellen | split: '|' -%}
            <tr {{ block.shopify_attributes }}>{%- for c in cellen -%}{%- if forloop.first -%}<th scope="row">{{ c }}</th>{%- else -%}<td data-label="{{ koppen[forloop.index0] | escape }}">{{ c }}</td>{%- endif -%}{%- endfor -%}</tr>
          {%- endfor -%}
        </tbody>
      </table>
    </div>
    {%- if section.settings.noot != blank -%}<p class="tt-maat__noot">{{ section.settings.noot }}</p>{%- endif -%}
    {%- if section.settings.btn_label != blank -%}<a class="tt-knop tt-knop--vol" href="{{ section.settings.btn_link | default: routes.all_products_collection_url }}"><span>{{ section.settings.btn_label }}</span></a>{%- endif -%}
  </div>
</section>
""", {
    "name": "TT: maattabel", "tag": "div", "max_blocks": 12,
    "settings": [
        bg("creme"),
        {"type": "text", "id": "anker", "label": "Anker (voor links naar dit deel)", "default": "maten"},
        kop("Maten"),
        {"type": "textarea", "id": "text", "label": "Intro", "default": ""},
        {"type": "text", "id": "kolommen", "label": "Kolommen (gescheiden door |)", "default": "Maat|Borst|Lengte"},
        {"type": "textarea", "id": "noot", "label": "Noot onder de tabel"},
        {"type": "text", "id": "btn_label", "label": "Knop"},
        {"type": "text", "id": "btn_link", "label": "Knop-link"},
    ],
    "blocks": [{"type": "rij", "name": "Rij", "settings": [{"type": "text", "id": "cellen", "label": "Cellen (gescheiden door |)", "default": "M|54 cm|74 cm"}]}],
    "presets": [{"name": "TT: maattabel", "blocks": [
        {"type": "rij", "settings": {"cellen": "S|51 cm|71 cm"}}, {"type": "rij", "settings": {"cellen": "M|54 cm|74 cm"}},
        {"type": "rij", "settings": {"cellen": "L|57 cm|76 cm"}}, {"type": "rij", "settings": {"cellen": "XL|60 cm|78 cm"}}]}]})

# ---------- COLLECTIE: redactionele kop, collectieknoppen, filter, sorteren en productkaarten ----------
schrijf('tt-collectie', """
{%- liquid
  assign sorteer = collection.sort_by | default: collection.default_sort_by
  assign kop_blok = nil
  for block in section.blocks
    if block.settings.handle == collection.handle
      assign kop_blok = block
    endif
  endfor
  assign intro = collection.description
  if intro == blank and kop_blok != nil
    assign intro = kop_blok.settings.intro
  endif
  assign actief = 0
  for filter in collection.filters
    assign actief = actief | plus: filter.active_values.size
  endfor
  assign ill = 'golf'
  if kop_blok != nil and kop_blok.settings.ill != blank
    assign ill = kop_blok.settings.ill
  endif
-%}
<section class="tt tt-col tt-bg--{{ section.settings.bg }}">
  <header class="tt-wrap tt-col__held{% if section.settings.beeld %} tt-col__held--beeld{% endif %}">
    <div class="tt-col__tekst">
      <p class="tt-col__label tt-in">{{ section.settings.label }}</p>
      {%- assign titel = collection.title | escape -%}
      {%- render 'tt-kop', text: titel, tag: 'h1', class: 'tt-kop--l' -%}
      {%- if intro != blank -%}<div class="tt-col__intro tt-in">{{ intro }}</div>{%- endif -%}
    </div>
    {%- if section.settings.beeld -%}
      <div class="tt-col__beeld tt-onthul">
        {%- if collection.image -%}
          {{ collection.image | image_url: width: 1600 | image_tag: loading: 'eager', fetchpriority: 'high', sizes: '(min-width: 990px) 42vw, 100vw', widths: '600, 900, 1200, 1600', alt: collection.title, class: 'tt-beeld__img' }}
        {%- elsif kop_blok != nil and kop_blok.settings.fallback != blank -%}
          {%- render 'tt-beeld', fallback: kop_blok.settings.fallback, alt: collection.title, sizes: '(min-width: 990px) 42vw, 100vw', loading: 'eager' -%}
        {%- else -%}
          {%- render 'tt-beeld', fallback: section.settings.fallback, alt: collection.title, sizes: '(min-width: 990px) 42vw, 100vw', loading: 'eager' -%}
        {%- endif -%}
      </div>
    {%- endif -%}
  </header>
  <div class="tt-wrap">
    <div class="tt-col__balk">
      {%- if section.blocks.size > 0 -%}
        <nav class="tt-col__nav" aria-label="Collecties">
          {%- for block in section.blocks -%}
            {%- assign doel = routes.collections_url | append: '/' | append: block.settings.handle -%}
            <a href="{{ doel }}" {{ block.shopify_attributes }}{% if collection.handle == block.settings.handle %} aria-current="page"{% endif %}>{{ block.settings.label }}</a>
          {%- endfor -%}
        </nav>
      {%- endif -%}
      <div class="tt-col__acties">
        <p class="tt-col__aantal">{{ collection.products_count }} {% if collection.products_count == 1 %}product{% else %}producten{% endif %}</p>
        {%- if section.settings.filters and collection.filters.size > 0 -%}
          <details class="tt-col__filter">
            <summary>Filter{% if actief > 0 %} <span>{{ actief }}</span>{% endif %}</summary>
            <div class="tt-col__paneel">
              {%- for filter in collection.filters -%}
                {%- if filter.type == 'list' or filter.type == 'boolean' -%}
                  <div class="tt-col__groep">
                    <p class="tt-col__groepnaam">{{ filter.label }}</p>
                    <div class="tt-col__keuzes">
                      {%- for value in filter.values -%}
                        {%- if value.count > 0 or value.active -%}
                          <a class="tt-col__keuze{% if value.active %} is-aan{% endif %}" href="{% if value.active %}{{ value.url_to_remove }}{% else %}{{ value.url_to_add }}{% endif %}"{% if value.active %} aria-current="true"{% endif %}>{{ value.label }}<span>{{ value.count }}</span></a>
                        {%- endif -%}
                      {%- endfor -%}
                    </div>
                  </div>
                {%- endif -%}
              {%- endfor -%}
            </div>
          </details>
        {%- endif -%}
        {%- if collection.sort_options.size > 0 -%}
          <label class="tt-col__sort"><span class="visually-hidden">Sorteer</span>
            <select data-tt-sorteer aria-label="Sorteer">
              {%- for o in collection.sort_options -%}<option value="{{ o.value }}"{% if o.value == sorteer %} selected{% endif %}>{{ o.name }}</option>{%- endfor -%}
            </select>
          </label>
        {%- endif -%}
      </div>
    </div>
    {%- if actief > 0 -%}
      <div class="tt-col__actief">
        {%- for filter in collection.filters -%}{%- for value in filter.active_values -%}
          <a class="tt-col__chip" href="{{ value.url_to_remove }}">{{ value.label }}<span aria-hidden="true">×</span><span class="visually-hidden">Filter weghalen</span></a>
        {%- endfor -%}{%- endfor -%}
        <a class="tt-col__wis" href="{{ collection.url }}?sort_by={{ sorteer }}">Alles wissen</a>
      </div>
    {%- endif -%}
    {%- paginate collection.products by section.settings.per_pagina -%}
      <ul class="tt-col__grid">
        {%- for product in collection.products -%}
          <li class="tt-in">
            {%- if forloop.index < 5 -%}{%- render 'tt-productkaart', p: product, laden: 'eager' -%}{%- else -%}{%- render 'tt-productkaart', p: product -%}{%- endif -%}
          </li>
        {%- else -%}
          <li class="tt-col__leeg">
            <div class="tt-col__leegkaart tt-in tt-teken">
              <div class="tt-col__leegbeeld">{%- render 'tt-ill', naam: ill -%}</div>
              <div class="tt-col__leegtekst">
                {%- if actief > 0 -%}
                  <h2 class="tt-kop tt-kop--m">Niets gevonden</h2>
                  <p>Met deze filters staat er niets in de shop. Haal een filter weg of bekijk alles.</p>
                  <div class="tt-knoppen"><a class="tt-knop" href="{{ collection.url }}">Filters wissen<span aria-hidden="true">→</span></a></div>
                {%- else -%}
                  <h2 class="tt-kop tt-kop--m">{{ section.settings.leeg_kop }}</h2>
                  <p>{{ section.settings.leeg_tekst }}</p>
                  <div class="tt-knoppen">
                    <a class="tt-knop" href="{{ routes.collections_url }}">Alle collecties<span aria-hidden="true">→</span></a>
                    <a class="tt-link" href="{{ routes.root_url }}">Naar de homepage</a>
                  </div>
                {%- endif -%}
              </div>
            </div>
          </li>
        {%- endfor -%}
      </ul>
      {%- if paginate.pages > 1 -%}<nav class="tt-col__paginas" aria-label="Pagina's">{{ paginate | default_pagination: next: 'Volgende', previous: 'Vorige' }}</nav>{%- endif -%}
    {%- endpaginate -%}
  </div>
</section>
""", {
    "name": "TT: collectie", "tag": "div", "max_blocks": 8,
    "settings": [
        bg("creme"),
        {"type": "text", "id": "label", "label": "Klein label boven de titel", "default": "Collectie"},
        {"type": "checkbox", "id": "beeld", "label": "Sfeerfoto naast de titel", "default": True, "info": "De foto van de collectie, of anders de sfeerfoto van de collectieknop hieronder."},
        {"type": "text", "id": "fallback", "label": "Sfeerfoto als niets anders past (asset)", "default": "tt-foto-mood-2"},
        {"type": "checkbox", "id": "filters", "label": "Filters tonen", "default": True, "info": "Zet filters aan in de app Search & Discovery."},
        {"type": "range", "id": "per_pagina", "label": "Producten per pagina", "min": 8, "max": 48, "step": 4, "default": 24},
        {"type": "header", "content": "Lege collectie"},
        {"type": "text", "id": "leeg_kop", "label": "Kop", "default": "Binnenkort in de shop"},
        {"type": "textarea", "id": "leeg_tekst", "label": "Tekst", "default": "We maken de laatste foto's. Kijk zo nog even rond, of kom over een paar dagen terug."},
    ],
    "blocks": [{"type": "link", "name": "Collectieknop", "settings": [
        {"type": "text", "id": "label", "label": "Tekst", "default": "Alles"},
        {"type": "text", "id": "handle", "label": "Handle van de collectie", "default": "all"},
        {"type": "textarea", "id": "intro", "label": "Intro (als de collectie zelf geen tekst heeft)"},
        {"type": "text", "id": "fallback", "label": "Sfeerfoto (asset, zonder .jpg)", "info": "Wordt gebruikt zolang de collectie geen eigen foto heeft."},
        {"type": "select", "id": "ill", "label": "Tekening bij een lege collectie", "options": [{"value": v, "label": l} for v, l in [("draagtas", "De draagtas"), ("golf", "Golf"), ("busje", "Busje"), ("zon", "Zon"), ("parasol", "Parasol")]], "default": "golf"}]}],
    "presets": [{"name": "TT: collectie", "blocks": [
        {"type": "link", "settings": {"label": "Alles", "handle": "all", "fallback": "tt-foto-mood-2", "ill": "zon", "intro": "Draagtassen, kleding en de kleine dingen die je elke sessie meeneemt."}},
        {"type": "link", "settings": {"label": "Draagtassen", "handle": "draagtassen", "fallback": "tt-foto-lifestyle-busje", "ill": "draagtas", "intro": "Negen draagtassen voor je surfboard. Board erin, tas over je schouder en je handen zijn vrij."}},
        {"type": "link", "settings": {"label": "Surfgear", "handle": "surfgear", "fallback": "tt-meer-4", "ill": "golf", "intro": "Wax voor elk water, een waxkam, karabijnhaken en stickers voor je board."}},
        {"type": "link", "settings": {"label": "Kleding en accessoires", "handle": "kleding-en-accessoires", "fallback": "tt-meer-1", "ill": "busje", "intro": "Zware shirts met een verhaal op de rug, een hoodie voor na het surfen en alles voor op het strand."}}]}]})

# ---------- ALLE COLLECTIES ----------
schrijf('tt-collecties', """
<section class="tt tt-cols tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    <header class="tt-cols__kop">
      {%- if section.settings.label != blank -%}<p class="tt-col__label tt-in">{{ section.settings.label }}</p>{%- endif -%}
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h1', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </header>
    <ul class="tt-cols__grid">
      {%- for block in section.blocks -%}
        {%- assign c = collections[block.settings.handle] -%}
        {%- assign doel = routes.collections_url | append: '/' | append: block.settings.handle -%}
        <li class="tt-in" {{ block.shopify_attributes }}>
          <a class="tt-cols__tegel tt-cols__tegel--{{ block.settings.kleur }}" href="{{ doel }}">
            <span class="tt-cols__beeld">
              {%- if c.featured_image -%}{{ c.featured_image | image_url: width: 1000 | image_tag: loading: 'lazy', sizes: '(min-width: 750px) 33vw, 100vw', widths: '500, 750, 1000', alt: '' }}
              {%- elsif block.settings.fallback != blank -%}{%- render 'tt-beeld', fallback: block.settings.fallback, alt: '', sizes: '(min-width: 750px) 33vw, 100vw' -%}
              {%- elsif c.products.first.featured_media -%}{{ c.products.first.featured_media | image_url: width: 1000 | image_tag: loading: 'lazy', sizes: '(min-width: 750px) 33vw, 100vw', widths: '500, 750, 1000', alt: '' }}
              {%- else -%}<span class="tt-cols__ill">{%- render 'tt-ill', naam: block.settings.ill -%}</span>{%- endif -%}
            </span>
            <span class="tt-cols__onder">
              <span class="tt-cols__naam">{{ block.settings.label }}</span>
              <span class="tt-cols__aantal">{%- if c.products_count > 0 -%}{{ c.products_count }} producten{%- else -%}Binnenkort{%- endif -%}</span>
              <span class="tt-cols__pijl" aria-hidden="true">→</span>
            </span>
          </a>
        </li>
      {%- endfor -%}
    </ul>
  </div>
</section>
""", {
    "name": "TT: alle collecties", "tag": "div", "max_blocks": 6,
    "settings": [bg("creme"), {"type": "text", "id": "label", "label": "Klein label", "default": "Shop"}, {"type": "text", "id": "heading", "label": "Kop", "default": "Alles van Tide Tode"},
                 {"type": "textarea", "id": "text", "label": "Tekst", "default": "Kies een collectie. Alles is ontworpen door twee surfers, voor onderweg naar zee."}],
    "blocks": [{"type": "collectie", "name": "Collectie", "settings": [
        {"type": "text", "id": "label", "label": "Naam", "default": "Collectie"},
        {"type": "text", "id": "handle", "label": "Handle", "default": "all"},
        {"type": "select", "id": "kleur", "label": "Kleur", "options": [{"value": v, "label": l} for v, l in [("baby", "Baby"), ("rose", "Rose"), ("zand", "Zand")]], "default": "baby"},
        {"type": "text", "id": "fallback", "label": "Sfeerfoto (asset, zonder .jpg)", "info": "Zolang de collectie geen eigen foto heeft."},
        {"type": "select", "id": "ill", "label": "Tekening (als er nog geen foto is)", "options": [{"value": v, "label": l} for v, l in [("draagtas", "De draagtas"), ("golf", "Golf"), ("busje", "Busje"), ("zon", "Zon"), ("parasol", "Parasol")]], "default": "draagtas"}]}],
    "presets": [{"name": "TT: alle collecties", "blocks": [
        {"type": "collectie", "settings": {"label": "Draagtassen", "handle": "draagtassen", "kleur": "baby", "ill": "draagtas", "fallback": "tt-foto-lifestyle-busje"}},
        {"type": "collectie", "settings": {"label": "Surfgear", "handle": "surfgear", "kleur": "rose", "ill": "golf", "fallback": "tt-meer-4"}},
        {"type": "collectie", "settings": {"label": "Kleding en accessoires", "handle": "kleding-en-accessoires", "kleur": "zand", "ill": "busje", "fallback": "tt-meer-1"}}]}]})

# ---------- AANRADERS: misschien ook iets voor jou (Shopify-aanbevelingen) ----------
schrijf('tt-aanraders', """
{%- liquid
  assign n = section.settings.aantal
  assign bron = section.settings.collectie
  if bron == blank
    assign bron = collections.all
  endif
  assign url = ''
  if product != blank
    assign url = routes.product_recommendations_url | append: '?section_id=' | append: section.id | append: '&product_id=' | append: product.id | append: '&limit=' | append: n | append: '&intent=related'
  endif
  assign heeft = false
  if recommendations.performed? and recommendations.products_count > 0
    assign heeft = true
  endif
-%}
{%- capture kaarten -%}
  {%- if heeft -%}
    {%- for r in recommendations.products -%}<li class="tt-in">{%- render 'tt-productkaart', p: r -%}</li>{%- endfor -%}
  {%- else -%}
    {%- assign telt = 0 -%}
    {%- for r in bron.products -%}
      {%- if telt < n and r.handle != product.handle -%}
        {%- assign telt = telt | plus: 1 -%}
        <li class="tt-in">{%- render 'tt-productkaart', p: r -%}</li>
      {%- endif -%}
    {%- endfor -%}
  {%- endif -%}
{%- endcapture -%}
<section class="tt tt-aanraders tt-bg--{{ section.settings.bg }}" data-tt-aanraders{% if url != blank and heeft == false %} data-url="{{ url }}"{% endif %}{% if kaarten == blank %} hidden{% endif %}>
  <div class="tt-wrap">
    <div class="tt-aanraders__kop">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
      {%- if section.settings.link_label != blank -%}<a class="tt-link tt-in" href="{{ section.settings.link | default: routes.all_products_collection_url }}">{{ section.settings.link_label }}</a>{%- endif -%}
    </div>
    <ul class="tt-aanraders__rij" data-tt-aanraders-lijst>{{ kaarten }}</ul>
  </div>
</section>
""", {
    "name": "TT: aanraders", "tag": "div",
    "settings": [
        bg("papier"),
        kop("Misschien ook|iets voor jou"),
        {"type": "range", "id": "aantal", "label": "Aantal producten", "min": 2, "max": 8, "step": 1, "default": 4},
        {"type": "collection", "id": "collectie", "label": "Collectie als er nog geen aanbevelingen zijn", "info": "Leeg = alle producten."},
        {"type": "text", "id": "link_label", "label": "Link", "default": "Bekijk alles"},
        {"type": "text", "id": "link", "label": "Link (adres)", "default": "/collections/all"},
    ],
    "presets": [{"name": "TT: aanraders"}]})

# ---------- DUURZAAMHEID: wat we nu al doen, in een paar punten ----------
# Alleen keuzes die echt zo zijn. Geen keurmerken, percentages of CO2-cijfers.
schrijf('tt-duurzaam', """
<section class="tt tt-duurzaam tt-bg--{{ section.settings.bg }}" id="duurzaamheid">
  <div class="tt-wrap">
    <div class="tt-duurzaam__kop">
      <div>
        {%- if section.settings.label != blank -%}<p class="tt-duurzaam__label tt-in">{{ section.settings.label }}</p>{%- endif -%}
        {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      </div>
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </div>
    <ul class="tt-duurzaam__punten tt-duurzaam__punten--{{ section.blocks.size }}">
      {%- for block in section.blocks -%}
        <li class="tt-duurzaam__punt tt-in" style="--d: {{ forloop.index0 | modulo: 4 | times: 0.1 }}s" {{ block.shopify_attributes }}>
          <span class="tt-duurzaam__icoon tt-duurzaam__icoon--{{ block.settings.kleur }}">{% render 'tt-icoon', icoon: block.settings.icoon %}</span>
          <h3>{{ block.settings.titel }}</h3>
          <p>{{ block.settings.tekst }}</p>
        </li>
      {%- endfor -%}
    </ul>
    {%- if section.settings.noot != blank or section.settings.link_label != blank -%}
    <div class="tt-duurzaam__onder tt-in">
      {%- if section.settings.noot != blank -%}<p class="tt-duurzaam__noot">{{ section.settings.noot }}</p>{%- endif -%}
      {%- if section.settings.link_label != blank -%}<a class="tt-link" href="{{ section.settings.link | default: '/pages/duurzaamheid' }}">{{ section.settings.link_label }}</a>{%- endif -%}
    </div>
    {%- endif -%}
  </div>
</section>
""", {
    "name": "TT: duurzaamheid", "tag": "div", "max_blocks": 6,
    "settings": [
        bg("papier"),
        {"type": "text", "id": "label", "label": "Klein label boven de kop", "default": "Duurzaamheid"},
        kop("Gemaakt om|*lang* mee te gaan"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "We zijn een klein en jong merk. Grote beloftes doen we niet. Dit doen we wel."},
        {"type": "textarea", "id": "noot", "label": "Eerlijke noot onder de punten", "info": "Laat leeg op de homepage."},
        {"type": "text", "id": "link_label", "label": "Link", "default": "Zo maken we het"},
        {"type": "url", "id": "link", "label": "Link-adres", "info": "Leeg = /pages/duurzaamheid"},
    ],
    "blocks": [{"type": "punt", "name": "Punt", "settings": [
        {"type": "select", "id": "icoon", "label": "Icoon", "options": ICONEN, "default": "tas"},
        {"type": "select", "id": "kleur", "label": "Kleur van het rondje", "options": [{"value": v, "label": l} for v, l in [("baby", "Baby"), ("rose", "Rose"), ("zand", "Zand"), ("creme", "Crème")]], "default": "baby"},
        {"type": "text", "id": "titel", "label": "Titel", "default": "Punt"},
        {"type": "textarea", "id": "tekst", "label": "Tekst", "default": ""}]}],
    "presets": [{"name": "TT: duurzaamheid", "blocks": [
        {"type": "punt", "settings": {"icoon": "tas", "kleur": "baby", "titel": "Gaat jaren mee", "tekst": "Eén band van sterk nylon loopt in één stuk rond je board. De naden zijn stevig gestikt, juist waar de tas het zwaarst draagt."}},
        {"type": "punt", "settings": {"icoon": "tij", "kleur": "rose", "titel": "We repareren je tas", "tekst": "Gaat er een band of naad stuk? Stuur ons een bericht. We maken hem eerst weer heel, voordat we het over een nieuwe hebben."}},
        {"type": "punt", "settings": {"icoon": "golfjes", "kleur": "zand", "titel": "Geen plastic in je pakket", "tekst": "Je bestelling komt in een kartonnen doos, met papier als opvulling. Geen plastic zakjes, geen bubbeltjesfolie."}},
        {"type": "punt", "settings": {"icoon": "schelp", "kleur": "baby", "titel": "Drie dingen mee", "tekst": "Neem na het surfen drie dingen mee van het strand. Een dop, een touwtje, een stukje plastic. Twee minuten werk."}}]}]})

# ---------- STRAND: neem drie dingen mee ----------
schrijf('tt-strand', """
<section class="tt tt-strand tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap tt-strand__grid">
    <div class="tt-strand__tekst">
      {%- if section.settings.label != blank -%}<p class="tt-duurzaam__label tt-in">{{ section.settings.label }}</p>{%- endif -%}
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
      {%- if section.settings.hand != blank -%}<p class="tt-strand__hand tt-in">{{ section.settings.hand }}</p>{%- endif -%}
    </div>
    <ol class="tt-strand__lijst">
      {%- for block in section.blocks -%}
        <li class="tt-strand__ding tt-in" style="--d: {{ forloop.index0 | times: 0.12 }}s" {{ block.shopify_attributes }}>
          <span class="tt-strand__nr" aria-hidden="true">{{ forloop.index }}</span>
          <span class="tt-strand__wat"><strong>{{ block.settings.titel }}</strong>{%- if block.settings.tekst != blank -%}<span>{{ block.settings.tekst }}</span>{%- endif -%}</span>
        </li>
      {%- endfor -%}
    </ol>
  </div>
</section>
""", {
    "name": "TT: drie dingen mee", "tag": "div", "max_blocks": 3,
    "settings": [
        bg("deep"),
        {"type": "text", "id": "label", "label": "Klein label boven de kop", "default": "Na het surfen"},
        kop("Neem drie dingen|mee van het strand"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Het kost je twee minuten. Kijk op de terugweg om je heen en neem drie dingen mee die niet op het strand horen. Gooi ze in de eerste afvalbak die je tegenkomt."},
        {"type": "text", "id": "hand", "label": "Handgeschreven regel", "default": "Laat het strand mooier achter dan je het vond"},
    ],
    "blocks": [{"type": "ding", "name": "Ding", "settings": [
        {"type": "text", "id": "titel", "label": "Titel", "default": "Een dop"},
        {"type": "text", "id": "tekst", "label": "Tekst"}]}],
    "presets": [{"name": "TT: drie dingen mee", "blocks": [
        {"type": "ding", "settings": {"titel": "Een dop", "tekst": "Van een fles of een blikje"}},
        {"type": "ding", "settings": {"titel": "Een stuk touw", "tekst": "Of visdraad, waar vogels in verstrikt raken"}},
        {"type": "ding", "settings": {"titel": "Een stukje plastic", "tekst": "Een zakje, een rietje, een snoeppapiertje"}}]}]})

# ---------- MEER: kleding en gear naast de draagtas ----------
# De draagtas blijft het hoofdproduct; dit blok laat zien dat er meer is.
schrijf('tt-meer', """
<section class="tt tt-meer tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    <div class="tt-meer__kop">
      <div>
        {%- if section.settings.label != blank -%}<p class="tt-duurzaam__label tt-in">{{ section.settings.label }}</p>{%- endif -%}
        {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      </div>
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </div>
    <ul class="tt-meer__rij">
      {%- for block in section.blocks -%}
        {%- assign mp = block.settings.product -%}
        <li class="tt-meer__item tt-in" style="--d: {{ forloop.index0 | modulo: 3 | times: 0.1 }}s" {{ block.shopify_attributes }}>
          <a class="tt-meer__kaart" href="{% if mp != blank %}{{ mp.url }}{% else %}{{ block.settings.link | default: routes.all_products_collection_url }}{% endif %}">
            <span class="tt-meer__beeld tt-onthul">
              {%- if mp != blank and mp.featured_media -%}{{ mp.featured_media | image_url: width: 900 | image_tag: loading: 'lazy', sizes: '(min-width: 750px) 33vw, 70vw', alt: mp.featured_media.alt | escape }}
              {%- else -%}""" + BB(extra=", sizes: '(min-width: 750px) 33vw, 70vw'") + """{%- endif -%}
            </span>
            <span class="tt-meer__naam">{% if mp != blank %}{{ mp.title }}{% else %}{{ block.settings.titel }}{% endif %}</span>
            <span class="tt-meer__prijs">{% if mp != blank %}{{ mp.price | money_without_trailing_zeros }}{% else %}{{ block.settings.prijs }}{% endif %}</span>
          </a>
        </li>
      {%- endfor -%}
    </ul>
    <div class="tt-knoppen tt-meer__knoppen tt-in">
      {%- if section.settings.btn1_label != blank -%}<a class="tt-knop" href="{{ section.settings.btn1_link | default: routes.all_products_collection_url }}">{{ section.settings.btn1_label }}<span aria-hidden="true">→</span></a>{%- endif -%}
      {%- if section.settings.btn2_label != blank -%}<a class="tt-link" href="{{ section.settings.btn2_link | default: routes.all_products_collection_url }}">{{ section.settings.btn2_label }}</a>{%- endif -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: meer dan een tas", "tag": "div", "max_blocks": 8,
    "settings": [
        bg("creme"),
        {"type": "text", "id": "label", "label": "Klein label boven de kop", "default": "Kleding en gear"},
        kop("Meer dan|een *tas*"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Zware shirts met een verhaal op de rug, een hoodie voor na het surfen en kleine dingen die je elke sessie gebruikt."},
        {"type": "text", "id": "btn1_label", "label": "Knop", "default": "Kleding en accessoires"},
        {"type": "text", "id": "btn1_link", "label": "Knop (adres)", "default": "/collections/kleding-en-accessoires"},
        {"type": "text", "id": "btn2_label", "label": "Tweede link", "default": "Surfgear"},
        {"type": "text", "id": "btn2_link", "label": "Tweede link (adres)", "default": "/collections/surfgear"},
    ],
    "blocks": [{"type": "item", "name": "Product", "settings": [
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = de foto, naam en prijs hieronder."},
        {"type": "text", "id": "titel", "label": "Naam", "default": "Product"},
        {"type": "text", "id": "prijs", "label": "Prijs (tekst)", "default": ""},
        {"type": "text", "id": "link", "label": "Link (adres)", "default": "/collections/all"},
    ] + blok_beeld('tt-meer-1', '', '')}],
    "presets": [{"name": "TT: meer dan een tas"}]})

print('klaar')
