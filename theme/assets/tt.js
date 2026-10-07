/* Tide-Tode: beweging en kopen voor de tt-secties. Geen libraries.
   Regels voor vloeiende beweging:
   - Eén requestAnimationFrame-lus voor alles wat met de scroll meebeweegt.
     Posities worden één keer gemeten (en opnieuw bij resize of als de pagina
     langer wordt), per frame wordt alleen nog geschreven: geen layout-reads.
   - Alleen transform en opacity bewegen. Geen clip-path, filter of hoogte.
   - In beeld komen: één IntersectionObserver voor de hele pagina. Wat samen
     binnenkomt, komt na elkaar binnen (stagger).
   - 'Minder beweging' of de thema-editor: alles staat meteen op de eindstand.
   - Zonder JS (of als dit bestand niet laadt) is alles gewoon zichtbaar. */
(() => {
  const root = document.documentElement;
  const stil = matchMedia('(prefers-reduced-motion: reduce)').matches || !!(window.Shopify && window.Shopify.designMode);
  const fijn = matchMedia('(hover: hover) and (pointer: fine)').matches;
  root.classList.add('tt-js', 'tt-klaar');
  if (stil) root.classList.add('tt-stil');

  const klem = (v, a, b) => Math.max(a, Math.min(b, v));
  const geld = (c) => {
    try { return new Intl.NumberFormat(document.documentElement.lang || 'nl', { style: 'currency', currency: (window.Shopify && Shopify.currency && Shopify.currency.active) || 'EUR', minimumFractionDigits: c % 100 ? 2 : 0 }).format(c / 100); }
    catch (e) { return '€' + (c % 100 ? (c / 100).toFixed(2).replace('.', ',') : String(c / 100)); }
  };

  /* ---------- 1. In beeld komen ---------- */
  const DOELEN = '[data-tt-regels], .tt-onthul, .tt-in, .tt-stickerzee, .tt-teken';
  const zichtbaar = (el) => el.classList.add('is-in');
  /* een foto pas onthullen als hij geladen is (max. 1,2 s wachten), anders schuift er een leeg vlak open */
  const onthul = (el) => {
    /* galerij: alle foto's van de baan tegelijk, anders schuift er tijdens het swipen een doek open */
    if (el.hasAttribute('data-tt-dia') && el.parentElement) {
      el.parentElement.querySelectorAll('[data-tt-dia]').forEach((d) => { if (d !== el) { if (io) io.unobserve(d); zichtbaar(d); } });
    }
    const img = el.classList.contains('tt-onthul') && el.querySelector('img');
    if (!img || img.complete) return zichtbaar(el);
    let klaar = false;
    const doe = () => { if (!klaar) { klaar = true; zichtbaar(el); } };
    img.addEventListener('load', doe, { once: true });
    img.addEventListener('error', doe, { once: true });
    setTimeout(doe, 1200);
  };
  const io = (!stil && 'IntersectionObserver' in window) ? new IntersectionObserver((items) => {
    const binnen = items.filter((e) => e.isIntersecting);
    /* wat in hetzelfde frame binnenkomt: van boven naar beneden, van links naar rechts */
    binnen.sort((a, b) => (a.boundingClientRect.top - b.boundingClientRect.top) || (a.boundingClientRect.left - b.boundingClientRect.left));
    binnen.forEach((e, i) => {
      e.target.style.setProperty('--tt-stap', `${Math.min(i * 0.08, 0.48).toFixed(2)}s`);
      io.unobserve(e.target);
      onthul(e.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.01 }) : null;

  /* ---------- 2. De scroll-lus ---------- */
  /* Elk item: { el, soort, ... , top, h } met top/h in documentcoördinaten (gemeten aan de ouder). */
  const items = [];
  let vh = innerHeight, gemeten = false;
  const meet = () => {
    vh = innerHeight;
    const y = scrollY;
    /* eerst alles lezen ... */
    const maten = items.map((it) => { const r = (it.meet || it.el.parentElement || it.el).getBoundingClientRect(); return [r.top + y, r.height, r.width]; });
    /* ... dan pas opslaan */
    maten.forEach(([t, h, w], i) => { items[i].top = t; items[i].h = h; items[i].w = w; });
    items.forEach((it) => { if (it.soort === 'vul') it.n = -1; });
    gemeten = true;
  };
  let doelY = scrollY, zachtY = scrollY, raf = 0, vorige = 0;
  const frame = (t) => {
    raf = 0;
    if (!gemeten) meet();
    const y = scrollY; doelY = y;
    /* parallax loopt een fractie achter de scroll aan: dat voelt zacht, zonder de scroll zelf over te nemen */
    const dt = vorige ? Math.min(64, t - vorige) : 16.7; vorige = t;
    zachtY += (doelY - zachtY) * (1 - Math.pow(1 - 0.18, dt / 16.7));
    if (Math.abs(doelY - zachtY) < 0.2) zachtY = doelY;
    for (const it of items) {
      const top = it.top - y; /* positie op het scherm (zonder de eigen verschuiving) */
      const binnen = !(top > vh + 200 || top + it.h < -200);
      /* alleen een eigen laag (will-change) zolang het item in de buurt van het scherm is */
      if (binnen !== it.aan) { it.aan = binnen; it.el.style.willChange = binnen ? (it.soort === 'schuif' ? 'transform' : 'translate') : ''; }
      if (!binnen) continue;
      switch (it.soort) {
        case 'hero': {
          const p = klem((zachtY - it.top) / Math.max(1, it.h), 0, 1);
          it.el.style.translate = `0 ${(p * it.h * 0.22).toFixed(1)}px`;
          if (it.inhoud) it.inhoud.style.opacity = (1 - p * 0.9).toFixed(3);
          break;
        }
        case 'foto': { /* foto schuift binnen zijn kader: -1 onder in beeld, +1 boven */
          const p = klem(((it.top - zachtY) + it.h / 2 - vh / 2) / (vh / 2 + it.h / 2), -1, 1);
          it.el.style.translate = `0 ${(p * it.h * it.v).toFixed(1)}px`;
          break;
        }
        case 'snelheid': {
          const p = ((it.top - zachtY) + it.h / 2 - vh / 2) / vh;
          it.el.style.translate = `0 ${(p * it.v * -300).toFixed(1)}px`;
          break;
        }
        case 'schuif': {
          const deel = it.w / 3 || 1;
          it.el.style.transform = `translate3d(${(-((vh - (it.top - zachtY)) * 0.45) % deel).toFixed(1)}px,0,0)`;
          break;
        }
        case 'vul': {
          const v = klem((vh * 0.85 - top) / (it.h + vh * 0.3), 0, 1);
          const n = Math.round(v * it.woorden.length * 1.1);
          if (n !== it.n) {
            const [a, b] = it.n < 0 ? [0, it.woorden.length] : [Math.min(n, it.n), Math.max(n, it.n)];
            for (let i = a; i < b && i < it.woorden.length; i++) it.woorden[i].classList.toggle('is-vol', i < n);
            it.n = n;
          }
          break;
        }
        default: break;
      }
    }
    for (const el of draai) el.style.rotate = `${(zachtY * parseFloat(el.dataset.ttDraai)).toFixed(1)}deg`;
    if (zachtY !== doelY) plan();
  };
  const draai = [];
  const plan = () => { if (!raf) raf = requestAnimationFrame(frame); };
  const opnieuw = () => { gemeten = false; plan(); };

  function registreer(scope) {
    if (stil) return;
    const voeg = (el, soort, extra = {}) => {
      if (el.dataset.ttLus) return; el.dataset.ttLus = '1';
      items.push({ el, soort, top: 0, h: 0, w: 0, ...extra });
    };
    /* hero: foto zakt langzaam weg, tekst vervaagt */
    scope.querySelectorAll('.tt-hero__foto').forEach((el) => voeg(el, 'hero', { meet: el.closest('.tt-hero'), inhoud: el.closest('.tt-hero').querySelector('.tt-hero__inhoud') }));
    /* slotfoto en foto's in de verhalende secties: zachte parallax binnen het kader */
    scope.querySelectorAll('.tt-slot__foto, .tt-verhaal__foto .tt-onthul, .tt-wie__foto .tt-onthul, .tt-probleem__foto, .tt-zo__foto, .tt-muur__item .tt-onthul, .tt-raster__vak--foto, .tt-col__beeld').forEach((kader) => {
      const img = kader.querySelector(':scope > img');
      if (!img) return;
      kader.classList.add('tt-par');
      voeg(img, 'foto', { meet: kader, v: kader.classList.contains('tt-slot__foto') ? 0.08 : 0.05 });
    });
    scope.querySelectorAll('[data-tt-snelheid]').forEach((el) => voeg(el, 'snelheid', { v: parseFloat(el.dataset.ttSnelheid) || 0.2 }));
    scope.querySelectorAll('[data-tt-schuif]').forEach((el) => voeg(el, 'schuif', { meet: el }));
    scope.querySelectorAll('[data-tt-vul]').forEach((el) => voeg(el, 'vul', { meet: el, woorden: [...el.querySelectorAll('.tt-w')], n: -1 }));
    scope.querySelectorAll('[data-tt-draai]').forEach((el) => { if (!draai.includes(el)) draai.push(el); });
    opnieuw();
  }

  if (!stil) {
    addEventListener('scroll', plan, { passive: true });
    addEventListener('resize', opnieuw, { passive: true });
    /* de pagina wordt langer als foto's of lettertypes laden: dan opnieuw meten */
    if ('ResizeObserver' in window) {
      let h = 0;
      new ResizeObserver(() => { const n = document.body.offsetHeight; if (n !== h) { h = n; opnieuw(); } }).observe(document.body);
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(opnieuw);
  }

  /* ---------- 3. Hover: magnetische knoppen, kantelende kaarten ---------- */
  function hover(scope) {
    if (stil || !fijn) return;
    scope.querySelectorAll('.tt-knop:not(.tt-knop--vol), .surf-icon-btn, [data-tt-magneet]').forEach((el) => {
      if (el.dataset.ttMagneet === '1') return; el.dataset.ttMagneet = '1';
      let r = null, f = 0, x = 0, y = 0;
      const schrijf = () => { f = 0; el.style.translate = `${x.toFixed(1)}px ${y.toFixed(1)}px`; };
      el.addEventListener('pointerenter', () => { r = el.getBoundingClientRect(); el.classList.add('is-magneet'); });
      el.addEventListener('pointermove', (e) => {
        if (!r) return;
        x = klem((e.clientX - (r.left + r.width / 2)) * 0.22, -7, 7);
        y = klem((e.clientY - (r.top + r.height / 2)) * 0.3, -5, 5);
        if (!f) f = requestAnimationFrame(schrijf);
      });
      el.addEventListener('pointerleave', () => { r = null; x = 0; y = 0; el.classList.remove('is-magneet'); if (!f) f = requestAnimationFrame(schrijf); });
    });
    scope.querySelectorAll('[data-tt-kantel]').forEach((el) => {
      if (el.dataset.ttKantelAan) return; el.dataset.ttKantelAan = '1';
      let r = null, f = 0, x = 0, y = 0;
      const schrijf = () => { f = 0; el.style.transform = r ? `perspective(900px) rotateX(${(-y * 5).toFixed(2)}deg) rotateY(${(x * 6).toFixed(2)}deg) translateY(-4px)` : ''; };
      el.addEventListener('pointerenter', () => { r = el.getBoundingClientRect(); });
      el.addEventListener('pointermove', (e) => {
        if (!r) return;
        x = (e.clientX - r.left) / r.width - 0.5; y = (e.clientY - r.top) / r.height - 0.5;
        if (!f) f = requestAnimationFrame(schrijf);
      });
      el.addEventListener('pointerleave', () => { r = null; if (!f) f = requestAnimationFrame(schrijf); });
    });
  }

  /* ---------- 4. Productpagina: galerij, lightbox, varianten, toevoegen ---------- */
  function galerij(sectie) {
    const baan = sectie.querySelector('[data-tt-galerij]');
    if (!baan) return null;
    const dias = [...baan.querySelectorAll('[data-tt-dia]')];
    const teller = sectie.querySelector('[data-tt-teller]');
    const balkje = sectie.querySelector('[data-tt-voortgang]');
    const duimen = [...sectie.querySelectorAll('[data-tt-duim]')];
    let huidig = 0;
    const zet = (i) => {
      huidig = i;
      if (teller) teller.textContent = String(i + 1);
      if (balkje) balkje.style.transform = `translateX(${(i * 100).toFixed(0)}%)`;
      duimen.forEach((d, n) => d.setAttribute('aria-current', String(n === i)));
    };
    if (balkje) balkje.style.width = `${100 / Math.max(1, dias.length)}%`;
    /* welke foto staat in beeld: IntersectionObserver binnen de baan, geen scroll-handler */
    if ('IntersectionObserver' in window && dias.length > 1) {
      const zicht = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) zet(dias.indexOf(e.target)); }), { root: baan, threshold: 0.6 });
      dias.forEach((d) => zicht.observe(d));
    }
    const naar = (i, gedrag) => {
      const d = dias[i]; if (!d) return;
      const horizontaal = getComputedStyle(baan).overflowX !== 'visible' && baan.scrollWidth > baan.clientWidth + 2;
      if (horizontaal) baan.scrollTo({ left: d.offsetLeft - baan.offsetLeft - parseFloat(getComputedStyle(baan).paddingLeft || 0), behavior: stil ? 'auto' : (gedrag || 'smooth') });
      else d.scrollIntoView({ behavior: stil ? 'auto' : 'smooth', block: 'nearest' });
      zet(i);
    };
    duimen.forEach((d, n) => d.addEventListener('click', () => naar(n)));
    /* klik op een foto: groot bekijken */
    dias.forEach((d, n) => {
      const knop = d.querySelector('[data-tt-zoom]');
      if (knop) knop.addEventListener('click', () => lightbox(dias, n));
    });
    return { naar, dias };
  }

  let lb = null;
  function lightbox(dias, start) {
    if (!window.HTMLDialogElement) return;
    if (!lb) {
      lb = document.createElement('dialog');
      lb.className = 'tt-lb';
      lb.setAttribute('aria-label', 'Foto’s');
      lb.innerHTML = '<div class="tt-lb__baan" data-lb-baan></div><p class="tt-lb__teller" aria-live="polite"><span data-lb-nr>1</span> / <span data-lb-tot>1</span></p><button type="button" class="tt-lb__knop tt-lb__sluit" data-lb-sluit aria-label="Sluiten"><span aria-hidden="true"></span></button><button type="button" class="tt-lb__knop tt-lb__vorige" data-lb-stap="-1" aria-label="Vorige foto">←</button><button type="button" class="tt-lb__knop tt-lb__volgende" data-lb-stap="1" aria-label="Volgende foto">→</button>';
      document.body.appendChild(lb);
      const baan = lb.querySelector('[data-lb-baan]');
      lb.querySelector('[data-lb-sluit]').addEventListener('click', () => sluit());
      lb.addEventListener('click', (e) => { if (e.target === lb) sluit(); });
      lb.addEventListener('cancel', (e) => { e.preventDefault(); sluit(); });
      lb.querySelectorAll('[data-lb-stap]').forEach((k) => k.addEventListener('click', () => stap(+k.dataset.lbStap)));
      lb.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') stap(1); if (e.key === 'ArrowLeft') stap(-1); });
      const stap = (s) => { const i = klem(lb._i + s, 0, lb._n - 1); baan.children[i].scrollIntoView({ behavior: stil ? 'auto' : 'smooth', inline: 'start', block: 'nearest' }); };
      const sluit = () => {
        if (stil) { lb.close(); return; }
        lb.classList.add('is-dicht');
        setTimeout(() => { lb.classList.remove('is-dicht'); lb.close(); }, 320);
      };
      /* zoomen: klik = 2x op die plek, bewegen = rondkijken */
      baan.addEventListener('click', (e) => {
        const fig = e.target.closest('.tt-lb__dia'); if (!fig) return;
        const img = fig.querySelector('img');
        const aan = !fig.classList.contains('is-zoom');
        fig.classList.toggle('is-zoom', aan);
        if (aan) { const r = fig.getBoundingClientRect(); img.style.transformOrigin = `${((e.clientX - r.left) / r.width) * 100}% ${((e.clientY - r.top) / r.height) * 100}%`; }
      });
      let f = 0;
      baan.addEventListener('pointermove', (e) => {
        const fig = e.target.closest('.tt-lb__dia.is-zoom'); if (!fig || e.pointerType !== 'mouse' || f) return;
        f = requestAnimationFrame(() => { f = 0; const r = fig.getBoundingClientRect(); fig.querySelector('img').style.transformOrigin = `${((e.clientX - r.left) / r.width) * 100}% ${((e.clientY - r.top) / r.height) * 100}%`; });
      });
      const zicht = new IntersectionObserver((es) => es.forEach((e) => {
        if (!e.isIntersecting) { e.target.classList.remove('is-zoom'); return; }
        lb._i = [...baan.children].indexOf(e.target);
        lb.querySelector('[data-lb-nr]').textContent = String(lb._i + 1);
      }), { root: baan, threshold: 0.6 });
      lb._zicht = zicht;
    }
    const baan = lb.querySelector('[data-lb-baan]');
    baan.textContent = '';
    dias.forEach((d) => {
      const bron = d.querySelector('img'); if (!bron) return;
      const fig = document.createElement('figure'); fig.className = 'tt-lb__dia';
      const img = document.createElement('img');
      img.src = bron.dataset.groot || bron.currentSrc || bron.src; img.alt = bron.alt || ''; img.decoding = 'async';
      fig.appendChild(img); baan.appendChild(fig); lb._zicht.observe(fig);
    });
    lb._n = baan.children.length; lb._i = start;
    lb.querySelector('[data-lb-tot]').textContent = String(lb._n);
    lb.querySelector('[data-lb-nr]').textContent = String(start + 1);
    lb.showModal();
    requestAnimationFrame(() => { const d = baan.children[start]; if (d) baan.scrollLeft = d.offsetLeft; });
  }

  /* winkelwagen: teller bijwerken en het icoon een tikje laten maken */
  function winkelwagen(aantal) {
    const knop = document.getElementById('cart-icon-bubble');
    if (!knop) return;
    let bol = knop.querySelector('.surf-count');
    if (!bol && aantal > 0) { bol = document.createElement('span'); bol.className = 'surf-count'; bol.setAttribute('aria-hidden', 'true'); knop.appendChild(bol); }
    if (bol) bol.textContent = String(aantal);
    knop.setAttribute('aria-label', `Winkelwagen (${aantal})`);
    if (stil) return;
    knop.classList.remove('is-tik'); void knop.offsetWidth; knop.classList.add('is-tik');
    knop.addEventListener('animationend', () => knop.classList.remove('is-tik'), { once: true });
  }
  let melding = null;
  function meld(titel, beeld) {
    if (!melding) {
      melding = document.createElement('div');
      melding.className = 'tt-melding'; melding.setAttribute('role', 'status'); melding.setAttribute('aria-live', 'polite');
      document.body.appendChild(melding);
    }
    const route = (window.routes && window.routes.cart_url) || '/cart';
    melding.innerHTML = `<span class="tt-melding__beeld">${beeld ? `<img src="${beeld}" alt="">` : ''}</span><span class="tt-melding__tekst"><strong>In je winkelwagen</strong><span></span></span><a class="tt-melding__link" href="${route}">Bekijk</a>`;
    melding.querySelector('.tt-melding__tekst span').textContent = titel;
    melding.classList.remove('is-aan'); void melding.offsetWidth; melding.classList.add('is-aan');
    clearTimeout(melding._t); melding._t = setTimeout(() => melding.classList.remove('is-aan'), 4200);
  }

  function koop(sectie) {
    if (sectie.dataset.ttKoopAan) return; sectie.dataset.ttKoopAan = '1';
    const gal = galerij(sectie);
    const form = sectie.querySelector('[data-tt-form]') || sectie.querySelector('.tt-koop__form form');
    if (!form) return;
    const data = form.querySelector('[data-tt-varianten]');
    const id = form.querySelector('[data-tt-variant]');
    const knop = form.querySelector('[data-tt-koopknop]');
    const tekst = form.querySelector('[data-tt-knoptekst]');
    const fout = form.querySelector('[data-tt-fout]');
    const was = sectie.querySelectorAll('[data-tt-prijs-was]');
    let varianten = [];
    try { varianten = data ? JSON.parse(data.textContent) : []; } catch (e) { varianten = []; }
    const groepen = [...form.querySelectorAll('.tt-koop__optie')];
    const kies = () => groepen.map((g) => (g.querySelector('input:checked') || {}).value);
    /* welke waarden zijn met de rest van de keuze nog leverbaar? */
    const markeer = () => {
      const gekozen = kies();
      groepen.forEach((g, gi) => g.querySelectorAll('input').forEach((inp) => {
        const kan = varianten.some((v) => v.available && v.options[gi] === inp.value && v.options.every((o, oi) => oi === gi || o === gekozen[oi] || gekozen[oi] == null));
        inp.parentElement.classList.toggle('is-op', !kan);
      }));
    };
    const label = (s) => { if (tekst) tekst.textContent = s; };
    if (varianten.length && groepen.length) {
      form.addEventListener('change', (e) => {
        if (!e.target.matches('.tt-koop__optie input')) return;
        const gekozen = kies();
        const v = varianten.find((x) => x.options.every((o, i) => o === gekozen[i]));
        markeer();
        groepen.forEach((g) => { const s = g.querySelector('[data-tt-gekozen]'); const c = g.querySelector('input:checked'); if (s && c) s.textContent = c.value; });
        if (!v) { knop.disabled = true; label('Niet beschikbaar'); return; }
        id.value = v.id; knop.disabled = !v.available;
        label(v.available ? 'In winkelwagen' : 'Uitverkocht');
        sectie.querySelectorAll('[data-tt-prijs-nu], .tt-balk__naam span').forEach((el) => { el.textContent = geld(v.price); });
        was.forEach((el) => { el.hidden = !(v.compare_at_price > v.price); if (v.compare_at_price > v.price) el.textContent = geld(v.compare_at_price); });
        try { const u = new URL(location.href); u.searchParams.set('variant', v.id); history.replaceState(history.state, '', u); } catch (err) { /* geen url */ }
        if (gal && v.featured_media) { const i = gal.dias.findIndex((d) => d.dataset.mediaId === String(v.featured_media.id)); if (i > -1) gal.naar(i); }
      });
      markeer();
    }
    /* aantal: min en plus */
    form.querySelectorAll('[data-tt-aantal]').forEach((k) => k.addEventListener('click', () => {
      const inp = form.querySelector('input[name="quantity"]'); if (!inp) return;
      inp.value = String(Math.max(1, (parseInt(inp.value, 10) || 1) + parseInt(k.dataset.ttAantal, 10)));
    }));
    /* toevoegen zonder de pagina te verlaten; lukt fetch niet, dan gewoon het formulier versturen */
    form.addEventListener('submit', async (e) => {
      if (!window.fetch || !window.FormData || form.dataset.ttGewoon) return;
      e.preventDefault();
      if (knop.disabled) return;
      const oud = tekst ? tekst.textContent : '';
      knop.classList.add('is-bezig'); knop.setAttribute('aria-busy', 'true');
      if (fout) { fout.hidden = true; fout.textContent = ''; }
      try {
        const add = ((window.routes && window.routes.cart_add_url) || '/cart/add').replace(/\.js$/, '') + '.js';
        const r = await fetch(add, { method: 'POST', headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' }, body: new FormData(form) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok) throw Object.assign(new Error('mislukt'), { tekst: j.description || j.message });
        knop.classList.remove('is-bezig'); knop.classList.add('is-klaar'); label('Toegevoegd');
        setTimeout(() => { knop.classList.remove('is-klaar'); label(oud); }, 2200);
        const cart = await fetch(((window.routes && window.routes.cart_url) || '/cart') + '.js', { headers: { Accept: 'application/json' } }).then((x) => x.json()).catch(() => null);
        if (cart) winkelwagen(cart.item_count);
        const img = sectie.querySelector('[data-tt-dia] img');
        meld(j.product_title || (sectie.querySelector('h1, h2') || {}).textContent || '', j.image ? `${j.image}${j.image.includes('?') ? '&' : '?'}width=160` : (img && img.currentSrc));
      } catch (err) {
        knop.classList.remove('is-bezig');
        if (err && err.tekst && fout) { fout.textContent = err.tekst; fout.hidden = false; }
        else { form.dataset.ttGewoon = '1'; form.requestSubmit ? form.requestSubmit(knop) : form.submit(); }
      }
      knop.removeAttribute('aria-busy');
    });
    /* plakbalk: verschijnt als de koopknop uit beeld is, en verdwijnt weer bij de footer */
    const balk = sectie.querySelector('[data-tt-balk]');
    if (balk && 'IntersectionObserver' in window) {
      document.body.appendChild(balk);
      balk.querySelector('[data-tt-balkknop]').addEventListener('click', () => {
        if (form.requestSubmit) form.requestSubmit(knop); else knop.click();
      });
      let voorbij = false, onder = false;
      const zet = () => {
        const aan = voorbij && !onder;
        balk.classList.toggle('is-aan', aan);
        balk.setAttribute('aria-hidden', String(!aan));
        balk.querySelector('button').tabIndex = aan ? 0 : -1;
      };
      new IntersectionObserver(([e]) => { voorbij = !e.isIntersecting && e.boundingClientRect.top < 0; zet(); }).observe(knop);
      const voet = document.querySelector('.surf-footer, footer');
      if (voet) new IntersectionObserver(([e]) => { onder = e.isIntersecting; zet(); }).observe(voet);
    }
  }

  /* aanraders: Shopify-aanbevelingen ophalen zodra de sectie bijna in beeld is */
  function aanraders(scope) {
    scope.querySelectorAll('[data-tt-aanraders][data-url]').forEach((s) => {
      if (s.dataset.ttGeladen) return; s.dataset.ttGeladen = '1';
      const haal = () => fetch(s.dataset.url).then((r) => r.text()).then((html) => {
        const nieuw = new DOMParser().parseFromString(html, 'text/html').querySelector('[data-tt-aanraders] [data-tt-aanraders-lijst]');
        if (!nieuw || !nieuw.children.length) return;
        const lijst = s.querySelector('[data-tt-aanraders-lijst]');
        lijst.replaceWith(nieuw);
        s.hidden = false;
        start(s);
      }).catch(() => {});
      if ('IntersectionObserver' in window) {
        const w = new IntersectionObserver(([e]) => { if (e.isIntersecting) { w.disconnect(); haal(); } }, { rootMargin: '600px 0px' });
        w.observe(s);
      } else haal();
    });
  }

  /* productkaart: de foto van de aangeklikte kaart vloeit over in de productpagina (View Transitions) */
  document.addEventListener('click', (e) => {
    const kaart = e.target.closest && e.target.closest('a.tt-pk');
    if (!kaart || stil) return;
    const img = kaart.querySelector('.tt-pk__img');
    if (!img) return;
    document.querySelectorAll('.tt-koop__eerste').forEach((i) => { i.style.viewTransitionName = 'none'; });
    img.style.viewTransitionName = 'tt-productfoto';
  });
  addEventListener('pageshow', () => document.querySelectorAll('.tt-pk__img, .tt-koop__eerste').forEach((i) => { i.style.viewTransitionName = ''; }));

  function start(scope = document) {
    /* collectie sorteren */
    scope.querySelectorAll('[data-tt-sorteer]').forEach((el) => {
      if (el.dataset.ttAan) return; el.dataset.ttAan = '1';
      el.addEventListener('change', () => { const u = new URL(location.href); u.searchParams.set('sort_by', el.value); u.searchParams.delete('page'); location.href = u; });
    });
    /* lijntekeningen: lengte van elke lijn meten zodat ze zichzelf kunnen tekenen */
    if (!stil) scope.querySelectorAll('.tt-teken .tt-ill path, .tt-teken .tt-ill line, .tt-teken .tt-ill circle').forEach((el) => {
      if (el.dataset.len || el.closest('defs')) return;
      try { const l = Math.ceil(el.getTotalLength()); el.dataset.len = l; el.style.setProperty('--len', l); } catch (e) { /* geen pad */ }
    });
    /* tekst die volloopt: woorden splitsen */
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
    const doelen = scope.querySelectorAll(DOELEN);
    if (!io) doelen.forEach(zichtbaar);
    else doelen.forEach((el) => { if (!el.classList.contains('is-in')) io.observe(el); });
    hover(scope);
    registreer(scope);
    scope.querySelectorAll('[data-tt-koop]').forEach(koop);
    aanraders(scope);
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
      const paneel = s.querySelector('.tt-check__paneel');
      const schouder = s.querySelector('.tt-check__schouder');
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
        /* de tas: tegelvak om het midden van het board, schouderband aan de zijkant */
        const py = top + h * 0.4, ph = Math.min(150, h * 0.26), pb = b * 0.92;
        paneel.setAttribute('d', `M${100 - pb * 0.8} ${py}L${100 + pb * 0.8} ${py}L${100 + pb} ${py + ph}L${100 - pb} ${py + ph}Z`);
        schouder.setAttribute('d', `M${100 - pb * 0.8} ${py + 6}L${100 - pb - 34} ${py + ph * 0.5}L${100 - pb} ${py + ph - 6}`);
        const cm = Math.round(i * 2.54);
        waarde.textContent = `${voet(i)} (${cm} cm)`;
        schuif.style.setProperty('--p', `${((i - 48) / 84) * 100}%`);
        const past = i >= min && i <= max;
        s.classList.toggle('is-past', past); s.classList.toggle('is-niet', !past);
        if (past) { antwoord.textContent = 'Ja, die past.'; uitleg.textContent = `Een board van ${voet(i)} past in de tas.`; }
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
          s.classList.remove('is-fout'); s.classList.add('is-klaar');
        } catch (e) {
          delete cache[i]; /* een volgende klik probeert het opnieuw */
          $('oordeel').textContent = 'De zee laat zich nu even niet checken. Probeer het over een paar minuten nog eens, of kies een andere spot.';
          $('tijd').textContent = 'De gegevens komen van Open-Meteo en zijn tijdelijk niet bereikbaar.';
          s.classList.add('is-fout'); s.classList.remove('is-klaar');
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
})();
