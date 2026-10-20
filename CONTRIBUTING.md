# Contributing

Thanks for helping. Three kinds of contributions are especially useful.

## 1. A measured category

1. Run the skill on a category (20+ static ads, 5+ advertisers, one platform, one country).
2. Create a folder: `data/<platform>-<category>-<country>-<YYYY-MM-DD>/`, e.g. `data/instagram-coffee-shops-us-2026-10-13/`.
3. Add:
   - `ads.csv`, coded with the rules in [`structure-taxonomy.md`](skills/most-likely-ad/references/structure-taxonomy.md). Same columns, same values.
   - `manifest.csv`: `file,ad_id,advertiser,platform,country,page_url,date_seen,order_used`.
   - A short `NOTES.md`: how you picked the advertisers, the order the library served the ads in, anything you skipped and why.
4. **No images.** Don't commit other brands' creative. The manifest links back to the library so anyone can look.
5. Open a pull request titled `data: <platform> <category> <country> <date>`.

Quality bar: every row coded by looking at the ad at full size; the edge-case rules followed; no ad included twice (deduplicate by content, not by ad ID).

## 2. A second coding

Pick a sample in `data/`, code the same ads yourself without looking at the existing `ads.csv`, and open an issue titled `coding: <sample>` with a table of the ads and decisions where you disagree. If a rule caused the disagreement, suggest a sharper wording.

## 3. A result

If you tested a counter-brief direction against a conventional version, open an issue titled `result: <category>` with what you ran, where, for how long, what you measured and what happened. Results where the conventional ad won are just as welcome.

## Code and docs

Issues and pull requests are welcome for the scripts, the taxonomy, the card and the docs. Keep the scripts dependency-light (standard library, plus Pillow for images) so they run anywhere. Changes to the taxonomy should explain which real layout decision the new value corresponds to.

## Ground rules

- Collect ads the way a person would, in your own browser, at a human pace. Don't add bulk scrapers.
- This project measures sameness, not effectiveness. Don't phrase results as performance claims.
- Be kind in issues. Disagreeing about how to code an ad is the point; disagreeing about people isn't.
