"""Schrijft de tt-secties (nieuwe homepage-ontwerp) naar theme/sections."""
import json, pathlib
T = pathlib.Path(__file__).parent.parent.parent / 'theme' / 'sections'
SCENES = [{"value": v, "label": l} for v, l in [("zee", "Zee"), ("duin", "Duinen"), ("onder", "Onder water"), ("avond", "Zonsondergang"), ("nacht", "Nachtzee"), ("palm", "Palmschaduw"), ("boards", "Boards"), ("tas", "De tas")]]
BG = [{"value": v, "label": l} for v, l in [("creme", "Crème"), ("deep", "Deep"), ("baby", "Baby"), ("rose", "Rose"), ("sunshine", "Sunshine"), ("poppy", "Poppy")]]
ICONEN = [{"value": k, "label": n} for k, n in [("tas", "De tas"), ("golf", "Golf"), ("golfjes", "Getij"), ("board", "Board"), ("schelp", "Schelp"), ("zon", "Zon"), ("maan", "Maan"), ("zeester", "Zeester"), ("koraal", "Koraal"), ("palmblad", "Palmblad"), ("meeuw", "Meeuw"), ("wax", "Wax"), ("karabijn", "Karabijnhaak"), ("tij", "Spiraal"), ("voeten", "Onderweg")]]
KOP_INFO = "Een | is een nieuwe regel. Zet een woord tussen *sterretjes* voor het cursieve accent."


def beeld(prefix, label, scene, filename, alt):
    return [
        {"type": "header", "content": label},
        {"type": "image_picker", "id": f"{prefix}image", "label": "Foto"},
        {"type": "text", "id": f"{prefix}filename", "label": "Bestandsnaam (SEO)", "default": filename, "info": "Upload in Content > Bestanden met precies deze naam; tot die tijd staat er een getekende scène."},
        {"type": "select", "id": f"{prefix}scene", "label": "Scène zolang er geen foto is", "options": SCENES, "default": scene},
        {"type": "text", "id": f"{prefix}alt", "label": "Alt-tekst", "default": alt},
    ]


def R(prefix, extra=""):
    return ("{%- render 'tt-beeld', image: section.settings." + prefix + "image, filename: section.settings." + prefix + "filename, scene: section.settings." + prefix + "scene, alt: section.settings." + prefix + "alt" + extra + " -%}")


def schrijf(naam, body, schema):
    (T / f'{naam}.liquid').write_text(body.strip() + "\n\n{% schema %}\n" + json.dumps(schema, indent=2, ensure_ascii=False) + "\n{% endschema %}\n")


