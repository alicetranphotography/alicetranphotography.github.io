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

  // Inquiry form: one page, checked before it is sent through Web3Forms
  var form = document.getElementById('inquiry');
  if (form) {
    var status = form.querySelector('.form-status');
    var phoneOk = function (v) { var d = v.replace(/\D/g, ''); return d.length >= 10 && d.length <= 15; };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var first = null;
      form.querySelectorAll('[required]').forEach(function (el) {
        var good = el.type === 'radio' ? !!form.querySelector('[name="' + el.name + '"]:checked')
                 : el.id === 'f-phone' ? el.value.trim() !== '' && phoneOk(el.value)
                 : el.checkValidity();
        var box = el.type === 'radio' ? el.closest('.choices') : el;
        box.classList.toggle('is-invalid', !good);
        if (!good && !first) first = el;
      });
      if (first) {
        status.className = 'form-status error';
        status.textContent = first.id === 'f-phone' && first.value.trim() !== ''
          ? 'Please enter a valid phone number with area code, like (703) 555-0100.'
          : 'Please fill in the highlighted fields.';
        if (first.type === 'radio') first.closest('.choices').scrollIntoView({ block: 'center' }); else first.focus();
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
    form.querySelectorAll('.choices input').forEach(function (r) {
      r.addEventListener('change', function () { r.closest('.choices').classList.remove('is-invalid'); });
    });
    var phone = document.getElementById('f-phone');
    phone.addEventListener('input', function () { phone.classList.toggle('is-invalid', phone.value.trim() !== '' && !phoneOk(phone.value)); });
  }
})();

// FAQ accordion: smooth open/close, one open at a time
(function () {
  var items = document.querySelectorAll('details.faq-item');
  if (!items.length) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function finish(body, after) {
    var done = false;
    function end() { if (done) return; done = true; body.style.height = body.style.overflow = body.style.transition = ''; body.removeEventListener('transitionend', end); if (after) after(); }
    body.addEventListener('transitionend', end);
    setTimeout(end, 450);
  }
  function open(d, body) {
    d.open = true;
    if (reduce) return;
    var h = body.scrollHeight;
    body.style.height = '0px'; body.style.overflow = 'hidden';
    void body.offsetHeight;
    body.style.transition = 'height .4s cubic-bezier(.2,.7,.2,1)'; body.style.height = h + 'px';
    finish(body);
  }
  function close(d, body) {
    if (reduce) { d.open = false; return; }
    body.style.height = body.scrollHeight + 'px'; body.style.overflow = 'hidden';
    void body.offsetHeight;
    body.style.transition = 'height .3s ease'; body.style.height = '0px';
    finish(body, function () { d.open = false; });
  }
  items.forEach(function (d) {
    var summary = d.querySelector('summary'), body = d.querySelector('.faq-body');
    if (!summary || !body) return;
    summary.addEventListener('click', function (e) {
      e.preventDefault();
      if (d.open) { close(d, body); return; }
      items.forEach(function (o) { if (o !== d && o.open) close(o, o.querySelector('.faq-body')); });
      open(d, body);
    });
  });
  function openHash() {
    if (!location.hash) return;
    var t = document.querySelector(location.hash);
    if (t && t.matches('details.faq-item')) { items.forEach(function (o) { o.open = o === t; }); }
  }
  openHash();
  window.addEventListener('hashchange', openHash);
})();
