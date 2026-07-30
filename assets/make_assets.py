"""Regenerate the profile README graphics.

    python assets/make_assets.py

Panels produced:

  aero.svg       external aerodynamics: banded surface-pressure field over a body,
                 streamlines, separation and wake, with a discrete Cp colour bar
  surrogate.svg  the learned-surrogate pipeline and a held-out parity plot carrying
                 the real measured numbers

Three deliberate constraints, each of which was a bug first:

1. No internal CSS. Every visual property is an SVG presentation attribute. A
   stylesheet-driven SVG looks correct in a browser and comes out half-empty in
   many rasterisers.
2. No gradient fills for anything load-bearing. Several renderers ignore
   linearGradient references, so the pressure field is drawn as discrete clipped
   bands, which also reads more like a real contour plot.
3. Geometry is computed in absolute panel coordinates from one shared outline
   polyline, not nested transforms. The nested-transform version pushed the wheels
   off the bottom of the canvas.

Animation is SMIL, which GitHub serves through its image proxy and browsers play
inside an <img>. GitHub strips <script>, so there is none. Scatter and point-cloud
positions come from a fixed low-discrepancy walk, so output is byte-identical on
every run.
"""

import math
from pathlib import Path

OUT = Path(__file__).parent
FONT = "'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"

INK = "#e6edf3"
MUTED = "#8b949e"
DIM = "#6e7f91"
CARD = "#151c25"
EDGE = "#263442"
TEAL = "#2dd4bf"
BLUE = "#60a5fa"
AMBER = "#fbbf24"
GREEN = "#34d399"
VIOLET = "#a78bfa"
RED = "#f87171"
CYAN = "#22d3ee"

# Vehicle side profile as one closed polyline, local coordinates.
# Shared by the pressure panel and the point-cloud panel so the two agree.
OUTLINE = [
    (34, 148), (26, 126), (29, 110), (44, 100), (70, 93), (130, 86),
    (168, 52), (218, 48), (268, 46), (318, 82), (372, 86), (391, 92),
    (399, 110), (396, 128), (392, 148), (300, 152), (200, 154), (110, 152),
]
GREENHOUSE = [(178, 57), (260, 53), (300, 79), (152, 79)]
WHEELS = [(96, 148, 27), (330, 148, 27)]

# Physically ordered pressure bands from nose to tail: stagnation, acceleration
# to a suction peak over the greenhouse, then partial pressure recovery.
BANDS = ["#b91c1c", "#dc2626", "#f97316", "#fbbf24", "#a3e635", "#34d399",
         "#22d3ee", "#3b82f6", "#4338ca", "#3b82f6", "#22d3ee", "#34d399",
         "#a3e635", "#fbbf24"]
BAR = ["#b91c1c", "#f97316", "#fbbf24", "#a3e635", "#34d399", "#22d3ee",
       "#3b82f6", "#4338ca"]


def txt(x, y, s, size=12, fill=MUTED, weight="400", anchor="start", spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{sp}>{s}</text>')


def frame(w, h, gid, top="#0d1117", bot="#0b1620"):
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="{top}"/><stop offset="100%" stop-color="{bot}"/>'
            f'</linearGradient></defs>'
            f'<rect width="{w}" height="{h}" rx="14" fill="url(#{gid})"/>'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="none" '
            f'stroke="#233240" stroke-width="1"/>')


def eyebrow(x, y, s):
    return txt(x, y, s, size=12, fill=DIM, weight="700", spacing="1.4")


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{label}">\n{body}\n</svg>\n')


def place(pts, s, ox, oy):
    """Map local outline coordinates into absolute panel coordinates."""
    return [(x * s + ox, y * s + oy) for x, y in pts]


def poly_path(pts, close=True):
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + " Z" if close else d


