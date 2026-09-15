"""
Procedural proxy plates for Canyon & Collar.

These are NOT the final assets. They are deterministic SVG stand-in frames — one
per asset, in the locked palette, at the correct aspect ratio, with the reserved
negative space blocked out — so the scroll experience can be built, timed and
reviewed before a single frame of real footage exists.

Swap them out by pointing assets/manifest.json at the real files.
"""
import hashlib
import math

# A sitting dog, facing left, drawn in a 0-100 box with the feet on y=100.
DOG_PARTS = """
  <ellipse cx="70" cy="70" rx="24" ry="30"/>
  <ellipse cx="48" cy="62" rx="22" ry="21"/>
  <rect x="24" y="54" width="11" height="44" rx="5"/>
  <ellipse cx="28" cy="97" rx="9" ry="4"/>
  <ellipse cx="62" cy="96" rx="23" ry="5"/>
  <path d="M 33 52 L 49 45 L 45 24 L 29 29 Z"/>
  <ellipse cx="31" cy="20" rx="15" ry="13"/>
  <path d="M 19 13 C 10 15 2 20 2 25 C 2 30 10 32 19 31 C 22 26 22 18 19 13 Z"/>
  <ellipse cx="39" cy="24" rx="5.5" ry="9"/>
  <path d="M 88 58 C 96 52 103 57 102 67 C 101 73 96 73 96 67 C 95 60 92 60 87 65 Z"/>
"""

# A standing person, facing left, in the same 0-100 box.
PERSON = (
    "M 50 1 C 54 1 57 4 57 8 C 57 12 54 15 50 15 C 46 15 43 12 43 8 C 43 4 46 1 50 1 Z "
    "M 50 16 C 57 16 61 21 62 28 L 64 45 C 64.5 49 60 50 59.5 46 L 58 34 L 58 52 "
    "C 58 56 57 58 57 62 L 58 97 C 58 100 53 100 52.5 97 L 50 66 L 47.5 97 "
    "C 47 100 42 100 42 97 L 43 62 C 43 58 42 56 42 52 L 42 34 L 40.5 46 "
    "C 40 50 35.5 49 36 45 L 38 28 C 39 21 43 16 50 16 Z"
)


class Rand:
    """Deterministic per-asset pseudo-randomness so plates never re-roll."""

    def __init__(self, seed):
        self.h = hashlib.sha256(seed.encode()).digest()
        self.i = 0

    def next(self):
        v = self.h[self.i % len(self.h)]
        self.i += 1
        if self.i % len(self.h) == 0:
            self.h = hashlib.sha256(self.h).digest()
        return v / 255.0

    def between(self, a, b):
        return a + (b - a) * self.next()


def _defs(light, w, h, key):
    sky, land = light["sky"], light["land"]
    return f"""  <defs>
    <linearGradient id="sky{key}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{sky[2]}"/>
      <stop offset="55%" stop-color="{sky[1]}"/>
      <stop offset="100%" stop-color="{sky[0]}"/>
    </linearGradient>
    <linearGradient id="ground{key}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{land[1]}"/>
      <stop offset="100%" stop-color="{land[2]}"/>
    </linearGradient>
    <radialGradient id="sun{key}" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="{light['key']}" stop-opacity="0.95"/>
      <stop offset="45%" stop-color="{light['key']}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="{light['key']}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="haze{key}" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="{light['haze']}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{light['haze']}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="vig{key}" cx="0.5" cy="0.5" r="0.75">
      <stop offset="55%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.42"/>
    </radialGradient>
    <filter id="grain{key}" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <filter id="soft{key}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="{h * 0.012:.1f}"/>
    </filter>
    <filter id="soft2{key}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="{h * 0.045:.1f}"/>
    </filter>
  </defs>
"""


def _ridge(rnd, w, base, amp, mesa=True):
    """One canyon layer. Flat-topped mesas with steep shoulders read as the
    American southwest; smooth sine hills do not."""
    x = -w * 0.06
    level = base - amp * rnd.between(0.35, 0.8)
    d = f"M {x:.0f} {base + amp * 3:.0f} L {x:.0f} {level:.0f}"
    while x < w * 1.06:
        plateau = w * rnd.between(0.05, 0.20)
        x2 = min(x + plateau, w * 1.06)
        # a plateau is not perfectly flat — give it a slight tilt
        level2 = level + amp * rnd.between(-0.05, 0.05)
        d += f" L {x2:.0f} {level2:.0f}"
        x, level = x2, level2
        if x >= w * 1.06:
            break
        slope = w * rnd.between(0.015, 0.06) if mesa else w * 0.12
        drop = amp * rnd.between(-0.55, 0.55)
        nx, nl = min(x + slope, w * 1.06), max(base - amp * 1.15, min(base, level + drop))
        d += (f" C {x + slope * 0.35:.0f} {level:.0f} {nx - slope * 0.30:.0f} {nl:.0f} "
              f"{nx:.0f} {nl:.0f}")
        x, level = nx, nl
    d += f" L {w * 1.06:.0f} {base + amp * 3:.0f} Z"
    return d


