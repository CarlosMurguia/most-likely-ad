---
name: most-likely-ad
description: Shows what the "most likely ad" looks like in a category before you make yours, then writes a counter-brief to make something that doesn't look like it. Use when someone is about to design or brief an ad (social, display, LinkedIn, Instagram) and wants to know what competitors' ads look like, which layouts, colors and typography the category repeats, or how to stand out from what's already running. Triggers on "what do ads in my category look like", "competitor ads", "make my ad different", "stand out from competitors", "ad library research", "category conventions", "counter-brief", "most likely ad".
---

# The most likely ad

Every category has an ad it keeps making: the same picture treatment, the words in the same place, the same palette, the same typeface. Readers recognize it before they read it, and an ad that announces what it is before anyone looks inside it rarely gets read. This skill finds that ad for a category, shows it, and writes a counter-brief.

It does **not** predict performance. Different is not automatically better; it is only less predictable. Say that in every report.

## What you need from the user

Ask only for what's missing, in one message:

1. **Category or competitors.** A category ("specialty coffee shops in the US") or 3–8 named competitors. Named competitors give a sharper answer.
2. **Platform.** Instagram/Facebook (Meta Ad Library) or LinkedIn (LinkedIn Ad Library). Default: Meta. Don't mix platforms in one tally (the platform's frame changes the layout; see `references/structure-taxonomy.md`).
3. **Country.** Default: United States.
4. **Optional:** their current ad or brand colors, to compare against the category.

## Workflow

### 1. Collect the ads
Follow `references/ad-libraries.md`. In short:
- Use the browser tools available in the session (e.g. Claude in Chrome) to open the public ad library pages, **at human pace, read-only**. Never log in on the user's behalf, never click anything that buys, boosts, follows or messages.
- If no browser tool is available, or the user prefers, ask them to paste screenshots or export images into a folder and work from those.
- Target **20–40 static image ads** from **at least 5 advertisers**, max 4 per advertiser, recent first. Skip video unless the user asks (code the first stable frame if so). Carousels: first card only.
- **Deduplicate by content, not by ad ID**: the same creative is often listed 5–10 times.
- Save images to a working folder named `<category>-<YYYY-MM-DD>/` and keep a `manifest.csv` (ad_id, advertiser, page_url, date_seen, file).

### 2. Code each ad
Open each image at full size and fill one row of `ads.csv` using `references/structure-taxonomy.md`. The core is **two decisions**:
- **picture**: `full-bleed` · `framed` · `none`
- **words**: vertical `top` · `middle` · `bottom` · `none`, and horizontal `centered` · `side`

Then the supporting attributes: background, type style, type levels, human scale, product, badge. Record facts, not judgments: never decide whether two ads "look alike". Similarity is computed later.

Extract colors with the script, not by eye:
```bash
python3 scripts/palette.py <folder-with-images> --out palettes.csv
```
Merge `palettes.csv` into `ads.csv` by file name (column `colors`).

### 3. Tally
```bash
python3 scripts/tally.py ads.csv --out tally.md
```
It reports: the most repeated structures and how far that is from chance, the modal value of every attribute, dominant color families, the structures and color families **nobody in the sample uses**, and a one-line description of the category's most likely ad.

### 4. Write the report
Use `templates/report.md`. Keep it short:
1. **The most likely ad**, in one sentence and as a structure sketch (grey box = picture, black bar = words).
2. **The numbers**: top 3 structures with counts out of N, chance comparison, palette and type conventions.
3. **Where nobody is**: unused structures, color families, type styles.
4. **Counter-brief**: three concrete directions, built with `references/counter-brief.md`. Each one changes **one or two** conventions on purpose and keeps the rest, so it still reads as the category.
5. **Limits**: sample size, date, platform, "this measures sameness, not effectiveness".

If the user shared their own ad, code it with the same rules and say plainly which conventions it shares with the category.

## Rules
- Report counts as "17 of 26", not just percentages. Never round a small sample into a big claim.
- Below 15 ads, say the result is indicative only.
- Don't invent ads, brands or numbers. If an ad couldn't be read, leave it out and say so.
- Don't reproduce competitors' creative in the report beyond small thumbnails or structure sketches; describe, don't copy.
- The counter-brief proposes directions, not finished ads.
