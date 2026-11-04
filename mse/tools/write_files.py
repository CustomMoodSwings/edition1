#!/usr/bin/env python3
"""Write the Magic Set Editor data files (game, stylesheet, symbol font, sample set).

Run build_assets.py first (it writes layout.json and the images). Then:
    python3 mse/tools/write_files.py

MSE data files need exactly one TAB per indent level. The text below is written with two spaces
per level and converted to tabs when it is saved, so it is easy to edit here.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MSE = os.path.dirname(HERE)
LAYOUT = json.load(open(os.path.join(HERE, "layout.json")))

GAME_DIR = os.path.join(MSE, "mood-swings.mse-game")
STYLE_DIR = os.path.join(MSE, "mood-swings-edition1.mse-style")
FONT_DIR = os.path.join(MSE, "mood-swings-dice.mse-symbol-font")
SAMPLE_DIR = os.path.join(MSE, "examples", "edition1-sample.mse-set")


def write(path, text):
    """Save text with two-space indents converted to tabs."""
    out = []
    for line in text.strip("\n").split("\n"):
        stripped = line.lstrip(" ")
        indent = (len(line) - len(stripped)) // 2
        out.append("\t" * indent + stripped)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def box(name, z, extra=""):
    b = LAYOUT[name]
    return (f"    left: {b['left']}\n    top: {b['top']}\n    width: {b['width']}\n"
            f"    height: {b['height']}\n    z index: {z}\n{extra}")


# --------------------------------------------------------------------------- game
frame_choices = "\n".join(f"  choice: {c}" for c in ("white", "blue", "black", "red", "green"))
die_choices = "\n".join(f"  choice: {n}" for n in range(0, 7))
lower_choices = "  choice: none\n" + "\n".join(f"  choice: {n}" for n in range(1, 13))

game = f"""
mse version: 2.0.0
short name: Mood Swings
full name: Mood Swings
position hint: 100

set field:
  type: text
  name: set code
  description: The set code printed at the bottom left of every card, for example MSW
  default: "MSW"
default set style:
  set code:
    left: 10
    top: 10
    width: 120
    height: 24
    alignment: middle left
    font:
      name: Arial
      size: 12
      color: rgb(0,0,0)

card field:
  type: text
  name: name
  description: The name of the card
  identifying: true
  card list visible: true
  card list column: 1
  card list width: 220
  show statistics: false
card field:
  type: choice
  name: frame color
  description: The color of the card frame
{frame_choices}
  initial: white
  card list visible: true
  card list column: 2
  card list width: 70
  choice colors cardlist:
    white: rgb(235,233,222)
    blue: rgb(160,200,235)
    black: rgb(150,140,160)
    red: rgb(235,170,160)
    green: rgb(165,215,170)
card field:
  type: choice
  name: top die
  description: The die in the top right corner, 0 shows a numeral and 1 to 6 show pips
{die_choices}
  initial: 1
  card list visible: true
  card list column: 3
  card list width: 50
card field:
  type: choice
  name: top die color
  description: White or black die. Printed cards use the same color for the top and lower dice - black for a value that applies while in play, white for one that changes after playing
  choice: white
  choice: black
  initial: white
  show statistics: false
card field:
  type: boolean
  name: reminder icon
  description: The "!" reminder icon next to the top die
  show statistics: false
card field:
  type: choice
  name: lower die
  description: The alternate value shown by the lower left dice, 1 to 6 is one die and 7 to 12 is two dice
{lower_choices}
  initial: none
  show statistics: false
card field:
  type: choice
  name: lower die color
  description: White or black dice. Use the same color as the top die
  choice: white
  choice: black
  initial: white
  show statistics: false
card field:
  type: choice
  name: rarity
  description: The rarity word at the bottom right
  choice: common
  choice: uncommon
  choice: rare
  choice: mythic
  initial: common
  card list visible: true
  card list column: 4
  card list width: 80
card field:
  type: text
  name: rules text
  description: The rules text. Use the Insert Symbol menu for dice inside the text.
  multi line: true
  show statistics: false
card field:
  type: image
  name: art
  description: The card art
  show statistics: false
card field:
  type: image
  name: set symbol
  description: The set symbol on the tab at the lower right. Leave it empty for the Edition 1 Custom symbol, or choose a square image (a white symbol on a transparent background works on every frame color).
  show statistics: false
card field:
  type: text
  name: set code
  description: The set code at the bottom left. It follows the Set Info value unless you type something here.
  default: set.set_code
  show statistics: false
card field:
  type: text
  name: collector number
  description: The collector number at the bottom left, for example 0020
  show statistics: false
card field:
  type: text
  name: artist
  description: The artist name at the bottom left
  show statistics: false
"""
write(os.path.join(GAME_DIR, "game"), game)

# --------------------------------------------------------------------------- stylesheet
TOP_DIE_IMAGE = ('{ "img/ud" + (if card.top_die_color == "black" then "b" else "w") + "-" + input + ".png" }')
LOWER_DIE_IMAGE = ('{ if input == "none" then "img/blank.png" else '
                   '"img/ld" + (if card.lower_die_color == "black" then "b" else "w") + "-" + '
                   '(if to_int(input) < 10 then "0" else "") + input + ".png" }')
def art_prop(key):
    """A scripted style value that depends on the frame color (each opening sits in a different place)."""
    colors = ("white", "blue", "black", "red", "green")
    boxes = LAYOUT["art"]["boxes"]
    cases = ", ".join(f"{c}: {boxes[c][key]}" for c in colors)
    return "{ case card.frame_color of " + cases + ", else: " + str(boxes["white"][key]) + " }"


ART_BLOCK = (f"    left: {art_prop('left')}\n    top: {art_prop('top')}\n"
             f"    width: {LAYOUT['art']['width']}\n    height: {LAYOUT['art']['height']}\n    z index: 20\n"
             '    mask: { "img/art-mask-" + card.frame_color + ".png" }')
TEXT_MASK = ('{ if card.lower_die == "none" then "img/text-mask-none.png" '
             'else if to_int(card.lower_die) <= 6 then "img/text-mask-single.png" '
             'else "img/text-mask-double.png" }')

style = f"""
mse version: 2.0.0
game: mood-swings
short name: Edition 1
full name: Mood Swings Edition 1 card frame
position hint: 1
card width: {LAYOUT['card']['width']}
card height: {LAYOUT['card']['height']}
card dpi: 300
card background: rgb(255,255,255)

