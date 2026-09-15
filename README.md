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
| `assets/proxy/` | Vector proxy plates, one per scene |
| `assets/guides/` | The same plates with reserved typography space marked, for art direction |
| `assets/still/` | Rendered proxy stills (JPEG, 2.39:1) |
| `assets/video/` | Rendered proxy motion (WebM, 24fps, with the specified camera move) |
| `assets/manifest.json` | The single file the website reads |
| `site/` | The scroll experience, wired to the manifest |
| `tools/` | The generator — one source of truth for all of the above |

## Read this first

**The files in `assets/still/` and `assets/video/` are proxies, not the final
assets.** They are procedurally generated stand-ins: correct aspect ratio,
correct palette, correct composition blocking, correct reserved negative space,
correct camera move, correct duration, correct cut points. They exist so the
scroll experience can be built, timed, reviewed and signed off before a single
frame of real footage is shot or generated.

The real assets are produced from `prompts/`. Every brief is copy-paste ready
for a photoreal image or video model, and each one carries the locked
continuity block so the property, the dog, the wardrobe and the props do not
drift between scenes.

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

## Swapping proxies for final footage

1. Drop the final files into `assets/still/` and `assets/video/` using the names
   in `brand/SHOT_LIST.md`.
2. In `assets/manifest.json`, point `poster` and `video` at them and set
   `posterIsProxy` / `videoIsProxy` to `false`.

Nothing in `site/` needs to change. The scroll ranges, overlay copy, chapter
rail and cross-dissolves are all driven by the manifest.

Final delivery targets, for when the real renders land: H.264 MP4 and WebM,
2.39:1 at 3840×1608 mastered, 1920×804 for the web, 24fps, no audio on the
scroll loops (the page is silent by default), plus JPEG poster frames at
2390×1000.

## Regenerating

```bash
python3 tools/build.py                        # prompts, plates, shot list, manifest
NODE_PATH=$(npm root -g) node tools/render.js  # stills and proxy motion
NODE_PATH=$(npm root -g) node tools/render.js --stills --only 13
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
