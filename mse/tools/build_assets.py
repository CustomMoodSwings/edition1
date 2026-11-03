#!/usr/bin/env python3
"""Build the derived images used by the Magic Set Editor template.

Run from anywhere:  python3 mse/tools/build_assets.py
Needs: Pillow and rsvg-convert (librsvg).

It reads the Inkscape template (src/00_w_blank.svg) and the sliced PNGs (sliced/) and writes the
images the MSE stylesheet and symbol font need:
  * the inline dice glyphs (from the SVG layer "dice-glyphs"),
  * the art mask (from the SVG path "art-placeholder"),
  * the three rules-text masks (no lower dice, one die, two dice), from the SVG "spacer" rectangles,
  * a blank transparent image,
and copies the base, dice, rarity and reminder slices into the stylesheet.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MSE = os.path.dirname(HERE)
REPO = os.path.dirname(MSE)
SVG = os.path.join(REPO, "src", "00_w_blank.svg")
COLOR_SVGS = {"white": "00_w_blank.svg", "blue": "01_u_blank.svg", "black": "02_b_blank.svg",
              "red": "03_r_blank.svg", "green": "04_g_blank.svg"}
SLICED = os.path.join(REPO, "sliced")
STYLE_IMG = os.path.join(MSE, "mood-swings-edition1.mse-style", "img")
FONT_DIR = os.path.join(MSE, "mood-swings-dice.mse-symbol-font")
CARD_WIDTH = 744
CARD_HEIGHT = 1040   # the SVG and slices are 1039 high; 1040 is a multiple of 4

NS = {
    "svg": "http://www.w3.org/2000/svg",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape",
}
INK = "{%s}" % NS["inkscape"]
SVGNS = "{%s}" % NS["svg"]
for prefix, uri in [("", NS["svg"]), ("inkscape", NS["inkscape"]),
                    ("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"),
                    ("xlink", "http://www.w3.org/1999/xlink"),
                    ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
                    ("cc", "http://creativecommons.org/ns#"),
                    ("dc", "http://purl.org/dc/elements/1.1/")]:
    ET.register_namespace(prefix, uri)


def label(e):
    return e.get(INK + "label") or e.get("id")


def set_display(e, shown):
    style = [s for s in e.get("style", "").split(";") if s and not s.startswith("display:")]
    style.append("display:inline" if shown else "display:none")
    e.set("style", ";".join(style))


def render(root, path, only_layers=None, show_children=None, zoom=1):
    """Render the SVG with only the named top-level layers visible. show_children maps a layer
    name to the set of child group labels to keep visible inside it."""
    for layer in root:
        if layer.tag == SVGNS + "g" and layer.get(INK + "groupmode") == "layer":
            keep = only_layers is not None and label(layer) in only_layers
            set_display(layer, keep)
            if keep and show_children and label(layer) in show_children:
                for child in layer:
                    if child.tag == SVGNS + "g":
                        set_display(child, label(child) in show_children[label(layer)])
    with tempfile.NamedTemporaryFile("wb", suffix=".svg", delete=False) as f:
        ET.ElementTree(root).write(f, encoding="utf-8", xml_declaration=True)
        tmp = f.name
    try:
        subprocess.run(["rsvg-convert", "-w", str(744 * zoom), "-h", str(1039 * zoom), "-o", path, tmp], check=True)
    finally:
        os.unlink(tmp)


def load_root(path=None):
    return ET.parse(path or SVG).getroot()


def find(root, name):
    for e in root.iter():
        if label(e) == name:
            return e
    raise KeyError(name)


def main():
    for tool in ("rsvg-convert",):
        if shutil.which(tool) is None:
            sys.exit("missing tool: " + tool)
    os.makedirs(STYLE_IMG, exist_ok=True)
    os.makedirs(FONT_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp()

    # 1. slices -> stylesheet images. The bases stay full-card; the overlays (dice, rarity, reminder)
    # are cropped to the union of their boxes, so each MSE field only covers its own small area.
    layout = {"card": {"width": CARD_WIDTH, "height": CARD_HEIGHT}}
    # The slices are 744 x 1039. The Unity client needs sizes that are a multiple of 4, so each base gets one
    # extra row at the bottom (a copy of the last row, which is the white margin around the card). Every
    # overlay is positioned from the top left, so nothing else moves.
    for c in "wubrg":
        base = Image.open(os.path.join(SLICED, f"base-{c}.png")).convert("RGBA")
        w, h = base.size
        padded = Image.new("RGBA", (w, CARD_HEIGHT), (0, 0, 0, 0))
        padded.paste(base, (0, 0))
        for extra in range(h, CARD_HEIGHT):
            padded.paste(base.crop((0, h - 1, w, h)), (0, extra))
        padded.save(os.path.join(STYLE_IMG, f"base-{c}.png"))

    def crop_group(sources, box_name):
        """sources: list of (source path, output name). Crop all to the union alpha box."""
        ims = [(Image.open(src).convert("RGBA"), name) for src, name in sources]
        boxes = [im.split()[3].getbbox() for im, _ in ims]
        x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
        x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
        for im, name in ims:
            im.crop((x0, y0, x1, y1)).save(os.path.join(STYLE_IMG, name))
        layout[box_name] = {"left": x0, "top": y0, "width": x1 - x0, "height": y1 - y0}
        print(box_name, layout[box_name])

    upper, lower = [], []
    for color, d in (("white", "w"), ("black", "b")):
        for n in range(0, 7):
            upper.append((os.path.join(SLICED, "upper-dice", color, f"ud{d}-{n}.png"), f"ud{d}-{n}.png"))
        for n in range(1, 13):
            lower.append((os.path.join(SLICED, "lower-dice", color, f"ld{d}-{n:02d}.png"), f"ld{d}-{n:02d}.png"))
    crop_group(upper, "upper-die")
    crop_group(lower, "lower-die")
    crop_group([(os.path.join(SLICED, "rarity", f"{r}.png"), f"rarity-{r}.png")
                for r in ("common", "uncommon", "rare", "mythic")], "rarity")
    crop_group([(os.path.join(SLICED, "reminder.png"), "reminder.png")], "reminder")

    # 2. blank transparent image
    Image.new("RGBA", (4, 4), (0, 0, 0, 0)).save(os.path.join(STYLE_IMG, "blank.png"))

    # 3. art masks, one per color. The art frame is tilted differently on the colors (white and blue are
    # nearly the same, black is tilted a little, red and green a lot), so every color gets its own box and
    # mask. The mask is read from the sliced frame itself: the art area is the flat gray (#999999)
    # placeholder, and the edge pixels are blended against the dark border around it. That makes the art
    # fit the frame image that is used, even if the slice differs slightly from the SVG.
    layout["art"] = {}
    GRAY = (153, 153, 153)
    for color, code in (("white", "w"), ("blue", "u"), ("black", "b"), ("red", "r"), ("green", "g")):
        base = Image.open(os.path.join(SLICED, f"base-{code}.png")).convert("RGB")
        w, h = base.size
        px = base.load()
        seed = Image.new("L", (w, h), 0)
        sp = seed.load()
        for y in range(h):
            for x in range(w):
                if px[x, y] == GRAY:
                    sp[x, y] = 255
        zone = seed.filter(ImageFilter.MaxFilter(5))          # the seed grown by 2 px
        zp = zone.load()
        ring = {}
        for y in range(h):
            for x in range(w):
                if zp[x, y] and not sp[x, y]:
                    ring[px[x, y]] = ring.get(px[x, y], 0) + 1
        dark = max(ring, key=ring.get)                          # the border colour just outside the art
        vx = [GRAY[i] - dark[i] for i in range(3)]
        norm = sum(v * v for v in vx)
        mask = Image.new("L", (w, h), 0)
        mp = mask.load()
        for y in range(h):
            for x in range(w):
                if sp[x, y]:
                    mp[x, y] = 255
                elif zp[x, y]:
                    t = sum((px[x, y][i] - dark[i]) * vx[i] for i in range(3)) / norm
                    mp[x, y] = int(round(255 * min(1.0, max(0.0, t))))
        bbox = mask.point(lambda v: 255 if v > 0 else 0).getbbox()
        left, top, right, bottom = bbox
        print("art region for", color, bbox, "border colour", dark)
        mask.crop(bbox).save(os.path.join(STYLE_IMG, f"art-mask-{color}.png"))
        layout["art"][color] = {"left": left, "top": top, "width": right - left, "height": bottom - top}

    # 4. rules text masks from the spacer rectangles (relative to textbox-main)
    root = load_root()
    main_rect = find(root, "textbox-main")
    mx, my = float(main_rect.get("x")), float(main_rect.get("y"))
    mw, mh = float(main_rect.get("width")), float(main_rect.get("height"))
    def rect(name):
        r = find(root, name)
        return (float(r.get("x")) - mx, float(r.get("y")) - my,
                float(r.get("width")), float(r.get("height")))
    W, H = round(mw), round(mh)
    print("rules text box: left %.2f top %.2f width %d height %d" % (mx, my, W, H))
    layout["rules-text"] = {"left": round(mx, 2), "top": round(my, 2), "width": W, "height": H}
    spacers = {n: rect(n) for n in ("top-spacer", "left-spacer", "right-spacer", "collation-spacer")}
    dice_spacer = rect("dice-spacer")
    # lower dice extents come from the sliced images (alpha bounding boxes)
    def dice_bbox(n):
        im = Image.open(os.path.join(SLICED, "lower-dice", "white", f"ldw-{n:02d}.png")).convert("RGBA")
        return im.split()[3].getbbox()
    single, double = dice_bbox(1), dice_bbox(7)
    print("single die bbox", single, "double dice bbox", double)

    def make_mask(dice):
        im = Image.new("L", (W, H), 255)
        d = ImageDraw.Draw(im)
        for x, y, w, h in spacers.values():
            d.rectangle([x, y, x + w, y + h], fill=0)
        if dice is not None:
            x0, y0, x1, y1 = dice
            # block from the left edge of the box, from just above the dice to the bottom
            d.rectangle([0, y0 - 8 - my, x1 + 12 - mx, H], fill=0)
        return im
    make_mask(None).save(os.path.join(STYLE_IMG, "text-mask-none.png"))
    make_mask(single).save(os.path.join(STYLE_IMG, "text-mask-single.png"))
    make_mask(double).save(os.path.join(STYLE_IMG, "text-mask-double.png"))

    # 5. inline dice glyphs from the dice-glyphs layer. Each glyph group sits at its own place in the
    # SVG, so render it alone at 4x, crop to its own box and centre it on a common canvas.
    ZOOM = 4
    crops = []
    for n in range(1, 7):
        root = load_root()
        out = os.path.join(tmp, f"glyph-{n}.png")
        render(root, out, only_layers={"dice-glyphs"}, show_children={"dice-glyphs": {f"dice-{n}"}}, zoom=ZOOM)
        im = Image.open(out).convert("RGBA")
        crops.append(im.crop(im.split()[3].getbbox()))
    cw = max(c.size[0] for c in crops) + 4
    ch = max(c.size[1] for c in crops) + 4
    for n, c in enumerate(crops, start=1):
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.paste(c, ((cw - c.size[0]) // 2, (ch - c.size[1]) // 2), c)
        canvas.save(os.path.join(FONT_DIR, f"die-{n}.png"))
    print("glyph size", (cw, ch), "(rendered at %dx)" % ZOOM)
    layout["glyph"] = {"width": cw, "height": ch, "zoom": ZOOM}
    with open(os.path.join(HERE, "layout.json"), "w") as f:
        json.dump(layout, f, indent=2, sort_keys=True)
        f.write("\n")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
