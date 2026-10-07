/* Surf: header, mobiel menu en lead-popup. Opkomen en scroll-beweging zitten in mk-stijl.js. */
(() => {
  /* Header: verbergen bij naar beneden scrollen, tonen bij omhoog */
  const wrap = document.querySelector('[data-surf-header]');
  if (wrap && wrap.dataset.hide === 'true') {
    let last = window.scrollY;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      wrap.classList.toggle('is-hidden', y > last && y > 200);
      last = y;
    }, { passive: true });
  }

  /* Mobiel menu */
  const drawer = document.getElementById('SurfDrawer');
  const openBtn = document.querySelector('[data-surf-drawer-open]');
  if (drawer && openBtn) {
    const setOpen = (open) => {
      drawer.hidden = !open;
      openBtn.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
      (open ? drawer.querySelector('[data-surf-drawer-close]') : openBtn).focus();
    };
    openBtn.addEventListener('click', () => setOpen(true));
    drawer.querySelector('[data-surf-drawer-close]').addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !drawer.hidden) setOpen(false); });
  }

  /* Desktop-dropdowns: sluiten bij klik buiten */
  document.addEventListener('click', (e) => {
    document.querySelectorAll('.surf-header__nav details[open]').forEach((d) => {
      if (!d.contains(e.target)) d.removeAttribute('open');
    });
  });

  /* Lead-popup */
  const popup = document.getElementById('SurfPopup');
  if (!popup) return;
  const teaser = document.querySelector('[data-surf-popup-open]');
  const KEY = 'surfPopup';
  const WEEK = 7 * 24 * 60 * 60 * 1000;
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; } },
    set(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* privé-venster */ } },
  };
  let vorige = null;
  const show = () => {
    if (!popup.hidden) return;
    vorige = document.activeElement;
    popup.hidden = false;
    requestAnimationFrame(() => popup.classList.add('is-open'));
    document.documentElement.classList.add('tt-pop-open');
    if (teaser) teaser.hidden = true;
    store.set({ ...store.get(), seen: Date.now() });
    popup.querySelector('input[type=email], [data-surf-popup-close]').focus({ preventScroll: true });
  };
  const hide = () => {
    if (popup.hidden) return;
    popup.classList.remove('is-open');
    document.documentElement.classList.remove('tt-pop-open');
    setTimeout(() => { popup.hidden = true; }, 450);
    if (teaser && !store.get().done) teaser.hidden = false;
    if (vorige && vorige.focus) vorige.focus({ preventScroll: true });
  };

  popup.querySelectorAll('[data-surf-popup-close]').forEach((b) => b.addEventListener('click', hide));
  popup.addEventListener('click', (e) => { if (e.target === popup) hide(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hide(); });
  popup.querySelector('form')?.addEventListener('submit', () => store.set({ ...store.get(), done: true }));
  teaser?.addEventListener('click', show);
  /* met de muis over de kortingsknop: de popup gaat open; ga je met de muis weg (en niet naar de kaart), dan sluit hij weer */
  if (teaser && window.matchMedia('(hover: hover)').matches) {
    const kaart = popup.querySelector('.tt-pop__kaart');
    let viaHover = false, klok = null;
    teaser.addEventListener('mouseenter', () => { viaHover = true; show(); });
    document.addEventListener('pointermove', (e) => {
      if (!viaHover || popup.hidden) return;
      const binnen = kaart && kaart.contains(e.target);
      if (binnen) { clearTimeout(klok); klok = null; }
      else if (!klok) klok = setTimeout(() => { viaHover = false; klok = null; hide(); }, 900);
    });
    popup.querySelector('form')?.addEventListener('focusin', () => { viaHover = false; clearTimeout(klok); });
  }
  /* in de footer de kortingsknop verbergen, zodat de onderste regel leesbaar blijft */
  const voet = document.querySelector('footer, .surf-footer, [class*="footer-group"]');
  if (teaser && voet && 'IntersectionObserver' in window) {
    new IntersectionObserver((es) => es.forEach((e) => document.documentElement.classList.toggle('tt-in-voet', e.isIntersecting)), { threshold: 0.05 }).observe(voet);
  }

  /* Code kopiëren */
  popup.querySelectorAll('[data-tt-kopieer]').forEach((b) => b.addEventListener('click', () => {
    const tekst = b.querySelector('[data-tt-kopieer-tekst]');
    const klaar = () => { tekst.textContent = 'Gekopieerd!'; setTimeout(() => { tekst.textContent = 'Kopieer code'; }, 2000); };
    if (navigator.clipboard) navigator.clipboard.writeText(b.dataset.ttKopieer).then(klaar, () => {}); else klaar();
  }));

  /* Na succesvolle inschrijving (pagina herlaadt met #SurfPopupForm) direct de bevestiging tonen */
  if (popup.querySelector('[data-surf-popup-success]')) {
    store.set({ ...store.get(), done: true });
    show();
    return;
  }

  const state = store.get();
  if (state.done) return;
  if (window.Shopify && window.Shopify.designMode) return;
  /* elke nieuwe bezoek (sessie) komt hij één keer vanzelf op; in dezelfde sessie alleen nog via de badge */
  let gezien = false;
  try { gezien = sessionStorage.getItem('surfPopupSessie') === '1'; sessionStorage.setItem('surfPopupSessie', '1'); } catch (e) { gezien = state.seen && Date.now() - state.seen < WEEK; }
  if (gezien) { if (teaser) teaser.hidden = false; return; }

  const delay = Math.max(5, Number(popup.dataset.delay) || 12) * 1000;
  setTimeout(show, delay);
  /* of eerder: halverwege de pagina */
  const halverwege = () => {
    if (scrollY + innerHeight > document.documentElement.scrollHeight * 0.5) { removeEventListener('scroll', halverwege); show(); }
  };
  setTimeout(() => addEventListener('scroll', halverwege, { passive: true }), 4000);
  if (window.matchMedia('(pointer: fine)').matches) {
    setTimeout(() => {
      document.addEventListener('mouseout', (e) => {
        if (!e.relatedTarget && e.clientY <= 0) show();
      });
    }, 8000);
  }
})();
