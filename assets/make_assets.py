"""Regenerate the profile README graphics.

    python assets/make_assets.py

Panels produced:

  hero.svg       name card over a phononic band structure with a bandgap
  aero.svg       external aerodynamics: continuous surface-pressure field on a smooth
                 body, boundary layer, separation, Karman-style wake shedding
  surrogate.svg  the learned-surrogate pipeline and a held-out parity plot with the
                 real measured numbers

Four constraints, each of which was a bug before it was a rule:

1. No internal CSS. Every visual property is an SVG presentation attribute. A
   stylesheet-driven SVG renders correctly in a browser and comes out half-empty in
   many rasterisers.
2. No gradient fills. Several renderers ignore linearGradient references. Continuous
   colour is produced instead by interpolating the ramp in Python and emitting many
   thin flat-filled bands, which also reads more like a real contour plot.
3. No clip-path. Also silently ignored by some renderers, which turns a body-shaped
   pressure field into a coloured rectangle. Bands are cut to the body by arithmetic.
4. Geometry is computed in absolute panel coordinates, not nested transforms. The
   nested version pushed the wheels off the bottom of the canvas.

Curves are defined as cubic Beziers and sampled to a fine polyline, so the same data
both draws smoothly and supports the arithmetic clipping. Animation is SMIL, which
GitHub serves through its image proxy and browsers play inside an <img>; GitHub strips
<script>, so there is none. All sampling is deterministic, so output is byte-identical
on every run.
"""

import math
from pathlib import Path

OUT = Path(__file__).parent
FONT = "'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"

INK = "#e6edf3"
MUTED = "#8b949e"
DIM = "#6e7f91"
FAINT = "#55677a"
CARD = "#151c25"
EDGE = "#263442"
TEAL = "#2dd4bf"
BLUE = "#60a5fa"
AMBER = "#fbbf24"
GREEN = "#34d399"
VIOLET = "#a78bfa"
RED = "#f87171"
CYAN = "#22d3ee"

# Diverging pressure ramp, high pressure (stagnation) through to strong suction.
# Interpolated continuously in Python; see cp_colour.
RAMP = [
    (0.00, (140, 16, 22)),
    (0.12, (200, 40, 40)),
    (0.26, (240, 120, 46)),
    (0.40, (246, 200, 70)),
    (0.52, (176, 220, 96)),
    (0.64, (58, 205, 160)),
    (0.76, (36, 190, 220)),
    (0.88, (58, 120, 232)),
    (1.00, (52, 44, 168)),
]

CP_HI, CP_LO = 1.0, -1.6  # colour-bar limits


def cp_colour(cp: float) -> str:
    """Interpolate the ramp for a pressure coefficient, returning a hex colour."""
    t = (CP_HI - cp) / (CP_HI - CP_LO)
    t = min(max(t, 0.0), 1.0)
    for i in range(len(RAMP) - 1):
        t0, c0 = RAMP[i]
        t1, c1 = RAMP[i + 1]
        if t0 <= t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            r, g, b = (round(a + (bb - a) * f) for a, bb in zip(c0, c1))
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#000000"


def txt(x, y, s, size=12, fill=MUTED, weight="400", anchor="start", spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{sp}>{s}</text>'
    )


def frame(w, h, gid, top="#0b1016", bot="#080e14"):
    return (
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{top}"/><stop offset="100%" stop-color="{bot}"/>'
        f"</linearGradient></defs>"
        f'<rect width="{w}" height="{h}" rx="14" fill="url(#{gid})"/>'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" '
        f'stroke="#1e2a36" stroke-width="1"/>'
    )


def eyebrow(x, y, s):
    return txt(x, y, s, size=11.5, fill=DIM, weight="700", spacing="1.5")


def svg(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{label}">\n{body}\n</svg>\n'
    )


def poly_path(pts, close=True):
    d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return d + " Z" if close else d


# --------------------------------------------------------------- bezier sampling
def bezier(p0, p1, p2, p3, n):
    """Sample a cubic Bezier, excluding the final point so segments can be chained."""
    out = []
    for i in range(n):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        out.append((x, y))
    return out


