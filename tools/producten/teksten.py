"""Unieke productteksten per product. De eerste alinea is de korte pitch naast de koopknop,
de rest staat op de productpagina in de uitklapblokken. Geen beloftes die we niet waar kunnen maken."""

TAS_BASIS = ('<h3>Zo werkt hij</h3><p>Leg de tas om het midden van je board, op het balanspunt. Trek de band aan, hang de lus over je schouder en loop. '
             'Op het strand haal je hem er in een paar tellen weer af.</p>'
             '<h3>Details</h3><ul><li>Eén maat voor softtops en hardboards, tot ongeveer 9\'6"</li>'
             '<li>Stevige nylon band, fijn geweven zodat hij zacht in je hand ligt</li>'
             '<li>De band loopt in één stuk rondom de tas, met ons logo erin geweven</li>'
             '<li>Geweven Tide Tode label op het paneel</li>'
             '<li>Je natte, zanderige board mag er gewoon in</li></ul>'
             '<h3>Materiaal en onderhoud</h3><ul><li>Zware geweven stof met sterke stiksels</li>'
             '<li>Spoel zout en zand eruit met zoet water en laat hem aan de lucht drogen</li>'
             '<li>Gaat er iets stuk? Stuur ons een bericht, dan repareren we hem</li></ul>')

TASSEN = {
    'draagtas-tegel': ('Het origineel. Een patchwork van geweven tegels in rood, terracotta, blauw, groen en crème, met een band in stoffig blauw.',
                       'Dit is de stof waar Tide Tode mee begon. De tegels doen denken aan de mozaïeken die je ziet in kustplaatsen in Portugal en Spanje. Omdat het patroon over de hele rol loopt, valt het op elke tas net iets anders.'),
    'draagtas-tegel-navy': ('Onze tegels in een rustige versie: navy, baby blue en crème, met een navy band.',
                            'Dezelfde tegelvorm als het origineel, maar dan in de kleuren van de Noordzee op een heldere dag. Rustig genoeg voor elk board, en vuil zie je er nauwelijks op.'),
    'draagtas-golfjes': ('Baby blue golfjes op navy, met een lichtblauwe band.',
                         'Een eenvoudig golfpatroon dat je van ver herkent. Het donkere navy houdt zand en vlekken goed verborgen.'),
    'draagtas-zonsondergang': ('Brede strepen in rose, zand, terracotta en crème, met een terracotta band.',
                               'De kleuren van de lucht na een avondsessie. De warmste van de negen, en mooi op een licht board.'),
    'draagtas-schelp': ('Een schelpenpatroon in zacht rose en crème, met een rose band.',
                        'Geïnspireerd op de schelpen die je na een storm op het strand vindt. Zacht van kleur en toch duidelijk aanwezig op je board.'),
    'draagtas-ruit': ('Een ruitje in baby blue en crème, met een navy band.',
                      'Een klassieke ruit, zoals op een oude strandstoel. Fris naast een wit of crème board.'),
    'draagtas-duin': ('Schuine strepen in zand en crème, met een terracotta band.',
                      'De kleuren van de duinen op weg naar de spot. Licht en rustig, met de terracotta band als accent.'),
    'draagtas-salie': ('Tegels in saliegroen, zand en crème, met een navy band.',
                       'Het tegelpatroon in groene tinten, zoals helmgras in de duinen. Past bij een board in een natuurlijke kleur.'),
    'draagtas-navy': ('Effen navy met een fijne streep in de stof en een band in stoffig blauw.',
                      'Voor wie het liefst geen patroon heeft. Strak, donker en tijdloos. Het geweven label is hier het enige accent.'),
}

KLEDING_MAAT_TEE = ('<h3>Maat en pasvorm</h3><ul><li>Ruime, rechte pasvorm</li><li>Twijfel je tussen twee maten, kies dan je normale maat</li>'
                    '<li>Alle maten staan in de <a href="/pages/maatwijzer">maatwijzer</a></li></ul>'
                    '<h3>Materiaal en onderhoud</h3><ul><li>100% biologisch katoen, zwaar en stevig</li><li>Print met inkt op waterbasis, zacht aan te voelen</li>'
                    '<li>Binnenstebuiten wassen op 30 graden en niet in de droger</li></ul>')
