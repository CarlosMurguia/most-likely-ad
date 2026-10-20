#!/usr/bin/env python3
"""
palette.py: extract the dominant colors of each ad image.

Usage:
    python3 palette.py <image-folder> [--colors 5] [--out palettes.csv]

Writes one row per image: file, aspect (9:16 · 4:5 · 1:1 · 1.91:1 · other), colors (hex, largest share first), shares (%),
families (color family of each color). Requires Pillow (pip install pillow).
"""
import argparse
import colorsys
import csv
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("palette.py needs Pillow: pip install pillow")

EXTS = (".jpg", ".jpeg", ".png", ".webp")


def family(rgb):
    """Name the color family of an (r, g, b) tuple. Shared with tally.py."""
    r, g, b = (c / 255 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if l < 0.15:
        return "black"
    if l > 0.93 or (l > 0.88 and s < 0.35):
        return "white"
    if s < 0.18:
        return "gray"
    hue = h * 360
    if (hue < 50 or hue >= 345) and (l < 0.3 or (l < 0.42 and s < 0.85)):
        return "brown"
    if l > 0.72 and s < 0.6 and 20 <= hue < 65:
        return "beige"
    if hue < 15 or hue >= 345:
        return "red"
    if hue < 45:
        return "orange"
    if hue < 70:
        return "yellow"
    if hue < 165:
        return "green"
    if hue < 200:
        return "teal"
    if hue < 255:
        return "blue"
    if hue < 290:
        return "purple"
    return "pink"


def aspect(w, h):
    r = w / h
    for name, val in [("9:16", 9 / 16), ("4:5", 4 / 5), ("1:1", 1.0), ("1.91:1", 1.91)]:
        if abs(r - val) / val < 0.06:
            return name
    return "other"


def palette(path, n=5):
    img = Image.open(path).convert("RGB")
    size = img.size
    img.thumbnail((200, 200))
    q = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: n * 3]
    counts = sorted(q.getcolors(), reverse=True)  # (count, index)
    total = sum(c for c, _ in counts)
    out = []
    for count, idx in counts:
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        out.append(("#%02x%02x%02x" % rgb, round(100 * count / total), family(rgb)))
    return out, aspect(*size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--colors", type=int, default=5)
    ap.add_argument("--out", default="palettes.csv")
    a = ap.parse_args()
    files = sorted(f for f in os.listdir(a.folder) if f.lower().endswith(EXTS))
    if not files:
        sys.exit(f"No images in {a.folder}")
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "aspect", "colors", "shares", "families"])
        for f in files:
            p, asp = palette(os.path.join(a.folder, f), a.colors)
            w.writerow([f, asp, ";".join(c for c, _, _ in p), ";".join(str(s) for _, s, _ in p),
                        ";".join(fam for _, _, fam in p)])
    print(f"{len(files)} images → {a.out}")


if __name__ == "__main__":
    main()
