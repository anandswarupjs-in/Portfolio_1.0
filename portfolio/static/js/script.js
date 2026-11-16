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

  /* Scrollspy: highlight nav link matching the section currently in view */
  var links = document.querySelectorAll(".site-nav a[data-section]");
  var path = location.pathname;
  document.querySelectorAll(".site-nav a").forEach(function (a) {
    if (a.dataset.page && path.indexOf("/" + a.dataset.page) === 0) a.classList.add("active");
  });

  if (links.length) {
    /* Build ordered list of [sectionEl, navLink] pairs */
    var pairs = [];
    links.forEach(function (a) {
      var el = document.getElementById(a.dataset.section);
      if (el) pairs.push([el, a]);
    });

    var headerH = 84; /* matches scroll-padding-top in CSS */
    var current = null;

    function setActive(link) {
      if (link === current) return;
      current = link;
      links.forEach(function (a) { a.classList.remove("active"); });
      if (link) {
        link.classList.add("active");
        /* scroll the nav link into view horizontally if nav overflows */
        link.scrollIntoView && link.scrollIntoView({ block: "nearest", inline: "nearest" });
      }
    }

    function onScroll() {
      var scrollY = window.scrollY || window.pageYOffset;
      /* Near bottom → activate last section */
      if ((window.innerHeight + scrollY) >= document.body.scrollHeight - 10) {
        setActive(pairs[pairs.length - 1][1]);
        return;
      }
      /* Walk sections bottom-up; first one whose top is at/above viewport midpoint wins */
      var mid = scrollY + headerH + window.innerHeight * 0.25;
      var active = null;
      for (var i = 0; i < pairs.length; i++) {
        if (pairs[i][0].getBoundingClientRect().top + scrollY <= mid) {
          active = pairs[i][1];
        }
      }
      setActive(active);
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll(); /* run once on load */

    /* Smooth scroll on click + immediately mark as active */
    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var target = document.getElementById(a.dataset.section);
        if (target) {
          e.preventDefault();
          setActive(a);
          target.scrollIntoView({ behavior: "smooth", block: "start" });
          history.pushState(null, "", "#" + a.dataset.section);
        }
      });
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
