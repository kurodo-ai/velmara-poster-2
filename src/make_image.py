#!/usr/bin/env python3
"""Generate the Velmara travel poster (entry.png) with Pillow.

Velmara is an invented cliff city above a dusk lagoon, known for the
Spiral Light: a shell-tower lighthouse whose beam sweeps the water.
Retro travel-poster style: flat colour bands, a limited teal/amber
palette, serif capitals for the name, a printed frame and grain.
Deterministic: fixed seed, no external assets.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 864, 1024
random.seed(20261121)

CREAM = (245, 233, 201)
PALE = (238, 214, 160)
AMBER = (232, 165, 88)
DEEP = (13, 52, 64)
TEAL = (23, 97, 110)
TEAL_LT = (52, 138, 148)
SEA = (18, 84, 99)
SEA_LT = (39, 120, 130)
CLIFF = (16, 44, 54)
CLIFF_LT = (24, 62, 72)
INK = (10, 34, 42)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(img):
    d = ImageDraw.Draw(img)
    horizon = 640
    stops = [(0.0, DEEP), (0.45, TEAL), (0.75, (44, 118, 116)), (1.0, AMBER)]
    for y in range(horizon):
        t = y / horizon
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                tt = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
                d.line([(0, y), (W, y)], fill=lerp(stops[i][1], stops[i + 1][1], tt))
                break


def draw_spaced_text(d, cx, y, text, font, fill, spacing):
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + spacing
    return total


def main():
    img = Image.new("RGB", (W, H), DEEP)
    sky_gradient(img)
    d = ImageDraw.Draw(img, "RGBA")

    # stars in the upper sky
    for _ in range(90):
        x = random.uniform(30, W - 30)
        y = random.uniform(150, 400) * random.random()
        r = random.uniform(0.8, 2.0)
        a = int(random.uniform(60, 170))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(245, 233, 201, a))

    # the great pale sun, low over the lagoon
    sun_cx, sun_cy, sun_r = 330, 600, 150
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=(246, 219, 158))
    d.ellipse([sun_cx - sun_r + 14, sun_cy - sun_r + 14, sun_cx + sun_r - 14, sun_cy + sun_r - 14],
              fill=(248, 226, 172))

    # distant headland, left
    d.polygon([(0, 640), (0, 560), (90, 520), (210, 545), (300, 600), (330, 640)], fill=CLIFF_LT)

    # sea: banded water below the horizon
    d.rectangle([0, 640, W, H], fill=SEA)
    for i, yy in enumerate(range(660, H - 60, 34)):
        col = SEA_LT if i % 2 == 0 else (30, 104, 116)
        amp = 7 + (i % 3) * 3
        pts = []
        for x in range(0, W + 16, 16):
            pts.append((x, yy + amp * math.sin(x / 90.0 + i * 1.7)))
        d.line(pts, fill=col, width=7)
    # sun path glitter on the water
    for i in range(46):
        gx = sun_cx + random.uniform(-95, 95) * (0.4 + i / 46)
        gy = 668 + i * 7.4
        gw = random.uniform(9, 34) * (0.5 + i / 40)
        d.line([(gx - gw / 2, gy), (gx + gw / 2, gy)], fill=(240, 205, 130, 150), width=3)

    # right cliff with the Spiral Light tower
    cliff = [(520, 1024), (560, 800), (610, 690), (690, 640), (780, 655), (864, 700),
             (864, 1024)]
    d.polygon(cliff, fill=CLIFF)
    d.polygon([(610, 690), (690, 640), (780, 655), (864, 700), (864, 760), (700, 720), (620, 760)],
              fill=CLIFF_LT)
    # terraced houses on the cliff: lit windows
    for _ in range(26):
        x = random.uniform(640, 830)
        y = random.uniform(730, 980)
        d.rectangle([x, y, x + 5, y + 7], fill=(250, 205, 120))

    # the Spiral Light: tapering stacked rings, lamp room, beam
    tx, ty = 724, 648           # tower base centre on the clifftop
    ring_w = [64, 56, 48, 40, 33]
    ring_h = 26
    y = ty
    for i, wdt in enumerate(ring_w):
        y -= ring_h
        col = (233, 220, 182) if i % 2 == 0 else (206, 188, 148)
        d.rectangle([tx - wdt / 2, y, tx + wdt / 2, y + ring_h - 3], fill=col)
        d.rectangle([tx - wdt / 2, y + ring_h - 3, tx + wdt / 2, y + ring_h], fill=(150, 132, 96))
    lamp_y = y - 30
    d.rectangle([tx - 15, lamp_y, tx + 15, y], fill=(60, 50, 38))
    d.ellipse([tx - 10, lamp_y + 4, tx + 10, lamp_y + 24], fill=(255, 224, 138))
    d.polygon([(tx - 22, lamp_y + 2), (tx + 22, lamp_y + 2), (tx, lamp_y - 16)], fill=(38, 32, 26))
    # light beam sweeping left over the water
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(tx - 6, lamp_y + 12), (60, 560), (96, 660)], fill=(255, 230, 150, 66))
    beam = beam.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), beam)
    d = ImageDraw.Draw(img, "RGBA")
    # glow at the lamp
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([tx - 34, lamp_y - 10, tx + 34, lamp_y + 38], fill=(255, 226, 140, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img, "RGBA")

    # left foreground cliff, framing the scene
    d.polygon([(0, 1024), (0, 760), (70, 800), (130, 880), (170, 1024)], fill=INK)
    # two small sailboats
    for bx, by, s in [(215, 800, 1.0), (420, 872, 0.7)]:
        d.polygon([(bx, by), (bx + 34 * s, by), (bx + 27 * s, by + 8 * s), (bx + 6 * s, by + 8 * s)], fill=INK)
        d.line([(bx + 16 * s, by), (bx + 16 * s, by - 40 * s)], fill=INK, width=3)
        d.polygon([(bx + 16 * s, by - 40 * s), (bx + 16 * s, by - 4 * s), (bx + 33 * s, by - 4 * s)], fill=CREAM)
        d.polygon([(bx + 14 * s, by - 34 * s), (bx + 14 * s, by - 4 * s), (bx + 2 * s, by - 4 * s)], fill=PALE)
        # a short broken reflection under each hull (fixed offsets, no
        # randomness, so the seeded draws that follow stay untouched)
        for k in range(3):
            ry = by + (14 + 9 * k) * s
            rw = (30 - 7 * k) * s
            d.line([(bx + 17 * s - rw / 2, ry), (bx + 17 * s + rw / 2, ry)],
                   fill=(39, 120, 130, 170), width=2)
    # birds
    for bx, by, s in [(180, 300, 1.0), (250, 262, 0.75), (540, 226, 0.85), (610, 286, 0.6)]:
        d.arc([bx - 14 * s, by - 6 * s, bx, by + 6 * s], 300, 30, fill=INK, width=3)
        d.arc([bx, by - 6 * s, bx + 14 * s, by + 6 * s], 150, 240, fill=INK, width=3)

    # the name, set into the sky
    name_font = ImageFont.truetype(SERIF_BOLD, 104)
    draw_spaced_text(d, W / 2, 56, "VELMARA", name_font, CREAM, 16)
    # a thin rule under the name
    d.line([(W / 2 - 218, 196), (W / 2 + 218, 196)], fill=PALE, width=3)
    d.ellipse([W / 2 - 6, 190, W / 2 + 6, 202], fill=PALE)

    # printed frame: outer cream keyline + inner dark line
    d.rectangle([18, 18, W - 18, H - 18], outline=CREAM, width=5)
    d.rectangle([34, 34, W - 34, H - 34], outline=(10, 34, 42, 200), width=2)

    img = img.convert("RGB")
    # grain: a whisper of grey noise blended over the print
    noise = Image.frombytes("L", (W, H), random.randbytes(W * H))
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, noise_rgb, 0.05)
    # a limited print palette keeps the file small and the colours flat
    img = img.quantize(colors=192, method=Image.MEDIANCUT)
    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