# ---------- HERO ----------
schrijf('tt-hero', """
<section class="tt tt-hero tt-bg--{{ section.settings.bg }}{% if section.settings.pagina %} tt-hero--pagina{% endif %}" id="tt-hero-{{ section.id }}">
  <div class="tt-hero__grid tt-wrap">
    <div class="tt-hero__tekst">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h1', class: 'tt-kop--xl' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in" style="--d: .5s">{{ section.settings.text }}</p>{%- endif -%}
      <div class="tt-knoppen tt-in" style="--d: .65s">
        {%- if section.settings.btn1_label != blank -%}<a class="tt-knop" href="{{ section.settings.btn1_link | default: routes.all_products_collection_url }}">{{ section.settings.btn1_label }}<span aria-hidden="true">→</span></a>{%- endif -%}
        {%- if section.settings.btn2_label != blank -%}<a class="tt-link" href="{{ section.settings.btn2_link | default: '#' }}">{{ section.settings.btn2_label }}</a>{%- endif -%}
      </div>
    </div>
    <div class="tt-hero__beelden">
      <div class="tt-hero__boog tt-onthul" data-tt-snelheid="-0.06" data-tt-cursor="{{ section.settings.cursor }}">""" + R('', ", sizes: '(min-width: 990px) 40vw, 90vw', loading: 'eager'") + """</div>
      <div class="tt-hero__rond tt-onthul" data-tt-snelheid="0.14" style="--d: .35s">""" + R('klein1_', ", sizes: '200px'") + """</div>
      <div class="tt-hero__staand tt-onthul" data-tt-snelheid="-0.18" style="--d: .5s">""" + R('klein2_', ", sizes: '200px'") + """</div>
      {%- if section.settings.zegel -%}<div class="tt-hero__zegel" data-tt-draai="0.12">{% render 'tt-logo', variant: 'zegel' %}</div>{%- endif -%}
    </div>
  </div>
  {%- unless section.settings.pagina -%}<div class="tt-hero__scroll" aria-hidden="true"><span>scroll</span><i></i></div>{%- endunless -%}
</section>
""", {
    "name": "TT: hero", "tag": "div",
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "creme"},
        {"type": "checkbox", "id": "pagina", "label": "Compacte versie (voor subpagina's)", "default": False},
        {"type": "text", "id": "heading", "label": "Kop", "info": KOP_INFO, "default": "Jij surft.|Wij *dragen.*"},
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "De draagtas die je board op je rug zet. Voor de hike naar die verstopte spot, de scooter naar het strand en elke reis daartussen."},
        {"type": "text", "id": "btn1_label", "label": "Knop", "default": "Bekijk de tas"},
        {"type": "url", "id": "btn1_link", "label": "Knop-link"},
        {"type": "text", "id": "btn2_label", "label": "Tweede link", "default": "Hoe het begon"},
        {"type": "url", "id": "btn2_link", "label": "Tweede link: adres"},
        {"type": "checkbox", "id": "zegel", "label": "Zegel tonen", "default": True},
        {"type": "text", "id": "cursor", "label": "Cursortekst op de grote foto", "default": "op pad"},
    ] + beeld('', 'Grote foto (boog)', 'zee', 'tide-tode-hike-naar-de-spot.jpg', 'Surfer met board op de rug onderweg naar de zee')
      + beeld('klein1_', 'Kleine ronde foto', 'palm', 'tide-tode-palmschaduw.jpg', 'Palmschaduw op een witte muur')
      + beeld('klein2_', 'Kleine staande foto', 'boards', 'tide-tode-boards-tegen-de-muur.jpg', 'Surfboards tegen een muur'),
    "presets": [{"name": "TT: hero"}]})

# ---------- BAND ----------
schrijf('tt-band', """
{%- capture woorden -%}{%- for block in section.blocks -%}{{ block.settings.tekst }}{% unless forloop.last %}, {% endunless %}{%- endfor -%}{%- endcapture -%}
<section class="tt tt-band tt-bg--{{ section.settings.bg }}" aria-label="{{ woorden | escape }}">
  {%- for rij in (1..section.settings.rijen) -%}
    <div class="tt-band__rij" data-tt-band="{% if rij == 2 %}1{% else %}-1{% endif %}" data-tt-snelheid-x="{{ section.settings.snelheid | divided_by: 100.0 }}">
      <div class="tt-band__spoor" aria-hidden="true">
        {%- for n in (1..4) -%}
          {%- for block in section.blocks -%}
            {%- assign lijn = forloop.index0 | modulo: 2 -%}
            <span class="tt-band__item{% if lijn == 1 %} tt-band__item--lijn{% endif %}">{{ block.settings.tekst }}</span>
            <span class="tt-band__teken">{%- if block.settings.icoon != blank and block.settings.icoon != 'golfje' -%}{% render 'tt-icoon', icoon: block.settings.icoon %}{%- else -%}{% render 'tt-logo', variant: 'golfje' %}{%- endif -%}</span>
          {%- endfor -%}
        {%- endfor -%}
      </div>
    </div>
  {%- endfor -%}
</section>
""", {
    "name": "TT: woordband", "tag": "div", "max_blocks": 6,
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "creme"},
        {"type": "range", "id": "rijen", "label": "Rijen", "min": 1, "max": 2, "step": 1, "default": 2},
        {"type": "range", "id": "snelheid", "label": "Snelheid", "min": 10, "max": 80, "step": 5, "default": 35},
    ],
    "blocks": [{"type": "woord", "name": "Woord", "settings": [
        {"type": "text", "id": "tekst", "label": "Tekst", "default": "handen vrij"},
        {"type": "select", "id": "icoon", "label": "Teken erna", "options": [{"value": "golfje", "label": "Golfje"}] + ICONEN, "default": "golfje"}]}],
    "presets": [{"name": "TT: woordband", "blocks": [
        {"type": "woord", "settings": {"tekst": "handen vrij", "icoon": "golfje"}},
        {"type": "woord", "settings": {"tekst": "op weg naar zee", "icoon": "schelp"}},
        {"type": "woord", "settings": {"tekst": "van riders, voor riders", "icoon": "golfje"}},
        {"type": "woord", "settings": {"tekst": "nul schuurplekken", "icoon": "zeester"}}]}]})

