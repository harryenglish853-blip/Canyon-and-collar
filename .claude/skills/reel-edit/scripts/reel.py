#!/usr/bin/env python3
"""reel.py - raw talking-head clips -> finished vertical reel.

  transcribe  CLIP...                 word timestamps via Groq Whisper (cached next to each clip as <clip>.words.json)
  plan        CLIP... -o edl.json     cut plan: phrases kept, silences/fillers/retakes dropped, punch-in zooms
  base        edl.json -o work/       cut + reframe 1080x1920 + grade + loudness -> work/base.mp4 + work/words.json
  captions    work/ [-o plan.json]    first-draft caption/overlay plan from work/words.json (edit it after!)
  compose     work/ plan.json         writes work/hf/ (HyperFrames project) ready to render
  render      work/ [-o final.mp4]    renders work/hf with HyperFrames, then encodes the IG/FB Reels delivery file
  deliver     master.mp4 -o final.mp4 re-encode any file to the Reels delivery spec (1080x1920 H.264 High, AAC 48k)
  matte       work/ START END         person cut-out (alpha WebM) of base.mp4 for text-behind-subject

Typical:  plan -> (review edl) -> base -> captions -> (art-direct plan) -> compose -> render
Looks:    --look kinetic (word-pop captions, glow grade)  |  --look cinematic (serif subtitles, big condensed titles, film grade)
"""
import argparse, json, math, os, re, shutil, subprocess, sys, html
from pathlib import Path

W, H, FPS = 1080, 1920, 30   # Reels canvas: 1080x1920 is the platforms' maximum - never upscale past the source
HERE = Path(__file__).resolve().parent
FILLERS = {"um", "uh", "uhm", "umm", "erm", "er", "ah", "hmm", "mm"}
STOP = set("a an the and or but so to of in on at for with is are was were be i i'm i've you your my me we our it it's that this those these they them their there here as by from up out just really very".split())


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"command failed: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r.stdout


def probe(path):
    return json.loads(sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]))


def duration(path):
    return float(probe(path)["format"]["duration"])


# ---------------------------------------------------------------- transcribe
def transcribe(clip):
    clip = Path(clip)
    cache = clip.with_name(clip.name + ".words.json")
    if cache.exists():
        return json.loads(cache.read_text())
    tmp = cache.with_suffix(".mp3")
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", str(tmp)])
    from groq import Groq  # proxy injects the key in this environment; GROQ_API_KEY elsewhere
    c = Groq(api_key=os.environ.get("GROQ_API_KEY", "proxy-injected"))
    with open(tmp, "rb") as f:
        r = c.audio.transcriptions.create(file=f, model="whisper-large-v3", response_format="verbose_json",
                                          timestamp_granularities=["word", "segment"], language="en",
                                          prompt="Um, uh, so, like. Keep filler words.")
    d = r.model_dump() if hasattr(r, "model_dump") else dict(r)
    words = [{"w": x["word"].strip(), "s": round(x["start"], 3), "e": round(x["end"], 3)} for x in d.get("words", [])]
    tmp.unlink(missing_ok=True)
    cache.write_text(json.dumps({"text": d["text"].strip(), "words": words}, indent=1))
    return json.loads(cache.read_text())


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


# ---------------------------------------------------------------- plan
def display_size(path):
    st = next(x for x in probe(path)["streams"] if x["codec_type"] == "video")
    w, h = st["width"], st["height"]
    rot = 0
    for sd in st.get("side_data_list", []):
        rot = int(sd.get("rotation", 0) or 0)
    rot = rot or int(st.get("tags", {}).get("rotate", 0))
    if abs(rot) % 180 == 90: w, h = h, w
    fr = st.get("avg_frame_rate", "30/1").split("/")
    return w, h, (float(fr[0]) / float(fr[1]) if len(fr) == 2 and float(fr[1]) else 30.0)


def res_report(path, zoom=1.0):
    """How many source pixels feed each output pixel after the 9:16 crop (+ zoom). <1 means upscaling = soft."""
    w, h, _ = display_size(path)
    scale = max(W / w, H / h) * zoom
    return w, h, scale


