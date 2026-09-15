# Generation briefs

One file per scene. Each contains:

- **Intent** — what the shot is actually doing in the story
- **Overlay typography** — composited by the website, never rendered into the asset
- **Camera / Motion / Transition** — how it is shot and how it hands off
- **Audio bed** — natural atmosphere and where the score sits
- **IMAGE PROMPT** — a single paragraph, copy-paste ready
- **VIDEO PROMPT** — the same scene with the camera move written in
- **NEGATIVE PROMPT** — identical across all scenes, by design

## How to use them

1. Generate the **still** first. It is the frame the shot has to earn, and it is
   also the poster frame the website shows before video loads.
2. Approve the still against `../brand/CONTINUITY_BIBLE.md` before generating
   motion. A wrong wall, a wrong collar or a second dog is cheaper to catch here.
3. Generate the **video** from the approved still where your tool supports
   image-to-video — it is the most reliable way to hold continuity.
4. Check the reserved negative space against `../assets/guides/`. If type would
   land on a branch, a highlight or a horizon, reframe rather than move the type.

## Continuity

Every prompt already contains the locked continuity block. Do not trim it to
save tokens — it is the only thing keeping 19 scenes on one property.

If a model drifts (different building, different dog, wardrobe change), re-roll
with the continuity block moved to the *front* of the prompt before the scene
description.

## Order of work

The film is a chain of hand-offs, not a set of independent clips. Generate in
scene order and check each shot against the one before it: 03 has to end on the
brass bloom that 04 opens with, 15 has to end on the strip of corridor light
that 16 match-cuts from.
