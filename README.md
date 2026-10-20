# The most likely ad

A Claude skill that shows you what the ads in your category look like before you make yours, then writes a counter-brief so yours doesn't look like them.

Every category has an ad it keeps making: the same picture treatment, the headline in the same place, the same palette, the same typeface. In one study of 246 ads across ten industries, 108 landed in the same two layouts, and in B2B SaaS 17 of 26 ads from 11 competing companies were built the same way. Nobody copied anybody. An ad built that predictably tells the reader what it is before they look inside it, so it often never gets read.

This skill makes that visible for your category, in about 20 minutes.

## What it does

1. **Collects** 20–40 recent static ads from your category or from competitors you name, from the public Meta Ad Library or LinkedIn Ad Library.
2. **Codes** each ad on a fixed set of layout decisions: how the picture sits in the frame, where the headline goes, background, typeface style, people, product, promo stickers. It extracts colors with a script, not by eye.
3. **Tallies** the most repeated structures and compares them with chance, and lists the structures, colors and type styles nobody in the sample uses.
4. **Reports** the category's most likely ad in one sentence, and writes a **counter-brief**: three directions, each breaking one or two conventions on purpose while keeping the ad recognizable as the category.

It measures **sameness, not effectiveness**. Different is not automatically better. It is less predictable.

See a real output: [`examples/coffee-shops-us-2026-10-13.md`](examples/coffee-shops-us-2026-10-13.md).

## Install

**Claude Code (plugin):**
```bash
/plugin marketplace add CarlosMurguia/most-likely-ad
/plugin install most-likely-ad@most-likely-ad
```

**Claude Code (manual):** copy `skills/most-likely-ad/` into `~/.claude/skills/`.

**Claude.ai / Claude Desktop:** zip the `skills/most-likely-ad/` folder and upload it under Settings → Capabilities → Skills.

**Requirements:** Python 3 and Pillow (`pip install pillow`) for the color script. A browser tool (such as Claude in Chrome) lets Claude read the ad libraries; without one, you can paste screenshots instead.

## Use

Just ask:
> "I'm about to make an Instagram ad for my coffee shop in Austin. What do coffee shop ads look like right now, and how do I make mine different?"

> "Show me the most likely ad for these competitors on LinkedIn: Airtable, Asana, Monday.com, ClickUp, Notion."

## A note on the ad libraries

Meta and LinkedIn publish their ad libraries for transparency, but their terms prohibit automated scraping, and there's no API for ordinary US commercial ads. The skill reads the libraries the way a person would: in your own browser, at a human pace, only the handful of ads it needs. If you'd rather, paste screenshots and it works from those.

## Where the method comes from

The taxonomy and the tally come from two essays by Carlos Murguía:
- [You already know what's coming](https://www.carlosmurguia.com/journal/you-already-know-whats-coming): 246 ads, two layout decisions, 108 in the same two structures.
- [The most likely ad](https://www.carlosmurguia.com/journal/ai-and-the-average): four AI image models, one brief, and the ad each one keeps handing back.

## Files
```
skills/most-likely-ad/
  SKILL.md                          workflow Claude follows
  references/structure-taxonomy.md  how to code an ad
  references/ad-libraries.md        how to collect ads, and the traps that bias a sample
  references/counter-brief.md       how to turn the tally into directions
  scripts/palette.py                dominant colors + aspect ratio per image
  scripts/tally.py                  structures, chance comparison, empty cells, one-line summary
  templates/report.md               report layout
examples/                           sample outputs
```

## License
To be decided.
