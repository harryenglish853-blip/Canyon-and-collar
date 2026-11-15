---
name: reel-edit
description: Edit raw talking-head phone footage into a finished vertical Instagram/TikTok reel in the user's signature style - tight jump cuts, punch-in reframes, warm glowy grade, kinetic word-by-word captions with gradient/neon hero words, animated counters, pill callouts, floating photo cards, call banner, light streaks, flash and zoom-blur transitions. Use whenever the user hands over raw video clips (selfie/talking-to-camera, real-estate/business/personal-brand content) and wants them edited, cut, captioned or "made into a reel", or asks to edit "like the reference" / "in my style".
---

# Reel edit - talking-head, kinetic-caption style

The style was learned from a reference reel (a realtor speaking straight to camera across
5-6 outdoor locations, ~37s). `reference/style.md` has the full shot-by-shot breakdown - read
it once before your first edit in a session. The short version:

**Style DNA**
- **Every sentence is its own shot.** Hard jump cuts on sentence/phrase boundaries (avg ~2.5-5s),
  no breaths, no "um", no dead air. Location or framing changes at most cuts:
  wide (full body walking/sitting) <-> punched-in medium (waist-up).
- **The words are the edit.** Captions appear word-by-word at the moment they're spoken, centred at
  chest/face height, 1-3 words on screen. Small thin white "lead" words lead into one
  **hero word per sentence** - huge, heavy, gradient (purple, cyan, silver) or neon yellow glow.
  Hero = the number or payoff noun ("secret", "CLIENTS", "2026", "50 HOMES", "SOLD", "2 THINGS",
  "skills", "Transparency", "investment").
- **Every claim gets a visual proof.** Numbers count up ("12 -> 46 -> 50 HOMES") with photo cards of
  the listings popping in around the speaker; "2 things" gets glowing pill buttons that land on each
  item as it's said; "marketing" gets floating thumbnails of their posts; "clients reach out" gets an
  incoming-call banner; "deliver" gets a neon light streak; social proof is a full-screen cutaway of a
  real post.
- **Motion everywhere, all of it fast:** text blurs/scales in (0.18-0.3s), zoom-blur whip into a new
  section ("So, let's talk about how."), white flash on big beats, Ken-Burns on cutaways.
- **Look:** warm, saturated greens, lifted and slightly glowy (bloom), soft vignette, golden-hour feel.
- **Sound:** voice-first, compressed, -14 LUFS. No music needed; if added, keep it under the voice.
- **Hook in the first second, loop at the end:** the opening line lands a hero word inside 0.5s; the
  last shot returns to the opening location so the reel loops seamlessly.

## Tools

`scripts/reel.py` (Python 3, ffmpeg, Groq Whisper for transcription, HyperFrames for the graphics
render). Check prerequisites first:

```bash
hyperframes --version && python3 -c "import groq" && ffmpeg -version | head -1
# missing? npm i -g hyperframes ; pip install groq
```
Groq: in this cloud environment the proxy injects the key (any dummy value works); elsewhere set `GROQ_API_KEY`.
HyperFrames renders offline - GSAP and the Inter font are copied into the project, never pulled from a CDN.

## Workflow

Work in the scratchpad (or a folder the user names); `R=<skill dir>/scripts/reel.py`.

1. **Inspect the raw files.** `ffprobe` each (duration, orientation, HDR?), and make a contact sheet
   (`ffmpeg -i clip -vf fps=1,scale=240:-1,tile=8x4 sheet.jpg`) and look at it - know which clip is
   which location/framing before cutting.
2. **Cut plan:** `python3 $R plan raw1.mov raw2.mov ... -o edl.json` - transcribes every clip
   (cached `*.words.json`), splits into phrases at pauses, drops fillers, marks retakes `keep:false`
   (an earlier take whose opening is repeated later), alternates zoom 1.0 / 1.14 / 1.0 / 1.08.
   **Review edl.json yourself** - this is editorial judgement, not a formality:
   - read the kept text top to bottom: does it read as one clean script? Remove flubs, false starts,
     repeated takes the heuristic missed; reorder segments if the user's clips are out of order.
   - order clips by the story, not by filename, when the user's script says so.
   - `zoom` per segment (1.0 wide - 1.2 tight) and `focus_y` (0 = keep top, 0.38 default keeps
     faces in frame) - set framing so consecutive shots differ.
   - `grade`: `warm-glow` (default, the reference look), `clean`, `none`, or a raw ffmpeg filter.
