/* Tide-Tode: beweging en kopen voor de tt-secties. Geen libraries.
   - Alles rekent in één requestAnimationFrame per scroll.
   - 'Minder beweging' of de thema-editor: alles staat meteen op de eindstand. */
(() => {
  const root = document.documentElement;
  const stil = matchMedia('(prefers-reduced-motion: reduce)').matches || !!(window.Shopify && window.Shopify.designMode);
  root.classList.add('tt-js');
  if (stil) root.classList.add('tt-stil');

  const klem = (v, a, b) => Math.max(a, Math.min(b, v));
  const geld = (c) => {
    try { return new Intl.NumberFormat(document.documentElement.lang || 'nl', { style: 'currency', currency: (window.Shopify && Shopify.currency && Shopify.currency.active) || 'EUR' }).format(c / 100); }
    catch (e) { return '€' + (c / 100).toFixed(2).replace('.', ','); }
  };

  function start(scope = document) {
    /* 1. In beeld komen */
    const doelen = scope.querySelectorAll('[data-tt-regels], .tt-onthul, .tt-in, .tt-stickerzee');
    if (stil || !('IntersectionObserver' in window)) {
      doelen.forEach((el) => el.classList.add('is-in'));
    } else {
      const io = new IntersectionObserver((items) => items.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      }), { rootMargin: '0px 0px -10% 0px', threshold: 0.01 });
      doelen.forEach((el) => io.observe(el));
    }

    /* 2. Tekst die volloopt: woorden splitsen */
    scope.querySelectorAll('[data-tt-vul]').forEach((p) => {
      if (p.dataset.ttKlaar) return;
      p.dataset.ttKlaar = '1';
      const frag = document.createDocumentFragment();
      p.textContent.split(/(\s+)/).forEach((w) => {
        if (!w) return;
        if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(w)); return; }
        const s = document.createElement('span'); s.className = 'tt-w'; s.textContent = w; frag.appendChild(s);
      });
      p.textContent = '';
      p.appendChild(frag);
    });

    /* 3. Kopen: varianten kiezen en de plakbalk */
    scope.querySelectorAll('[data-tt-koop]').forEach((sectie) => {
      const form = sectie.querySelector('[data-tt-form]');
      if (!form) return;
      const data = form.querySelector('[data-tt-varianten]');
      const id = form.querySelector('[data-tt-variant]');
      const knop = form.querySelector('[data-tt-koopknop]');
      const tekst = form.querySelector('[data-tt-knoptekst]');
      if (data) {
        const varianten = JSON.parse(data.textContent);
        form.addEventListener('change', () => {
          const gekozen = [...form.querySelectorAll('.tt-koop__optie')].map((f) => (f.querySelector('input:checked') || {}).value);
          const v = varianten.find((x) => x.options.every((o, i) => o === gekozen[i]));
          if (!v) { knop.disabled = true; tekst.textContent = 'Niet beschikbaar'; return; }
          id.value = v.id; knop.disabled = !v.available;
          tekst.textContent = v.available ? 'In winkelwagen' : 'Uitverkocht';
          sectie.querySelectorAll('.tt-koop__prijs span, .tt-balk__naam span').forEach((el) => { el.textContent = geld(v.price); });
        });
      }
      const galerij = sectie.querySelector('[data-tt-galerij]');
      const teller = sectie.querySelector('[data-tt-teller]');
      if (galerij && teller) {
        galerij.addEventListener('scroll', () => {
          const kind = galerij.firstElementChild;
          if (!kind) return;
          teller.textContent = String(Math.round(galerij.scrollLeft / (kind.offsetWidth + 8)) + 1);
        }, { passive: true });
      }
      const balk = sectie.querySelector('[data-tt-balk]');
      if (balk) {
        document.body.appendChild(balk);
        balk.querySelector('[data-tt-balkknop]').addEventListener('click', () => {
          if (form.requestSubmit) form.requestSubmit(knop); else knop.click();
        });
        let zichtbaar = false;
        const toon = () => {
          const r = sectie.getBoundingClientRect();
          const aan = r.bottom < 0 && document.documentElement.scrollHeight - scrollY - innerHeight > 600;
          if (aan !== zichtbaar) {
            zichtbaar = aan;
            balk.classList.toggle('is-aan', aan);
            balk.setAttribute('aria-hidden', String(!aan));
            balk.querySelector('button').tabIndex = aan ? 0 : -1;
          }
        };
        addEventListener('scroll', toon, { passive: true });
        toon();
      }
    });
  }

  /* 4. De maan van vanavond (eigen berekening, geen externe dienst) */
  const SYN = 29.530588853;
  const NIEUW = Date.UTC(2000, 0, 6, 18, 14);
  const dag = 86400000;
  function maan(datum) {
    const leeftijd = (((datum - NIEUW) / dag) % SYN + SYN) % SYN;
    const f = leeftijd / SYN;
    const licht = (1 - Math.cos(2 * Math.PI * f)) / 2;
    const namen = ['nieuwe maan', 'wassende sikkel', 'eerste kwartier', 'wassende maan', 'volle maan', 'afnemende maan', 'laatste kwartier', 'afnemende sikkel'];
    return { leeftijd, f, licht, naam: namen[Math.round(f * 8) % 8] };
  }
  function maanPad(f) {
    const rx = (48 * Math.abs(Math.cos(2 * Math.PI * f))).toFixed(2);
    const wassend = f < 0.5;
    const sikkel = f < 0.25 || f > 0.75;
    if (wassend) return `M50 2A48 48 0 0 1 50 98A${rx} 48 0 0 ${sikkel ? 0 : 1} 50 2Z`;
    return `M50 2A48 48 0 0 0 50 98A${rx} 48 0 0 ${sikkel ? 1 : 0} 50 2Z`;
  }
  function startMaan(scope) {
    scope.querySelectorAll('[data-tt-maanstand]').forEach((el) => {
      const nu = new Date();
      const vanavond = new Date(nu); vanavond.setHours(21, 0, 0, 0);
      const m = maan(vanavond);
      el.querySelector('.tt-maanstand__licht').setAttribute('d', maanPad(m.f));
      el.querySelector('[data-tt-maan-naam]').textContent = `${m.naam}, ${Math.round(m.licht * 100)}% verlicht`;
      const totVol = ((0.5 - m.f + 1) % 1) * SYN;
      const totNieuw = ((1 - m.f) % 1) * SYN;
      const dichtbij = Math.min(totVol, SYN - totVol, totNieuw, SYN - totNieuw);
      const fmt = (d) => d.toLocaleDateString('nl-NL', { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'Europe/Amsterdam' });
      el.querySelector('[data-tt-maan-info]').textContent = dichtbij <= 2
        ? 'Rond nieuwe en volle maan is het springtij: extra hoog en extra laag water. Check je getijdentabel voor je gaat.'
        : `Volgende volle maan: ${fmt(new Date(vanavond.getTime() + totVol * dag))}. Dan is het springtij.`;
      el.hidden = false;
    });
  }

  /* 5. Past jouw board? */
  const voet = (i) => `${Math.floor(i / 12)}'${i % 12}"`;
  function startCheck(scope) {
    scope.querySelectorAll('[data-tt-check]').forEach((s) => {
      const min = +s.dataset.min, max = +s.dataset.max;
      const schuif = s.querySelector('[data-tt-check-schuif]');
      const waarde = s.querySelector('[data-tt-check-waarde]');
      const antwoord = s.querySelector('[data-tt-check-antwoord]');
      const uitleg = s.querySelector('[data-tt-check-uitleg]');
      const board = s.querySelector('.tt-check__board');
      const stringer = s.querySelector('.tt-check__stringer');
      const banden = s.querySelectorAll('.tt-check__band');
      const maxlijn = s.querySelector('[data-tt-check-maxlijn]');
      const maxtekst = s.querySelector('[data-tt-check-maxtekst]');
      const H = 560, onder = 540, perInch = 500 / 132;
      const yMax = onder - max * perInch;
      maxlijn.setAttribute('y1', yMax); maxlijn.setAttribute('y2', yMax);
      maxtekst.setAttribute('y', yMax - 8); maxtekst.textContent = `max ${voet(max)}`;
      const teken = () => {
        const i = +schuif.value;
        const h = i * perInch, top = onder - h, b = Math.min(58, 30 + i * 0.22);
        board.setAttribute('d', `M100 ${top}C${100 + b * 1.15} ${top + h * 0.18} ${100 + b} ${top + h * 0.82} 100 ${onder}C${100 - b} ${top + h * 0.82} ${100 - b * 1.15} ${top + h * 0.18} 100 ${top}Z`);
        stringer.setAttribute('y1', top + 6); stringer.setAttribute('y2', onder - 6);
        banden[0].setAttribute('y', top + h * 0.28); banden[1].setAttribute('y', top + h * 0.66);
        const cm = Math.round(i * 2.54);
        waarde.textContent = `${voet(i)} (${cm} cm)`;
        schuif.style.setProperty('--p', `${((i - 48) / 84) * 100}%`);
        const past = i >= min && i <= max;
        s.classList.toggle('is-past', past); s.classList.toggle('is-niet', !past);
        if (past) { antwoord.textContent = 'Ja, die past.'; uitleg.textContent = `Een board van ${voet(i)} gaat in de tas. Banden strak, op je rug en gaan.`; }
        else if (i > max) { antwoord.textContent = 'Net te lang.'; uitleg.textContent = `Deze tas past op boards tot ${voet(max)}. Een grotere maat staat op de planning.`; }
        else { antwoord.textContent = 'Te klein voor deze tas.'; uitleg.textContent = `Deze tas is gemaakt voor boards vanaf ${voet(min)}.`; }
      };
      schuif.addEventListener('input', teken);
      teken();
    });
  }

  /* 6. Surfcheck: golven, wind, water en getij (Open-Meteo) */
  const windNaam = (g) => ['N', 'NO', 'O', 'ZO', 'Z', 'ZW', 'W', 'NW'][Math.round(((g % 360) + 360) % 360 / 45) % 8];
  const uur = (iso) => iso.slice(11, 16);
  function oordeel(golf, wind) {
    let zin;
    if (golf < 0.4) zin = 'Bijna vlak. Goed voor een eerste les op de softtop, of een dag rust.';
    else if (golf < 0.9) zin = 'Kleine, rustige golven. Ideaal om te leren en voor een longboard.';
    else if (golf < 1.6) zin = 'Lekker surfbaar. Pak je board en ga.';
    else if (golf < 2.5) zin = 'Flinke golven. Vooral voor wie al wat ervaring heeft.';
    else zin = 'Grote zee. Alleen voor gevorderden, en kijk eerst goed vanaf de kant.';
    if (wind != null && wind >= 20) zin += ' Wel veel wind, dus het water kan rommelig zijn.';
    return zin;
  }
  function startSurfcheck(scope) {
    scope.querySelectorAll('[data-tt-surfcheck]').forEach((s) => {
      let spots = [];
      try { spots = JSON.parse(s.querySelector('[data-tt-spots]').textContent); } catch (e) { return; }
      if (!spots.length) return;
      const sleutel = s.dataset.sleutel;
      const zee = sleutel ? 'https://customer-marine-api.open-meteo.com' : 'https://marine-api.open-meteo.com';
      const weer = sleutel ? 'https://customer-api.open-meteo.com' : 'https://api.open-meteo.com';
      const extra = sleutel ? `&apikey=${encodeURIComponent(sleutel)}` : '';
      const $ = (k) => s.querySelector(`[data-tt-${k}]`);
      const knoppen = s.querySelectorAll('[data-tt-spot]');
      const cache = {};
      async function haal(i) {
        if (cache[i]) return cache[i];
        const { lat, lon } = spots[i];
        const z = fetch(`${zee}/v1/marine?latitude=${lat}&longitude=${lon}&current=wave_height,wave_period,wave_direction,sea_surface_temperature&hourly=sea_level_height_msl&timezone=auto&forecast_days=2${extra}`).then((r) => r.ok ? r.json() : Promise.reject(r.status));
        const w = fetch(`${weer}/v1/forecast?latitude=${lat}&longitude=${lon}&current=wind_speed_10m,wind_direction_10m&wind_speed_unit=kn&timezone=auto${extra}`).then((r) => r.ok ? r.json() : null).catch(() => null);
        cache[i] = Promise.all([z, w]);
        return cache[i];
      }
      async function toon(i) {
        knoppen.forEach((k, n) => k.setAttribute('aria-selected', String(n === i)));
        try { localStorage.setItem('ttSpot', spots[i].naam); } catch (e) { /* geen opslag */ }
        s.classList.add('is-laden');
        try {
          const [m, w] = await haal(i);
          const c = m.current;
          $('golf').textContent = `${c.wave_height.toFixed(1).replace('.', ',')} m`;
          $('golf-extra').textContent = `om de ${Math.round(c.wave_period)} seconden, uit het ${windNaam(c.wave_direction)}`;
          $('water').textContent = c.sea_surface_temperature != null ? `${Math.round(c.sea_surface_temperature)}°C` : '';
          $('water-extra').textContent = c.sea_surface_temperature == null ? '' : c.sea_surface_temperature < 13 ? 'dik wetsuit (5/4)' : c.sea_surface_temperature < 17 ? 'wetsuit 4/3' : c.sea_surface_temperature < 21 ? 'wetsuit 3/2' : c.sea_surface_temperature < 24 ? 'shorty' : 'boardshort of bikini';
          let wind = null;
          if (w && w.current) {
            wind = w.current.wind_speed_10m;
            $('wind').textContent = `${Math.round(wind)} knopen`;
            $('wind-extra').textContent = `uit het ${windNaam(w.current.wind_direction_10m)}`;
            $('windblok').hidden = false;
          } else $('windblok').hidden = true;
          /* getij: de lokale toppen en dalen in het zeeniveau van vandaag en morgen */
          const tijd = m.hourly.time, zn = m.hourly.sea_level_height_msl;
          const nu = c.time.slice(0, 13) + ':00';
          let ni = Math.max(0, tijd.indexOf(nu));
          const stijgt = zn[ni + 1] > zn[ni];
          let volgende = null;
          for (let k = ni + 1; k < zn.length - 1; k++) {
            if ((zn[k] >= zn[k - 1] && zn[k] > zn[k + 1]) || (zn[k] <= zn[k - 1] && zn[k] < zn[k + 1])) { volgende = { t: tijd[k], hoog: zn[k] > zn[k - 1] }; break; }
          }
          const vlak = Math.max(...zn.slice(0, 24)) - Math.min(...zn.slice(0, 24)) < 0.15;
          $('getij').textContent = vlak ? 'nauwelijks' : stijgt ? 'opkomend' : 'afgaand';
          $('getij-extra').textContent = vlak ? 'weinig eb en vloed hier' : volgende ? `${volgende.hoog ? 'hoog' : 'laag'} water rond ${uur(volgende.t)}` : '';
          /* curve van vandaag */
          const dagW = zn.slice(0, 25), lo = Math.min(...dagW), hi = Math.max(...dagW), sp = (hi - lo) || 1;
          const pts = dagW.map((v, k) => [k * 25, 108 - ((v - lo) / sp) * 92]);
          const d = pts.map((q, k) => `${k ? 'L' : 'M'}${q[0].toFixed(1)} ${q[1].toFixed(1)}`).join('');
          $('curve').setAttribute('d', d);
          $('curve-vlak').setAttribute('d', `${d}L600 120L0 120Z`);
          const x = (parseInt(c.time.slice(11, 13), 10) + parseInt(c.time.slice(14, 16), 10) / 60) * 25;
          $('nu').setAttribute('x1', x); $('nu').setAttribute('x2', x);
          $('oordeel').textContent = oordeel(c.wave_height, wind);
          $('tijd').textContent = `${spots[i].naam}, nu (${uur(c.time)} lokale tijd)`;
          s.classList.remove('is-fout');
        } catch (e) {
          $('oordeel').textContent = 'De gegevens zijn nu niet te laden. Probeer het later nog eens.';
          $('tijd').textContent = '';
          s.classList.add('is-fout');
        }
        s.classList.remove('is-laden');
      }
      knoppen.forEach((k, n) => k.addEventListener('click', () => toon(n)));
      let start = 0;
      try { const opgeslagen = localStorage.getItem('ttSpot'); const n = spots.findIndex((x) => x.naam === opgeslagen); if (n > -1) start = n; } catch (e) { /* geen opslag */ }
      /* pas laden als de sectie bijna in beeld is */
      if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver((items) => { if (items[0].isIntersecting) { io.disconnect(); toon(start); } }, { rootMargin: '400px 0px' });
        io.observe(s);
      } else toon(start);
    });
  }

  start();
  startMaan(document); startCheck(document); startSurfcheck(document);
  document.addEventListener('shopify:section:load', (e) => { start(e.target); startMaan(e.target); startCheck(e.target); startSurfcheck(e.target); });

  if (stil) return;

  /* 7. Scroll: parallax en volloop-tekst */
  let raf = 0;
  const tick = () => {
    raf = 0;
    const vh = innerHeight;
    document.querySelectorAll('[data-tt-hero]').forEach((el) => {
      const r = el.parentElement.getBoundingClientRect();
      if (r.bottom < 0) return;
      const p = klem(-r.top / r.height, 0, 1);
      el.style.translate = `0 ${(p * r.height * 0.28).toFixed(1)}px`;
      el.style.opacity = (1 - p * 0.5).toFixed(3);
    });
    document.querySelectorAll('[data-tt-snelheid]').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < -300 || r.top > vh + 300) return;
      const p = (r.top + r.height / 2 - vh / 2) / vh;
      el.style.translate = `0 ${(p * parseFloat(el.dataset.ttSnelheid) * -300).toFixed(1)}px`;
    });
    document.querySelectorAll('[data-tt-draai]').forEach((el) => {
      el.style.rotate = `${(scrollY * parseFloat(el.dataset.ttDraai)).toFixed(1)}deg`;
    });
    document.querySelectorAll('[data-tt-schuif]').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const deel = el.scrollWidth / 3;
      el.style.transform = `translate3d(${(-((vh - r.top) * 0.45) % deel).toFixed(1)}px,0,0)`;
    });
    document.querySelectorAll('[data-tt-vul]').forEach((p) => {
      const r = p.getBoundingClientRect();
      const woorden = p.querySelectorAll('.tt-w');
      const v = klem((vh * 0.85 - r.top) / (r.height + vh * 0.3), 0, 1);
      const n = Math.round(v * woorden.length * 1.1);
      woorden.forEach((w, i) => w.classList.toggle('is-vol', i < n));
    });
  };
  const plan = () => { if (!raf) raf = requestAnimationFrame(tick); };
  addEventListener('scroll', plan, { passive: true });
  addEventListener('resize', plan);
  tick();

})();
