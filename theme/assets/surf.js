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
  const KEY = 'surfPopup';
  const WEEK = 7 * 24 * 60 * 60 * 1000;
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; } },
    set(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* privé-venster */ } },
  };
  const show = () => {
    if (!popup.hidden) return;
    popup.hidden = false;
    store.set({ ...store.get(), seen: Date.now() });
    popup.querySelector('input[type=email], [data-surf-popup-close]').focus();
  };
  const hide = () => { popup.hidden = true; };

  popup.querySelector('[data-surf-popup-close]').addEventListener('click', hide);
  popup.addEventListener('click', (e) => { if (e.target === popup) hide(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hide(); });
  popup.querySelector('form')?.addEventListener('submit', () => store.set({ ...store.get(), done: true }));

  /* Na succesvolle inschrijving (pagina herlaadt met #SurfPopupForm) direct de bevestiging tonen */
  if (popup.querySelector('[data-surf-popup-success]')) {
    store.set({ ...store.get(), done: true });
    popup.hidden = false;
    return;
  }

  const state = store.get();
  if (state.done || (state.seen && Date.now() - state.seen < WEEK)) return;
  if (window.Shopify && window.Shopify.designMode) return;

  const delay = Math.max(5, Number(popup.dataset.delay) || 120) * 1000;
  setTimeout(show, delay);
  if (window.matchMedia('(pointer: fine)').matches) {
    setTimeout(() => {
      document.addEventListener('mouseout', (e) => {
        if (!e.relatedTarget && e.clientY <= 0) show();
      });
    }, 8000);
  }
})();