def plan(clips, out, gap=0.45, pad_in=0.08, pad_out=0.14, look="kinetic", broll=()):
    segs, cl = [], []
    for i, p in enumerate(clips):
        p = Path(p).resolve()
        cid = f"c{i+1}"
        dur = duration(p)
        w, h, fps = display_size(p)
        cl.append({"id": cid, "path": str(p), "duration": round(dur, 3), "size": f"{w}x{h}", "fps": round(fps, 2)})
        _, _, sc = res_report(p)
        if sc > 1.0:
            print(f"WARNING {p.name}: {w}x{h} must be upscaled {sc:.2f}x to fill 1080x1920 - it WILL look soft. "
                  f"Ask the user for the original camera file (4K/1080p, not a screen recording or a messaging-app copy).")
        words = [w for w in transcribe(p)["words"] if norm(w["w"]) not in FILLERS]
        cur = []
        for w in words:
            if cur and (w["s"] - cur[-1]["e"] > gap or (re.search(r"[.!?]$", cur[-1]["w"]) and w["s"] - cur[-1]["e"] > 0.2)):
                segs.append((cid, dur, cur)); cur = []
            cur.append(w)
        if cur:
            segs.append((cid, dur, cur))
    out_segs = []
    for k, (cid, dur, ws) in enumerate(segs):
        prev_end = segs[k - 1][2][-1]["e"] if k and segs[k - 1][0] == cid else 0
        nxt = segs[k + 1][2][0]["s"] if k + 1 < len(segs) and segs[k + 1][0] == cid else dur
        a = max(ws[0]["s"] - pad_in, (prev_end + ws[0]["s"]) / 2, 0)
        b = min(ws[-1]["e"] + pad_out, (ws[-1]["e"] + nxt) / 2, dur)
        out_segs.append({"clip": cid, "in": round(a, 3), "out": round(b, 3),
                         "text": " ".join(w["w"] for w in ws), "keep": True})
    # retakes: a phrase whose opening (3 words) is repeated by a later phrase -> keep the later take
    for i, s in enumerate(out_segs):
        head = [norm(x) for x in s["text"].split()[:3]]
        for t in out_segs[i + 1:i + 4]:
            if len(head) >= 2 and [norm(x) for x in t["text"].split()[:len(head)]] == head:
                s["keep"] = False; s["why"] = "retake - a later take repeats this opening"
                break
    # framing rhythm: wide / punch-in alternate per phrase, like the reference
    z = [1.0, 1.14, 1.0, 1.08] if look == "kinetic" else [1.0, 1.06]
    for i, s in enumerate([s for s in out_segs if s["keep"]]):
        s["zoom"] = z[i % len(z)]
    for s in out_segs:
        s.setdefault("zoom", 1.0); s["focus_y"] = 0.38
        cp = next(c["path"] for c in cl if c["id"] == s["clip"])
        if res_report(cp, s["zoom"])[2] > 1.0 and s["zoom"] > 1.0:
            s["zoom"] = 1.0  # no punch-in on footage that is already short of pixels
    bl = []
    for j, b in enumerate(broll):
        b = Path(b).resolve(); w, h, fps = display_size(b)
        if res_report(b)[2] > 1.0:
            print(f"WARNING b-roll {b.name}: {w}x{h} is below 1080x1920 - will be soft.")
        bl.append({"path": str(b), "size": f"{w}x{h}", "in": 0.0, "dur": round(min(duration(b), 2.0), 3), "at": None,
                   "zoom": 1.0, "focus_y": 0.5, "sfx": 0.0})
    edl = {"look": look, "clips": cl, "grade": "warm-glow" if look == "kinetic" else "cine-natural", "fps": 30,
           "loudness": -14, "segments": out_segs, "broll": bl}
    if bl:
        print(f"{len(bl)} b-roll clips listed - set each one's 'at' (seconds on the EDITED timeline), 'in' and 'dur'.")
    Path(out).write_text(json.dumps(edl, indent=1))
    kept = [s for s in out_segs if s["keep"]]
    print(f"{len(kept)}/{len(out_segs)} phrases kept, {sum(s['out']-s['in'] for s in kept):.1f}s -> {out}")


# ---------------------------------------------------------------- base
GRADES = {
    # warm, saturated greens, lifted mids, soft bloom, gentle vignette (the reference look)
    "warm-glow": ("eq=contrast=1.07:saturation=1.22:brightness=0.015:gamma=1.03,"
                  "colorbalance=rm=0.035:bm=-0.03:rh=0.02:bh=-0.035,"
                  "split[a][b];[b]gblur=sigma=22[g];[a][g]blend=all_mode=screen:all_opacity=0.12,"
                  "vignette=angle=PI/5"),
    # natural film look: gentle S-curve, warm highlights / cool shadows, no bloom (keeps it crisp)
    "cine-natural": ("curves=all='0/0.02 0.25/0.22 0.5/0.5 0.75/0.79 1/0.98',"
                     "colorbalance=rs=-0.03:bs=0.035:rh=0.04:gh=0.01:bh=-0.035,eq=saturation=1.08"),
    "clean": "eq=contrast=1.04:saturation=1.1",
    "none": "null",
}


def is_hdr(st):
    return st.get("color_transfer") in ("arib-std-b67", "smpte2084")


SHARPEN = "unsharp=5:5:0.45:5:5:0"   # restores detail lost to the downscale + platform re-encode; light enough to stay natural


