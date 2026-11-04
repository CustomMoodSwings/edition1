#!/usr/bin/env python3
"""Make the colorless frame (sliced/base-c.png) by mixing parts of the five colored frames.

Every colored frame has its own art tilt, its own shapes behind the art, and its own grid in the text box, so the
colorless frame is not just the white frame in gray. It borrows one part from each of three frames and recolors
them to a dark slate (frame color RGB 70, 76, 86, between the light gray of white and the near-black of black):

    art box, its border and drop shadow:   green   (a strong tilt)
    shapes behind the art, text box edge:  red     (the pale wings and diagonal pieces)
    grid in the text box:                  blue

Change ART_FROM, SHAPES_FROM and GRID_FROM below to try another mix. The art box of the colorless frame is the one
of the frame it takes the art box from, so build_assets.py uses that frame's art mask and position for colorless cards.
The word "White" is replaced by "Colorless", set in Montserrat as a stand-in for the Gilroy of the original words.

    python3 mse/tools/make_colorless_frame.py

Needs Pillow, numpy, scipy and the Montserrat font. The result is a source image like the other slices.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SLICED = os.path.join(ROOT, "sliced")

ART_FROM, SHAPES_FROM, GRID_FROM = "g", "r", "u"

# per frame: the frame color, the darker tint and the main tint of the shapes behind the art
PALETTE = {
    "w": ((149, 146, 135), (200, 199, 189), (227, 228, 212)),
    "u": ((0, 143, 210), (131, 203, 213), (169, 223, 235)),
    "b": ((19, 1, 38), (168, 169, 172), (194, 196, 198)),
    "r": ((205, 60, 54), (232, 170, 164), (240, 202, 197)),
    "g": ((1, 146, 69), (160, 210, 189), (186, 220, 205)),
}
WHITE, BORDER, GRAY = (255, 255, 255), (35, 33, 33), (153, 153, 153)
SLATE, SLATE_DARK_TINT, SLATE_TINT = (70, 76, 86), (146, 153, 163), (190, 197, 206)
TARGET = [SLATE, SLATE_DARK_TINT, SLATE_TINT, WHITE]

WORD_BOX = (141, 971, 196, 987)    # where the color word is, clear of the brush icon below it
WORD_LEFT, WORD_BASELINE, CAP_HEIGHT = 143, 985, 11
WORD_COLOR = (255, 253, 252)
FONTS = ["/usr/share/fonts/truetype/montserrat/Montserrat-Medium.ttf",
         "/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf"]


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


def load(c):
    return np.asarray(Image.open(os.path.join(SLICED, "base-%s.png" % c)).convert("RGBA")).astype(float)


def along(rgb, pts):
    """For every pixel: where it falls along the polyline pts (0 to len-1) and how far it is from it."""
    best = np.full(rgb.shape[:2], 1e9)
    pos = np.zeros(rgb.shape[:2])
    for i in range(len(pts) - 1):
        a, b = np.array(pts[i], float), np.array(pts[i + 1], float)
        d = b - a
        t = np.clip(((rgb - a) @ d) / (d @ d), 0, 1)
        dist = np.linalg.norm(rgb - (a + t[..., None] * d), axis=-1)
        closer = dist < best
        best = np.where(closer, dist, best)
        pos = np.where(closer, i + t, pos)
    return pos, best


def point_at(pos, pts):
    pts = np.array(pts, float)
    i = np.clip(np.floor(pos).astype(int), 0, len(pts) - 2)
    t = (pos - i)[..., None]
    return pts[i] * (1 - t) + pts[i + 1] * t


def recolor(c):
    """The frame in slate: frame color, tints and their anti-aliased edges are mapped onto the slate tints.
    The art placeholder gray, the border and white are kept."""
    frame, dark, light = PALETTE[c]
    rgb = load(c)[..., :3]
    pos, dist = along(rgb, [frame, dark, light, WHITE])
    out = rgb.copy()
    keep = (rgb == GRAY).all(axis=-1)
    m = (dist < 14) & ~keep
    out[m] = point_at(pos, TARGET)[m]
    # the anti-aliased edge of the dark border against the frame color and against each tint
    done = m | keep
    for src, dst in ((frame, SLATE), (dark, SLATE_DARK_TINT), (light, SLATE_TINT)):
        pos2, dist2 = along(rgb, [BORDER, src])
        m2 = (dist2 < 18) & ~done
        out[m2] = point_at(pos2, [BORDER, dst])[m2]
        done |= m2
    return out, pos, dist


def assembly(c):
    """The art opening, its border and its drop shadow (the frame-colored sliver down and to the right)."""
    rgb = load(c)[..., :3]
    opening = ndimage.binary_opening((rgb == GRAY).all(axis=-1), structure=disk(2))
    core = ndimage.binary_dilation(opening, structure=disk(8))
    is_frame = np.abs(rgb - np.array(PALETTE[c][0])).sum(axis=-1) < 20
    swept = np.zeros_like(core)
    for k in range(1, 12):
        swept |= np.roll(np.roll(core, k, 0), k, 1)
    return core | (swept & is_frame)


def mix():
    art, art_pos, art_dist = recolor(ART_FROM)
    shapes, shapes_pos, shapes_dist = recolor(SHAPES_FROM)
    alpha = load(SHAPES_FROM)[..., 3]
    h, w = alpha.shape
    rows = np.arange(h)[:, None] * np.ones((1, w))
    gone = ndimage.binary_dilation(assembly(SHAPES_FROM), structure=disk(3))
    mine = assembly(ART_FROM)
    # the shapes frame without its own art box: those pixels are filled from the nearest frame or tint pixel
    background = (shapes_dist < 14) & (shapes_pos < 2.6) & ~gone
    idx = ndimage.distance_transform_edt(~background, return_distances=False, return_indices=True)
    out = shapes.copy()
    out[gone] = shapes[idx[0], idx[1]][gone]
    out[mine] = art[mine]                                # the art box of the other frame on top
    # the grid: inside the white text box of the shapes frame, drawn as in the grid frame
    grid = load(GRID_FROM)[..., :3]
    base = load(SHAPES_FROM)[..., :3]
    lum = lambda a: a @ np.array([.299, .587, .114])
    inside = (lum(base) >= 205) & (np.abs(base[..., 0] - base[..., 2]) < 6) & (rows >= 520) & ~mine
    light = (lum(grid) >= 205) & (np.abs(grid[..., 0] - grid[..., 2]) < 6)
    out[inside & light] = grid[inside & light]
    out[inside & ~light] = 255
    # a few anti-aliased edge pixels of the other frames' colors are left: make them the neutral slate
    odd = (out[..., 1] > out[..., 2] + 4) | (out[..., 0] > out[..., 2] + 4)
    v = lum(out)
    out[odd] = np.stack([v - 6, v, v + 6], axis=-1)[odd]
    return Image.fromarray(np.dstack([out, alpha]).round().clip(0, 255).astype(np.uint8), "RGBA")


def word_image(text):
    """The word as a white image with transparency, drawn at 8x and scaled down so the edges are smooth."""
    path = next(f for f in FONTS if os.path.exists(f))
    scale = 8
    font = ImageFont.truetype(path, round(CAP_HEIGHT / 0.7) * scale)   # capitals are 0.7 of the font size tall
    box = font.getbbox(text, anchor="ls")
    w, h = box[2] - box[0], -box[1] + font.getbbox("g", anchor="ls")[3]
    big = Image.new("L", (w + 8 * scale, h + 8 * scale), 0)
    ImageDraw.Draw(big).text((4 * scale - box[0], 4 * scale - box[1]), text, fill=255, font=font, anchor="ls")
    small = big.resize((big.width // scale, big.height // scale), Image.LANCZOS)
    out = Image.new("RGBA", small.size, WORD_COLOR + (0,))
    out.putalpha(small)
    return out, 4, -box[1] // scale + 4


def main():
    base = mix()
    ImageDraw.Draw(base).rectangle(WORD_BOX, fill=SLATE + (255,))
    word, bx, by = word_image("Colorless")
    base.alpha_composite(word, (WORD_LEFT - bx, WORD_BASELINE - by))
    out = os.path.join(SLICED, "base-c.png")
    base.save(out)
    print("wrote", os.path.relpath(out, ROOT), "(art box from %s, shapes from %s, grid from %s)"
          % (ART_FROM, SHAPES_FROM, GRID_FROM))


if __name__ == "__main__":
    main()
