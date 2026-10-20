# The card

`scripts/card.py` turns a tally into a 1080 × 1350 PNG (4:5, for LinkedIn and Instagram feeds). It needs only Python 3 and Pillow.

```bash
python3 scripts/card.py --tally tally.json --out card.png                    # the category
python3 scripts/card.py --tally tally.json --mine mine.json --out check.png  # Check my ad
```

Examples: [`examples/coffee-shops-card.png`](examples/coffee-shops-card.png), [`examples/coffee-shops-check.png`](examples/coffee-shops-check.png).

## The idea
**The category's ad, drawn empty: you recognize it with nothing in it.**

That is the essays' point. A predictable ad gets recognized before anyone reads it. The card proves it by drawing the most common layout as a blank, with a grey box where the picture goes and black bars where the headline goes. It has no photo, product or brand in it, and it still reads as "an ad". The ad nobody makes is drawn the same way, with a dashed edge.

## Decisions
- **One number leads.** The card picks the strongest pile-up, either the most common full structure or the most common headline position, and sets that count at 260 px: "12 of 25 put the headline at the top, centered." If two structures tie, it draws the headline position everyone shares and says the picture tie in the caption.
- **The sketch is drawn in the category's most common aspect** (9:16 for coffee, 1:1 for LinkedIn SaaS), so the shape is a finding too.
- **The only color on the card is the category's.** The card itself uses paper `#F4F3EF` and ink `#1A1918`, with no accent, so warm, cold or neon swatches never fight the layout. White, black and gray are left out of the swatches because almost every ad has them; pale swatches get a hairline edge.
- **"k of n" is the card's only unit:** the three conventions, the empty structure and the missing color all use it. Counts, never percentages, as in the reports.
- **Where nobody is:** the unused structure furthest from the dominant one, drawn dashed, plus the first color family nobody uses, shown as a dashed empty swatch.
- **Type:** Instrument Serif (title, number, sentences) and Instrument Sans (labels and counts), both SIL OFL 1.1. They are bundled in `assets/fonts/` from the official Google Fonts repository (`github.com/google/fonts`, `ofl/instrumentserif` and `ofl/instrumentsans`) with their licenses. If they are missing, the card falls back to Georgia/Arial (or DejaVu) and says so.
- **No third-party ads on the card**, only sketches and color. Nothing on it is copied from anyone's creative.
- **Check my ad:** the title is the result ("Your ad shares 6 of 7 conventions"). Your ad's sketch sits beside the category's, each with its colors, and a filled or hollow dot marks each convention. The last line says how many ads share your layout.

## Discarded
1. **A grid of thumbnails of the real ads.** It's the most persuasive version and would be copying other people's creative, and the card is meant to be posted. Out on copyright, and it puts the brands in front of the finding.
2. **A bar chart of the 14 structures.** It's accurate but has too much in it. At phone size it reads as "a chart", not "everyone makes the same ad". The bars stay in the report.
3. **A dark card with a red accent** (the carlosmurguia.com site palette). The accent fought the category swatches (coffee orange and red, SaaS pink), and a brand color on the card made it about the author, not the category.

## Limits
- The sketch shows two decisions (picture and headline position). Type, people and product are in the text, not in the drawing.
- If `mine.json` carries no aspect, both sketches use the category's most common aspect.
- Long category names wrap to a third title line and the sketch shrinks to fit. Tested with a 50-character name; beyond that, shorten it.
