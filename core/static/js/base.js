/**
 * Global Link Store — Base interactions
 */
(function () {
  "use strict";

  const navbar = document.querySelector(".navbar");
  const backToTop = document.querySelector(".back-to-top");
  const topBar = document.querySelector(".site-header");

  let navbarOffset = 0;

  /* ───────── NAVBAR OFFSET ───────── */
  function updateNavbarOffset() {
    if (!navbar || !topBar) return;
    navbarOffset = topBar.offsetHeight;
  }

  /* ───────── SCROLL HANDLER ───────── */
  function onScroll() {
    const scrollY = window.scrollY;

    if (navbar) {
      if (scrollY > navbarOffset) {
        navbar.classList.add("is-sticky");
        document.body.style.paddingTop = navbar.offsetHeight + "px";
      } else {
        navbar.classList.remove("is-sticky");
        document.body.style.paddingTop = "";
      }
    }

    if (backToTop) {
      backToTop.classList.toggle("is-visible", scrollY > 400);
    }
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

      setTimeout(() => {
        message.remove();
      }, 250);
    });
  }

  /* ───────── INIT ───────── */
  function init() {
    updateNavbarOffset();
    initBackToTop();
    initMessages();
  }

  /* ───────── EVENTS ───────── */
  window.addEventListener("resize", updateNavbarOffset);
  window.addEventListener("scroll", onScroll, { passive: true });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();