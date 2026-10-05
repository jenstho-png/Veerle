/* Tide-Tode · beweging en kopen voor de tt-secties. Geen libraries.
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
    const doelen = scope.querySelectorAll('[data-tt-regels], .tt-onthul, .tt-in');
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
          tekst.textContent = v.available ? `In mijn tas · ${geld(v.price)}` : 'Uitverkocht';
          sectie.querySelectorAll('.tt-koop__prijs span, .tt-balk__naam span').forEach((el) => { el.textContent = geld(v.price); });
        });
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
        waarde.textContent = `${voet(i)} · ${cm} cm`;
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

  start();
  startMaan(document); startCheck(document);
  document.addEventListener('shopify:section:load', (e) => { start(e.target); startMaan(e.target); startCheck(e.target); });

  if (stil) return;

  /* 6. Scroll: parallax en volloop-tekst */
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

  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    /* 7. Magnetische knoppen */
    document.querySelectorAll('.tt-knop:not(.tt-knop--vol)').forEach((b) => {
      b.addEventListener('pointermove', (e) => {
        const r = b.getBoundingClientRect();
        b.style.transform = `translate(${((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1)}px, ${((e.clientY - r.top - r.height / 2) * 0.3).toFixed(1)}px)`;
      });
      b.addEventListener('pointerleave', () => { b.style.transform = ''; });
    });

    /* 8. Cursor-bubbel boven beelden */
    const c = document.createElement('div');
    c.className = 'tt-cursor';
    c.setAttribute('aria-hidden', 'true');
    c.innerHTML = '<span></span>';
    document.body.appendChild(c);
    let x = -200, y = -200, tx = -200, ty = -200;
    addEventListener('pointermove', (e) => { tx = e.clientX; ty = e.clientY; }, { passive: true });
    const volg = () => { x += (tx - x) * 0.18; y += (ty - y) * 0.18; c.style.transform = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0)`; requestAnimationFrame(volg); };
    volg();
    document.addEventListener('pointerover', (e) => {
      const t = e.target.closest('[data-tt-cursor]');
      if (t && t.dataset.ttCursor) { c.firstChild.textContent = t.dataset.ttCursor; c.classList.add('is-aan'); }
    });
    document.addEventListener('pointerout', (e) => {
      const t = e.target.closest('[data-tt-cursor]');
      if (t && !t.contains(e.relatedTarget)) c.classList.remove('is-aan');
    });
  }
})();
