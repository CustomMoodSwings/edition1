#!/usr/bin/env python3
"""Cut the art of the reprinted cards out of the printed card images of the original game.

    python3 mse/tools/extract_reprint_art.py /path/to/MoodSwings-Web

The printed images are web-static/img/cards/MSW/<number>-<name>.webp (744 x 1039, the same frames as sliced/).
For each reprint the art box of that card's frame color is cut out (585 x 452, the same box the MSE stylesheet uses),
so in MSE the art field shows it through the frame's mask exactly as it was printed. Pixels outside the slanted opening
are the frame's own border and are hidden by the mask. The top right corner of the box also holds the top die that was
printed over the art; the template draws the same die over it again, so it is not visible.

The result goes to mse/tools/reprint-art/<name>.png, with artists.json next to it. The artist names are read from
the printed footers (the line after the brush icon).
"""
import glob
import json
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "reprint-art")
LAYOUT = json.load(open(os.path.join(HERE, "layout.json")))

# card name -> (frame color, artist as printed in the footer)
REPRINTS = {
    "Pacifism": ("white", "Jesper Ejsing"),
    "Panic": ("blue", "Jesper Ejsing"),
    "Fear": ("blue", "Jesper Ejsing"),
    "Hate": ("black", "Karl Kopinski"),
    "Suspicion": ("black", "Matt Stewart"),
    "Shock": ("red", "Jon Foster"),
    "Zeal": ("red", "Volkan Baga"),
    "Compulsion": ("red", "Jesper Ejsing"),
    "Joy": ("green", "Rhonda Libbey"),
    "Nostalgia": ("green", "Zoltan Boros & Gabor Szikszai"),
    "Determination": ("green", "Arif Wijaya"),
}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cards = os.path.join(sys.argv[1], "web-static", "img", "cards", "MSW")
    w, h = LAYOUT["art"]["width"], LAYOUT["art"]["height"]
    os.makedirs(OUT, exist_ok=True)
    artists = {}
    for name, (color, artist) in REPRINTS.items():
        matches = glob.glob(os.path.join(cards, "*-%s.webp" % slug(name)))
        if len(matches) != 1:
            sys.exit("expected one printed image for %s, found %s" % (name, matches))
        box = LAYOUT["art"]["boxes"][color]
        img = Image.open(matches[0]).convert("RGB")
        crop = img.crop((box["left"], box["top"], box["left"] + w, box["top"] + h))
        crop.save(os.path.join(OUT, slug(name) + ".png"), optimize=True)
        artists[name] = artist
        print("cut the art of", name, "from", os.path.basename(matches[0]))
    with open(os.path.join(OUT, "artists.json"), "w", encoding="utf8") as f:
        json.dump(artists, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
