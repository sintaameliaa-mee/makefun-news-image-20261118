#!/usr/bin/env python3
"""Render the v2 front page for news-image-20261118 (Wednesday 18 Nov 2026).

Dense newspaper front-page format: masthead + date, big-numbers strip,
3 large illustrated stories, 10 small illustrated cards, a world map with
numbered pins, and a numbered list of the remaining stories (44 total).

All 44 stories were verified against live news dated 18 November 2026
(see SOURCES in the report / README). Illustrations are procedural PIL
drawings - no external images, no copied artwork.

Run: python3 draw.py  ->  writes entry.png next to this file.
Requires Pillow (build-time only). The graded entrypoint is main.py,
which copies the pre-rendered entry.png (stdlib only).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 14  # outer margin

# ---- palette ---------------------------------------------------------------
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (178, 32, 44)
BLUE = (31, 78, 121)
GREY = (110, 108, 100)
LIGHT_LINE = (200, 192, 172)
MAP_OCEAN = (214, 228, 240)
MAP_LAND = (232, 224, 200)
MAP_LAND_LINE = (150, 140, 110)

FDIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF = "LiberationSerif-Regular.ttf"
SERIF_B = "LiberationSerif-Bold.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SANS = "LiberationSans-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"

# ---- text helpers ----------------------------------------------------------


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_center(draw, cx, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def draw_lines(draw, x, y, lines, fnt, fill=INK, leading=None):
    if leading is None:
        leading = fnt.size + 3
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


# ---- story data ------------------------------------------------------------
# (kicker, headline, subtext, illustration key)
LARGE = [
    (
        "THE GULF  |  WAR",
        "Iran strikes US bases in Kuwait and Bahrain",
        "Tehran hits Ali Al Salem air base and a US radar site after US jets "
        "struck an IRGC missile site on Qeshm Island. Qatar seeks talks; "
        "Russia urges a halt.",
        "gulf",
    ),
    (
        "SHENZHEN  |  APEC",
        "Xi and Putin meet as Trump flies in for first three-way summit",
        "China's Xi breaks protocol to greet Trump on the tarmac; the first "
        "Trump-Xi-Putin trilateral is set for Thursday. Trump met Marcos "
        "in Manila on the way.",
        "shenzhen",
    ),
    (
        "MARKETS  |  IPO",
        "Anthropic prices $1.4tn IPO today; trading starts Thursday",
        "The AI maker sets its final Nasdaq price (ticker ANT) after a "
        "$70-$78 range; reports say demand is 7x oversubscribed and the "
        "price may top $80.",
        "ipo",
    ),
]

# (headline, subtext, illustration key)
CARDS = [
    (
        "Ebola toll tops 11,000 cases in Congo",
        "UN: outbreak more than doubled in three months; 5,400 dead, "
        "children worst hit.",
        "ebola",
    ),
    (
        "Cyclone Xavier hits Category 5",
        "Gusts of 315 km/h lash the Northern Cook Islands; Manihiki "
        "in its path.",
        "cyclone",
    ),
    (
        "US loses measles-free status",
        "5,400 cases and 10 deaths end 26 years of elimination; Mexico "
        "and Bolivia too.",
        "measles",
    ),
    (
        "NSA network down in US outage wave",
        "At least eight major failures in a week hit Microsoft, Apple "
        "and banks.",
        "outage",
    ),
    (
        "Stocks slide as Gulf war fears grow",
        "S&P 500 -1.03%, Nasdaq -0.74%; gold falls 2.3% to $3,775.",
        "markets",
    ),
    (
        "Korea lifts 2027 growth call to 3.9%",
        "State think tank nearly doubles its forecast on the AI chip boom.",
        "korea",
    ),
    (
        "UK inflation hits one-year high 3.6%",
        "Energy price cap to rise 26% in January, Cornwall Insight predicts.",
        "uk",
    ),
    (
        "'Human' is word of the year",
        "Cambridge Dictionary picks it over 'agent' as AI blurs what "
        "people are.",
        "human",
    ),
    (
        "Fiji declares disaster over drought",
        "El Nino dry spell empties reservoirs; $20m response, water rationed.",
        "fiji",
    ),
    (
        "Cricket Australia opens sandpapergate forum",
        "Players can tell their side of 2018; no re-investigation, says CA.",
        "cricket",
    ),
]

# Numbered list, items 14-44 (one line each).
LIST_ITEMS = [
    "Myanmar to review future ASEAN ties",
    "World Court rules Thu on Rohingya case",
    "Putin 'not ready' for Ukraine peace talks",
    "Board of Peace: Gaza truce may collapse",
    "UN warns Yemen crisis worsening",
    "Iraq reopens idle oil pipeline to Turkey",
    "Four held over alleged Iran plot in Greece",
    "27 years for Iran-linked plot on Trump",
    "US tightens chip rules; mulls naming AI users",
    "Trump seals preliminary Thailand deal",
    "Seoul uses APEC to warm Beijing ties",
    "Trump-Kim meeting 'more likely'",
    "Pakistan solar hits 28%; grid lags behind",
    "NATO unveils next-gen comms strategy",
    "GTA VI hits shelves tomorrow",
    "WHO: drug resistance may kill 39m in 25 yrs",
    "Senate plans AI hearings after probe",
    "Russia opens case over An-12 crash, 19 dead",
    "Brazil real falls on Lula fiscal plan",
    "Ethiopia-Eritrea border war fears grow",
    "ECB: markets must discipline France",
    "US road deaths at lowest H1 rate since 2014",
    "FDA clears new Roche breast cancer pill",
    "$173m raised for sickle-cell therapy",
    "Higher methadone doses aid quality of life",
    "All 19 crew airlifted off stricken tanker",
    "Brazil passes 2026 tourism target",
    "Laptops for Jamaica pupils hit by Melissa",
    "Modi launches 246 tribal projects, Rs 3,000 cr",
    "India launches AI heritage search 'Sanskriti'",
    "Stamp honours biogas pioneer Singh",
]

NUMBERS = [
    ("11,000+", "EBOLA CASES IN CONGO"),
    ("$1.4tn", "ANTHROPIC IPO VALUE"),
    ("315 km/h", "CYCLONE XAVIER GUSTS"),
    ("-1.03%", "S&P 500 ON GULF FEARS"),
    ("3.9%", "KOREA 2027 GROWTH"),
    ("39m", "AMR DEATHS FEARED BY 2050"),
]

# ---- world map (rough lon/lat polygons, equirectangular) -------------------

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 72), (-85, 70),
     (-80, 73), (-65, 62), (-60, 52), (-55, 47), (-65, 45), (-70, 42),
     (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 29), (-97, 26),
     (-105, 22), (-110, 24), (-115, 29), (-120, 34), (-125, 40), (-125, 49),
     (-135, 57), (-150, 61), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 76),
     (-55, 78), (-65, 76)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-44, 2), (-35, -8),
     (-38, -15), (-41, -23), (-48, -28), (-52, -33), (-58, -38), (-62, -41),
     (-65, -45), (-68, -50), (-69, -54), (-71, -54), (-73, -45), (-73, -37),
     (-71, -30), (-70, -20), (-77, -12), (-80, -6), (-81, 1)],
    # Africa
    [(-17, 15), (-10, 5), (-8, 4), (3, 6), (9, 4), (9, -1), (13, -12),
     (12, -18), (15, -22), (17, -29), (20, -35), (28, -33), (32, -29),
     (35, -24), (40, -16), (40, -10), (42, -2), (46, 2), (51, 11), (44, 11),
     (40, 15), (37, 18), (35, 22), (33, 27), (32, 31), (20, 32), (11, 34),
     (0, 36), (-6, 36), (-10, 31), (-15, 27), (-17, 21)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (3, 51), (8, 54), (8, 57), (12, 58),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 66), (35, 67),
     (40, 68), (45, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 69), (170, 67), (178, 65), (178, 62), (170, 60), (162, 56),
     (158, 52), (150, 59), (142, 54), (140, 40), (135, 35), (130, 33),
     (127, 35), (122, 38), (120, 32), (122, 28), (118, 25), (110, 21),
     (108, 18), (105, 10), (103, 8), (100, 7), (98, 10), (94, 17), (92, 21),
     (88, 22), (86, 20), (80, 16), (77, 8), (74, 14), (72, 20), (68, 23),
     (66, 25), (62, 25), (58, 26), (56, 27), (52, 26), (50, 29), (48, 30),
     (44, 29), (40, 32), (36, 36), (30, 36), (27, 37), (23, 36), (19, 40),
     (16, 42), (12, 44), (8, 44), (3, 43), (-2, 37), (-6, 36), (-9, 37)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (1, 51)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 39), (142, 44),
     (145, 44), (141, 40), (139, 36), (135, 33)],
    # Australia
    [(114, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -31), (153, -27), (151, -24), (146, -19), (142, -15), (142, -11),
     (141, -13), (136, -12), (132, -12), (126, -14), (122, -17)],
    # New Zealand
    [(167, -46), (172, -41), (175, -38), (178, -38), (174, -42), (170, -44)],
]

# (story number, lon, lat) - pins for the map
PINS = [
    (1, 48, 29),    # Gulf / Kuwait
    (2, 114, 22),   # Shenzhen
    (3, -122, 38),  # Anthropic / San Francisco
    (4, 23, -3),    # DR Congo / Ebola
    (5, -160, -21),  # Cook Islands / Xavier
    (6, -77, 39),   # Washington DC / measles
    (7, 0, 51),     # London / UK inflation
    (8, 178, -18),  # Fiji
    (9, 145, -38),  # Australia / cricket
    (10, 96, 20),   # Myanmar
    (11, 34, 31),   # Gaza
    (12, 127, 37),  # Seoul / KDI
    (13, -52, -10),  # Brazil
    (14, 78, 21),   # India
]

# ---- procedural illustrations ----------------------------------------------
# Each draws into box (x0, y0, x1, y1). All original, PIL primitives only.


def _burst(draw, cx, cy, r, color1, color2):
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=color1, outline=color2)
    draw.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28],
                 fill=(255, 240, 180))


def ill_gulf(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(22, 40, 60))
    # sea
    draw.rectangle([x0, y0 + (y1 - y0) * 0.55, x1, y1], fill=(31, 78, 121))
    # landmass (stylised Gulf coast)
    w, h = x1 - x0, y1 - y0
    land = [(x0, y0 + h * 0.55), (x0 + w * 0.25, y0 + h * 0.30),
            (x0 + w * 0.45, y0 + h * 0.42), (x0 + w * 0.60, y0 + h * 0.18),
            (x0 + w * 0.78, y0 + h * 0.30), (x0 + w, y0 + h * 0.22),
            (x0 + w, y0 + h * 0.55)]
    draw.polygon(land, fill=(196, 178, 140))
    # missile arcs (dotted)
    for (ax, ay, bx, by) in [(0.12, 0.85, 0.30, 0.38), (0.55, 0.90, 0.72, 0.34),
                             (0.85, 0.88, 0.62, 0.22)]:
        px, py = x0 + w * ax, y0 + h * ay
        qx, qy = x0 + w * bx, y0 + h * by
        for t in [i / 12 for i in range(13)]:
            mx = px + (qx - px) * t
            my = py + (qy - py) * t - 26 * (1 - (2 * t - 1) ** 2)
            draw.ellipse([mx - 1.5, my - 1.5, mx + 1.5, my + 1.5],
                         fill=(255, 220, 150))
    # bursts
    _burst(draw, x0 + w * 0.30, y0 + h * 0.38, 13, (255, 120, 30), (200, 60, 20))
    _burst(draw, x0 + w * 0.72, y0 + h * 0.34, 11, (255, 120, 30), (200, 60, 20))
    _burst(draw, x0 + w * 0.62, y0 + h * 0.22, 9, (255, 150, 60), (200, 60, 20))
    f = font(SANS_B, 10)
    for txt, fx, fy in [("QESHM", 0.24, 0.52), ("KUWAIT", 0.66, 0.48),
                        ("BAHRAIN", 0.52, 0.08)]:
        draw.text((x0 + w * fx, y0 + h * fy), txt, font=f, fill=(255, 255, 255))


def _flag(draw, x, y, w, h, kind):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    if kind == "us":
        for i in range(7):
            if i % 2 == 0:
                draw.rectangle([x, y + h * i / 7, x + w, y + h * (i + 1) / 7],
                               fill=(178, 32, 44))
        draw.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(31, 78, 121))
    elif kind == "cn":
        draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        draw.ellipse([x + w * 0.14, y + h * 0.14, x + w * 0.38, y + h * 0.46],
                     fill=(255, 222, 0))
    elif kind == "ru":
        draw.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
        draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 60, 160))
        draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(200, 20, 30))


def ill_shenzhen(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    # dusk sky bands
    for i in range(6):
        shade = 26 + i * 10
        draw.rectangle([x0, y0 + h * i / 6, x1, y0 + h * (i + 1) / 6],
                       fill=(shade, shade + 14, 66 + i * 6))
    # sun
    draw.ellipse([x0 + w * 0.70, y0 + h * 0.10, x0 + w * 0.86, y0 + h * 0.42],
                 fill=(255, 170, 60))
    # skyline
    import random
    rnd = random.Random(18)
    bx = x0
    while bx < x1 - 10:
        bw = rnd.randint(18, 34)
        bh = rnd.randint(int(h * 0.25), int(h * 0.62))
        draw.rectangle([bx, y1 - bh, bx + bw, y1], fill=(14, 22, 34))
        for wy in range(int(y1 - bh + 6), y1 - 6, 10):
            for wx in range(int(bx + 4), int(bx + bw - 4), 8):
                if rnd.random() < 0.45:
                    draw.rectangle([wx, wy, wx + 3, wy + 4],
                                   fill=(255, 210, 110))
        bx += bw + 3
    # three flag poles in front
    base_y = y1 - 4
    for i, kind in enumerate(["us", "cn", "ru"]):
        fx = x0 + w * (0.12 + i * 0.30)
        draw.line([fx, y0 + h * 0.30, fx, base_y], fill=(240, 240, 240), width=2)
        _flag(draw, fx + 2, y0 + h * 0.30, 34, 22, kind)


def ill_ipo(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(12, 38, 28))
    # grid
    for i in range(1, 5):
        gy = y0 + h * i / 5
        draw.line([x0, gy, x1, gy], fill=(30, 70, 50), width=1)
    # rising candlesticks
    import random
    rnd = random.Random(7)
    n = 9
    cw = w / (n + 1)
    for i in range(n):
        cx = x0 + cw * (i + 0.7)
        base = y0 + h * (0.88 - i * 0.055)
        top = base - rnd.randint(14, 30)
        draw.rectangle([cx - 6, top, cx + 6, base], fill=(46, 204, 113))
        draw.line([cx, top - 8, cx, base + 8], fill=(46, 204, 113), width=2)
    # arrow
    draw.line([x0 + w * 0.08, y0 + h * 0.82, x0 + w * 0.90, y0 + h * 0.22],
              fill=(255, 220, 80), width=4)
    draw.polygon([(x0 + w * 0.90, y0 + h * 0.22), (x0 + w * 0.82, y0 + h * 0.24),
                  (x0 + w * 0.88, y0 + h * 0.34)], fill=(255, 220, 80))
    f = font(SANS_B, 30)
    draw.text((x0 + 10, y0 + 8), "ANT", font=f, fill=(255, 255, 255))
    f2 = font(SANS_B, 13)
    draw.text((x0 + 10, y0 + 42), "NASDAQ  ·  $70-$78", font=f2,
              fill=(160, 220, 180))


def ill_ebola(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(250, 230, 228))
    import math
    for (cx, cy, r) in [(0.25, 0.5, 16), (0.60, 0.35, 11), (0.78, 0.65, 13)]:
        px, py = x0 + (x1 - x0) * cx, y0 + (y1 - y0) * cy
        for i in range(10):
            ang = math.pi * i / 5
            draw.line([px, py, px + r * 1.5 * math.cos(ang),
                       py + r * 1.5 * math.sin(ang)], fill=(178, 32, 44),
                      width=2)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(178, 32, 44))
        draw.ellipse([px - r * 0.4, py - r * 0.4, px + r * 0.4, py + r * 0.4],
                     fill=(230, 120, 120))


def ill_cyclone(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(200, 216, 230))
    cx, cy = x0 + w * 0.5, y0 + h * 0.5
    for r in range(8, 34, 7):
        draw.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8],
                 start=r * 9 % 360, end=r * 9 % 360 + 250,
                 fill=(31, 78, 121), width=3)
    draw.ellipse([cx - 6, cy - 5, cx + 6, cy + 5], fill=(255, 255, 255),
                 outline=(31, 78, 121))
    f = font(SANS_B, 11)
    draw.text((x0 + 6, y0 + 4), "315 km/h", font=f, fill=(31, 78, 121))


def ill_measles(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(250, 240, 210))
    import random
    rnd = random.Random(3)
    for _ in range(26):
        px = x0 + rnd.randint(4, int(w) - 8)
        py = y0 + rnd.randint(4, int(h) - 8)
        r = rnd.randint(2, 5)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(200, 40, 50))
    draw.ellipse([x0 + w * 0.62, y0 + h * 0.18, x0 + w * 0.92, y0 + h * 0.78],
                 fill=(178, 32, 44))
    f = font(SANS_B, 12)
    draw.text((x0 + w * 0.68, y0 + h * 0.36), "5,400", font=f,
              fill=(255, 255, 255))


def ill_outage(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(20, 20, 24))
    f = font(SANS_B, 17)
    draw.text((x0 + 10, y0 + 8), "OFFLINE", font=f, fill=(255, 80, 80))
    # broken plug: two prongs + snapped cord
    draw.rectangle([x0 + w * 0.68, y0 + h * 0.30, x0 + w * 0.86, y0 + h * 0.62],
                   outline=(220, 220, 220), width=2)
    draw.line([x0 + w * 0.72, y0 + h * 0.30, x0 + w * 0.72, y0 + h * 0.12],
              fill=(220, 220, 220), width=3)
    draw.line([x0 + w * 0.82, y0 + h * 0.30, x0 + w * 0.82, y0 + h * 0.12],
              fill=(220, 220, 220), width=3)
    draw.line([x0 + w * 0.68, y0 + h * 0.75, x0 + w * 0.78, y0 + h * 0.62,
               x0 + w * 0.86, y0 + h * 0.75], fill=(255, 80, 80), width=2)
    f2 = font(SANS, 10)
    draw.text((x0 + 10, y0 + h - 20), "NSA  ·  MICROSOFT  ·  APPLE",
              font=f2, fill=(180, 180, 180))


def ill_markets(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
    pts = [(0.05, 0.25), (0.22, 0.35), (0.38, 0.30), (0.55, 0.55),
           (0.70, 0.50), (0.88, 0.78)]
    xy = [(x0 + w * a, y0 + h * b) for a, b in pts]
    draw.line(xy, fill=(178, 32, 44), width=3)
    draw.polygon([(xy[-1][0], xy[-1][1]), (xy[-1][0] - 12, xy[-1][1] - 2),
                  (xy[-1][0] - 2, xy[-1][1] - 12)], fill=(178, 32, 44))
    f = font(SANS_B, 13)
    draw.text((x0 + 6, y0 + 4), "-1.03%", font=f, fill=(178, 32, 44))


def ill_korea(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(230, 238, 246))
    bars = [0.30, 0.42, 0.38, 0.55, 0.72, 0.90]
    bw = w / (len(bars) + 1)
    for i, v in enumerate(bars):
        bx = x0 + bw * (i + 0.6)
        draw.rectangle([bx, y1 - h * v * 0.85, bx + bw * 0.7, y1 - 4],
                       fill=(31, 78, 121))
    f = font(SANS_B, 13)
    draw.text((x0 + 6, y0 + 4), "3.9%", font=f, fill=(31, 78, 121))


def ill_uk(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(240, 236, 224))
    f = font(SERIF_B, 40)
    draw.text((x0 + 12, y0 + 6), "£", font=f, fill=(26, 26, 26))
    # up arrow
    ax = x0 + w * 0.62
    draw.line([ax, y1 - 12, ax, y0 + 14], fill=(178, 32, 44), width=4)
    draw.polygon([(ax, y0 + 6), (ax - 9, y0 + 20), (ax + 9, y0 + 20)],
                 fill=(178, 32, 44))
    f2 = font(SANS_B, 13)
    draw.text((x0 + w * 0.72, y0 + h * 0.55), "3.6%", font=f2,
              fill=(178, 32, 44))


def ill_human(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(232, 226, 208))
    # open book
    draw.polygon([(x0 + w * 0.12, y0 + h * 0.20), (x0 + w * 0.50, y0 + h * 0.32),
                  (x0 + w * 0.88, y0 + h * 0.20), (x0 + w * 0.88, y0 + h * 0.80),
                  (x0 + w * 0.50, y0 + h * 0.92), (x0 + w * 0.12, y0 + h * 0.80)],
                 fill=(255, 252, 240), outline=(120, 110, 90))
    draw.line([x0 + w * 0.50, y0 + h * 0.32, x0 + w * 0.50, y0 + h * 0.92],
              fill=(120, 110, 90), width=1)
    f = font(SERIF_B, 17)
    draw.text((x0 + w * 0.30, y0 + h * 0.36), '"human"', font=f, fill=INK)


def ill_fiji(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(222, 196, 150))
    # sun
    draw.ellipse([x0 + w * 0.76, y0 + 4, x0 + w * 0.94, y0 + h * 0.42],
                 fill=(255, 200, 60))
    # cracks
    for (sx, sy, pts) in [
            (0.15, 0.20, [(0.15, 0.20), (0.22, 0.45), (0.18, 0.70), (0.26, 0.95)]),
            (0.50, 0.10, [(0.50, 0.10), (0.55, 0.40), (0.48, 0.65), (0.56, 0.95)]),
            (0.80, 0.45, [(0.80, 0.45), (0.72, 0.70), (0.78, 0.95)])]:
        xy = [(x0 + w * a, y0 + h * b) for a, b in pts]
        draw.line(xy, fill=(120, 80, 40), width=2)
    # water drop, empty
    draw.ellipse([x0 + w * 0.06, y0 + h * 0.55, x0 + w * 0.20, y0 + h * 0.85],
                 outline=(31, 78, 121), width=2)


def ill_cricket(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(34, 110, 60))
    # pitch strip
    draw.rectangle([x0 + w * 0.42, y0, x0 + w * 0.58, y1],
                   fill=(222, 200, 150))
    # bat (rotated rectangle)
    bat = [(x0 + w * 0.20, y0 + h * 0.15), (x0 + w * 0.34, y0 + h * 0.10),
           (x0 + w * 0.30, y0 + h * 0.85), (x0 + w * 0.16, y0 + h * 0.80)]
    draw.polygon(bat, fill=(222, 184, 120), outline=(140, 100, 50))
    # ball
    draw.ellipse([x0 + w * 0.70, y0 + h * 0.55, x0 + w * 0.86, y0 + h * 0.85],
                 fill=(178, 32, 44))
    draw.arc([x0 + w * 0.70, y0 + h * 0.55, x0 + w * 0.86, y0 + h * 0.85],
             start=60, end=300, fill=(255, 255, 255), width=1)
    # stumps
    for i in range(3):
        sx = x0 + w * (0.46 + i * 0.04)
        draw.line([sx, y0 + h * 0.10, sx, y0 + h * 0.30],
                  fill=(255, 240, 200), width=3)


ILLUSTRATIONS = {
    "gulf": ill_gulf, "shenzhen": ill_shenzhen, "ipo": ill_ipo,
    "ebola": ill_ebola, "cyclone": ill_cyclone, "measles": ill_measles,
    "outage": ill_outage, "markets": ill_markets, "korea": ill_korea,
    "uk": ill_uk, "human": ill_human, "fiji": ill_fiji,
    "cricket": ill_cricket,
}

# ---- page layout -----------------------------------------------------------


def draw_map(draw, x0, y0, x1, y1):
    """World map panel with numbered pins. Returns nothing."""
    draw.rectangle([x0, y0, x1, y1], fill=MAP_OCEAN, outline=INK, width=1)
    w, h = x1 - x0, y1 - y0
    # equirectangular: lon -180..180 -> width; lat 75..-60
    scale = w / 360.0
    map_h = 135 * scale
    my0 = y0 + (h - map_h) / 2

    def proj(lon, lat):
        return (x0 + (lon + 180) * scale, my0 + (75 - lat) * scale)

    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = proj(lon, 0)
        draw.line([gx, my0, gx, my0 + map_h], fill=(190, 208, 224), width=1)
    for lat in (-30, 0, 30, 60):
        _, gy = proj(0, lat)
        draw.line([x0, gy, x1, gy], fill=(190, 208, 224), width=1)
    # continents
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=MAP_LAND, outline=MAP_LAND_LINE)
    # pins
    fnum = font(SANS_B, 10)
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        r = 8
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        t = str(num)
        tw = draw.textlength(t, font=fnum)
        draw.text((px - tw / 2, py - r + 2.5), t, font=fnum,
                  fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # outer frame
    draw.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)
    draw.rectangle([10, 10, W - 11, H - 11], outline=INK, width=1)

    # ---------- masthead ----------
    f_top = font(SANS, 9)
    draw.text((M + 4, 16), "WEDNESDAY EDITION", font=f_top, fill=GREY)
    text_center(draw, W / 2, 16, "ONE DAY  ·  ONE PAGE  ·  THE WHOLE WORLD",
                f_top, GREY)
    r = "No. 322"
    draw.text((W - M - 4 - draw.textlength(r, font=f_top), 16), r,
              font=f_top, fill=GREY)

    f_name = font(SERIF_B, 52)
    text_center(draw, W / 2, 28, "THE WORLD TODAY", f_name)
    # double rule under name
    draw.line([M + 4, 88, W - M - 4, 88], fill=INK, width=2)
    draw.line([M + 4, 91, W - M - 4, 91], fill=INK, width=1)

    f_date = font(SERIF_B, 21)
    text_center(draw, W / 2, 96, "WEDNESDAY  18 NOVEMBER 2026", f_date)
    f_kick = font(SANS_B, 11)
    text_center(draw, W / 2, 120, "44 STORIES  ·  6 CONTINENTS  ·  ALL FROM TODAY",
                f_kick, RED)
    draw.line([M + 4, 138, W - M - 4, 138], fill=INK, width=1)

    # ---------- big-numbers strip ----------
    strip_y0, strip_y1 = 142, 182
    cell_w = (W - 2 * M - 8) / 6
    f_num = font(SERIF_B, 19)
    f_lab = font(SANS_B, 8)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + 4 + cell_w * (i + 0.5)
        text_center(draw, cx, strip_y0 + 2, num, f_num, BLUE)
        text_center(draw, cx, strip_y0 + 24, lab, f_lab, GREY)
        if i:
            vx = M + 4 + cell_w * i
            draw.line([vx, strip_y0 + 2, vx, strip_y1 - 2], fill=LIGHT_LINE,
                      width=1)
    draw.line([M + 4, strip_y1, W - M - 4, strip_y1], fill=INK, width=2)

    # ---------- 3 large stories ----------
    large_y0 = 190
    col_w = 320
    gap = 8
    total_w = 3 * col_w + 2 * gap
    lx0 = (W - total_w) / 2
    f_lkick = font(SANS_B, 10)
    f_lhead = font(SERIF_B, 19)
    f_lsub = font(SANS, 11)
    ill_h = 140
    for i, (kick, head, sub, key) in enumerate(LARGE):
        x0 = lx0 + i * (col_w + gap)
        x1 = x0 + col_w
        ILLUSTRATIONS[key](draw, x0, large_y0, x1, large_y0 + ill_h)
        draw.rectangle([x0, large_y0, x1, large_y0 + ill_h], outline=INK,
                       width=1)
        y = large_y0 + ill_h + 6
        draw.text((x0, y), kick, font=f_lkick, fill=RED)
        y += 15
        lines = wrap(draw, head, f_lhead, col_w)
        y = draw_lines(draw, x0, y, lines[:3], f_lhead, leading=21)
        y += 2
        slines = wrap(draw, sub, f_lsub, col_w)
        draw_lines(draw, x0, y, slines[:4], f_lsub, leading=14)
        if i < 2:
            vx = x1 + gap / 2
            draw.line([vx, large_y0, vx, large_y0 + 250], fill=LIGHT_LINE,
                      width=1)
    large_y1 = large_y0 + 252
    draw.line([M + 4, large_y1, W - M - 4, large_y1], fill=INK, width=1)

    # ---------- 10 cards (5 + 5) ----------
    card_y0 = large_y1 + 8
    card_w = 192
    card_gap = 6
    card_total = 5 * card_w + 4 * card_gap
    cx0 = (W - card_total) / 2
    f_chead = font(SERIF_B, 12)
    f_csub = font(SANS, 10)
    card_ill_h = 62
    row_h = 132
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            head, sub, key = CARDS[idx]
            x0 = cx0 + col * (card_w + card_gap)
            x1 = x0 + card_w
            y0 = card_y0 + row * row_h
            ILLUSTRATIONS[key](draw, x0, y0, x1, y0 + card_ill_h)
            draw.rectangle([x0, y0, x1, y0 + card_ill_h], outline=INK,
                           width=1)
            y = y0 + card_ill_h + 4
            lines = wrap(draw, head, f_chead, card_w)
            y = draw_lines(draw, x0, y, lines[:2], f_chead, leading=14)
            slines = wrap(draw, sub, f_csub, card_w)
            draw_lines(draw, x0, y + 1, slines[:2], f_csub, leading=12)
    cards_y1 = card_y0 + 2 * row_h
    draw.line([M + 4, cards_y1, W - M - 4, cards_y1], fill=INK, width=2)

    # ---------- bottom: map + numbered list ----------
    bot_y0 = cards_y1 + 8
    bot_y1 = H - M - 4
    f_sec = font(SERIF_B, 14)
    f_list = font(SANS, 10)
    f_list_b = font(SANS_B, 10)

    # map (left)
    map_x0 = M + 4
    map_x1 = 496
    draw.text((map_x0, bot_y0), "WHERE IT HAPPENED", font=f_sec, fill=BLUE)
    f_mapsub = font(SANS, 9)
    draw.text((map_x0, bot_y0 + 18),
              "Numbered pins mark the stories above and at right.",
              font=f_mapsub, fill=GREY)
    draw_map(draw, map_x0, bot_y0 + 36, map_x1, bot_y1 - 24)
    f_src = font(SANS, 8)
    draw.text((map_x0, bot_y1 - 20),
              "Sources: Reuters  ·  AP  ·  AFP  ·  UN News  ·  WHO  ·  BBC  ·  "
              "Yonhap  ·  KDI  ·  FBC News  ·  Cricbuzz",
              font=f_src, fill=GREY)

    # numbered list (right)
    list_x0 = 512
    list_x1 = W - M - 4
    draw.text((list_x0, bot_y0), "ALSO ON WEDNESDAY", font=f_sec, fill=BLUE)
    draw.line([list_x0, bot_y0 + 20, list_x1, bot_y0 + 20], fill=LIGHT_LINE,
              width=1)
    col_w2 = (list_x1 - list_x0 - 12) / 2
    row_h2 = 14.5
    ly = bot_y0 + 24
    for j, item in enumerate(LIST_ITEMS):
        col = 0 if j < 16 else 1
        row = j if j < 16 else j - 16
        x = list_x0 + col * (col_w2 + 12)
        y = ly + row * row_h2
        num = "%d." % (14 + j)
        draw.text((x, y), num, font=f_list_b, fill=RED)
        nw = draw.textlength(num + " ", font=f_list_b)
        # truncate to fit the column
        txt = item
        while draw.textlength(txt, font=f_list) > col_w2 - nw and len(txt) > 8:
            txt = txt[:-1]
        if txt != item:
            txt = txt.rstrip()[:-1] + "…"
        draw.text((x + nw, y), txt, font=f_list, fill=INK)
    # footer line under list
    draw.text((list_x0, bot_y1 - 20),
              "All 44 stories were reported on Wednesday 18 November 2026.",
              font=f_src, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
