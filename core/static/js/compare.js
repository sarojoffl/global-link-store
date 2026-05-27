(function () {
  "use strict";

  const STORAGE_KEY = "gls_compare";
  const MAX_ITEMS = 3;

  window.GLS = window.GLS || {};

  function readList() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch {
      return [];
    }
  }

  function writeList(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, MAX_ITEMS)));
    updateBadge();
  }

  function getIds() {
    return readList().map((item) => item.id);
  }

  function compareUrl() {
    const ids = getIds();
    if (!ids.length) {
      return "/products/compare/";
    }
    return "/products/compare/?ids=" + ids.join(",");
  }

  function updateBadge() {
    const count = readList().length;
    document.querySelectorAll("[data-compare-count]").forEach((el) => {
      el.textContent = String(count);
      el.hidden = count <= 0;
    });
    document.querySelectorAll("[data-compare-link]").forEach((link) => {
      link.href = compareUrl();
    });
  }

  function showToast(message) {
    const existing = document.querySelector(".compare-toast");
    if (existing) existing.remove();
    const toast = document.createElement("div");
    toast.className = "compare-toast";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2800);
  }

  window.GLS.addToCompare = function (product) {
    if (!product || !product.id) return false;

    const id = parseInt(product.id, 10);
    const list = readList();

    if (list.some((item) => item.id === id)) {
      showToast("Already in compare list.");
      window.location.href = compareUrl();
      return false;
    }

    if (list.length >= MAX_ITEMS) {
      showToast("Compare list is full (3 products). Remove one to add another.");
      return false;
    }

    list.push({
      id: id,
      slug: product.slug || "",
      title: product.title || "Product",
    });
    writeList(list);
    showToast("Added to compare.");
    updateCompareButtons();
    return true;
  };

  window.GLS.removeFromCompare = function (productId) {
    const id = parseInt(productId, 10);
    writeList(readList().filter((item) => item.id !== id));
    updateCompareButtons();
    window.location.href = compareUrl();
  };

  window.GLS.clearCompare = function () {
    writeList([]);
    updateCompareButtons();
    window.location.href = "/products/compare/";
  };

  function updateCompareButtons() {
    const ids = new Set(getIds());
    document.querySelectorAll("[data-compare]").forEach((btn) => {
      const pid = parseInt(btn.dataset.productId, 10);
      const inList = ids.has(pid);
      btn.classList.toggle("is-active", inList);
      btn.setAttribute("aria-pressed", inList ? "true" : "false");
    });
  }

  function handleCompareClick(e) {
    const btn = e.target.closest("button[data-compare][data-product-id]");
    if (!btn) return;
    e.preventDefault();
    window.GLS.addToCompare({
      id: btn.dataset.productId,
      slug: btn.dataset.productSlug,
      title: btn.dataset.productTitle,
    });
  }

  function init() {
    updateBadge();
    updateCompareButtons();

    document.addEventListener("click", handleCompareClick);

    document.querySelectorAll("[data-compare-remove]").forEach((btn) => {
      btn.addEventListener("click", () => {
        window.GLS.removeFromCompare(btn.dataset.compareRemove);
      });
    });

    document.querySelector("[data-compare-clear]")?.addEventListener("click", () => {
      window.GLS.clearCompare();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
