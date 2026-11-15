---
name: reel-edit
description: Edit the user's raw phone/camera footage into a finished, sharp 1080x1920 Instagram/Facebook Reel in one of their two signature looks - "kinetic" (talking head, tight jump cuts, word-by-word captions with gradient/neon hero words, counters, pills, photo cards, call banner, light streaks, flashes) or "cinematic" (B-roll shot sequences between locations, giant yellow condensed titles often behind the subject, small serif subtitles, collages, film grade). Use whenever the user hands over raw video clips or b-roll and wants them edited, cut, captioned, "made into a reel", or edited "like the reference" / "in my style".
---

# Reel edit

Two looks, both learned from reference reels the user supplied. Read the matching reference file
once per session before editing - it has the beat-by-beat breakdown:

| look | reference | pick it when |
|---|---|---|
| **kinetic** | `reference/kinetic.md` (realtor talking head) | mostly talking to camera; claims, numbers, tips, business/personal-brand |
| **cinematic** | `reference/cinematic.md` (creator moving between locations) | there's B-roll/travel/multiple places; storytelling, voice-over over visuals |

If the user doesn't say, choose from the footage (lots of b-roll -> cinematic, all talking head ->
kinetic) and say which you chose in one line. They can ask for "the realtor style" (kinetic) or
"the cinematic / location style". Mixing is allowed: e.g. a kinetic reel can use a `title` for a
location, a cinematic reel can use a `counter`.

**Shared DNA (both looks):** no dead air, no ums, no retakes; a hook inside the first second; every
claim gets a visual; cut on the word; the ending flows back into the opening so it loops.

**Kinetic in short:** a jump cut at every sentence, alternating wide and punched-in framing; captions appear
word by word at chest height; one huge hero word per sentence (purple/cyan gradient, neon yellow);
counters, pills, photo cards, call banner, streaks, flash, zoom-blur; warm glow grade.

**Cinematic in short:** B-roll mini-sequences carry the story while the voice runs (grab handle ->
drive -> step out -> arrive); giant yellow Anton titles (place names, key words) fitted edge to edge
in the top third, often **behind the subject**; quiet small yellow serif subtitles; collages of past
work; one location per "here"; hand-over-lens and rack-focus transitions; natural film grade.

## Quality rules (the user posts to IG and FB Reels - it must never look soft)

- **Delivery spec (handled by `render`/`deliver`):** 1080x1920 9:16, H.264 High 4.2, 30fps CFR,
  yuv420p BT.709, CRF 16 capped at 25 Mbps (≈15-25 Mbps), AAC 320k 48kHz, faststart.
  1080x1920 is the maximum both apps display; uploading larger only lets the app downscale it
  worse, so we downscale ourselves once, with lanczos, from the camera original.
- **The source decides sharpness.** `plan` prints a WARNING for any clip below 1080x1920 after the
  crop. When you see it, tell the user plainly and ask for the original camera file. Screen
  recordings, WhatsApp/Messenger/AirDrop "compatible" copies and downloads from Instagram are the
  usual culprits. The first test edit looked blurry because its source was a 512x910 screen
  recording. No upscaling fixes that.
- No punch-in on footage that's already short of pixels (`plan` drops it to 1.0 automatically).
  4K sources can punch in to ~1.9x with no loss.
- Pipeline quality: one lanczos resample from the camera pixels, light unsharp, CRF 10
  intermediates, HyperFrames frames extracted as PNG, near-lossless master, then exactly one
  delivery encode. Don't add extra re-encodes (no exporting then re-importing).
- iPhone HDR (HLG/Dolby Vision) is tone-mapped to SDR in `base`. Delivering HDR to Reels is
  unreliable, so it stays SDR.
- Tell the user to upload with **"Upload at highest quality"** turned on (Instagram: Settings ->
  Data usage and media quality; Facebook: Settings -> Media -> Video quality: HD) and over Wi-Fi.
- Duration: Facebook Reels max 90s; Instagram up to 3 min. `deliver` warns past 90s.

## Tools

`scripts/reel.py` uses Python 3, ffmpeg, Groq Whisper for transcripts, HyperFrames for graphics, and
rembg for the text-behind-subject matte. Check the prerequisites first:
```bash
hyperframes --version && python3 -c "import groq, rembg, fontTools" && ffmpeg -version | head -1
# missing: npm i -g hyperframes ; pip install groq "rembg[cpu]" fonttools brotli
```
Groq: in this cloud environment the proxy injects the key (any dummy value works); elsewhere set `GROQ_API_KEY`.
Fonts (Inter, Anton, Instrument Serif) and GSAP are copied into each project, so renders never hit a CDN.

## Workflow

Work in the scratchpad (or a folder the user names); `R=<skill dir>/scripts/reel.py`.

1. **Inspect.** `ffprobe` every file (resolution after rotation, fps, HDR). Make a contact sheet
   (`ffmpeg -i clip -vf fps=1,scale=240:-1,tile=8x4 sheet.jpg`) and look at it. Sort the files into
   A-roll (talking) and B-roll (no speech), and note the locations.