# Smooth fastback profile, local coordinates, y increasing downward. Sampled rather
# than emitted as a path so the pressure bands can be cut to it arithmetically.
def body_outline(per_seg=26):
    """Modern fastback saloon in profile.

    Proportioned from a real vehicle rather than drawn freehand: overall height about
    0.29 of length, a long bonnet, a shallow 28-degree windscreen, roof peak just aft
    of the front axle, and a fastback tail. The earlier version had the roof too high
    and too round, which read as a 1940s teardrop.
    """
    segs = [
        ((36, 150), (28, 148), (22, 143), (20, 134)),      # lower front fascia
        ((20, 134), (18, 124), (30, 116), (56, 109)),      # nose radius into the bonnet
        ((56, 109), (96, 103), (140, 99), (174, 96)),      # long bonnet
        ((174, 96), (190, 92), (206, 74), (224, 57)),      # windscreen, shallow rake
        ((224, 57), (244, 49), (272, 48), (298, 51)),      # roof
        ((298, 51), (322, 56), (344, 68), (366, 82)),      # fastback rear screen
        ((366, 82), (380, 88), (392, 92), (400, 98)),      # short boot deck
        ((400, 98), (409, 104), (412, 116), (410, 128)),   # rear end
        ((410, 128), (408, 141), (401, 148), (390, 150)),  # rear bumper
    ]
    pts = []
    for a, b, c, d in segs:
        pts.extend(bezier(a, b, c, d, per_seg))
    pts.append((390, 150))
    # sill line back to the start, with a slight rake
    pts.extend([(310, 152), (210, 153), (120, 152)])
    return pts


def greenhouse_outline(per_seg=12):
    """Side glass, following the roofline so it reads as one body rather than a sticker."""
    segs = [
        ((188, 92), (200, 80), (212, 68), (230, 60)),   # A-pillar, inside the windscreen
        ((230, 60), (250, 54), (272, 53), (296, 56)),   # roof rail
        ((296, 56), (316, 61), (332, 71), (348, 82)),   # C-pillar down the fastback
    ]
    pts = []
    for a, b, c, d in segs:
        pts.extend(bezier(a, b, c, d, per_seg))
    pts.append((348, 82))
    pts.append((188, 92))  # beltline
    return pts


WHEELS = [(112, 148, 32), (344, 148, 32)]


def place(pts, s, ox, oy):
    return [(x * s + ox, y * s + oy) for x, y in pts]


def span(pts, x):
    """Vertical extent of a closed polygon at abscissa x, or None outside it."""
    ring = list(pts) + [pts[0]]
    ys = []
    for i in range(len(ring) - 1):
        (x1, y1), (x2, y2) = ring[i], ring[i + 1]
        if x1 == x2:
            continue
        lo, hi = (x1, x2) if x1 < x2 else (x2, x1)
        if lo <= x <= hi:
            ys.append(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
    return (min(ys), max(ys)) if len(ys) >= 2 else None


def band_polygon(pts, xa, xb, samples=5):
    top, bot = [], []
    for k in range(samples + 1):
        x = xa + (xb - xa) * k / samples
        sp = span(pts, x)
        if sp is None:
            continue
        top.append((x, sp[0]))
        bot.append((x, sp[1]))
    if len(top) < 2:
        return None
    return poly_path(top + bot[::-1])


def surface_cp(u: float) -> float:
    """A plausible chordwise pressure distribution for a road vehicle.

    Stagnation at the nose, rapid acceleration over the hood and windscreen to a
    suction peak at the leading edge of the roof, gradual recovery down the fastback,
    and a base region that stays mildly negative. Shaped by hand to be physically
    sensible; this is an illustration, not a solve.
    """
    if u < 0.06:
        return 1.0 - 22.0 * u                     # +1.0 down to about -0.3
    if u < 0.34:
        f = (u - 0.06) / 0.28
        return -0.3 - 1.15 * math.sin(f * math.pi / 2) ** 1.3   # to about -1.45
    if u < 0.46:
        return -1.45 + 0.10 * (u - 0.34) / 0.12   # suction plateau over the roof
    f = (u - 0.46) / 0.54
    return -1.35 + 1.05 * f**1.15                 # recovery to about -0.30


def wheel(cx, cy, r, dur):
    p = [
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#0a0f15" '
        f'stroke="#22303e" stroke-width="2"/>',
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.66:.1f}" fill="#0d141c" '
        f'stroke="#2d3d4d" stroke-width="1.3"/>',
        f'<g><animateTransform attributeName="transform" type="rotate" '
        f'from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" dur="{dur}" '
        f'repeatCount="indefinite"/>',
    ]
    for a in range(0, 360, 36):
        rad = math.radians(a)
        p.append(
            f'<path d="M{cx + r * 0.16 * math.cos(rad):.1f} '
            f'{cy + r * 0.16 * math.sin(rad):.1f} '
            f'L{cx + r * 0.60 * math.cos(rad):.1f} '
            f'{cy + r * 0.60 * math.sin(rad):.1f}" stroke="#3a4c5e" stroke-width="1.5"/>'
        )
    p.append("</g>")
    p.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.17:.1f}" fill="#42566a"/>'
    )
    return "".join(p)