def _tufts(rnd, w, y0, y1, count, colours, scale):
    """Scattered desert planting. Scatter across a depth band, scaling with
    distance, so nothing lines up into a hedge."""
    out = []
    for _ in range(count):
        t = rnd.next()                      # 0 = far, 1 = near
        y = y0 + (y1 - y0) * t
        x = rnd.between(-w * 0.02, w * 1.02)
        s = scale * (0.30 + 0.95 * t) * rnd.between(0.7, 1.3)
        colour = colours[min(len(colours) - 1, int(rnd.next() * len(colours)))]
        blades = []
        for b in range(6):
            lean = rnd.between(-1.0, 1.0)
            blades.append(
                f"M {x:.1f} {y:.1f} C {x + lean * s * 0.18:.1f} {y - s * 0.45:.1f} "
                f"{x + lean * s * 0.45:.1f} {y - s * 0.75:.1f} "
                f"{x + lean * s * 0.72:.1f} {y - s:.1f}"
            )
        out.append(
            f'<path d="{" ".join(blades)}" stroke="{colour}" '
            f'stroke-width="{max(0.9, s * 0.05):.1f}" fill="none" '
            f'opacity="{0.20 + 0.40 * t:.2f}" stroke-linecap="round"/>'
        )
    return "\n    ".join(out)


def _scrub(rnd, w, y0, y1, count, colour):
    """Low rounded shrub masses — sage and juniper — for mid-ground body."""
    out = []
    for _ in range(count):
        t = rnd.next()
        y = y0 + (y1 - y0) * t
        x = rnd.between(-w * 0.02, w * 1.02)
        rx = w * rnd.between(0.008, 0.026) * (0.5 + t)
        ry = rx * rnd.between(0.45, 0.75)
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" '
                   f'fill="{colour}" opacity="{0.18 + 0.32 * t:.2f}"/>')
    return "\n    ".join(out)


