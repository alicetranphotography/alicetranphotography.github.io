// Mobile menu, dropdowns, homepage slideshow, click-to-play YouTube.
(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open);
    });
  }
  document.querySelectorAll('.sub-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.parentElement.classList.toggle('sub-open');
      btn.setAttribute('aria-expanded', open);
    });
  });

  // Mark the current page in the menu
  var path = location.pathname.replace(/\/index\.html$/, '').replace(/\/$/, '') || '/';
  document.querySelectorAll('.site-nav a').forEach(function (a) {
    if (a.getAttribute('href') === path) a.setAttribute('aria-current', 'page');
  });

  // Slideshows (a page may have more than one)
  document.querySelectorAll('.slideshow').forEach(function (show) {
    var slides = show.querySelectorAll('.slide');
    var i = 0, timer;
    var go = function (n) {
      slides[i].classList.remove('is-active');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('is-active');
      // warm the next photo so the fade never shows a blank frame
      var next = slides[(i + 1) % slides.length].querySelector('img');
      if (next) next.loading = 'eager';
    };
    var start = function () {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      clearInterval(timer);
      timer = setInterval(function () { go(i + 1); }, 4500);
    };
    show.querySelector('.prev').addEventListener('click', function () { go(i - 1); start(); });
    show.querySelector('.next').addEventListener('click', function () { go(i + 1); start(); });
    slides[1] && (slides[1].querySelector('img').loading = 'eager');
    start();
  });

  // YouTube: load the player only when someone presses play
  document.querySelectorAll('.yt').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + btn.dataset.id + '?autoplay=1&rel=0';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.title = btn.getAttribute('aria-label');
      var box = document.createElement('div');
      box.className = 'yt';
      box.appendChild(f);
      btn.replaceWith(box);
    }, { once: true });
  });

  // Inquiry form: sends through Web3Forms, shows the result in place
  var form = document.getElementById('inquiry');
  if (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = [].filter.call(form.querySelectorAll('[required]'), function (el) {
        el.classList.toggle('is-invalid', !el.checkValidity());
        return !el.checkValidity();
      });
      if (bad.length) {
        status.className = 'form-status error';
        status.textContent = 'Please fill in the highlighted fields.';
        bad[0].focus();
        return;
      }
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      status.className = 'form-status';
      status.textContent = 'Sending...';
      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form)))
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (d.success) {
          form.reset();
          status.textContent = 'Thank you! Your inquiry is on its way. I will be in touch within 24 to 48 hours.';
        } else { throw new Error(d.message || 'failed'); }
      }).catch(function () {
        status.className = 'form-status error';
        status.textContent = 'Sorry, something went wrong. Please email alicetranphotography@gmail.com instead.';
      }).finally(function () { btn.disabled = false; });
    });
  }
})();