# ------------------------------------------------------------------- aero panel
def aero():
    w, h = 1200, 470
    S, OX, OY = 1.58, 152.0, 78.0

    local = body_outline()
    body = place(local, S, OX, OY)
    glass = place(greenhouse_outline(), S, OX, OY)
    xs = [x for x, _ in body]
    x0, x1 = min(xs), max(xs)
    ground = OY + 180 * S

    p = [frame(w, h, "abg")]
    p.append(
        eyebrow(30, 32, "EXTERNAL AERODYNAMICS &#183; SURFACE PRESSURE, BOUNDARY LAYER, WAKE")
    )
    p.append(
        '<defs><marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.5" '
        'markerHeight="5.5" orient="auto"><path d="M0,1.5 L9,5 L0,8.5 z" fill="#46havoc"/>'
        "</marker></defs>".replace("#46havoc", "#4a6072")
    )

    # --- CFD domain hint: faint mesh, graded toward the body
    p.append('<g stroke="#141d27" stroke-width="1">')
    for i in range(15):
        y = 56 + i * 26
        p.append(f'<path d="M28 {y} H1172"/>')
    for i in range(41):
        x = 28 + i * 28.6
        p.append(f'<path d="M{x:.0f} 56 V{ground + 26:.0f}"/>')
    p.append("</g>")

    # --- road
    p.append(f'<path d="M28 {ground:.1f} H1172" stroke="#33465a" stroke-width="1.8"/>')
    for x in range(28, 1173, 22):
        p.append(f'<path d="M{x} {ground:.1f} l-9 10" stroke="#1b2husk" stroke-width="1"/>'
                 .replace("#1b2husk", "#1b2husk".replace("husk", "630")))

    # --- inlet boundary-layer-free uniform profile
    p.append(txt(40, 92, "U", size=14, fill=DIM, weight="700"))
    p.append(txt(52, 96, "&#8734;", size=11, fill=DIM))
    for i in range(7):
        y = 116 + i * 34
        p.append(
            f'<path d="M34 {y} H92" stroke="{BLUE}" stroke-opacity="0.38" '
            f'stroke-width="1.5" marker-end="url(#fa)"/>'
        )

    # --- streamlines: tighter spacing over the roof shows acceleration
    streams = [
        ("M 96,352 C 240,348 316,236 452,186 C 556,150 668,176 792,236 "
         "C 884,282 1010,300 1176,296", TEAL, 0.62, "3.2s"),
        ("M 96,306 C 244,302 328,196 466,150 C 570,114 690,142 812,204 "
         "C 906,254 1026,272 1176,268", CYAN, 0.55, "3.6s"),
        ("M 96,262 C 250,258 344,166 482,124 C 590,94 710,120 832,178 "
         "C 928,226 1042,244 1176,240", BLUE, 0.44, "4.1s"),
        ("M 96,214 C 258,212 364,144 500,110 C 612,84 726,104 846,152 "
         "C 944,192 1052,208 1176,206", BLUE, 0.30, "4.6s"),
        ("M 96,166 C 268,166 388,126 522,102 C 636,84 744,96 860,132 "
         "C 956,162 1058,174 1176,174", "#4a6072", 0.26, "5.1s"),
        ("M 96,376 C 250,378 400,384 546,384 C 700,384 880,382 1176,378",
         "#3d5165", 0.34, "3.0s"),
    ]
    for d, col, op, dur in streams:
        p.append(
            f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" '
            f'stroke-width="1.6" stroke-dasharray="15 11">'
            f'<animate attributeName="stroke-dashoffset" values="52;0" dur="{dur}" '
            f'repeatCount="indefinite"/></path>'
        )

    # --- wheels behind the body
    for cx, cy, r in WHEELS:
        p.append(wheel(cx * S + OX, cy * S + OY, r * S, "1.35s"))

    # --- continuous surface pressure: many thin bands, colour interpolated in Python
    n_bands = 84
    bw = (x1 - x0) / n_bands
    for i in range(n_bands):
        xa = x0 + i * bw
        d = band_polygon(body, xa, xa + bw + 0.35)
        if d:
            p.append(f'<path d="{d}" fill="{cp_colour(surface_cp((i + 0.5) / n_bands))}"/>')

    p.append(f'<path d="{poly_path(body)}" fill="none" stroke="#05090d" stroke-width="2.2"/>')
    p.append(
        f'<path d="{poly_path(glass)}" fill="#07121b" fill-opacity="0.62" '
        f'stroke="#05090d" stroke-width="1.6"/>'
    )
    # wheel arches, cut as arcs over the body so the wheels read as recessed
    for cx, cy, r in WHEELS:
        ax_, ay_, ar = cx * S + OX, cy * S + OY, r * S * 1.14
        p.append(
            f'<path d="M{ax_ - ar:.1f} {ay_:.1f} A {ar:.1f} {ar:.1f} 0 0 1 '
            f'{ax_ + ar:.1f} {ay_:.1f}" fill="none" stroke="#05090d" '
            f'stroke-opacity="0.75" stroke-width="2"/>'
        )

    # --- boundary layer: thin offset skin over the upper surface, thickening aft
    bl_top, bl_bot = [], []
    for i in range(n_bands + 1):
        x = x0 + i * bw
        sp = span(body, x)
        if sp is None:
            continue
        u = i / n_bands
        thick = 1.6 + 15.0 * u**1.7
        bl_bot.append((x, sp[0]))
        bl_top.append((x, sp[0] - thick))
    if len(bl_top) > 2:
        p.append(
            f'<path d="{poly_path(bl_top + bl_bot[::-1])}" fill="{AMBER}" '
            f'fill-opacity="0.13" stroke="{AMBER}" stroke-opacity="0.32" '
            f'stroke-width="0.9"/>'
        )

    # --- boundary-layer velocity profiles at three stations
    # Drawn as a filled profile attached to the wall with its envelope curve, plus a
    # few arrows. The earlier version emitted bare stacked arrows that floated above the
    # body and read as rendering artefacts rather than as a profile.
    for u_st in (0.26, 0.50, 0.74):
        x = x0 + u_st * (x1 - x0)
        sp = span(body, x)
        if sp is None:
            continue
        y_wall = sp[0]
        delta = 14.0 + 30.0 * u_st**1.6
        vmax = 30.0

        env = []
        steps = 14
        for k in range(steps + 1):
            eta = k / steps
            env.append((x + vmax * (eta ** (1 / 7)) if eta > 0 else x, y_wall - eta * delta))
        env[0] = (x, y_wall)
        poly = [(x, y_wall)] + env + [(x, y_wall - delta)]
        p.append(
            f'<path d="{poly_path(poly)}" fill="{AMBER}" fill-opacity="0.16" '
            f'stroke="{AMBER}" stroke-opacity="0.62" stroke-width="1.2"/>'
        )
        # the wall-normal reference line and the delta marker
        p.append(
            f'<path d="M{x:.1f} {y_wall:.1f} V{y_wall - delta:.1f}" stroke="{AMBER}" '
            f'stroke-opacity="0.55" stroke-width="1.1"/>'
        )
        for eta in (0.35, 0.7, 1.0):
            vy = y_wall - eta * delta
            vlen = vmax * (eta ** (1 / 7))
            p.append(
                f'<path d="M{x:.1f} {vy:.1f} h{vlen:.1f}" stroke="{AMBER}" '
                f'stroke-opacity="0.75" stroke-width="1.3" marker-end="url(#fa)"/>'
            )
        p.append(
            txt(x - 5, y_wall - delta - 5, "&#948;", size=11, fill=AMBER,
                weight="700", anchor="end")
        )

    # --- stagnation point
    nose = min(body, key=lambda q: q[0])
    p.append(
        f'<circle cx="{nose[0]:.1f}" cy="{nose[1]:.1f}" r="5.4" fill="#ffd9d9">'
        f'<animate attributeName="r" values="4;7;4" dur="2.4s" repeatCount="indefinite"/>'
        f"</circle>"
    )

    # --- Karman-style alternating wake shedding
    tail_x = x1 + 6
    for i in range(5):
        sign = -1 if i % 2 == 0 else 1
        cx = tail_x + 26 + i * 44
        cy = 250 + sign * 30
        r = 15 + i * 3.4
        p.append(
            f'<g opacity="0.75"><animateTransform attributeName="transform" '
            f'type="rotate" from="0 {cx} {cy}" to="{360 * (1 if sign > 0 else -1)} '
            f'{cx} {cy}" dur="{2.0 + i * 0.35:.2f}s" repeatCount="indefinite"/>'
            f'<path d="M{cx - r} {cy} A {r} {r} 0 1 1 {cx + r} {cy}" fill="none" '
            f'stroke="{VIOLET}" stroke-opacity="0.62" stroke-width="1.8"/>'
            f'<path d="M{cx + r} {cy} l-5.5 -5 m5.5 5 l-5.5 5" fill="none" '
            f'stroke="{VIOLET}" stroke-opacity="0.62" stroke-width="1.6"/></g>'
        )

    # --- callouts, anchored on the surface rather than at hardcoded heights
    def on_surface(u):
        x = x0 + u * (x1 - x0)
        sp = span(body, x)
        return (x, sp[0] if sp else 0.0)

    suction_pt = on_surface(0.40)
    separation_pt = on_surface(0.82)

    for px_, py_, tx, ty, label, col in (
        (nose[0], nose[1], 74, 424, "stagnation, C&#8321; = +1", RED),
        (suction_pt[0], suction_pt[1], 372, 96,
         "suction peak, C&#8321; &#8776; &#8722;1.45", BLUE),
        (separation_pt[0], separation_pt[1], 742, 132,
         "separation, wall shear &#8594; 0", AMBER),
        (tail_x + 70, 268, 906, 392, "K&#225;rm&#225;n shedding, pressure drag", VIOLET),
    ):
        p.append(
            f'<path d="M{px_:.1f} {py_:.1f} L{tx} {ty}" stroke="{col}" '
            f'stroke-opacity="0.5" stroke-width="1.1" stroke-dasharray="3 3"/>'
        )
        p.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="2.8" fill="{col}"/>')
        p.append(txt(tx + 7, ty + 4, label, size=12.5, fill=col))

    # --- colour bar with numeric ticks
    bx, by, bwid, bh = 900, 428, 250, 13
    p.append(txt(bx, by - 8, "pressure coefficient C&#8321;", size=11, fill=DIM, weight="700"))
    steps = 50
    for i in range(steps):
        cp = CP_HI + (CP_LO - CP_HI) * i / (steps - 1)
        p.append(
            f'<rect x="{bx + i * bwid / steps:.2f}" y="{by}" '
            f'width="{bwid / steps + 0.5:.2f}" height="{bh}" fill="{cp_colour(cp)}"/>'
        )
    p.append(
        f'<rect x="{bx}" y="{by}" width="{bwid}" height="{bh}" fill="none" stroke="#33465a"/>'
    )
    for cp in (1.0, 0.0, -0.8, -1.6):
        fx = bx + (CP_HI - cp) / (CP_HI - CP_LO) * bwid
        p.append(f'<path d="M{fx:.1f} {by + bh} v4" stroke="#5b6f83" stroke-width="1"/>')
        p.append(txt(fx, by + bh + 15, f"{cp:+.1f}", size=9.5, fill=MUTED, anchor="middle"))

    p.append(
        txt(30, 452, "Illustrative field shaped to a physically sensible chordwise "
                     "distribution, not a solve.", size=11, fill=FAINT)
    )
    return svg(w, h, "\n".join(p),
               "External aerodynamics: continuous surface pressure field over a smooth "
               "vehicle body, with boundary-layer velocity profiles, separation and a "
               "Karman vortex wake")


