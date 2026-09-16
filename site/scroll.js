/**
 * Canyon & Collar.
 *
 * The film plays. Chapter typography from ../assets/manifest.json fades in and
 * out over it as its slice of the scroll passes — no motion is added to the
 * footage and none is faked around it.
 */
(() => {
  const STAGE = document.getElementById('stage');
  const RAIL = document.getElementById('rail');
  const CUE = document.getElementById('cue');
  const BAR = document.getElementById('progress');
  const JOURNEY = document.getElementById('journey');
  const BRANDMARK = document.getElementById('brandmark');
  const STATE = document.getElementById('colophon-state');
  const SOUND = document.getElementById('sound');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = t => t * t * (3 - 2 * t);

  let chapters = [];
  let film = null;
  let active = -1;
  let ticking = false;

  fetch('../assets/manifest.json')
    .then(r => r.json())
    .then(build)
    .catch(err => { STATE.textContent = 'Manifest failed to load'; console.error(err); });

  function makeFilm(film, preload = 'auto') {
    const v = document.createElement('video');
    v.src = '../' + film.src;
    if (film.poster) v.poster = '../' + film.poster;
    v.muted = true;
    v.loop = true;
    v.playsInline = true;
    v.preload = preload;
    v.setAttribute('aria-hidden', 'true');
    return v;
  }

  function build(manifest) {
    const spine = manifest.chapters.filter(c => c.scroll);

    // Enough runway that every chapter gets real scroll time of its own.
    JOURNEY.style.height = `${spine.length * 135 + 100}svh`;

    film = makeFilm(manifest.film);
    film.className = 'film';
    STAGE.prepend(film);
    film.play().catch(() => {});
    film.addEventListener('error', () => {
      STATE.textContent = 'Film failed to load';
      STAGE.classList.add('film-failed');
    });
    if (reduced) film.pause();

    if (manifest.film.hasAudio) setupSound();
    else SOUND.remove();

    spine.forEach((c, i) => {
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

      (c.overlay || []).forEach(line => {
        const el = document.createElement('span');
        el.className = 'line';
        el.textContent = line;
        copy.appendChild(el);
      });
      STAGE.appendChild(copy);

      const btn = document.createElement('button');
      btn.innerHTML = `<span class="name">${c.chapter}</span><span class="tick"></span>`;
      btn.title = `${c.id} — ${c.title}`;
      btn.addEventListener('click', () => {
        const mid = (c.scroll[0] + c.scroll[1]) / 2;
        scrollTo({ top: mid * scrollable(), behavior: 'smooth' });
      });
      RAIL.appendChild(btn);

      chapters.push({ c, copy, btn });
    });

    // The closing band replays the same film. It stays unloaded until it is
    // nearly on screen — by then the file is in cache from the stage above.
    const band = makeFilm(manifest.film, 'none');
    BRANDMARK.prepend(band);
    new IntersectionObserver(es => es.forEach(e => {
      if (reduced) return;
      if (e.isIntersecting) { band.preload = 'auto'; band.play().catch(() => {}); }
      else band.pause();
    }), { threshold: 0.25 }).observe(BRANDMARK);

    STATE.textContent = `${spine.length} chapters · one continuous film`;

    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', () => requestAnimationFrame(render), { passive: true });
    render();
  }

  /* The film carries its own sound, so it is offered rather than forced: muted
     to satisfy autoplay, with the viewer opting in. */
  function setupSound() {
    const label = SOUND.querySelector('.label');
    const set = on => {
      film.muted = !on;
      SOUND.setAttribute('aria-pressed', String(on));
      label.textContent = on ? 'Sound on' : 'Sound';
    };
    set(false);
    SOUND.addEventListener('click', () => {
      const on = SOUND.getAttribute('aria-pressed') !== 'true';
      set(on);
      if (on) film.play().catch(() => set(false));
    });
  }

  const scrollable = () => JOURNEY.offsetHeight - innerHeight;

  function onScroll() {
    CUE.style.opacity = scrollY > 40 ? '0' : '.55';
    if (!ticking) { ticking = true; requestAnimationFrame(() => { render(); ticking = false; }); }
  }

  function render() {
    const p = clamp(scrollY / Math.max(1, scrollable()));
    BAR.style.width = `${p * 100}%`;

    let top = -1, topOpacity = 0;

    chapters.forEach((s, i) => {
      const [a, b] = s.c.scroll;
      const span = Math.max(0.0001, b - a);
      const local = (p - a) / span;
      // Each chapter's type fades up over its first fifth and away over its
      // last fifth, so two chapters are never on screen at full strength at
      // once. The opening title and the closing hero are the exceptions —
      // there is nothing on the other side of them to dissolve with, and both
      // have to sit at full strength at the very top and bottom of the page.
      const fade = 0.22;
      let o = 0;
      if (local > -fade && local < 1 + fade) {
        const up = i === 0 ? 1 : smooth(clamp((local + fade) / (fade * 2)));
        const down = i === chapters.length - 1 ? 1
          : smooth(clamp((1 + fade - local) / (fade * 2)));
        o = Math.min(up, down);
      }
      s.copy.style.opacity = o.toFixed(3);
      s.copy.style.pointerEvents = o > 0.5 ? 'auto' : 'none';

      if (o > topOpacity) { topOpacity = o; top = i; }
    });

    if (top !== active) {
      chapters.forEach((s, i) => s.btn.setAttribute('aria-current', String(i === top)));
      active = top;
    }
  }
})();
