(function () {
  "use strict";

  document.querySelectorAll(".cart-qty-form [data-qty-minus]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.parentElement?.querySelector(".qty-input");
      if (input) input.value = Math.max(1, parseInt(input.value, 10) - 1);
    });
  });

  document.querySelectorAll(".cart-qty-form [data-qty-plus]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.parentElement?.querySelector(".qty-input");
      const max = parseInt(input?.max, 10) || 10;
      if (input) input.value = Math.min(max, parseInt(input.value, 10) + 1);
    });
  });

  function getCsrfToken() {
    const input = document.querySelector("input[name=csrfmiddlewaretoken]");
    if (input) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  window.GLS = window.GLS || {};

  window.GLS.addToCart = function (payload) {
    return fetch("/cart/add/ajax/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCsrfToken(),
      },
      body: new URLSearchParams(payload).toString(),
    }).then((r) => r.json());
  };

  window.GLS.updateCartBadge = function (count, total) {
    const badge = document.getElementById("cart-count");
    const totalEl = document.querySelector(".cart-total");
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? "" : "none";
    }
    if (totalEl) totalEl.textContent = "Rs " + parseFloat(total).toFixed(2);
  };

  window.GLS.updateWishlistBadge = function (count) {
    document.querySelectorAll("[data-wishlist-count]").forEach((el) => {
      el.textContent = count;
      el.hidden = count <= 0;
    });
  };

  const addressSelect = document.getElementById("id_address_id");
  const saveAddressBlock = document.getElementById("checkout-save-address");
  const saveAddressCheckbox = document.getElementById("id_save_address");
  const saveAddressExtra = document.getElementById("checkout-save-address-extra");

  function toggleSaveAddressUI() {
    if (!saveAddressBlock || !addressSelect) return;
    const usingSaved = Boolean(addressSelect.value);
    saveAddressBlock.hidden = usingSaved;
    if (usingSaved && saveAddressCheckbox) {
      saveAddressCheckbox.checked = false;
      if (saveAddressExtra) saveAddressExtra.hidden = true;
    }
  }

  function toggleSaveAddressExtra() {
    if (!saveAddressExtra || !saveAddressCheckbox) return;
    saveAddressExtra.hidden = !saveAddressCheckbox.checked;
  }

  if (addressSelect) {
    addressSelect.addEventListener("change", toggleSaveAddressUI);
    toggleSaveAddressUI();
  }
  if (saveAddressCheckbox) {
    saveAddressCheckbox.addEventListener("change", toggleSaveAddressExtra);
    toggleSaveAddressExtra();
  }

  /* ───────── Newsletter (footer) ───────── */
  document.querySelectorAll("[data-newsletter-form]").forEach((form) => {
    const feedback = form.parentElement?.querySelector("[data-newsletter-feedback]");
    const submitBtn = form.querySelector("[data-newsletter-submit]");

    form.addEventListener("submit", (e) => {
      e.preventDefault();

      const emailInput = form.querySelector('input[name="email"]');
      const email = (emailInput?.value || "").trim();
      if (!email) {
        showNewsletterFeedback(feedback, "Please enter your email address.", false);
        return;
      }

      if (submitBtn) submitBtn.disabled = true;
      showNewsletterFeedback(feedback, "", false, true);

      fetch(form.action, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCsrfToken(),
        },
        body: new URLSearchParams({ email }).toString(),
      })
        .then((r) => r.json().then((data) => ({ ok: r.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.ok) {
            if (emailInput) emailInput.value = "";
            showNewsletterFeedback(feedback, data.message, true);
          } else {
            showNewsletterFeedback(
              feedback,
              data.error || "Could not subscribe. Please try again.",
              false,
            );
          }
        })
        .catch(() => {
          showNewsletterFeedback(feedback, "Could not subscribe. Please try again.", false);
        })
        .finally(() => {
          if (submitBtn) submitBtn.disabled = false;
        });
    });
  });

  function showNewsletterFeedback(el, text, success, hide) {
    if (!el) return;
    if (hide || !text) {
      el.hidden = true;
      el.textContent = "";
      el.classList.remove("is-success", "is-error");
      return;
    }
    el.hidden = false;
    el.textContent = text;
    el.classList.toggle("is-success", success);
    el.classList.toggle("is-error", !success);
  }
})();