def _exterior(a, rnd, light, w, h, key):
    sun_x = rnd.between(0.60, 0.80) * w
    horizon = h * rnd.between(0.58, 0.64)
    sun_y = horizon - h * rnd.between(0.26, 0.38)
    building = a["chapter"] in ("ARRIVAL", "WELCOME", "EVENING", "REUNION", "CLOSE")
    night = a["light"] == "dusk"
    path_shot = a["id"] in ("01", "14", "18", "06")

    s = [f'<rect width="{w}" height="{h}" fill="url(#sky{key})"/>']

    if not night:
        s.append(f'<circle cx="{sun_x:.0f}" cy="{sun_y:.0f}" r="{h * 1.25:.0f}" fill="url(#sun{key})"/>')
        s.append(f'<ellipse cx="{sun_x:.0f}" cy="{sun_y:.0f}" rx="{w * 0.46:.0f}" ry="{h * 0.055:.0f}" '
                 f'fill="{light["key"]}" opacity="0.30" filter="url(#soft2{key})"/>')
        s.append(f'<circle cx="{sun_x:.0f}" cy="{sun_y:.0f}" r="{h * 0.034:.0f}" fill="#FFF3DC" '
                 f'opacity="0.95" filter="url(#soft{key})"/>')
    else:
        for _ in range(34):
            s.append(f'<circle cx="{rnd.between(0, w):.0f}" cy="{rnd.between(0, horizon * 0.72):.0f}" '
                     f'r="{rnd.between(0.7, 1.9):.1f}" fill="#F3EBDF" '
                     f'opacity="{rnd.between(0.12, 0.45):.2f}"/>')

    # Three canyon layers, each hazed back toward the sky colour with distance.
    layers = [
        (horizon - h * 0.055, h * 0.26, light["land"][0], 0.42),
        (horizon - h * 0.015, h * 0.17, light["land"][1], 0.66),
        (horizon + h * 0.010, h * 0.10, light["land"][2], 0.88),
    ]
    for base, amp, col, op in layers:
        s.append(f'<path d="{_ridge(rnd, w, base, amp)}" fill="{col}" opacity="{op}"/>')
        s.append(f'<rect y="{base - amp * 1.3:.0f}" width="{w}" height="{amp * 1.3 + h * 0.02:.0f}" '
                 f'fill="url(#haze{key})" opacity="0.38"/>')

    s.append(f'<rect y="{horizon:.0f}" width="{w}" height="{h - horizon:.0f}" fill="url(#ground{key})"/>')
    s.append(f'<ellipse cx="{w * 0.5:.0f}" cy="{h * 1.06:.0f}" rx="{w * 0.75:.0f}" ry="{h * 0.30:.0f}" '
             f'fill="{light["land"][2]}" opacity="0.45" filter="url(#soft2{key})"/>')

    if building:
        bw, bh = w * 0.40, h * 0.185
        bx = w * (0.46 if a["id"] == "18" else 0.28)
        by = horizon - bh * 0.72
        wall = "#2A2621" if night else light["land"][1]
        s.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="{wall}"/>')
        s.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw * 0.24:.0f}" height="{bh:.0f}" '
                 f'fill="#1A1816" opacity="0.18"/>')
        s.append(f'<rect x="{bx - w * 0.024:.0f}" y="{by - h * 0.020:.0f}" width="{bw + w * 0.048:.0f}" '
                 f'height="{h * 0.020:.0f}" fill="#3A2F24"/>')
        s.append(f'<rect x="{bx - w * 0.024:.0f}" y="{by:.0f}" width="{bw + w * 0.048:.0f}" '
                 f'height="{h * 0.012:.0f}" fill="#1A1816" opacity="0.35"/>')
        for i in range(4):
            gx = bx + bw * (0.10 + i * 0.22)
            gw, gh = bw * 0.15, bh * 0.56
            gy = by + bh * 0.26
            s.append(f'<rect x="{gx:.0f}" y="{gy:.0f}" width="{gw:.0f}" height="{gh:.0f}" '
                     f'fill="#E0A04A" opacity="{0.90 if night else 0.42}"/>')
            s.append(f'<rect x="{gx - gw * 0.3:.0f}" y="{gy - gh * 0.12:.0f}" width="{gw * 1.6:.0f}" '
                     f'height="{gh * 1.3:.0f}" fill="#E0A04A" opacity="{0.35 if night else 0.14}" '
                     f'filter="url(#soft2{key})"/>')
        if night:
            for i in range(6):
                s.append(f'<circle cx="{w * (0.30 + i * 0.075):.0f}" '
                         f'cy="{horizon + h * 0.07 + i * h * 0.045:.0f}" r="{h * 0.016:.0f}" '
                         f'fill="#E0A04A" opacity="0.40" filter="url(#soft2{key})"/>')

    if path_shot:
        # decomposed-granite path running from the bottom of frame to the building
        px = w * (0.50 if a["id"] != "18" else 0.60)
        s.append(f'<path d="M {px - w * 0.035:.0f} {horizon:.0f} L {px + w * 0.035:.0f} {horizon:.0f} '
                 f'L {px + w * 0.34:.0f} {h:.0f} L {px - w * 0.36:.0f} {h:.0f} Z" '
                 f'fill="{light["haze"]}" opacity="0.16"/>')
        s.append(f'<path d="M {px - w * 0.035:.0f} {horizon:.0f} L {px - w * 0.36:.0f} {h:.0f}" '
                 f'stroke="#4A4F3C" stroke-width="{h * 0.004:.1f}" opacity="0.30" fill="none"/>')
        s.append(f'<path d="M {px + w * 0.035:.0f} {horizon:.0f} L {px + w * 0.34:.0f} {h:.0f}" '
                 f'stroke="#4A4F3C" stroke-width="{h * 0.004:.1f}" opacity="0.30" fill="none"/>')

    s.append("    " + _scrub(rnd, w, horizon + h * 0.01, h * 1.02, 30, "#3F4534"))
    s.append("    " + _tufts(rnd, w, horizon + h * 0.015, h * 1.04, 46,
                             ["#6E7C60", "#434833", "#9A8460"], h * 0.105))

    # subject
    dog_h = h * (0.26 if a["id"] in ("01", "18") else 0.32)
    dog_x = w * {"01": 0.615, "18": 0.60, "13": 0.40, "06": 0.46, "07": 0.50,
                 "14": 0.52, "17": 0.44, "02": 0.46}.get(a["id"], 0.46)
    ground_y = h * (0.90 if a["id"] in ("01", "18") else 0.965)
    s.append(_dog(dog_x, ground_y - dog_h, dog_h, "#2C1F16" if not night else "#1C1510", 0.92))
    s.append(f'<ellipse cx="{dog_x + dog_h * 0.5:.0f}" cy="{ground_y:.0f}" rx="{dog_h * 0.85:.0f}" '
             f'ry="{dog_h * 0.07:.0f}" fill="#1A1816" opacity="0.22" filter="url(#soft{key})"/>')

    if a["chapter"] in ("NATURE", "PLAY", "EVENING", "REUNION", "GOLDEN HOUR", "WELCOME"):
        ph = h * (0.40 if a["id"] == "13" else 0.50)
        px2 = w * {"13": 0.78, "06": 0.26, "07": 0.86, "14": 0.40, "17": 0.66, "02": 0.26}.get(a["id"], 0.26)
        s.append(_person(px2, h * 0.965 - ph, ph, "#241C15" if not night else "#15100C", 0.88))
    if a["id"] == "07":                       # two companion dogs, well spaced
        for cx, ch in ((0.18, 0.20), (0.76, 0.17)):
            s.append(_dog(w * cx, h * 0.965 - h * ch, h * ch, "#33312E", 0.75))
    return "\n  ".join(s), horizon


