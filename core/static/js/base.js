/**
 * Global Link Store — Base interactions
 */
(function () {
  "use strict";

  const siteHeader = document.querySelector(".site-header");
  const backToTop = document.querySelector(".back-to-top");
  const menuToggle = document.querySelector(".mobile-menu-toggle");
  const menuClose = document.querySelector(".mobile-nav-close");
  const menuPanel = document.querySelector(".mobile-nav-panel");
  const menuOverlay = document.querySelector(".mobile-nav-overlay");

  let headerOffset = 0;

  /* ───────── STICKY HEADER ───────── */
  function updateHeaderOffset() {
    if (!siteHeader) return;
    headerOffset = siteHeader.offsetHeight;
  }

  function onScroll() {
    const scrollY = window.scrollY;

    if (siteHeader) {
      const isSticky = scrollY > 0;
      siteHeader.classList.toggle("is-sticky", isSticky);
      document.body.style.paddingTop = isSticky ? headerOffset + "px" : "";
    }

    if (backToTop) {
      backToTop.classList.toggle("is-visible", scrollY > 400);
    }
  }

  /* ───────── MOBILE MENU ───────── */
  function setMobileMenuOpen(open) {
    if (!menuPanel || !menuOverlay) return;

    menuPanel.classList.toggle("is-open", open);
    menuOverlay.classList.toggle("is-visible", open);
    menuOverlay.hidden = !open;
    menuPanel.setAttribute("aria-hidden", open ? "false" : "true");
    document.body.classList.toggle("mobile-nav-open", open);

    if (menuToggle) {
      menuToggle.setAttribute("aria-expanded", open ? "true" : "false");
      menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      const icon = menuToggle.querySelector("i");
      if (icon) {
        icon.className = open ? "fas fa-times" : "fas fa-bars";
      }
    }
  }

  function initMobileMenu() {
    if (!menuToggle || !menuPanel || !menuOverlay) return;

    menuToggle.addEventListener("click", function () {
      const isOpen = menuPanel.classList.contains("is-open");
      setMobileMenuOpen(!isOpen);
    });

    if (menuClose) {
      menuClose.addEventListener("click", function () {
        setMobileMenuOpen(false);
      });
    }

    menuOverlay.addEventListener("click", function () {
      setMobileMenuOpen(false);
    });

    menuPanel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setMobileMenuOpen(false);
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        setMobileMenuOpen(false);
      }
    });
  }

  /* ───────── BACK TO TOP ───────── */
  function initBackToTop() {
    if (!backToTop) return;

    backToTop.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }

  /* ───────── MESSAGES ───────── */
  function initMessages() {
    document.addEventListener("click", function (e) {
      const btn = e.target.closest(".message-close");
      if (!btn) return;

      const message = btn.closest(".site-message");
      if (!message) return;

      message.style.opacity = "0";
      message.style.transform = "translateY(-8px)";
      message.style.transition = "0.25s ease";

      setTimeout(function () {
        message.remove();
      }, 250);
    });
  }

  /* ───────── AUTOCOMPLETE SEARCH ───────── */
  function initSearchAutocomplete() {
    const input = document.getElementById("search-input");
    const resultsContainer = document.getElementById("search-autocomplete-results");
    if (!input || !resultsContainer) return;

    let debounceTimeout = null;
    let highlightedIndex = -1;

    document.addEventListener("click", function (e) {
      if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.hidden = true;
      }
    });

    input.addEventListener("focus", function () {
      if (resultsContainer.children.length > 0 && input.value.trim().length >= 2) {
        resultsContainer.hidden = false;
      }
    });

    input.addEventListener("input", function () {
      const q = input.value.trim();
      clearTimeout(debounceTimeout);
      highlightedIndex = -1;

      if (q.length < 2) {
        resultsContainer.hidden = true;
        resultsContainer.innerHTML = "";
        return;
      }

      debounceTimeout = setTimeout(function () {
        fetch("/products/search/autocomplete/?q=" + encodeURIComponent(q))
          .then(res => res.json())
          .then(data => {
            resultsContainer.innerHTML = "";
            const items = data.results || [];
            
            if (items.length === 0) {
              const empty = document.createElement("div");
              empty.className = "autocomplete-no-results";
              empty.textContent = "No products found";
              resultsContainer.appendChild(empty);
            } else {
              items.forEach(function (item) {
                const a = document.createElement("a");
                a.className = "autocomplete-item";
                a.href = item.url;
                
                const img = document.createElement("img");
                img.src = item.image ? item.image : "/static/img/placeholder.png";
                img.alt = item.title;
                a.appendChild(img);

                const info = document.createElement("div");
                info.className = "autocomplete-item-info";
                
                const title = document.createElement("span");
                title.className = "autocomplete-item-title";
                title.textContent = item.title;
                info.appendChild(title);

                const meta = document.createElement("span");
                meta.className = "autocomplete-item-meta";
                meta.textContent = (item.brand ? item.brand + " · " : "") + item.category;
                info.appendChild(meta);
                
                a.appendChild(info);

                const price = document.createElement("span");
                price.className = "autocomplete-item-price";
                price.textContent = "Rs " + parseFloat(item.price).toFixed(2);
                a.appendChild(price);

                resultsContainer.appendChild(a);
              });
            }
            resultsContainer.hidden = false;
          })
          .catch(err => {
            console.error("Autocomplete fetch error:", err);
          });
      }, 250);
    });

    input.addEventListener("keydown", function (e) {
      const items = resultsContainer.querySelectorAll(".autocomplete-item");
      if (items.length === 0) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        highlightedIndex = (highlightedIndex + 1) % items.length;
        updateHighlight(items);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        highlightedIndex = (highlightedIndex - 1 + items.length) % items.length;
        updateHighlight(items);
      } else if (e.key === "Enter") {
        if (highlightedIndex >= 0 && highlightedIndex < items.length) {
          e.preventDefault();
          items[highlightedIndex].click();
        }
      } else if (e.key === "Escape") {
        resultsContainer.hidden = true;
        input.blur();
      }
    });

    function updateHighlight(items) {
      items.forEach((item, idx) => {
        item.classList.toggle("highlighted", idx === highlightedIndex);
        if (idx === highlightedIndex) {
          item.scrollIntoView({ block: "nearest" });
        }
      });
    }
  }

  /* ───────── INIT ───────── */
  function init() {
    updateHeaderOffset();
    onScroll();
    initBackToTop();
    initMessages();
    initMobileMenu();
    initSearchAutocomplete();
  }

  /* ───────── EVENTS ───────── */
  window.addEventListener("resize", function () {
    const wasSticky = siteHeader && siteHeader.classList.contains("is-sticky");
    if (wasSticky) {
      document.body.style.paddingTop = "";
      siteHeader.classList.remove("is-sticky");
    }
    updateHeaderOffset();
    if (wasSticky) {
      siteHeader.classList.add("is-sticky");
      document.body.style.paddingTop = headerOffset + "px";
    }
  });

  window.addEventListener("scroll", onScroll, { passive: true });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
