(function () {
  "use strict";

  /* Mobile navigation */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  function setNav(open) {
    nav.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () { setNav(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setNav(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { setNav(false); toggle.focus(); }
    });
  }

  /* Active nav link: current page, or section in view on the home page */
  var links = document.querySelectorAll(".site-nav a");
  var path = location.pathname;
  links.forEach(function (a) {
    if (a.dataset.page && path.indexOf("/" + a.dataset.page) === 0) a.classList.add("active");
  });
  if ("IntersectionObserver" in window && document.getElementById("home")) {
    var map = {};
    links.forEach(function (a) { if (a.dataset.section) map[a.dataset.section] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          links.forEach(function (a) { a.classList.remove("active"); });
          map[en.target.id].classList.add("active");
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    ["home", "about", "skills", "projects", "achievements", "trainings", "contact"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) io.observe(el);
    });
  }

  /* Toasts fade after a few seconds */
  document.querySelectorAll(".toast").forEach(function (t) {
    setTimeout(function () { t.style.opacity = "0"; setTimeout(function () { t.remove(); }, 500); }, 6000);
  });

  /* Live project search and filters (progressive enhancement over the GET form) */
  var form = document.getElementById("project-filters");
  if (form) {
    var q = form.elements.q, cat = form.elements.category, tech = form.elements.tech;
    var cards = Array.prototype.slice.call(document.querySelectorAll("#project-grid .project-card"));
    var empty = document.getElementById("empty-state");
    var count = document.getElementById("result-count");
    var featured = document.getElementById("featured-block");
    var timer;
    var apply = function () {
      var term = q.value.trim().toLowerCase(), c = cat.value, t = tech.value.toLowerCase(), shown = 0;
      cards.forEach(function (card) {
        var ok = (!term || card.dataset.search.indexOf(term) !== -1) &&
          (!c || card.dataset.category === c) &&
          (!t || card.dataset.tech.split("|").indexOf(t) !== -1);
        card.hidden = !ok;
        if (ok) shown++;
      });
      if (empty) empty.hidden = shown !== 0;
      if (count) count.textContent = "(" + shown + ")";
      if (featured) featured.hidden = !!(term || c || t);
      var params = new URLSearchParams();
      if (term) params.set("q", q.value.trim());
      if (c) params.set("category", c);
      if (tech.value) params.set("tech", tech.value);
      var qs = params.toString();
      history.replaceState(null, "", location.pathname + (qs ? "?" + qs : ""));
    };
    form.addEventListener("submit", function (e) { e.preventDefault(); apply(); });
    q.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(apply, 120); });
    cat.addEventListener("change", apply);
    tech.addEventListener("change", apply);
    var reset = document.getElementById("filters-reset");
    if (reset) reset.addEventListener("click", function (e) {
      e.preventDefault(); form.reset(); q.value = ""; cat.value = ""; tech.value = ""; apply();
    });
  }

  /* Gallery lightbox with keyboard support */
  var dialog = document.getElementById("lightbox");
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-lightbox]"));
  if (dialog && items.length && typeof dialog.showModal === "function") {
    var img = document.getElementById("lb-img"), cap = document.getElementById("lb-caption");
    var index = 0, opener = null;
    var show = function (i) {
      index = (i + items.length) % items.length;
      var el = items[index];
      img.src = el.dataset.full;
      img.alt = el.dataset.alt || el.dataset.caption || "";
      cap.textContent = el.dataset.caption || "";
    };
    items.forEach(function (el, i) {
      el.addEventListener("click", function () { opener = el; show(i); dialog.showModal(); });
    });
    var multi = items.length > 1;
    dialog.querySelector(".lb-prev").hidden = !multi;
    dialog.querySelector(".lb-next").hidden = !multi;
    dialog.querySelector(".lb-prev").addEventListener("click", function () { show(index - 1); });
    dialog.querySelector(".lb-next").addEventListener("click", function () { show(index + 1); });
    dialog.querySelector(".lb-close").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("keydown", function (e) {
      if (!multi) return;
      if (e.key === "ArrowLeft") show(index - 1);
      if (e.key === "ArrowRight") show(index + 1);
    });
    dialog.addEventListener("close", function () { if (opener) opener.focus(); });
  }
})();
