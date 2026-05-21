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

  /* ───────── INIT ───────── */
  function init() {
    updateHeaderOffset();
    onScroll();
    initBackToTop();
    initMessages();
    initMobileMenu();
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