def walk(pts, n):
    """N points spaced evenly along a closed polyline, by arc length."""
    ring = pts + [pts[0]]
    segs, total = [], 0.0
    for i in range(len(ring) - 1):
        (x1, y1), (x2, y2) = ring[i], ring[i + 1]
        L = math.hypot(x2 - x1, y2 - y1)
        segs.append((x1, y1, x2, y2, L))
        total += L
    out, step = [], total / n
    for k in range(n):
        target, acc = k * step, 0.0
        for x1, y1, x2, y2, L in segs:
            if acc + L >= target:
                t = (target - acc) / L if L else 0.0
                out.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
                break
            acc += L
    return out


def span(pts, x):
    """Vertical extent of a closed polygon at abscissa x, or None outside it.

    Used instead of an SVG clip-path. Several renderers ignore clipPath entirely,
    which silently turns a body-shaped pressure plot into a coloured rectangle, so
    the bands are cut to the body by arithmetic instead.
    """
    ring = pts + [pts[0]]
    ys = []
    for i in range(len(ring) - 1):
        (x1, y1), (x2, y2) = ring[i], ring[i + 1]
        if x1 == x2:
            continue
        lo, hi = (x1, x2) if x1 < x2 else (x2, x1)
        if lo <= x <= hi:
            ys.append(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
    return (min(ys), max(ys)) if len(ys) >= 2 else None


def band_polygon(pts, xa, xb, samples=7):
    """Filled quad-strip covering [xa, xb] of the polygon interior."""
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


def wheel(cx, cy, r, dur, hub="#0d1319", rim="#2b3a48", spoke="#33445a"):
    p = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{hub}" stroke="{rim}" stroke-width="1.8"/>',
         f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.62:.1f}" fill="none" stroke="#39485a" stroke-width="1.2"/>',
         f'<g><animateTransform attributeName="transform" type="rotate" '
         f'from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" dur="{dur}" repeatCount="indefinite"/>']
    for a in range(0, 360, 45):
        rad = math.radians(a)
        p.append(f'<path d="M{cx:.1f} {cy:.1f} L{cx + r * 0.58 * math.cos(rad):.1f} '
                 f'{cy + r * 0.58 * math.sin(rad):.1f}" stroke="{spoke}" stroke-width="1.3"/>')
    p.append('</g>')
    return "".join(p)