def _interior(a, rnd, light, w, h, key):
    warm = a["light"] == "interior_lamp"
    floor = h * 0.66
    s = [f'<rect width="{w}" height="{h}" fill="{light["land"][0] if not warm else "#4A3A2B"}"/>',
         f'<rect width="{w}" height="{floor:.0f}" fill="url(#sky{key})" opacity="0.5"/>',
         # ceiling shadow and the plaster wall's own soft falloff
         f'<rect width="{w}" height="{h * 0.10:.0f}" fill="#1A1816" opacity="0.30"/>',
         f'<rect y="{h * 0.10:.0f}" width="{w}" height="{h * 0.14:.0f}" fill="#1A1816" opacity="0.07"/>',
         f'<rect y="{floor:.0f}" width="{w}" height="{h - floor:.0f}" fill="url(#ground{key})"/>',
         f'<rect y="{floor:.0f}" width="{w}" height="{h * 0.012:.0f}" fill="#1A1816" opacity="0.22"/>']

    # doorway, left — the way in, and the way the staff leave at night
    dx, dy = w * 0.045, h * 0.115
    dw, dh = w * 0.115, floor - dy
    s.append(f'<rect x="{dx:.0f}" y="{dy:.0f}" width="{dw:.0f}" height="{dh:.0f}" fill="#2A211A" opacity="0.9"/>')
    s.append(f'<rect x="{dx + dw * 0.10:.0f}" y="{dy + dh * 0.06:.0f}" width="{dw * 0.80:.0f}" '
             f'height="{dh * 0.94:.0f}" fill="{"#E0A04A" if warm else light["key"]}" '
             f'opacity="{0.40 if warm else 0.30}"/>')
    s.append(f'<rect x="{dx - w * 0.006:.0f}" y="{dy - h * 0.012:.0f}" width="{dw + w * 0.012:.0f}" '
             f'height="{h * 0.012:.0f}" fill="#6B4A32" opacity="0.8"/>')

    # tall window, right of centre
    wx, wy = w * 0.575, h * 0.115
    ww, wh = w * 0.255, floor - wy
    s.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="{ww:.0f}" height="{wh:.0f}" '
             f'fill="{"#2B3448" if warm else light["key"]}" opacity="{0.6 if warm else 0.92}"/>')
    if not warm:                      # canyon and planting seen through the glass
        s.append(f'<rect x="{wx:.0f}" y="{wy + wh * 0.52:.0f}" width="{ww:.0f}" height="{wh * 0.48:.0f}" '
                 f'fill="{light["land"][0]}" opacity="0.30"/>')
        s.append(f'<rect x="{wx:.0f}" y="{wy + wh * 0.50:.0f}" width="{ww:.0f}" height="{wh * 0.03:.0f}" '
                 f'fill="{light["land"][1]}" opacity="0.35"/>')
        for fx, fr, fo in ((0.16, 0.10, 0.45), (0.38, 0.07, 0.35), (0.62, 0.11, 0.40), (0.86, 0.08, 0.30)):
            s.append(f'<ellipse cx="{wx + ww * fx:.0f}" cy="{wy + wh * 0.97:.0f}" rx="{ww * fr * 1.4:.0f}" '
                     f'ry="{wh * fr * 0.8:.0f}" fill="#5E6B4E" opacity="{fo}"/>')
    s.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="{ww:.0f}" height="{wh:.0f}" fill="none" '
             f'stroke="#6B4A32" stroke-width="{w * 0.0045:.1f}"/>')
    s.append(f'<line x1="{wx + ww / 2:.0f}" y1="{wy:.0f}" x2="{wx + ww / 2:.0f}" y2="{floor:.0f}" '
             f'stroke="#6B4A32" stroke-width="{w * 0.003:.1f}"/>')
    s.append(f'<rect x="{wx - w * 0.008:.0f}" y="{wy - h * 0.014:.0f}" width="{ww + w * 0.016:.0f}" '
             f'height="{h * 0.014:.0f}" fill="#6B4A32" opacity="0.85"/>')

    if not warm:
        for spread, op, blur in ((0.45, 0.34, f"soft{key}"), (0.95, 0.10, f"soft2{key}")):
            s.append(f'<path d="M {wx:.0f} {floor:.0f} L {wx + ww:.0f} {floor:.0f} '
                     f'L {wx + ww * spread:.0f} {h:.0f} L {wx - ww * (1.0 - spread * 0.4):.0f} {h:.0f} Z" '
                     f'fill="{light["key"]}" opacity="{op}" filter="url(#{blur})"/>')
        s.append(f'<path d="M {wx:.0f} {wy:.0f} L {wx + ww:.0f} {wy:.0f} L {wx + ww * 0.5:.0f} {h:.0f} '
                 f'L {wx - ww * 0.8:.0f} {h:.0f} Z" fill="{light["key"]}" opacity="0.06" '
                 f'filter="url(#soft2{key})"/>')
    else:
        s.append(f'<circle cx="{w * 0.335:.0f}" cy="{h * 0.40:.0f}" r="{h * 0.09:.0f}" fill="#F0B76E" '
                 f'opacity="0.55" filter="url(#soft{key})"/>')
        s.append(f'<circle cx="{w * 0.335:.0f}" cy="{h * 0.42:.0f}" r="{h * 0.34:.0f}" fill="#F0B76E" '
                 f'opacity="0.24" filter="url(#soft2{key})"/>')

    # wool rug, then the low platform bed on top of it
    s.append(f'<ellipse cx="{w * 0.33:.0f}" cy="{floor + h * 0.20:.0f}" rx="{w * 0.25:.0f}" '
             f'ry="{h * 0.115:.0f}" fill="#9A8460" opacity="0.28"/>')
    bx, by = w * 0.165, floor + h * 0.085
    bw, bh = w * 0.255, h * 0.105
    s.append(f'<rect x="{bx - w * 0.014:.0f}" y="{by + bh * 0.62:.0f}" width="{bw + w * 0.028:.0f}" '
             f'height="{bh * 0.42:.0f}" rx="{bh * 0.10:.0f}" fill="#6B4A32" opacity="0.85"/>')
    s.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh * 0.80:.0f}" '
             f'rx="{bh * 0.34:.0f}" fill="#E4D5C3" opacity="0.95"/>')
    s.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh * 0.24:.0f}" '
             f'rx="{bh * 0.12:.0f}" fill="#F3EBDF" opacity="0.55"/>')
    # the dog's own blanket, folded, never quite square
    s.append(f'<rect x="{bx + bw * 0.60:.0f}" y="{by + bh * 0.16:.0f}" width="{bw * 0.34:.0f}" '
             f'height="{bh * 0.52:.0f}" rx="{bh * 0.08:.0f}" fill="#9C5B3C" opacity="0.55" '
             f'transform="rotate(-1.5 {bx + bw * 0.7:.0f} {by:.0f})"/>')

    # oak ledge with the two stoneware bowls, right
    lx, ly = w * 0.735, floor + h * 0.075
    s.append(f'<rect x="{lx:.0f}" y="{ly:.0f}" width="{w * 0.175:.0f}" height="{h * 0.016:.0f}" '
             f'fill="#6B4A32" opacity="0.9"/>')
    for i in range(2):
        cx = lx + w * 0.045 + i * w * 0.062
        s.append(f'<ellipse cx="{cx:.0f}" cy="{ly - h * 0.004:.0f}" rx="{w * 0.024:.0f}" '
                 f'ry="{h * 0.017:.0f}" fill="#F3EBDF" opacity="0.92"/>')
        s.append(f'<ellipse cx="{cx:.0f}" cy="{ly - h * 0.008:.0f}" rx="{w * 0.016:.0f}" '
                 f'ry="{h * 0.010:.0f}" fill="#33312E" opacity="0.30"/>')
    # storage nook
    s.append(f'<rect x="{w * 0.905:.0f}" y="{floor - h * 0.20:.0f}" width="{w * 0.075:.0f}" '
             f'height="{h * 0.20:.0f}" fill="#1A1816" opacity="0.22"/>')
    s.append(f'<rect x="{w * 0.915:.0f}" y="{floor - h * 0.075:.0f}" width="{w * 0.055:.0f}" '
             f'height="{h * 0.022:.0f}" fill="#9C5B3C" opacity="0.5"/>')

    if a["id"] in ("12", "15"):                       # asleep on the bed
        cy = by + bh * 0.12
        s.append(f'<ellipse cx="{bx + bw * 0.46:.0f}" cy="{cy:.0f}" rx="{bw * 0.29:.0f}" '
                 f'ry="{bh * 0.30:.0f}" fill="#2C1F16" opacity="0.92"/>')
        s.append(f'<circle cx="{bx + bw * 0.19:.0f}" cy="{cy - bh * 0.06:.0f}" r="{bh * 0.24:.0f}" '
                 f'fill="#2C1F16" opacity="0.92"/>')
        s.append(f'<ellipse cx="{bx + bw * 0.09:.0f}" cy="{cy + bh * 0.06:.0f}" rx="{bh * 0.17:.0f}" '
                 f'ry="{bh * 0.10:.0f}" fill="#2C1F16" opacity="0.92"/>')
    else:
        dog_h = h * 0.30
        dog_x = w * (0.525 if a["id"] != "16" else 0.44)
        s.append(_dog(dog_x, h * 0.955 - dog_h, dog_h, "#2C1F16", 0.92))
        s.append(f'<ellipse cx="{dog_x + dog_h * 0.5:.0f}" cy="{h * 0.955:.0f}" rx="{dog_h * 0.8:.0f}" '
                 f'ry="{dog_h * 0.06:.0f}" fill="#1A1816" opacity="0.22" filter="url(#soft{key})"/>')

    if a["chapter"] in ("CARE", "EVENING", "MORNING", "PEACE OF MIND"):
        ph = h * 0.60
        s.append(_person(w * 0.175, h * 0.955 - ph, ph, "#33312E", 0.85))
    return "\n  ".join(s), floor


