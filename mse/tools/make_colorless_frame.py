#!/usr/bin/env python3
"""Make the colorless frame (sliced/base-c.png) from the white frame.

The white frame is a warm mid gray. The colorless frame is the same artwork recolored to a darker slate
(frame color RGB 70, 76, 86), so it sits between white (a light gray) and black (a near-black purple) and does
not read as either, with the "White" word replaced by "Colorless". Because the geometry is the white frame's,
colorless cards use white's art opening and art mask.

    python3 mse/tools/make_colorless_frame.py

Needs Pillow and the Montserrat font (a stand-in for Gilroy, which the original words use). The result is a source
image like the other slices, so build_assets.py picks it up with the rest.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SLICED = os.path.join(ROOT, "sliced")

SLATE = (70, 76, 86)              # replaces the frame gray (149, 146, 135)
FRAME = (149, 146, 135)
LIGHT = (190, 197, 206)           # replaces the light cream (227, 228, 212) that shows around the art
CREAM = (227, 228, 212)
BORDER = (35, 33, 33)             # the dark line around the art, kept as it is
WORD_BOX = (141, 971, 196, 987)   # where the word "White" is, clear of the brush icon below it
WORD_LEFT, WORD_BASELINE, CAP_HEIGHT = 143, 985, 11   # the "W" starts at x 143, its letters end at row 984
WORD_COLOR = (255, 253, 252)
FONTS = ["/usr/share/fonts/truetype/montserrat/Montserrat-Medium.ttf",
         "/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf"]


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def recolor(p):
    """Warm gray pixels (the frame and its anti-aliased edges) become slate; neutral pixels are kept."""
    if p[0] - p[2] < 3:
        return p                       # white, the art placeholder gray, the border line, text: neutral
    y = lum(p)
    y_frame, y_cream = lum(FRAME), lum(CREAM)
    if y <= y_frame:
        return lerp(BORDER, SLATE, max(0.0, (y - lum(BORDER)) / (y_frame - lum(BORDER))))
    if y <= y_cream:
        return lerp(SLATE, LIGHT, (y - y_frame) / (y_cream - y_frame))
    return lerp(LIGHT, (255, 255, 255), min(1.0, (y - y_cream) / (255 - y_cream)))


def word_image(text):
    """The word as a white image with transparency, drawn at 8x and scaled down so the edges are smooth."""
    path = next(f for f in FONTS if os.path.exists(f))
    scale = 8
    size = round(CAP_HEIGHT / 0.7)     # Montserrat's capital letters are 0.7 of the font size tall
    font = ImageFont.truetype(path, size * scale)
    box = font.getbbox(text, anchor="ls")
    w, h = box[2] - box[0], -box[1] + font.getbbox("g", anchor="ls")[3]
    big = Image.new("L", (w + 8 * scale, h + 8 * scale), 0)
    ImageDraw.Draw(big).text((4 * scale - box[0], 4 * scale - box[1]), text, fill=255, font=font, anchor="ls")
    small = big.resize((big.width // scale, big.height // scale), Image.LANCZOS)
    out = Image.new("RGBA", small.size, WORD_COLOR + (0,))
    out.putalpha(small)
    return out, 4, -box[1] // scale + 4      # the image, and where the baseline's left end is inside it


def main():
    base = Image.open(os.path.join(SLICED, "base-w.png")).convert("RGBA")
    px = base.load()
    for y in range(base.height):
        for x in range(base.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = recolor((r, g, b)) + (a,)
    x0, y0, x1, y1 = WORD_BOX
    ImageDraw.Draw(base).rectangle((x0, y0, x1, y1), fill=SLATE + (255,))
    word, bx, by = word_image("Colorless")
    base.alpha_composite(word, (WORD_LEFT - bx, WORD_BASELINE - by))
    out = os.path.join(SLICED, "base-c.png")
    base.save(out)
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
