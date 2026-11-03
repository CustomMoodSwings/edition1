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
| top die | The value die at the top right: 0 shows a numeral, 1 to 6 show pips. |
| top die color | White or black die. |
| reminder icon | Ticks on the "!" icon next to the top die. |
| lower die | The alternate value in the lower left: 1 to 6 is one die, 7 to 12 is two dice (a 6 and the rest), or none. The rules text flows around the dice. |
| lower die color | White or black dice. |
| rarity | Common, uncommon, rare or mythic. |
| rules text | Centered, vertically centered. Use bold and italic for the ability name and reminder text. For a die inside the text, use the Insert Symbol menu and pick a die. |
| art | Click the art box and choose an image; the art is clipped to the slanted frame. |
| collector number | Bottom left, for example `0020`. |
| artist | Bottom left, after the brush icon. |

### Not editable (baked into the images)

The set code `MSW`, the color word (for example "Black"), the brush icon, the copyright line and the "Edition 1 Custom" set symbol are part of the base image for each color, taken from the slices. If you want a different set code or symbol, edit the SVG, re-slice, and rerun the tools.

## Things to check first

I could not run MSE, so these are the likeliest places to need a small fix:

1. **Font sizes and vertical placement** of the name, collector number and artist boxes. They are positioned from the SVG's text baselines. If a line sits a few pixels off, change `top` or `height` in `mood-swings-edition1.mse-style/style` (or in `tools/write_files.py`).
2. **Inline dice scale.** The dice glyphs are drawn at about 30 px tall (symbol font `size: 28` over `image font size: 90`). Change `size` in the stylesheet's `symbol font` block to make them larger or smaller.
3. **Rules text masks.** The text flows around the lower dice and the set symbol using the three `text-mask-*.png` images. If text is clipped or overlaps the dice, look at those images (black is blocked) and the `mask:` line on `rules text`.
4. **Image paths in subfolders.** The stylesheet refers to `img/...`. If your version of MSE does not accept a folder in an image name, move the images up one level and drop the `img/` prefix.
5. **No letter spacing.** MSE has no letter-spacing setting, so the name and collector number are a little tighter or looser than the Inkscape versions.

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
