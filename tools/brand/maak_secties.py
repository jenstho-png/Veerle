"""Schrijft de tt-secties (webshop-homepage, ronde 3) naar theme/sections.

Opbouw volgt de koopvolgorde: beeld en belofte, bewijs (USP's), direct kopen,
het probleem herkennen, hoe het werkt, droombeeld, voor wie, het verhaal,
vragen, laatste duw. Alle beelden hebben een sfeerfoto uit de assets als
plaatsvervanger tot Veerle eigen foto's uploadt.
"""
import json, pathlib
T = pathlib.Path(__file__).parent.parent.parent / 'theme' / 'sections'
BG = [{"value": v, "label": l} for v, l in [("creme", "Crème"), ("zand", "Zand"), ("deep", "Deep"), ("baby", "Baby"), ("rose", "Rose"), ("sunshine", "Sunshine")]]
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
  if p == blank
    assign p = settings.tt_product
  endif
  assign v = p.selected_or_first_available_variant
-%}"""

# ---------- HERO: volle foto, grote belofte, productkaartje ----------
s, fb = beeld('', 'Foto', 'tt-foto-hero', 'tide-tode-hero.jpg', 'Surfer loopt met board over het strand naar zee')
schrijf('tt-hero', PRIJS + """
<section class="tt tt-hero{% if section.settings.pagina %} tt-hero--pagina{% endif %}" id="tt-hero-{{ section.id }}">
  <div class="tt-hero__foto" data-tt-hero>""" + B('', fb, ", sizes: '100vw', loading: 'eager'") + """</div>
  <div class="tt-hero__inhoud tt-wrap">
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h1', class: 'tt-kop--xl' -%}
    <div class="tt-hero__onder">
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in" style="--d: .7s">{{ section.settings.text }}</p>{%- endif -%}
      <div class="tt-knoppen tt-in" style="--d: .85s">
        {%- if section.settings.btn_label != blank -%}
          <a class="tt-knop tt-knop--licht" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}{% if p != blank %} · {{ v.price | money_without_trailing_zeros }}{% endif %}<span aria-hidden="true">→</span></a>
        {%- endif -%}
        {%- if section.settings.link_label != blank -%}<a class="tt-link" href="{{ section.settings.link_url | default: '#tt-verhaal' }}">{{ section.settings.link_label }}</a>{%- endif -%}
      </div>
    </div>
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
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        kop("Jij surft.|Wij *dragen.*"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "De draagtas die je board op je rug zet. Handen vrij voor de hike, de scooter en elke reis daartussen."},
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Shop de draagtas"},
        {"type": "url", "id": "btn_link", "label": "Knop-link", "info": "Leeg = het product."},
        {"type": "text", "id": "link_label", "label": "Tweede link", "default": "Waarom we hem maakten"},
        {"type": "url", "id": "link_url", "label": "Tweede link: adres"},
        {"type": "checkbox", "id": "kaart", "label": "Productkaartje rechtsonder", "default": True},
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
          <li class="tt-usp__golf" aria-hidden="true">{% render 'tt-logo', variant: 'golfje' %}</li>
        {%- endfor -%}
      </ul>
    {%- endfor -%}
  </div>
  {%- if section.settings.zegel -%}<div class="tt-usp__zegel" data-tt-draai="0.05">{% render 'tt-logo', variant: 'zegel' %}</div>{%- endif -%}
