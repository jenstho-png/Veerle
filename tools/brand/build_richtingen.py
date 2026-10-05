"""Bouwt docs/brandbook/logorichtingen.html: vier logorichtingen naast elkaar, elk als complete familie."""
import json, pathlib
hier = pathlib.Path(__file__).parent
R = json.load(open(hier / 'richtingen.json'))
A = json.load(open(hier / 'logo.json'))


def nul(vb):
    x, y, w, h = vb.split()
    return f'0 0 {w} {h}'


def use(sym, vb, cls='', style='', label=''):
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    c = f' class="{cls}"' if cls else ''
    st = f' style="{style}"' if style else ''
    return f'<svg viewBox="{nul(vb)}"{c}{st} {aria}><use href="#{sym}"/></svg>'


# ---------- richtingen in één vorm ----------
D = {
    'A': dict(naam='De maan', sub='De maan draagt het getij', font='Fraunces Italic', css="font-family:'Fraunces',Georgia,serif;font-style:italic;font-weight:500;font-variation-settings:'SOFT' 100,'WONK' 1,'opsz' 144;letter-spacing:-.01em",
              merkVB='0 0 200 200', woordVB=A['woord']['viewBox'], monoVB='0 0 200 200', merkW=86,
              tag='Van riders, voor riders', kleuren=('#1F3F6B', '#F5EEDF', '#F2D06B', '#C4DAF0'),
              verhaal='Tide betekent getij, en het getij bestaat omdat de maan aan de zee trekt. De maan draagt het water, Tide-Tode draagt je board. Tussen de woorden staat een getekend golfje.',
              past='Luxe, warm en eigen. Het verhaal is sterk, maar je moet het even kennen om het te snappen.'),
    'B': dict(naam='Handen vrij', sub='Het board met draagbanden', font='Archivo Expanded ExtraBold', css="font-family:'Archivo',system-ui,sans-serif;font-weight:800;font-stretch:125%;text-transform:uppercase;letter-spacing:.01em",
              merkVB=R['B']['merkVB'], woordVB=R['B']['woordVB'], monoVB=R['B']['monoVB'], merkW=78,
              tag='Handen vrij', kleuren=('#1F3F6B', '#F5EEDF', '#EE7B4F', '#3D6FB6'),
              verhaal='Veerles probleem in één beeld: een board met twee draagbanden en een schouderband. Het monogram is een TT waarvan de dwarsbalk één doorlopende band is, net als de draagband van de tas.',
              past='Stoer, no-nonsense en direct duidelijk wat je koopt. Het minst luxe van de vier, wel het meest herkenbaar als product.'),
    'C': dict(naam='De weg naar de spot', sub='Voetstappen die een golf worden', font='Caprasimo', css="font-family:'Caprasimo',Georgia,serif;font-weight:400;letter-spacing:0",
              merkVB=R['C']['merkVB'], woordVB=R['C']['woordVB'], monoVB=R['C']['monoVB'], merkW=92,
              tag='Van de hike naar de golf', kleuren=('#1F3F6B', '#F2BDBD', '#EE7B4F', '#F2D06B'),
              verhaal='Veerles verhaal begint niet bij de golf, maar bij de weg ernaartoe: de hike, de duinen, het pad over de rotsen. Drie stappen in het zand die eindigen in een golf, uit papier geknipt.',
              past='Avontuurlijk, warm en vrolijk, met de meeste vrouwelijke touch. Het speelst, en klein minder strak.'),
    'D': dict(naam='Het golfje', sub='Het teken uit de naam', font='Gilda Display', css="font-family:'Gilda Display',Georgia,serif;font-weight:400;text-transform:uppercase;letter-spacing:.14em",
              merkVB=R['D']['merkVB'], woordVB=R['D']['woordVB'], monoVB=R['D']['monoVB'], merkW=90,
              tag='Draagtassen voor surfers', kleuren=('#1F3F6B', '#F5EEDF', '#C4DAF0', '#F2D06B'),
              verhaal='Alleen het golfje dat Tide en Tode verbindt, dik en dun als met een penseel. Een fijne serif met veel lucht tussen de letters. Rust en fineline, precies waar Veerle om vroeg.',
              past='Het rustigst en het meest luxe. Minder stoer en avontuurlijk; het verhaal zit vooral in de naam.'),
}