2. **Cut plan.** Run `python3 $R plan A1.mov A2.mov ... --look kinetic|cinematic --broll B1.mov B2.mov -o edl.json`.
   It transcribes (cached), splits into phrases, drops fillers, flags retakes, sets zooms and warns about resolution.
   **Review edl.json yourself:** read the kept text as a script. Drop flubs and repeats the heuristic
   missed, reorder by story, and set `zoom` (1.0-1.2) and `focus_y` (0 keeps the top, 0.38 is the default).
   Set the `grade`: `warm-glow` (kinetic), `cine-natural` (cinematic), `clean`, `none`, or any ffmpeg filter.
   For each b-roll entry, set `at` (seconds on the **edited** timeline, i.e. after cuts; check
   `work/words.json` after a first `base` run), `in`, and `dur`. Optionally set `sfx` (0-1) to mix in its natural
   sound under the voice (door clunk, engine, footsteps). B-roll replaces the picture; the voice keeps running.
   Cinematic: build mini-sequences of 0.4-0.8s shots that land the arrival shot on the word.
3. **Base.** `python3 $R base edl.json -o work` produces `work/base.mp4` (graded, b-roll inserted,
   -14 LUFS) and `work/words.json`. Re-run after changing b-roll `at` values.
4. **Draft captions.** `python3 $R captions work` writes `work/plan.json`. Kinetic gets word-by-word
   captions with hero words; cinematic gets serif phrase subtitles.
5. **Art-direct plan.json.** This is the creative step, so never ship the draft as-is.
   - Kinetic: choose the hero words yourself; hooks get `hook` or a pop style at y≈0.2. Add a
     counter, pills, cards, call, streak, punch or flash wherever there's a claim.
   - Cinematic: add a `title` for every location name and the 1-2 key words of the reel (use
     `"behind": true` when the subject is under the title area; titles sit at y≈0.06-0.3). Add a `grid`
     when they mention past work. Keep subtitles off titles (y≈0.62-0.7).
   - Ask the user for photos, b-roll or screenshots whenever the script references things you
     don't have. Cards, grids and cutaways need real images.
6. **Compose + render.** Run `python3 $R compose work work/plan.json && python3 $R render work -o final.mp4`.
   This writes the near-lossless `work/master.mp4`, then the Reels-spec `final.mp4`. Use `-q draft` for previews.
   Allow about 1-2 minutes of render time per 15s of video, plus about 30s per second of "behind" title (matting).
7. **QA.** Pull a frame at every title, hero word and overlay, then tile and look at them. Check that
   text is fitted and uncropped, faces are clear of text, nothing outstays its line, and the person
   sits in front of the "behind" titles. Check sharpness on a 1:1 crop of a face. Check loudness
   (`ffmpeg -i final.mp4 -af ebur128 -f null -`, I ≈ -14). Fix the plan and re-compose.
8. **Deliver.** Send `final.mp4` (SendUserFile) with a short summary of what was cut and which
   moments got graphics, the upload-quality tip, and any resolution warnings.

## plan.json reference

```jsonc
{"captions": [
  {"start": 0.0, "end": 0.95, "y": 0.40,                    // seconds on the edited timeline; y = fraction of height (centre)
   "lines": [ {"style": "lead",     "words": [["It's", 0.0], ["no", 0.18]]},
              {"style": "pop-cyan", "words": [["secret,", 0.3]]} ]}],   // each word appears at its own time
 "overlays": [ ... ]}
```
Caption styles: `lead` (thin small white), `word` (medium white), `hook` (giant thin white),
`white-heavy`, `pop-purple`, `pop-cyan`, `pop-silver` (heavy gradient), `neon-yellow` (glow),
`serif` (cinematic subtitle). Text can be edited freely; the timings come from words.json.

| overlay | fields | use for |
|---|---|---|
| `title` | start, end, lines[text or {text, at, px}], y, behind, margin, max_px | cinematic titles: place names, key words; auto-fitted to width |
| `grid` | start, end, items[{src, label}], top, bottom, stagger | collage of past videos/work |
| `counter` | start, end, from, to, suffix, lead, y, count_for | number claims - counts up |
| `cards` | start, end, images[], w, h, stagger, spots[[x,y,rot]] | listings/posts popping in around the speaker |
| `pills` | start, end, y, items[{text, at, x, y}] | spoken lists |
| `call` | start, end, y, name, sub | "clients call me" |
| `broll` | start, end, src (img/video), media_start | stills/screenshots as cutaways (video b-roll goes in the EDL instead, which is sharper) |
| `streak` | start, end, y | neon swoosh behind a results line |
| `punch` | at, scale, dur | zoom-blur whip into a section |
| `flash` | at, strength | white flash on a big beat |

Paths in overlays are relative to plan.json's folder, or absolute.

## Rules of thumb
- Target 30-60s (FB max 90s). Cut whole sentences rather than speeding up the voice.
- Never leave a caption up through a pause longer than 0.6s. Never stack more than 2 caption lines plus 1 overlay.
- Kinetic: one hero word per sentence, rotating purple -> cyan -> yellow.
  Cinematic: 1 title per location plus at most 2 word titles per reel, so they stay special.
- Keep the bottom 18% and the right 12% free of key content, because the app UI covers them.
- Selfie footage with the face high in frame: lower `focus_y` (0.2-0.3) instead of cutting off the head.
