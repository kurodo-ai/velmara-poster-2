#!/usr/bin/env python3
"""Paint the Velmara poster and save it as entry.png.

Velmara does not exist. It is a cliff town above a lagoon at dusk,
invented for this poster, and its one landmark is the Spiral Light —
a lighthouse built as a stack of rings, sweeping its beam across the
water. The picture is drawn with Pillow in the flat, few-colour style
of old screen-printed travel posters: banded sky and sea, serif
capitals for the town's name, a printed border, and a dusting of
grain over everything at the end.

Nothing here is random in the colloquial sense. A single seeded
generator drives every scattered element, in a fixed call order, so
running the script twice produces the same file byte for byte.
"""

import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Canvas: portrait poster, 864 x 1024.
PAGE_W, PAGE_H = 864, 1024
HORIZON = 640  # y where sky stops and water starts

# The whole picture uses this small set of inks.
PAPER = (245, 233, 201)      # warm cream: title, sails, starlight
SAND = (238, 214, 160)       # pale gold: small sail, rule under title
OCHRE = (232, 165, 88)       # amber the sky fades into at the horizon
ABYSS = (13, 52, 64)         # deepest teal, top of the sky
LAGOON = (23, 97, 110)       # mid teal of the sky
LAGOON_PALE = (52, 138, 148)
WATER = (18, 84, 99)         # base colour of the sea
WATER_PALE = (39, 120, 130)  # lighter wave bands and boat reflections
WATER_MID = (30, 104, 116)   # alternate wave band
ROCK = (16, 44, 54)          # shadowed cliff face
ROCK_PALE = (24, 62, 72)     # cliff where the light catches it
SHADOW = (10, 34, 42)        # near-black for silhouettes
SUN_CORE = (246, 219, 158)
SUN_HALO = (248, 226, 172)
GLITTER = (240, 205, 130, 150)
WINDOW_GLOW = (250, 205, 120)
RING_LIGHT = (233, 220, 182)
RING_DARK = (206, 188, 148)
RING_SEAM = (150, 132, 96)

TITLE_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# Sky colours from zenith to horizon: (height fraction, ink) pairs.
SKY_STOPS = [(0.0, ABYSS), (0.45, LAGOON), (0.75, (44, 118, 116)), (1.0, OCHRE)]

# One seeded generator for every scattered element. The order in
# which it is called below is part of the picture; do not reorder.
rng = random.Random(20261121)


def mix(ink_a, ink_b, fraction):
    """Blend two RGB inks; fraction 0 gives ink_a, 1 gives ink_b."""
    return tuple(
        int(ink_a[channel] + (ink_b[channel] - ink_a[channel]) * fraction)
        for channel in range(3)
    )


def paint_sky(canvas):
    """Fill the sky with horizontal rows lerped through four stops."""
    pen = ImageDraw.Draw(canvas)
    for row in range(HORIZON):
        t = row / HORIZON
        for (lo_t, lo_ink), (hi_t, hi_ink) in zip(SKY_STOPS, SKY_STOPS[1:]):
            if lo_t <= t <= hi_t:
                local = (t - lo_t) / (hi_t - lo_t)
                pen.line([(0, row), (PAGE_W, row)], fill=mix(lo_ink, hi_ink, local))
                break


def scatter_stars(pen):
    """Ninety faint stars, kept high in the sky and away from the edges."""
    for _ in range(90):
        x = rng.uniform(30, PAGE_W - 30)
        y = rng.uniform(150, 400) * rng.random()
        radius = rng.uniform(0.8, 2.0)
        alpha = int(rng.uniform(60, 170))
        pen.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=PAPER + (alpha,),
        )


def draw_sun(pen):
    """A big pale disc sitting low over the water, ringed once."""
    cx, cy, r = 330, 600, 150
    pen.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN_CORE)
    inset = 14
    pen.ellipse(
        [cx - r + inset, cy - r + inset, cx + r - inset, cy + r - inset],
        fill=SUN_HALO,
    )


