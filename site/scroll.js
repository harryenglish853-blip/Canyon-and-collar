/**
 * Canyon & Collar — scroll-driven journey.
 *
 * Everything on this page is built from ../assets/manifest.json. Each chapter
 * owns a slice of the page scroll (the ranges are the ones in the brief), and
 * the stage cross-dissolves between chapters as that slice passes. Swap a
 * proxy plate for final footage in the manifest and nothing here changes.
 */
(() => {
  const STAGE = document.getElementById('stage');
  const RAIL = document.getElementById('rail');
  const CUE = document.getElementById('cue');
  const BAR = document.getElementById('progress');
  const JOURNEY = document.getElementById('journey');
  const BRANDMARK = document.getElementById('brandmark');
  const STATE = document.getElementById('colophon-state');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = t => t * t * (3 - 2 * t);

  let scenes = [];
  let active = -1;
  let ticking = false;

  fetch('../assets/manifest.json')
    .then(r => r.json())
    .then(build)
    .catch(err => { STATE.textContent = 'Manifest failed to load'; console.error(err); });

  function build(manifest) {
    const chapters = manifest.chapters.filter(c => c.scroll);
    const brand = manifest.chapters.find(c => !c.scroll);

    // The journey needs enough runway that each chapter gets real scroll time.
    JOURNEY.style.height = `${chapters.length * 135 + 100}svh`;

    chapters.forEach((c, i) => {
      const scene = document.createElement('div');
      scene.className = 'scene';
      scene.dataset.id = c.id;

      let plate;
      if (c.video && !reduced) {
        plate = document.createElement('video');
        plate.src = c.video;
        plate.muted = true;
        plate.loop = true;
        plate.playsInline = true;
        plate.preload = i < 3 ? 'auto' : 'metadata';
        plate.poster = '../' + c.poster;
        plate.setAttribute('aria-hidden', 'true');
      } else {
        plate = document.createElement('img');
        plate.src = '../' + c.poster;
        plate.alt = c.title;
        plate.loading = i < 2 ? 'eager' : 'lazy';
      }
      if (plate.tagName === 'VIDEO') plate.src = '../' + c.video;
      plate.className = 'plate';
      scene.appendChild(plate);

      if (c.overlay.length) {
        const copy = document.createElement('div');
        // Type goes where the shot reserved room for it.
        const space = (c.negativeSpace || '').toLowerCase();
        const place = (space.includes('upper') || space.includes('sky') ? ' top' : '')
                    + (space.startsWith('right') ? ' right' : '');
        copy.className = 'copy' + (c.id === '01' || c.id === '18' ? ' wordmark' : '') + place;
        const eyebrow = document.createElement('p');
        eyebrow.className = 'eyebrow';
        eyebrow.textContent = c.chapter;
        copy.appendChild(eyebrow);
        c.overlay.forEach((line, li) => {
          const el = document.createElement('span');
          el.className = 'line';
          el.style.setProperty('--i', String(li));
          el.textContent = line;
          copy.appendChild(el);
        });
        if (i === 0) copy.classList.add('intro');
        scene.appendChild(copy);
      }

      STAGE.appendChild(scene);

      const btn = document.createElement('button');
      btn.innerHTML = `<span class="name">${c.chapter}</span><span class="tick"></span>`;
      btn.title = `${c.id} — ${c.title}`;
      btn.addEventListener('click', () => {
        const mid = (c.scroll[0] + c.scroll[1]) / 2;
        scrollTo({ top: mid * scrollable(), behavior: 'smooth' });
      });
      RAIL.appendChild(btn);

      scenes.push({ c, scene, plate, btn, lines: [...scene.querySelectorAll('.line')] });
    });

    if (brand) {
      const el = document.createElement(brand.video && !reduced ? 'video' : 'img');
      if (el.tagName === 'VIDEO') {
        Object.assign(el, { src: '../' + brand.video, muted: true, loop: true, playsInline: true });
        el.poster = '../' + brand.poster;
      } else {
        el.src = '../' + brand.poster;
        el.alt = brand.title;
      }
      BRANDMARK.prepend(el);
      new IntersectionObserver(es => es.forEach(e => {
        if (el.tagName !== 'VIDEO') return;
        e.isIntersecting ? el.play().catch(() => {}) : el.pause();
      }), { threshold: 0.25 }).observe(BRANDMARK);
    }

    const proxies = manifest.chapters.filter(c => c.posterIsProxy).length;
    STATE.textContent = `${manifest.chapters.length} scenes · ${proxies} proxy plates`;

    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', () => requestAnimationFrame(render), { passive: true });
    render();
    setTimeout(() => { if (scrollY < 40) CUE.style.opacity = '.6'; }, 1400);
  }

  const scrollable = () => JOURNEY.offsetHeight - innerHeight;

  function onScroll() {
    CUE.style.opacity = scrollY > 40 ? '0' : '.6';
    if (!ticking) { ticking = true; requestAnimationFrame(() => { render(); ticking = false; }); }
  }

  function render() {
    const p = clamp(scrollY / Math.max(1, scrollable()));
    BAR.style.width = `${p * 100}%`;

    let top = -1, topOpacity = 0;

    scenes.forEach((s, i) => {
      const [a, b] = s.c.scroll;
      const span = Math.max(0.0001, b - a);
      const local = (p - a) / span;
      // Cross-dissolve: each chapter fades up over its first fifth and away
      // over its last fifth, so two chapters are never hard-cut against.
      const fade = 0.22;
      let o = 0;
      if (local > -fade && local < 1 + fade) {
        o = local < fade ? smooth(clamp((local + fade) / (fade * 2)))
          : local > 1 - fade ? smooth(clamp((1 + fade - local) / (fade * 2)))
          : 1;
      }
      s.scene.style.opacity = o.toFixed(3);
      s.scene.style.zIndex = String(Math.round(o * 100));

      if (o > topOpacity) { topOpacity = o; top = i; }

      if (o > 0.01) {
        // Stills get a slow push; video carries its own move, so it only gets
        // a whisper of drift to keep the cut from feeling static.
        const t = clamp(local);
        const z = s.plate.tagName === 'VIDEO' ? 1.02 + t * 0.02 : 1.10 - t * 0.09;
        const y = (t - 0.5) * (s.plate.tagName === 'VIDEO' ? 6 : 22);
        if (!reduced) s.plate.style.transform = `scale(${z.toFixed(3)}) translate3d(0,${y.toFixed(1)}px,0)`;

        const first = i === 0;
        s.lines.forEach((line, li) => {
          const out = smooth(clamp((t - (first ? 0.82 : 0.80)) / 0.18));
          if (first) {
            // the CSS intro owns the entrance; only the exit is scroll-driven
            if (t > 0.04) {
              line.style.opacity = (1 - out).toFixed(3);
              line.style.transform = 'none';
            }
            return;
          }
          const k = smooth(clamp((t - (0.10 + li * 0.07)) / 0.22));
          line.style.opacity = (k * (1 - out)).toFixed(3);
          line.style.transform = `translateY(${(1 - k) * 26}px)`;
        });
      }

      if (s.plate.tagName === 'VIDEO') {
        if (o > 0.45) { if (s.plate.paused) s.plate.play().catch(() => {}); }
        else if (!s.plate.paused) s.plate.pause();
      }
    });

    if (top !== active) {
      scenes.forEach((s, i) => s.btn.setAttribute('aria-current', String(i === top)));
      active = top;
    }
  }
})();