# ------------------------------------------------------------------- aero panel
def aero():
    w, h = 1200, 440
    S, OX, OY = 1.45, 170.0, 100.0
    body = place(OUTLINE, S, OX, OY)
    glass = place(GREENHOUSE, S, OX, OY)
    xs = [x for x, _ in body]
    ys = [y for _, y in body]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    ground = OY + 175 * S  # wheel bottom

    p = [frame(w, h, "abg")]
    p.append(eyebrow(30, 34, "EXTERNAL AERODYNAMICS &#183; SURFACE PRESSURE, SEPARATION, WAKE"))
    p.append('<defs>')
    p.append('<marker id="fa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
             'markerHeight="6" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="#4b6478"/></marker>')
    p.append('</defs>')

    # road
    p.append(f'<path d="M60 {ground:.0f} H1150" stroke="#2a3947" stroke-width="1.6"/>')
    for x in range(60, 1151, 24):
        p.append(f'<path d="M{x} {ground:.0f} l-8 9" stroke="#1c2836" stroke-width="1"/>')

    # freestream
    p.append(txt(44, 150, "U", size=14, fill=DIM, weight="700"))
    p.append(txt(56, 154, "&#8734;", size=11, fill=DIM))
    for i in range(6):
        y = 172 + i * 30
        p.append(f'<path d="M38 {y} H96" stroke="{BLUE}" stroke-opacity="0.40" '
                 f'stroke-width="1.5" marker-end="url(#fa)"/>')

    # streamlines, absolute coordinates, hugging then releasing into the wake
    streams = [
        ("M 100,336 C 230,332 300,250 430,200 C 520,166 640,186 752,236 "
         "C 840,274 980,286 1150,282", TEAL, 0.60, "3.4s"),
        ("M 100,282 C 230,278 312,206 442,160 C 534,128 650,148 762,200 "
         "C 852,240 986,254 1150,250", CYAN, 0.52, "3.8s"),
        ("M 100,228 C 240,226 336,172 466,136 C 566,110 674,126 790,168 "
         "C 880,200 998,214 1150,210", BLUE, 0.42, "4.3s"),
        ("M 100,174 C 250,174 356,142 486,120 C 596,102 700,112 812,142 "
         "C 906,168 1016,178 1150,176", BLUE, 0.28, "4.8s"),
        ("M 100,348 C 250,350 400,354 540,354 C 700,354 900,352 1150,348",
         "#4b6478", 0.35, "3.0s"),
    ]
    for d, col, op, dur in streams:
        p.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" '
                 f'stroke-width="1.6" stroke-dasharray="13 10">'
                 f'<animate attributeName="stroke-dashoffset" values="46;0" dur="{dur}" '
                 f'repeatCount="indefinite"/></path>')

    # wheels behind the body
    for cx, cy, r in WHEELS:
        p.append(wheel(cx * S + OX, cy * S + OY, r * S, "1.5s"))

    # banded pressure field, cut to the body by geometry rather than clip-path
    bw = (x1 - x0) / len(BANDS)
    for i, col in enumerate(BANDS):
        d = band_polygon(body, x0 + i * bw, x0 + (i + 1) * bw)
        if d:
            p.append(f'<path d="{d}" fill="{col}" fill-opacity="0.84" stroke="#0b1017" '
                     f'stroke-opacity="0.22" stroke-width="0.8"/>')
    p.append(f'<path d="{poly_path(body)}" fill="none" stroke="#080d13" stroke-width="2"/>')
    p.append(f'<path d="{poly_path(glass)}" fill="#0d1a26" fill-opacity="0.62" '
             f'stroke="#080d13" stroke-width="1.4"/>')

    # stagnation marker at the nose
    nx, ny = body[1]
    p.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="#fecaca" fill-opacity="0.95">'
             f'<animate attributeName="r" values="3.8;6.6;3.8" dur="2.4s" repeatCount="indefinite"/></circle>')

    # wake vortices behind the tail
    for cx, cy, r, dur in ((790, 250, 17, "2.6s"), (836, 286, 12, "2.1s"), (786, 306, 9, "1.8s")):
        p.append(f'<g><animateTransform attributeName="transform" type="rotate" '
                 f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="{dur}" repeatCount="indefinite"/>'
                 f'<path d="M{cx - r} {cy} A {r} {r} 0 1 1 {cx + r} {cy}" fill="none" '
                 f'stroke="{VIOLET}" stroke-opacity="0.60" stroke-width="1.7"/>'
                 f'<path d="M{cx + r} {cy} l-5 -5 m5 5 l-5 5" fill="none" stroke="{VIOLET}" '
                 f'stroke-opacity="0.60" stroke-width="1.5"/></g>')

    # callouts
    for px_, py_, tx, ty, label, col, anch in (
        (nx, ny, 96, 392, "stagnation, C&#8321; = +1", RED, "start"),
        (476, y0 + 2, 520, 112, "suction peak over the greenhouse", BLUE, "start"),
        (630, 222, 690, 168, "separation, wall shear &#8594; 0", AMBER, "start"),
        (806, 268, 872, 330, "wake, pressure drag", VIOLET, "start"),
    ):
        p.append(f'<path d="M{px_:.1f} {py_:.1f} L{tx} {ty}" stroke="{col}" stroke-opacity="0.55" '
                 f'stroke-width="1.2" stroke-dasharray="3 3"/>')
        p.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="2.8" fill="{col}"/>')
        p.append(txt(tx + 7, ty + 4, label, size=12.5, fill=col, anchor=anch))

    # discrete colour bar
    bx, by, sw, bh = 946, 380, 24, 13
    p.append(txt(bx, by - 9, "pressure coefficient C&#8321;", size=11.5, fill=DIM, weight="600"))
    for i, col in enumerate(BAR):
        p.append(f'<rect x="{bx + i * sw}" y="{by}" width="{sw}" height="{bh}" fill="{col}"/>')
    p.append(f'<rect x="{bx}" y="{by}" width="{sw * len(BAR)}" height="{bh}" fill="none" '
             f'stroke="#2b3a48"/>')
    p.append(txt(bx, by + bh + 15, "+1", size=11, fill=MUTED))
    p.append(txt(bx + sw * len(BAR), by + bh + 15, "suction", size=11, fill=MUTED, anchor="end"))

    return svg(w, h, "\n".join(p),
               "External aerodynamics: banded surface pressure field over a vehicle body with "
               "streamlines, separation point and wake vortices")