def _macro(a, rnd, light, w, h, key):
    """Collar, leash hardware, water — one lit object, everything else gone."""
    s = [f'<rect width="{w}" height="{h}" fill="{light["land"][2]}"/>',
         f'<circle cx="{w * 0.32:.0f}" cy="{h * 0.30:.0f}" r="{h * 0.78:.0f}" '
         f'fill="url(#sun{key})" opacity="0.50"/>']
    for _ in range(18):                      # out-of-focus highlights behind
        s.append(f'<circle cx="{rnd.between(0, w):.0f}" cy="{rnd.between(0, h * 0.75):.0f}" '
                 f'r="{rnd.between(h * 0.04, h * 0.15):.0f}" fill="{light["key"]}" '
                 f'opacity="{rnd.between(0.04, 0.13):.2f}" filter="url(#soft2{key})"/>')

    # the strap, running low-left to high-right
    top = (f"M -20 {h * 0.80:.0f} C {w * 0.34:.0f} {h * 0.72:.0f} {w * 0.60:.0f} {h * 0.50:.0f} "
           f"{w + 20:.0f} {h * 0.38:.0f}")
    bot = (f"M -20 {h * 1.02:.0f} C {w * 0.34:.0f} {h * 0.94:.0f} {w * 0.60:.0f} {h * 0.72:.0f} "
           f"{w + 20:.0f} {h * 0.60:.0f}")
    s.append(f'<path d="{top} L {w + 20:.0f} {h * 0.60:.0f} '
             f'C {w * 0.60:.0f} {h * 0.72:.0f} {w * 0.34:.0f} {h * 0.94:.0f} -20 {h * 1.02:.0f} Z" '
             f'fill="#6B4A32"/>')
    s.append(f'<path d="{top}" stroke="{light["key"]}" stroke-width="{h * 0.010:.1f}" fill="none" '
             f'opacity="0.55"/>')                                        # burnished top edge
    s.append(f'<path d="{bot}" stroke="#1A1816" stroke-width="{h * 0.014:.1f}" fill="none" '
             f'opacity="0.45"/>')                                        # shadowed lower edge
    for off, op in ((0.035, 0.30), (0.175, 0.22)):                       # saddle stitching
        s.append(f'<path d="{top}" transform="translate(0,{h * off:.0f})" stroke="#D8C3A5" '
                 f'stroke-width="{max(1.0, h * 0.004):.1f}" stroke-dasharray="{h * 0.022:.0f} {h * 0.018:.0f}" '
                 f'fill="none" opacity="{op}"/>')

    # brass hardware: a D-ring, then the engraved tag hanging off it
    rx, ry = w * 0.335, h * 0.685
    s.append(f'<ellipse cx="{rx:.0f}" cy="{ry:.0f}" rx="{h * 0.055:.0f}" ry="{h * 0.050:.0f}" '
             f'fill="none" stroke="#B08B4F" stroke-width="{h * 0.022:.1f}"/>')
    s.append(f'<ellipse cx="{rx:.0f}" cy="{ry - h * 0.012:.0f}" rx="{h * 0.050:.0f}" ry="{h * 0.030:.0f}" '
             f'fill="none" stroke="#F0D9A6" stroke-width="{h * 0.006:.1f}" opacity="0.6"/>')

    tw, th = w * 0.155, h * 0.30
    tx, ty = w * 0.40, h * 0.56
    rot = f'rotate(-7 {tx + tw / 2:.0f} {ty + th / 2:.0f})'
    s.append(f'<g transform="{rot}">'
             f'<rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" height="{th:.0f}" rx="{th * 0.16:.0f}" '
             f'fill="#A8813F"/>'
             f'<rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" height="{th * 0.42:.0f}" '
             f'rx="{th * 0.16:.0f}" fill="#E3C075" opacity="0.55"/>'
             f'<rect x="{tx + tw * 0.06:.0f}" y="{ty + th * 0.07:.0f}" width="{tw * 0.88:.0f}" '
             f'height="{th * 0.86:.0f}" rx="{th * 0.11:.0f}" fill="none" stroke="#F3E0B4" '
             f'stroke-width="{max(1.0, h * 0.003):.1f}" opacity="0.45"/>'
             # struck engraving: a dark cut with a bright catching edge below it
             f'<rect x="{tx + tw * 0.14:.0f}" y="{ty + th * 0.36:.0f}" width="{tw * 0.72:.0f}" '
             f'height="{th * 0.075:.0f}" rx="{th * 0.02:.0f}" fill="#4A3418" opacity="0.75"/>'
             f'<rect x="{tx + tw * 0.14:.0f}" y="{ty + th * 0.435:.0f}" width="{tw * 0.72:.0f}" '
             f'height="{th * 0.018:.0f}" fill="#FFF0C8" opacity="0.55"/>'
             f'<rect x="{tx + tw * 0.22:.0f}" y="{ty + th * 0.56:.0f}" width="{tw * 0.56:.0f}" '
             f'height="{th * 0.045:.0f}" rx="{th * 0.015:.0f}" fill="#4A3418" opacity="0.65"/>'
             f'<rect x="{tx + tw * 0.22:.0f}" y="{ty + th * 0.605:.0f}" width="{tw * 0.56:.0f}" '
             f'height="{th * 0.012:.0f}" fill="#FFF0C8" opacity="0.4"/>'
             f'</g>')
    s.append(f'<ellipse cx="{tx + tw * 0.2:.0f}" cy="{ty + th * 0.15:.0f}" rx="{w * 0.05:.0f}" '
             f'ry="{h * 0.07:.0f}" fill="{light["key"]}" opacity="0.28" filter="url(#soft2{key})"/>')

    if a["id"] == "08":                       # water, not leather: a bowl rim and a meniscus
        s.append(f'<ellipse cx="{w * 0.52:.0f}" cy="{h * 0.72:.0f}" rx="{w * 0.30:.0f}" '
                 f'ry="{h * 0.20:.0f}" fill="#F3EBDF" opacity="0.30"/>')
        s.append(f'<ellipse cx="{w * 0.52:.0f}" cy="{h * 0.72:.0f}" rx="{w * 0.255:.0f}" '
                 f'ry="{h * 0.165:.0f}" fill="#3E4E64" opacity="0.45"/>')
        s.append(f'<ellipse cx="{w * 0.47:.0f}" cy="{h * 0.68:.0f}" rx="{w * 0.10:.0f}" '
                 f'ry="{h * 0.045:.0f}" fill="{light["key"]}" opacity="0.35" filter="url(#soft{key})"/>')
        for _ in range(9):
            s.append(f'<circle cx="{rnd.between(w * 0.30, w * 0.75):.0f}" '
                     f'cy="{rnd.between(h * 0.60, h * 0.84):.0f}" r="{rnd.between(2, h * 0.012):.1f}" '
                     f'fill="#F3EBDF" opacity="{rnd.between(0.25, 0.6):.2f}"/>')

    s.append(f'<rect width="{w}" height="{h}" fill="#1A1816" opacity="0.22"/>')
    return "\n  ".join(s), h * 0.7