KLEDING_MAAT_TRUI = ('<h3>Maat en pasvorm</h3><ul><li>Ruime pasvorm met boorden aan de mouwen</li>'
                     '<li>Alle maten staan in de <a href="/pages/maatwijzer">maatwijzer</a></li></ul>'
                     '<h3>Materiaal en onderhoud</h3><ul><li>Biologisch katoen, geruwd aan de binnenkant</li><li>Print met inkt op waterbasis</li>'
                     '<li>Binnenstebuiten wassen op 30 graden en niet in de droger</li></ul>')

KLEDING = {
    't-shirt-lijn-naar-zee': ('Zwaar crème T-shirt met op de rug de lijn naar zee: onze surfspots als haltes op één lijn, van Petten tot Domburg.',
                              '<h3>Het ontwerp</h3><p>Zes plekken langs de kust waar we graag het water in gaan, met hun coördinaten eronder, getekend als een lijn van haltes. Op de borst een klein board.</p>', KLEDING_MAAT_TEE),
    't-shirt-op-weg-naar-zee': ('Zwaar crème T-shirt met op de rug zeven keer OP WEG NAAR ZEE, de laatste regel in terracotta.',
                                '<h3>Het ontwerp</h3><p>Zes regels in omlijnde letters en de zevende vol in terracotta. Zo voelt de weg naar de spot: steeds dichterbij. Op de borst een klein board.</p>', KLEDING_MAAT_TEE),
    't-shirt-klassiek': ('Zwaar baby blue T-shirt met de klassieker op de rug: TIDE TODE in een boog boven ons board.',
                         '<h3>Het ontwerp</h3><p>Onze naam in een boog, het board eronder en NOORDZEE en SINDS 2025 in kleine letters. Gedrukt in één kleur navy. Op de borst een klein board.</p>', KLEDING_MAAT_TEE),
    't-shirt-board': ('Zwaar zandkleurig T-shirt met ons board groot op de rug en TIDE TODE langs de rail geschreven.',
                      '<h3>Het ontwerp</h3><p>Ons board met de twee golflijnen, zo groot als de rug het toelaat. De naam loopt langs de rand, zoals een shaper zijn naam op een board zet. Op de borst een klein board.</p>', KLEDING_MAAT_TEE),
    't-shirt-zon': ('Zwaar navy T-shirt met op de rug een grote zon, met TIDE TODE in een cirkel eromheen.',
                    '<h3>Het ontwerp</h3><p>Een zon met stralen, met onze naam drie keer rondom. Gedrukt in crème op navy. Op de borst een klein board.</p>', KLEDING_MAAT_TEE),
    't-shirt-golf': ('Zwaar roze T-shirt met op de rug ons board en onze golf, met TIDE TODE in een boog erboven.',
                     '<h3>Het ontwerp</h3><p>Het board en de golf uit ons beeldmerk, groot op de rug en gedrukt in één kleur navy. Op de borst een klein board.</p>', KLEDING_MAAT_TEE),
    'longsleeve-vin': ('Navy longsleeve met op de rug een grote surfvin en TIDE TODE langs de achterrand.',
                       '<h3>Het ontwerp</h3><p>De vorm van een surfvin, groot en in crème gedrukt. Onze naam volgt de bocht van de achterrand. Op de borst een klein board.</p>', KLEDING_MAAT_TRUI.replace('geruwd aan de binnenkant', '220 gram')),
    'longsleeve-zon': ('Crème longsleeve voor koele ochtenden, met op de rug de grote zon en TIDE TODE eromheen.',
                       '<h3>Het ontwerp</h3><p>Dezelfde zon als op het T-shirt, nu in navy op crème. Fijn onder een jas als je in het voorjaar naar de spot fietst. Op de borst een klein board.</p>', KLEDING_MAAT_TRUI.replace('geruwd aan de binnenkant', '220 gram')),
    'hoodie-twee-boards': ('Zware navy hoodie voor na het surfen, met op de rug twee boards en TIDE TODE in een boog eronder.',
                           '<h3>Het ontwerp</h3><p>Twee boards naast elkaar, in crème gedrukt. Met een buidelzak voor koude handen en een koord in de capuchon.</p>', KLEDING_MAAT_TRUI.replace('geruwd aan de binnenkant', '400 gram, geruwd aan de binnenkant')),
    'sweater-boards': ('Crème sweater met ronde hals, met op de rug twee boards zonder tekst.',
                       '<h3>Het ontwerp</h3><p>Alleen de twee boards, in navy op crème. Rustig genoeg om ook naar je werk te dragen. Op de borst een klein board.</p>', KLEDING_MAAT_TRUI.replace('geruwd aan de binnenkant', '350 gram, geruwd aan de binnenkant')),
    'uv-shirt-lange-mouw': ('Strak navy UV-shirt om in te surfen. Het beschermt je tegen de zon en tegen schuren van je board en wetsuit.',
                            '<h3>Details</h3><ul><li>UPF 50+</li><li>Platte naden, zodat niets schuurt</li><li>Tegelprint aan het eind van de mouwen en klein ons logo op de borst</li></ul>'
                            '<h3>Materiaal en onderhoud</h3><ul><li>Gerecycled polyamide met elastaan</li><li>Droogt snel</li><li>Spoel na het surfen uit met zoet water</li></ul>',
                            '<h3>Maat en pasvorm</h3><ul><li>Strak, zodat hij niet opbolt in het water</li><li>Maten XS tot XL, zie de <a href="/pages/maatwijzer">maatwijzer</a></li></ul>'),
    'surfponcho-tegel': ('Badstof poncho om je op het strand of naast de auto om te kleden, met een rand in onze tegelprint.',
                         '<h3>Details</h3><ul><li>Capuchon en korte, wijde mouwen</li><li>Geweven band in tegelprint en ons logo groot op de rug</li><li>Wordt opgevouwen geleverd</li><li>Eén maat, voor lengtes van 160 tot 195 cm</li></ul>',
                         '<h3>Materiaal en onderhoud</h3><ul><li>Katoenen badstof, 350 gram</li><li>Droogt snel aan de lucht</li><li>Wassen op 40 graden</li></ul>'),
}

