#!/usr/bin/env python3
"""news-image-20261124: draw a one-page newspaper front page summing up the
world news of Tuesday 24 November 2026. Pure stdlib, no network, deterministic.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png, or argv[1]/entry.png).
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '#' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[base + (xx - x0) * 3: base + (xx - x0) * 3 + 3] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r:
                    self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, c)

    def tri(self, x, y, s, c):
        self.poly([(x, y), (x + s, y), (x + s // 2, y + s)], c)


# ---------------------------------------------------------------- text
def text_w(s, sc):
    return len(s) * 6 * sc - sc


def draw_char(cv, x, y, ch, sc, c):
    g = FONT.get(ch.upper(), FONT['?'])
    for r, row in enumerate(g):
        for col, bit in enumerate(row):
            if bit == '1':
                cv.rect(x + col * sc, y + r * sc, sc, sc, c)


def draw_text(cv, x, y, s, sc, c):
    for ch in s:
        draw_char(cv, x, y, ch, sc, c)
        x += 6 * sc
    return x


def draw_text_c(cv, cx, y, s, sc, c):
    draw_text(cv, cx - text_w(s, sc) // 2, y, s, sc, c)


def wrap(s, max_w, sc):
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, sc) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, sc, c, max_w, lh=None):
    lh = lh if lh is not None else 7 * sc + 2
    lines = wrap(s, max_w, sc)
    for ln in lines:
        draw_text(cv, x, y, ln, sc, c)
        y += lh
    return y, len(lines)


# ---------------------------------------------------------------- PNG
def _chunk(typ, data):
    ch = struct.pack('>I', len(data)) + typ + data
    ch += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    return ch


def write_png(path, cv):
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 9)
    png = (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr)
           + _chunk(b'IDAT', data) + _chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- colours
PAPER = bytes((253, 248, 238))
WHITE = bytes((255, 255, 255))
NAVY = bytes((16, 36, 62))
NAVY2 = bytes((27, 58, 95))
RED = bytes((192, 57, 43))
GOLD = bytes((232, 163, 61))
INK = bytes((24, 30, 40))
GREY = bytes((90, 96, 106))
LINE = bytes((190, 180, 165))
C_WORLD = bytes((27, 79, 114))
C_POL = bytes((125, 60, 152))
C_INDIA = bytes((176, 112, 14))
C_SPORT = bytes((30, 132, 73))
C_TECH = bytes((46, 134, 193))
C_GOLD = bytes((202, 142, 26))

# ---------------------------------------------------------------- icons
# Small pictograms drawn inside a coloured disc (cx, cy, r).
def icon(cv, kind, cx, cy, r, bg, fg):
    cv.disc(cx, cy, r, bg)
    s = r  # half-size unit
    if kind == 'flame':
        cv.poly([(cx - s // 2, cy + s // 2), (cx - s // 2, cy),
                 (cx - s // 4, cy - s // 3), (cx, cy - s),
                 (cx + s // 4, cy - s // 3), (cx + s // 2, cy + s // 6),
                 (cx + s // 2, cy + s // 2)], fg)
        cv.disc(cx, cy + s // 4, s // 4, bg)
    elif kind == 'burst':  # explosion / strike: 8-point star
        cv.poly([(cx, cy - s), (cx + s // 3, cy - s // 3), (cx + s, cy),
                 (cx + s // 3, cy + s // 3), (cx, cy + s),
                 (cx - s // 3, cy + s // 3), (cx - s, cy),
                 (cx - s // 3, cy - s // 3)], fg)
        cv.disc(cx, cy, s // 3, bg)
    elif kind == 'ship':
        cv.poly([(cx - s, cy), (cx + s, cy), (cx + s // 2, cy + s // 2),
                 (cx - s // 2, cy + s // 2)], fg)
        cv.vline(cx, cy - s, s, fg, 3)
        cv.poly([(cx, cy - s), (cx + s // 2, cy - s // 3), (cx, cy - s // 3)], fg)
    elif kind == 'plane':
        cv.poly([(cx - s, cy + s // 4), (cx + s, cy - s // 4),
                 (cx + s // 2, cy + s // 4), (cx, cy + s // 2)], fg)
        cv.poly([(cx - s // 4, cy - s // 2), (cx + s // 4, cy - s // 2),
                 (cx, cy + s // 4)], fg)
    elif kind == 'globe':
        cv.disc(cx, cy, s, fg)
        cv.disc(cx, cy, s - 3, bg)
        cv.line(cx - s + 3, cy, cx + s - 3, cy, fg, 2)
        cv.line(cx, cy - s + 3, cx, cy + s - 3, fg, 2)
        cv.disc(cx - s // 3, cy - s // 3, s // 4, fg)
        cv.disc(cx + s // 4, cy + s // 3, s // 5, fg)
    elif kind == 'chart':
        for i, h in enumerate((s // 3, 2 * s // 3, s)):
            cv.rect(cx - s + i * (2 * s // 3), cy + s - h, s // 2, h, fg)
        cv.line(cx - s, cy + s, cx + s, cy - s // 2, RED, 3)
    elif kind == 'gavel':
        cv.line(cx - s // 2, cy + s // 2, cx + s // 2, cy - s // 2, fg, 4)
        cv.rect(cx - s, cy - s // 2, s // 2, s // 3, fg)
        cv.rect(cx + s // 2, cy + s // 6, s // 2, s // 3, fg)
    elif kind == 'trophy':
        cv.rect(cx - s // 2, cy - s, s, s, fg)
        cv.rect(cx - s // 4, cy, s // 2, s // 3, fg)
        cv.rect(cx - s // 2, cy + s // 3, s, s // 4, fg)
        cv.disc(cx - s // 2 - 2, cy - s // 2, 3, fg)
        cv.disc(cx + s // 2 + 2, cy - s // 2, 3, fg)
    elif kind == 'moon':
        cv.disc(cx, cy, s, fg)
        cv.disc(cx + s // 2, cy - s // 4, s - 2, bg)
        for dx, dy in ((-s // 2, -s // 2), (s // 3, s // 2), (-s // 4, s // 2)):
            cv.disc(cx + dx, cy + dy, 2, GOLD)
    elif kind == 'train':
        cv.rect(cx - s, cy - s // 2, 2 * s, s, fg)
        cv.rect(cx - s // 2, cy - s // 2, s, s // 2, bg)
        cv.disc(cx - s // 2, cy + s // 2, 3, fg)
        cv.disc(cx + s // 2, cy + s // 2, 3, fg)
        cv.line(cx - s, cy + s, cx + s, cy + s, fg, 2)
    elif kind == 'crown':
        cv.poly([(cx - s, cy + s // 2), (cx - s, cy - s // 2),
                 (cx - s // 2, cy), (cx, cy - s), (cx + s // 2, cy),
                 (cx + s, cy - s // 2), (cx + s, cy + s // 2)], fg)
    elif kind == 'warning':
        cv.poly([(cx, cy - s), (cx + s, cy + s // 2), (cx - s, cy + s // 2)], fg)
        cv.vline(cx, cy - s // 2, s // 2, bg, 4)
        cv.disc(cx, cy + s // 3, 3, bg)
    elif kind == 'scales':
        cv.vline(cx, cy - s, 2 * s, fg, 3)
        cv.hline(cx - s, cy - s, 2 * s, fg, 3)
        cv.poly([(cx - s, cy - s), (cx - s // 2, cy), (cx - 3 * s // 2, cy)], fg)
        cv.poly([(cx + s, cy - s), (cx + s // 2, cy), (cx + 3 * s // 2, cy)], fg)
        cv.rect(cx - s // 3, cy + s // 2, 2 * s // 3, s // 4, fg)
    elif kind == 'people':
        cv.disc(cx - s // 2, cy - s // 3, s // 3, fg)
        cv.disc(cx + s // 2, cy - s // 3, s // 3, fg)
        cv.poly([(cx - s, cy + s), (cx - s // 2, cy), (cx, cy + s)], fg)
        cv.poly([(cx, cy + s), (cx + s // 2, cy), (cx + s, cy + s)], fg)
    elif kind == 'doc':
        cv.rect(cx - s // 2, cy - s, s, 2 * s, fg)
        for i in range(3):
            cv.hline(cx - s // 2 + 3, cy - s // 2 + i * 5, s - 6, bg, 2)
    elif kind == 'chip':
        cv.rect(cx - s // 2, cy - s // 2, s, s, fg)
        cv.rect(cx - s // 4, cy - s // 4, s // 2, s // 2, bg)
        for i in (-1, 0, 1):
            cv.hline(cx - s, cy + i * s // 3, s // 2, fg, 2)
            cv.hline(cx + s // 2, cy + i * s // 3, s // 2, fg, 2)
    elif kind == 'leaf':
        cv.poly([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fg)
        cv.line(cx, cy - s, cx, cy + s, bg, 2)
    elif kind == 'ballot':
        cv.rect(cx - s // 2, cy - s // 2, s, s, fg)
        cv.hline(cx - s // 2, cy - s // 2 + 2, s, bg, 2)
        cv.line(cx - s // 3, cy + s // 4, cx, cy + s // 2, bg, 3)
        cv.line(cx, cy + s // 2, cx + s // 2, cy - s // 4, bg, 3)
    elif kind == 'shield':
        cv.poly([(cx - s // 2, cy - s), (cx + s // 2, cy - s),
                 (cx + s // 2, cy), (cx, cy + s), (cx - s // 2, cy)], fg)
        cv.line(cx - s // 4, cy, cx, cy + s // 3, bg, 3)
        cv.line(cx, cy + s // 3, cx + s // 3, cy - s // 3, bg, 3)
    elif kind == 'factory':
        cv.rect(cx - s, cy, s, s, fg)
        cv.rect(cx, cy - s // 2, s, 3 * s // 2, fg)
        cv.rect(cx + s // 4, cy - s, s // 4, s // 2, fg)
        cv.poly([(cx - s, cy), (cx - s // 2, cy - s // 2), (cx, cy),
                 (cx + s // 2, cy - s // 2), (cx + s, cy)], bg)
    elif kind == 'megaphone':
        cv.poly([(cx - s, cy - s // 3), (cx + s // 3, cy - s),
                 (cx + s // 3, cy + s), (cx - s, cy + s // 3)], fg)
        cv.rect(cx - s, cy - s // 3, s // 3, 2 * s // 3, fg)
    elif kind == 'camera':
        cv.rect(cx - s, cy - s // 2, 2 * s, s, fg)
        cv.disc(cx, cy, s // 2, bg)
        cv.disc(cx, cy, s // 4, fg)
    elif kind == 'cricket':
        cv.line(cx - s // 2, cy - s, cx + s // 2, cy + s, fg, 4)
        cv.disc(cx + s // 3, cy - s // 3, s // 4, fg)
    else:  # 'dot'
        cv.disc(cx, cy, s // 2, fg)



# ---------------------------------------------------------------- stories
# (headline, summary, icon, accent) — every item is a real event of
# Tuesday 24 November 2026, as reported that day.
HERO = [
    ("INDONESIA FIRE KILLS 24",
     "Blaze rips through a candy factory; dozens still missing.",
     'flame', RED),
    ("KYIV REGION UNDER FIRE",
     "Russian drones and missiles kill at least 14; homes hit near the capital.",
     'burst', C_WORLD),
]

COLUMNS = [
    ("WORLD", C_WORLD, [
        ("RUSSIAN SHIP ABLAZE", "Cargo ship Sparta II burns after a drone strike.", 'ship'),
        ("NATO SENDS AWACS JETS", "Early-warning jets sent to Poland.", 'plane'),
        ("GAZA STRIKES KILL 3", "Israeli strikes kill 3, incl. UN worker.", 'burst'),
        ("SUDAN DRONES HIT UN", "Drones strike homes and a UN building in Sudan.", 'warning'),
        ("S. KOREA ALERT", "Evacuation alert as a Russian jet enters.", 'warning'),
        ("UK SANCTIONS MYANMAR", "Top generals hit after the Rohingya ruling.", 'scales'),
        ("TURKEY PROTESTS", "Thousands march over closure of media outlets.", 'people'),
        ("MEXICO NABS KINGPIN", "'Chapo Isidro' seized by elite troops with US help.", 'shield'),
        ("ARMENIA NEW CHARTER", "Draft charter aims to push peace with Azerbaijan.", 'doc'),
    ]),
    ("POLITICS & MARKETS", C_POL, [
        ("NVIDIA SOARS 31%", "Jensen Huang back as CEO; Nasdaq jumps 6.5%.", 'chart'),
        ("COP31 COLLAPSES", "Climate talks fail in Antalya over fossil fuels.", 'leaf'),
        ("TRUMP BLAMES DEMOCRATS", "President blames Democrats for $1tn sell-off.", 'megaphone'),
        ("STATES SUE MUSK", "US states sue over Grok's sexualised AI images.", 'gavel'),
        ("GOMEZ RESIGNS", "US congressman quits after ethics findings.", 'ballot'),
        ("MACRON EYES REFORM", "French president seeks curbs on state spending.", 'doc'),
        ("SENSEX TUMBLES", "Sensex down 1,484 points in a day.", 'chart'),
        ("UN: AI RULES IN A YEAR", "UN chief wants a global AI risk framework.", 'chip'),
        ("TRUMP PAUSES BLASTS", "US Army halts detonation of toxic lead azide.", 'warning'),
    ]),
    ("INDIA - SPORT - TECH", C_INDIA, [
        ("MODI MEETS NEPAL PM", "Eight pacts and a Rs 15,000-crore package.", 'globe'),
        ("AI CENTRE AT IIT PATNA", "Modi opens an AI hub and research park.", 'chip'),
        ("INDIA-CHINA TALKS", "Commanders meet in Arunachal to ease tension.", 'globe'),
        ("DEV DEEPAWALI", "Varanasi glows with lamps; Guru Nanak Jayanti.", 'flame'),
        ("INDIA v NZ DRAW", "First Test drawn; Pant hits a record 128.", 'cricket'),
        ("CHESS CROWN BEGINS", "Gukesh defends his title vs Sindarov in Geneva.", 'crown'),
        ("SUPERMOON TONIGHT", "A supermoon meets the Pleiades tonight.", 'moon'),
        ("CISCO + OPENAI", "Launch of Shirudo, self-defending security.", 'shield'),
        ("FERRARI UNVEILS 296", "Two new 296 models shown as marque revs up.", 'trophy'),
    ]),
]

# ---------------------------------------------------------------- layout
def draw_story(cv, x, y, w, head, summ, kind, accent):
    """One story block: icon top-left, headline beside it, summary below.
    Returns the y just below the block."""
    icon(cv, kind, x + 16, y + 15, 14, accent, WHITE)
    hx = x + 38
    hw = w - 38
    draw_para(cv, hx, y + 1, head, 2, INK, hw, lh=16)
    y2, _n = draw_para(cv, x, y + 34, summ, 2, GREY, w, lh=15)
    return y2 + 6


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.rect(0, 0, W, 108, NAVY)
    cv.rect(0, 108, W, 6, RED)
    draw_text_c(cv, W // 2, 12, "THE WORLD TODAY", 6, WHITE)
    draw_text_c(cv, W // 2, 58, "TUESDAY  -  24 NOVEMBER 2026", 3, GOLD)
    draw_text_c(cv, W // 2, 86, "THE DAY IN ONE IMAGE  -  29 STORIES FROM AROUND THE GLOBE",
                2, bytes((210, 220, 235)))

    # ---- hero: the two biggest stories ----
    hy, hh = 122, 148
    hw = (W - 24 * 2 - 12) // 2
    for i, (head, summ, kind, accent) in enumerate(HERO):
        x = 24 + i * (hw + 12)
        cv.rect(x, hy, hw, hh, WHITE)
        cv.rect(x, hy, hw, 6, accent)
        cv.rect(x, hy, 6, hh, accent)
        icon(cv, kind, x + 38, hy + 40, 26, accent, WHITE)
        draw_para(cv, x + 78, hy + 14, head, 4, INK, hw - 94, lh=34)
        draw_para(cv, x + 20, hy + 90, summ, 2, GREY, hw - 40, lh=18)
        draw_text(cv, x + 20, hy + hh - 20, "TOP STORY", 2, accent)

    # ---- three columns ----
    col_y = 280
    col_w = (W - 24 * 2 - 12 * 2) // 3
    for i, (title, accent, stories) in enumerate(COLUMNS):
        x = 24 + i * (col_w + 12)
        # section header bar
        cv.rect(x, col_y, col_w, 32, accent)
        draw_text_c(cv, x + col_w // 2, col_y + 7, title, 2, WHITE)
        y = col_y + 44
        for j, (head, summ, kind) in enumerate(stories):
            y = draw_story(cv, x, y, col_w, head, summ, kind, accent)
            if j < len(stories) - 1:
                cv.hline(x, y - 3, col_w, LINE, 1)

    # ---- footer ----
    fy = 960
    cv.rect(0, fy, W, H - fy, NAVY)
    cv.rect(0, fy, W, 4, GOLD)
    draw_text_c(cv, W // 2, fy + 14, "TUESDAY 24 NOVEMBER 2026  -  THE WORLD TODAY", 2, GOLD)
    draw_text_c(cv, W // 2, fy + 38,
                "EVENTS OF 24 NOVEMBER 2026 - AS REPORTED BY REUTERS, AP, BBC AND CNN",
                2, bytes((210, 220, 235)))
    return cv


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR')
    if not outdir and len(sys.argv) > 1:
        outdir = sys.argv[1]
    if not outdir:
        outdir = '/output'
    os.makedirs(outdir, exist_ok=True)
    cv = build()
    path = os.path.join(outdir, 'entry.png')
    n = write_png(path, cv)
    print(f"wrote {path} {cv.w}x{cv.h} {n} bytes")


if __name__ == '__main__':
    main()