# ---------- MANIFEST ----------
schrijf('tt-manifest', """
<section class="tt tt-manifest tt-bg--{{ section.settings.bg }}" id="tt-manifest-{{ section.id }}">
  <div class="tt-wrap tt-manifest__binnen">
    <p class="tt-manifest__tekst" data-tt-vul>
      {%- assign delen = section.settings.tekst | split: '*' -%}
      {%- for deel in delen -%}
        {%- assign odd = forloop.index0 | modulo: 2 -%}
        {%- if odd == 1 -%}<em>{{ deel | escape }}</em>{%- else -%}{{ deel | escape }}{%- endif -%}
      {%- endfor -%}
    </p>
    {%- if section.settings.naam != blank -%}
      <p class="tt-manifest__naam tt-in">{% render 'tt-logo', variant: 'maan-simpel' %}<span><em>{{ section.settings.naam }}</em>{{ section.settings.rol }}</span></p>
    {%- endif -%}
  </div>
</section>
""", {
    "name": "TT: manifest", "tag": "div",
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "creme"},
        {"type": "textarea", "id": "tekst", "label": "Tekst", "info": "*woord* = cursief accent. De woorden kleuren in terwijl je scrolt.", "default": "Niet iedereen rolt uit bed *de golf in.* Sommigen lopen eerst een uur door de duinen, klimmen over rotsen, met een board dat nergens lekker vast te houden is. Voor hen maakten we *Tide-Tode.*"},
        {"type": "text", "id": "naam", "label": "Naam", "default": "Veerle"},
        {"type": "text", "id": "rol", "label": "Rol", "default": "oprichter, surfer, sjouwer"},
    ],
    "presets": [{"name": "TT: manifest"}]})

