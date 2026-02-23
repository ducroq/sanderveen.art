(function () {
  // Mobile menu toggle
  var toggle = document.getElementById('menu-toggle');
  var nav = document.getElementById('main-nav');

  if (toggle && nav) {
    // Set initial state
    nav.setAttribute('aria-hidden', 'true');

    toggle.addEventListener('click', function () {
      var expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      nav.classList.toggle('is-open');
      nav.setAttribute('aria-hidden', String(expanded));
      document.body.style.overflow = expanded ? '' : 'hidden';
    });
  }

  // Header scroll state
  var header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', function () {
      header.classList.toggle('is-scrolled', window.scrollY > 10);
    }, { passive: true });
  }

  // Lightbox
  var lightbox = document.getElementById('lightbox');
  var trigger = document.getElementById('painting-image');

  if (lightbox && trigger) {
    var lightboxImg = lightbox.querySelector('.lightbox-img');
    var closeBtn = lightbox.querySelector('.lightbox-close');
    var previousFocus = null;

    function openLightbox() {
      previousFocus = document.activeElement;
      // Show thumbnail immediately, then load full-res
      var thumbSrc = trigger.getAttribute('data-thumb') || trigger.querySelector('img').src;
      var fullSrc = trigger.getAttribute('data-full');
      var altText = trigger.querySelector('img') ? trigger.querySelector('img').alt : '';

      lightboxImg.src = thumbSrc;
      lightboxImg.alt = altText;
      lightbox.hidden = false;
      document.body.style.overflow = 'hidden';
      closeBtn.focus();

      // Load full-res in background
      if (fullSrc && fullSrc !== thumbSrc) {
        var preload = new Image();
        preload.onload = function () {
          lightboxImg.src = fullSrc;
        };
        preload.src = fullSrc;
      }
    }

    function closeLightbox() {
      lightbox.hidden = true;
      lightboxImg.src = '';
      document.body.style.overflow = '';
      if (previousFocus) previousFocus.focus();
    }

    trigger.addEventListener('click', openLightbox);

    closeBtn.addEventListener('click', closeLightbox);

    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) closeLightbox();
    });

    // Keyboard: Escape closes, Tab traps focus inside lightbox
    document.addEventListener('keydown', function (e) {
      if (lightbox.hidden) return;

      if (e.key === 'Escape') {
        closeLightbox();
      } else if (e.key === 'Tab') {
        // Trap focus inside lightbox (only focusable element is close button)
        e.preventDefault();
        closeBtn.focus();
      }
    });
  }

  // Pre-fill inquiry form from URL params
  var params = new URLSearchParams(window.location.search);
  var paintingParam = params.get('painting');
  if (paintingParam) {
    var paintingField = document.getElementById('painting-field');
    if (paintingField) {
      paintingField.value = paintingParam;
    }

    var messageField = document.getElementById('message');
    if (messageField && !messageField.value) {
      var lang = document.documentElement.lang;
      if (lang === 'nl') {
        messageField.value = 'Graag ontvang ik meer informatie over het schilderij "' + paintingParam + '".';
      } else {
        messageField.value = 'I would like more information about the painting "' + paintingParam + '".';
      }
    }
  }
})();
