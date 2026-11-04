#!/usr/bin/env python3
"""Build an MSE set file with every card of the custom set (Emotional Baggage) from its card files.

    python3 mse/tools/make_custom_set.py /path/to/mood-swings-custom [output set folder]

It reads cards/*.yaml and design/skeleton.yaml from the mood-swings-custom repository (needs PyYAML) and writes
mse/examples/emotional-baggage.mse-set/set by default. Mapping of the card fields:

  which cards                only cards that claim a slot of the skeleton. A card file without a slot is a backup
                             candidate (for example the unrestricted Entitlement) and is left out until it is chosen
                             for play testing; the slotted one is the primary
  name, rarity               as written, except that a variant label in parentheses ("Entitlement (restricted)") is
                             dropped, because only the primary version is in the set
  frame color                the card color (colorless cards use the colorless frame, a darker slate version of
                             the white frame made by make_colorless_frame.py)
  top die                    base_value (0 to 12; 7 to 12 show two dice)
  lower die                  alt_value, or none
  top/lower die color        black when the card's own value is set or changed by a "While in play" ability that
                             starts with the value ("This mood's value is N if ...", "increases by N for each ...",
                             "is N more than ..."), otherwise white (a value that changes after playing, growth through
                             a trigger such as "at the start of each of your turns", and ordinary cards). The printed
                             cards of the original game follow this rule on every card checked
  reminder icon              yes for an ongoing effect that is not only about this mood's own value (extra plays,
                             scoring, choices, effects on other moods), or one that lasts "for as long as". This rule
                             matches the printed icon on all 132 printed cards of the original game that were checked
  rules text                 the timing labels (To play this card, After playing this mood, While in play) in bold,
                             parenthetical reminder text in italics, and every number in the text (point values, the
                             numbers on cards, "0 is even") as dice from the dice symbol font, as on the printed cards
  designed by                "Designed by X" when the card file names a designer; the original cards (designer Maro) read
                             "Original WOTC Design"
  collector number           provisional and unofficial, so the first digit is an X: X001 to X133, by color (colorless, white, blue,
                             black, red, green) and alphabetically by name within each color
  art, artist                for the 11 reprints, the art and artist of the printed card (cut out by
                             extract_reprint_art.py into tools/reprint-art/ and copied into the set folder);
                             left empty for the new cards

The set is rebuilt from scratch each time, so edit the card files (not the set file) to change a card.
"""
import glob
import json
import os
import re
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
MSE = os.path.dirname(HERE)
DEFAULT_OUT = os.path.join(MSE, "examples", "emotional-baggage.mse-set")
ART_DIR = os.path.join(HERE, "reprint-art")
COLORS = ["colorless", "white", "blue", "black", "red", "green"]


def dice(n):
    """The inline dice for a value: one die up to 6, otherwise a 6 and the rest (as on the printed cards)."""
    return "<sym>%d</sym>" % n if n <= 6 else "<sym>6</sym><sym>%d</sym>" % (n - 6)


def has_reminder(text):
    """Whether the card gets the "!" icon: a lasting effect that is not just a change to this mood's own value."""
    t = " ".join(text.split())
    if re.search(r"for as long as|no longer in play", t, re.I):
        return True
    for m in re.finditer(r"while in play\s*(?:—|,)\s*(.*?)(?:\.(?:\s|$))", t, re.I):
        rest = m.group(1)
        if re.match(r"(?:after scoring,\s*(?:if [^,]*,\s*)?(?:put )?)?this mood", rest, re.I):
            continue                       # only affects this mood (its value, or putting itself away)
        return True
    return False


def markup(text):
    t = " ".join(text.split())
    # every number in the rules text is a point value (or a number on a card), which the printed cards write as dice,
    # including 0 (a die with a 0 on it) and, for 7 to 12, two dice (a 6 and the rest)
    t = re.sub(r"(?<![\w<>/])(\d+)(?![\w<>])", lambda m: dice(int(m.group(1))), t)
    t = re.sub(r"(To play this card|After playing this mood|While in play) —", r"<b>\1</b> —", t)
    t = re.sub(r"\(([^()]*)\)", r"<i>(\1)</i>", t)
    return t


def display_name(c):
    """The name on the card: a variant label in parentheses is dropped."""
    return re.sub(r"\s*\([^)]*\)$", "", c["name"])


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def card_block(c, number, artists):
    alt = c.get("alt_value")
    text = " ".join(c["rules_text"].split())
    # as on the printed cards: black dice when the card's own value is set or changed by a "While in play" ability
    # that starts with the value (This mood's value is 6 if ..., increases by 1 for each ..., is 1 more than ...), white
    # for everything else, including growth through a trigger (At the start of each of your turns, ... permanently
    # increases) and a value that changes after playing
    in_play_value = re.search(r"While in play — This mood's value", text) is not None
    die_color = "black" if in_play_value else "white"
    frame = c["color"]
    lines = ["card:",
             "\tname: " + display_name(c),
             "\tframe color: " + frame,
             "\ttop die: %d" % c["base_value"],
             "\ttop die color: " + die_color,
             "\treminder icon: " + ("yes" if has_reminder(text) else "no"),
             "\tlower die: " + ("none" if alt is None else str(alt)),
             "\tlower die color: " + die_color,
             "\trarity: " + c["rarity"],
             "\trules text:",
             "\t\t" + markup(text),
             "\tcollector number: X%03d" % number]
    reprint = c.get("reprint_of")
    if reprint in artists and os.path.exists(os.path.join(ART_DIR, slug(reprint) + ".png")):
        lines.append("\tart: art-%s.png" % slug(reprint))
        lines.append("\tartist: " + artists[reprint])
    if c.get("designer"):
        credit = "Original WOTC Design" if c["designer"] == "Maro" else "Designed by " + c["designer"]
        lines.append("\tdesigned by: " + credit)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    repo = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    all_cards = [yaml.safe_load(open(f, encoding="utf8")) for f in sorted(glob.glob(os.path.join(repo, "cards", "*.yaml")))]
    cards = [c for c in all_cards if c.get("slot")]
    for c in all_cards:
        if not c.get("slot"):
            print("left out (no slot, backup candidate):", c["name"])
    skeleton = yaml.safe_load(open(os.path.join(repo, "design", "skeleton.yaml"), encoding="utf8"))
    code = skeleton["set"].get("code", "XEMB")

    def order(c):
        return (COLORS.index(c["color"]), display_name(c).lower())

    cards.sort(key=order)
    artists_file = os.path.join(ART_DIR, "artists.json")
    artists = json.load(open(artists_file, encoding="utf8")) if os.path.exists(artists_file) else {}
    blocks = [card_block(c, i + 1, artists) for i, c in enumerate(cards)]
    text = "mse version: 2.0.0\ngame: mood-swings\nstylesheet: edition1\nset info:\n\tset code: %s\n" % code
    text += "\n".join(blocks) + "\n"
    os.makedirs(out, exist_ok=True)
    for old in glob.glob(os.path.join(out, "art-*.png")):
        os.remove(old)
    for name in artists:
        src = os.path.join(ART_DIR, slug(name) + ".png")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(out, "art-%s.png" % slug(name)))
    with open(os.path.join(out, "set"), "w", encoding="utf8", newline="\n") as f:
        f.write(text)
    print("wrote %d cards to %s" % (len(cards), os.path.relpath(os.path.join(out, "set"), MSE)))


if __name__ == "__main__":
    main()
