# Coding an ad: the taxonomy

Every variable is a **decision someone made when building the ad**, and its values are the real options of that decision on a layout table. You record facts about each ad. You never judge whether two ads "look alike": that is computed afterwards from the values.

## The core: two decisions → one structure

These two are made before anyone picks a photo or writes a line. They are what makes an ad recognizable at a glance.

| Column | Decision | Values |
|---|---|---|
| `picture` | How the picture sits in the frame | `full-bleed` (picture reaches all four edges, words laid over it) · `framed` (picture sits inside the frame, with a margin, band or panel around it) · `none` (type only, no picture) |
| `words_v` | Where the headline sits vertically | `top` · `middle` · `bottom` · `none` (no headline inside the frame) |
| `words_h` | Where the headline sits horizontally | `centered` · `side` (left- or right-aligned block) · leave empty if `words_v` = `none` |

**Structure** = `picture` + `words_v` + `words_h`. That gives 7 word positions × 3 picture treatments = 21 possible structures (14 if no ad in the sample is type-only). The finding is never "there are few structures"; it is **how far the pile-up is from chance** (`scripts/tally.py` computes it).

### What counts as the headline
- The headline is the phrase that makes a claim or an offer. **A logo or wordmark is not a headline.** A price alone is not a headline.
- If there are two text blocks, the headline is the largest one.
- Vertical position = where the center of the headline block falls in thirds of the frame.
- `centered` = the block's center is within the middle fifth of the width; otherwise `side`.

## Supporting attributes

| Column | Decision | Values |
|---|---|---|
| `aspect` | What gets uploaded | `1:1` · `4:5` · `9:16` · `1.91:1` · `other` (filled by `scripts/palette.py`) |
| `image_kind` | What gets commissioned | `photo` · `illustration` · `flat-graphic` · `none` |
| `product` | Whether the product appears, and how | `absent` · `held` · `in-use` · `isolated` (cut out or on a plain background) |
| `human` | Human scale | `none` · `incidental` · `half-body` · `face` (head covers ≥ 1/3 of the frame) |
| `background` | What's behind | `plain` · `gradient` · `photo-environment` · `cutout-on-color` |
| `type_style` | Headline typeface family | `sans` · `serif` · `condensed` · `display` (heavy/decorative) · `script` · `mixed` |
| `type_case` | Headline case | `upper` · `sentence` · `title` · `lower` |
| `type_levels` | Visible type sizes | `1` · `2` · `3` · `4+` |
| `badge` | Commercial sticker (discount, "new", stars, price burst) | `yes` · `no` |
| `colors` | Dominant colors | filled by `scripts/palette.py`, semicolon-separated hex, largest first |

## Edge cases (decided in advance)

| Case | Rule |
|---|---|
| A hand holds the product, no face | `human` = `none`; `product` = `held` |
| Carousel or dynamic ad | Code the first card only |
| Video | First stable frame (skip a title card shorter than ~0.5 s) |
| Plain vs gradient | More than one tone family behind the subject = `gradient` |
| Isolated product with a cast shadow | Still `isolated` |
| Two products | Code the larger one |
| No picture at all | `picture` = `none`; `product`, `human`, `background` = `n/a` |
| Words only in the platform's post text, none in the creative | `words_v` = `none` |
| Product or person cut out on a flat color field | `picture` = `framed` (the picture is the cut-out, surrounded by color); `background` = `cutout-on-color` |
| Product shown in a styled scene (on a table, crate, leaves) | `product` = `in-use`; a plain backdrop with a few props stays `isolated` |
| Screenshot of an app/UI as the picture | `image_kind` = `flat-graphic`; `picture` by how it sits in the frame |

## ads.csv

One row per ad:
```
file,advertiser,picture,words_v,words_h,aspect,image_kind,product,human,background,type_style,type_case,type_levels,badge,colors
```

## Why not mix platforms
On Instagram the creative is a closed canvas fully authored by the advertiser. On LinkedIn the interface dominates the unit and pictures are usually framed. Mixing them confuses "how alike the advertisers are" with "how different the two canvases are". Run one tally per platform.