def _dog(x, y, height, colour, opacity, flip=False):
    sc = height / 100.0
    mirror = ' scale(-1,1) translate(-100,0)' if flip else ''
    return (f'<g transform="translate({x:.0f},{y:.0f}) scale({sc:.3f}){mirror}" fill="{colour}" '
            f'opacity="{opacity}">{DOG_PARTS}</g>')


def _person(x, y, height, colour, opacity):
    sc = height / 100.0
    return (f'<g transform="translate({x:.0f},{y:.0f}) scale({sc:.3f})" fill="{colour}" '
            f'opacity="{opacity}"><path d="{PERSON}"/></g>')


NEG_BOXES = {
    "upper left third and sky band": (0.04, 0.06, 0.42, 0.46),
    "upper right":                   (0.56, 0.07, 0.40, 0.40),
    "left third":                    (0.04, 0.12, 0.30, 0.72),
    "left wall plane":               (0.05, 0.12, 0.32, 0.68),
    "upper band / sky":              (0.06, 0.06, 0.88, 0.28),
    "right third":                   (0.65, 0.10, 0.30, 0.74),
    "upper left":                    (0.05, 0.08, 0.40, 0.38),
    "upper left sky":                (0.05, 0.07, 0.40, 0.40),
    "right third — reserve for UI overlay": (0.64, 0.10, 0.31, 0.74),
    "upper band / deep blue sky":    (0.06, 0.05, 0.88, 0.30),
    "right two-thirds":              (0.36, 0.10, 0.58, 0.76),
    "entire left half and lower third — reserve for wordmark and three CTAs":
                                     (0.05, 0.10, 0.44, 0.76),
}