def paint_sea(pen):
    """Flat water, wavy highlight bands, and the sun's glitter path."""
    pen.rectangle([0, HORIZON, PAGE_W, PAGE_H], fill=WATER)
    # Swaying bands of lighter water, drawn as sine-curved lines.
    for band, top in enumerate(range(660, PAGE_H - 60, 34)):
        ink = WATER_PALE if band % 2 == 0 else WATER_MID
        sway = 7 + (band % 3) * 3
        curve = [
            (x, top + sway * math.sin(x / 90.0 + band * 1.7))
            for x in range(0, PAGE_W + 16, 16)
        ]
        pen.line(curve, fill=ink, width=7)
    # Short bright strokes under the sun, widening as they come closer.
    for i in range(46):
        gx = 330 + rng.uniform(-95, 95) * (0.4 + i / 46)
        gy = 668 + i * 7.4
        half = rng.uniform(9, 34) * (0.5 + i / 40) / 2
        pen.line([(gx - half, gy), (gx + half, gy)], fill=GLITTER, width=3)


def draw_headland(pen):
    """The far shore on the left, a low silhouette across the bay."""
    pen.polygon(
        [(0, 640), (0, 560), (90, 520), (210, 545), (300, 600), (330, 640)],
        fill=ROCK_PALE,
    )


def build_cliff(pen):
    """The near cliff on the right, its lit top, and its windows."""
    face = [
        (520, 1024), (560, 800), (610, 690), (690, 640),
        (780, 655), (864, 700), (864, 1024),
    ]
    pen.polygon(face, fill=ROCK)
    lit_top = [
        (610, 690), (690, 640), (780, 655), (864, 700),
        (864, 760), (700, 720), (620, 760),
    ]
    pen.polygon(lit_top, fill=ROCK_PALE)
    # Tiny lit windows scattered over the cliff's terraces.
    for _ in range(26):
        wx = rng.uniform(640, 830)
        wy = rng.uniform(730, 980)
        pen.rectangle([wx, wy, wx + 5, wy + 7], fill=WINDOW_GLOW)


def build_spiral_light(pen):
    """Stack the lighthouse rings; return (centre x, lamp room top y)."""
    tower_x, ground_y = 724, 648
    widths = [64, 56, 48, 40, 33]  # each ring narrower than the one below
    ring_height = 26
    y = ground_y
    for level, width in enumerate(widths):
        y -= ring_height
        ink = RING_LIGHT if level % 2 == 0 else RING_DARK
        pen.rectangle(
            [tower_x - width / 2, y, tower_x + width / 2, y + ring_height - 3],
            fill=ink,
        )
        pen.rectangle(
            [tower_x - width / 2, y + ring_height - 3,
             tower_x + width / 2, y + ring_height],
            fill=RING_SEAM,
        )
    lamp_top = y - 30
    # Lamp room: dark housing, bright lamp, little peaked roof.
    pen.rectangle([tower_x - 15, lamp_top, tower_x + 15, y], fill=(60, 50, 38))
    pen.ellipse(
        [tower_x - 10, lamp_top + 4, tower_x + 10, lamp_top + 24],
        fill=(255, 224, 138),
    )
    pen.polygon(
        [(tower_x - 22, lamp_top + 2), (tower_x + 22, lamp_top + 2),
         (tower_x, lamp_top - 16)],
        fill=(38, 32, 26),
    )
    return tower_x, lamp_top


def add_light_effects(canvas, tower_x, lamp_top):
    """Composite the blurred beam and the lamp's glow over the scene."""
    beam_layer = Image.new("RGBA", (PAGE_W, PAGE_H), (0, 0, 0, 0))
    beam_pen = ImageDraw.Draw(beam_layer)
    beam_pen.polygon(
        [(tower_x - 6, lamp_top + 12), (60, 560), (96, 660)],
        fill=(255, 230, 150, 66),
    )
    beam_layer = beam_layer.filter(ImageFilter.GaussianBlur(6))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), beam_layer)

    glow_layer = Image.new("RGBA", (PAGE_W, PAGE_H), (0, 0, 0, 0))
    glow_pen = ImageDraw.Draw(glow_layer)
    glow_pen.ellipse(
        [tower_x - 34, lamp_top - 10, tower_x + 34, lamp_top + 38],
        fill=(255, 226, 140, 90),
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(10))
    return Image.alpha_composite(canvas, glow_layer)