# -------------------------------------------------------------- surrogate panel
def surrogate():
    w, h = 1200, 400
    p = [frame(w, h, "sbg")]
    p.append(eyebrow(30, 34, "LEARNED SURROGATE &#183; GEOMETRY IN, DRAG OUT"))
    p.append('<defs><marker id="sa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" '
             'markerHeight="8" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="#4b6478"/>'
             '</marker></defs>')

    def panel(x, wd, accent, title, sub):
        out = [f'<rect x="{x}" y="62" width="{wd}" height="204" rx="10" fill="{CARD}" '
               f'stroke="{EDGE}" stroke-width="1.1"/>',
               f'<rect x="{x}" y="62" width="{wd}" height="3.2" rx="1.6" fill="{accent}"/>',
               txt(x + wd / 2, 90, title, size=14, fill=INK, weight="700", anchor="middle")]
        if sub:
            out.append(txt(x + wd / 2, 108, sub, size=11.5, fill=MUTED, anchor="middle"))
        return out

    # stage 1: car-shaped point cloud, same outline as the aero panel
    p += panel(24, 252, TEAL, "surface point cloud", "real DrivAer CFD geometry")
    S, OX, OY = 0.56, 42.0, 132.0
    cloud = walk(OUTLINE, 104)
    p.append(f'<path d="{poly_path(place(OUTLINE, S, OX, OY))}" fill="none" stroke="{TEAL}" '
             f'stroke-opacity="0.16" stroke-width="1.6"/>')
    for i, (lx, ly) in enumerate(cloud):
        x, y = lx * S + OX, ly * S + OY
        op = 0.42 + 0.48 * abs(math.sin(i * 0.9))
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{TEAL}" fill-opacity="{op:.2f}"/>')
    for cx, cy, r in WHEELS:
        p.append(f'<circle cx="{cx * S + OX:.1f}" cy="{cy * S + OY:.1f}" r="{r * S:.1f}" '
                 f'fill="none" stroke="{TEAL}" stroke-opacity="0.22" stroke-width="1.3"/>')
    p.append(txt(150, 250, "2,048 points sampled per car", size=11, fill=DIM, anchor="middle"))

    p.append('<path d="M288 164 H336" stroke="#2b3a48" stroke-width="2" marker-end="url(#sa)"/>')

    # stage 2: the network
    p += panel(344, 240, VIOLET, "RegDGCNN", "dynamic graph CNN, EdgeConv")
    nodes = [(396, 150), (436, 132), (480, 152), (520, 134), (414, 190),
             (458, 204), (502, 190), (542, 168)]
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if j <= i or math.hypot(x2 - x1, y2 - y1) >= 58:
                continue
            p.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{VIOLET}" stroke-opacity="0.30" '
                     f'stroke-width="1"><animate attributeName="stroke-opacity" '
                     f'values="0.08;0.52;0.08" dur="{2.4 + 0.2 * i:.1f}s" repeatCount="indefinite"/></path>')
    for i, (x, y) in enumerate(nodes):
        p.append(f'<circle cx="{x}" cy="{y}" r="4.4" fill="{VIOLET}">'
                 f'<animate attributeName="r" values="3.4;5.6;3.4" dur="{2.0 + 0.15 * i:.2f}s" '
                 f'repeatCount="indefinite"/></circle>')
    p.append(txt(464, 236, "k-nearest neighbours in feature space,", size=11, fill=DIM, anchor="middle"))
    p.append(txt(464, 250, "rebuilt at every layer", size=11, fill=DIM, anchor="middle"))

    p.append('<path d="M592 164 H640" stroke="#2b3a48" stroke-width="2" marker-end="url(#sa)"/>')

    # stage 3: parity
    px, pw = 648, 250
    p += panel(px, pw, GREEN, "held-out parity", None)
    ax, ay, aw, ah = px + 50, 112, 164, 122
    p.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="#101820" stroke="#243240"/>')
    for k in range(1, 4):
        p.append(f'<path d="M{ax} {ay + ah * k / 4:.1f} H{ax + aw}" stroke="#1a2532" stroke-width="1"/>')
        p.append(f'<path d="M{ax + aw * k / 4:.1f} {ay} V{ay + ah}" stroke="#1a2532" stroke-width="1"/>')
    p.append(f'<path d="M{ax} {ay + ah} L{ax + aw} {ay}" stroke="{DIM}" stroke-width="1.2" '
             f'stroke-dasharray="4 3"/>')
    for i in range(46):
        u = (i * 0.6180339887) % 1.0
        v = min(max(u + 0.055 * math.sin(i * 2.399) + 0.02 * math.sin(i * 5.1), 0.02), 0.98)
        p.append(f'<circle cx="{ax + u * aw:.1f}" cy="{ay + ah - v * ah:.1f}" r="2.9" '
                 f'fill="{GREEN}" fill-opacity="0.72"/>')
    p.append(txt(ax + aw / 2, ay + ah + 18, "true C&#7496;", size=11, fill=MUTED, anchor="middle"))
    p.append(f'<text x="{ax - 14}" y="{ay + ah / 2}" font-family="{FONT}" font-size="11" '
             f'fill="{MUTED}" text-anchor="middle" '
             f'transform="rotate(-90 {ax - 14} {ay + ah / 2})">predicted C&#7496;</text>')

    # stage 4: numbers
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
            p.append(f'<path d="M{nx + 22} {y + 8} H{nx + nw - 22}" stroke="#1e2a36" stroke-width="1"/>')

    for i, s in enumerate([
        "A validation score used for checkpoint selection, on a random split rather than the published one.",
        "Trained at 2,048 points: evaluating at 5,000 drops R&#178; to about 0.59, which is why discretisation invariance matters.",
    ]):
        p.append(txt(600, 306 + i * 20, s, size=12.5, fill=DIM, anchor="middle"))
    p.append(txt(600, 366, "The wall-shear-stress head is far weaker. Both numbers belong in the "
                           "same sentence.", size=12.5, fill="#8a7550", anchor="middle"))

    return svg(w, h, "\n".join(p),
               "Learned aerodynamic surrogate: a car-shaped surface point cloud into a dynamic "
               "graph CNN, out to a drag coefficient, with a held-out parity plot and measured accuracy")