OVERIG = {
    'pet-navy': '<p>Navy pet van katoen met ons board geborduurd op de voorkant.</p><h3>Details</h3><ul><li>Geborduurd board in crème</li><li>Verstelbaar aan de achterkant, één maat</li><li>Met onze klepsticker, die haal je eraf of laat je zitten</li></ul><h3>Onderhoud</h3><ul><li>Met de hand wassen in koud water</li></ul>',
    'bucket-hat-tegel': '<p>Crème bucket hat van gewassen katoen met ons board geborduurd op de voorkant.</p><h3>Details</h3><ul><li>Geborduurd board in navy</li><li>Brede rand tegen zon en wind</li><li>Eén maat</li></ul><h3>Onderhoud</h3><ul><li>Met de hand wassen in koud water</li></ul>',
    'canvas-tas': '<p>Stevige canvas tas met ons busje erop en OP WEG NAAR ZEE eronder. Voor je handdoek, wetsuit en lunch.</p><h3>Details</h3><ul><li>38 bij 42 cm</li><li>Lange hengsels, dus ook over je schouder</li><li>Print met inkt op waterbasis</li></ul><h3>Materiaal</h3><ul><li>Naturel katoenen canvas</li></ul>',
    'strandhanddoek-tegel': '<p>Grote strandhanddoek in de tegelprint van onze draagtas, met franjes aan de korte kanten.</p><h3>Details</h3><ul><li>90 bij 170 cm</li><li>Klein geweven Tide Tode label aan de zijkant</li><li>Zand schud je er zo uit</li></ul><h3>Materiaal en onderhoud</h3><ul><li>Katoen</li><li>Wassen op 40 graden</li></ul>',
    'stickerset': '<p>Een vel met zeven vinyl stickers in onze stijl.</p><h3>Wat erop staat</h3><ul><li>De zonsondergang en op weg naar zee</li><li>Een rond tegeltje en het vaantje van de surfclub</li><li>Een postzegel, de ruitjesband en ons board</li></ul><h3>Details</h3><ul><li>Waterbestendig, dus ook voor je board, fles of laptop</li></ul>',
    'waxkam': '<p>Kam en schraper in één, in terracotta met ons logo in het plastic gedrukt.</p><h3>Zo gebruik je hem</h3><ul><li>Met de tanden maak je oude wax weer ruw voor meer grip</li><li>Met de rechte kant haal je wax eraf als je opnieuw wilt beginnen</li></ul><h3>Details</h3><ul><li>Past in de zak van je boardshort</li></ul>',
    'karabijnhaak-messing': '<p>Karabijnhaak van messing met TIDE TODE in het metaal gegoten. Aan een D-ring hangt een lus van dezelfde band als onze draagtas, navy met het geweven logo.</p><h3>Details</h3><ul><li>Haak ongeveer 7 cm, lus 12 cm</li><li>Schroefsluiting, zodat hij niet zomaar opengaat</li><li>Voor je sleutels, een waterfles of je slippers aan je tas</li></ul><p>Niet geschikt om te klimmen.</p>',
    'karabijnhaak-zwart': '<p>Karabijnhaak in zwart metaal met TIDE TODE in het metaal gegoten. Aan een D-ring hangt een lus van dezelfde band als onze draagtas, in stoffig blauw met het geweven logo.</p><h3>Details</h3><ul><li>Haak ongeveer 7 cm, lus 12 cm</li><li>Schroefsluiting, zodat hij niet zomaar opengaat</li><li>Voor je sleutels, een waterfles of je slippers aan je tas</li></ul><p>Niet geschikt om te klimmen.</p>',
}

