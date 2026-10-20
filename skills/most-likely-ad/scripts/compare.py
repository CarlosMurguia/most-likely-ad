#!/usr/bin/env python3
"""
compare.py: "Check my ad". How many of the category's conventions does my ad repeat?

Usage:
    python3 compare.py ads.csv mine.csv [--out mine.md] [--json mine.json]

ads.csv  = the coded category sample (see references/structure-taxonomy.md)
mine.csv = the user's ad, coded with the same columns (one row; extra rows are ignored)

A convention is the most common value of a decision in the category sample, when at
least 40% of the ads share it. The check reports, for each convention, whether the
user's ad repeats it. It measures predictability, not quality. Standard library only.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tally import family, structure, words  # same folder

DECISIONS = [  # (key, label, how to read a row)
    ("words", "Where the headline sits", words),
    ("picture", "How the picture sits", lambda r: (r.get("picture") or "").strip().lower()),
    ("product", "Product", lambda r: (r.get("product") or "").strip().lower()),
    ("human", "People", lambda r: (r.get("human") or "").strip().lower()),
    ("background", "Background", lambda r: (r.get("background") or "").strip().lower()),
    ("type_style", "Headline typeface", lambda r: (r.get("type_style") or "").strip().lower()),
    ("type_case", "Headline case", lambda r: (r.get("type_case") or "").strip().lower()),
    ("badge", "Promo sticker", lambda r: (r.get("badge") or "").strip().lower()),
]
THRESHOLD = 0.4
NEUTRAL = ("black", "white", "gray", "beige")


def lead_family(row):
    for c in (row.get("colors") or "").split(";"):
        c = c.strip()
        if c and family(c) not in NEUTRAL:
            return family(c)
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ads")
    ap.add_argument("mine")
    ap.add_argument("--out", default="mine.md")
    ap.add_argument("--json")
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(a.ads, newline="")) if (r.get("picture") or "").strip()]
    mine_rows = list(csv.DictReader(open(a.mine, newline="")))
    if not rows or not mine_rows:
        raise SystemExit("Need a coded category sample and one coded ad.")
    me = mine_rows[0]
    n = len(rows)

    checks = []
    decisions = DECISIONS + [("lead_color", "Lead color", lead_family)]
    for key, label, get in decisions:
        vals = Counter(v for v in (get(r) for r in rows) if v and v != "n/a")
        if not vals:
            continue
        mode, count = vals.most_common(1)[0]
        of = sum(vals.values())
        mine_v = get(me)
        if count / of < THRESHOLD or not mine_v or mine_v == "n/a":
            continue  # no convention here, or not applicable to my ad
        checks.append({"decision": key, "label": label, "mine": mine_v, "category": mode,
                       "count": count, "of": of, "shared": mine_v == mode})

    my_struct = structure(me)
    sc = Counter(structure(r) for r in rows)
    shared = sum(c["shared"] for c in checks)
    data = {
        "file": me.get("file", ""),
        "aspect": (me.get("aspect") or "").strip(),
        "structure": {"picture": my_struct.split(" · ")[0], "words": my_struct.split(" · ")[1]},
        "shares_structure": sc.get(my_struct, 0) > 0,
        "structure_count": sc.get(my_struct, 0),
        "n": n,
        "checks": [{k: c[k] for k in ("decision", "mine", "category", "count", "of", "shared")} for c in checks],
        "shared": shared,
        "total": len(checks),
        "colors": [c for c in (me.get("colors") or "").split(";") if c.strip()],
    }

    out = [f"# Check my ad: {data['file']}\n",
           f"**Your ad repeats {shared} of the category's {len(checks)} conventions.**\n",
           f"Its structure ({my_struct}) is shared by **{data['structure_count']} of {n}** ads in the sample.\n",
           "| Decision | Your ad | Category convention | Repeats it? |", "|---|---|---|---|"]
    for c in checks:
        out.append(f"| {c['label']} | {c['mine']} | {c['category']} ({c['count']} of {c['of']}) | "
                   f"{'yes' if c['shared'] else '**no**'} |")
    breaks = [c["label"].lower() for c in checks if not c["shared"]]
    out.append("")
    out.append(f"Where it already breaks from the category: {', '.join(breaks)}." if breaks
               else "It breaks none of the category's conventions: this is close to the most likely ad.")
    out.append("\nThis measures how predictable the ad is in its category, not whether it works.")
    open(a.out, "w").write("\n".join(out) + "\n")
    if a.json:
        json.dump(data, open(a.json, "w"), indent=2)
    print(f"{shared} of {len(checks)} conventions → {a.out}")


if __name__ == "__main__":
    main()