card style:
  frame color:
    left: 0
    top: 0
    width: {LAYOUT['card']['width']}
    height: {LAYOUT['card']['height']}
    z index: 10
    render style: image
    choice images:
      white: img/base-w.png
      blue: img/base-u.png
      black: img/base-b.png
      red: img/base-r.png
      green: img/base-g.png
  art:
{ART_BLOCK}
  top die:
{box('upper-die', 30)}    render style: image
    image: {TOP_DIE_IMAGE}
  reminder icon:
{box('reminder', 30)}    render style: image
    choice images:
      yes: img/reminder.png
      no: img/blank.png
  lower die:
{box('lower-die', 30)}    render style: image
    image: {LOWER_DIE_IMAGE}
  rarity:
{box('rarity', 30)}    render style: image
    choice images:
      common: img/rarity-common.png
      uncommon: img/rarity-uncommon.png
      rare: img/rarity-rare.png
      mythic: img/rarity-mythic.png
  set symbol:
{box('set-symbol', 35)}    default: img/set-symbol.png
  name:
    left: 57
    top: 44
    width: 468
    height: 80
    z index: 40
    alignment: middle left
    font:
      name: Beleren Small Caps
      size: 50
      weight: bold
      color: rgb(255,253,252)
      scale down to: 30
  rules text:
    left: {LAYOUT['rules-text']['left']}
    top: {LAYOUT['rules-text']['top']}
    width: {LAYOUT['rules-text']['width']}
    height: {LAYOUT['rules-text']['height']}
    z index: 40
    alignment: middle center
    font:
      name: Plantin MT Pro
      size: 21
      color: rgb(45,45,45)
      scale down to: 14
    symbol font:
      name: mood-swings-dice
      size: 28
      alignment: middle center
    mask: {TEXT_MASK}
  set code:
    left: 48.4
    top: 989
    width: 90
    height: 20
    z index: 40
    alignment: middle left
    font:
      name: Gotham
      size: 12
      color: rgb(255,253,252)
  collector number:
    left: 47.7
    top: 968
    width: 90
    height: 22
    z index: 40
    alignment: middle left
    font:
      name: Gotham
      size: 12
      color: rgb(255,253,252)
  artist:
    left: 164.85
    top: 985
    width: 280
    height: 24
    z index: 40
    alignment: middle left
    font:
      name: Beleren Small Caps
      size: 14
      weight: bold
      color: rgb(255,253,252)
"""
write(os.path.join(STYLE_DIR, "style"), style)

# --------------------------------------------------------------------------- symbol font
glyph_symbols = "\n".join(f"symbol:\n  code: {n}\n  image: die-{n}.png" for n in range(1, 7))
menu_items = "\n".join(f"  item:\n    name: {n}\n    label: Die with {n} pip{'s' if n > 1 else ''}"
                       for n in range(1, 7))
font = f"""
mse version: 2.0.0
short name: Mood Swings dice
full name: Mood Swings inline dice
image font size: 90
horizontal space: 1
{glyph_symbols}
insert symbol menu:
{menu_items}
"""
write(os.path.join(FONT_DIR, "symbol-font"), font)

# --------------------------------------------------------------------------- sample set
def card(name, frame, top, top_color, reminder, lower, lower_color, rarity, rules, number, artist):
    return f"""card:
  name: {name}
  frame color: {frame}
  top die: {top}
  top die color: {top_color}
  reminder icon: {reminder}
  lower die: {lower}
  lower die color: {lower_color}
  rarity: {rarity}
  rules text:
    {rules}
  collector number: {number}
  artist: {artist}"""

DIE6 = "<sym>6</sym>"
cards = [
    card("Pacifism", "white", 1, "white", "yes", "none", "white", "common",
         "<b>After playing this mood</b> — Choose up to two players. For each chosen player, suppress one of their moods. "
         "It remains suppressed for as long as you have this mood. "
         "<i>(While suppressed, that mood has a value of 0. Turn it sideways to keep track.)</i>",
         "0020", "Jesper Ejsing"),
    card("Fear", "blue", 0, "white", "no", "none", "white", "common",
         "<b>After playing this mood</b> — You may put another one of your moods into your hand. "
         "You may play an additional mood this turn.",
         "0038", "Jesper Ejsing"),
    card("Determination", "green", 3, "black", "no", 6, "black", "common",
         "<b>While in play</b> — This mood's value is " + DIE6 + " if there are three or more moods that share a color. "
         "<i>(Moods are cards in play.)</i>",
         "0112", "Arif Wijaya"),
    card("Test Card With Two Dice", "red", 3, "white", "no", 9, "white", "mythic",
         "<b>After playing this mood</b> — You may put two of your other moods into the discard pile. "
         "If you do, this mood's value becomes 9.",
         "0000", "Nobody"),
]
sample = "mse version: 2.0.0\ngame: mood-swings\nstylesheet: edition1\nset info:\n\tset code: MSW\n" + "\n".join(cards) + "\n"
write(os.path.join(SAMPLE_DIR, "set"), sample)
print("wrote game, style, symbol-font and sample set")