# ---------- symbolen ----------
sym = []
sym.append(f'<mask id="m-gravure" maskUnits="userSpaceOnUse" x="0" y="0" width="200" height="200"><rect width="200" height="200" fill="#fff"/><path d="{A["gravure"]}" fill="none" stroke="#000" stroke-width="1.6"/></mask>')
sym.append(f'<symbol id="A-merk" viewBox="0 0 200 200"><path d="{A["sikkel"]}" fill="currentColor" mask="url(#m-gravure)"/><path d="{A["golfjes"]}" fill="currentColor"/></symbol>')
sym.append(f'<symbol id="A-mono" viewBox="0 0 200 200"><path d="{A["sikkel"]}" fill="currentColor"/><path d="{A["golfjes"]}" fill="currentColor"/></symbol>')
sym.append(f'<symbol id="A-woord" viewBox="{A["woord"]["viewBox"]}"><path d="{A["woord"]["d"]}" fill="currentColor"/></symbol>')
z = A['zegel']
sym.append(f'<symbol id="A-zegel" viewBox="0 0 200 200"><circle cx="100" cy="100" r="97" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="100" cy="100" r="62" fill="none" stroke="currentColor"/><path d="{z["boven"]}{z["onder"]}{z["tilde"]}" fill="currentColor"/><use href="#A-merk" x="56" y="56" width="88" height="88"/></symbol>')
for k in 'BCD':
    r = R[k]
    sym.append(f'<symbol id="{k}-merk" viewBox="{r["merkVB"]}"><path d="{r["merk"]}" fill="currentColor" fill-rule="evenodd"/></symbol>')
    sym.append(f'<symbol id="{k}-woord" viewBox="{r["woordVB"]}"><path d="{r["woord"]}" fill="currentColor"/></symbol>')
    sym.append(f'<symbol id="{k}-mono" viewBox="{r["monoVB"]}"><path d="{r["mono"]}" fill="currentColor" fill-rule="evenodd"/></symbol>')
    mx, my, mw, mh = [float(v) for v in r['merkVB'].split()]
    sc = 76 / max(mw, mh)
    w, h = mw * sc, mh * sc
    sym.append(f'<symbol id="{k}-zegel" viewBox="0 0 200 200"><circle cx="100" cy="100" r="97" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="100" cy="100" r="60" fill="none" stroke="currentColor"/><path d="{r["zegelBoven"]}{r["zegelOnder"]}" fill="currentColor"/><circle cx="18" cy="100" r="2.4" fill="currentColor"/><circle cx="182" cy="100" r="2.4" fill="currentColor"/><svg x="{100 - w / 2:.1f}" y="{100 - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" viewBox="{r["merkVB"]}"><path d="{r["merk"]}" fill="currentColor" fill-rule="evenodd"/></svg></symbol>')