WAX_GEBRUIK = ('<h3>Zo gebruik je het</h3><ul><li>Begin met een schoon board</li><li>Wax in kleine rondjes en daarna in kruislijnen, tot er bobbeltjes ontstaan</li>'
               '<li>Wax alleen waar je staat en ligt</li><li>Maak oude wax weer ruw met een waxkam</li></ul>'
               '<h3>Details</h3><ul><li>70 gram</li><li>Bijenwas en kokosolie</li><li>In een papieren wikkel, zonder plastic</li></ul>')
WAX = {
    'surfwax-koud': '<p>Surfwax voor koud water, onder 14 graden. Voor de Noordzee in het voorjaar, najaar en de winter.</p><p>Koude wax is zachter, zodat hij ook in kou goed blijft plakken.</p>' + WAX_GEBRUIK,
    'surfwax-koel': '<p>Surfwax voor koel water, van 14 tot 19 graden. Voor de Noordzee in de zomer en de Atlantische kust.</p><p>De wax die je het vaakst nodig hebt in Nederland.</p>' + WAX_GEBRUIK,
    'surfwax-warm': '<p>Surfwax voor warm water, boven 19 graden. Voor Portugal in de zomer en verder weg.</p><p>Warme wax is harder, zodat hij niet smelt in de zon.</p>' + WAX_GEBRUIK,
}


def tekst_voor(handle):
    """Volledige productbeschrijving (zonder verzendregel), of None als we niets unieks hebben."""
    if handle in TASSEN:
        pitch, ontwerp = TASSEN[handle]
        return f'<p>{pitch}</p><h3>Het ontwerp</h3><p>{ontwerp}</p>' + TAS_BASIS
    if handle in KLEDING:
        pitch, ontwerp, rest = KLEDING[handle]
        return f'<p>{pitch}</p>{ontwerp}{rest}'
    return OVERIG.get(handle) or WAX.get(handle)
