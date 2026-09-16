# CANYON & COLLAR

**Luxury stays. Grounded in nature.**

The complete cinematic asset package for a scroll-driven luxury pet concierge
experience — a visitor scrolls through an entire stay at a private desert
retreat, from arrival to reunion, at their dog's eye level.

---

## What is in here

| | |
|---|---|
| `brand/` | Style bible, continuity bible, and the generated shot list |
| `prompts/` | One generation brief per scene — image prompt, video prompt, negative prompt, camera, motion, transition, audio |
| `assets/video/canyon_collar_film.mp4` | The film the site plays |
| `assets/manifest.json` | The single file the website reads |
| `site/` | The scroll experience, wired to the manifest |
| `tools/` | The generator — one source of truth for all of the above |

## How the site plays

`assets/video/canyon_collar_film.mp4` runs as one continuous film behind the
entire scroll. The chapters supply the timing and the typography over it: each
owns a slice of the page scroll, and its copy dissolves in and out as that
slice passes.

The film is played and looped rather than scrubbed. The supplied encode carries
a single keyframe, so seeking it frame by frame would stutter on every scroll
tick — looping keeps it smooth and keeps the atmosphere moving while the
viewer reads.

It has an audio track, so the page offers sound rather than forcing it: the
film starts muted (browsers require that to autoplay) and a control in the
corner lets the viewer turn it on.

Two copies of the film are kept. `canyon_collar_film.mp4` is the master as
delivered — 1280×720, 10.06s, 24fps, H.264 + AAC, with its metadata after the
media, so a browser has to fetch all 10.8MB before the first frame appears.
`canyon_collar_film_web.mp4` is what the site loads: same picture, fast-start,
a keyframe every two seconds, 2.9MB, with `canyon_collar_poster.jpg` as the
first paint.

The footage is a single continuous arrival shot — the dog coming down out of
the truck into golden-hour canyon light, the leash going on, the walk away. It
covers chapter 01. The remaining chapters still need their own footage; their
briefs are in `prompts/`.

## Shooting the rest

`prompts/` holds a generation brief per scene — copy-paste ready for a
photoreal image or video model, each carrying the locked continuity block so
the property, the dog, the wardrobe and the props do not drift between scenes.

`brand/SHOT_LIST.md` lists every scene with its lens, format, duration, camera
move and the typography space it has to keep clear.

## The journey

| Scroll | Scene |
|---|---|
| 0–8% | 01 Arrival — the property reveals itself |
| 8–15% | 02 The welcome — a concierge kneels to greet |
| 15–22% | 03 Leash handoff — the macro transition into the interior |
| 22–32% | 04 The suite — not a kennel, a room |
| 32–37% | 05 Personal belongings — this stay belongs to this dog |
| 37–47% | 06 Nature walk — grounded in nature |
| 47–54% | 07 Off-leash exploration — spacious, calm, supervised |
| 54–58% | 08 Water — attentiveness, in macro |
| 58–64% | 09 Personalised meal — your routine, our priority |
| 64–70% | 10 Concierge care — care that feels personal |
| 70–75% | 11 Owner update — peace of mind, even when you're away |
| 75–80% | 12 Afternoon rest — rest is part of the experience |
| 80–87% | 13 Golden hour — the hero frame |
| 87–91% | 14 Evening retreat — the property turns over into night |
| 91–94% | 15 Bedtime — the last check of the night |
| 94–96.5% | 16 Morning — a new day |
| 96.5–98.5% | 17 Reunion — welcome home |
| 98.5–100% | 18 Final hero — wordmark, tagline, booking |
| interstitial | 19 Signature collar macro — reusable transition |

Emotional progression: uncertainty → trust → discovery → joy → care → rest →
peace of mind → reunion.

## Running the site

```bash
npx http-server . -p 8080     # serve from the repo root, not from site/
# then open http://localhost:8080/site/
```

It must be served over HTTP — the page fetches `assets/manifest.json`, which a
`file://` origin will block.

## Changing the film

Replace `assets/video/canyon_collar_film.mp4`, or point `film.src` in
`assets/manifest.json` somewhere else. `film.hasAudio` controls whether the
sound toggle appears at all.

Delivery targets for further footage: H.264 MP4 (plus WebM for breadth),
1920×1080 or 2.39:1 at 1920×804, 24fps, and a keyframe every second or two if
you ever want scroll-scrubbed playback instead of looping.

## Regenerating

```bash
python3 tools/build.py    # prompts, shot list, manifest
```

`tools/asset_spec.py` is the single source of truth — scene text, palette,
lighting states, continuity block, negative prompt, scroll ranges and camera
moves. Change it there and everything downstream follows.

## Naming

Scenes delivered as both a still and a motion asset use the `_image` / `_video`
suffix; motion-only scenes use the bare name, and their poster frame takes a
`_poster` suffix.

```
01_canyon_collar_arrival_image     01_canyon_collar_arrival_video
02_concierge_welcome               03_leash_handoff
04_private_suite_image             04_private_suite_video
05_personal_belongings             06_nature_walk_image / _video
07_outdoor_exploration             08_fresh_water
09_personalized_meal               10_concierge_care
11_owner_update                    12_afternoon_rest
13_golden_hour_image / _video      14_evening_retreat
15_bedtime                         16_morning
17_reunion                         18_final_hero_image / _video
19_signature_collar_macro
```
