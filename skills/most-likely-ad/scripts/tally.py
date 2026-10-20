#!/usr/bin/env python3
"""
tally.py: find the category's most likely ad from coded ads.

Usage:
    python3 tally.py ads.csv [--out tally.md] [--seed 1]

ads.csv columns (see references/structure-taxonomy.md):
    file, advertiser, picture, words_v, words_h, aspect, image_kind, product, human,
    background, type_style, type_case, type_levels, badge, colors
`colors` can be filled from palette.py (semicolon-separated hex). Standard library only.
"""
import argparse
import colorsys
import csv
import random
from collections import Counter

PICTURE = ["full-bleed", "framed", "none"]
WORDS = ["top centered", "top side", "middle centered", "middle side",
         "bottom centered", "bottom side", "no words"]
FAMILIES = ["red", "orange", "yellow", "brown", "green", "teal", "blue", "purple", "pink",
            "black", "white", "gray"]
ATTRS = ["aspect", "image_kind", "product", "human", "background", "type_style",
         "type_case", "type_levels", "badge"]
TYPE_STYLES = ["sans", "serif", "condensed", "display", "script", "mixed"]


def family(hexcode):
    h = hexcode.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    if l < 0.15:
        return "black"
    if l > 0.93 or (l > 0.88 and s < 0.35):
        return "white"
    if s < 0.18:
        return "gray"
    hue = hh * 360
    if l < 0.42 and hue < 50 and s < 0.85:
        return "brown"
    for limit, name in [(15, "red"), (45, "orange"), (70, "yellow"), (165, "green"),
                        (200, "teal"), (255, "blue"), (290, "purple"), (345, "pink")]:
        if hue < limit:
            return name
    return "red"


def words(row):
    v = (row.get("words_v") or "").strip().lower()
    if v in ("", "none", "n/a"):
        return "no words"
    hz = (row.get("words_h") or "centered").strip().lower()
    return f"{v} {hz}"


def structure(row):
    return f"{(row.get('picture') or '').strip().lower()} · {words(row)}"


def expected_max(n, cells, sims, rng, top=1):
    """Average size of the `top` fullest cells if n ads were spread at random over `cells` boxes."""
    tot = 0
    for _ in range(sims):
        c = Counter(rng.randrange(cells) for _ in range(n))
        tot += sum(sorted(c.values(), reverse=True)[:top])
    return tot / sims


