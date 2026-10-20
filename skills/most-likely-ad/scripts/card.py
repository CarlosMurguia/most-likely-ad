#!/usr/bin/env python3
"""
card.py: a shareable 1080x1350 card of the category's most likely ad.

Usage:
    python3 card.py --tally tally.json --out card.png
    python3 card.py --tally tally.json --mine mine.json --out check.png

tally.json comes from tally.py (--json); mine.json from compare.py (--json).
The card draws only structure sketches and color swatches, never anyone's ad.
Requires Pillow (pip install pillow). Fonts: assets/fonts (Instrument Sans and
Instrument Serif, SIL OFL 1.1); falls back to a system font if they are missing.
"""
import argparse
import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("card.py needs Pillow: pip install pillow")

# ---------------------------------------------------------------- constants
W, H = 1080, 1350
S = 2                      # supersampling: draw at 2x, downsample once
M = 72                     # outer margin
PAPER = (244, 243, 239)    # neutral paper: lets any category palette sit on it
INK = (26, 25, 24)
INK_2 = (90, 86, 80)       # secondary text, 6.5:1 on paper
PICTURE = (196, 193, 186)  # grey box = picture
RULE = (216, 213, 206)
GHOST = (228, 226, 220)    # the picture in the ad nobody makes
REPO = "github.com/CarlosMurguia/most-likely-ad"

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "assets", "fonts")
SERIF = os.path.join(FONTS, "InstrumentSerif-Regular.ttf")
SANS = os.path.join(FONTS, "InstrumentSans[wdth,wght].ttf")
FALLBACKS = {
    "serif": ["/System/Library/Fonts/Supplemental/Georgia.ttf", "C:/Windows/Fonts/georgia.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
    "sans": ["/System/Library/Fonts/Supplemental/Arial.ttf", "C:/Windows/Fonts/arial.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
}
NEUTRAL = {"white", "black", "gray"}
ASPECTS = {"1:1": 1.0, "4:5": 1.25, "9:16": 16 / 9, "1.91:1": 1 / 1.91}

_warned = False


def font(kind, size, weight=400):
    """Instrument Serif / Instrument Sans at `size` px (1x), with a system fallback."""
    global _warned
    path = SERIF if kind == "serif" else SANS
    px = int(size * S)
    try:
        f = ImageFont.truetype(path, px)
        if kind == "sans":
            try:
                f.set_variation_by_axes([100, weight])
            except Exception:
                pass
        return f
    except OSError:
        if not _warned:
            print("card.py: bundled fonts not found, using a system font.", file=sys.stderr)
            _warned = True
        for p in FALLBACKS[kind]:
            try:
                return ImageFont.truetype(p, px)
            except OSError:
                continue
        return ImageFont.load_default(px)


# ---------------------------------------------------------------- words
WORDS_TXT = {
    "top centered": "at the top, centered", "top side": "at the top, to one side",
    "middle centered": "in the middle, centered", "middle side": "in the middle, to one side",
    "bottom centered": "at the bottom, centered", "bottom side": "at the bottom, to one side",
}
PICTURE_TXT = {"full-bleed": "a full-bleed picture", "framed": "a framed picture", "none": "no picture"}
VALUE_TXT = {
    "human": {"none": "No people", "incidental": "People, small", "half-body": "A person, half body",
              "face": "A face, close"},
    "product": {"isolated": "Product on its own", "held": "Product in a hand",
                "in-use": "Product in a scene", "absent": "No product"},
    "type_case": {"upper": "Headline in all caps", "sentence": "Headline in sentence case",
                  "title": "Headline in Title Case", "lower": "Headline in lowercase"},
    "type_style": {"display": "Heavy display type", "sans": "Sans-serif headline",
                   "serif": "Serif headline", "condensed": "Condensed headline",
                   "script": "Script headline", "mixed": "Mixed typefaces"},
    "background": {"plain": "Plain background", "gradient": "Gradient background",
                   "photo-environment": "Photo background", "cutout-on-color": "Cut-out on color"},
    "badge": {"yes": "Promo sticker", "no": "No promo sticker"},
    "picture": {"full-bleed": "Full-bleed picture", "framed": "Framed picture", "none": "No picture"},
    "image_kind": {"photo": "Photography", "illustration": "Illustration",
                   "flat-graphic": "Flat graphic", "none": "No image"},
}
# the conventions worth a line on the card, in order of how much they say about the ad
CONVENTION_ORDER = ["human", "product", "type_case", "type_style", "background", "badge"]


def say(decision, value):
    value = (value or "").strip()
    if decision == "words":
        if value in ("no words", "none", ""):
            return "No headline in the frame"
        v, _, hz = value.partition(" ")
        return f"Headline {v}, " + ("centered" if hz == "centered" else "off-center")
    if decision == "lead_color":
        return f"{value.capitalize()} as the lead color"
    return VALUE_TXT.get(decision, {}).get(value, f"{decision.replace('_', ' ').capitalize()}: {value}")


def short(decision, value):
    """The category's value, compact, for the 'Most: ...' note."""
    if decision == "lead_color":
        return value
    txt = say(decision, value)
    return txt[len("Headline "):] if txt.startswith("Headline ") else txt[0].lower() + txt[1:]


def category_phrase(cat):
    """'Coffee shops' -> 'coffee shops'; keeps 'SaaS', 'B2B software', 'Nike'-style casing."""
    cat = (cat or "this category").strip()
    if len(cat) > 1 and cat[0].isupper() and cat[1].islower() and " " in cat:
        return cat[0].lower() + cat[1:]
    return cat


def nice_date(d):
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    try:
        y, m, dd = d.split("-")
        return f"{months[int(m) - 1]} {int(dd)}, {y}"
    except Exception:
        return d or ""


# ---------------------------------------------------------------- reading the tally
def dominant(t):
    """What the card leads with: the strongest convergence between structure and word position."""
    n = t.get("n") or 0
    structs = t.get("structures") or []
    words = [w for w in (t.get("words") or []) if w["position"] != "no words"]
    picture_totals = {}
    for s in structs:
        picture_totals[s["picture"]] = picture_totals.get(s["picture"], 0) + s["count"]
    top_picture = max(picture_totals, key=picture_totals.get) if picture_totals else "framed"
    top_s = structs[0] if structs else None
    tied = [s for s in structs if top_s and s["count"] == top_s["count"]]
    top_w = words[0] if words else None

    d = {"n": n, "tie": None}
    if top_s and (not top_w or top_s["count"] >= top_w["count"]) and len(tied) == 1:
        d.update(kind="structure", count=top_s["count"], picture=top_s["picture"], words=top_s["words"])
    elif top_w:
        d.update(kind="words", count=top_w["count"], words=top_w["position"], picture=top_picture)
        if len(tied) > 1:
            d["tie"] = tied
    else:
        d.update(kind="structure", count=top_s["count"] if top_s else 0,
                 picture=top_s["picture"] if top_s else "framed",
                 words=top_s["words"] if top_s else "no words")
    return d


def hero_line(d, cat):
    if d["kind"] == "structure":
        w = WORDS_TXT.get(d["words"])
        how = f"{PICTURE_TXT.get(d['picture'], d['picture'])}, the headline {w}" if w \
            else f"{PICTURE_TXT.get(d['picture'], d['picture'])}, no headline"
        return f"of {d['n']} are built the same way: {how}."
    return f"of {d['n']} put the headline {WORDS_TXT.get(d['words'], d['words'])}."


def pick_conventions(t, k=3):
    conv = t.get("conventions") or {}
    out = []
    for key in CONVENTION_ORDER:
        c = conv.get(key)
        if not c or not c.get("of") or c["count"] / c["of"] < 0.4:
            continue
        out.append((c["count"] / c["of"], key, c))
    out.sort(key=lambda x: -x[0])
    # badge "no" is the least telling; keep it only if nothing else qualifies
    keep = [o for o in out if o[1] != "badge"][:k]
    if len(keep) < k:
        keep += [o for o in out if o[1] == "badge"][:k - len(keep)]
    return [(say(key, c["value"]), c["count"], c["of"]) for _, key, c in keep]


def nobody(t, d):
    """The unused structure that sits furthest from the dominant one."""
    unused = t.get("unused_structures") or []
    if not unused:
        return None
    dv, _, dh = (d["words"] + "  ").partition(" ")
    best, score = None, -1
    for u in unused:
        pic, _, w = u.partition(" · ")
        v, _, hz = w.partition(" ")
        rows = {'top': 0, 'middle': 1, 'bottom': 2}
        sc = abs(rows.get(v, 1) - rows.get(dv, 1)) * 1.5 + (1 if hz.strip() != dh.strip() else 0) + (1 if pic != d["picture"] else 0)
        if sc > score:
            best, score = (pic, w), sc
    return best


def swatches(t, k=5):
    fams = [c for c in (t.get("color_families") or []) if c["family"] not in NEUTRAL and c.get("hex")]
    if len(fams) < 3:  # a category that really is black-and-white: show it
        fams = [c for c in (t.get("color_families") or []) if c.get("hex")]
    return fams[:k]


def aspect_ratio(t):
    a = ((t.get("conventions") or {}).get("aspect") or {}).get("value", "4:5")
    return a, ASPECTS.get(a, 1.25)


# ---------------------------------------------------------------- drawing
class Canvas:
    def __init__(self):
        self.im = Image.new("RGB", (W * S, H * S), PAPER)
        self.d = ImageDraw.Draw(self.im)

    def text(self, xy, s, f, fill=INK, anchor="la", tracking=0):
        x, y = xy
        if not tracking:
            self.d.text((x * S, y * S), s, font=f, fill=fill, anchor=anchor)
            return
        for ch in s:  # letter-spaced small caps labels
            self.d.text((x * S, y * S), ch, font=f, fill=fill, anchor=anchor)
            x += self.width(ch, f) + tracking

    def width(self, s, f):
        return self.d.textlength(s, font=f) / S

    def wrap(self, s, f, maxw):
        lines, cur = [], ""
        for word in s.split():
            trial = (cur + " " + word).strip()
            if self.width(trial, f) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, xy, s, f, maxw, lead, fill=INK):
        x, y = xy
        lines = self.wrap(s, f, maxw)
        for i, ln in enumerate(lines):
            self.text((x, y + i * lead), ln, f, fill)
        return y + len(lines) * lead

    def rect(self, box, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        self.d.rectangle((x0 * S, y0 * S, x1 * S - 1, y1 * S - 1), fill=fill, outline=outline,
                         width=int(width * S) if outline else 0)

    def line(self, a, b, fill=RULE, width=1):
        self.d.line((a[0] * S, a[1] * S, b[0] * S, b[1] * S), fill=fill, width=int(width * S))

    def dot(self, c, r, fill=None, outline=None, width=2):
        x, y = c
        self.d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=fill, outline=outline,
                       width=int(width * S) if outline else 0)

    def dashed_rect(self, box, fill=INK, dash=10, gap=8, width=2):
        x0, y0, x1, y1 = box
        for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
            length = abs(bx - ax) + abs(by - ay)
            sx, sy = (bx - ax) / length, (by - ay) / length
            t = 0
            while t < length:
                e = min(t + dash, length)
                self.line((ax + sx * t, ay + sy * t), (ax + sx * e, ay + sy * e), fill, width)
                t = e + gap

    def save(self, path):
        self.im.resize((W, H), Image.LANCZOS).save(path, optimize=True)


def sketch(c, box, picture, words, dashed=False, stroke=3):
    """The ad as a blank: frame, grey box where the picture goes, black bars where the words go."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    v, _, hz = (words or "no words").partition(" ")
    has_words = v in ("top", "middle", "bottom")
    pad = w * 0.09
    bar_h = max(4, h * 0.035)
    gap = bar_h * 0.75
    block_h = bar_h * 2 + gap
    # where the headline block sits (center of its third)
    third = {"top": 0, "middle": 1, "bottom": 2}.get(v, 1)
    by = y0 + h * (third + 0.5) / 3 - block_h / 2
    if third == 0:
        by = y0 + pad * 1.4
    if third == 2:
        by = y1 - pad * 1.4 - block_h

    if dashed:
        tone, bars = GHOST, INK
    else:
        tone, bars = PICTURE, INK

    # picture
    if picture == "full-bleed":
        c.rect((x0 + 3, y0 + 3, x1 - 3, y1 - 3) if dashed else box, fill=tone)
    elif picture == "framed":
        px0, px1 = x0 + pad, x1 - pad
        py0, py1 = y0 + pad, y1 - pad
        if has_words and third == 0:
            py0 = by + block_h + pad
        elif has_words and third == 2:
            py1 = by - pad
        elif has_words and third == 1:
            # words in the middle: picture beside them if side, else picture shrinks around them
            if hz == "side":
                px0 = x0 + w * 0.52
            else:
                py0, py1 = by + block_h + pad * 0.8, y1 - pad
        c.rect((px0, py0, px1, py1), fill=tone)

    # words
    if has_words:
        widths = (0.72, 0.5) if hz != "side" else (0.5, 0.34)
        for i, f in enumerate(widths):
            bw = w * f
            bx = x0 + (w - bw) / 2 if hz != "side" else x0 + pad
            yy = by + i * (bar_h + gap)
            c.rect((bx, yy, bx + bw, yy + bar_h), fill=bars)

    if dashed:  # the ad nobody makes: same drawing, dashed edge, paler picture
        c.dashed_rect(box, fill=INK, dash=max(5, w * 0.08), gap=max(4, w * 0.06), width=2)
    else:
        c.rect(box, outline=INK, width=stroke)


def chips(c, x, y, fams, size, gap, label=True):
    f = font("sans", 15, 500)
    for i, fam in enumerate(fams):
        cx = x + i * (size + gap)
        rgb = hex_rgb(fam["hex"])
        c.rect((cx, y, cx + size, y + size), fill=rgb)
        if luminance(rgb) > 0.8:  # a white or pale chip still needs an edge on paper
            c.rect((cx, y, cx + size, y + size), outline=RULE, width=1)
        if label:
            c.text((cx, y + size + 10), fam["family"].capitalize(), f, INK)
            c.text((cx, y + size + 30), f"{fam['ads']} ads", f, INK_2)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def frame_box(x, y, maxw, maxh, ratio):
    """Fit an ad frame of height/width `ratio` inside maxw x maxh, top-left at x, y."""
    w = maxw
    h = w * ratio
    if h > maxh:
        h = maxh
        w = h / ratio
    return (x, y, x + w, y + h)


def footer(c, t):
    y = H - M - 4
    c.line((M, FOOT_RULE), (W - M, FOOT_RULE), RULE, 1)
    f = font("sans", 18, 400)
    bits = [f"{t.get('n', '?')} ads", f"{t.get('advertisers', '?')} advertisers",
            t.get("platform", ""), nice_date(t.get("date", ""))]
    c.text((M, y), " · ".join(b for b in bits if b), f, INK_2, anchor="ls")
    c.text((W - M, y), REPO, f, INK_2, anchor="rs")


def label(c, xy, s):
    c.text(xy, s.upper(), font("sans", 15, 600), INK_2, tracking=1.6)


# ---------------------------------------------------------------- the two cards
FOOT_RULE = H - M - 30          # hairline above the footer
CAP = 191                       # cap height of the 260 px hero number


def title(c, first, second, y):
    """Two-line serif title with a chosen break; the second line wraps if it must."""
    ft = font("serif", 84)
    c.text((M - 3, y), first, ft)
    return c.para((M - 3, y + 80), second, ft, W - 2 * M, 80)


def stat(c, x, y, k, of, txt, w):
    """The card's one repeated unit: 'k of n' over a short label."""
    c.text((x, y), f"{k} of {of}", font("sans", 30, 600), INK)
    return c.para((x, y + 42), txt, font("sans", 21, 400), w - 24, 26, INK)


def hero_block(c, x, y, w, d, cat, sw, draw=True):
    """The number, the sentence, the colors. Returns the bottom y."""
    fh = font("serif", 260)
    if draw:
        c.text((x - 4, y + CAP), str(d["count"]), fh, INK, anchor="ls")
    yy = c.para((x, y + CAP + 30), hero_line(d, cat), font("serif", 44), w, 46) if draw else \
        y + CAP + 30 + 46 * len(c.wrap(hero_line(d, cat), font("serif", 44), w))
    if sw:
        if draw:
            label(c, (x, yy + 34), "Colors in the most ads")
            size = min(64, (w - 4 * 12) / max(len(sw), 1))
            chips(c, x, yy + 64, sw, size, 12)
        yy += 64 + 64 + 50
    return yy


def category_card(t, out):
    c = Canvas()
    cat = category_phrase(t.get("category"))
    d = dominant(t)
    asp_name, ratio = aspect_ratio(t)
    sw = swatches(t)
    n = t.get("n")

    # top: the title
    ty = title(c, "The most likely ad", f"in {cat}", M - 10)

    # bottom up: where nobody is, then three conventions
    gap = nobody(t, d)
    unused_c = [u for u in (t.get("unused_color_families") or []) if u not in NEUTRAL]
    colw = (W - 2 * M) / 3
    ny = FOOT_RULE - 44 - 128
    if gap or unused_c:
        label(c, (M, ny - 34), "Where nobody is")
        if gap:
            nb = frame_box(M, ny, 92, 128, ratio)
            sketch(c, nb, gap[0], gap[1], dashed=True)
            tx = nb[2] + 24
            w = WORDS_TXT.get(gap[1])
            txt = (f"{PICTURE_TXT.get(gap[0], gap[0]).capitalize()}, {say('words', gap[1]).lower()}"
                   if w else f"{PICTURE_TXT.get(gap[0], gap[0]).capitalize()}, no headline")
            stat(c, tx, ny, 0, n, txt, M + 2 * colw - tx)
        if unused_c:
            x = M + 2 * colw
            c.dashed_rect((x, ny, x + 40, ny + 40), fill=INK, dash=6, gap=5, width=2)
            stat(c, x + 58, ny, 0, n, unused_c[0].capitalize(), colw - 58)
    cy = ny - 34 - 44 - 76
    c.line((M, cy - 26), (W - M, cy - 26), RULE, 1)
    for i, (txt, k, of) in enumerate(pick_conventions(t)):
        stat(c, M + i * colw, cy, k, of, txt, colw)

    # middle: the sketch and the number, centred in what is left
    col_l = 400
    rx = M + col_l + 64
    rw = W - M - rx
    region_top, region_bot = ty + 56, cy - 26 - 56
    right_h = hero_block(c, rx, 0, rw, d, cat, sw, draw=False)
    cap_h = 50
    box_h = min(region_bot - region_top - cap_h, 600)
    box = frame_box(0, 0, col_l, box_h, ratio)
    left_h = box[3] + cap_h
    top = region_top + max(0, (region_bot - region_top - max(left_h, right_h)) / 2)
    box = frame_box(M, top, col_l, box_h, ratio)
    sketch(c, box, d["picture"], d["words"])
    cap = font("sans", 17, 400)
    if d["tie"]:
        names = ", ".join(f"{s['picture']} {s['count']}" for s in d["tie"][:3])
        c.text((M, box[3] + 16), f"{asp_name} · picture tie: {names}", cap, INK_2)
    else:
        c.text((M, box[3] + 16), f"{asp_name} · {d['picture']} picture", cap, INK_2)
    hero_block(c, rx, top, rw, d, cat, sw)

    footer(c, t)
    c.save(out)


def check_card(t, mine, out):
    c = Canvas()
    cat = category_phrase(t.get("category"))
    d = dominant(t)
    _, ratio = aspect_ratio(t)
    shared, total = mine.get("shared", 0), mine.get("total", 0)
    n = mine.get("n", t.get("n"))

    label(c, (M, M), f"Check my ad · {cat}")
    ty = title(c, "Your ad shares", f"{shared} of {total} conventions", M + 26)

    # bottom: one line about the layout
    sc = mine.get("structure_count", 0)
    line = (f"Its layout is the same as {sc} of the {n} ads in the sample." if mine.get("shares_structure")
            else f"None of the {n} ads in the sample uses its layout.")
    fl = font("serif", 36)
    lines = c.wrap(line, fl, W - 2 * M)
    ly = FOOT_RULE - 48 - 40 * len(lines)
    c.para((M, ly), line, fl, W - 2 * M, 40)
    c.line((M, ly - 30), (W - M, ly - 30), RULE, 1)

    # middle: two sketches (left) and the list (right)
    each, gx = 280, 32
    lx = M + 2 * each + gx + 48
    lw = W - M - lx
    checks = mine.get("checks") or []
    f1, f2 = font("sans", 22, 500), font("sans", 17, 400)

    def note(ch):
        if ch["shared"]:
            return f"{ch['count']} of {ch['of']} do too"
        return f"Most: {short(ch['decision'], ch['category'])}, {ch['count']} of {ch['of']}"

    list_h = 34
    for ch in checks:
        list_h += 25 * len(c.wrap(say(ch["decision"], ch["mine"]), f1, lw - 28)) + 2 + \
            20 * len(c.wrap(note(ch), f2, lw - 28)) + 14
    region_top, region_bot = ty + 60, ly - 30 - 50
    sk_h = min(region_bot - region_top - 30 - 60, 620)
    box0 = frame_box(0, 0, each, sk_h, ratio)
    left_h = 30 + box0[3] + 16 + 40
    top = region_top + max(0, (region_bot - region_top - max(left_h, list_h)) / 2)

    st = mine.get("structure") or {}
    for i, (lab, pic, words, cols) in enumerate([
        ("Your ad", st.get("picture", "framed"), st.get("words", "no words"),
         [{"hex": h, "family": "", "ads": 0} for h in (mine.get("colors") or [])[:5]]),
        ("Most likely", d["picture"], d["words"], swatches(t)),
    ]):
        x = M + i * (each + gx)
        label(c, (x, top), lab)
        box = frame_box(x, top + 30, each, sk_h, ratio)
        sketch(c, box, pic, words)
        if cols:
            size = (box[2] - box[0] - 4 * 8) / 5
            chips(c, x, box[3] + 16, cols, size, 8, label=False)

    yy = top
    label(c, (lx, yy), "Convention by convention")
    yy += 34
    for ch in checks:
        if ch["shared"]:
            c.dot((lx + 8, yy + 13), 7, fill=INK)
        else:
            c.dot((lx + 8, yy + 13), 6, outline=INK, width=2)
        y2 = c.para((lx + 28, yy), say(ch["decision"], ch["mine"]), f1, lw - 28, 25, INK)
        y2 = c.para((lx + 28, y2 + 2), note(ch), f2, lw - 28, 20, INK_2)
        yy = y2 + 14

    footer(c, t)
    c.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tally", required=True, help="tally.json from tally.py")
    ap.add_argument("--mine", help="mine.json from compare.py (makes the Check my ad card)")
    ap.add_argument("--out", default=None, help="output PNG (default card.png / check.png)")
    a = ap.parse_args()
    t = json.load(open(a.tally))
    if a.mine:
        out = a.out or "check.png"
        check_card(t, json.load(open(a.mine)), out)
    else:
        out = a.out or "card.png"
        category_card(t, out)
    print(f"card → {out}")


if __name__ == "__main__":
    main()