</section>
""", {
    "name": "TT: voordelen-strook", "tag": "div", "max_blocks": 6,
    "settings": [bg("deep"), {"type": "checkbox", "id": "zegel", "label": "Zegel tonen (half over de foto erboven)", "default": True}],
    "blocks": [{"type": "usp", "name": "Voordeel", "settings": [
        {"type": "select", "id": "icoon", "label": "Icoon", "options": ICONEN, "default": "golf"},
        {"type": "text", "id": "tekst", "label": "Tekst", "default": "Handen vrij"}]}],
    "presets": [{"name": "TT: voordelen-strook", "blocks": [
        {"type": "usp", "settings": {"icoon": "voeten", "tekst": "Handen vrij, ook op de scooter"}},
        {"type": "usp", "settings": {"icoon": "board", "tekst": "Softtop én hardboard"}},
        {"type": "usp", "settings": {"icoon": "golf", "tekst": "Sterke, waterbestendige stof"}},
        {"type": "usp", "settings": {"icoon": "tas", "tekst": "Makkelijk mee in het vliegtuig"}}]}]})

# ---------- KOPEN: galerij + koopblok ----------
s1, fb1 = beeld('', 'Productfoto 1 (zolang het product geen foto\'s heeft)', 'tt-foto-product-1', 'tide-tode-draagtas-1.jpg', 'De Tide-Tode draagtas met board')
s2, fb2 = beeld('b2_', 'Productfoto 2', 'tt-foto-product-2', 'tide-tode-draagtas-2.jpg', 'Board op de rug onderweg naar de spot')
schrijf('tt-koop', PRIJS + """
<section class="tt tt-koop tt-bg--{{ section.settings.bg }}" id="tt-koop-{{ section.id }}" data-tt-koop>
  <div class="tt-wrap tt-koop__grid">
    <div class="tt-koop__galerij">
      {%- assign media = p.media | where: 'media_type', 'image' -%}
      {%- if media.size > 0 -%}
        {%- for m in media limit: 4 -%}
          <div class="tt-koop__foto tt-onthul"{% if forloop.first %} data-tt-cursor="zoom"{% endif %}>{%- if forloop.first -%}{%- render 'tt-sticker', tekst: section.settings.sticker, kleur: 'poppy', vorm: 'rond', class: 'tt-sticker--rechtsboven' -%}{%- endif -%}{{ m.preview_image | image_url: width: 1800 | image_tag: loading: 'lazy', sizes: '(min-width: 990px) 55vw, 100vw', widths: '600, 900, 1200, 1800', alt: m.alt | default: p.title, class: 'tt-beeld__img' }}</div>
        {%- endfor -%}
      {%- else -%}
        <div class="tt-koop__foto tt-onthul">{%- render 'tt-sticker', tekst: section.settings.sticker, kleur: 'poppy', vorm: 'rond', class: 'tt-sticker--rechtsboven' -%}""" + B('', fb1, ", sizes: '(min-width: 990px) 55vw, 100vw'") + """</div>
        <div class="tt-koop__foto tt-onthul">""" + B('b2_', fb2, ", sizes: '(min-width: 990px) 55vw, 100vw'") + """</div>
      {%- endif -%}
    </div>
    <div class="tt-koop__info">
      <div class="tt-koop__plak">
        {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
        <p class="tt-koop__prijs tt-in">
          {%- if p != blank -%}
            <span>{{ v.price | money }}</span>
            {%- if v.compare_at_price > v.price -%}<s>{{ v.compare_at_price | money }}</s>{%- endif -%}
          {%- else -%}<span>{{ section.settings.prijs_tekst }}</span>{%- endif -%}
        </p>
        {%- if section.settings.text != blank -%}<p class="tt-koop__pitch tt-in">{{ section.settings.text }}</p>{%- endif -%}
        <ul class="tt-koop__punten tt-in">
          {%- for block in section.blocks -%}{%- if block.type == 'punt' -%}<li {{ block.shopify_attributes }}><span aria-hidden="true">{% render 'tt-logo', variant: 'golfje' %}</span>{{ block.settings.tekst }}</li>{%- endif -%}{%- endfor -%}
        </ul>
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
                <span data-tt-knoptekst>{% if v.available %}In mijn tas · {{ v.price | money }}{% else %}Uitverkocht{% endif %}</span>
              </button>
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
        <div class="tt-koop__details tt-in">
          {%- for block in section.blocks -%}{%- if block.type == 'detail' -%}
            <details {{ block.shopify_attributes }}><summary>{{ block.settings.titel }}<i aria-hidden="true"></i></summary><div>{{ block.settings.tekst }}</div></details>
          {%- endif -%}{%- endfor -%}
        </div>
      </div>
    </div>
  </div>
  {%- if p != blank -%}
    <div class="tt-balk" data-tt-balk aria-hidden="true">
      <span class="tt-balk__naam">{{ p.title }}<span>{{ v.price | money }}</span></span>
      <button type="button" class="tt-knop" tabindex="-1" data-tt-balkknop>In mijn tas</button>
    </div>
  {%- endif -%}
</section>
""", {
    "name": "TT: kopen", "tag": "div", "max_blocks": 12,
    "settings": [
        bg("creme"),
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        kop("De draagtas.|*Board op je rug.*"),
        {"type": "textarea", "id": "text", "label": "Korte pitch", "default": "Niet meer met je board onder je arm door de duinen. Leg je plank erin, trek de banden aan en hang hem op je rug. Je schouders blijven heel, je wax blijft op je board en je hebt je handen vrij."},
        {"type": "text", "id": "prijs_tekst", "label": "Tekst als er nog geen product is", "default": "Binnenkort"},
        {"type": "text", "id": "sticker", "label": "Sticker op de eerste foto", "default": "nieuw"},
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
        {"type": "punt", "settings": {"tekst": "Geen natte, zanderige plank in een dichte hoes"}},
        {"type": "detail", "settings": {"titel": "Wat past erin", "tekst": "<p>Eén universele maat. Van de grote softtop waar je op leert surfen tot je hardboard voor de verstopte spot.</p>"}},
        {"type": "detail", "settings": {"titel": "Materiaal", "tekst": "<p>Zware, waterbestendige stof, sterke stiksels en donker metalen gespen. Gemaakt om jaren mee te gaan, niet voor één zomer.</p>"}},
        {"type": "detail", "settings": {"titel": "Verzending en retour", "tekst": "<p>We versturen door heel Europa. Past hij toch niet bij je? Je hebt 14 dagen bedenktijd.</p>"}}]}]})

# ---------- PROBLEEM: tekst die volloopt, met losse foto's ----------
s1, fb1 = beeld('', 'Foto links', 'tt-foto-probleem-1', 'tide-tode-sjouwen.jpg', 'Board onder de arm op weg naar het strand')
s2, fb2 = beeld('b2_', 'Foto rechts', 'tt-foto-probleem-2', 'tide-tode-onderweg.jpg', 'Onderweg naar de spot')
schrijf('tt-probleem', """
<section class="tt tt-probleem tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap tt-probleem__wrap">
    <div class="tt-probleem__foto tt-probleem__foto--1" data-tt-snelheid="0.12"><div class="tt-onthul">""" + B('', fb1, ", sizes: '(min-width: 990px) 22vw, 40vw'") + """</div>{%- render 'tt-sticker', tekst: section.settings.sticker, kleur: 'sunshine', icoon: 'voeten', class: 'tt-sticker--onder' -%}</div>
    <p class="tt-probleem__tekst" data-tt-vul>{{ section.settings.tekst | escape | replace: '*', '' }}</p>
    <div class="tt-probleem__foto tt-probleem__foto--2" data-tt-snelheid="-0.1"><div class="tt-onthul">""" + B('b2_', fb2, ", sizes: '(min-width: 990px) 22vw, 40vw'") + """</div><span class="tt-probleem__icoon">{% render 'tt-icoon', icoon: 'zon' %}</span></div>
    {%- if section.settings.slot != blank -%}{%- render 'tt-kop', text: section.settings.slot, tag: 'p', class: 'tt-kop--l tt-probleem__slot' -%}{%- endif -%}
  </div>
</section>
""", {
    "name": "TT: het probleem", "tag": "div",
    "settings": [
        bg("rose"),
        {"type": "text", "id": "sticker", "label": "Sticker op de linkerfoto", "default": "1 uur lopen"},
        {"type": "textarea", "id": "tekst", "label": "Tekst die volloopt", "default": "Wax onder je arm. Pijn in je schouders. Met één hand sturen op de scooter. Je natte, zanderige plank in een dichte hoes proppen. Elke surfer kent het."},
        {"type": "text", "id": "slot", "label": "Slotzin", "info": KOP_INFO, "default": "Dat kan *anders.*"},
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
          <div class="tt-zo__foto tt-onthul">""" + BB(extra=", sizes: '(min-width: 990px) 30vw, 80vw'") + """<span class="tt-zo__nr">{{ forloop.index }}</span></div>
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
    "settings": [bg("zand"), kop("Board erin.|Banden om.|*Gaan.*")],
    "blocks": [{"type": "stap", "name": "Stap", "settings": [
        {"type": "text", "id": "titel", "label": "Titel", "default": "Stap"},
        {"type": "textarea", "id": "tekst", "label": "Tekst", "default": ""},
        {"type": "select", "id": "icoon", "label": "Icoon", "options": ICONEN, "default": "board"}] + blok_beeld('tt-foto-stap-1', '', '')}],
    "presets": [{"name": "TT: zo werkt het", "blocks": [
        {"type": "stap", "settings": {"titel": "Leg je board erin", "tekst": "Softtop of hardboard, nat of droog. Gewoon zoals hij uit het water komt.", "icoon": "board", "fallback": "tt-foto-stap-1", "filename": "tide-tode-stap-1.jpg", "alt": "Surfboard in het zand"}},
        {"type": "stap", "settings": {"titel": "Trek de banden aan", "tekst": "Je board zit vast en schuift niet. Geen losse touwtjes of spanbanden meer.", "icoon": "karabijn", "fallback": "tt-foto-stap-2", "filename": "tide-tode-stap-2.jpg", "alt": "Handen trekken een band strak"}},
        {"type": "stap", "settings": {"titel": "Op je rug en gaan", "tekst": "Door de duinen, over de rotsen of achterop de scooter. Jij hebt je handen vrij.", "icoon": "voeten", "fallback": "tt-foto-stap-3", "filename": "tide-tode-stap-3.jpg", "alt": "Surfer loopt met board naar zee"}}]}]})

# ---------- MOOD: Pinterest-muur ----------
schrijf('tt-muur', """
<section class="tt tt-muur tt-bg--{{ section.settings.bg }}">
  <div class="tt-muur__kop tt-wrap">
    <span class="tt-zweef tt-zweef--1" data-tt-snelheid="0.3" aria-hidden="true">{% render 'tt-icoon', icoon: 'zeester' %}</span>
    <span class="tt-zweef tt-zweef--2" data-tt-snelheid="-0.2" aria-hidden="true">{% render 'tt-icoon', icoon: 'schelp' %}</span>
    <span class="tt-zweef tt-zweef--3" data-tt-snelheid="0.45" aria-hidden="true">{% render 'tt-icoon', icoon: 'zon' %}</span>
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
    {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
  </div>
  <div class="tt-muur__kolommen">
    {%- for k in (1..3) -%}
      {%- assign snel = '0.10' -%}{%- if k == 2 -%}{%- assign snel = '-0.14' -%}{%- elsif k == 3 -%}{%- assign snel = '0.2' -%}{%- endif -%}
      <div class="tt-muur__kolom tt-muur__kolom--{{ k }}" data-tt-snelheid="{{ snel }}">
        {%- for block in section.blocks -%}
          {%- assign kol = forloop.index0 | modulo: 3 | plus: 1 -%}
          {%- if kol == k -%}
            <figure class="tt-muur__item tt-muur__item--{{ block.settings.vorm }}" {{ block.shopify_attributes }}>
              <div class="tt-onthul">""" + BB(extra=", sizes: '(min-width: 990px) 30vw, 46vw'") + """</div>
              {%- render 'tt-sticker', tekst: block.settings.sticker, kleur: block.settings.sticker_kleur, icoon: block.settings.sticker_icoon -%}
              {%- if block.settings.onderschrift != blank -%}<figcaption>{{ block.settings.onderschrift }}</figcaption>{%- endif -%}
            </figure>
          {%- endif -%}
        {%- endfor -%}
      </div>
    {%- endfor -%}
  </div>
</section>
""", {
    "name": "TT: fotomuur", "tag": "div", "max_blocks": 12,
    "settings": [bg("creme"), kop("Overal waar|het water *roept.*"),
                 {"type": "textarea", "id": "text", "label": "Tekst", "default": "Australië, Midden-Amerika, Azië of gewoon de duinen om de hoek. De tas gaat mee, zodat jij alleen nog aan die ene golf hoeft te denken."}],
    "blocks": [{"type": "foto", "name": "Foto", "settings": [
        {"type": "select", "id": "vorm", "label": "Vorm", "options": [{"value": "staand", "label": "Staand"}, {"value": "hoog", "label": "Hoog"}, {"value": "vierkant", "label": "Vierkant"}, {"value": "boog", "label": "Boog"}, {"value": "liggend", "label": "Liggend"}], "default": "staand"},
        {"type": "text", "id": "onderschrift", "label": "Onderschrift"},
        {"type": "text", "id": "sticker", "label": "Sticker"},
        {"type": "select", "id": "sticker_kleur", "label": "Stickerkleur", "options": KLEUREN, "default": "sunshine"},
        {"type": "select", "id": "sticker_icoon", "label": "Stickericoon", "options": [{"value": "", "label": "Geen"}] + ICONEN, "default": ""}] + blok_beeld('tt-foto-mood-1', '', '')}],
    "presets": [{"name": "TT: fotomuur", "blocks": [
        {"type": "foto", "settings": {"vorm": "hoog", "fallback": "tt-foto-mood-1", "onderschrift": "de hike naar de spot", "alt": "Pad door de duinen naar zee"}},
        {"type": "foto", "settings": {"vorm": "vierkant", "sticker": "handen vrij", "sticker_kleur": "sunshine", "sticker_icoon": "zon", "fallback": "tt-foto-mood-2", "alt": "Boards in het zand"}},
        {"type": "foto", "settings": {"vorm": "boog", "fallback": "tt-foto-mood-3", "onderschrift": "golden hour", "alt": "Zee bij zonsondergang"}},
        {"type": "foto", "settings": {"vorm": "liggend", "fallback": "tt-foto-mood-4", "alt": "Rustige golven"}},
        {"type": "foto", "settings": {"vorm": "staand", "fallback": "tt-foto-mood-5", "onderschrift": "op weg naar zee", "alt": "Surfer op weg naar zee"}},
        {"type": "foto", "settings": {"vorm": "hoog", "sticker": "zout, zand, nat: prima", "sticker_kleur": "rose", "sticker_icoon": "schelp", "fallback": "tt-foto-mood-6", "alt": "Board tegen een muur"}},
        {"type": "foto", "settings": {"vorm": "staand", "fallback": "tt-foto-mood-7", "onderschrift": "van riders voor riders", "alt": "Surfers op het strand"}},
        {"type": "foto", "settings": {"vorm": "boog", "sticker": "Tide~Tode", "sticker_kleur": "deep", "sticker_icoon": "maan", "fallback": "tt-foto-mood-8", "alt": "Kust van bovenaf"}},
        {"type": "foto", "settings": {"vorm": "vierkant", "fallback": "tt-foto-mood-9", "onderschrift": "door de duinen", "alt": "Hek tussen het duingras"}}]}]})

# ---------- VOOR WIE ----------
schrijf('tt-wie', """
<section class="tt tt-wie tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap">
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l tt-wie__kop' -%}
    <div class="tt-wie__grid">
      {%- for block in section.blocks -%}
        <a class="tt-wie__kaart" href="{{ block.settings.link | default: routes.all_products_collection_url }}" {{ block.shopify_attributes }} data-tt-cursor="shop">
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
    "settings": [bg("baby"), kop("Voor elke|*soort* surfer.")],
    "blocks": [{"type": "kaart", "name": "Kaart", "settings": [
        {"type": "text", "id": "titel", "label": "Titel", "default": "Titel"},
        {"type": "textarea", "id": "tekst", "label": "Tekst"},
        {"type": "text", "id": "knop", "label": "Linktekst", "default": "Shop de tas"},
        {"type": "url", "id": "link", "label": "Link"},
        {"type": "text", "id": "sticker", "label": "Sticker"},
        {"type": "select", "id": "sticker_kleur", "label": "Stickerkleur", "options": KLEUREN, "default": "sunshine"},
        {"type": "select", "id": "sticker_icoon", "label": "Stickericoon", "options": [{"value": "", "label": "Geen"}] + ICONEN, "default": ""}] + blok_beeld('tt-foto-beginner', '', '')}],
    "presets": [{"name": "TT: voor wie", "blocks": [
        {"type": "kaart", "settings": {"titel": "Je leert surfen", "tekst": "Groot softtop-board, lange wandeling van hostel of hotel naar het strand. Met de tas loop je ontspannen en heb je je handen vrij.", "knop": "Shop de tas", "sticker": "softtop", "sticker_kleur": "sunshine", "sticker_icoon": "board", "fallback": "tt-foto-beginner", "filename": "tide-tode-beginner.jpg", "alt": "Beginner met een softtop op het strand"}},
        {"type": "kaart", "settings": {"titel": "Je zoekt de verstopte spot", "tekst": "Door de bush, over rotsen, achterop de scooter. Jouw board hangt veilig op je rug, jij houdt je handen vrij om te klimmen.", "knop": "Shop de tas", "sticker": "hardboard", "sticker_kleur": "poppy", "sticker_icoon": "golf", "fallback": "tt-foto-avontuur", "filename": "tide-tode-avontuur.jpg", "alt": "Surfer klimt over rotsen naar een afgelegen spot"}}]}]})