def part(src, a, b, zoom, fy, grade, out, fps, audio=True):
    vs = next(x for x in probe(src)["streams"] if x["codec_type"] == "video")
    tm = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
          "zscale=t=bt709:m=bt709:r=tv,format=yuv420p," if is_hdr(vs) else "")
    zw, zh = int(W * zoom) // 2 * 2, int(H * zoom) // 2 * 2
    # one high-quality resample straight from the camera pixels (lanczos), then crop - never scale twice
    vf = (f"[0:v]{tm}scale={zw}:{zh}:force_original_aspect_ratio=increase:flags=lanczos+accurate_rnd+full_chroma_int,"
          f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*{fy},fps={fps},setsar=1,{grade},{SHARPEN},format=yuv420p[v]")
    d = b - a
    has_a = audio and any(x["codec_type"] == "audio" for x in probe(src)["streams"])
    fc = vf + (f";[0:a]aresample=48000,afade=t=in:d=0.012,afade=t=out:st={max(d-0.02,0):.3f}:d=0.02[a]" if has_a else "")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", src, "-filter_complex", fc, "-map", "[v]"]
    cmd += (["-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000"] if has_a else ["-an"])
    sh(cmd + ["-c:v", "libx264", "-crf", "10", "-preset", "slow", "-tune", "film", "-pix_fmt", "yuv420p",
              "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(out)])
    return duration(out)


def base(edl_path, work):
    edl = json.loads(Path(edl_path).read_text())
    work = Path(work); (work / "parts").mkdir(parents=True, exist_ok=True)
    clips = {c["id"]: c for c in edl["clips"]}
    words_by = {cid: transcribe(c["path"])["words"] for cid, c in clips.items()}
    grade = GRADES.get(edl.get("grade", "warm-glow"), edl.get("grade"))
    fps = edl.get("fps", FPS)
    parts, out_words, t = [], [], 0.0
    for i, s in enumerate([s for s in edl["segments"] if s.get("keep", True)]):
        c = clips[s["clip"]]
        p = work / "parts" / f"{i:03d}.mov"
        real = part(c["path"], s["in"], s["out"], s.get("zoom", 1.0), s.get("focus_y", 0.38), grade, p, fps)
        for w in words_by[s["clip"]]:
            if s["in"] - 0.02 <= w["s"] < s["out"] - 0.03 and norm(w["w"]) not in FILLERS:
                out_words.append({"w": w["w"], "s": round(t + max(w["s"] - s["in"], 0), 3),
                                  "e": round(t + min(w["e"], s["out"]) - s["in"], 3), "seg": i})
        parts.append(p); t += real
    lst = work / "parts" / "list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    aroll = work / "parts" / "aroll.mov"
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", aroll])
    # b-roll: replaces the picture over [at, at+dur] while the voice keeps running (optionally mixes its own sound)
    br = [b for b in edl.get("broll", []) if b.get("at") is not None]
    inputs, fc, vlast, sfx = ["-i", str(aroll)], [], "0:v", []
    for j, b in enumerate(br):
        bp = work / "parts" / f"broll{j:02d}.mov"
        part(b["path"], b.get("in", 0), b.get("in", 0) + b["dur"], b.get("zoom", 1.0), b.get("focus_y", 0.5), grade, bp, fps,
             audio=b.get("sfx", 0) > 0)
        inputs += ["-i", str(bp)]; k = j + 1
        fc.append(f"[{k}:v]setpts=PTS-STARTPTS+{b['at']}/TB[b{k}];[{vlast}][b{k}]overlay=enable='between(t,{b['at']},{b['at']+b['dur']-0.001})':eof_action=pass[o{k}]")
        vlast = f"o{k}"
        if b.get("sfx", 0) > 0 and any(x["codec_type"] == "audio" for x in probe(bp)["streams"]):
            ms = int(b["at"] * 1000)
            fc.append(f"[{k}:a]volume={b['sfx']},adelay={ms}|{ms}[s{k}]"); sfx.append(f"[s{k}]")
    voice = "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2"
    if sfx:
        fc.append(f"[0:a]{voice}[vo];[vo]{''.join(sfx)}amix=inputs={len(sfx)+1}:normalize=0:duration=first[mx]")
        amap, aflt = "[mx]", []
    else:
        amap, aflt = "0:a", ["-af", voice + ","]
    loud = f"loudnorm=I={edl.get('loudness',-14)}:TP=-1.0:LRA=7"
    if aflt: aflt[1] += loud
    else:
        fc.append(f"[mx]{loud}[mxl]"); amap = "[mxl]"
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs]
    if fc: cmd += ["-filter_complex", ";".join(fc), "-map", f"[{vlast}]" if br else "0:v", "-map", amap]
    else: cmd += ["-map", "0:v", "-map", "0:a"]
    cmd += aflt + ["-c:v", "libx264", "-crf", "10", "-preset", "slow", "-tune", "film", "-pix_fmt", "yuv420p",
                   "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                   "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(work / "base.mp4")]
    sh(cmd)
    (work / "words.json").write_text(json.dumps(out_words, indent=1))
    (work / "look.txt").write_text(edl.get("look", "kinetic"))
    print(f"base.mp4 {duration(work/'base.mp4'):.2f}s, {len(parts)} cuts, {len(br)} b-roll inserts, {len(out_words)} words -> {work}")


# ---------------------------------------------------------------- captions (draft plan)
POPS = ["pop-purple", "pop-cyan", "neon-yellow", "pop-purple", "pop-cyan"]


def captions_cinematic(words, out):
    """Phrase subtitles: small yellow serif, 2-6 words, whole phrase at once, lower-middle. Titles are added by hand."""
    caps, cur = [], []
    def flush():
        if cur:
            caps.append({"start": cur[0]["s"], "end": cur[-1]["e"], "y": 0.66,
                         "lines": [{"style": "serif", "words": [[" ".join(x["w"] for x in cur), cur[0]["s"]]]}]})
        cur.clear()
    for i, w in enumerate(words):
        if cur and (w["s"] - cur[-1]["e"] > 0.35 or len(cur) >= 6): flush()
        cur.append(w)
        if re.search(r"[,;:.!?]$", w["w"]) and len(cur) >= 2: flush()
    flush()
    for a, b in zip(caps, caps[1:]):
        a["end"] = round(min(b["start"], a["end"] + 0.4), 3)
    caps[-1]["end"] = round(caps[-1]["end"] + 0.5, 3)
    Path(out).write_text(json.dumps({"look": "cinematic", "captions": caps, "overlays": []}, indent=1))
    print(f"{len(caps)} subtitle phrases -> {out}  (now add titles/b-roll beats: see SKILL.md, cinematic look)")


def captions(work, out, look=None):
    work = Path(work); words = json.loads((work / "words.json").read_text())
    look = look or ((work / "look.txt").read_text().strip() if (work / "look.txt").exists() else "kinetic")
    if look == "cinematic":
        return captions_cinematic(words, out)
    # sentences
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.!?]$", w["w"]):
            sents.append(cur); cur = []
    if cur: sents.append(cur)
    caps, pop_i = [], 0
    for si, sent in enumerate(sents):
        # hero word: a number, else the strongest content word among the sentence's last 4
        nums = [w for w in sent if re.search(r"\d", w["w"])]
        cands = [w for w in sent[-4:] if norm(w["w"]) not in STOP]
        hero = nums[-1] if nums else (max(cands, key=lambda w: len(norm(w["w"]))) if cands else None)
        # chunks of <=3 words, break on , ; : or hero word
        chunk = []
        def flush():
            nonlocal chunk, pop_i
            if not chunk: return
            lines, lead = [], [w for w in chunk if w is not hero]
            big = hero if hero in chunk else None
            if big:
                pre = [w for w in chunk if w["s"] < big["s"]]
                post = [w for w in chunk if w["s"] > big["s"]]
                if pre: lines.append({"style": "lead", "words": pre})
                lines.append({"style": POPS[pop_i % len(POPS)], "words": [big]}); pop_i += 1
                if post: lines.append({"style": "lead", "words": post})
            else:
                lines.append({"style": "word", "words": lead})
            caps.append({"start": chunk[0]["s"], "end": chunk[-1]["e"], "y": 0.30 if (si == 0 and big) else 0.47,
                         "lines": [{"style": l["style"], "words": [[x["w"], x["s"]] for x in l["words"]]} for l in lines]})
            chunk = []
        for w in sent:
            if w is hero and chunk:
                if len(chunk) > 2: flush()
            chunk.append(w)
            if w is hero or len(chunk) >= 3 or re.search(r"[,;:.!?]$", w["w"]):
                flush()
        flush()
    # hold each caption until the next one starts (no flicker), but not across long pauses
    for a, b in zip(caps, caps[1:]):
        a["end"] = round(min(b["start"], a["end"] + 0.6), 3)
    caps[-1]["end"] = round(caps[-1]["end"] + 0.5, 3)
    plan = {"font": "Inter", "captions": caps, "overlays": [], "end_flash": True}
    txt = re.sub(r'\[\s*("(?:[^"\\]|\\.)*"),\s*([\d.]+)\s*\]', r'[\1, \2]', json.dumps(plan, indent=1))
    Path(out).write_text(txt)
    print(f"{len(caps)} caption beats -> {out}  (now art-direct it: hero words, overlays, b-roll)")


# ---------------------------------------------------------------- compose
CSS = r"""
@font-face{font-family:IR;src:url(fonts/inter-300.woff2);font-weight:300}
@font-face{font-family:IR;src:url(fonts/inter-500.woff2);font-weight:500}
@font-face{font-family:IR;src:url(fonts/inter-800.woff2);font-weight:800}
@font-face{font-family:IR;src:url(fonts/inter-900.woff2);font-weight:900}
@font-face{font-family:AN;src:url(fonts/anton-400.woff2)}
@font-face{font-family:IS;src:url(fonts/iserif-400.woff2)}
@font-face{font-family:IS;src:url(fonts/iserif-400i.woff2);font-style:italic}
html,body{margin:0;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:IR,Inter,Helvetica,Arial,sans-serif}
#v{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 40%}
.layer{position:absolute;inset:0;pointer-events:none}
.cap{position:absolute;left:60px;right:60px;text-align:center;transform:translateY(-50%)}
.ln{display:block;line-height:1.02;white-space:nowrap}
.wd{display:inline-block;opacity:0;margin:0 .12em}
.lead{font-weight:300;font-size:66px;color:#fff;letter-spacing:-.02em;text-shadow:0 2px 14px rgba(0,0,0,.45)}
.word{font-weight:500;font-size:76px;color:#fff;letter-spacing:-.02em;text-shadow:0 2px 16px rgba(0,0,0,.5)}
.hook{font-weight:300;font-size:220px;color:#fff;letter-spacing:-.04em;text-shadow:0 6px 30px rgba(0,0,0,.35)}
.white-heavy{font-weight:900;font-size:150px;color:#fff;letter-spacing:-.04em;text-shadow:0 6px 26px rgba(0,0,0,.4)}
.pop-purple,.pop-cyan,.pop-silver{font-weight:900;font-size:150px;letter-spacing:-.045em;filter:drop-shadow(0 6px 18px rgba(0,0,0,.35))}
.pop-purple .wd,.pop-cyan .wd,.pop-silver .wd,.pop-silver>span{-webkit-background-clip:text;background-clip:text;color:transparent;padding:.06em .04em .1em}
.pop-purple .wd{background-image:linear-gradient(180deg,#e9b8ff 0%,#b05cff 45%,#7a2be0 100%)}
.pop-cyan .wd{background-image:linear-gradient(180deg,#d9fbff 0%,#5fe0ee 45%,#1aa7c4 100%)}
.pop-silver .wd,.pop-silver>span{background-image:linear-gradient(180deg,#ffffff 0%,#d6d9de 50%,#8e949c 100%)}
.neon-yellow{font-weight:900;font-size:140px;letter-spacing:-.03em;color:#fff36b;text-shadow:0 0 8px #ffe600,0 0 24px #ffc400,0 0 60px #ff9d00}
.pill{position:absolute;padding:20px 42px;border-radius:999px;background:rgba(20,20,20,.62);color:#fff;font-weight:500;font-size:46px;
 border:4px solid #ffd21a;box-shadow:0 0 18px #ffcc00,0 0 46px rgba(255,170,0,.7),inset 0 0 14px rgba(255,200,0,.35);opacity:0;white-space:nowrap}
.dot{position:absolute;width:44px;height:44px;border-radius:50%;border:4px solid #ffd21a;box-shadow:0 0 18px #ffcc00;opacity:0}
.card{position:absolute;border:7px solid #fff;border-radius:6px;box-shadow:0 18px 40px rgba(0,0,0,.45);object-fit:cover;opacity:0}
.call{position:absolute;left:150px;right:150px;height:150px;border-radius:40px;background:rgba(235,235,235,.82);display:flex;align-items:center;
 padding:0 36px;box-sizing:border-box;box-shadow:0 12px 40px rgba(0,0,0,.35);opacity:0}
.call b{font-weight:800;font-size:40px;color:#111;display:block}.call i{font-style:normal;font-weight:500;font-size:30px;color:#555}
.call .r,.call .g{width:84px;height:84px;border-radius:50%;margin-left:20px}.call .r{background:#ff3b30;margin-left:auto}.call .g{background:#34c759}
.broll{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0}
.counter{position:absolute;left:0;right:0;text-align:center;opacity:0}
.flash{position:absolute;inset:0;background:#fff;opacity:0;mix-blend-mode:screen}
.serif{font-family:IS,Georgia,serif;font-size:62px;color:#f6e05e;letter-spacing:-.005em;white-space:normal;
 text-shadow:0 2px 3px rgba(0,0,0,.55),0 0 18px rgba(0,0,0,.35)}
.title{position:absolute;left:0;right:0;text-align:center;font-family:AN,sans-serif;color:#f4e23c;text-transform:uppercase;
 line-height:.86;letter-spacing:-.005em;text-shadow:0 4px 24px rgba(0,0,0,.18);z-index:2}
.title .tl{display:block;opacity:0;white-space:nowrap}
.fg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:3}
.cap,.pill,.dot,.card,.call,.counter{z-index:4}.broll{z-index:1}.flash{z-index:6}
.tile{position:absolute;overflow:hidden;border-radius:10px;opacity:0;box-shadow:0 10px 30px rgba(0,0,0,.4);z-index:2}
.tile img,.tile video{width:100%;height:100%;object-fit:cover;display:block}
.tile span{position:absolute;left:14px;right:14px;top:12px;font-family:AN,sans-serif;font-size:46px;line-height:.9;color:#f4e23c;
 text-transform:uppercase;text-shadow:0 2px 10px rgba(0,0,0,.6)}
"""

ENTER = {
    "lead": ('{opacity:0,y:18,filter:"blur(8px)"}', '{opacity:1,y:0,filter:"blur(0px)",duration:.22,ease:"power3.out"}'),
    "serif": ('{opacity:0,y:8}', '{opacity:1,y:0,duration:.14,ease:"power2.out"}'),
    "word": ('{opacity:0,scale:.86,filter:"blur(8px)"}', '{opacity:1,scale:1,filter:"blur(0px)",duration:.18,ease:"power3.out"}'),
    "hook": ('{opacity:0,scale:1.25,filter:"blur(22px)"}', '{opacity:1,scale:1,filter:"blur(0px)",duration:.35,ease:"power3.out"}'),
    "pop": ('{opacity:0,scale:1.45,filter:"blur(18px)"}', '{opacity:1,scale:1,filter:"blur(0px)",duration:.3,ease:"back.out(1.4)"}'),
}


def fonts_into(dst):
    dst.mkdir(parents=True, exist_ok=True)
    cache = Path.home() / ".cache/reel-edit/package/files"
    if not cache.exists():
        cache.parent.parent.mkdir(parents=True, exist_ok=True)
        try:
            sh(["npm", "pack", "@fontsource/inter@5.1.0", "-s"], cwd=cache.parent.parent)
            sh(["tar", "xzf", "fontsource-inter-5.1.0.tgz"], cwd=cache.parent.parent)
        except SystemExit:
            print("warning: could not fetch Inter; falling back to system fonts"); return
    for wgt in (300, 500, 800, 900):
        shutil.copy(cache / f"inter-latin-{wgt}-normal.woff2", dst / f"inter-{wgt}.woff2")
    for pkg, files in (("anton", {"anton-latin-400-normal.woff2": "anton-400.woff2"}),
                       ("instrument-serif", {"instrument-serif-latin-400-normal.woff2": "iserif-400.woff2",
                                             "instrument-serif-latin-400-italic.woff2": "iserif-400i.woff2"})):
        src = font_pkg(pkg)
        for a, b in files.items():
            if src and (src / a).exists(): shutil.copy(src / a, dst / b)


def font_pkg(name, ver="5.1.0"):
    root = Path.home() / ".cache/reel-edit"; d = root / f"fontsource-{name}-{ver}/package/files"
    if not d.exists():
        root.mkdir(parents=True, exist_ok=True)
        try:
            sh(["npm", "pack", f"@fontsource/{name}@{ver}", "-s"], cwd=root)
            (root / f"fontsource-{name}-{ver}").mkdir(exist_ok=True)
            sh(["tar", "xzf", f"fontsource-{name}-{ver}.tgz", "-C", f"fontsource-{name}-{ver}"], cwd=root)
        except SystemExit:
            print(f"warning: could not fetch font {name}"); return None
    return d


def anton_width(text):
    """Width of text in Anton, in em. Uses the real glyph advances when fontTools is available."""
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(str(font_pkg("anton") / "anton-latin-400-normal.woff2"))
        cm, hm, u = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
        return sum(hm[cm.get(ord(c), cm[ord("M")])][0] for c in text.upper()) / u
    except Exception:
        return len(text) * 0.46


def gsap_into(dst):
    root = Path(sh(["npm", "root", "-g"]).strip()) / "hyperframes/dist/vendor/npm"
    g = sorted(root.glob("gsap@*/dist/gsap.min.js"))
    if not g:
        sys.exit("GSAP not found - is hyperframes installed globally? (npm i -g hyperframes)")
    shutil.copy(g[-1], dst / "gsap.min.js")


def compose(work, plan_path):
    work = Path(work); plan = json.loads(Path(plan_path).read_text())
    hf = work / "hf"; hf.mkdir(exist_ok=True); (hf / "assets").mkdir(exist_ok=True)
    shutil.copy(work / "base.mp4", hf / "base.mp4")
    fonts_into(hf / "fonts"); gsap_into(hf)
    total = duration(work / "base.mp4")
    for c in plan["captions"]: c["end"] = min(c["end"], total)
    for o in plan.get("overlays", []):
        if "end" in o: o["end"] = min(o["end"], total)
    els, js, n = [], [], [0]

    def nid(p):
        n[0] += 1; return f"{p}{n[0]}"

    def asset(src):
        p = Path(src)
        if not p.is_absolute(): p = (Path(plan_path).parent / p).resolve()
        shutil.copy(p, hf / "assets" / p.name); return f"assets/{p.name}"

    def clip_attr(a, b):
        return f'data-start="{a:.3f}" data-duration="{max(b-a,0.05):.3f}"'

    for c in plan["captions"]:
        cid = nid("cap"); a, b = c["start"], c["end"]
        lines_html = []
        for ln in c["lines"]:
            st = ln["style"]
            spans = []
            for w, t in ln["words"]:
                wid = nid("w")
                spans.append(f'<span id="{wid}" class="wd">{html.escape(w)}</span>')
                kind = "pop" if st.startswith(("pop", "neon", "white-heavy")) else st if st in ENTER else "lead"
                f, to = ENTER[kind]
                js.append(f'tl.fromTo("#{wid}",{f},{to},{max(t-0.04,a):.3f});')
            lines_html.append(f'<span class="ln {st}">{"".join(spans)}</span>')
        els.append(f'<div id="{cid}" {clip_attr(a,b)} class="clip cap" style="top:{c.get("y",0.47)*H:.0f}px">{"".join(lines_html)}</div>')
        js.append(f'tl.to("#{cid}",{{opacity:0,filter:"blur(6px)",duration:.1}},{max(b-0.1,a):.3f});')

    for o in plan.get("overlays", []):
        t, a, b = o["type"], o.get("start", 0), o.get("end", 0)
        if t == "pills":
            for k, it in enumerate(o["items"]):
                pid = nid("pill"); x = it.get("x", [0.62, 0.18, 0.62, 0.18][k % 4]); y = it.get("y", o.get("y", 0.6))
                els.append(f'<div id="{pid}" {clip_attr(it["at"],b)} class="clip pill" style="left:{x*W:.0f}px;top:{y*H:.0f}px">{html.escape(it["text"])}</div>')
                js.append(f'tl.fromTo("#{pid}",{{opacity:0,scale:.3}},{{opacity:1,scale:1,duration:.28,ease:"back.out(2)"}},{it["at"]:.3f});')
                js.append(f'tl.to("#{pid}",{{opacity:0,duration:.15}},{b-0.15:.3f});')
        elif t == "cards":
            spots = o.get("spots") or [(.08, .30, -6), (.66, .27, 5), (.05, .52, 4), (.70, .50, -5), (.12, .70, -3), (.68, .70, 6)]
            for k, src in enumerate(o["images"]):
                kid = nid("card"); x, y, r = spots[k % len(spots)]; at = a + k * o.get("stagger", 0.18)
                els.append(f'<img id="{kid}" src="{asset(src)}" data-start="{at:.3f}" data-duration="{b-at:.3f}" class="clip card" '
                           f'style="left:{x*W:.0f}px;top:{y*H:.0f}px;width:{o.get("w",260)}px;height:{o.get("h",330)}px;transform:rotate({r}deg)">')
                js.append(f'tl.fromTo("#{kid}",{{opacity:0,scale:.4,y:40}},{{opacity:1,scale:1,y:0,duration:.32,ease:"back.out(1.7)"}},{at:.3f});')
                js.append(f'tl.to("#{kid}",{{y:-30,duration:{b-at-0.3:.3f},ease:"none"}},{at+0.32:.3f});')
                js.append(f'tl.to("#{kid}",{{opacity:0,scale:.8,duration:.15}},{b-0.15:.3f});')
        elif t == "counter":
            kid = nid("cnt"); y = o.get("y", 0.40); fr, to_ = o["from"], o["to"]
            steps = max(min(to_ - fr, 14), 1); seg = (o.get("count_for", 0.6)) / steps
            inner = []
            for k in range(steps + 1):
                v = round(fr + (to_ - fr) * k / steps); sid = nid("n")
                inner.append(f'<span id="{sid}" style="position:absolute;left:0;right:0;opacity:0">{v}</span>')
                js.append(f'tl.set("#{sid}",{{opacity:1}},{a+k*seg:.3f});')
                if k < steps: js.append(f'tl.set("#{sid}",{{opacity:0}},{a+(k+1)*seg:.3f});')
            lead = f'<span class="ln lead">{html.escape(o.get("lead",""))}</span>' if o.get("lead") else ""
            els.append(f'<div id="{kid}" data-start="{a:.3f}" data-duration="{b-a:.3f}" class="clip counter" style="top:{y*H:.0f}px">{lead}'
                       f'<span class="ln pop-silver" style="position:relative;height:150px;font-size:170px">{"".join(inner)}</span>'
                       f'<span class="ln pop-silver" style="font-size:96px"><span>{html.escape(o.get("suffix",""))}</span></span></div>')
            js.append(f'tl.fromTo("#{kid}",{{opacity:0,scale:1.3,filter:"blur(14px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.25}},{a:.3f});')
            js.append(f'tl.to("#{kid}",{{opacity:0,duration:.12}},{b-0.12:.3f});')
        elif t == "call":
            kid = nid("call"); y = o.get("y", 0.47)
            els.append(f'<div id="{kid}" data-start="{a:.3f}" data-duration="{b-a:.3f}" class="clip call" style="top:{y*H:.0f}px">'
                       f'<span><b>{html.escape(o.get("name","CLIENT"))}</b><i>{html.escape(o.get("sub","Mobile"))}</i></span><span class="r"></span><span class="g"></span></div>')
            js.append(f'tl.fromTo("#{kid}",{{opacity:0,y:-60,scale:.9}},{{opacity:1,y:0,scale:1,duration:.3,ease:"back.out(1.6)"}},{a:.3f});')
            js.append(f'tl.to("#{kid}",{{opacity:0,y:-40,duration:.18}},{b-0.18:.3f});')
        elif t == "broll":
            kid = nid("br"); src = asset(o["src"]); vid = src.lower().endswith((".mp4", ".mov", ".webm"))
            tag = (f'<video id="{kid}" src="{src}" muted data-media-start="{o.get("media_start",0)}"' if vid else f'<img id="{kid}" src="{src}"')
            els.append(f'{tag} data-start="{a:.3f}" data-duration="{b-a:.3f}" class="clip broll">{"</video>" if vid else ""}')
            js.append(f'tl.fromTo("#{kid}",{{opacity:0,scale:1.12}},{{opacity:1,scale:1.0,duration:.2}},{a:.3f});')
            js.append(f'tl.to("#{kid}",{{scale:1.06,duration:{b-a-0.2:.3f},ease:"none"}},{a+0.2:.3f});')
            js.append(f'tl.to("#{kid}",{{opacity:0,duration:.12}},{b-0.12:.3f});')
        elif t == "streak":
            kid = nid("stk"); y = o.get("y", 0.40)
            els.append(f'<svg id="{kid}" data-start="{a:.3f}" data-duration="{b-a:.3f}" class="clip layer" viewBox="0 0 1080 1920">'
                       f'<defs><linearGradient id="{kid}g"><stop offset="0" stop-color="#ffe14d"/><stop offset="1" stop-color="#ff8a00"/></linearGradient>'
                       f'<filter id="{kid}f"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
                       f'<path id="{kid}p" d="M-40 {y*H+80:.0f} C 200 {y*H-120:.0f}, 380 {y*H+200:.0f}, 560 {y*H:.0f} S 900 {y*H-160:.0f}, 1120 {y*H-60:.0f}" '
                       f'fill="none" stroke="url(#{kid}g)" stroke-width="16" stroke-linecap="round" filter="url(#{kid}f)" stroke-dasharray="1600" stroke-dashoffset="1600"/></svg>')
            js.append(f'tl.to("#{kid}p",{{attr:{{"stroke-dashoffset":0}},duration:{min(0.6,b-a):.3f},ease:"power2.out"}},{a:.3f});')
            js.append(f'tl.to("#{kid}",{{opacity:0,duration:.2}},{b-0.2:.3f});')
        elif t == "punch":  # zoom-blur whip into a beat, applied to the footage itself
            js.append(f'tl.fromTo("#v",{{scale:{o.get("scale",1.2)},filter:"blur(10px)"}},{{scale:1,filter:"blur(0px)",duration:{o.get("dur",0.3)},ease:"power3.out"}},{o["at"]:.3f});')
        elif t == "title":
            # giant condensed yellow words; each line fitted to the frame width; "behind": true puts the person in front
            kid = nid("ttl"); y = o.get("y", 0.07); margin = o.get("margin", 0.05)
            lines = o["lines"]; spans, top = [], 0
            for k, ln in enumerate(lines):
                txt = ln["text"] if isinstance(ln, dict) else ln
                at = ln.get("at", a) if isinstance(ln, dict) else a
                px = min(o.get("max_px", 640), (1 - 2 * margin) * W / max(anton_width(txt), 0.1))
                if isinstance(ln, dict) and ln.get("px"): px = ln["px"]
                lid = nid("tl")
                spans.append(f'<span id="{lid}" class="tl" style="font-size:{px:.0f}px">{html.escape(txt)}</span>')
                js.append(f'tl.fromTo("#{lid}",{{opacity:0,scale:1.18,y:-20}},{{opacity:1,scale:1,y:0,duration:.14,ease:"power4.out"}},{at:.3f});')
            els.append(f'<div id="{kid}" data-start="{a:.3f}" data-duration="{b-a:.3f}" class="clip title" style="top:{y*H:.0f}px">{"".join(spans)}</div>')
            js.append(f'tl.to("#{kid}",{{opacity:0,duration:.08}},{b-0.08:.3f});')
            if o.get("behind"):
                fg = matte(work, a, b)
                els.append(f'<video id="{nid("fg")}" src="{fg.name}" muted data-start="{a:.3f}" data-duration="{b-a:.3f}" class="clip fg"></video>')
                shutil.copy(fg, hf / fg.name)
        elif t == "grid":
            # collage of past work: 2x2 (or 3/4 tiles) with yellow condensed labels, popping in one by one
            items = o["items"]; gap = 18; cols = 2; rows = math.ceil(len(items) / cols)
            top, bot = o.get("top", 0.12), o.get("bottom", 0.80)
            tw = (W - gap * (cols + 1)) / cols; th = ((bot - top) * H - gap * (rows - 1)) / rows
            for k, it in enumerate(items):
                gid = nid("tile"); x = gap + (k % cols) * (tw + gap); yy = top * H + (k // cols) * (th + gap)
                at = a + k * o.get("stagger", 0.12); src = asset(it["src"]); vid = src.lower().endswith((".mp4", ".mov", ".webm"))
                media = f'<video src="{src}" muted></video>' if vid else f'<img src="{src}">'
                els.append(f'<div id="{gid}" data-start="{at:.3f}" data-duration="{b-at:.3f}" class="clip tile" '
                           f'style="left:{x:.0f}px;top:{yy:.0f}px;width:{tw:.0f}px;height:{th:.0f}px">{media}<span>{html.escape(it.get("label",""))}</span></div>')
                js.append(f'tl.fromTo("#{gid}",{{opacity:0,scale:.85}},{{opacity:1,scale:1,duration:.18,ease:"power3.out"}},{at:.3f});')
        elif t == "flash":
            kid = nid("fl")
            els.append(f'<div id="{kid}" data-start="{o["at"]:.3f}" data-duration="0.35" class="clip flash"></div>')
            js.append(f'tl.fromTo("#{kid}",{{opacity:0}},{{opacity:{o.get("strength",0.7)},duration:.08}},{o["at"]:.3f});')
            js.append(f'tl.to("#{kid}",{{opacity:0,duration:.25}},{o["at"]+0.08:.3f});')
        else:
            print(f"warning: unknown overlay type {t}")

    page = f"""<!doctype html><html><head><meta charset="utf-8"><script src="gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="root" data-width="{W}" data-height="{H}" data-start="0" data-duration="{total:.3f}">
<video id="v" class="clip" src="base.mp4" data-start="0" data-duration="{total:.3f}" data-has-audio="true"></video>
{chr(10).join(els)}
</div>
<script>
const tl=gsap.timeline({{paused:true}});
{chr(10).join(js)}
window.__timelines={{root:tl}};
</script></body></html>"""
    (hf / "index.html").write_text(page)
    print(f"composition -> {hf/'index.html'} ({len(plan['captions'])} captions, {len(plan.get('overlays',[]))} overlays)")


def matte(work, a, b):
    """Cut the person out of base.mp4 over [a,b] -> alpha WebM, laid over titles so the text sits behind them."""
    work = Path(work); out = work / f"fg_{a:.2f}_{b:.2f}.webm"
    if out.exists(): return out
    fr = work / f"fg_frames_{a:.2f}"; fr.mkdir(exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(work / "base.mp4"),
        "-vf", f"fps={FPS}", str(fr / "%04d.png")])
    try:
        from rembg import new_session, remove
    except ImportError:
        sys.exit('text-behind-subject needs rembg:  pip install "rembg[cpu]"')
    from PIL import Image
    sess = new_session("u2net_human_seg")
    for f in sorted(fr.glob("*.png")):
        im = Image.open(f).convert("RGB")
        remove(im, session=sess, post_process_mask=True).save(f)
    sh(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(fr / "%04d.png"), "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p", "-crf", "18", "-b:v", "0", "-auto-alt-ref", "0", str(out)])
    shutil.rmtree(fr)
    return out


