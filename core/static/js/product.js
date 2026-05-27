(function () {
  "use strict";

  const mainImg = document.querySelector("[data-gallery-main]");
  const thumbs = document.querySelectorAll("[data-gallery-thumb]");
  const priceEl = document.getElementById("product-price");
  const oldPriceEl = document.getElementById("product-old-price");
  const saveEl = document.getElementById("product-save");
  const discountBadge = document.getElementById("product-discount-badge");
  const basePrice = priceEl ? parseFloat(priceEl.dataset.basePrice) : 0;
  const baseOldPrice = oldPriceEl ? parseFloat(oldPriceEl.dataset.baseOldPrice) : 0;
  const qtyInput = document.getElementById("product-qty");

  function formatRs(amount) {
    const n = parseFloat(amount);
    if (isNaN(n)) return "Rs 0.00";
    return "Rs " + n.toFixed(2);
  }

  /* ───────── IMAGE HOVER ZOOM (magnifier) ───────── */
  function initImageZoom() {
    const galleryMain = document.querySelector(".gallery-main");
    const wrap = document.querySelector("[data-zoom-wrap]");
    const lens = document.querySelector(".zoom-lens");
    const result = document.querySelector(".zoom-result");
    if (!galleryMain || !wrap || !lens || !result || !mainImg) return;

    const ZOOM = 2.2;
    const lensSize = 120;

    function canZoom() {
      return (
        window.matchMedia("(hover: hover) and (min-width: 1101px)").matches &&
        mainImg.complete &&
        mainImg.naturalWidth > 0
      );
    }

    function refreshZoomBackground() {
      const w = mainImg.offsetWidth;
      const h = mainImg.offsetHeight;
      result.style.backgroundImage = `url("${mainImg.src}")`;
      result.style.backgroundSize = `${w * ZOOM}px ${h * ZOOM}px`;
    }

    function hideZoom() {
      lens.hidden = true;
      result.hidden = true;
      galleryMain.classList.remove("is-zooming");
    }

    wrap.addEventListener("mouseenter", () => {
      if (!canZoom()) return;
      refreshZoomBackground();
      lens.hidden = false;
      result.hidden = false;
      galleryMain.classList.add("is-zooming");
    });

    wrap.addEventListener("mouseleave", hideZoom);

    wrap.addEventListener("mousemove", (e) => {
      if (!galleryMain.classList.contains("is-zooming")) return;

      const rect = wrap.getBoundingClientRect();
      const imgRect = mainImg.getBoundingClientRect();
      const imgW = imgRect.width;
      const imgH = imgRect.height;
      const offsetX = imgRect.left - rect.left;
      const offsetY = imgRect.top - rect.top;

      let x = e.clientX - imgRect.left;
      let y = e.clientY - imgRect.top;
      x = Math.max(0, Math.min(x, imgW));
      y = Math.max(0, Math.min(y, imgH));

      const half = lensSize / 2;
      let lensX = offsetX + x - half;
      let lensY = offsetY + y - half;
      lensX = Math.max(offsetX, Math.min(lensX, offsetX + imgW - lensSize));
      lensY = Math.max(offsetY, Math.min(lensY, offsetY + imgH - lensSize));

      lens.style.width = lensSize + "px";
      lens.style.height = lensSize + "px";
      lens.style.left = lensX + "px";
      lens.style.top = lensY + "px";

      const ratioX = imgW > lensSize ? (x - half) / (imgW - lensSize) : 0;
      const ratioY = imgH > lensSize ? (y - half) / (imgH - lensSize) : 0;
      const clampedX = Math.max(0, Math.min(1, ratioX));
      const clampedY = Math.max(0, Math.min(1, ratioY));

      const bgW = imgW * ZOOM - result.offsetWidth;
      const bgH = imgH * ZOOM - result.offsetHeight;
      result.style.backgroundPosition = `-${clampedX * bgW}px -${clampedY * bgH}px`;
    });

    mainImg.addEventListener("load", refreshZoomBackground);
    window.addEventListener("resize", hideZoom);
  }

  initImageZoom();

  /* ───────── GALLERY THUMBS ───────── */
  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      const url = thumb.dataset.galleryThumb;
      if (!url || !mainImg) return;

      mainImg.style.opacity = "0";
      setTimeout(() => {
        mainImg.src = url;
        mainImg.style.opacity = "1";
      }, 150);

      thumbs.forEach((t) => t.classList.remove("is-active"));
      thumb.classList.add("is-active");
    });
  });

  const lightbox = document.getElementById("gallery-lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const zoomBtn = document.querySelector("[data-gallery-zoom]");
  const lightboxClose = lightbox?.querySelector(".lightbox-close");

  function openLightbox() {
    if (!lightbox || !lightboxImg || !mainImg) return;
    lightboxImg.src = mainImg.src;
    lightbox.hidden = false;
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.hidden = true;
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  zoomBtn?.addEventListener("click", openLightbox);
  lightboxClose?.addEventListener("click", closeLightbox);
  lightbox?.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox && !lightbox.hidden) closeLightbox();
  });

  /* ───────── SKU LOOKUP & VARIANTS ───────── */

  const SKUS = window.GLS_SKUS || [];
  const BASE_PRICE = window.GLS_BASE_PRICE || basePrice;
  const BASE_OLD_PRICE = window.GLS_BASE_OLD_PRICE || baseOldPrice;
  const hasVariants = document.querySelectorAll(".variant-group").length > 0;

  function normalizeCombo(str) {
    return (str || "")
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean)
      .sort()
      .join(",");
  }

  function getSelectedCombo() {
    const parts = [];

    document.querySelectorAll(".variant-group").forEach((group) => {
      const label = group.dataset.variantGroup;
      const selected = group.querySelector(".variant-option.is-selected");

      if (label && selected) {
        const key = label.trim();
        const value = (selected.dataset.value || "").trim();
        parts.push(`${key}:${value}`);
      }
    });

    return normalizeCombo(parts.join(","));
  }

  function findSKU(combo) {
    const normalized = normalizeCombo(combo);
    for (const sku of SKUS) {
      if (normalizeCombo(sku.variant_combo) === normalized) {
        return sku;
      }
    }
    return null;
  }

  /* STOCK HANDLING */
  function updateStockStatus(sku) {
    const stockEl = document.getElementById("product-stock-status");
    const addBtn = document.querySelector("[data-add-cart]");
    const buyBtn = document.querySelector("[data-buy-now]");

    if (!stockEl) return;

    const icon = stockEl.querySelector("i");
    const text = stockEl.querySelector("span");

    if (!sku) {
      stockEl.className = "product-stock out-of-stock";
      if (icon) icon.className = "fas fa-times-circle";
      if (text) text.textContent = "This combination is not available";

      if (addBtn) addBtn.disabled = true;
      if (buyBtn) buyBtn.disabled = true;

      if (qtyInput) {
        qtyInput.max = 1;
        qtyInput.value = 1;
      }
      return;
    }

    const inStock = sku.stock > 0;

    stockEl.className = "product-stock " + (inStock ? "in-stock" : "out-of-stock");
    if (icon) icon.className = inStock ? "fas fa-check-circle" : "fas fa-times-circle";

    if (inStock) {
      text.textContent =
        sku.stock <= 5
          ? `Only ${sku.stock} left — order soon`
          : "In stock — ready to ship";

      if (addBtn) addBtn.disabled = false;
      if (buyBtn) buyBtn.disabled = false;

      if (qtyInput) {
        const maxQty = Math.min(sku.stock, 10);
        qtyInput.max = maxQty;

        if (parseInt(qtyInput.value) > maxQty) {
          qtyInput.value = maxQty;
        }
      }
    } else {
      text.textContent = "Out of stock";

      if (addBtn) addBtn.disabled = true;
      if (buyBtn) buyBtn.disabled = true;

      if (qtyInput) {
        qtyInput.max = 1;
        qtyInput.value = 1;
      }
    }
  }

  /* PRICE UPDATE (FIXED) */
  function updatePrice(sku) {
    let currentPrice = BASE_PRICE;
    let currentOld = BASE_OLD_PRICE;

    if (sku) {
      const adj = parseFloat(sku.price_adjustment || 0);
      currentPrice = BASE_PRICE + adj;
      currentOld = BASE_OLD_PRICE ? BASE_OLD_PRICE + adj : 0;
    }

    if (priceEl) {
      priceEl.textContent = formatRs(currentPrice);
    }

    if (oldPriceEl && currentOld > 0) {
      oldPriceEl.textContent = formatRs(currentOld);
    }

    if (saveEl && currentOld > 0) {
      const save = currentOld - currentPrice;
      saveEl.textContent = "Save Rs " + save.toFixed(2);
      saveEl.hidden = save <= 0;
    }

    if (discountBadge && currentOld > 0) {
      const save = currentOld - currentPrice;
      if (save > 0) {
        const pct = Math.round((save / currentOld) * 100);
        discountBadge.textContent = "-" + pct + "% OFF";
        discountBadge.hidden = false;
      } else {
        discountBadge.hidden = true;
      }
    }
  }

  /* MAIN TRIGGER */
  function onVariantChange() {
    if (SKUS.length === 0) return;

    const combo = hasVariants ? getSelectedCombo() : "";
    const sku = findSKU(combo);

    updatePrice(sku);
    updateStockStatus(sku);
  }

  /* EVENTS */
  document.querySelectorAll(".variant-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      const group = btn.closest(".variant-group");

      group.querySelectorAll(".variant-option").forEach((o) => {
        o.classList.remove("is-selected");
      });

      btn.classList.add("is-selected");

      onVariantChange();
    });
  });

  /* INIT */
  onVariantChange();

  /* ───────── QUANTITY ───────── */
  document.querySelector("[data-qty-minus]")?.addEventListener("click", () => {
    if (!qtyInput) return;
    const val = Math.max(1, parseInt(qtyInput.value, 10) - 1);
    qtyInput.value = val;
  });

  document.querySelector("[data-qty-plus]")?.addEventListener("click", () => {
    if (!qtyInput) return;
    const max = parseInt(qtyInput.max, 10) || 10;
    const val = Math.min(max, parseInt(qtyInput.value, 10) + 1);
    qtyInput.value = val;
  });

  qtyInput?.addEventListener("change", () => {
    const min = parseInt(qtyInput.min, 10) || 1;
    const max = parseInt(qtyInput.max, 10) || 10;
    let val = parseInt(qtyInput.value, 10);
    if (isNaN(val) || val < min) val = min;
    if (val > max) val = max;
    qtyInput.value = val;
  });

  /* ───────── TABS ───────── */
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      if (!target) return;

      tabBtns.forEach((b) => {
        b.classList.remove("is-active");
        b.setAttribute("aria-selected", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-selected", "true");

      tabPanels.forEach((panel) => {
        const isTarget = panel.id === "tab-" + target;
        panel.classList.toggle("is-active", isTarget);
        panel.hidden = !isTarget;
      });
    });
  });

  /* ───────── CART / BUY ───────── */
  function getVariantNote() {
    if (!hasVariants) return "";
    return getSelectedCombo();
  }

  function buildCartPayload(productId) {
    return {
      product_id: productId,
      quantity: qtyInput ? qtyInput.value : "1",
      variant_note: getVariantNote(),
    };
  }

  document.querySelector("[data-add-cart]")?.addEventListener("click", function () {
    const productId = this.dataset.productId;
    if (!productId || !window.GLS?.addToCart) return;

    this.disabled = true;
    window.GLS.addToCart(buildCartPayload(productId)).then((data) => {
      this.disabled = false;
      if (data.ok) {
        window.GLS.updateCartBadge(data.cart_count, data.cart_total);
        const toast = document.createElement("div");
        toast.className = "cart-toast";
        toast.textContent = data.message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
      } else {
        alert(data.error || "Could not add to cart.");
      }
    }).catch(() => {
      this.disabled = false;
      alert("Could not add to cart. Please try again.");
    });
  });

  document.querySelector("[data-buy-now]")?.addEventListener("click", function () {
    const productId = this.dataset.productId;
    if (!productId || !window.GLS?.addToCart) return;

    this.disabled = true;
    window.GLS.addToCart(buildCartPayload(productId)).then((data) => {
      if (data.ok) {
        window.location.href = "/checkout/";
      } else {
        this.disabled = false;
        alert(data.error || "Could not add to cart.");
      }
    });
  });

  document.querySelector("[data-wishlist-form]")?.addEventListener("submit", function (e) {
    e.preventDefault();
    const form = this;
    const fd = new FormData(form);
    fetch(form.action, {
      method: "POST",
      body: fd,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.ok) {
          window.GLS?.updateWishlistBadge(data.wishlist_count);
          const btn = form.querySelector("[data-wishlist-btn]");
          const icon = btn?.querySelector("i");
          if (icon) {
            icon.classList.toggle("far", !data.added);
            icon.classList.toggle("fas", data.added);
          }
          btn?.classList.toggle("is-active", data.added);
        }
      });
  });

  /* ───────── SHARE ───────── */
  document.querySelector('[data-share="copy"]')?.addEventListener("click", async function () {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      const orig = this.innerHTML;
      this.innerHTML = '<i class="fas fa-check" aria-hidden="true"></i>';
      setTimeout(() => {
        this.innerHTML = orig;
      }, 2000);
    } catch {
      prompt("Copy this link:", url);
    }
  });

  /* ───────── REVIEW STARS (UI only) ───────── */
  document.querySelectorAll(".star-input__btn").forEach((btn, index, all) => {
    btn.addEventListener("click", () => {
      all.forEach((b, i) => {
        b.classList.toggle("is-active", i <= index);
        const icon = b.querySelector("i");
        if (icon) {
          icon.classList.toggle("fas", i <= index);
          icon.classList.toggle("far", i > index);
        }
      });
    });
  });
})();