3. **Base edit:** `python3 $R base edl.json -o work` -> `work/base.mp4` (1080x1920, 30fps, graded,
   HDR tone-mapped, loudness -14 LUFS) and `work/words.json` (word timings on the new timeline).
4. **Draft captions:** `python3 $R captions work` -> `work/plan.json` (word-by-word captions, one
   auto-picked hero word per sentence, rotating colours).
5. **Art-direct plan.json - the creative step; never ship the draft as-is.** Read the script and:
   - pick each sentence's hero word yourself (numbers, results, the emotional payoff); give hooks and
     section openers `hook` (giant thin white, top third, y≈0.2) or a pop style at y≈0.2-0.3;
   - keep ordinary captions at y≈0.45-0.5 (chest), and keep them off the face;
   - add overlays for every claim (types below). Ask the user for b-roll/photos when the script
     mentions listings, posts, results, testimonials - cards/cutaways need real images;
   - `punch` at every new section, `flash` on the biggest one or two beats, not more.
6. **Compose + render:** `python3 $R compose work work/plan.json && python3 $R render work -o final.mp4`
   (`-q draft` for a quick look; default `delivery`). ~1 min render per 15s of video.
7. **QA before handing over:** pull a frame at every hero word/overlay
   (`ffmpeg -ss T -i final.mp4 -frames:v 1 f.png`), tile them, look: text centred and uncropped,
   not over the face, nothing lingering past its line, cuts clean. Check loudness
   (`ffmpeg -i final.mp4 -af ebur128 -f null -`, I ≈ -14). Fix plan.json and re-compose; only re-run
   `base` if cuts/grade changed.
8. Deliver `final.mp4` to the user (SendUserFile) with a two-line summary of what was cut and which
   moments got graphics; offer to swap hero words, colours or overlays.

## plan.json reference

```jsonc
{"captions": [
  {"start": 0.0, "end": 0.95, "y": 0.40,            // seconds on the edited timeline; y = fraction of height (centre)
   "lines": [ {"style": "lead",      "words": [["It's", 0.0], ["no", 0.18]]},
              {"style": "pop-cyan",  "words": [["secret,", 0.3]]} ]}],   // each word appears at its own time
 "overlays": [ ... ]}
```
Caption styles: `lead` (thin small white), `word` (medium white, default single-line captions),
`hook` (giant thin white), `white-heavy`, `pop-purple`, `pop-cyan`, `pop-silver` (gradient heavy),
`neon-yellow` (glowing). Text may be edited freely (e.g. "2 weeks" -> "2 WEEKS", merge two words into
one hero) - timings come from words.json.

Overlay types (all times in seconds):
| type | fields | use for |
|---|---|---|
| `counter` | start, end, from, to, suffix, lead, y, count_for | any number claim - counts up |
| `cards` | start, end, images[], w, h, stagger, spots[[x,y,rot]] | listings, posts, before/after - pop in around the speaker and drift |
| `pills` | start, end, y, items[{text, at, x, y}] | lists ("pricing / presentation") - one per item as spoken |
| `call` | start, end, y, name, sub | "clients call/reach out" |
| `broll` | start, end, src (img/video), media_start | full-screen cutaway: proof, property, screenshot |
| `streak` | start, end, y | neon light swoosh behind a "deliver/results" line |
| `punch` | at, scale, dur | zoom-blur whip into a new section |
| `flash` | at, strength | white flash on a big beat or cut |

Image/video paths in overlays are relative to plan.json (or absolute); they're copied into the project.

## Rules of thumb
- Target 30-45s; if the raw talk runs long, cut whole sentences, never speed up the voice.
- Never leave a caption on screen during a pause > 0.6s; never stack more than 2 caption lines + 1 overlay.
- One hero word per sentence; colours rotate purple -> cyan -> yellow so neighbours never match.
- Keep the bottom 18% and right 12% clear of anything important (Instagram UI covers it).
- Selfie footage often has the face high in frame: lower `focus_y` (0.2-0.3) rather than cropping heads.
- If footage is HDR (iPhone HLG) `base` tone-maps it; if colours still look flat, try `grade: clean` and compare.
- Text behind the subject (as in the reference's "So,") needs a person matte - not built in; skip it
  unless the user asks, then use a segmentation model (e.g. `pip install rembg`) to cut a foreground layer.
