(function () {
  "use strict";

  const MOBILE_MQ = window.matchMedia("(max-width: 992px)");

  /* =========================================================
     DRAG HELPER
  ========================================================= */
  function makeDraggable(container, onDragEnd) {
    let startX = 0;
    let isDragging = false;

    function getX(e) {
      return e.touches ? e.touches[0].clientX : e.clientX;
    }

    function onDown(e) {
      startX = getX(e);
      isDragging = true;
      container.classList.add("is-dragging");
      container.style.cursor = "grabbing";
    }

    function onMove() {
      /* scroll-snap containers use native touch scroll */
    }

    function onUp(e) {
      if (!isDragging) return;
      isDragging = false;
      container.classList.remove("is-dragging");
      container.style.cursor = "";
      const diff = getX(e) - startX;
      if (Math.abs(diff) > 50) {
        onDragEnd(diff < 0 ? "next" : "prev");
      }
    }

    container.addEventListener("mousedown", onDown);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    container.addEventListener("touchstart", onDown, { passive: true });
    container.addEventListener("touchmove", onMove, { passive: true });
    container.addEventListener("touchend", onUp);
    container.addEventListener("dragstart", (e) => e.preventDefault());
  }

  /* =========================================================
     TOUCH / DRAG SLIDER (live follow + snap)
  ========================================================= */
  function bindSliderSwipe(wrapper, track, moveTo, getOffset, stepSize, maxOffset) {
    let startX = 0;
    let startOffset = 0;
    let dragging = false;

    function pointerX(e) {
      if (e.touches && e.touches.length) {
        return e.touches[0].clientX;
      }
      if (e.changedTouches && e.changedTouches.length) {
        return e.changedTouches[0].clientX;
      }
      return e.clientX;
    }

    function onStart(e) {
      if (e.type === "mousedown" && e.button !== 0) return;
      dragging = true;
      startX = pointerX(e);
      startOffset = getOffset();
      track.classList.add("is-dragging");
      wrapper.classList.add("is-dragging");
    }

    function onMove(e) {
      if (!dragging) return;
      const x = pointerX(e);
      const dx = startX - x;
      if (e.cancelable && Math.abs(dx) > 4) {
        e.preventDefault();
      }
      moveTo(Math.max(0, Math.min(startOffset + dx, maxOffset())), true);
    }

    function onEnd(e) {
      if (!dragging) return;
      dragging = false;
      track.classList.remove("is-dragging");
      wrapper.classList.remove("is-dragging");

      const x = pointerX(e);
      const dx = startX - x;
      const step = stepSize();
      let target = getOffset();

      if (Math.abs(dx) > 40) {
        target = startOffset + (dx > 0 ? step : -step);
      } else {
        target = Math.round(getOffset() / step) * step;
      }

      moveTo(Math.max(0, Math.min(target, maxOffset())), false);
    }

    wrapper.addEventListener("mousedown", onStart);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onEnd);
    wrapper.addEventListener("touchstart", onStart, { passive: true });
    wrapper.addEventListener("touchmove", onMove, { passive: false });
    wrapper.addEventListener("touchend", onEnd);
    wrapper.addEventListener("touchcancel", onEnd);
  }

  /* =========================================================
     BRAND STRIP
  ========================================================= */
  function initBrandStrip() {
    const strip = document.querySelector(".brand-strip");
    if (!strip) return;

    const track = strip.querySelector(".brand-track");
    const wrapper = strip.querySelector(".brand-track-wrapper");
    const prevBtn = strip.querySelector(".brand-arrow--prev");
    const nextBtn = strip.querySelector(".brand-arrow--next");

    let offset = 0;

    function brandsPerView() {
      const styles = getComputedStyle(strip);
      const raw = styles.getPropertyValue("--brands-per-view").trim();
      const count = parseInt(raw, 10);
      return Number.isFinite(count) && count > 0 ? count : 9;
    }

    function stepSize() {
      return wrapper.clientWidth / brandsPerView();
    }

    function moveTo(val) {
      const maxScroll = track.scrollWidth - wrapper.clientWidth;
      offset = Math.max(0, Math.min(val, maxScroll));
      track.style.transform = `translateX(-${offset}px)`;
    }

    function scrollBrands(dir) {
      wrapper.scrollBy({
        left: dir === "next" ? wrapper.clientWidth * 0.8 : -wrapper.clientWidth * 0.8,
        behavior: "smooth",
      });
    }

    function onModeChange() {
      if (MOBILE_MQ.matches) {
        track.style.transform = "none";
        offset = 0;
      } else {
        moveTo(offset);
      }
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        if (MOBILE_MQ.matches) scrollBrands("next");
        else moveTo(offset + stepSize());
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (MOBILE_MQ.matches) scrollBrands("prev");
        else moveTo(offset - stepSize());
      });
    }

    makeDraggable(wrapper, (dir) => {
      if (MOBILE_MQ.matches) scrollBrands(dir);
      else moveTo(dir === "next" ? offset + stepSize() : offset - stepSize());
    });

    wrapper.style.cursor = "grab";
    MOBILE_MQ.addEventListener("change", onModeChange);
    window.addEventListener("resize", () => {
      if (!MOBILE_MQ.matches) moveTo(offset);
    });
    onModeChange();
  }

  /* =========================================================
     HERO — desktop: fade carousel | mobile: swipe scroll
  ========================================================= */
  function initHeroSlider(slider) {
    const track = slider.querySelector(".hero-slides-track") || slider;
    const slides = Array.from(track.querySelectorAll(".hero-slide"));
    if (slides.length <= 1) return;

    const dots = Array.from(slider.querySelectorAll(".hero-dot"));
    const prevBtn = slider.querySelector(".hero-arrow--prev");
    const nextBtn = slider.querySelector(".hero-arrow--next");

    let current = 0;
    let timer = null;
    const AUTOPLAY_MS = 5500;

    function activeScrollIndex() {
      const w = track.clientWidth || 1;
      return Math.round(track.scrollLeft / w);
    }

    function scrollToSlide(index) {
      const i = Math.max(0, Math.min(index, slides.length - 1));
      const w = track.clientWidth;
      track.scrollTo({ left: i * w, behavior: "smooth" });
    }

    function syncVideos(index) {
      slides.forEach((slide, i) => {
        const video = slide.querySelector(".hero-video");
        if (!video) return;
        if (i === index) {
          video.play().catch(() => {});
        } else {
          video.pause();
          video.currentTime = 0;
        }
      });
    }

    function updateScrollUI() {
      const idx = activeScrollIndex();
      dots.forEach((d, i) => d.classList.toggle("is-active", i === idx));
      syncVideos(idx);
    }

    function updateCarouselUI(index, direction = "next") {
      const prev = current;
      current = (index + slides.length) % slides.length;

      slides[prev].classList.remove("is-active");
      slides[prev].classList.add(direction === "next" ? "is-leaving-left" : "is-leaving-right");

      slides[current].classList.add(direction === "next" ? "is-entering-right" : "is-entering-left");
      slides[current].getBoundingClientRect();
      slides[current].classList.add("is-active");
      slides[current].classList.remove("is-entering-right", "is-entering-left");

      setTimeout(() => {
        slides[prev].classList.remove("is-leaving-left", "is-leaving-right");
      }, 600);

      dots.forEach((d, i) => d.classList.toggle("is-active", i === current));
      syncVideos(current);
    }

    function next() {
      if (MOBILE_MQ.matches) {
        const idx = activeScrollIndex();
        if (idx < slides.length - 1) scrollToSlide(idx + 1);
      } else {
        updateCarouselUI(current + 1, "next");
      }
    }

    function prev() {
      if (MOBILE_MQ.matches) {
        const idx = activeScrollIndex();
        if (idx > 0) scrollToSlide(idx - 1);
      } else {
        updateCarouselUI(current - 1, "prev");
      }
    }

    function startAutoplay() {
      stopAutoplay();
      if (MOBILE_MQ.matches) {
        timer = setInterval(() => {
          const idx = activeScrollIndex();
          scrollToSlide((idx + 1) % slides.length);
        }, AUTOPLAY_MS);
        return;
      }
      timer = setInterval(() => updateCarouselUI(current + 1, "next"), AUTOPLAY_MS);
    }

    function stopAutoplay() {
      if (timer) clearInterval(timer);
      timer = null;
    }

    let scrollTimer = null;
    track.addEventListener(
      "scroll",
      () => {
        if (!MOBILE_MQ.matches) return;
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(updateScrollUI, 60);
      },
      { passive: true }
    );

    if (nextBtn) nextBtn.addEventListener("click", () => { next(); startAutoplay(); });
    if (prevBtn) prevBtn.addEventListener("click", () => { prev(); startAutoplay(); });

    dots.forEach((dot, i) => {
      dot.addEventListener("click", () => {
        if (MOBILE_MQ.matches) scrollToSlide(i);
        else {
          updateCarouselUI(i);
          startAutoplay();
        }
      });
    });

    slider.addEventListener("mouseenter", stopAutoplay);
    slider.addEventListener("mouseleave", startAutoplay);

    makeDraggable(track, (dir) => {
      if (dir === "next") next();
      else prev();
      startAutoplay();
    });

    track.addEventListener("touchstart", stopAutoplay, { passive: true });
    track.addEventListener("touchend", () => {
      if (MOBILE_MQ.matches) startAutoplay();
    });

    function onModeChange() {
      stopAutoplay();
      if (MOBILE_MQ.matches) {
        slides.forEach((s) => {
          s.classList.add("is-active");
          s.classList.remove("is-leaving-left", "is-leaving-right", "is-entering-left", "is-entering-right");
        });
        updateScrollUI();
        startAutoplay();
      } else {
        track.scrollLeft = 0;
        slides.forEach((s, i) => s.classList.toggle("is-active", i === current));
        updateCarouselUI(current);
        startAutoplay();
      }
    }

    MOBILE_MQ.addEventListener("change", onModeChange);

    if (MOBILE_MQ.matches) {
      updateScrollUI();
      startAutoplay();
    } else {
      updateCarouselUI(0);
      startAutoplay();
    }
  }

  document.querySelectorAll(".hero-slider").forEach(initHeroSlider);
  initBrandStrip();

  /* =========================================================
     PRODUCT SLIDERS
  ========================================================= */
  function initProductSliders() {
    document.querySelectorAll(".products-slider").forEach((slider) => {
      const track = slider.querySelector(".products-track");
      const wrapper = slider.querySelector(".products-track-wrapper");
      const prevBtn = slider.querySelector(".products-arrow--prev");
      const nextBtn = slider.querySelector(".products-arrow--next");
      if (!track || !wrapper) return;

      let offset = 0;

      function productsPerView() {
        const raw = getComputedStyle(slider).getPropertyValue("--products-per-view").trim();
        const n = parseInt(raw, 10);
        return Number.isFinite(n) && n > 0 ? n : 4;
      }

      function gapSize() {
        const raw = getComputedStyle(slider).getPropertyValue("--products-gap").trim();
        const g = parseFloat(raw);
        return Number.isFinite(g) ? g : 16;
      }

      function syncCardWidths() {
        const pv = productsPerView();
        const gap = gapSize();
        const w = Math.max(140, (wrapper.clientWidth - gap * (pv - 1)) / pv);
        track.querySelectorAll(".product-card-wrap").forEach((el) => {
          el.style.flexBasis = `${w}px`;
          el.style.maxWidth = `${w}px`;
        });
      }

      function stepSize() {
        const card = track.querySelector(".product-card-wrap");
        if (!card) return wrapper.clientWidth;
        return card.offsetWidth + gapSize();
      }

      function maxOffset() {
        return Math.max(0, track.scrollWidth - wrapper.clientWidth);
      }

      function updateArrows() {
        const max = maxOffset();
        if (prevBtn) prevBtn.disabled = offset <= 1;
        if (nextBtn) nextBtn.disabled = offset >= max - 1;
      }

      function moveTo(val, instant) {
        offset = Math.max(0, Math.min(val, maxOffset()));
        track.style.transform = `translateX(-${offset}px)`;
        if (instant) {
          track.classList.add("is-dragging");
        } else {
          track.classList.remove("is-dragging");
        }
        updateArrows();
      }

      if (nextBtn) {
        nextBtn.addEventListener("click", () => moveTo(offset + stepSize(), false));
      }

      if (prevBtn) {
        prevBtn.addEventListener("click", () => moveTo(offset - stepSize(), false));
      }

      bindSliderSwipe(
        wrapper,
        track,
        moveTo,
        () => offset,
        stepSize,
        maxOffset
      );

      function onResize() {
        syncCardWidths();
        moveTo(Math.min(offset, maxOffset()));
      }

      window.addEventListener("resize", onResize);
      syncCardWidths();

      moveTo(0);
    });
  }

  initProductSliders();

  /* =========================================================
     ABOUT SECTION — count-up stats
  ========================================================= */
  function initAboutCounters() {
    const section = document.getElementById("about-section");
    if (!section) return;

    const counters = Array.from(section.querySelectorAll("[data-count]"));
    if (!counters.length) return;

    function formatNumber(n) {
      return n.toLocaleString();
    }

    function animateCounter(el) {
      const target = parseInt(el.getAttribute("data-count"), 10) || 0;
      const duration = 2200;
      const startTime = performance.now();

      function tick(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = formatNumber(Math.floor(target * eased));
        if (progress < 1) {
          requestAnimationFrame(tick);
        } else {
          el.textContent = formatNumber(target);
        }
      }

      requestAnimationFrame(tick);
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          counters.forEach((el) => {
            if (el.dataset.counted === "true") return;
            el.dataset.counted = "true";
            animateCounter(el);
          });
          observer.disconnect();
        });
      },
      { threshold: 0.25, rootMargin: "0px 0px -40px 0px" }
    );

    observer.observe(section);
  }

  initAboutCounters();

  /* =========================================================
     PRODUCT ACTIONS
  ========================================================= */
  const cartButtons = document.querySelectorAll(".btn-cart");

  cartButtons.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const productCard = this.closest(".product-card");
      const title = productCard?.querySelector(".title")?.innerText;
      alert(title + " added to cart!");
    });
  });

})();