# ---------- VERHAAL ----------
s, fb = beeld('', 'Foto', 'tt-foto-verhaal', 'tide-tode-verhaal.jpg', 'Op reis met een surfboard')
schrijf('tt-verhaal', """
<section class="tt tt-verhaal tt-bg--{{ section.settings.bg }}" id="tt-verhaal">
  <div class="tt-wrap tt-verhaal__grid">
    <div class="tt-verhaal__foto" data-tt-snelheid="-0.06"><div class="tt-onthul">""" + B('', fb, ", sizes: '(min-width: 990px) 42vw, 90vw'") + """</div><div class="tt-verhaal__zegel" data-tt-draai="-0.05">{% render 'tt-logo', variant: 'zegel' %}</div></div>
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
        kop("“Niets hield het vol.|*Dus maakten we|hem zelf.*”"),
        {"type": "richtext", "id": "text", "label": "Tekst", "default": "<p>Lange hikes naar afgelegen spots in Australië, Midden-Amerika en Azië, met een log board onder je arm. De wax schuurt, je schouders doen pijn en op de scooter stuur je met één hand. Losse touwtjes, spanbanden, standaardhoezen: we hebben het allemaal geprobeerd.</p><p>Dus maakten we de tas die we zelf zochten. Van riders, voor riders.</p>"},
        {"type": "text", "id": "naam", "label": "Ondertekening", "default": "Veerle"},
        {"type": "text", "id": "link_label", "label": "Link", "default": "Lees het hele verhaal"},
        {"type": "url", "id": "link", "label": "Link-adres"},
    ] + s,
    "presets": [{"name": "TT: het verhaal"}]})

# ---------- SLOT ----------
s, fb = beeld('', 'Foto', 'tt-foto-slot', 'tide-tode-slot.jpg', 'Zee bij zonsondergang')
schrijf('tt-slot', PRIJS + """
<section class="tt tt-slot">
  <div class="tt-slot__foto" data-tt-snelheid="0.12">""" + B('', fb, ", sizes: '100vw'") + """</div>
  <div class="tt-slot__inhoud tt-wrap">
    <div class="tt-slot__maan tt-in">{% render 'tt-logo', variant: 'maan' %}</div>
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--xl' -%}
    <div class="tt-knoppen tt-in">
      <a class="tt-knop tt-knop--licht" href="{% if section.settings.btn_link != blank %}{{ section.settings.btn_link }}{% elsif p != blank %}{{ p.url }}{% else %}{{ routes.all_products_collection_url }}{% endif %}">{{ section.settings.btn_label }}{% if p != blank %} · {{ v.price | money_without_trailing_zeros }}{% endif %}<span aria-hidden="true">→</span></a>
    </div>
  </div>
</section>
""", {
    "name": "TT: slot", "tag": "div",
    "settings": [
        {"type": "product", "id": "product", "label": "Product", "info": "Leeg = het product uit Thema-instellingen > Tide-Tode."},
        kop("Pak je tas.|*De zee wacht.*"),
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Shop de draagtas"},
        {"type": "url", "id": "btn_link", "label": "Knop-link"},
    ] + s,
    "presets": [{"name": "TT: slot"}]})

# ---------- MERK: de maan draagt het getij ----------
schrijf('tt-merk', """
<section class="tt tt-merk tt-bg--{{ section.settings.bg }}">
  <div class="tt-wrap tt-merk__wrap">
    <div class="tt-merk__maan" data-tt-snelheid="0.12">{% render 'tt-logo', variant: 'maan' %}</div>
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
    {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
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
        kop("Zoals de maan|het getij draagt,|dragen wij *je board.*"),
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Het getij bestaat omdat de maan aan de zee trekt. Elke dag, overal ter wereld, zonder dat iemand er iets voor hoeft te doen. Daarom staat er een maan in ons teken, met drie golfjes in haar arm."},
        {"type": "text", "id": "iconen", "label": "Iconen (komma's, zonder spaties)", "default": "golf,schelp,zon,zeester,board,tas,palmblad,meeuw"},
    ],
    "presets": [{"name": "TT: merk"}]})

print('klaar')
