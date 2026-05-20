/**
 * Global Link Store — Base interactions (sticky nav, back to top)
 */
(function () {
  "use strict";

  const navbar = document.querySelector(".navbar");
  const backToTop = document.querySelector(".back-to-top");
  const topBar = document.querySelector(".site-header");

  let navbarOffset = 0;

  function updateNavbarOffset() {
    if (!navbar || !topBar) return;
    navbarOffset = topBar.offsetHeight;
  }

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

  function initBackToTop() {
    if (!backToTop) return;
    backToTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  window.addEventListener("resize", updateNavbarOffset);
  window.addEventListener("scroll", onScroll, { passive: true });

  document.addEventListener("DOMContentLoaded", function () {
    updateNavbarOffset();
    initBackToTop();
    onScroll();
  });
})();