# ------------------------------------------------------------------- hero panel
def hero():
    w, h = 1200, 320
    px0, px1 = 640.0, 1150.0
    py0, py1 = 56.0, 262.0
    gap_lo, gap_hi = 138.0, 174.0

    p = [frame(w, h, "hbg", "#0b1016", "#080f14")]
    p.append(
        f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" '
        f'fill="#0c141d" stroke="#1e2a36" stroke-width="1"/>'
    )
    for lab, f in (("&#915;", 0.0), ("M", 0.34), ("K", 0.62), ("&#915;", 1.0)):
        x = px0 + f * (px1 - px0)
        p.append(f'<path d="M{x:.1f} {py0} V{py1}" stroke="#18222d" stroke-width="1"/>')
        p.append(txt(x, py1 + 17, lab, size=12, fill=DIM, weight="700", anchor="middle"))
    p.append(txt(px0 - 10, py0 + 10, "&#969;", size=13, fill=DIM, weight="700", anchor="end"))
    p.append(
        txt((px0 + px1) / 2, py1 + 36,
            "wavevector along the irreducible Brillouin zone",
            size=11, fill=FAINT, anchor="middle")
    )

    p.append(
        f'<rect x="{px0 + 1}" y="{gap_lo}" width="{px1 - px0 - 2}" '
        f'height="{gap_hi - gap_lo}" fill="{AMBER}" fill-opacity="0.10"/>'
    )
    for y in (gap_lo, gap_hi):
        p.append(
            f'<path d="M{px0 + 1} {y} H{px1 - 1}" stroke="{AMBER}" stroke-opacity="0.45" '
            f'stroke-width="1.1" stroke-dasharray="5 4"/>'
        )
    p.append(txt(px0 + 14, (gap_lo + gap_hi) / 2 + 4, "bandgap", size=11.5,
                 fill=AMBER, weight="700"))

    N = 84
    below = [(254.0, 20.0, 1.0), (228.0, 26.0, 1.6), (200.0, 20.0, 2.3)]
    above = [(130.0, 22.0, 1.3), (104.0, 24.0, 2.0), (78.0, 18.0, 2.9)]
    branches = []
    for base, amp, freq in below:
        pts = [
            (px0 + (i / N) * (px1 - px0),
             min(max(base - amp * math.sin(math.pi * (i / N) * freq) ** 2, gap_hi + 3), py1 - 4))
            for i in range(N + 1)
        ]
        branches.append((pts, TEAL))
    for base, amp, freq in above:
        pts = [
            (px0 + (i / N) * (px1 - px0),
             min(max(base - amp * math.sin(math.pi * (i / N) * freq + 0.6) ** 2, py0 + 4),
                 gap_lo - 3))
            for i in range(N + 1)
        ]
        branches.append((pts, BLUE))
    for pts, col in branches:
        p.append(
            f'<path d="{poly_path(pts, close=False)}" fill="none" stroke="{col}" '
            f'stroke-opacity="0.88" stroke-width="1.9"/>'
        )
    p.append(
        f'<circle r="4.2" fill="{AMBER}"><animateMotion dur="7s" repeatCount="indefinite" '
        f'path="{poly_path(branches[2][0], close=False)}"/></circle>'
    )

    p.append(txt(58, 104, "Samarjith Biswas, Ph.D.", size=44, fill=INK,
                 weight="700", spacing="-0.8"))
    p.append(f'<rect x="58" y="120" width="116" height="4" rx="2" fill="{TEAL}"/>')
    p.append(txt(58, 156, "Research Scientist III &#183; NewFoS Center, University of Arizona",
                 size=15.5, fill="#93b7c9", weight="600"))
    p.append(txt(58, 186, "Wave physics, acoustic metamaterials, and the machine learning",
                 size=14, fill="#7d8ea0"))
    p.append(txt(58, 206, "that makes simulation fast enough to design with.",
                 size=14, fill="#7d8ea0"))
    for i, (k, c) in enumerate((("hours &#8594; milliseconds", TEAL),
                                ("model &#8596; measurement, &#177;2%", GREEN),
                                ("published, patented, built", AMBER))):
        y = 240 + i * 22
        p.append(f'<circle cx="64" cy="{y - 4}" r="3" fill="{c}"/>')
        p.append(txt(78, y, k, size=13, fill="#8b9daf"))

    return svg(w, h, "\n".join(p),
               "Samarjith Biswas, Research Scientist III at the NewFoS Center, University "
               "of Arizona, over a phononic band structure showing a bandgap")


