(function () {
  // Mobile menu
  var btn = document.querySelector('.menu-btn');
  var nav = document.querySelector('.nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Scroll reveal
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  // The clock. Pacific time, but it only ever lands on a minute whose digits sum to a multiple of nine.
  var clocks = document.querySelectorAll('[data-clock]');
  function nineTime() {
    var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'America/Los_Angeles', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
    var h = Number(parts.find(function (p) { return p.type === 'hour'; }).value) % 24;
    var m = Number(parts.find(function (p) { return p.type === 'minute'; }).value);
    for (var i = 0; i < 1440; i++) {
      var s = String(h).padStart(2, '0') + String(m).padStart(2, '0');
      var sum = 0; for (var k = 0; k < 4; k++) sum += Number(s[k]);
      if (sum % 9 === 0) return [s.slice(0, 2), s.slice(2)];
      m -= 1; if (m < 0) { m = 59; h = (h + 23) % 24; }
    }
    return ['00', '00'];
  }
  function tick() {
    var t = nineTime();
    clocks.forEach(function (c) {
      c.innerHTML = 'CALIFORNIA&#160;&#160;' + t[0] + '<span class="blink">:</span>' + t[1];
    });
  }
  if (clocks.length) { tick(); setInterval(tick, 5000); }

  // Email links: many browsers have no mail app set up, so a mailto: click can do nothing.
  // Copy the address too, and say so.
  var toast;
  function showToast(msg) {
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast mono';
      toast.setAttribute('role', 'status');
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('on');
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { toast.classList.remove('on'); }, 3200);
  }
  document.querySelectorAll('a[href^="mailto:"]:not([data-nocopy])').forEach(function (a) {
    a.addEventListener('click', function () {
      var addr = a.getAttribute('href').replace('mailto:', '').split('?')[0];
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(addr).then(function () {
          showToast('Copied — ' + addr);
        }, function () { showToast(addr); });
      } else {
        showToast(addr);
      }
    });
  });

  // Contact form: send via FormSubmit without leaving the page.
  var form = document.getElementById('cform');
  if (form) {
    var status = form.querySelector('.form-status');
    var done = function () {
      form.innerHTML = '<div class="sent wide"><p class="display">Sent.</p><p>Thanks — I’ll get back to you soon.</p></div>';
    };
    if (/[?&]sent=1/.test(location.search)) done();
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form._honey && form._honey.value) return;
      var bad = [].filter.call(form.querySelectorAll('[required]'), function (f) { return !f.value.trim() || (f.type === 'email' && !/^\S+@\S+\.\S+$/.test(f.value)); });
      form.querySelectorAll('.field').forEach(function (f) { f.classList.remove('err'); });
      if (bad.length) {
        bad.forEach(function (f) { f.closest('.field').classList.add('err'); });
        status.textContent = 'Please fill in your name, a valid email and a message.';
        bad[0].focus();
        return;
      }
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true; status.textContent = 'Sending…';
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data._replyto = data.email;
      fetch('https://formsubmit.co/ajax/hello@mehrantorgoley.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) { return r.json().then(function (j) { if (!r.ok || String(j.success) !== 'true') throw j; }); })
        .then(done)
        .catch(function () {
          btn.disabled = false;
          status.innerHTML = 'That didn’t go through. Please use <a class="mail" href="mailto:hello@mehrantorgoley.com">email</a> instead.';
        });
    });
  }

  // "Email me directly" chooser: webmail, device mail app, or copy.
  var pk = document.querySelector('.picker');
  if (pk) {
    var pb = pk.querySelector('.picker-btn'), pm = pk.querySelector('.picker-menu');
    var setOpen = function (o) { pm.hidden = !o; pb.setAttribute('aria-expanded', o); pk.classList.toggle('open', o); };
    pb.addEventListener('click', function (e) { e.stopPropagation(); setOpen(pm.hidden); });
    document.addEventListener('click', function (e) { if (!pk.contains(e.target)) setOpen(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    pk.querySelector('.copy-addr').addEventListener('click', function () {
      var addr = 'hello@mehrantorgoley.com';
      var ok = function () { showToast('Copied — ' + addr); setOpen(false); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(addr).then(ok, function () { showToast(addr); });
      else showToast(addr);
    });
    pm.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
  }

  // Homepage carousel: crossfade, autoplay (paused on hover/focus/hidden tab), arrows, keys, swipe.
  var car = document.querySelector('.carousel');
  if (car) {
    var slides = [].slice.call(car.querySelectorAll('.slide'));
    var capT = car.querySelector('.cap-t'), count = car.querySelector('.ccount');
    var cur = 0, timer = null, paused = false, n = slides.length;
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var pad = function (x) { return (x < 10 ? '0' : '') + x; };
    var go = function (i) {
      slides[cur].classList.remove('on'); slides[cur].setAttribute('tabindex', '-1');
      cur = (i + n) % n;
      var s = slides[cur], img = s.querySelector('img');
      if (img && img.loading === 'lazy') img.loading = 'eager';
      s.classList.add('on'); s.removeAttribute('tabindex');
      capT.textContent = s.getAttribute('data-cap');
      count.textContent = pad(cur + 1) + ' / ' + pad(n);
      var nx = slides[(cur + 1) % n].querySelector('img'); if (nx) nx.loading = 'eager';
    };
    var tick = function () { if (!paused && !document.hidden) go(cur + 1); };
    var start = function () { if (!still && n > 1) { clearInterval(timer); timer = setInterval(tick, 5500); } };
    car.querySelector('.cnext').addEventListener('click', function (e) { e.preventDefault(); go(cur + 1); start(); });
    car.querySelector('.cprev').addEventListener('click', function (e) { e.preventDefault(); go(cur - 1); start(); });
    car.addEventListener('mouseenter', function () { paused = true; });
    car.addEventListener('mouseleave', function () { paused = false; });
    car.addEventListener('focusin', function () { paused = true; });
    car.addEventListener('focusout', function () { paused = false; });
    car.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { go(cur + 1); start(); slides[cur].focus(); }
      if (e.key === 'ArrowLeft') { go(cur - 1); start(); slides[cur].focus(); }
    });
    var x0 = null, moved = false;
    car.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; moved = false; }, { passive: true });
    car.addEventListener('touchmove', function (e) { if (x0 !== null && Math.abs(e.touches[0].clientX - x0) > 10) moved = true; }, { passive: true });
    car.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) { go(cur + (dx < 0 ? 1 : -1)); start(); }
    });
    slides.forEach(function (s) { s.addEventListener('click', function (e) { if (moved) { e.preventDefault(); moved = false; } }); });
    start();
  }

  // Click-to-play embeds: nothing loads from YouTube or Vimeo until someone presses play.
  function mount(player, html) {
    player.innerHTML = html;
    player.classList.add('live');
  }
  document.querySelectorAll('.player[data-yt], .player[data-vimeo]').forEach(function (p) {
    p.addEventListener('click', function () {
      if (p.classList.contains('live')) return;
      var title = p.getAttribute('data-title') || 'Video';
      var yt = p.getAttribute('data-yt');
      if (yt) {
        mount(p, '<iframe src="https://www.youtube-nocookie.com/embed/' + yt + '?autoplay=1&rel=0&modestbranding=1" title="' + title + '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>');
        return;
      }
      var vurl = p.getAttribute('data-vimeo');
      fetch('https://vimeo.com/api/oembed.json?autoplay=1&url=' + encodeURIComponent(vurl))
        .then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .then(function (d) {
          mount(p, '<iframe src="https://player.vimeo.com/video/' + d.video_id + '?autoplay=1&title=0&byline=0&portrait=0" title="' + title + '" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>');
        })
        .catch(function () { window.open(vurl, '_blank', 'noopener'); });
    });
  });
})();