def label(k):
    d = D[k]
    hoofd, licht, warm, zacht = d['kleuren']
    W = lambda style: use(f'{k}-woord', d['woordVB'], style=style)
    if k == 'A':  # hanglabel
        return (f'<svg viewBox="0 0 240 320" class="label-svg" aria-label="Hanglabel" role="img"><rect width="240" height="320" rx="26" fill="{warm}"/><circle cx="120" cy="30" r="10" fill="var(--tegel)"/>'
                f'<svg x="70" y="70" width="100" height="100" viewBox="0 0 200 200" style="color:{hoofd}"><use href="#A-merk"/></svg>'
                f'<svg x="34" y="210" width="172" height="40" viewBox="{nul(d["woordVB"])}" style="color:{hoofd}"><use href="#A-woord"/></svg></svg>')
    if k == 'B':  # geweven label
        return (f'<svg viewBox="0 0 320 120" class="label-svg" role="img" aria-label="Geweven label"><path d="M0 10h14v100H0zM306 10h14v100h-14z" fill="#132b4b"/><rect x="10" y="4" width="300" height="112" rx="4" fill="{hoofd}"/>'
                f'<rect x="20" y="14" width="280" height="92" rx="2" fill="none" stroke="{licht}" stroke-width="1.2" stroke-dasharray="4 4" opacity=".6"/>'
                f'<svg x="42" y="38" width="236" height="28" viewBox="{nul(d["woordVB"])}" style="color:{licht}"><use href="#B-woord"/></svg>'
                f'<text x="160" y="88" text-anchor="middle" font-family="Inter,sans-serif" font-weight="600" font-size="9" letter-spacing="3.4" fill="{warm}">HANDEN VRIJ</text></svg>')
    if k == 'C':  # bagagelabel
        return (f'<svg viewBox="0 0 320 170" class="label-svg" role="img" aria-label="Bagagelabel"><path d="M8 40 C30 10 40 30 30 60" fill="none" stroke="{hoofd}" stroke-width="2"/><path d="M40 20h260a12 12 0 0 1 12 12v106a12 12 0 0 1-12 12H40L12 122V48z" fill="{warm}"/><circle cx="34" cy="85" r="7" fill="var(--tegel)"/><circle cx="34" cy="85" r="10" fill="none" stroke="{licht}" stroke-width="3"/>'
                f'<svg x="58" y="40" width="80" height="80" viewBox="{d["merkVB"]}" style="color:{licht}"><use href="#C-merk"/></svg>'
                f'<svg x="148" y="52" width="148" height="36" viewBox="{nul(d["woordVB"])}" style="color:{licht}"><use href="#C-woord"/></svg>'
                f'<text x="150" y="112" font-family="Inter,sans-serif" font-weight="600" font-size="8" letter-spacing="2.4" fill="{licht}">VAN DE HIKE NAAR DE GOLF</text></svg>')
    return (f'<svg viewBox="0 0 170 300" class="label-svg" role="img" aria-label="Smalle kaart"><rect width="170" height="300" rx="6" fill="{licht}"/><rect x="10" y="10" width="150" height="280" rx="3" fill="none" stroke="{hoofd}" stroke-width=".8"/>'
            f'<svg x="40" y="44" width="90" height="34" viewBox="{nul(d["monoVB"])}" style="color:{hoofd}"><use href="#D-mono"/></svg>'
            f'<svg x="55" y="138" width="60" height="30" viewBox="{d["merkVB"]}" style="color:{hoofd}"><use href="#D-merk"/></svg>'
            f'<svg x="24" y="226" width="122" height="16" viewBox="{nul(d["woordVB"])}" style="color:{hoofd}"><use href="#D-woord"/></svg>'
            f'<text x="85" y="262" text-anchor="middle" font-family="Inter,sans-serif" font-weight="600" font-size="6" letter-spacing="2" fill="{hoofd}">DRAAGTASSEN VOOR SURFERS</text></svg>')