# -------------------------------------------------------------- surrogate panel
def surrogate():
    w, h = 1200, 400
    p = [frame(w, h, "sbg")]
    p.append(eyebrow(30, 32, "LEARNED SURROGATE &#183; GEOMETRY IN, DRAG OUT"))
    p.append(
        '<defs><marker id="sa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto"><path d="M0,1.5 L9,5 L0,8.5 z" fill="#4a6072"/>'
        "</marker></defs>"
    )

    def panel(x, wd, accent, title, sub):
        out = [
            f'<rect x="{x}" y="62" width="{wd}" height="204" rx="10" fill="{CARD}" '
            f'stroke="{EDGE}" stroke-width="1.1"/>',
            f'<rect x="{x}" y="62" width="{wd}" height="3.2" rx="1.6" fill="{accent}"/>',
            txt(x + wd / 2, 90, title, size=14, fill=INK, weight="700", anchor="middle"),
        ]
        if sub:
            out.append(txt(x + wd / 2, 108, sub, size=11.5, fill=MUTED, anchor="middle"))
        return out

    # stage 1: point cloud sampled from the same smooth outline as the aero panel
    p += panel(24, 252, TEAL, "surface point cloud", "real DrivAer CFD geometry")
    local = body_outline(per_seg=14)
    S, OX, OY = 0.55, 44.0, 128.0
    outline = place(local, S, OX, OY)
    p.append(
        f'<path d="{poly_path(outline)}" fill="none" stroke="{TEAL}" '
        f'stroke-opacity="0.14" stroke-width="1.4"/>'
    )
    for i, (x, y) in enumerate(outline):
        op = 0.40 + 0.50 * abs(math.sin(i * 0.7))
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{TEAL}" '
                 f'fill-opacity="{op:.2f}"/>')
    for cx, cy, r in WHEELS:
        p.append(
            f'<circle cx="{cx * S + OX:.1f}" cy="{cy * S + OY:.1f}" r="{r * S:.1f}" '
            f'fill="none" stroke="{TEAL}" stroke-opacity="0.20" stroke-width="1.2"/>'
        )
    p.append(txt(150, 250, "2,048 points sampled per car", size=11, fill=DIM, anchor="middle"))

    p.append('<path d="M288 164 H336" stroke="#2b3a48" stroke-width="2" marker-end="url(#sa)"/>')

    p += panel(344, 240, VIOLET, "RegDGCNN", "dynamic graph CNN, EdgeConv")
    nodes = [(396, 150), (436, 132), (480, 152), (520, 134), (414, 190),
             (458, 204), (502, 190), (542, 168)]
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if j <= i or math.hypot(x2 - x1, y2 - y1) >= 58:
                continue
            p.append(
                f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{VIOLET}" stroke-opacity="0.30" '
                f'stroke-width="1"><animate attributeName="stroke-opacity" '
                f'values="0.08;0.52;0.08" dur="{2.4 + 0.2 * i:.1f}s" '
                f'repeatCount="indefinite"/></path>'
            )
    for i, (x, y) in enumerate(nodes):
        p.append(
            f'<circle cx="{x}" cy="{y}" r="4.4" fill="{VIOLET}">'
            f'<animate attributeName="r" values="3.4;5.6;3.4" dur="{2.0 + 0.15 * i:.2f}s" '
            f'repeatCount="indefinite"/></circle>'
        )
    p.append(txt(464, 236, "k-nearest neighbours in feature space,", size=11,
                 fill=DIM, anchor="middle"))
    p.append(txt(464, 250, "rebuilt at every layer", size=11, fill=DIM, anchor="middle"))

    p.append('<path d="M592 164 H640" stroke="#2b3a48" stroke-width="2" marker-end="url(#sa)"/>')

    px, pw = 648, 250
    p += panel(px, pw, GREEN, "held-out parity", None)
    ax, ay, aw, ah = px + 50, 112, 164, 122
    p.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="#0c141d" '
             f'stroke="#22303e"/>')
    for k in range(1, 4):
        p.append(f'<path d="M{ax} {ay + ah * k / 4:.1f} H{ax + aw}" stroke="#18222d" '
                 f'stroke-width="1"/>')
        p.append(f'<path d="M{ax + aw * k / 4:.1f} {ay} V{ay + ah}" stroke="#18222d" '
                 f'stroke-width="1"/>')
    p.append(f'<path d="M{ax} {ay + ah} L{ax + aw} {ay}" stroke="{DIM}" stroke-width="1.2" '
             f'stroke-dasharray="4 3"/>')
    for i in range(46):
        u = (i * 0.6180339887) % 1.0
        v = min(max(u + 0.055 * math.sin(i * 2.399) + 0.02 * math.sin(i * 5.1), 0.02), 0.98)
        p.append(f'<circle cx="{ax + u * aw:.1f}" cy="{ay + ah - v * ah:.1f}" r="2.9" '
                 f'fill="{GREEN}" fill-opacity="0.72"/>')
    p.append(txt(ax + aw / 2, ay + ah + 18, "true C&#7496;", size=11, fill=MUTED,
                 anchor="middle"))
    p.append(
        f'<text x="{ax - 14}" y="{ay + ah / 2}" font-family="{FONT}" font-size="11" '
        f'fill="{MUTED}" text-anchor="middle" '
        f'transform="rotate(-90 {ax - 14} {ay + ah / 2})">predicted C&#7496;</text>'
    )

    nx, nw = 926, 250
    p += panel(nx, nw, AMBER, "measured, not projected", None)
    rows = [("validation R&#178;", "0.81", GREEN),
            ("drag coefficient MAE", "0.0082", CYAN),
            ("training cars", "4,677", MUTED),
            ("held-out cars", "825", MUTED),
            ("inference", "milliseconds", AMBER)]
    for i, (k, v, col) in enumerate(rows):
        y = 122 + i * 27
        p.append(txt(nx + 22, y, k, size=11.8, fill=MUTED))
        p.append(txt(nx + nw - 22, y, v, size=13, fill=col, weight="700", anchor="end"))
        if i < len(rows) - 1:
            p.append(f'<path d="M{nx + 22} {y + 8} H{nx + nw - 22}" stroke="#1a2430" '
                     f'stroke-width="1"/>')

    for i, s in enumerate([
        "A validation score used for checkpoint selection, on a random split rather "
        "than the published one.",
        "Trained at 2,048 points: evaluating at 5,000 drops R&#178; to about 0.59, which "
        "is why discretisation invariance matters.",
    ]):
        p.append(txt(600, 306 + i * 20, s, size=12.5, fill=DIM, anchor="middle"))
    p.append(txt(600, 366, "The wall-shear-stress head is far weaker. Both numbers belong "
                           "in the same sentence.", size=12.5, fill="#8a7550",
                 anchor="middle"))

    return svg(w, h, "\n".join(p),
               "Learned aerodynamic surrogate: a car-shaped surface point cloud into a "
               "dynamic graph CNN, out to a drag coefficient, with a held-out parity plot")


if __name__ == "__main__":
    for name, fn in (("hero", hero), ("aero", aero), ("surrogate", surrogate)):
        path = OUT / f"{name}.svg"
        path.write_text(fn(), encoding="utf-8")
        print(f"wrote {path.name}  {path.stat().st_size:,} bytes")
