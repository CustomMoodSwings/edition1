# Mood Swings custom card templates

These are [Inkscape](https://inkscape.org) templates for creating custom [Mood Swings](https://magic.wizards.com/en/news/announcements/introducing-mood-swings) cards. They're very close matches to Wizards of the Coast's Edition 1 printing. They're intentionally imperfect: one, because it's very hard to get a perfect match, and two, because they aren't intended for producing counterfeit cards.

![Welcome card](assets/welcome.png)

## Installation/setup

You'll need some software and fonts to work with these templates.

Software:
- [Inkscape 1.4+](https://inkscape.org/release/)

Fonts:
- Beleren Small Caps Bold (card name)
- Plantin MT Pro (rules text)
- Gilroy Ultra-Bold (set symbol, rarity)
- Gotham (collation data)
- Francisco Serial (copyright notice)
- optional: Proxyglyph (if you need to edit the artist "brush" icon as text)

![Visual representation of font stack](assets/font-stack.png)

Obtaining fonts is left as an exercise for the reader.

## Working with a template

Each template has everything you need to reproduce any card of that color in Edition 1. You should hide and show layers or groups to use the values needed for your card. First, copy the desired template out of [src/](src/) to your project folder and open it in Inkscape.

### Top dice

The top dice are in layers called "top-dice-b" and "top-dice-w". `b` and `w` stand for black and white, respectively. Within each of those layers, there are seven faces: one through six pips plus a numeral zero, each represented as a group. To create a white dice, turn off the black layer (and vice versa). Within the color of dice you want, turn off all the faces you don't want, leaving just one visible. Below, we show examples of a white 4-pip face and a black 0-numeral face, along with what the layer control in Inkscape should look like.

| Dice face | Layer control |
|-----------|---------------|
| ![White 4-pip dice](assets/white4.png) | ![Layer control for white 4-pip dice](assets/white4-layers.png) |
| ![Black 0-numeral dice](assets/black0.png) | ![Layer control for black 0-numeral dice](assets/black0-layers.png) |

### "!" reminder icon

Cards which require the exclamation point reminder icon can toggle on the layer called `reminder-icon`.

### Bottom dice

Bottom dice are much like top dice, but there are four options. The layers are named `bottom-dice-<color><number>`, where `<color>` can be "b" or "w" and `<number>` can be "1" or "2" (since there are black and white variants of both one and two dice). Of course, if your card design requires no bottom dice, you can turn off all four layers.

### Rarity

The four existing rarities are available in the `rarity` layer. They can be toggled on and off to present common, uncommon, rare, and mythic.

### Art

In layer `artbox`, replace `art-placeholder` with your desired artwork.

### Text

There are multiple text-based fields to update. The most obvious is the card's name, `top > cardname`. Several fields in the `collation` layer such as `color`, `setcode`, `collector`, and `artist-name` can be changed.

Editing the card rules text is a bit more involved. Here are the steps:

1. Update the text in `text > textbox-main` with all the rules text required. This should included formatting like bold and italics. Leave gaps for any inline dice.
2. If the card has single or double dice in the lower left, slide the right edge of `textbox > dice-spacer` to roughly match its bounds.
3. Use Inkscape's ["Set Subtraction Frames"](https://wiki.inkscape.org/wiki/index.php/Release_notes/1.2#Text_Tool) feature to flow text around the dice and spacers. Make sure to select `rules-text`, `left-spacer`, `right-spacer`, `collation-spacer`, and `top-spacer` for sure, and `dice-spacer` if the card includes lower-left dice. From the **Text** menu, choose _Set Subtraction Frames_. Then resize the top and left/right spacers to center the text on the card text box.
4. Copy/paste and unhide any needed dice glyphs to fill in gaps in the card text.

## Alternative: quick use of rasterized images

If you don't want to deal with Inkscape and (most of) the font stuff, you can use the ["sliced" images](sliced/) in any raster image editor to quickly hack together some cards.

1. Start with a base image, like [sliced/base-b.png](base-b.png) for black. Layer a [rarity](sliced/rarity) on top of it, any [upper]() or [lower]() dice you need, and optionally the reminder icon. Then create your own text boxes for typing the card name and text.

You'll still need the Beleran Plantin fonts if you want accurate card names and rules text. These slices are currently produced manually, thus are a lot of effort and likely won't be updated very frequently.

## Alternative: Magic Set Editor

If you'd rather type card data into [Magic Set Editor 2](https://github.com/twanvl/MagicSetEditor2) and export cards from there, see [mse/](mse/). It is a game, a stylesheet and a small symbol font built from these templates. It has not been tested in MSE yet, and [mse/README.md](mse/README.md) lists what to check first.

## Fan content

These templates iare unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