def familie(k):
    d = D[k]
    hoofd, licht, warm, zacht = d['kleuren']
    merk = lambda w, kleur, extra='': f'<svg viewBox="{nul(d["merkVB"])}" style="width:{w}px;color:{kleur}{extra}" aria-hidden="true"><use href="#{k}-merk"/></svg>'
    mono_w = 90 if d['monoVB'] in ('0 0 100 100', '0 0 200 200') else 150
    woord = lambda w, kleur: f'<svg viewBox="{nul(d["woordVB"])}" style="width:min({w}px,90%);color:{kleur}" role="img" aria-label="Tide-Tode"><use href="#{k}-woord"/></svg>'
    tegels = [
        ('Hoofdlogo', 'website, tas, verpakking', licht, f'<div class="staand">{merk(d["merkW"], hoofd)}{woord(260, hoofd)}<p class="tagline" style="color:{hoofd}">{d["tag"]}</p></div>'),
        ('Liggend', 'header, mail, smalle plekken', hoofd, f'<div class="liggend">{merk(round(d["merkW"] * .62), licht)}<span class="streep" style="background:{licht}"></span>{woord(210, licht)}</div>'),
        ('Woordmerk', 'als het beeldmerk al ergens staat', zacht, woord(270, hoofd)),
        ('Beeldmerk', 'avatar, borduursel, stempel', warm, merk(round(d["merkW"] * 1.35), hoofd if warm != hoofd else licht)),
        ('Monogram', 'favicon, knoop, kleine labels', hoofd, f'<svg viewBox="{nul(d["monoVB"])}" style="width:{mono_w}px;color:{licht}" aria-hidden="true"><use href="#{k}-mono"/></svg>'),
        ('Zegel', 'stickers, hanglabel, verpakking', licht, f'<svg viewBox="0 0 200 200" style="width:180px;color:{hoofd}" role="img" aria-label="Zegel"><use href="#{k}-zegel"/></svg>'),
    ]
    html = ''
    for naam, waar, bg, inhoud in tegels:
        html += f'<figure><div class="tegel korrel" style="background:{bg}">{inhoud}</div><figcaption><b>{naam}</b>{waar}</figcaption></figure>'
    html += f'<figure><div class="tegel korrel" style="background:var(--kaart);--tegel:var(--kaart)">{label(k)}</div><figcaption><b>Label</b>de kant die je vasthoudt</figcaption></figure>'
    # toepassing: header + avatar
    html += (f'<figure class="breed"><div class="tegel korrel toepassing" style="background:{zacht}">'
             f'<div class="nav"><div class="liggend klein">{merk(30, hoofd)}{woord(120, hoofd)}</div><span>Shop · Ons verhaal · FAQ</span><i style="background:{hoofd};color:{licht}">Bekijk de tas</i></div>'
             f'<div class="avatar" style="background:{hoofd}"><svg viewBox="{nul(d["monoVB"])}" style="width:58%;color:{licht}" aria-hidden="true"><use href="#{k}-mono"/></svg></div>'
             f'<div class="sticker" style="background:{warm};color:{hoofd if warm != hoofd else licht}"><svg viewBox="0 0 200 200" aria-hidden="true"><use href="#{k}-zegel"/></svg></div>'
             f'</div><figcaption><b>Samen</b>website-header, Instagram-profielfoto en sticker: steeds een andere kant van hetzelfde merk</figcaption></figure>')
    return html


secties = ''
kaartjes = ''
for k, d in D.items():
    hoofd, licht, warm, zacht = d['kleuren']
    mw_klein, mw_groot = round(d["merkW"] * .7), round(d["merkW"] * 1.5)
    tag_kleur = licht
    merk_k = use(f"{k}-merk", d["merkVB"], style=f"width:{mw_klein}px;color:{hoofd}")
    woord_k = use(f"{k}-woord", d["woordVB"], style=f"width:min(200px,86%);color:{hoofd}")
    merk_g = use(f"{k}-merk", d["merkVB"], style=f"width:{mw_groot}px;color:{licht}")
    woord_g = use(f"{k}-woord", d["woordVB"], style=f"width:min(560px,88%);color:{licht}", label="Tide-Tode")
    kaart_bg = licht if k != "C" else zacht
    kaartjes += (f'<a class="keuze korrel" href="#r-{k}" style="background:{kaart_bg}"><span class="letter">{k}</span>'
                 f'<div class="staand">{merk_k}{woord_k}</div>'
                 f'<b>{d["naam"]}</b><span class="klein">{d["font"]}</span></a>')
    secties += f'''
  <section id="r-{k}" class="richting">
    <div class="r-kop">
      <p class="label">Richting {k} · {d["font"]}</p>
      <h2 style="{d["css"]}">{d["naam"]}</h2>
      <p class="sub">{d["sub"]}</p>
      <p class="lead">{d["verhaal"]}</p>
      <p class="past"><b>Past bij Veerle:</b> {d["past"]}</p>
    </div>
    <div class="held korrel" style="background:{hoofd}">
      <div class="staand groot">{merk_g}{woord_g}<p class="tagline" style="color:{tag_kleur};opacity:.78">{d["tag"]}</p></div>
    </div>
    <div class="familie">{familie(k)}</div>
  </section>'''

