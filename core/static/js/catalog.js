(function () {
  "use strict";

  const filtersPanel = document.getElementById("catalog-filters");
  const filtersOverlay = document.querySelector("[data-filters-overlay]");
  const toggleBtn = document.querySelector("[data-filters-toggle]");
  const closeBtn = document.querySelector("[data-filters-close]");

  function openFilters() {
    filtersPanel?.classList.add("is-open");
    if (filtersOverlay) {
      filtersOverlay.hidden = false;
    }
    toggleBtn?.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  function closeFilters() {
    filtersPanel?.classList.remove("is-open");
    if (filtersOverlay) {
      filtersOverlay.hidden = true;
    }
    toggleBtn?.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }

  toggleBtn?.addEventListener("click", openFilters);
  closeBtn?.addEventListener("click", closeFilters);
  filtersOverlay?.addEventListener("click", closeFilters);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && filtersPanel?.classList.contains("is-open")) {
      closeFilters();
    }
  });

  document.querySelectorAll("[data-auto-submit]").forEach((el) => {
    el.addEventListener("change", () => {
      el.closest("form")?.submit();
    });
  });

  const cartButtons = document.querySelectorAll(".catalog-grid .btn-cart");
  cartButtons.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      if (this.getAttribute("href") && this.getAttribute("href") !== "#") return;
      e.preventDefault();
      const title = this.closest(".product-card")?.querySelector(".title")?.innerText;
      if (title) alert(title + " added to cart!");
    });
  });
})();