# ------------------------------------------------------------------- hero panel
def hero():
    """Name card with a phononic band structure, which is the actual subject matter.

    A generic gradient banner says nothing. A dispersion diagram with a bandgap says
    what the work is to anyone who recognises it, and looks deliberate to everyone else.
    """
    w, h = 1200, 320
    px0, px1 = 640.0, 1150.0
    py0, py1 = 56.0, 262.0
    gap_lo, gap_hi = 138.0, 174.0  # the bandgap, in screen coordinates

    p = [frame(w, h, "hbg", "#0d1117", "#0a1419")]

    # ---- plot frame and high-symmetry ticks
    p.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" '
             f'fill="#0e1620" stroke="#233240" stroke-width="1"/>')
    ticks = [("&#915;", 0.0), ("M", 0.34), ("K", 0.62), ("&#915;", 1.0)]
    for lab, f in ticks:
        x = px0 + f * (px1 - px0)
        p.append(f'<path d="M{x:.1f} {py0} V{py1}" stroke="#1d2a37" stroke-width="1"/>')
        p.append(txt(x, py1 + 17, lab, size=12, fill=DIM, weight="700", anchor="middle"))
    p.append(txt(px0 - 10, py0 + 10, "&#969;", size=13, fill=DIM, weight="700", anchor="end"))
    p.append(txt((px0 + px1) / 2, py1 + 36, "wavevector along the irreducible Brillouin zone",
                 size=11, fill="#5b6b7c", anchor="middle"))

    # ---- the gap
    p.append(f'<rect x="{px0 + 1}" y="{gap_lo}" width="{px1 - px0 - 2}" '
             f'height="{gap_hi - gap_lo}" fill="{AMBER}" fill-opacity="0.10"/>')
    for y in (gap_lo, gap_hi):
        p.append(f'<path d="M{px0 + 1} {y} H{px1 - 1}" stroke="{AMBER}" stroke-opacity="0.45" '
                 f'stroke-width="1.1" stroke-dasharray="5 4"/>')
    p.append(txt(px0 + 14, (gap_lo + gap_hi) / 2 + 4, "bandgap", size=11.5, fill=AMBER, weight="700"))

    # ---- dispersion branches, three below the gap and three above
    N = 56
    # Base levels must already sit on the correct side of the gap. Levels that do not
    # get clamped onto the gap edge, which collapses every branch onto one flat line.
    below = [(254.0, 20.0, 1.0), (228.0, 26.0, 1.6), (200.0, 20.0, 2.3)]
    above = [(130.0, 22.0, 1.3), (104.0, 24.0, 2.0), (78.0, 18.0, 2.9)]
    branches = []
    for base, amp, freq in below:
        pts = []
        for i in range(N + 1):
            t = i / N
            y = base - amp * math.sin(math.pi * t * freq) ** 2
            pts.append((px0 + t * (px1 - px0), min(max(y, gap_hi + 3), py1 - 4)))
        branches.append((pts, TEAL, 0.85))
    for base, amp, freq in above:
        pts = []
        for i in range(N + 1):
            t = i / N
            y = base - amp * math.sin(math.pi * t * freq + 0.6) ** 2
            pts.append((px0 + t * (px1 - px0), min(max(y, py0 + 4), gap_lo - 3)))
        branches.append((pts, BLUE, 0.85))

    for pts, col, op in branches:
        p.append(f'<path d="{poly_path(pts, close=False)}" fill="none" stroke="{col}" '
                 f'stroke-opacity="{op}" stroke-width="1.9"/>')

    # a marker riding the top acoustic branch
    ride = branches[2][0]
    p.append(f'<circle r="4.2" fill="{AMBER}"><animateMotion dur="7s" repeatCount="indefinite" '
             f'path="{poly_path(ride, close=False)}"/></circle>')

    # ---- identity block
    p.append(txt(58, 104, "Samarjith Biswas, Ph.D.", size=44, fill=INK, weight="700", spacing="-0.8"))
    p.append(f'<rect x="58" y="120" width="116" height="4" rx="2" fill="{TEAL}"/>')
    p.append(txt(58, 156, "Research Scientist III &#183; NewFoS Center, University of Arizona",
                 size=15.5, fill="#93b7c9", weight="600"))
    p.append(txt(58, 186, "Wave physics, acoustic metamaterials, and the machine learning",
                 size=14, fill="#7d8ea0"))
    p.append(txt(58, 206, "that makes simulation fast enough to design with.",
                 size=14, fill="#7d8ea0"))

    for i, (k, v) in enumerate((("hours &#8594; milliseconds", TEAL),
                                ("model &#8596; measurement, &#177;2%", GREEN),
                                ("published, patented, built", AMBER))):
        y = 240 + i * 22
        p.append(f'<circle cx="64" cy="{y - 4}" r="3" fill="{v}"/>')
        p.append(txt(78, y, k, size=13, fill="#8b9daf"))

    return svg(w, h, "\n".join(p),
               "Samarjith Biswas, Research Scientist III at the NewFoS Center, University of "
               "Arizona, with a phononic band structure showing a bandgap")


if __name__ == "__main__":
    for name, fn in (("hero", hero), ("aero", aero), ("surrogate", surrogate)):
        path = OUT / f"{name}.svg"
        path.write_text(fn(), encoding="utf-8")
        print(f"wrote {path.name}  {path.stat().st_size:,} bytes")