def render(a, light, out_path, show_guides=True):
    w, h = (2390, 1000) if a["ratio"] == "2.39:1" else (1920, 1080)
    key = a["id"]
    rnd = Rand(f'{a["id"]}-{a["slug"]}')
    body = {"EXT": _exterior, "INT": _interior, "MACRO": _macro}[a["mode"]](a, rnd, light, w, h, key)[0]

    guides = ""
    if show_guides:
        box = NEG_BOXES.get(a["negative_space"])
        if box:
            bx, by, bw, bh = box[0] * w, box[1] * h, box[2] * w, box[3] * h
            guides += (f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="none" '
                       f'stroke="#F3EBDF" stroke-opacity="0.30" stroke-width="2" stroke-dasharray="14 12"/>\n  '
                       f'<text x="{bx + 18:.0f}" y="{by + 34:.0f}" font-family="Helvetica,Arial,sans-serif" '
                       f'font-size="20" letter-spacing="3" fill="#F3EBDF" fill-opacity="0.55">'
                       f'RESERVED — {a["negative_space"].split(" — ")[0].upper()}</text>\n  ')
        label = f'{a["id"]} · {a["title"]}'
        meta = f'{a["lens"]} · {a["ratio"]} · {a["duration"]} · {light["label"]}'
        guides += (
            f'<text x="48" y="{h - 78}" font-family="Helvetica,Arial,sans-serif" font-size="30" '
            f'letter-spacing="7" fill="#F3EBDF" fill-opacity="0.82">{label}</text>\n  '
            f'<text x="48" y="{h - 42}" font-family="Helvetica,Arial,sans-serif" font-size="20" '
            f'letter-spacing="4" fill="#F3EBDF" fill-opacity="0.55">{meta}</text>\n  '
            f'<text x="{w - 48}" y="{h - 42}" text-anchor="end" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="20" letter-spacing="5" fill="#F3EBDF" fill-opacity="0.45">'
            f'PROXY PLATE — NOT FINAL ASSET</text>\n  '
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"
     role="img" aria-label="{a['title']} — Canyon and Collar proxy plate">
  <title>{a['id']} {a['title']} — Canyon &amp; Collar proxy plate</title>
{_defs(light, w, h, key)}  {body}
  <rect width="{w}" height="{h}" fill="url(#vig{key})"/>
  <rect width="{w}" height="{h}" filter="url(#grain{key})" opacity="0.11"/>
  {guides}</svg>
"""
    with open(out_path, "w") as f:
        f.write(svg)
    return out_path