# ---------- COLLAGE ----------
schrijf('tt-collage', """
<section class="tt tt-collage tt-bg--{{ section.settings.bg }}" id="tt-collage-{{ section.id }}">
  <div class="tt-wrap">
    <div class="tt-collage__kop">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    </div>
    <div class="tt-collage__raster">
      {%- for block in section.blocks -%}
        {%- liquid
          assign i = forloop.index0 | modulo: 4
          case i
            when 0
              assign v = '-0.08'
            when 1
              assign v = '0.06'
            when 2
              assign v = '-0.14'
            else
              assign v = '0.1'
          endcase
        -%}
        {%- case block.type -%}
          {%- when 'beeld' -%}
            <figure class="tt-stuk tt-stuk--{{ block.settings.vorm }}" data-tt-snelheid="{{ v }}" {{ block.shopify_attributes }}>
              <div class="tt-stuk__beeld tt-onthul" data-tt-cursor="{{ block.settings.caption | default: 'onderweg' }}">{%- render 'tt-beeld', image: block.settings.image, filename: block.settings.filename, scene: block.settings.scene, alt: block.settings.alt, sizes: '(min-width: 990px) 30vw, 50vw' -%}</div>
              {%- if block.settings.caption != blank -%}<figcaption>{{ block.settings.caption }}</figcaption>{%- endif -%}
            </figure>
          {%- when 'quote' -%}
            <blockquote class="tt-stuk tt-stuk--quote tt-bg--{{ block.settings.bg }}" data-tt-snelheid="{{ v }}" {{ block.shopify_attributes }}><p>{{ block.settings.tekst }}</p></blockquote>
          {%- when 'zegel' -%}
            <div class="tt-stuk tt-stuk--zegel tt-bg--{{ block.settings.bg }}" data-tt-draai="0.08" {{ block.shopify_attributes }}>{% render 'tt-logo', variant: 'zegel' %}</div>
          {%- when 'icoon' -%}
            <div class="tt-stuk tt-stuk--icoon tt-bg--{{ block.settings.bg }}" data-tt-snelheid="{{ v }}" {{ block.shopify_attributes }}>{% render 'tt-icoon', icoon: block.settings.icoon %}</div>
        {%- endcase -%}
      {%- endfor -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: collage", "tag": "div", "max_blocks": 12,
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "creme"},
        {"type": "text", "id": "heading", "label": "Kop", "info": KOP_INFO, "default": "Overal waar|het water *roept.*"},
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Australië, Midden-Amerika, Azië, de duinen om de hoek. De tas ging overal mee, zodat jij alleen nog aan die ene golf hoeft te denken."},
    ],
    "blocks": [
        {"type": "beeld", "name": "Foto", "settings": [
            {"type": "select", "id": "vorm", "label": "Vorm", "options": [{"value": "boog", "label": "Boog"}, {"value": "rond", "label": "Rond"}, {"value": "staand", "label": "Staand"}, {"value": "vierkant", "label": "Vierkant"}, {"value": "breed", "label": "Breed"}], "default": "boog"},
            {"type": "image_picker", "id": "image", "label": "Foto"},
            {"type": "text", "id": "filename", "label": "Bestandsnaam (SEO)", "default": "tide-tode-onderweg.jpg"},
            {"type": "select", "id": "scene", "label": "Scène zolang er geen foto is", "options": SCENES, "default": "zee"},
            {"type": "text", "id": "alt", "label": "Alt-tekst"},
            {"type": "text", "id": "caption", "label": "Onderschrift"}]},
        {"type": "quote", "name": "Zin", "settings": [{"type": "text", "id": "tekst", "label": "Tekst", "default": "Board op je rug, wind in je haar."}, {"type": "select", "id": "bg", "label": "Kleur", "options": BG, "default": "rose"}]},
        {"type": "zegel", "name": "Zegel", "limit": 2, "settings": [{"type": "select", "id": "bg", "label": "Kleur", "options": BG, "default": "sunshine"}]},
        {"type": "icoon", "name": "Icoon", "settings": [{"type": "select", "id": "icoon", "label": "Icoon", "options": ICONEN, "default": "schelp"}, {"type": "select", "id": "bg", "label": "Kleur", "options": BG, "default": "baby"}]},
    ],
    "presets": [{"name": "TT: collage", "blocks": [
        {"type": "beeld", "settings": {"vorm": "boog", "scene": "zee", "filename": "tide-tode-australie-hike.jpg", "alt": "Hike naar een surfspot in Australië", "caption": "Australië, om zes uur 's ochtends"}},
        {"type": "quote", "settings": {"tekst": "Board op je rug, wind in je haar.", "bg": "rose"}},
        {"type": "beeld", "settings": {"vorm": "rond", "scene": "palm", "filename": "tide-tode-palmschaduw-hostel.jpg", "alt": "Palmschaduw op de muur van een hostel", "caption": "het hostel"}},
        {"type": "zegel", "settings": {"bg": "sunshine"}},
        {"type": "beeld", "settings": {"vorm": "staand", "scene": "onder", "filename": "tide-tode-duiken.jpg", "alt": "Duiken in diep blauw water", "caption": "en dan even onder water"}},
        {"type": "icoon", "settings": {"icoon": "schelp", "bg": "baby"}},
        {"type": "beeld", "settings": {"vorm": "breed", "scene": "avond", "filename": "tide-tode-zonsondergang.jpg", "alt": "Zonsondergang na een surfsessie", "caption": "golden hour"}},
        {"type": "beeld", "settings": {"vorm": "vierkant", "scene": "boards", "filename": "tide-tode-boards.jpg", "alt": "Surfboards tegen een muur", "caption": "kies je board"}},
        {"type": "beeld", "settings": {"vorm": "boog", "scene": "duin", "filename": "tide-tode-duinen.jpg", "alt": "Tas op de rug in de duinen", "caption": "de duinen om de hoek"}}]}]})

# ---------- DE TAS (sticky) ----------
schrijf('tt-tas', """
{%- assign p = section.settings.product -%}
{%- assign variant = p.selected_or_first_available_variant -%}
<section class="tt tt-tas tt-bg--{{ section.settings.bg }}" id="tt-tas-{{ section.id }}">
  <div class="tt-wrap tt-tas__grid">
    <div class="tt-tas__plak">
      <div class="tt-tas__beeld tt-onthul" data-tt-cursor="{{ section.settings.cursor }}">
        {%- if p.featured_media != blank and section.settings.image == blank -%}
          {%- render 'tt-beeld', image: p.featured_media.preview_image, alt: p.title, sizes: '(min-width: 990px) 45vw, 90vw' -%}
        {%- else -%}""" + R('', ", sizes: '(min-width: 990px) 45vw, 90vw'") + """{%- endif -%}
      </div>
      <div class="tt-tas__prijs">
        {%- if p != blank -%}<span>{{ variant.price | money_without_trailing_zeros }}</span>{%- else -%}<span>{{ section.settings.prijs_tekst }}</span>{%- endif -%}
      </div>
    </div>
    <div class="tt-tas__info">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
      {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
      <ol class="tt-tas__lijst">
        {%- for block in section.blocks -%}
          <li class="tt-in" {{ block.shopify_attributes }}>
            <span class="tt-tas__icoon">{% render 'tt-icoon', icoon: block.settings.icoon %}</span>
            <div><h3>{{ block.settings.titel }}</h3><p>{{ block.settings.tekst }}</p></div>
          </li>
        {%- endfor -%}
      </ol>
      <div class="tt-tas__koop tt-in">
        {%- if p != blank -%}
          {%- form 'product', p -%}
            <input type="hidden" name="id" value="{{ variant.id }}">
            <button type="submit" class="tt-knop"{% unless p.available %} disabled{% endunless %}>{% if p.available %}In je tas · {{ variant.price | money }}{% else %}Binnenkort weer op voorraad{% endif %}<span aria-hidden="true">→</span></button>
          {%- endform -%}
          <a class="tt-link" href="{{ p.url }}">Alle details</a>
        {%- else -%}
          <a class="tt-knop" href="{{ routes.all_products_collection_url }}">Bekijk de tas<span aria-hidden="true">→</span></a>
        {%- endif -%}
      </div>
      {%- if section.settings.note != blank -%}<p class="tt-klein tt-in">{{ section.settings.note }}</p>{%- endif -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: de tas", "tag": "div", "max_blocks": 6,
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "baby"},
        {"type": "product", "id": "product", "label": "Product"},
        {"type": "text", "id": "heading", "label": "Kop", "info": KOP_INFO, "default": "Eén tas.|*Elk* board."},
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Van de grote softtop waar je op leert surfen tot het hardboard dat al vijf reizen meegaat. Board erin, banden om, gaan."},
        {"type": "text", "id": "note", "label": "Kleine regel", "default": "Geen wegwerpproduct. Een tas waar je jaren mee vooruit kunt."},
        {"type": "text", "id": "prijs_tekst", "label": "Tekst in de cirkel zonder product", "default": "nieuw"},
        {"type": "text", "id": "cursor", "label": "Cursortekst", "default": "draag mij"},
    ] + beeld('', 'Productfoto (als het product nog geen foto heeft)', 'tas', 'tide-tode-draagtas.jpg', 'De Tide-Tode draagtas met surfboard'),
    "blocks": [{"type": "punt", "name": "Kenmerk", "settings": [
        {"type": "select", "id": "icoon", "label": "Icoon", "options": ICONEN, "default": "tas"},
        {"type": "text", "id": "titel", "label": "Titel", "default": "Handen vrij"},
        {"type": "textarea", "id": "tekst", "label": "Tekst"}]}],
    "presets": [{"name": "TT: de tas", "blocks": [
        {"type": "punt", "settings": {"icoon": "tas", "titel": "Handen vrij", "tekst": "Het board hangt op je rug. Je handen zijn voor het stuur, de rotsen of je koffie."}},
        {"type": "punt", "settings": {"icoon": "voeten", "titel": "Kilometers zonder klagen", "tekst": "Ergonomische banden verdelen het gewicht. Je schouders komen net zo fris aan als jij."}},
        {"type": "punt", "settings": {"icoon": "golf", "titel": "Nat, zand, zout: prima", "tekst": "Zware stof en stevige stiksels. Natte board erin na de sessie, klaar."}},
        {"type": "punt", "settings": {"icoon": "meeuw", "titel": "Reist mee", "tekst": "Klein opgevouwen in je bagage. Huur je ter plekke een board, dan heb je je tas al."}}]}]})