vergelijk_rijen = [
    ('Eerste indruk', 'Luxe en warm', 'Stoer en sportief', 'Vrolijk en avontuurlijk', 'Rustig en chic'),
    ('Sluit aan bij', '"Kwalitatief", "rust"', '"No-nonsense", "stoer"', '"Avontuurlijk", vrouwelijke touch', '"Rust", "fineline", "kwalitatief"'),
    ('Zie je het product?', 'Nee, via het verhaal', 'Ja, meteen', 'Half: de weg ernaartoe', 'Nee, via de naam'),
    ('Klein leesbaar (favicon)', 'Goed', 'Heel goed', 'Matig', 'Goed'),
    ('Op tas en stof', 'Mooi geborduurd', 'Sterk als patch', 'Leuk als print', 'Chic als geweven label'),
]
tabel = '<table><thead><tr><th></th>' + ''.join(f'<th>{k} · {D[k]["naam"]}</th>' for k in D) + '</tr></thead><tbody>'
for rij in vergelijk_rijen:
    tabel += f'<tr><th>{rij[0]}</th>' + ''.join(f'<td>{c}</td>' for c in rij[1:]) + '</tr>'
tabel += '</tbody></table>'

html = f'''<title>Tide-Tode Logorichtingen</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Caprasimo&family=Gilda+Display&family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..700,0..100,0..1;1,9..144,300..700,0..100,0..1&family=Inter:wght@400;500;600&display=swap">
<style>
  /* Layout: vier logorichtingen als hoofdstukken; elk eerst een groot vlak, dan de logofamilie in tegels. */
  :root {{
    color-scheme: light;
    --creme: #F5EEDF; --deep: #1F3F6B; --ink: #18325A; --captain: #3D6FB6; --baby: #C4DAF0;
    --poppy: #EE7B4F; --rose: #F2BDBD; --sunshine: #F2D06B; --zacht: #4C5F7E; --lijn: rgba(24, 50, 90, .16); --kaart: #FBF7EF;
    --f-display: 'Fraunces', Georgia, serif; --f-tekst: 'Inter', system-ui, sans-serif;
    --sh: 0 24px 50px -22px rgba(24, 50, 90, .32), 0 0 0 1px var(--lijn);
    --korrel: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .6 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  }}
  * {{ box-sizing: border-box; }}
  body {{ background: var(--creme); color: var(--ink); font: 400 16px/1.6 var(--f-tekst); padding-inline: clamp(16px, 3.5vw, 40px); -webkit-font-smoothing: antialiased; }}
  body::before {{ content: ''; position: fixed; inset: 0; background-image: var(--korrel); opacity: .13; mix-blend-mode: multiply; pointer-events: none; z-index: 50; }}
  .wrap {{ max-width: 1200px; margin-inline: auto; }}
  h1, h2, h3 {{ margin: 0; color: var(--deep); text-wrap: balance; }}
  p {{ margin: 0; }}
  svg {{ display: block; }}
  .korrel {{ position: relative; isolation: isolate; }}
  .korrel::after {{ content: ''; position: absolute; inset: 0; background-image: var(--korrel); opacity: .26; mix-blend-mode: multiply; pointer-events: none; border-radius: inherit; z-index: 3; }}
  .label {{ font: 600 11px/1 var(--f-tekst); letter-spacing: .22em; text-transform: uppercase; color: var(--captain); }}
  .lead {{ font-size: clamp(16px, 1.4vw, 18px); color: var(--zacht); max-width: 62ch; }}
  .klein {{ font-size: 13px; color: var(--zacht); }}
  .tagline {{ font: 600 10.5px/1 var(--f-tekst); letter-spacing: .3em; text-transform: uppercase; white-space: nowrap; }}
  .tegel .tagline {{ font-size: 9px; letter-spacing: .24em; }}
  :focus-visible {{ outline: 2px solid var(--poppy); outline-offset: 3px; }}

  header.intro {{ padding-block: clamp(48px, 8vw, 96px) 40px; display: grid; gap: 22px; }}
  header.intro h1 {{ font: 400 clamp(40px, 6.4vw, 78px)/1 var(--f-display); font-variation-settings: 'SOFT' 100, 'opsz' 144; letter-spacing: -0.025em; }}
  header.intro h1 em {{ font-style: italic; font-variation-settings: 'SOFT' 100, 'WONK' 1, 'opsz' 144; color: var(--captain); }}
  .rollen {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 160px), 1fr)); margin-top: 10px; }}
  .rollen div {{ background: var(--kaart); border-radius: 16px; box-shadow: var(--sh); padding: 14px 16px; font-size: 13px; color: var(--zacht); }}
  .rollen b {{ display: block; color: var(--deep); font: 500 17px/1.2 var(--f-display); font-variation-settings: 'SOFT' 100; margin-bottom: 4px; }}

  .keuzes {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr)); padding-bottom: 32px; }}
  .keuze {{ border-radius: 22px; padding: 26px 20px 20px; display: grid; gap: 8px; justify-items: center; text-align: center; text-decoration: none; color: var(--deep); box-shadow: var(--sh); transition: transform .35s cubic-bezier(.16,1,.3,1); }}
  .keuze:hover {{ transform: translateY(-4px); }}
  .keuze .letter {{ justify-self: start; font: 600 11px/1 var(--f-tekst); letter-spacing: .2em; color: var(--captain); position: relative; z-index: 4; }}
  .keuze .staand {{ min-height: 150px; align-content: center; }}
  .keuze b {{ font: 500 20px/1.2 var(--f-display); font-variation-settings: 'SOFT' 100; position: relative; z-index: 4; }}
  .keuze .klein {{ position: relative; z-index: 4; }}

  .staand {{ display: grid; justify-items: center; gap: 14px; width: 100%; position: relative; z-index: 4; }}
  .staand.groot {{ gap: 22px; }}
  .liggend {{ display: flex; align-items: center; justify-content: center; gap: 14px; width: 100%; position: relative; z-index: 4; }}
  .liggend .streep {{ width: 1.5px; height: 34px; opacity: .5; }}
  .liggend.klein {{ gap: 8px; width: auto; justify-content: flex-start; }}

  .richting {{ padding-block: clamp(56px, 8vw, 104px); border-top: 1px solid var(--lijn); }}
  .r-kop {{ display: grid; gap: 14px; margin-bottom: 32px; }}
  .r-kop h2 {{ font-size: clamp(40px, 6vw, 72px); line-height: 1; }}
  .r-kop .sub {{ font: italic 400 22px/1.2 var(--f-display); font-variation-settings: 'SOFT' 100, 'WONK' 1; color: var(--captain); }}
  .r-kop .past {{ font-size: 15px; max-width: 62ch; padding: 14px 18px; background: var(--kaart); border-radius: 16px; box-shadow: var(--sh); }}
  .r-kop .past b {{ color: var(--deep); }}
  .held {{ border-radius: 36px; min-height: clamp(320px, 42vw, 480px); display: grid; place-items: center; padding: clamp(32px, 6vw, 72px) 20px; margin-bottom: 14px; }}
  .familie {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); }}
  figure {{ margin: 0; display: grid; gap: 8px; min-width: 0; align-content: start; }}
  figure.breed {{ grid-column: 1 / -1; }}
  figcaption {{ font-size: 13px; color: var(--zacht); display: flex; gap: 10px; flex-wrap: wrap; align-items: baseline; }}
  figcaption b {{ font: 500 16px/1.2 var(--f-display); font-variation-settings: 'SOFT' 100; color: var(--deep); }}
  .tegel {{ border-radius: 22px; min-height: 240px; display: grid; place-items: center; padding: 26px; overflow: hidden; }}
  .tegel > svg, .tegel > div {{ position: relative; z-index: 4; }}
  .label-svg {{ width: min(240px, 90%); filter: drop-shadow(0 18px 22px rgba(24, 50, 90, .28)); transform: rotate(-3deg); }}
  .toepassing {{ grid-template-columns: 1fr; gap: 18px; justify-items: center; }}
  .toepassing .nav {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; width: min(720px, 100%); background: var(--kaart); border-radius: 999px; padding: 10px 10px 10px 18px; box-shadow: var(--sh); }}
  .toepassing .nav span {{ font-size: 12px; color: var(--zacht); display: none; }}
  .toepassing .nav i {{ font-style: normal; font-size: 12px; font-weight: 600; padding: 9px 14px; border-radius: 999px; white-space: nowrap; }}
  .toepassing .avatar {{ width: 110px; aspect-ratio: 1; border-radius: 50%; display: grid; place-items: center; box-shadow: var(--sh); }}
  .toepassing .sticker {{ width: 130px; aspect-ratio: 1; border-radius: 50%; display: grid; place-items: center; transform: rotate(8deg); box-shadow: 0 16px 26px -14px rgba(0,0,0,.4); }}
  .toepassing .sticker svg {{ width: 86%; }}
  @media (min-width: 760px) {{
    .toepassing {{ grid-template-columns: 1fr auto auto; }}
    .toepassing .nav span {{ display: inline; }}
  }}

  .vergelijk {{ padding-block: clamp(56px, 8vw, 104px); border-top: 1px solid var(--lijn); display: grid; gap: 24px; }}
  .vergelijk h2, .advies h2 {{ font: 400 clamp(34px, 5vw, 58px)/1 var(--f-display); font-variation-settings: 'SOFT' 100, 'opsz' 144; letter-spacing: -0.02em; }}
  .tabel {{ overflow-x: auto; border-radius: 20px; box-shadow: var(--sh); background: var(--kaart); }}
  table {{ width: 100%; border-collapse: collapse; min-width: 720px; font-size: 14px; }}
  th, td {{ text-align: left; padding: 14px 16px; border-bottom: 1px solid var(--lijn); vertical-align: top; }}
  thead th {{ font: 500 16px/1.2 var(--f-display); font-variation-settings: 'SOFT' 100; color: var(--deep); background: var(--creme); }}
  tbody th {{ font-weight: 600; color: var(--deep); width: 18%; }}
  td {{ color: var(--zacht); }}
  .advies {{ margin-bottom: 48px; border-radius: 36px; background: var(--deep); color: var(--creme); padding: clamp(28px, 5vw, 64px); display: grid; gap: 18px; }}
  .advies h2 {{ color: var(--creme); }}
  .advies p {{ color: rgba(245, 238, 223, .85); max-width: 66ch; }}
  .advies .label {{ color: var(--baby); }}
</style>

<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
{chr(10).join(sym)}
</defs></svg>

<div class="wrap">
  <header class="intro">
    <p class="label">Tide-Tode · logorichtingen · oktober 2026</p>
    <h1>Eén merk, <em>vier</em> mogelijke gezichten</h1>
    <p class="lead">Hieronder staan vier richtingen voor het logo, elk met een eigen beeldmerk en lettertype. Kleuren, toon en iconen blijven hetzelfde. Elke richting is een complete familie: één merk dat zich steeds van een andere kant laat zien, afhankelijk van waar het staat.</p>
    <div class="rollen">
      <div><b>Hoofdlogo</b>beeldmerk, naam en regel samen</div>
      <div><b>Liggend</b>voor smalle, brede plekken</div>
      <div><b>Woordmerk</b>alleen de naam</div>
      <div><b>Beeldmerk</b>alleen het teken</div>
      <div><b>Monogram</b>voor heel klein</div>
      <div><b>Zegel</b>de ronde stempel</div>
      <div><b>Label</b>wat je aan de tas hangt</div>
    </div>
  </header>
  <nav class="keuzes" aria-label="Richtingen">{kaartjes}</nav>
  {secties}
  <section class="vergelijk">
    <p class="label">Naast elkaar</p>
    <h2>Welke past het best?</h2>
    <div class="tabel">{tabel}</div>
  </section>
  <section class="advies korrel">
    <p class="label">Mijn advies</p>
    <h2>D als basis, met de stoerheid van B</h2>
    <p>Veerle vroeg letterlijk om rust, fineline en kwaliteit, en het golfje staat al in de naam. Daarom past richting D het best als hoofdlogo. Het TT-monogram uit richting B kan erbij als stoere kant voor op de tas en de patches. Wil ze meer avontuur en vrolijkheid, dan is C de warmste keuze. De maan (A) blijft mooi, maar vraagt het meeste uitleg.</p>
    <p>Kies samen één richting. Daarna werk ik die volledig uit in het brand book en zet ik hem op de website.</p>
  </section>
</div>
'''
out = hier.parent.parent / 'docs' / 'brandbook' / 'logorichtingen.html'
out.write_text(html)
print(out, len(html) // 1024, 'KB')
