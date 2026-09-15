#!/usr/bin/env node
/**
 * Canyon & Collar — proxy still and motion renderer.
 *
 * Drives headless Chromium over each vector plate, animating the SVG viewBox so
 * the camera move stays resolution-independent, then encodes the frame sequence.
 *
 *   node tools/render.js            # stills + motion for every asset
 *   node tools/render.js --stills   # stills only
 *   node tools/render.js --only 13  # a single asset
 */
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const FFMPEG = '/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux';
const FPS = 24;

const args = process.argv.slice(2);
const stillsOnly = args.includes('--stills');
const onlyIdx = args.indexOf('--only');
const only = onlyIdx >= 0 ? args[onlyIdx + 1] : null;

const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets', 'manifest.json'), 'utf8'));

const ease = {
  linear: t => t,
  in: t => t * t,
  out: t => 1 - (1 - t) * (1 - t),
  inout: t => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
};

function page_html(svg, w, h, label) {
  // Strip the plate's own pixel dimensions so it fills the stage, and keep the
  // viewBox — that is what the camera move animates.
  const sized = svg
    .replace(/(<svg[^>]*?)\swidth="\d+"/, '$1')
    .replace(/(<svg[^>]*?)\sheight="\d+"/, '$1')
    .replace(/<svg /, '<svg id="plate" preserveAspectRatio="xMidYMid slice" ' +
                      `style="position:absolute;inset:0;width:${w}px;height:${h}px" `);
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;background:#0B0A09;overflow:hidden}
  #stage{position:relative;width:${w}px;height:${h}px;overflow:hidden}
  #grain,#fade{position:absolute;inset:0;pointer-events:none}
  #fade{background:#000;opacity:0}
  /* inset far enough that a 16:9 crop of a 2.39:1 plate never clips it */
  #mark{position:absolute;right:${Math.round(w * 0.175)}px;bottom:${Math.round(h * 0.055)}px;
        font:${Math.round(h * 0.018)}px/1.5 Helvetica,Arial,sans-serif;letter-spacing:.3em;
        color:#F3EBDF;opacity:.38;text-transform:uppercase}
</style></head><body><div id="stage">${sized}
  <svg id="grain" width="${w}" height="${h}"><filter id="g"><feTurbulence id="turb" type="fractalNoise"
    baseFrequency="0.9" numOctaves="2" seed="1"/><feColorMatrix type="saturate" values="0"/></filter>
    <rect width="${w}" height="${h}" filter="url(#g)" opacity="0.07"/></svg>
  <div id="mark">${label}</div><div id="fade"></div></div>
<script>
  const plate = document.getElementById('plate');
  const vb = plate.getAttribute('viewBox').split(/\\s+/).map(Number);
  const BW = vb[2], BH = vb[3];
  window.setFrame = (z, dx, dy, seed, fade) => {
    const w = BW / z, h = BH / z;
    const x = (BW - w) / 2 + dx * BW / 100;
    const y = (BH - h) / 2 + dy * BH / 100;
    plate.setAttribute('viewBox', x.toFixed(2)+' '+y.toFixed(2)+' '+w.toFixed(2)+' '+h.toFixed(2));
    document.getElementById('turb').setAttribute('seed', String(seed));
    document.getElementById('fade').style.opacity = String(fade);
  };
<\/script></body></html>`;
}

(async () => {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
  const chapters = manifest.chapters.filter(c => !only || c.id === only);

  for (const c of chapters) {
    const svg = fs.readFileSync(path.join(ROOT, c.vector), 'utf8');
    const [bw, bh] = c.ratio === '2.39:1' ? [2390, 1000] : [1920, 1080];

    // ---- still -------------------------------------------------------------
    const stillPage = await browser.newPage({ viewport: { width: bw, height: bh } });
    await stillPage.setContent(page_html(svg, bw, bh, ''), { waitUntil: 'load' });
    await stillPage.evaluate(() => window.setFrame(1, 0, 0, 3, 0));
    await stillPage.locator('#stage').screenshot({
      path: path.join(ROOT, c.poster), type: 'jpeg', quality: 92,
    });
    await stillPage.close();
    console.log('still  ' + c.poster);

    if (stillsOnly || !c.video) continue;

    // ---- motion ------------------------------------------------------------
    const [vw, vh] = c.ratio === '2.39:1' ? [1600, 670] : [1600, 900];
    const m = c.move;
    const frames = Math.round(m.dur * FPS);
    const out = path.join(ROOT, c.video);

    // This ffmpeg build only demuxes image2pipe, so frames are streamed straight
    // from the browser into the encoder — nothing hits the disk in between.
    const ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe',
      '-vcodec', 'mjpeg', '-framerate', String(FPS), '-i', 'pipe:0',
      '-c:v', 'libvpx', '-b:v', '1800k', '-crf', '31', '-deadline', 'good',
      '-cpu-used', '2', '-auto-alt-ref', '0', '-pix_fmt', 'yuv420p', out]);
    ff.stderr.on('data', d => process.stderr.write(d));
    const done = new Promise((res, rej) => {
      ff.on('close', code => (code === 0 ? res() : rej(new Error('ffmpeg exit ' + code))));
    });
    const write = buf => new Promise(res => (ff.stdin.write(buf) ? res() : ff.stdin.once('drain', res)));

    const label = `${c.id} ${c.title.split(' / ')[0]} · proxy`;
    const p = await browser.newPage({ viewport: { width: vw, height: vh } });
    await p.setContent(page_html(svg, vw, vh, label), { waitUntil: 'load' });
    const stage = p.locator('#stage');
    const fn = ease[m.ease] || ease.inout;

    for (let i = 0; i < frames; i++) {
      const raw = frames === 1 ? 0 : i / (frames - 1);
      const t = fn(raw);
      let z = m.z[0] + (m.z[1] - m.z[0]) * t;
      let dx = m.x[0] + (m.x[1] - m.x[0]) * t;
      let dy = m.y[0] + (m.y[1] - m.y[0]) * t;
      if (m.handheld) {                       // the one handheld shot in the film
        dx += Math.sin(i / 7.3) * 0.16 + Math.sin(i / 3.1) * 0.05;
        dy += Math.cos(i / 6.1) * 0.14 + Math.sin(i / 4.7) * 0.04;
      }
      const secs = i / FPS, rem = m.dur - secs;
      const fade = Math.max(0, Math.min(1,
        Math.max(secs < 0.5 ? 1 - secs / 0.5 : 0, rem < 0.5 ? 1 - rem / 0.5 : 0)));
      await p.evaluate(([z, dx, dy, s, f]) => window.setFrame(z, dx, dy, s, f),
        [z, dx, dy, (i * 7) % 97, fade]);
      await write(await stage.screenshot({ type: 'jpeg', quality: 90 }));
    }
    ff.stdin.end();
    await done;
    await p.close();
    const kb = Math.round(fs.statSync(out).size / 1024);
    console.log(`motion ${c.video}  ${frames} frames  ${m.dur}s  ${kb}KB  (${m.note})`);
  }

  await browser.close();
})();
