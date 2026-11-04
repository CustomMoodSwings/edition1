# Magic Set Editor template

A [Magic Set Editor 2](https://github.com/twanvl/MagicSetEditor2) (MSE) version of the Edition 1 card frames, built from the Inkscape templates in [`src/`](../src/) and the images in [`sliced/`](../sliced/). It lets you type card data into MSE and export finished cards, instead of editing layers by hand in Inkscape.

> **Status: not yet tried in MSE itself.** It was written from the MSE documentation and checked by compositing the layers and masks with a script, not by opening it in the program. Expect to tune a few numbers (see "Things to check first").

## What is in this folder

| Package | What it is |
|---|---|
| `mood-swings.mse-game/` | The game: the fields of a card (name, frame color, dice, rarity, rules text, art, ...). |
| `mood-swings-edition1.mse-style/` | The stylesheet: where each field goes on the 744 x 1040 card, plus the images (`img/`). |
| `mood-swings-dice.mse-symbol-font/` | A symbol font for the six dice that appear inside rules text. |
| `examples/edition1-sample.mse-set/` | A small sample set (Pacifism, Fear, Determination and a two-dice test card). |
| `tools/` | The scripts that generate everything above (see "Regenerating"). |

MSE finds a stylesheet by its package name: the game is `mood-swings`, so the stylesheet package has to be called `mood-swings-<name>`, here `mood-swings-edition1`.

## Install

1. Copy the three package folders (`mood-swings.mse-game`, `mood-swings-edition1.mse-style`, `mood-swings-dice.mse-symbol-font`) into MSE's `data` folder. On Windows that is usually `C:\Program Files\Magic Set Editor 2\data`, or `%APPDATA%\Magic Set Editor\data` if you can't write there.
2. Or run `python3 mse/tools/make_packages.py` to get zipped versions in `mse/dist/` (a package can be a folder or a zip) and copy those instead.
3. Install the fonts below, then start MSE and open `examples/edition1-sample.mse-set` (or choose New set > Mood Swings).

### Fonts

Same fonts as the Inkscape templates, except two that are no longer needed because they are already part of the base images:

- Beleren Small Caps Bold: card name and artist name
- Plantin MT Pro: rules text
- Gotham: collector number

Gilroy (rarity word) and Francisco Serial (copyright) are baked into the images, so you don't need them. Obtaining fonts is left to you, as in the main README.

## Using it

Each card has these fields:

| Field | What it does |
|---|---|
| name | Card name (Beleren Small Caps Bold, shrinks if it is long). |
| frame color | White, blue, black, red or green frame. |
| top die | The value die at the top right: 0 shows a numeral, 1 to 6 show pips. **7 to 12 show two dice** (a 6 and the rest), using the same pair artwork as the lower-left dice, right-aligned to where the single die ends. The reminder icon and the end of the name box move left by the extra width, so a long name shrinks sooner. The pair covers a little more of the top right of the art (about 37 px of height over the art opening), and the die is scaled by the same box as the lower dice (194 x 117). |
| top die color | White or black die (for two dice too). On the printed cards the top and lower dice are always the same color, and the color follows the kind of value: **black** for a value that applies while in play (Determination, Triumph, Serenity), **white** for one that changes after playing (Altruism, Cheer, Infatuation) and for ordinary cards with no lower die (almost all of them). |
| reminder icon | Ticks on the "!" icon next to the top die. |
| lower die | The alternate value in the lower left: 1 to 6 is one die, 7 to 12 is two dice (a 6 and the rest), or none. The rules text flows around the dice. |
| lower die color | White or black dice. Use the same color as the top die. |
| rarity | Common, uncommon, rare or mythic. |
| rules text | Centered, vertically centered. Use bold and italic for the ability name and reminder text. For a die inside the text, use the Insert Symbol menu and pick a die. |
| art | Click the art box and choose an image; the art is clipped to the slanted frame. The art box is the same size for every color, **585 x 452**, so you can make art at one size. The frames are tilted differently (white and blue about the same, black a little, red and green a lot), so the box moves a few pixels with the frame color to stay centered on each opening, and the mask changes with it. A few pixels of the picture, mostly at the corners, are cut off by the opening on the more tilted frames. |
| set symbol | The symbol on the tab at the lower right. Empty shows the original "Edition 1 Custom" symbol; click the box to choose your own image. It is drawn into a **80 x 80** square box (at left 622, top 886), so use a square image; the image is stretched to that size. The tab is the frame color, so a white symbol on a transparent background suits every frame (the default is one). Set per card, like the art. |
| set code | The set code at the bottom left (default `MSW`). Set it once in **Set Info** and every card follows it; type a different value on a card to override it. |
| collector number | Bottom left, for example `0020`. |
| designed by | Optional. A small italic line at the bottom of the rules text box, centered between the lower dice and the set symbol. Type the whole line, for example `Designed by Jane Doe`; leave it empty for none. When it is filled in the rules text keeps 24 px clear above it (`padding bottom`). Plantin italic 15 (shrinks to 10 if long). |
| artist | Bottom left, after the brush icon. |

### Not editable (baked into the images)

The color word (for example "Black"), the brush icon and the copyright line are part of the base image for each color, taken from the slices. If you want to change them, edit the SVG, re-slice, and rerun the tools. (The set code and the set symbol used to be in this list; both are now painted out of the base images and drawn from the `set code` and `set symbol` fields. `build_assets.py` cuts the original symbol out of the black frame as `img/set-symbol.png`, a white image with transparency, which is the default.)

## Things to check first

I could not run MSE, so these are the likeliest places to need a small fix:

1. **Font sizes and vertical placement** of the name, set code, collector number and artist boxes. They are positioned from the SVG's text baselines. If a line sits a few pixels off, change `top` or `height` in `mood-swings-edition1.mse-style/style` (or in `tools/write_files.py`).
2. **Inline dice scale.** The dice glyphs are drawn at about 30 px tall (symbol font `size: 28` over `image font size: 90`). Change `size` in the stylesheet's `symbol font` block to make them larger or smaller.
3. **Per-color art position.** The art box's `left` and `top` are scripted from the frame color (`case card.frame_color of ...`); the width and height are plain numbers. If MSE complains about those lines, the five positions are listed in `tools/layout.json` and can be written out as separate styles instead.
4. **Rules text masks.** The text flows around the lower dice and the set symbol using the three `text-mask-*.png` images. If text is clipped or overlaps the dice, look at those images (black is blocked) and the `mask:` line on `rules text`.
5. **Image paths in subfolders.** The stylesheet refers to `img/...`. If your version of MSE does not accept a folder in an image name, move the images up one level and drop the `img/` prefix.
6. **No letter spacing.** MSE has no letter-spacing setting, so the name and collector number are a little tighter or looser than the Inkscape versions.

## Not included

- No colorless frame (the Inkscape templates have five colors).
- No `themed/steampunk` variant.
- Printing and bleed are not set up. The card size is 744 x 1040 pixels at 300 dpi. The Inkscape template and the slices are 744 x 1039; the frame images here have one extra row at the bottom (a copy of the white margin) so both dimensions are multiples of 4, as the Unity client needs. Nothing else moves, because everything is positioned from the top left.

## Regenerating

The packages are generated, so after changing the SVG templates or the slices:

```bash
python3 mse/tools/build_assets.py    # images, masks, dice glyphs, layout.json
python3 mse/tools/write_files.py     # game, style, symbol-font and the sample set
python3 mse/tools/make_packages.py   # optional: zipped packages in mse/dist/
```

`build_assets.py` needs [Pillow](https://pypi.org/project/Pillow/) and `rsvg-convert` (from librsvg). The other two use only the standard library.

## Fan content

Same as the main README: unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
