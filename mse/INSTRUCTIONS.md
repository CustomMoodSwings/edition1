# Mood Swings card template for Magic Set Editor 2 (Edition 1 frames)

This zip has everything needed to type card data into [Magic Set Editor 2](https://github.com/twanvl/MagicSetEditor2) (MSE) and export finished Mood Swings cards (744 x 1040 pixels, 300 dpi).

> Status: not yet tried in MSE itself by the author. If a text line sits a few pixels off, or a font size looks wrong, see "Tuning" at the end and report what you see.

## What is in the zip

| Item | What it is |
|---|---|
| `mood-swings.mse-game/` | The game: the fields of a card. |
| `mood-swings-edition1.mse-style/` | The stylesheet: where each field goes on the card, plus the frame images. |
| `mood-swings-dice.mse-symbol-font/` | A symbol font for the six dice used inside rules text. |
| `examples/edition1-sample.mse-set/` | A small sample set (Pacifism, Fear, Determination, a two-dice card and FOMO). |
| `examples/emotional-baggage.mse-set/` | The whole custom set, Emotional Baggage (code XEMB): the 133 slotted cards of the community design (backup candidates are left out until they are chosen for play testing). There is no art or artist yet, the 8 colorless cards use the white frame as a placeholder (there is no colorless frame yet, so the color word on them is wrong), and the collector numbers are provisional and start with an X (X001 to X133) to mark them as unofficial. |

## 1. Install

1. Unzip this file.
2. Copy the three folders ending in `.mse-game`, `.mse-style` and `.mse-symbol-font` into MSE's `data` folder:
   - Windows: `C:\Program Files\Magic Set Editor 2\data`, or `%APPDATA%\Magic Set Editor\data` if you cannot write to Program Files.
   - Keep each folder as it is; do not put them inside another folder.
3. Install the fonts below. They are not included, so you have to get them yourself:
   - **Beleren Small Caps Bold**: card name and artist name
   - **Plantin MT Pro**: rules text and the "designed by" line
   - **Gotham**: collector number and set code
4. Start MSE. Choose **File > Open** and open `examples/edition1-sample.mse-set`, or choose **File > New** and pick **Mood Swings**.

## 2. Fill in a card

Click a card in the list, then edit its fields in the panel next to the card. Click the card picture to edit the text on the card itself.

| Field | What it does |
|---|---|
| name | Card name. It shrinks if it is long. |
| frame color | White, blue, black, red or green. |
| top die | The value at the top right. 0 shows a numeral, 1 to 6 show pips on one die, and **7 to 12 show two dice** (a 6 plus the rest); two dice push the name and the "!" icon to the left. |
| top die color | White or black. Use **black** for a value that applies while in play (for example Determination), and **white** for a value that changes after playing and for ordinary cards. |
| reminder icon | Ticks on the "!" icon next to the top die. |
| lower die | The alternate value at the lower left: 1 to 6 is one die, 7 to 12 is two dice, or none. The rules text flows around the dice. |
| lower die color | White or black. Use the same color as the top die. |
| rarity | Common, uncommon, rare or mythic. |
| rules text | Centered. Use bold for the ability timing ("After playing this mood") and italic for reminder text. To put a die inside the text, use the **Insert Symbol** menu and pick a die. |
| designed by | Optional. A small italic line at the bottom of the rules text box. Type the whole line, for example `Designed by Jane Doe`. Leave it empty for none. |
| art | Click the art box and choose an image. It is clipped to the slanted frame. The art box is **585 x 452** for every color, so make art at that size. A few pixels at the corners are cut off by the opening on the more tilted frames (red and green most). |
| set symbol | The symbol on the tab at the lower right. Empty shows the "Edition 1 Custom" symbol. To use your own, click the box and choose an image: use a **square** image (it is drawn into an 80 x 80 box and stretched to fit), ideally white on a transparent background so it shows on every frame color. |
| set code | The code at the bottom left (default `XEMB`, the working set code of the custom set Emotional Baggage; change it in Set Info). Set it once in **Set > Set Info** and every card follows it; type something on a card to override it. |
| collector number | Bottom left, for example `0020`. |
| artist | Bottom left, after the brush icon. |

Not editable (part of the frame images): the color word, the brush icon and the copyright line.

## 3. Export

- **File > Export > Images...** writes every card as an image file.
- **File > Export > HTML...** and **File > Print** are also available. Printing and bleed are not set up in this template.
- The card size is 744 x 1040 pixels (a multiple of 4, as some game clients need).

## Tuning

If something is a few pixels off, the numbers are in `mood-swings-edition1.mse-style/style` (a text file; indent with TAB characters only):

- Positions and sizes of the name, set code, collector number, artist, "designed by" and rules text boxes (`left`, `top`, `width`, `height`, `font: size`).
- The size of dice inside the rules text: `size` in the `symbol font` block of `rules text` (default 28).
- If your version of MSE does not accept images in a subfolder, move the files out of `img/` and remove the `img/` prefix in the style file.

Source, build scripts and the Inkscape templates this was made from are in the repository: https://github.com/jceddy/edition1

## Fan content

Unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
