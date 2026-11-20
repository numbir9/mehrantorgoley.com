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
