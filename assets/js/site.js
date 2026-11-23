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

  // Shorts page: rotating featured short. #slug in the URL features that short (and stops rotation).
  var stage = document.querySelector('.shorts-stage');
  if (stage) {
    var sl = [].slice.call(stage.querySelectorAll('.sslide'));
    var th = [].slice.call(stage.querySelectorAll('.sthumb'));
    var DUR = 8000, idx = 0, tmr = null, hold = false, stopped = false;
    stage.style.setProperty('--sdur', DUR + 'ms');
    var still2 = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    sl.forEach(function (s) { var p = s.querySelector('.player'); if (p) p._orig = p.innerHTML; });
    var reset = function (s) {
      var p = s.querySelector('.player');
      if (p && p.classList.contains('live')) { p.innerHTML = p._orig; p.classList.remove('live'); }
    };
    var show = function (i) {
      i = (i + sl.length) % sl.length;
      if (i !== idx) reset(sl[idx]);
      sl.forEach(function (s, k) {
        var on = k === i; s.classList.toggle('on', on);
        if (on) s.removeAttribute('aria-hidden'); else s.setAttribute('aria-hidden', 'true');
        var b = s.querySelector('.player > button'); if (b) { if (on) b.removeAttribute('tabindex'); else b.setAttribute('tabindex', '-1'); }
        s.querySelectorAll('img[loading="lazy"]').forEach(function (im) { if (on) im.loading = 'eager'; });
      });
      th.forEach(function (t, k) {
        var on = k === i; t.classList.toggle('on', on);
        if (on) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current');
        if (on) { var bar = t.querySelector('.tbar i'); bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = ''; }
      });
      idx = i;
    };
    var stop = function () { stopped = true; clearInterval(tmr); stage.classList.remove('running'); };
    var start = function () {
      if (still2 || stopped) return;
      stage.classList.add('running');
      clearInterval(tmr);
      tmr = setInterval(function () { if (!hold && !document.hidden) show(idx + 1); }, DUR);
    };
    stage.addEventListener('mouseenter', function () { hold = true; stage.classList.add('hold'); });
    stage.addEventListener('mouseleave', function () { hold = false; stage.classList.remove('hold'); });
    th.forEach(function (t, k) { t.addEventListener('click', function () { stop(); show(k); }); });
    sl.forEach(function (s) { var p = s.querySelector('.player'); if (p) p.addEventListener('click', stop, true); });
    var pick = function () {
      var slug = (location.hash || '').slice(1);
      var k = sl.findIndex ? sl.findIndex(function (s) { return s.getAttribute('data-slug') === slug; }) : -1;
      if (k > -1) {
        stop(); show(k);
        var top = stage.getBoundingClientRect().top + window.pageYOffset - 100;
        window.scrollTo(0, Math.max(0, top));
        return true;
      }
      return false;
    };
    window.addEventListener('hashchange', pick);
    if (!pick()) start();
  }

  // Homepage featured-short band: shows the next short on every page load.
  var fs = document.querySelector('.featured-short[data-fs]'), fsd = document.getElementById('fs-data');
  if (fs && fsd) {
    try {
      var list = JSON.parse(fsd.textContent), n = 0;
      try { n = (parseInt(localStorage.getItem('mct_fs'), 10) + 1) || 0; } catch (e) { n = Math.floor(Math.random() * list.length); }
      n = n % list.length;
      try { localStorage.setItem('mct_fs', n); } catch (e) {}
      var d = list[n];
      if (n !== 0) {
        fs.setAttribute('href', '/shorts/#' + d.slug);
        var honors = d.honors.length ? '<ul class="laurels mono">' + d.honors.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>' : '';
        fs.querySelector('.frame').innerHTML = '<img src="' + d.img + '" alt="' + d.alt + '" loading="lazy" style="object-position:' + d.pos + '">' + d.laurel + '<span class="ptag">Short Film</span>';
        var t = fs.querySelector('.txt');
        t.innerHTML = '<span class="mono" style="font-size:13px;color:var(--dim)">Featured short — ' + d.year + '</span>' +
          '<span class="ttl display">' + d.title + '</span><p>' + d.log + '</p>' + honors +
          '<span class="mono" style="font-size:13px;color:var(--accent)">Watch the film →</span>';
      }
    } catch (e) {}
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
