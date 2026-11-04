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
  frame color                the card color. There is no colorless frame yet, so colorless cards use the white
                             frame as a placeholder (the "White" word baked into that frame is wrong for them)
  top die                    base_value (0 to 12; 7 to 12 show two dice)
  lower die                  alt_value, or none
  top/lower die color        black when the alternate value applies while in play ("While in play - This mood's value
                             is N if ..."), otherwise white (a value that changes after playing, and ordinary cards)
  reminder icon              yes for an ongoing effect that is not only about this mood's own value (extra plays,
                             scoring, choices, effects on other moods), or one that lasts "for as long as". This rule
                             matches the printed icon on all 132 printed cards of the original game that were checked
  rules text                 the timing labels (To play this card, After playing this mood, While in play) in bold,
                             parenthetical reminder text in italics, and the alternate value written in the text as dice
  designed by                "Designed by X" when the card file names a designer
  collector number           provisional: by color (white, blue, black, red, green, colorless), rarity, then slot
  art, artist                left empty

The set is rebuilt from scratch each time, so edit the card files (not the set file) to change a card.
"""
import glob
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
MSE = os.path.dirname(HERE)
DEFAULT_OUT = os.path.join(MSE, "examples", "emotional-baggage.mse-set")
COLORS = ["white", "blue", "black", "red", "green", "colorless"]
RARITIES = ["common", "uncommon", "rare", "mythic"]


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


def markup(text, alt):
    t = " ".join(text.split())
    t = re.sub(r"(To play this card|After playing this mood|While in play) —", r"<b>\1</b> —", t)
    t = re.sub(r"\(([^()]*)\)", r"<i>(\1)</i>", t)
    if alt is not None:
        t = re.sub(r"(value (?:is|becomes) )%d\b" % alt, lambda m: m.group(1) + dice(alt), t)
    return t


def card_block(c, number):
    alt = c.get("alt_value")
    text = " ".join(c["rules_text"].split())
    in_play_alt = alt is not None and re.search(r"While in play — This mood's value is", text) is not None
    die_color = "black" if in_play_alt else "white"
    frame = "white" if c["color"] == "colorless" else c["color"]
    lines = ["card:",
             "\tname: " + re.sub(r"\s*\([^)]*\)$", "", c["name"]),
             "\tframe color: " + frame,
             "\ttop die: %d" % c["base_value"],
             "\ttop die color: " + die_color,
             "\treminder icon: " + ("yes" if has_reminder(text) else "no"),
             "\tlower die: " + ("none" if alt is None else str(alt)),
             "\tlower die color: " + die_color,
             "\trarity: " + c["rarity"],
             "\trules text:",
             "\t\t" + markup(text, alt),
             "\tcollector number: %04d" % number]
    if c.get("designer"):
        lines.append("\tdesigned by: Designed by " + c["designer"])
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
        return (COLORS.index(c["color"]), RARITIES.index(c["rarity"]), c.get("slot") or "~", c["name"])

    cards.sort(key=order)
    blocks = [card_block(c, i + 1) for i, c in enumerate(cards)]
    text = "mse version: 2.0.0\ngame: mood-swings\nstylesheet: edition1\nset info:\n\tset code: %s\n" % code
    text += "\n".join(blocks) + "\n"
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "set"), "w", encoding="utf8", newline="\n") as f:
        f.write(text)
    print("wrote %d cards to %s" % (len(cards), os.path.relpath(os.path.join(out, "set"), MSE)))


if __name__ == "__main__":
    main()