def pct(k, n):
    return f"{round(100 * k / n)}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", default="tally.md")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = random.Random(a.seed)

    rows = [r for r in csv.DictReader(open(a.csv, newline="")) if (r.get("picture") or "").strip()]
    n = len(rows)
    if n == 0:
        raise SystemExit("No coded rows found.")
    advertisers = len({r.get("advertiser", "") for r in rows})

    used_pictures = sorted({(r["picture"] or "").strip().lower() for r in rows})
    pictures_in_play = [p for p in PICTURE if p in used_pictures] or used_pictures
    cells = len(pictures_in_play) * len(WORDS)
    sc = Counter(structure(r) for r in rows)
    top = sc.most_common(3)
    e1 = expected_max(n, cells, 2000, rng, 1)
    e2 = expected_max(n, cells, 2000, rng, 2)
    top2 = sum(c for _, c in sc.most_common(2))
    all_structs = [f"{p} · {w}" for p in pictures_in_play for w in WORDS]
    unused = [s for s in all_structs if s not in sc]

    out = []
    w = out.append
    w(f"# The most likely ad\n\nSample: **{n} ads from {advertisers} advertisers.**")
    if n < 15:
        w("\n> Fewer than 15 ads: treat this as indicative only.")

    # Structure
    w("\n## Structure (picture × where the words sit)\n")
    w(f"Possible structures with the picture treatments seen here: **{cells}**. Used: **{len(sc)}**.\n")
    w("| Structure | Ads | Share |\n|---|---|---|")
    for s, c in sc.most_common():
        w(f"| {s} | {c} of {n} | {pct(c, n)} |")
    w(f"\n**Concentration vs chance.** Spread {n} ads over {cells} structures at random and the fullest "
      f"one would hold about **{e1:.1f}**; here it holds **{top[0][1]}**. The two fullest would hold about "
      f"**{e2:.1f}** together; here they hold **{top2}**.")

    # Words alone
    wc = Counter(words(r) for r in rows)
    w("\n## Where the words go (all picture treatments)\n")
    w(" · ".join(f"{k}: {v} of {n}" for k, v in wc.most_common()))

    # Attributes
    w("\n## Conventions\n\n| Decision | Most common | Share | Next |\n|---|---|---|---|")
    modal = {}
    for at in ATTRS:
        vals = Counter((r.get(at) or "").strip().lower() for r in rows if (r.get(at) or "").strip()
                       and (r.get(at) or "").strip().lower() != "n/a")
        if not vals:
            continue
        (m, mc), *rest = vals.most_common()
        modal[at] = (m, mc, sum(vals.values()))
        nxt = ", ".join(f"{k} ({v})" for k, v in rest[:2]) or "—"
        w(f"| {at} | {m} | {mc} of {sum(vals.values())} | {nxt} |")

    # Color
    fam_ads = Counter()
    lead = Counter()
    have_color = 0
    for r in rows:
        cols = [c for c in (r.get("colors") or "").split(";") if c.strip()]
        if not cols:
            continue
        have_color += 1
        fams = {family(c) for c in cols}
        fam_ads.update(fams)
        chromatic = [family(c) for c in cols if family(c) not in ("black", "white", "gray")]
        if chromatic:
            lead[chromatic[0]] += 1
    if have_color:
        w(f"\n## Color ({have_color} ads with palettes)\n")
        w("Ads containing each color family: " +
          " · ".join(f"{k} {v}" for k, v in fam_ads.most_common()))
        if lead:
            w("\nLeading (largest) chromatic color: " + " · ".join(f"{k} {v}" for k, v in lead.most_common()))
        unused_fam = [f for f in FAMILIES if f not in fam_ads]
        rare_fam = [f for f in FAMILIES if 0 < fam_ads.get(f, 0) <= max(1, have_color // 10)]
    else:
        unused_fam, rare_fam = [], []

    # Empty cells
    w("\n## Where nobody is\n")
    w(f"- Structures no ad uses: {', '.join(unused) if unused else 'none'}")
    if have_color:
        w(f"- Color families absent: {', '.join(unused_fam) or 'none'}; rare (≤10% of ads): {', '.join(rare_fam) or 'none'}")
    ts = Counter((r.get("type_style") or "").strip().lower() for r in rows if (r.get("type_style") or "").strip())
    if ts:
        w(f"- Type styles nobody uses: {', '.join(t for t in TYPE_STYLES if t not in ts) or 'none'}")

    # One-liner
    s0, c0 = top[0]
    tied = [s for s, c in sc.most_common() if c == c0]
    pic, wd = s0.split(" · ")
    w_top, w_c = wc.most_common(1)[0]
    parts = []
    if len(tied) == 1:
        parts.append(f"a {pic} picture" if pic != "none" else "no picture, type only")
    parts.append("no words in the frame" if w_top == "no words"
                 else f"the headline {w_top.replace(' ', ' and ')} ({w_c} of {n})")
    labels = {
        "background": lambda v: f"{v.replace('-', ' ')} background",
        "type_style": lambda v: f"{v} type",
        "product": lambda v: {"absent": "no product", "held": "the product held in a hand",
                              "in-use": "the product in a scene", "isolated": "the product isolated"}.get(v, v),
        "human": lambda v: {"none": "no people", "incidental": "people at small scale",
                            "half-body": "a person at half body", "face": "a face filling the frame"}.get(v, v),
        "type_case": lambda v: {"upper": "all caps"}.get(v, f"{v} case"),
        "badge": lambda v: "a promo sticker" if v == "yes" else "no sticker",
    }
    for at in ["product", "human", "background", "type_style", "type_case", "badge"]:
        if at in modal and modal[at][1] / modal[at][2] >= 0.5:
            parts.append(labels[at](modal[at][0]))
    if lead:
        parts.append(f"{lead.most_common(1)[0][0]} as the lead color")
    w("\n## In one line\n")
    w(f"The most likely ad in this sample: {', '.join(parts)}.")
    if len(tied) > 1:
        w(f"\nTwo or more structures tie for first ({', '.join(tied)}, {c0} of {n} each); "
          f"the convergence is in where the words go, not in the picture.")
    w("\n---\nThis measures how alike the ads are built, not whether they work.")

    open(a.out, "w").write("\n".join(out) + "\n")
    print(f"{n} ads → {a.out}")


if __name__ == "__main__":
    main()
