(function () {
  "use strict";

  /* ───────── ELEMENT REFS ───────── */
  const mainImg     = document.querySelector("[data-gallery-main]");
  const thumbs      = document.querySelectorAll("[data-gallery-thumb]");
  const priceEl     = document.getElementById("product-price");
  const oldPriceEl  = document.getElementById("product-old-price");
  const saveEl      = document.getElementById("product-save");
  const discountBadge = document.getElementById("product-discount-badge");
  const basePrice   = priceEl   ? parseFloat(priceEl.dataset.basePrice)   : 0;
  const baseOldPrice = oldPriceEl ? parseFloat(oldPriceEl.dataset.baseOldPrice) : 0;
  const qtyInput    = document.getElementById("product-qty");

  /* ───────── UTILS ───────── */
  function formatRs(amount) {
    const n = parseFloat(amount);
    return isNaN(n) ? "Rs 0.00" : "Rs " + n.toFixed(2);
  }

  function showToast(message) {
    const existing = document.querySelector(".cart-toast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.className = "cart-toast";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = "none";
      toast.style.opacity = "0";
      toast.style.transition = "opacity .3s";
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  /* ───────── IMAGE HOVER ZOOM (magnifier) ───────── */
  function initImageZoom() {
    const galleryMain = document.querySelector(".gallery-main");
    const wrap   = document.querySelector("[data-zoom-wrap]");
    const lens   = document.querySelector(".zoom-lens");
    const result = document.querySelector(".zoom-result");
    if (!galleryMain || !wrap || !lens || !result || !mainImg) return;

    const ZOOM     = 2.2;
    const lensSize = 120;

    function canZoom() {
      return (
        window.matchMedia("(hover: hover) and (min-width: 1181px)").matches &&
        mainImg.complete &&
        mainImg.naturalWidth > 0
      );
    }

    function refreshZoomBackground() {
      const w = mainImg.offsetWidth;
      const h = mainImg.offsetHeight;
      result.style.backgroundImage  = `url("${mainImg.src}")`;
      result.style.backgroundSize   = `${w * ZOOM}px ${h * ZOOM}px`;
    }

    function hideZoom() {
      lens.hidden   = true;
      result.hidden = true;
      galleryMain.classList.remove("is-zooming");
    }

    wrap.addEventListener("mouseenter", () => {
      if (!canZoom()) return;
      refreshZoomBackground();
      lens.hidden   = false;
      result.hidden = false;
      galleryMain.classList.add("is-zooming");
    });

    wrap.addEventListener("mouseleave", hideZoom);

    wrap.addEventListener("mousemove", (e) => {
      if (!galleryMain.classList.contains("is-zooming")) return;

      const rect   = wrap.getBoundingClientRect();
      const imgRect = mainImg.getBoundingClientRect();
      const imgW   = imgRect.width;
      const imgH   = imgRect.height;
      const offsetX = imgRect.left - rect.left;
      const offsetY = imgRect.top  - rect.top;

      let x = e.clientX - imgRect.left;
      let y = e.clientY - imgRect.top;
      x = Math.max(0, Math.min(x, imgW));
      y = Math.max(0, Math.min(y, imgH));

      const half = lensSize / 2;
      let lensX = offsetX + x - half;
      let lensY = offsetY + y - half;
      lensX = Math.max(offsetX, Math.min(lensX, offsetX + imgW - lensSize));
      lensY = Math.max(offsetY, Math.min(lensY, offsetY + imgH - lensSize));

      lens.style.width  = lensSize + "px";
      lens.style.height = lensSize + "px";
      lens.style.left   = lensX + "px";
      lens.style.top    = lensY + "px";

      const ratioX   = imgW > lensSize ? (x - half) / (imgW - lensSize) : 0;
      const ratioY   = imgH > lensSize ? (y - half) / (imgH - lensSize) : 0;
      const clampedX = Math.max(0, Math.min(1, ratioX));
      const clampedY = Math.max(0, Math.min(1, ratioY));

      const bgW = imgW * ZOOM - result.offsetWidth;
      const bgH = imgH * ZOOM - result.offsetHeight;
      result.style.backgroundPosition = `-${clampedX * bgW}px -${clampedY * bgH}px`;
    });

    mainImg.addEventListener("load",  refreshZoomBackground);
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

  /* ───────── LIGHTBOX ───────── */
  const lightbox      = document.getElementById("gallery-lightbox");
  const lightboxImg   = document.getElementById("lightbox-img");
  const zoomBtn       = document.querySelector("[data-gallery-zoom]");
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
  lightbox?.addEventListener("click", (e) => { if (e.target === lightbox) closeLightbox(); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox && !lightbox.hidden) closeLightbox();
  });

  /* ───────── SKU LOOKUP & VARIANTS ───────── */
  const SKUS         = window.GLS_SKUS || [];
  const BASE_PRICE   = window.GLS_BASE_PRICE   || basePrice;
  const BASE_OLD_PRICE = window.GLS_BASE_OLD_PRICE || baseOldPrice;
  const hasVariants  = document.querySelectorAll(".variant-group").length > 0;

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
      const label    = group.dataset.variantGroup;
      const selected = group.querySelector(".variant-option.is-selected");
      if (label && selected) {
        parts.push(`${label.trim()}:${(selected.dataset.value || "").trim()}`);
      }
    });
    return normalizeCombo(parts.join(","));
  }

  function findSKU(combo) {
    const normalized = normalizeCombo(combo);
    for (const sku of SKUS) {
      if (normalizeCombo(sku.variant_combo) === normalized) return sku;
    }
    return null;
  }

  /* Stock */
  function updateStockStatus(sku) {
    const stockEl = document.getElementById("product-stock-status");
    const addBtn  = document.querySelector("[data-add-cart]");
    const buyBtn  = document.querySelector("[data-buy-now]");
    if (!stockEl) return;

    const icon = stockEl.querySelector("i");
    const text = stockEl.querySelector("span");

    if (!sku) {
      stockEl.className = "product-stock out-of-stock";
      if (icon) icon.className = "fas fa-times-circle";
      if (text) text.textContent = "This combination is not available";
      if (addBtn) addBtn.disabled = true;
      if (buyBtn) buyBtn.disabled = true;
      if (qtyInput) { qtyInput.max = 1; qtyInput.value = 1; }
      return;
    }

    const inStock = sku.stock > 0;
    stockEl.className = "product-stock " + (inStock ? "in-stock" : "out-of-stock");
    if (icon) icon.className = inStock ? "fas fa-check-circle" : "fas fa-times-circle";

    if (inStock) {
      text.textContent = sku.stock <= 5 ? `Only ${sku.stock} left — order soon` : "In stock — ready to ship";
      if (addBtn) addBtn.disabled = false;
      if (buyBtn) buyBtn.disabled = false;
      if (qtyInput) {
        const maxQty = Math.min(sku.stock, 10);
        qtyInput.max = maxQty;
        if (parseInt(qtyInput.value) > maxQty) qtyInput.value = maxQty;
      }
    } else {
      text.textContent = "Out of stock";
      if (addBtn) addBtn.disabled = true;
      if (buyBtn) buyBtn.disabled = true;
      if (qtyInput) { qtyInput.max = 1; qtyInput.value = 1; }
    }
  }

  /* Price */
  function updatePrice(sku) {
    let currentPrice = BASE_PRICE;
    let currentOld   = BASE_OLD_PRICE;

    if (sku) {
      const adj  = parseFloat(sku.price_adjustment || 0);
      currentPrice = BASE_PRICE + adj;
      currentOld   = BASE_OLD_PRICE ? BASE_OLD_PRICE + adj : 0;
    }

    if (priceEl)   priceEl.textContent = formatRs(currentPrice);

    if (oldPriceEl && currentOld > 0) oldPriceEl.textContent = formatRs(currentOld);

    if (saveEl && currentOld > 0) {
      const save = currentOld - currentPrice;
      saveEl.textContent = "Save Rs " + save.toFixed(2);
      saveEl.hidden = save <= 0;
    }

    if (discountBadge && currentOld > 0) {
      const save = currentOld - currentPrice;
      if (save > 0) {
        discountBadge.textContent = "-" + Math.round((save / currentOld) * 100) + "% OFF";
        discountBadge.hidden = false;
      } else {
        discountBadge.hidden = true;
      }
    }
  }

  function onVariantChange() {
    if (SKUS.length === 0) return;
    const combo = hasVariants ? getSelectedCombo() : "";
    const sku   = findSKU(combo);
    updatePrice(sku);
    updateStockStatus(sku);
  }

  document.querySelectorAll(".variant-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.closest(".variant-group").querySelectorAll(".variant-option")
        .forEach((o) => o.classList.remove("is-selected"));
      btn.classList.add("is-selected");
      onVariantChange();
    });
  });

  onVariantChange();

  /* ───────── QUANTITY ───────── */
  document.querySelector("[data-qty-minus]")?.addEventListener("click", () => {
    if (!qtyInput) return;
    qtyInput.value = Math.max(1, parseInt(qtyInput.value, 10) - 1);
  });

  document.querySelector("[data-qty-plus]")?.addEventListener("click", () => {
    if (!qtyInput) return;
    const max = parseInt(qtyInput.max, 10) || 10;
    qtyInput.value = Math.min(max, parseInt(qtyInput.value, 10) + 1);
  });

  qtyInput?.addEventListener("change", () => {
    const min = parseInt(qtyInput.min, 10) || 1;
    const max = parseInt(qtyInput.max, 10) || 10;
    let val   = parseInt(qtyInput.value, 10);
    if (isNaN(val) || val < min) val = min;
    if (val > max) val = max;
    qtyInput.value = val;
  });

  /* ───────── TABS ───────── */
  const tabBtns   = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  function activateTab(tabName) {
    tabBtns.forEach((b) => {
      const active = b.dataset.tab === tabName;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-selected", active ? "true" : "false");
    });
    tabPanels.forEach((panel) => {
      const active = panel.id === "tab-" + tabName;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
  }

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => activateTab(btn.dataset.tab));
  });

  /* "View all specs" link jumps to the specifications tab */
  document.querySelectorAll("[data-tab-jump]").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const target = link.dataset.tabJump;
      activateTab(target);
      document.querySelector(".product-tabs-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  /* ───────── CART / BUY ───────── */
  function getVariantNote() {
    return hasVariants ? getSelectedCombo() : "";
  }

  function buildCartPayload(productId) {
    return {
      product_id:   productId,
      quantity:     qtyInput ? qtyInput.value : "1",
      variant_note: getVariantNote(),
    };
  }

  document.querySelector("[data-add-cart]")?.addEventListener("click", function () {
    const productId = this.dataset.productId;
    if (!productId || !window.GLS?.addToCart) return;

    const originalHtml = this.innerHTML;
    this.disabled   = true;
    this.innerHTML  = '<i class="fas fa-spinner fa-spin"></i> Adding…';

    window.GLS.addToCart(buildCartPayload(productId))
      .then((data) => {
        this.disabled  = false;
        this.innerHTML = originalHtml;
        if (data.ok) {
          window.GLS.updateCartBadge(data.cart_count, data.cart_total);
          showToast(data.message || "Added to cart!");
        } else {
          alert(data.error || "Could not add to cart.");
        }
      })
      .catch(() => {
        this.disabled  = false;
        this.innerHTML = originalHtml;
        alert("Could not add to cart. Please try again.");
      });
  });

  document.querySelector("[data-buy-now]")?.addEventListener("click", function () {
    const productId = this.dataset.productId;
    if (!productId || !window.GLS?.addToCart) return;

    const originalHtml = this.innerHTML;
    this.disabled  = true;
    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Please wait…';

    window.GLS.addToCart(buildCartPayload(productId)).then((data) => {
      if (data.ok) {
        window.location.href = "/checkout/";
      } else {
        this.disabled  = false;
        this.innerHTML = originalHtml;
        alert(data.error || "Could not add to cart.");
      }
    });
  });

  /* ───────── WISHLIST ───────── */
  document.querySelector("[data-wishlist-form]")?.addEventListener("submit", function (e) {
    e.preventDefault();
    fetch(this.action, {
      method:  "POST",
      body:    new FormData(this),
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        if (!data.ok) return;
        window.GLS?.updateWishlistBadge(data.wishlist_count);
        const btn  = this.querySelector("[data-wishlist-btn]");
        const icon = btn?.querySelector("i");
        if (icon) {
          icon.classList.toggle("far", !data.added);
          icon.classList.toggle("fas",  data.added);
        }
        btn?.classList.toggle("is-active", data.added);
        showToast(data.added ? "Added to wishlist!" : "Removed from wishlist");
      });
  });

  /* ───────── SHARE ───────── */
  document.querySelector('[data-share="copy"]')?.addEventListener("click", async function () {
    const url  = window.location.href;
    const icon = this.querySelector("i");
    try {
      await navigator.clipboard.writeText(url);
      if (icon) { icon.className = "fas fa-check"; }
      setTimeout(() => { if (icon) icon.className = "fas fa-link"; }, 2000);
      showToast("Link copied to clipboard!");
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