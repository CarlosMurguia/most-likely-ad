# Writing the counter-brief

The counter-brief turns the tally into three directions that don't look like the category's most likely ad. It is a brief, not a design: it says what to decide differently and why, and leaves the execution to the designer.

## Principles

1. **Different is not better.** The tally measures sameness, not effectiveness. Never promise performance. The argument is narrower: an ad built the way its category always builds it tells the reader what it is before they look inside it, so it often isn't read at all.
2. **Break one or two conventions, keep the rest.** An ad that breaks everything stops reading as the category, and people can't place it. Each direction names the convention it breaks and the ones it deliberately keeps.
3. **Start with the structure.** Color and type are easier to change and easier to copy. A different structure (where the picture sits, where the words go) is the change a reader notices first.
4. **Use the empty cells.** The strongest candidates are structures, color families or type styles that **nobody in the sample uses**, listed by `tally.py` under "Where nobody is". An empty cell isn't automatically good: check it isn't empty for a practical reason (e.g. words at the bottom get covered by the platform's UI on some placements).
5. **Respect the brand.** If the user shared brand colors or type, directions should use them. Breaking the category's palette is fine; breaking the brand's is not the goal.

## Format for each direction

```
Direction 1 — <short name>
Breaks:   <the convention, with its count: "words top-centered (17 of 26)">
Keeps:    <what still makes it read as the category>
Do:       <2–3 concrete instructions: structure, color, type>
Watch:    <the practical risk: legibility, platform crop, brand fit>
```

## Typical moves

| If the category converges on… | Try |
|---|---|
| Words top-centered over a full-bleed photo | Words on the side in a column; or no words in the frame and let the post text carry them; or type-only frame |
| Framed product on a plain background | Product in use, full-bleed; or no product, just the outcome |
| Faces filling a third of the frame | No person, or a person at incidental scale; or hands only |
| One color family (e.g. warm browns in coffee) | A family nobody uses, kept within the brand palette; or one high-contrast accent on neutral |
| Sans-serif, 3+ type sizes, badges | One type size; serif or condensed; no sticker |
| Every ad says the offer first | Lead with a claim or a question; offer in the post text |

## Limits to state in the report
- Sample: N ads, M advertisers, platform, country, date seen.
- The library shows what is running, ordered in ways that favor big spenders (see `ad-libraries.md`).
- The counts describe this sample on this day; they will drift.
