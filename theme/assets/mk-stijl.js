/* ============================================================
   MERKSTIJL · beweging bij het scrollen (vanilla, geen libraries)
   - Gewone scroll van de browser: geen smooth-scroll-library.
   - Elke scroll-handler is passive en rekent hooguit één keer per
     frame (requestAnimationFrame). De JS schrijft alleen een getal
     (--p) of een transform; de CSS doet de rest.
   - Werkt opnieuw na wijzigingen in de thema-editor van Shopify.
   ============================================================ */
(function () {
  "use strict";
  if (window.__mkStijl) return;
  window.__mkStijl = true;

  var stil = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var editor = !!(window.Shopify && window.Shopify.designMode);
  if (editor) document.documentElement.classList.add("mk-editor");

  var klem = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var perFrame = function (fn) { var raf = 0; return function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(fn); }; };
  var luister = function (fn) {
    var tik = perFrame(fn);
    window.addEventListener("scroll", tik, { passive: true });
    window.addEventListener("resize", tik);
    fn();
  };

  /* Opkomen: één keer, zodra 5% van het element in beeld is
     (met 8% marge van onderen). Wat al in beeld staat komt meteen
     op. Vangnet: na 2 seconden is alles zichtbaar. */
  function opkomen(root) {
    var els = Array.prototype.slice.call(root.querySelectorAll(".mk-in:not(.is-zichtbaar)"));
    if (!els.length) return;
    var alles = function () { els.forEach(function (el) { el.classList.add("is-zichtbaar"); }); };
    if (editor || !("IntersectionObserver" in window)) return alles();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-zichtbaar"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    var vh = window.innerHeight || 800;
    els.forEach(function (el) {
      if (el.getBoundingClientRect().top < vh * 1.05) el.classList.add("is-zichtbaar");
      else io.observe(el);
    });
    setTimeout(alles, 2000);
  }

  /* Gepinde sectie: de sectie is hoger dan het scherm en heeft een
     sticky kind. --p = 0 als de sectie bovenaan het scherm komt,
     1 als de onderkant onderaan het scherm komt. */
  function scrub(root) {
    root.querySelectorAll("[data-mk-scrub]:not([data-mk-klaar])").forEach(function (el) {
      el.setAttribute("data-mk-klaar", "");
      if (editor) { el.style.setProperty("--p", "0"); return; }
      luister(function () {
        var r = el.getBoundingClientRect();
        var totaal = r.height - window.innerHeight;
        var p = stil ? 1 : klem(totaal > 0 ? -r.top / totaal : 0, 0, 1);
        el.style.setProperty("--p", p.toFixed(4));
      });
    });
  }

  /* Woorden die één voor één oplichten terwijl de alinea door beeld
     schuift (van 85% tot 45% van de schermhoogte). */
  function woorden(root) {
    root.querySelectorAll("[data-mk-woorden]:not([data-mk-klaar])").forEach(function (p) {
      p.setAttribute("data-mk-klaar", "");
      var w = p.textContent.trim().split(/\s+/), n = w.length;
      p.textContent = "";
      w.forEach(function (woord, i) {
        var s = document.createElement("span");
        s.textContent = woord + (i < n - 1 ? " " : "");
        s.style.opacity = "calc(0.16 + 0.84 * clamp(0, calc(var(--p) * " + (n + 2) + " - " + i + "), 1))";
        s.style.transition = "opacity .15s linear";
        p.appendChild(s);
      });
      if (stil || editor) { p.style.setProperty("--p", "1"); return; }
      luister(function () {
        var r = p.getBoundingClientRect(), vh = window.innerHeight;
        var v = (vh * 0.85 - r.top) / (vh * 0.4 + r.height);
        p.style.setProperty("--p", klem(v, 0, 1).toFixed(4));
      });
    });
  }

  /* Parallax: data-mk-parallax="0.06" = verschuiving als fractie van
     de schermhoogte (negatief = tegen de scroll in). Rekent alleen
     zolang het element in de buurt van het scherm is. */
  function parallax(root) {
    if (stil || editor) return;
    root.querySelectorAll("[data-mk-parallax]:not([data-mk-klaar])").forEach(function (el) {
      el.setAttribute("data-mk-klaar", "");
      var snelheid = parseFloat(el.getAttribute("data-mk-parallax")) || 0.06;
      el.style.willChange = "transform";
      var reken = function () {
        var r = el.getBoundingClientRect(), vh = window.innerHeight;
        var p = klem((vh / 2 - (r.top + r.height / 2)) / (vh / 2 + r.height / 2), -1, 1);
        el.style.transform = "translate3d(0," + (-p * snelheid * vh).toFixed(1) + "px,0)";
      };
      var tik = perFrame(reken), aan = false;
      new IntersectionObserver(function (e) {
        if (e[0].isIntersecting && !aan) { aan = true; window.addEventListener("scroll", tik, { passive: true }); tik(); }
        if (!e[0].isIntersecting && aan) { aan = false; window.removeEventListener("scroll", tik); }
      }, { rootMargin: "20% 0px" }).observe(el);
    });
  }

  /* Kanteling op de muis: data-mk-kantel="9" (max. graden). */
  function kantel(root) {
    if (stil || !window.matchMedia("(hover: hover)").matches) return;
    root.querySelectorAll("[data-mk-kantel]:not([data-mk-klaar])").forEach(function (el) {
      el.setAttribute("data-mk-klaar", "");
      var max = parseFloat(el.getAttribute("data-mk-kantel")) || 9;
      el.style.transition = "transform .4s var(--mk-ease)";
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = "perspective(1100px) rotateY(" + x * max + "deg) rotateX(" + -y * max + "deg)";
      });
      el.addEventListener("mouseleave", function () { el.style.transform = ""; });
    });
  }

  /* Leesbalk bovenaan: aan via {% render 'mk-stijl', leesbalk: true %}
     of door zelf een <div class="mk-leesbalk"></div> te plaatsen. */
  function leesbalk() {
    var bar = document.querySelector(".mk-leesbalk");
    if (!bar && document.documentElement.hasAttribute("data-mk-leesbalk")) {
      bar = document.createElement("div");
      bar.className = "mk-leesbalk";
      bar.setAttribute("aria-hidden", "true");
      document.body.appendChild(bar);
    }
    if (!bar || bar.hasAttribute("data-mk-klaar")) return;
    bar.setAttribute("data-mk-klaar", "");
    luister(function () {
      var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
      bar.style.transform = "scaleX(" + (max > 0 ? h.scrollTop / max : 0) + ")";
    });
  }

  function start(root) {
    root = root || document;
    opkomen(root); scrub(root); woorden(root); parallax(root); kantel(root); leesbalk();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { start(); });
  else start();

  /* Thema-editor: een sectie die opnieuw wordt geladen, opnieuw starten. */
  document.addEventListener("shopify:section:load", function (e) { start(e.target); });
})();
