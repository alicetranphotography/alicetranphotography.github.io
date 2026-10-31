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

  // Inquiry form: three short steps, then sends through Web3Forms
  var form = document.getElementById('inquiry');
  if (form) {
    var steps = form.querySelectorAll('.step');
    var bars = form.querySelectorAll('.progress span');
    var status = form.querySelector('.form-status');
    var current = 0;

    var valid = function (step) {
      var ok = true, first = null;
      step.querySelectorAll('[required]').forEach(function (el) {
        var good = el.type === 'radio' ? !!form.querySelector('[name="' + el.name + '"]:checked') : el.checkValidity();
        var box = el.type === 'radio' ? el.closest('.choices') : el;
        box.classList.toggle('is-invalid', !good);
        if (!good) { ok = false; first = first || el; }
      });
      if (!ok) {
        status.className = 'form-status error';
        status.textContent = 'Please fill in the highlighted fields.';
        if (first.type === 'radio') first.closest('.choices').scrollIntoView({ block: 'center' }); else first.focus();
      }
      return ok;
    };

    var show = function (n) {
      current = n;
      steps.forEach(function (s, i) { s.classList.toggle('is-active', i === n); });
      bars.forEach(function (b, i) { b.className = i < n ? 'done' : i === n ? 'now' : ''; });
      form.querySelector('.step-count').textContent = '0' + (n + 1) + ' of 0' + steps.length;
      form.querySelector('.step-title').textContent = steps[n].dataset.title;
      form.querySelector('.step-sub').textContent = steps[n].dataset.sub;
      status.textContent = '';
      form.querySelector('.inquiry-head').scrollIntoView({ block: 'start', behavior: 'smooth' });
    };

    form.querySelectorAll('[data-next]').forEach(function (b) {
      b.addEventListener('click', function () { if (valid(steps[current])) show(current + 1); });
    });
    form.querySelectorAll('[data-back]').forEach(function (b) {
      b.addEventListener('click', function () { show(current - 1); });
    });
    form.querySelectorAll('.choices input').forEach(function (r) {
      r.addEventListener('change', function () { r.closest('.choices').classList.remove('is-invalid'); });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!valid(steps[current])) return;
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      status.className = 'form-status';
      status.textContent = 'Sending...';
      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form)))
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (!d.success) throw new Error(d.message || 'failed');
        form.style.display = 'none';
        var done = document.getElementById('received');
        done.classList.add('is-active');
        done.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }).catch(function () {
        status.className = 'form-status error';
        status.textContent = 'Sorry, something went wrong. Please email alicetranphotography@gmail.com instead.';
        btn.disabled = false;
      });
    });
  }
})();
