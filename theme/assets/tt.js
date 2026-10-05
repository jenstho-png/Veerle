/* Tide-Tode · beweging voor de tt-secties. Geen libraries.
   - Alles rekent in één requestAnimationFrame per scroll.
   - 'Minder beweging' of de thema-editor: alles staat meteen op de eindstand. */
(() => {
  const root = document.documentElement;
  const stil = matchMedia('(prefers-reduced-motion: reduce)').matches || !!(window.Shopify && window.Shopify.designMode);
  root.classList.add('tt-js');
  if (stil) root.classList.add('tt-stil');

  const klem = (v, a, b) => Math.max(a, Math.min(b, v));

  function start(scope = document) {
    /* 1. In beeld komen: regels, onthullen, tekenen */
    const doelen = scope.querySelectorAll('[data-tt-regels], .tt-onthul, .tt-in, [data-tt-teken]');
    if (stil || !('IntersectionObserver' in window)) {
      doelen.forEach((el) => el.classList.add('is-in'));
    } else {
      const io = new IntersectionObserver((items) => items.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      }), { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
      doelen.forEach((el) => io.observe(el));
    }

    /* 2. Maan: lijnlengte voor het tekenen */
    scope.querySelectorAll('[data-tt-teken] .tt-teken__lijn path').forEach((p) => {
      try { p.style.setProperty('--len', Math.ceil(p.getTotalLength())); } catch (e) { /* oude browser */ }
    });

    /* 3. Manifest: woorden splitsen */
    scope.querySelectorAll('[data-tt-vul]').forEach((p) => {
      if (p.dataset.ttKlaar) return;
      p.dataset.ttKlaar = '1';
      const splits = (node) => {
        [...node.childNodes].forEach((n) => {
          if (n.nodeType === 3) {
            const frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach((w) => {
              if (!w) return;
              if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(w)); return; }
              const s = document.createElement('span'); s.className = 'tt-w'; s.textContent = w; frag.appendChild(s);
            });
            node.replaceChild(frag, n);
          } else if (n.nodeType === 1) splits(n);
        });
      };
      splits(p);
      if (stil) p.querySelectorAll('.tt-w').forEach((w) => w.classList.add('is-vol'));
    });
  }

  start();
  document.addEventListener('shopify:section:load', (e) => start(e.target));

  if (stil) return;

  /* 4. Scroll: parallax, draaien, band, vullen, pinnen, groeien */
  let raf = 0;
  const tick = () => {
    raf = 0;
    const vh = innerHeight, vw = innerWidth, y = scrollY;
    document.querySelectorAll('[data-tt-snelheid]').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      const p = (r.top + r.height / 2 - vh / 2) / vh;
      el.style.translate = `0 ${(p * parseFloat(el.dataset.ttSnelheid) * -260).toFixed(1)}px`;
    });
    document.querySelectorAll('[data-tt-draai]').forEach((el) => {
      el.style.rotate = `${(y * parseFloat(el.dataset.ttDraai)).toFixed(1)}deg`;
    });
    document.querySelectorAll('[data-tt-band]').forEach((rij) => {
      const r = rij.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const spoor = rij.firstElementChild;
      const kwart = spoor.scrollWidth / 4;
      const v = parseFloat(rij.dataset.ttSnelheidX || .35);
      let x = ((vh - r.top) * v * 2.4) % kwart;
      if (rij.dataset.ttBand === '1') x = -kwart + x;
      else x = -x;
      spoor.style.transform = `translate3d(${x.toFixed(1)}px,0,0)`;
    });
    document.querySelectorAll('[data-tt-vul]').forEach((p) => {
      const r = p.getBoundingClientRect();
      const woorden = p.querySelectorAll('.tt-w');
      const v = klem((vh * 0.82 - r.top) / (r.height + vh * 0.25), 0, 1);
      const n = Math.round(v * woorden.length * 1.08);
      woorden.forEach((w, i) => w.classList.toggle('is-vol', i < n));
    });
    document.querySelectorAll('[data-tt-pin]').forEach((s) => {
      const r = s.getBoundingClientRect();
      const spoor = s.querySelector('[data-tt-spoor]');
      const totaal = r.height - vh;
      const p = klem(-r.top / (totaal || 1), 0, 1);
      const max = Math.max(0, spoor.scrollWidth - vw);
      spoor.style.transform = `translate3d(${(-p * max).toFixed(1)}px,0,0)`;
    });
    document.querySelectorAll('[data-tt-groei]').forEach((el) => {
      const r = el.getBoundingClientRect();
      const p = klem(1 - (r.top + r.height / 2 - vh / 2) / vh, 0, 1);
      el.style.scale = (0.72 + 0.28 * p).toFixed(3);
    });
  };
  const plan = () => { if (!raf) raf = requestAnimationFrame(tick); };
  addEventListener('scroll', plan, { passive: true });
  addEventListener('resize', plan);
  tick();

  /* 5. Magnetische knoppen */
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('.tt-knop').forEach((b) => {
      b.addEventListener('pointermove', (e) => {
        const r = b.getBoundingClientRect();
        b.style.transform = `translate(${((e.clientX - r.left - r.width / 2) * 0.22).toFixed(1)}px, ${((e.clientY - r.top - r.height / 2) * 0.35).toFixed(1)}px)`;
      });
      b.addEventListener('pointerleave', () => { b.style.transform = ''; });
    });

    /* 6. Cursor-bubbel boven beelden */
    const c = document.createElement('div');
    c.className = 'tt-cursor';
    c.setAttribute('aria-hidden', 'true');
    c.innerHTML = '<span></span>';
    document.body.appendChild(c);
    let x = -200, yy = -200, tx = -200, ty = -200;
    addEventListener('pointermove', (e) => { tx = e.clientX; ty = e.clientY; }, { passive: true });
    const volg = () => { x += (tx - x) * 0.2; yy += (ty - yy) * 0.2; c.style.transform = `translate3d(${x.toFixed(1)}px,${yy.toFixed(1)}px,0)`; requestAnimationFrame(volg); };
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