def draw_boat(pen, bow_x, water_y, scale):
    """One small sailboat in silhouette, with a broken reflection."""
    s = scale
    pen.polygon(
        [(bow_x, water_y), (bow_x + 34 * s, water_y),
         (bow_x + 27 * s, water_y + 8 * s), (bow_x + 6 * s, water_y + 8 * s)],
        fill=SHADOW,
    )
    pen.line(
        [(bow_x + 16 * s, water_y), (bow_x + 16 * s, water_y - 40 * s)],
        fill=SHADOW, width=3,
    )
    pen.polygon(
        [(bow_x + 16 * s, water_y - 40 * s), (bow_x + 16 * s, water_y - 4 * s),
         (bow_x + 33 * s, water_y - 4 * s)],
        fill=PAPER,
    )
    pen.polygon(
        [(bow_x + 14 * s, water_y - 34 * s), (bow_x + 14 * s, water_y - 4 * s),
         (bow_x + 2 * s, water_y - 4 * s)],
        fill=SAND,
    )
    # Three short reflection strokes under the hull. Their offsets are
    # fixed numbers, not rng draws, so the seeded sequence is undisturbed.
    for k in range(3):
        ry = water_y + (14 + 9 * k) * s
        half = (30 - 7 * k) * s / 2
        pen.line(
            [(bow_x + 17 * s - half, ry), (bow_x + 17 * s + half, ry)],
            fill=WATER_PALE + (170,), width=2,
        )


def draw_bird(pen, cx, cy, scale):
    """A distant bird as two shallow arcs, like a child's drawing."""
    s = scale
    pen.arc([cx - 14 * s, cy - 6 * s, cx, cy + 6 * s], 300, 30, fill=SHADOW, width=3)
    pen.arc([cx, cy - 6 * s, cx + 14 * s, cy + 6 * s], 150, 240, fill=SHADOW, width=3)


def tracked_text(pen, centre_x, top_y, word, font, ink, tracking):
    """Draw a word letter by letter with even space between glyphs."""
    glyph_widths = [pen.textlength(ch, font=font) for ch in word]
    total = sum(glyph_widths) + tracking * (len(word) - 1)
    pen_x = centre_x - total / 2
    for ch, w in zip(word, glyph_widths):
        pen.text((pen_x, top_y), ch, font=font, fill=ink)
        pen_x += w + tracking
    return total


def add_title_and_frame(pen):
    """The town's name in the sky, a rule beneath it, and the border."""
    name_font = ImageFont.truetype(TITLE_FONT, 104)
    tracked_text(pen, PAGE_W / 2, 56, "VELMARA", name_font, PAPER, 16)
    pen.line(
        [(PAGE_W / 2 - 218, 196), (PAGE_W / 2 + 218, 196)], fill=SAND, width=3
    )
    pen.ellipse([PAGE_W / 2 - 6, 190, PAGE_W / 2 + 6, 202], fill=SAND)
    # Printed border: a cream keyline outside, a hairline of ink inside.
    pen.rectangle([18, 18, PAGE_W - 18, PAGE_H - 18], outline=PAPER, width=5)
    pen.rectangle(
        [34, 34, PAGE_W - 34, PAGE_H - 34], outline=SHADOW + (200,), width=2
    )


def finish_print(canvas):
    """Flatten, add grain, reduce to a print palette, and save."""
    flat = canvas.convert("RGB")
    # Grey noise from the same seeded generator, lightly blended in.
    noise = Image.frombytes("L", (PAGE_W, PAGE_H), rng.randbytes(PAGE_W * PAGE_H))
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    printed = Image.blend(flat, noise_rgb, 0.05)
    printed = printed.quantize(colors=192, method=Image.MEDIANCUT)
    printed.save("entry.png", optimize=True)
    print("wrote entry.png")


def render():
    canvas = Image.new("RGB", (PAGE_W, PAGE_H), ABYSS)
    paint_sky(canvas)
    pen = ImageDraw.Draw(canvas, "RGBA")

    scatter_stars(pen)
    draw_sun(pen)
    draw_headland(pen)
    paint_sea(pen)
    build_cliff(pen)
    tower_x, lamp_top = build_spiral_light(pen)

    canvas = add_light_effects(canvas, tower_x, lamp_top)
    pen = ImageDraw.Draw(canvas, "RGBA")

    # Foreground rock on the left frames the whole view.
    pen.polygon(
        [(0, 1024), (0, 760), (70, 800), (130, 880), (170, 1024)], fill=SHADOW
    )
    draw_boat(pen, 215, 800, 1.0)
    draw_boat(pen, 420, 872, 0.7)
    for bird_x, bird_y, bird_s in [(180, 300, 1.0), (250, 262, 0.75),
                                   (540, 226, 0.85), (610, 286, 0.6)]:
        draw_bird(pen, bird_x, bird_y, bird_s)

    add_title_and_frame(pen)
    finish_print(canvas)


if __name__ == "__main__":
    render()