# ---------- REIS (horizontaal) ----------
schrijf('tt-reis', """
<section class="tt tt-reis tt-bg--{{ section.settings.bg }}" data-tt-pin style="--n: {{ section.blocks.size | plus: 1 }}" id="tt-reis-{{ section.id }}">
  <div class="tt-reis__pin">
    <div class="tt-reis__spoor" data-tt-spoor>
      <div class="tt-reis__intro">
        {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--l' -%}
        {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
        <span class="tt-reis__pijl tt-in" aria-hidden="true">{% render 'tt-logo', variant: 'golfje' %}<i>→</i></span>
      </div>
      {%- for block in section.blocks -%}
        <article class="tt-reis__paneel" {{ block.shopify_attributes }}>
          <div class="tt-reis__beeld" data-tt-cursor="{{ block.settings.titel | split: ' ' | last }}">{%- render 'tt-beeld', image: block.settings.image, filename: block.settings.filename, scene: block.settings.scene, alt: block.settings.titel, sizes: '(min-width: 990px) 34vw, 80vw' -%}</div>
          <span class="tt-reis__nr">{{ forloop.index | prepend: '0' }}</span>
          <h3>{{ block.settings.titel }}</h3>
          <p>{{ block.settings.tekst }}</p>
        </article>
      {%- endfor -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: waar ga jij heen", "tag": "div", "max_blocks": 6,
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "creme"},
        {"type": "text", "id": "heading", "label": "Kop", "info": KOP_INFO, "default": "Waar ga|*jij* heen?"},
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Eén tas voor elke weg naar het water."},
    ],
    "blocks": [{"type": "paneel", "name": "Paneel", "settings": [
        {"type": "image_picker", "id": "image", "label": "Foto"},
        {"type": "text", "id": "filename", "label": "Bestandsnaam (SEO)", "default": "tide-tode-onderweg.jpg"},
        {"type": "select", "id": "scene", "label": "Scène zolang er geen foto is", "options": SCENES, "default": "zee"},
        {"type": "text", "id": "titel", "label": "Titel", "default": "Naar het strand"},
        {"type": "textarea", "id": "tekst", "label": "Tekst"}]}],
    "presets": [{"name": "TT: waar ga jij heen", "blocks": [
        {"type": "paneel", "settings": {"scene": "duin", "filename": "tide-tode-hostel-naar-strand.jpg", "titel": "Van je hostel naar het strand", "tekst": "Groot board, lange wandeling. Banden om en lopen maar."}},
        {"type": "paneel", "settings": {"scene": "zee", "filename": "tide-tode-verstopte-spot.jpg", "titel": "Over de rotsen naar die verstopte spot", "tekst": "Twee handen vrij om te klimmen. Je board hangt veilig op je rug."}},
        {"type": "paneel", "settings": {"scene": "avond", "filename": "tide-tode-scooter-kust.jpg", "titel": "Op de scooter langs de kust", "tekst": "Stuur met twee handen. De tas doet de rest."}},
        {"type": "paneel", "settings": {"scene": "boards", "filename": "tide-tode-op-reis.jpg", "titel": "Naar de andere kant van de wereld", "tekst": "Opgevouwen in je bagage. Huur ter plekke een board en je tas is er al."}}]}]})

# ---------- VERHAAL ----------
schrijf('tt-verhaal', """
<section class="tt tt-verhaal tt-bg--{{ section.settings.bg }}" id="tt-verhaal-{{ section.id }}">
  <div class="tt-wrap tt-verhaal__grid">
    <div class="tt-verhaal__rond" data-tt-groei>""" + R('', ", sizes: '(min-width: 990px) 40vw, 80vw'") + """</div>
    <div class="tt-verhaal__tekst">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
      <div class="tt-lead tt-in rte">{{ section.settings.text }}</div>
      {%- if section.settings.naam != blank -%}<p class="tt-handtekening tt-in">{{ section.settings.naam }}</p>{%- endif -%}
      {%- if section.settings.btn_label != blank -%}<a class="tt-link tt-in" href="{{ section.settings.btn_link | default: '#' }}">{{ section.settings.btn_label }}</a>{%- endif -%}
    </div>
  </div>
</section>
""", {
    "name": "TT: verhaal", "tag": "div",
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "rose"},
        {"type": "text", "id": "heading", "label": "Kop", "info": KOP_INFO, "default": "Het begon met|pijnlijke schouders|in *Australië.*"},
        {"type": "richtext", "id": "text", "label": "Tekst", "default": "<p>Lange hikes naar afgelegen spots. Wax die schuurt, een board dat nergens lekker vast te houden is, met één hand sturen op de scooter. Touwtjes en spanbanden hielden het niet. Dus maakte ik de tas zelf.</p>"},
        {"type": "text", "id": "naam", "label": "Ondertekening", "default": "Veerle"},
        {"type": "text", "id": "btn_label", "label": "Link", "default": "Lees het hele verhaal"},
        {"type": "url", "id": "btn_link", "label": "Link: adres"},
    ] + beeld('', 'Ronde foto', 'duin', 'veerle-op-reis.jpg', 'Veerle op reis met haar surfboard'),
    "presets": [{"name": "TT: verhaal"}]})

# ---------- TEKEN ----------
schrijf('tt-teken', """
<section class="tt tt-teken tt-bg--{{ section.settings.bg }}" id="tt-teken-{{ section.id }}">
  <div class="tt-wrap tt-teken__grid">
    <div class="tt-teken__maan" data-tt-teken>
      <svg viewBox="0 0 200 200" aria-hidden="true"><g class="tt-teken__lijn">{% render 'tt-logo', variant: 'maan-simpel-pad' %}</g><g class="tt-teken__vul">{% render 'tt-logo', variant: 'maan-simpel-pad' %}</g></svg>
    </div>
    <div class="tt-teken__tekst">
      {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--m' -%}
      <div class="tt-lead tt-in rte">{{ section.settings.text }}</div>
      <p class="tt-teken__slot tt-in">{{ section.settings.slot }}</p>
    </div>
  </div>
</section>
""", {
    "name": "TT: ons teken", "tag": "div",
    "settings": [
        {"type": "select", "id": "bg", "label": "Achtergrond", "options": BG, "default": "deep"},
        {"type": "text", "id": "heading", "label": "Kop", "info": KOP_INFO, "default": "Zoals de maan|het getij draagt,|dragen wij *je board.*"},
        {"type": "richtext", "id": "text", "label": "Tekst", "default": "<p>Het getij bestaat omdat de maan aan de zee trekt. Elke dag, overal ter wereld, zonder dat iemand er iets voor hoeft te doen. Daarom staat er een maan in ons teken, met drie golfjes in haar arm. En daarom staat er een golfje in onze naam.</p>"},
        {"type": "text", "id": "slot", "label": "Slotregel", "default": "Wij dragen. Jij gaat."},
    ],
    "presets": [{"name": "TT: ons teken"}]})

# ---------- SLOT ----------
schrijf('tt-slot', """
<section class="tt tt-slot" id="tt-slot-{{ section.id }}">
  <div class="tt-slot__achter" data-tt-snelheid="0.18">
    {%- assign achter = section.settings.image -%}
    {%- if achter == blank and section.settings.filename != blank -%}{%- assign achter = images[section.settings.filename] -%}{%- endif -%}
    {%- if achter != blank -%}
      {%- render 'tt-beeld', image: achter, alt: section.settings.alt, sizes: '100vw' -%}
    {%- else -%}
      <svg class="tt-scene" viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice" role="img" aria-label="{{ section.settings.alt | escape }}">
        <defs><linearGradient id="ttg-slot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16325A"/><stop offset=".62" stop-color="#2A4F84"/><stop offset=".62" stop-color="#18325A"/><stop offset="1" stop-color="#10264A"/></linearGradient></defs>
        <rect width="1600" height="1000" fill="url(#ttg-slot)"/>
        <g fill="#F5EEDF" opacity=".55"><circle cx="220" cy="140" r="2"/><circle cx="480" cy="90" r="1.5"/><circle cx="760" cy="180" r="1.8"/><circle cx="900" cy="70" r="1.4"/><circle cx="1420" cy="120" r="1.6"/><circle cx="1300" cy="260" r="1.3"/><circle cx="640" cy="300" r="1.2"/></g>
        <g transform="translate(1080 170) scale(1.6)" fill="#F5EEDF">{%- render 'tt-logo', variant: 'maan-simpel-pad' -%}</g>
        <g stroke="#F5EEDF" stroke-linecap="round" opacity=".3"><path d="M1150 660h220M1180 700h160M1210 740h100M1235 780h50" stroke-width="5"/></g>
        <g fill="none" stroke="#C4DAF0" stroke-width="4" stroke-linecap="round" opacity=".3"><path d="M120 720c30 0 30-12 60-12s30 12 60 12 30-12 60-12M520 800c30 0 30-12 60-12s30 12 60 12 30-12 60-12 30 12 60 12M260 900c30 0 30-12 60-12s30 12 60 12"/></g>
      </svg>
    {%- endif -%}
  </div>
  <div class="tt-wrap tt-slot__binnen">
    {%- render 'tt-kop', text: section.settings.heading, tag: 'h2', class: 'tt-kop--xl' -%}
    {%- if section.settings.text != blank -%}<p class="tt-lead tt-in">{{ section.settings.text }}</p>{%- endif -%}
    <div class="tt-knoppen tt-in">
      <a class="tt-knop tt-knop--licht" href="{{ section.settings.btn_link | default: routes.all_products_collection_url }}">{{ section.settings.btn_label }}<span aria-hidden="true">→</span></a>
    </div>
  </div>
  <div class="tt-slot__zegel" data-tt-draai="0.1">{% render 'tt-logo', variant: 'zegel' %}</div>
</section>
""", {
    "name": "TT: slot", "tag": "div",
    "settings": [
        {"type": "text", "id": "heading", "label": "Kop", "info": KOP_INFO, "default": "Pak je tas.|*De zee wacht.*"},
        {"type": "textarea", "id": "text", "label": "Tekst", "default": "Voor wie vroeg opstaat, de natuur in trekt en de gebaande paden verlaat voor die ene lege golf."},
        {"type": "text", "id": "btn_label", "label": "Knop", "default": "Bekijk de tas"},
        {"type": "url", "id": "btn_link", "label": "Knop-link"},
    ] + beeld('', 'Achtergrond', 'nacht', 'tide-tode-nachtzee.jpg', 'De zee bij maanlicht'),
    "presets": [{"name": "TT: slot"}]})
print('secties geschreven')
