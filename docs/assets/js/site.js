/* UBS site runtime: animations, hero slider, header, menus, popup, sliders, forms.
   No dependencies. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var docLang = document.documentElement.lang || 'en';
  var T = {
    en: { sent: 'Thank you! We will contact you shortly.', error: 'Sending failed. Please try again or write to ubs@ubsystem.kz', required: 'Please fill in this field', email: 'Please enter a valid email' },
    ru: { sent: 'Спасибо! Мы скоро свяжемся с вами.', error: 'Не удалось отправить. Попробуйте ещё раз или напишите на ubs@ubsystem.kz', required: 'Заполните это поле', email: 'Укажите корректный email' },
    kk: { sent: 'Рақмет! Біз сізбен жақын арада хабарласамыз.', error: 'Жіберу мүмкін болмады. Қайталап көріңіз немесе ubs@ubsystem.kz поштасына жазыңыз', required: 'Осы өрісті толтырыңыз', email: 'Дұрыс email енгізіңіз' }
  }[docLang] || {};

  function screenRes() {
    var w = window.innerWidth;
    return w >= 1200 ? 1200 : w >= 960 ? 960 : w >= 640 ? 640 : w >= 480 ? 480 : 320;
  }

  /* ---------- Appear animations (fade in / from left / from right) ---------- */
  function initAppear() {
    var els = $$('[data-anim]');
    if (!els.length) return;
    var mobile = window.innerWidth < 1200;
    els.forEach(function (el) {
      if (reduceMotion || (mobile && !el.hasAttribute('data-anim-mobile'))) {
        el.classList.add('is-shown');
        return;
      }
      var d = parseFloat(el.getAttribute('data-anim-distance') || '100');
      var style = el.getAttribute('data-anim');
      var tr = style === 'fadeinright' ? 'translateX(' + -d + 'px)'
        : style === 'fadeinleft' ? 'translateX(' + d + 'px)'
        : style === 'fadeinup' ? 'translateY(' + d + 'px)'
        : style === 'fadeindown' ? 'translateY(' + -d + 'px)' : '';
      if (tr) el.style.transform = tr;
      el.style.transitionDuration = (el.getAttribute('data-anim-duration') || '1') + 's';
      el.style.transitionDelay = (el.getAttribute('data-anim-delay') || '0') + 's';
      el.style.transitionTimingFunction = 'cubic-bezier(0.19, 1, 0.22, 1)';
    });
    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-shown'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-shown'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { if (!el.classList.contains('is-shown')) io.observe(el); });
  }

  /* ---------- Step-by-step animations (scroll / into view / hover) ---------- */
  var EASE = {
    easeIn: 'cubic-bezier(0.42,0,1,1)', easeOut: 'cubic-bezier(0,0,0.58,1)',
    easeInOut: 'cubic-bezier(0.42,0,0.58,1)', linear: 'linear', '0': 'linear', '': 'linear'
  };

  function stepsFor(el) {
    var res = screenRes();
    var bps = [320, 480, 640, 960];
    for (var i = 0; i < bps.length; i++) {
      if (res <= bps[i] && el.hasAttribute('data-sbs-steps-' + bps[i])) {
        return JSON.parse(el.getAttribute('data-sbs-steps-' + bps[i]));
      }
    }
    return JSON.parse(el.getAttribute('data-sbs-steps') || '[]');
  }

  function num(v) { v = parseFloat(v); return isNaN(v) ? 0 : v; }

  function applyState(el, s) {
    el.style.translate = num(s.mx) + 'px ' + num(s.my) + 'px';
    el.style.scale = (s.sx == null ? 1 : s.sx) + ' ' + (s.sy == null ? 1 : s.sy);
    el.style.rotate = num(s.ro) + 'deg';
    el.style.opacity = s.op == null ? 1 : s.op;
  }

  function lerpState(a, b, t) {
    var o = {};
    ['mx', 'my', 'sx', 'sy', 'op', 'ro'].forEach(function (k) {
      var def = (k === 'sx' || k === 'sy' || k === 'op') ? 1 : 0;
      var x = a[k] == null ? def : num(a[k]);
      var y = b[k] == null ? def : num(b[k]);
      o[k] = x + (y - x) * t;
    });
    return o;
  }

  function docTop(el) {
    return el.getBoundingClientRect().top + window.pageYOffset;
  }

  function playTimeline(el, steps) {
    var t = 0;
    var frames = [];
    steps.slice(1).forEach(function (s) {
      var dur = num(s.ti);
      t += num(s.dt);
      frames.push({ at: t, dur: dur, state: s, ease: EASE[s.ea] || 'linear' });
      t += dur;
    });
    if (el._sbsTimers) el._sbsTimers.forEach(clearTimeout);
    el._sbsTimers = frames.map(function (f) {
      return setTimeout(function () {
        el.style.transition = f.dur ? ['translate', 'scale', 'rotate', 'opacity'].map(function (p) {
          return p + ' ' + f.dur + 'ms ' + f.ease;
        }).join(',') : 'none';
        applyState(el, f.state);
      }, f.at);
    });
  }

  function initSbs() {
    var els = $$('[data-sbs]');
    if (!els.length) return;
    var scrollEls = [];
    els.forEach(function (el) {
      var ev = el.getAttribute('data-sbs');
      var steps = stepsFor(el);
      el.classList.add('is-ready');
      if (!steps.length) return;
      if (steps.length < 2) { applyState(el, steps[0]); return; }
      if (reduceMotion) { applyState(el, steps[steps.length - 1]); return; }
      if (ev === 'scroll') {
        scrollEls.push({ el: el, steps: steps, fixed: !!el.closest('.z--fixed') });
      } else if (ev === 'intoview') {
        applyState(el, steps[0]);
        var io = new IntersectionObserver(function (entries) {
          if (!entries[0].isIntersecting) return;
          io.disconnect();
          playTimeline(el, steps);
        });
        io.observe(el);
      } else if (ev === 'hover') {
        applyState(el, steps[0]);
        var sec = el.closest('.z');
        var triggers = [el];
        (el.getAttribute('data-sbs-hover-els') || '').split(' ').forEach(function (c) {
          var t = c && sec && sec.querySelector('.' + c);
          if (t) triggers.push(t);
        });
        triggers.forEach(function (t) {
          t.addEventListener('mouseenter', function () { playTimeline(el, steps); });
          t.addEventListener('mouseleave', function () {
            var last = steps[steps.length - 1];
            var back = {};
            for (var k in steps[0]) back[k] = steps[0][k];
            back.ti = last.ti;
            back.ea = last.ea;
            playTimeline(el, [last, back]);
          });
        });
      }
    });
    if (!scrollEls.length) return;
    function measure() {
      scrollEls.forEach(function (o) {
        var tr = o.el.style.translate;
        o.el.style.translate = '';
        o.start = o.fixed ? 0 : docTop(o.el) - window.innerHeight;
        o.el.style.translate = tr;
      });
    }
    function tick() {
      var y = window.pageYOffset;
      scrollEls.forEach(function (o) {
        var p = y - o.start, s = o.steps, cur = s[0], acc = 0;
        for (var i = 1; i < s.length; i++) {
          var di = num(s[i].di);
          acc += num(s[i].dd);
          if (p < acc) break;
          if (di <= 0 || p >= acc + di) { cur = s[i]; acc += di; continue; }
          cur = lerpState(s[i - 1], s[i], (p - acc) / di);
          break;
        }
        applyState(o.el, cur);
      });
    }
    measure(); tick();
    var raf = 0;
    window.addEventListener('scroll', function () {
      if (!raf) raf = requestAnimationFrame(function () { raf = 0; tick(); });
    }, { passive: true });
    window.addEventListener('resize', function () { measure(); tick(); });
    window.addEventListener('load', function () { measure(); tick(); });
  }

  /* ---------- Hero slider (slides are groups of elements st-slide-N) ---------- */
  function initHeroSlider() {
    var total = 0;
    while ($('.st-slide-' + (total + 1))) total++;
    if (!total) return;
    var bar = $('.st-progress-container .a');
    var prev = $('.st-btn-prev .a'), next = $('.st-btn-next .a');
    var DURATION = 5000, current = 1, timer, fills = [];
    if (bar) {
      var wrap = document.createElement('div');
      wrap.className = 'st-pagination';
      for (var i = 1; i <= total; i++) {
        (function (n) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'st-bar';
          b.setAttribute('aria-label', 'Slide ' + n);
          var f = document.createElement('span');
          f.className = 'st-fill';
          b.appendChild(f);
          b.addEventListener('click', function (e) { e.stopPropagation(); go(n); });
          wrap.appendChild(b);
          fills.push(f);
        })(i);
      }
      bar.innerHTML = '';
      bar.appendChild(wrap);
    }
    if (prev) prev.addEventListener('click', function () { go(current - 1 < 1 ? total : current - 1); });
    if (next) next.addEventListener('click', function () { go(current + 1 > total ? 1 : current + 1); });
    // swipe left / right on phones and tablets
    var hero = $('.st-slide-1').closest('.z'), x0 = null, y0 = 0;
    hero.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    hero.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      x0 = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) {
        go(dx < 0 ? (current + 1 > total ? 1 : current + 1) : (current - 1 < 1 ? total : current - 1));
      }
    }, { passive: true });
    function go(n) {
      clearTimeout(timer);
      for (var i = 1; i <= total; i++) {
        $$('.st-slide-' + i).forEach(function (el) {
          el.classList.toggle('active-slide', i === n);
          el.setAttribute('aria-hidden', i === n ? 'false' : 'true');
          $$('a,button', el).forEach(function (a) { a.tabIndex = i === n ? 0 : -1; });
        });
        if (fills[i - 1]) {
          fills[i - 1].style.transition = 'none';
          fills[i - 1].style.width = i < n ? '100%' : '0%';
        }
      }
      if (fills[n - 1]) {
        void fills[n - 1].offsetWidth;
        fills[n - 1].style.transition = 'width ' + DURATION + 'ms linear';
        fills[n - 1].style.width = '100%';
      }
      current = n;
      timer = setTimeout(function () { go(current + 1 > total ? 1 : current + 1); }, DURATION);
    }
    go(1);
  }

  /* ---------- Language menu (globe button) ---------- */
  function initLangMenu() {
    var menu = $('#lang-menu');
    if (!menu) return;
    var btns = $$('a[href="#language"]');
    var active = null;
    function close() {
      menu.hidden = true;
      btns.forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
      active = null;
    }
    function place() {
      if (!active) return;
      var r = active.getBoundingClientRect();
      menu.style.top = (r.bottom + 8) + 'px';
      menu.style.left = Math.max(10, Math.min(window.innerWidth - menu.offsetWidth - 10,
        r.left + r.width / 2 - menu.offsetWidth / 2)) + 'px';
    }
    btns.forEach(function (btn) {
      btn.setAttribute('role', 'button');
      btn.setAttribute('aria-haspopup', 'true');
      btn.setAttribute('aria-controls', 'lang-menu');
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-label', menu.getAttribute('aria-label'));
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (!menu.hidden && active === btn) { close(); return; }
        active = btn;
        menu.hidden = false;
        btn.setAttribute('aria-expanded', 'true');
        place();
      });
    });
    document.addEventListener('click', function (e) { if (!menu.contains(e.target)) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    window.addEventListener('scroll', place, { passive: true });
    window.addEventListener('resize', close);
  }

  /* ---------- Burger menu ---------- */
  function initBurger() {
    var menu = $('#site-menu');
    if (!menu) return;
    var openers = $$('a[href="#menuopen"]');
    var closeBtn = $('.menu__close', menu);
    var last;
    function open(e) {
      if (e) e.preventDefault();
      last = document.activeElement;
      menu.hidden = false;
      requestAnimationFrame(function () { menu.classList.add('is-open'); });
      document.body.classList.add('no-scroll');
      openers.forEach(function (o) { o.setAttribute('aria-expanded', 'true'); });
      setTimeout(function () { if (closeBtn) closeBtn.focus(); }, 50);
    }
    function close() {
      menu.classList.remove('is-open');
      document.body.classList.remove('no-scroll');
      openers.forEach(function (o) { o.setAttribute('aria-expanded', 'false'); });
      setTimeout(function () { menu.hidden = true; }, 300);
      if (last) last.focus();
    }
    openers.forEach(function (o) {
      o.setAttribute('role', 'button');
      o.setAttribute('aria-controls', 'site-menu');
      o.setAttribute('aria-expanded', 'false');
      o.setAttribute('aria-label', menu.getAttribute('aria-label'));
      o.addEventListener('click', open);
    });
    if (closeBtn) closeBtn.addEventListener('click', close);
    $$('[data-menu-close]', menu).forEach(function (b) { b.addEventListener('click', close); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) close();
    });
  }

  /* ---------- Popup (consultation form) ---------- */
  function initPopup() {
    var popup = $('#popup-consultation');
    if (!popup) return;
    var last;
    function open(e) {
      if (e) e.preventDefault();
      last = document.activeElement;
      popup.hidden = false;
      requestAnimationFrame(function () { popup.classList.add('is-open'); });
      document.body.classList.add('no-scroll');
      var f = $('input:not([tabindex="-1"])', popup);
      setTimeout(function () { if (f) f.focus(); }, 300);
    }
    function close() {
      popup.classList.remove('is-open');
      document.body.classList.remove('no-scroll');
      setTimeout(function () { popup.hidden = true; }, 300);
      if (last) last.focus();
    }
    $$('a[href="#popup:myform"]').forEach(function (a) { a.addEventListener('click', open); });
    $$('[data-popup-close]', popup).forEach(function (b) { b.addEventListener('click', close); });
    popup.addEventListener('click', function (e) {
      if (e.target === popup || e.target.classList.contains('popup__wrap')) close();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !popup.hidden) close(); });
    if (location.hash === '#popup:myform') open();
  }

  /* ---------- Logo slider ---------- */
  function initBrands() {
    $$('.brands').forEach(function (root) {
      var track = $('.brands__track', root);
      var items = $$('.brands__item', root);
      var prev = $('.brands__prev', root), next = $('.brands__next', root);
      var index = 0, timer;
      function perView() { return parseInt(getComputedStyle(root).getPropertyValue('--per-view'), 10) || 6; }
      function maxIndex() { return Math.max(0, items.length - perView()); }
      function render(animate) {
        var w = items[0].getBoundingClientRect().width;
        track.style.transition = animate === false ? 'none' : '';
        track.style.transform = 'translateX(' + (-index * w) + 'px)';
      }
      function restart() {
        clearInterval(timer);
        if (!reduceMotion) timer = setInterval(function () { go(index + 1); }, 4000);
      }
      function go(n) {
        var m = maxIndex();
        index = n > m ? 0 : n < 0 ? m : n;
        render();
        restart();
      }
      prev.addEventListener('click', function () { go(index - 1); });
      next.addEventListener('click', function () { go(index + 1); });
      window.addEventListener('resize', function () { index = Math.min(index, maxIndex()); render(false); });
      var x0 = null;
      var y0 = 0;
      root.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
      root.addEventListener('touchend', function (e) {
        if (x0 === null) return;
        var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
        if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) go(index + (dx < 0 ? 1 : -1));
        x0 = null;
      }, { passive: true });
      root.addEventListener('mouseenter', function () { clearInterval(timer); });
      root.addEventListener('mouseleave', restart);
      render(false);
      restart();
    });
  }

  /* ---------- Forms (send.php on the hosting) ---------- */
  function initForms() {
    var root = document.documentElement.getAttribute('data-root') || '';
    $$('form.js-form').forEach(function (form) {
      form.setAttribute('action', root + 'send.php');
      var msg = $('.zf__msg', form);
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var ok = true;
        $$('.zf__input', form).forEach(function (inp) {
          var v = inp.value.trim();
          var bad = (inp.required && !v) || (inp.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v));
          inp.classList.toggle('is-error', bad);
          inp.setAttribute('aria-invalid', bad ? 'true' : 'false');
          if (bad && ok) {
            ok = false;
            inp.focus();
            msg.textContent = inp.type === 'email' && v ? T.email : T.required;
          }
        });
        if (!ok) return;
        var btn = $('button[type=submit]', form);
        btn.disabled = true;
        msg.textContent = '';
        var data = new FormData(form);
        data.append('page', location.href);
        data.append('lang', docLang);
        fetch(form.getAttribute('action'), { method: 'POST', body: data, headers: { Accept: 'application/json' } })
          .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
          .then(function (j) {
            if (!j || !j.ok) throw new Error('fail');
            form.reset();
            msg.textContent = T.sent;
          })
          .catch(function () { msg.textContent = T.error; })
          .then(function () { btn.disabled = false; });
      });
    });
  }

  /* ---------- Map: load the iframe only when it gets close to the viewport ---------- */
  function initMap() {
    var box = $('[data-map]');
    if (!box) return;
    var root = document.documentElement.getAttribute('data-root') || '';
    function addFile(tag, attrs, done) {
      var el = document.createElement(tag);
      for (var k in attrs) el.setAttribute(k, attrs[k]);
      if (done) el.onload = done;
      document.head.appendChild(el);
    }
    function draw() {
      var L = window.L;
      var ll = [parseFloat(box.getAttribute('data-lat')), parseFloat(box.getAttribute('data-lng'))];
      var touch = window.matchMedia('(pointer: coarse)').matches;
      var map = L.map(box, {
        center: ll, zoom: 17, scrollWheelZoom: false, dragging: !touch, tap: false,
        attributionControl: true, zoomControl: true
      });
      // on phones the page keeps scrolling with one finger; the map moves with two
      if (touch) {
        box.addEventListener('touchstart', function (e) {
          if (e.touches.length > 1) map.dragging.enable(); else map.dragging.disable();
        }, { passive: true });
      }
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, attribution: '&copy; OpenStreetMap'
      }).addTo(map);
      var icon = L.divIcon({ className: 'map-pin', html: '<span></span>', iconSize: [34, 44], iconAnchor: [17, 42], popupAnchor: [0, -38] });
      L.marker(ll, { icon: icon, keyboard: false }).addTo(map)
        .bindPopup(box.getAttribute('data-popup'));
      map.attributionControl.setPrefix(false);
    }
    function load() {
      if (box.getAttribute('data-loaded')) return;
      box.setAttribute('data-loaded', '1');
      addFile('link', { rel: 'stylesheet', href: root + 'assets/vendor/leaflet/leaflet.css' });
      addFile('script', { src: root + 'assets/vendor/leaflet/leaflet.js' }, draw);
    }
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { load(); io.disconnect(); }
      }, { rootMargin: '400px' });
      io.observe(box);
    } else load();
  }

  /* ---------- Keep texts from overlapping in positioned sections ----------
     Elements keep their design positions. In RU / KK, when a text became taller than in
     English (data-eh = English heights), the elements below it in the same column move down
     and glass panels / sections grow. Below 1200px real overlaps are fixed in every language.
     Desktop English is never touched. */
  function reflowSection(sec) {
    var els = Array.prototype.filter.call(sec.children, function (e) { return e.classList.contains('el'); });
    els.forEach(function (e) {
      e.style.marginTop = '';
      if (e._fh) { e.style.height = ''; e._fh = 0; }
    });
    sec.style.height = '';
    var H = sec.offsetHeight, W = sec.offsetWidth;
    var bp = [1200, 960, 640, 480, 320].indexOf(screenRes());
    var fixOverlap = bp > 0; // below 1200px the original layout had overlaps of its own
    var items = els.filter(function (e) { return e.offsetParent !== null; }).map(function (e) {
      var m = e.className.match(/st-slide-\d+/);
      var eh = (e.getAttribute('data-eh') || '').split(',');
      var hEn = parseFloat(eh[bp]);
      var h = e.offsetHeight;
      // an image that has not loaded yet (lazy) counts with its design height
      if (h < 10 && /el--image\b/.test(e.className)) {
        var img = e.querySelector('img');
        h = hEn > 0 ? hEn : (img && img.getAttribute('height') ? +img.getAttribute('height') : e.offsetWidth);
      }
      return {
        e: e, top: e.offsetTop, left: e.offsetLeft, w: e.offsetWidth, h: h,
        grow: hEn > 0 ? Math.max(0, h - hEn) : 0,
        slide: m ? m[0] : '', shift: 0,
        content: /el--(text|button|image|form)\b/.test(e.className) || e.classList.contains('svc-card') ||
          (/el--shape\b/.test(e.className) && h < 150 && e.offsetWidth < 300) // small badges move with their row
      };
    });
    var content = items.filter(function (i) { return i.content && i.h < H * 0.8 && i.w < W * 0.95; });
    content.sort(function (a, b) { return a.top - b.top; });
    function sameRow(a, b) {
      var ix = Math.min(a.left + a.w, b.left + b.w) - Math.max(a.left, b.left);
      var ah = a.h - a.grow, bh = b.h - b.grow; // compare the design (English) boxes
      var iy = Math.min(a.top + ah, b.top + bh) - Math.max(a.top, b.top);
      var small = Math.min(a.w * ah, b.w * bh), big = Math.max(a.w * ah, b.w * bh);
      if (ix > 0 && iy > 0 && ix * iy >= 0.5 * small && small >= 0.25 * big) return true; // stacked badge
      if (Math.abs(a.top - b.top) > 14 && Math.abs(a.top + ah / 2 - b.top - bh / 2) > 14) return false;
      var gap = Math.max(a.left, b.left) - Math.min(a.left + a.w, b.left + b.w);
      return gap < 120;
    }
    var moved = false;
    // repeat until nothing changes: a row (button, photos, badge) settles on one shift
    for (var pass = 0, changed = true; changed && pass < 8; pass++) {
      changed = false;
      content.forEach(function (b, bi) {
        var shift = pass ? b.shift : 0;
        for (var ai = 0; ai < content.length; ai++) {
          var a = content[ai];
          if (a === b) continue;
          if (a.slide && b.slide && a.slide !== b.slide) continue;
          if (sameRow(a, b)) { shift = Math.max(shift, a.shift); continue; }
          if (ai >= bi || a.top >= b.top - 2) continue;
          var ov = Math.min(a.left + a.w, b.left + b.w) - Math.max(a.left, b.left);
          if (ov < 10) continue;
          shift = Math.max(shift, a.shift + a.grow);
          if (fixOverlap && b.top >= a.top + Math.min((a.h - a.grow) * 0.5, 40)) {
            shift = Math.max(shift, a.top + a.h + a.shift + 6 - b.top);
          }
        }
        shift = Math.round(shift);
        if (shift !== b.shift) { b.shift = shift; changed = true; }
      });
    }
    content.forEach(function (b) {
      if (b.shift > 0) { b.e.style.marginTop = b.shift + 'px'; moved = true; }
    });
    var extra = 0;
    content.forEach(function (c) { if (c.shift || c.grow) extra = Math.max(extra, c.shift + c.grow); });
    var overflow = content.some(function (c) { return c.top + c.h > H - 8; });
    if (!moved && !extra && !overflow) return;
    // glass panels and backgrounds that hold the moved content grow with it
    items.filter(function (i) {
      if (i.content || i.w >= W * 0.98) return false;
      var atom = i.e.querySelector('.a');
      var r = atom ? parseFloat(getComputedStyle(atom).borderTopLeftRadius) || 0 : 0;
      return r < Math.min(i.w, i.h) / 2 - 1; // circles keep their shape
    }).forEach(function (s) {
      var inside = content.filter(function (c) {
        return c.left >= s.left - 4 && c.left + c.w <= s.left + s.w + 4 && c.top >= s.top - 4 && c.top <= s.top + s.h;
      });
      var add = 0;
      inside.forEach(function (c) { add = Math.max(add, c.shift + c.grow); });
      if (add > 0) { s.e.style.height = (s.h + add) + 'px'; s.e._fh = 1; }
    });
    // the section grows by the growth of its lowest content
    var bottom = 0, lowest = null;
    content.forEach(function (c) { if (c.top + c.h - c.grow > bottom) { bottom = c.top + c.h - c.grow; lowest = c; } });
    var need = 0;
    content.forEach(function (c) {
      if (c.top + c.h - c.grow >= bottom - 40) need = Math.max(need, c.shift + c.grow);
    });
    // nothing may end below the section (it would be cut off): grow it, and its backgrounds
    var maxBottom = 0;
    content.forEach(function (c) { maxBottom = Math.max(maxBottom, c.top + c.h + c.shift); });
    var newH = Math.max(H + need, maxBottom > H - 8 ? maxBottom + 32 : 0);
    if (newH > H) {
      sec.style.height = newH + 'px';
      items.forEach(function (i) {
        if (!i.content && i.h >= H * 0.9 && i.top <= 2) { i.e.style.height = (i.h + newH - H) + 'px'; i.e._fh = 1; }
      });
    }
  }

  /* Longer RU / KK headings: shrink a text that runs off the screen or into its neighbour */
  function fitTexts(sec) {
    var W = sec.offsetWidth;
    var els = Array.prototype.filter.call(sec.children, function (e) {
      return e.classList.contains('el') && e.offsetParent !== null;
    });
    els.filter(function (e) { return e.classList.contains('el--text'); }).forEach(function (e) {
      var a = e.querySelector('.a');
      if (!a) return;
      a.style.fontSize = '';
      var base = parseFloat(getComputedStyle(a).fontSize);
      if (base < 18) return; // body text wraps by itself
      var slide = e.className.match(/st-slide-\d+/);
      function bad() {
        var l = e.offsetLeft, r = l + Math.max(e.offsetWidth, a.scrollWidth), t = e.offsetTop, b = t + e.offsetHeight;
        if (r > W - 4 || a.scrollWidth > e.clientWidth + 2) return true;
        return els.some(function (o) {
          if (o === e || o.offsetLeft <= l + 10 || !/el--(text|button|image)/.test(o.className)) return false;
          var os = o.className.match(/st-slide-\d+/);
          if (slide && os && os[0] !== slide[0]) return false;
          var ot = o.offsetTop, ob = ot + o.offsetHeight;
          return ot < b - 4 && ob > t + 4 && r > o.offsetLeft - 4;
        });
      }
      var size = base;
      while (bad() && size > base * 0.6) {
        size = Math.round(size * 0.94 * 10) / 10;
        a.style.fontSize = size + 'px';
      }
    });
  }

  function initReflow() {
    var secs = $$('section.z');
    var t;
    function run() {
      if (docLang !== 'en') secs.forEach(fitTexts);
      secs.forEach(reflowSection);
    }
    run();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(run);
    window.addEventListener('load', function () { run(); setTimeout(run, 400); setTimeout(run, 1500); });
    if (document.fonts && document.fonts.addEventListener) {
      document.fonts.addEventListener('loadingdone', function () { clearTimeout(t); t = setTimeout(run, 60); });
    }
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(run, 150); });
    // any late change of a text box (font swap, hyphenation, zoom) re-runs the layout pass
    if ('ResizeObserver' in window) {
      var sizes = new WeakMap();
      var ro = new ResizeObserver(function (entries) {
        var changed = entries.some(function (en) {
          var h = Math.round(en.contentRect.height), w = Math.round(en.contentRect.width);
          var old = sizes.get(en.target);
          sizes.set(en.target, w + 'x' + h);
          return old !== undefined && old !== w + 'x' + h;
        });
        if (changed) { clearTimeout(t); t = setTimeout(run, 80); }
      });
      secs.forEach(function (sec) {
        Array.prototype.forEach.call(sec.querySelectorAll(':scope > .el--text, :scope > .el--image'), function (e) { ro.observe(e); });
      });
    }
  }

  /* ---------- Team accordion ---------- */
  function initAccordion() {
    $$('.acc__btn').forEach(function (btn) {
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      btn.addEventListener('click', function () {
        var open = btn.getAttribute('aria-expanded') !== 'true';
        btn.setAttribute('aria-expanded', String(open));
        if (reduceMotion) { panel.hidden = !open; return; }
        if (open) {
          panel.hidden = false;
          var h = panel.scrollHeight;
          panel.style.height = '0px';
          panel.style.opacity = '0';
          requestAnimationFrame(function () {
            panel.style.height = h + 'px';
            panel.style.opacity = '1';
          });
        } else {
          panel.style.height = panel.scrollHeight + 'px';
          requestAnimationFrame(function () {
            panel.style.height = '0px';
            panel.style.opacity = '0';
          });
        }
        panel.addEventListener('transitionend', function done(e) {
          if (e.propertyName !== 'height') return;
          panel.removeEventListener('transitionend', done);
          if (btn.getAttribute('aria-expanded') === 'true') panel.style.height = '';
          else panel.hidden = true;
        });
      });
    });
  }

  function initScrolled() {
    var on = false;
    function check() {
      var y = window.pageYOffset > 10;
      if (y !== on) { on = y; document.documentElement.classList.toggle('is-scrolled', y); }
    }
    check();
    window.addEventListener('scroll', check, { passive: true });
  }

  function init() {
    initScrolled();
    initAccordion();
    initReflow();
    initAppear();
    initSbs();
    initHeroSlider();
    initLangMenu();
    initBurger();
    initPopup();
    initBrands();
    initForms();
    initMap();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
