(function () {
  "use strict";

  /* =========================================================
     DRAG HELPER
  ========================================================= */
  function makeDraggable(container, onDragEnd) {
    let startX = 0;
    let isDragging = false;
    let hasMoved = false;

    function getX(e) {
      return e.touches ? e.touches[0].clientX : e.clientX;
    }

    function onDown(e) {
      startX = getX(e);
      isDragging = true;
      hasMoved = false;
      container.style.cursor = "grabbing";
    }

    function onMove(e) {
      if (!isDragging) return;
      if (Math.abs(getX(e) - startX) > 5) hasMoved = true;
    }

    function onUp(e) {
      if (!isDragging) return;
      isDragging = false;
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
    container.addEventListener("dragstart", e => e.preventDefault());

    return { getHasMoved: () => hasMoved };
  }

  /* =========================================================
     BRAND STRIP
  ========================================================= */
  const strip = document.querySelector(".brand-strip");

  if (strip) {
    const track = strip.querySelector(".brand-track");
    const wrapper = strip.querySelector(".brand-track-wrapper");
    const prevBtn = strip.querySelector(".brand-arrow--prev");
    const nextBtn = strip.querySelector(".brand-arrow--next");

    const STEP = wrapper.clientWidth / 5;
    let offset = 0;

    function moveTo(val) {
      const maxScroll = track.scrollWidth - wrapper.clientWidth;
      offset = Math.max(0, Math.min(val, maxScroll));
      track.style.transform = `translateX(-${offset}px)`;
    }

    if (nextBtn) nextBtn.addEventListener("click", () => moveTo(offset + STEP));
    if (prevBtn) prevBtn.addEventListener("click", () => moveTo(offset - STEP));

    makeDraggable(wrapper, (dir) => {
      moveTo(dir === "next" ? offset + STEP : offset - STEP);
    });

    wrapper.style.cursor = "grab";
  }

  /* =========================================================
     HERO CAROUSEL
  ========================================================= */
  const slider = document.querySelector(".hero-slider");

  if (slider) {
    const slides = Array.from(slider.querySelectorAll(".hero-slide"));
    const dots = Array.from(slider.querySelectorAll(".hero-dot"));
    const prevBtn = slider.querySelector(".hero-arrow--prev");
    const nextBtn = slider.querySelector(".hero-arrow--next");
    const progressBar = slider.querySelector(".hero-progress");
    const counter = slider.querySelector(".hero-counter");

    let current = 0;
    let timer = null;
    const AUTOPLAY_MS = 5000;

    function updateUI(index, direction = "next") {
      const prev = current;
      current = (index + slides.length) % slides.length;

      slides[prev].classList.remove("is-active");
      slides[prev].classList.add(direction === "next" ? "is-leaving-left" : "is-leaving-right");

      slides[current].classList.add(direction === "next" ? "is-entering-right" : "is-entering-left");
      slides[current].getBoundingClientRect(); // force reflow
      slides[current].classList.add("is-active");
      slides[current].classList.remove("is-entering-right", "is-entering-left");

      setTimeout(() => {
        slides[prev].classList.remove("is-leaving-left", "is-leaving-right");
      }, 600);

      dots.forEach((d, i) => d.classList.toggle("is-active", i === current));

      if (counter) counter.textContent = `${current + 1} / ${slides.length}`;

      if (progressBar) {
        progressBar.style.transition = "none";
        progressBar.style.width = "0%";
        progressBar.getBoundingClientRect();
        progressBar.style.transition = `width ${AUTOPLAY_MS}ms linear`;
        progressBar.style.width = "100%";
      }
    }

    function next() { updateUI(current + 1, "next"); }
    function prev() { updateUI(current - 1, "prev"); }

    function start() {
      stop();
      timer = setInterval(next, AUTOPLAY_MS);
      if (progressBar) {
        progressBar.style.transition = `width ${AUTOPLAY_MS}ms linear`;
        progressBar.style.width = "100%";
      }
    }

    function stop() {
      if (timer) clearInterval(timer);
      timer = null;
      if (progressBar) {
        progressBar.style.transition = "none";
        progressBar.style.width = "0%";
      }
    }

    if (nextBtn) nextBtn.addEventListener("click", () => { next(); start(); });
    if (prevBtn) prevBtn.addEventListener("click", () => { prev(); start(); });

    dots.forEach((dot, i) => {
      dot.addEventListener("click", () => { updateUI(i); start(); });
    });

    slider.addEventListener("mouseenter", stop);
    slider.addEventListener("mouseleave", start);

    makeDraggable(slider, (dir) => {
      if (dir === "next") { next(); start(); }
      else { prev(); start(); }
    });

    updateUI(0);
    start();
  }

  /* =========================================================
     PRODUCT ACTIONS
  ========================================================= */
  const cartButtons = document.querySelectorAll(".btn-cart");

  cartButtons.forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const productCard = this.closest(".product-card");
      const title = productCard?.querySelector(".title")?.innerText;
      alert(title + " added to cart!");
    });
  });

})();