#!/usr/bin/env python3
"""Build the Canyon & Collar asset package from tools/asset_spec.py.

    python3 tools/build.py

Regenerates:
    prompts/*.md          one generation brief per named asset
    assets/proxy/*.svg    one procedural proxy plate per asset
    assets/manifest.json  what the website reads
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import proxy
from asset_spec import (ASSETS, BRAND, CONTINUITY, LIGHT, MOVES, NEGATIVE, PALETTE,
                        TECH_IMAGE, TECH_VIDEO, filebase, poster_base)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def wrap(text, width=94, indent=""):
    out, line = [], indent
    for word in text.split():
        if len(line) + len(word) + 1 > width and line.strip():
            out.append(line.rstrip())
            line = indent + word + " "
        else:
            line += word + " "
    if line.strip():
        out.append(line.rstrip())
    return "\n".join(out)


def one_line(*parts):
    return " ".join(" ".join(p.split()) for p in parts if p)


def image_prompt(a, light):
    return one_line(
        f"{a['subject']}", a["scene"],
        a["camera"],
        light["prompt"] + ".",
        f"Framed {a['ratio']} with clean unobstructed negative space in the {a['negative_space']}.",
        "Colour palette strictly sandstone, warm beige, desert clay, sage green, deep olive, aged "
        "leather brown, cream, muted rust, charcoal, soft black and sunset amber.",
        CONTINUITY, TECH_IMAGE + ".",
    )


def video_prompt(a, light):
    return one_line(
        f"{a['duration']} cinematic shot.", a["subject"], a["scene"],
        a["camera"],
        "CAMERA MOVE: " + a["motion"],
        light["prompt"] + ".",
        f"Framed {a['ratio']} with clean unobstructed negative space in the {a['negative_space']}.",
        CONTINUITY, TECH_VIDEO + ".",
    )


def write_prompt_file(a):
    light = LIGHT[a["light"]]
    names = [filebase(a, k) for k in a["outputs"]]
    scroll = (f"{a['scroll'][0] * 100:.1f}% → {a['scroll'][1] * 100:.1f}%"
              if a["scroll"] else "floating interstitial — not bound to a scroll range")
    overlay = "\n".join(f"> **{line}**" for line in a["overlay"]) or "_none — pure image_"

    md = f"""# {a['id']} — {a['title']}

**Chapter:** {a['chapter']}  ·  **Scroll position:** {scroll}
**Deliverables:** {', '.join(f'`{n}`' for n in names)}
**Format:** {a['ratio']}  ·  **Lens:** {a['lens']}  ·  **Duration:** {a['duration']}  ·  **Light:** {light['label']}
**Reserved negative space:** {a['negative_space']}

## Intent

{wrap(a['scene'])}

## Overlay typography (composited by the website — do not render into the asset)

{overlay}

## Camera

{wrap(a['camera'])}

## Motion

{wrap(a['motion'])}

## Transition

{wrap(a['transition'])}

## Audio bed

{wrap(a['audio'])}

---

## IMAGE PROMPT — `{poster_base(a)}`

```text
{wrap(image_prompt(a, light))}
```

## VIDEO PROMPT — `{filebase(a, 'video') if 'video' in a['outputs'] else filebase(a, 'image')}`

```text
{wrap(video_prompt(a, light))}
```

## NEGATIVE PROMPT (both)

```text
{wrap(NEGATIVE)}
```
"""
    path = os.path.join(ROOT, "prompts", f"{a['id']}_{a['slug']}.md")
    with open(path, "w") as f:
        f.write(md)
    return path


def write_shot_list():
    rows = []
    for a in ASSETS:
        names = " · ".join(f"`{filebase(a, k)}`" for k in a["outputs"])
        scroll = f"{a['scroll'][0] * 100:.0f}–{a['scroll'][1] * 100:.0f}%" if a["scroll"] else "interstitial"
        move = MOVES[a["id"]]
        rows.append(f"| {a['id']} | {a['title']} | {a['chapter']} | {scroll} | {a['lens']} | "
                    f"{a['ratio']} | {a['duration']} | {move['note']} | {names} |")

    overlays = []
    for a in ASSETS:
        if a["overlay"]:
            overlays.append(f"| {a['id']} | {' / '.join(a['overlay'])} | {a['negative_space']} |")

    md = f"""# Canyon & Collar — Shot List

_Generated from `tools/asset_spec.py` by `tools/build.py`. Do not hand-edit._

{len(ASSETS)} scenes · {sum(len(a['outputs']) for a in ASSETS)} named deliverables ·
{sum(MOVES[a['id']]['dur'] for a in ASSETS):.0f} seconds of motion.

| # | Scene | Chapter | Scroll | Lens | Format | Duration | Camera move | Deliverables |
|---|-------|---------|--------|------|--------|----------|-------------|--------------|
{chr(10).join(rows)}

## Scroll journey

The website maps each scene to a slice of the page scroll. Chapter 19 is an
interstitial — it is not on the scroll spine and can be cut in anywhere.

| Scroll | Chapter |
|--------|---------|
{chr(10).join(f"| {a['scroll'][0] * 100:.0f}–{a['scroll'][1] * 100:.0f}% | {a['chapter']} — {a['title']} |" for a in ASSETS if a['scroll'])}

## Overlay typography and the space reserved for it

Text is composited by the website. Nothing below is rendered into an asset.

| # | Overlay | Reserved area |
|---|---------|---------------|
{chr(10).join(overlays)}
"""
    with open(os.path.join(ROOT, "brand", "SHOT_LIST.md"), "w") as f:
        f.write(md)


def main():
    for d in ("proxy", "guides", "still", "video"):
        os.makedirs(os.path.join(ROOT, "assets", d), exist_ok=True)
    manifest = {
        "brand": BRAND,
        "palette": PALETTE,
        "note": "Proxy plates are placeholders. Replace poster/video paths with the final "
                "renders; nothing else in the site needs to change.",
        "chapters": [],
    }

    for a in ASSETS:
        write_prompt_file(a)
        pb = poster_base(a)
        light = LIGHT[a["light"]]
        proxy.render(a, light, os.path.join(ROOT, "assets", "proxy", f"{pb}.svg"),
                     show_guides=False)
        proxy.render(a, light, os.path.join(ROOT, "assets", "guides", f"{pb}_guides.svg"),
                     show_guides=True)
        vb = filebase(a, "video") if "video" in a["outputs"] else None
        manifest["chapters"].append({
            "id": a["id"],
            "slug": a["slug"],
            "title": a["title"],
            "chapter": a["chapter"],
            "scroll": list(a["scroll"]) if a["scroll"] else None,
            "duration": a["duration"],
            "lens": a["lens"],
            "ratio": a["ratio"],
            "light": a["light"],
            "overlay": a["overlay"],
            "negativeSpace": a["negative_space"],
            "move": MOVES[a["id"]],
            "vector": f"assets/proxy/{pb}.svg",
            "guides": f"assets/guides/{pb}_guides.svg",
            "poster": f"assets/still/{pb}.jpg",
            "posterIsProxy": True,
            "video": f"assets/video/{vb}.webm" if vb else None,
            "videoIsProxy": True,
            "finalVideo": f"assets/video/{vb}.mp4" if vb else None,
        })

    with open(os.path.join(ROOT, "assets", "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    write_shot_list()

    named = sum(len(a["outputs"]) for a in ASSETS)
    print(f"{len(ASSETS)} scenes · {named} named deliverables · "
          f"{len(ASSETS)} prompt briefs · {len(ASSETS)} proxy plates")


if __name__ == "__main__":
    main()