def deliver(src, out, fps=None):
    """Instagram / Facebook Reels delivery: 1080x1920 9:16, H.264 High 4.2, yuv420p BT.709, 30fps CFR,
    high bitrate (CRF 16, capped 25 Mbps) so the platform's own re-encode has clean detail to work from,
    AAC-LC 320k 48kHz stereo, moov atom first."""
    fps = fps or FPS
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(src),
        "-vf", f"scale={W}:{H}:flags=lanczos,fps={fps},format=yuv420p",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.2", "-preset", "slow", "-tune", "film",
        "-crf", "16", "-maxrate", "25M", "-bufsize", "50M", "-g", str(int(fps * 2)), "-keyint_min", str(int(fps)),
        "-bf", "2", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-color_range", "tv", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", str(out)])
    d = duration(out); mb = Path(out).stat().st_size / 1e6
    v = next(x for x in probe(out)["streams"] if x["codec_type"] == "video")
    print(f"delivered {out}: {v['width']}x{v['height']} {v.get('profile')} {d:.1f}s {mb:.1f}MB ({mb*8/d:.1f} Mbps)")
    if d > 90: print("note: over 90s - fine for Instagram Reels (up to 3 min) but Facebook Reels caps at 90s.")


def render(work, out, quality):
    hf = Path(work) / "hf"
    master = (Path(work) / "master.mp4").resolve()
    out = Path(out or Path(work) / "final.mp4").resolve()
    # near-lossless master: PNG frame extraction (no JPEG step) and CRF 8, then one clean delivery encode
    cmd = ["hyperframes", "render", str(hf), "-o", str(master), "-q", quality, "--video-frame-format", "png",
           "--fps", str(FPS)]
    if quality != "draft": cmd += ["--crf", "8"]
    r = subprocess.run(cmd)
    if r.returncode: sys.exit("render failed")
    deliver(master, out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("transcribe"); p.add_argument("clips", nargs="+")
    p = sp.add_parser("plan"); p.add_argument("clips", nargs="+"); p.add_argument("-o", default="edl.json"); p.add_argument("--gap", type=float, default=0.45)
    p.add_argument("--look", choices=["kinetic", "cinematic"], default="kinetic"); p.add_argument("--broll", nargs="*", default=[])
    p = sp.add_parser("base"); p.add_argument("edl"); p.add_argument("-o", default="work")
    p = sp.add_parser("captions"); p.add_argument("work"); p.add_argument("-o", default=None); p.add_argument("--look", default=None)
    p = sp.add_parser("deliver"); p.add_argument("src"); p.add_argument("-o", default="final.mp4")
    p = sp.add_parser("matte"); p.add_argument("work"); p.add_argument("start", type=float); p.add_argument("end", type=float)
    p = sp.add_parser("compose"); p.add_argument("work"); p.add_argument("plan")
    p = sp.add_parser("render"); p.add_argument("work"); p.add_argument("-o", default=None); p.add_argument("-q", default="delivery")
    a = ap.parse_args()
    if a.cmd == "transcribe":
        for c in a.clips: print(c, "->", transcribe(c)["text"])
    elif a.cmd == "plan": plan(a.clips, a.o, gap=a.gap, look=a.look, broll=a.broll)
    elif a.cmd == "base": base(a.edl, a.o)
    elif a.cmd == "captions": captions(a.work, a.o or str(Path(a.work) / "plan.json"), a.look)
    elif a.cmd == "deliver": deliver(a.src, a.o)
    elif a.cmd == "matte": print(matte(a.work, a.start, a.end))
    elif a.cmd == "compose": compose(a.work, a.plan)
    elif a.cmd == "render": render(a.work, a.o, a.q)
