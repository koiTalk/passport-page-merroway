#!/usr/bin/env python3
"""Merroway Passport - The Passport Page of a Country That Isn't There.
Pure-stdlib procedural passport spread, 1024x1024 PNG, deterministic.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---
NAVY_DESK = (26, 36, 54)
PAGE = (244, 239, 228)
PAGE_EDGE = (232, 224, 205)
INK = (28, 42, 66)
INK_SOFT = (74, 92, 118)
GOLD = (176, 138, 62)
GOLD_SOFT = (198, 166, 96)
RULE = (150, 158, 168)
RED_BROWN = (146, 58, 44)
STAMP_BLUE = (58, 84, 120)
STAMP_FADE = (96, 118, 148)
SKIN = (214, 172, 134)
SKIN_DARK = (186, 140, 104)
HAIR = (58, 38, 30)
UNIFORM = (36, 54, 84)
SEA_GREY = (168, 178, 182)
STRIP = (238, 232, 214)

# --- MRZ (ICAO 9303, two lines of 44 chars) ---
MRZ1 = "P<MRWVOSS<<ELARA<MAREN<<<<<<<<<<<<<<<<<<<<<<"
MRZ2 = "MRW4829174MRW8706146F3403129<<<<<<<<<<<<<<04"

_WEIGHTS = (7, 3, 1)


def _mrz_val(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10 .. Z=35


def mrz_check(s):
    total = 0
    for i, ch in enumerate(s):
        total += _mrz_val(ch) * _WEIGHTS[i % 3]
    return total % 10


# NOTE: the brief's stated composite check "2" is wrong. Recomputed twice
# by hand (weights 7,3,1): composite sum = 574, 574 % 10 = 4. The other
# four check digits (4, 6, 9, 0) match the brief exactly. MRZ2 therefore
# ends in "04" so the MRZ verifies under ICAO 9303.
assert len(MRZ1) == 44 and len(MRZ2) == 44
assert mrz_check(MRZ2[0:9]) == int(MRZ2[9]), "doc number check"
assert mrz_check(MRZ2[13:19]) == int(MRZ2[19]), "dob check"
assert mrz_check(MRZ2[21:27]) == int(MRZ2[27]), "expiry check"
assert mrz_check(MRZ2[28:42]) == int(MRZ2[42]), "personal check"
_comp = MRZ2[0:10] + MRZ2[13:20] + MRZ2[21:28] + MRZ2[28:43]
assert mrz_check(_comp) == int(MRZ2[43]), "composite check"

# --- 5x7 bitmap font ('#' = on, '.' = off) ---
FONT = {
"A": ("01110","10001","10001","11111","10001","10001","10001"),
"B": ("11110","10001","10001","11110","10001","10001","11110"),
"C": ("01110","10001","10000","10000","10000","10001","01110"),
"D": ("11110","10001","10001","10001","10001","10001","11110"),
"E": ("11111","10000","10000","11110","10000","10000","11111"),
"F": ("11111","10000","10000","11110","10000","10000","10000"),
"G": ("01110","10001","10000","10111","10001","10001","01111"),
"H": ("10001","10001","10001","11111","10001","10001","10001"),
"I": ("01110","00100","00100","00100","00100","00100","01110"),
"J": ("00111","00010","00010","00010","00010","10010","01100"),
"K": ("10001","10010","10100","11000","10100","10010","10001"),
"L": ("10000","10000","10000","10000","10000","10000","11111"),
"M": ("10001","11011","10101","10101","10001","10001","10001"),
}
FONT.update({
"N": ("10001","11001","10101","10011","10001","10001","10001"),
"O": ("01110","10001","10001","10001","10001","10001","01110"),
"P": ("11110","10001","10001","11110","10000","10000","10000"),
"Q": ("01110","10001","10001","10001","10101","10010","01101"),
"R": ("11110","10001","10001","11110","10100","10010","10001"),
"S": ("01111","10000","10000","01110","00001","00001","11110"),
"T": ("11111","00100","00100","00100","00100","00100","00100"),
"U": ("10001","10001","10001","10001","10001","10001","01110"),
"V": ("10001","10001","10001","10001","10001","01010","00100"),
"W": ("10001","10001","10001","10101","10101","11011","10001"),
"X": ("10001","10001","01010","00100","01010","10001","10001"),
"Y": ("10001","10001","01010","00100","00100","00100","00100"),
"Z": ("11111","00001","00010","00100","01000","10000","11111"),
"0": ("01110","10001","10011","10101","11001","10001","01110"),
"1": ("00100","01100","00100","00100","00100","00100","01110"),
"2": ("01110","10001","00001","00110","01000","10000","11111"),
"3": ("11111","00010","00100","00010","00001","10001","01110"),
"4": ("00010","00110","01010","10010","11111","00010","00010"),
"5": ("11111","10000","11110","00001","00001","10001","01110"),
"6": ("00110","01000","10000","11110","10001","10001","01110"),
"7": ("11111","00001","00010","00100","01000","01000","01000"),
"8": ("01110","10001","10001","01110","10001","10001","01110"),
"9": ("01110","10001","10001","01111","00001","00010","01100"),
" ": ("00000","00000","00000","00000","00000","00000","00000"),
})
FONT.update({
".": ("00000","00000","00000","00000","00000","01100","01100"),
",": ("00000","00000","00000","00000","01100","00100","01000"),
"-": ("00000","00000","00000","01110","00000","00000","00000"),
"/": ("00001","00010","00010","00100","01000","01000","10000"),
"<": ("00010","00100","01000","10000","01000","00100","00010"),
">": ("01000","00100","00010","00001","00010","00100","01000"),
"(": ("00010","00100","01000","01000","01000","00100","00010"),
")": ("01000","00100","00010","00010","00010","00100","01000"),
":": ("00000","01100","01100","00000","01100","01100","00000"),
"·": ("00000","00000","01100","01100","00000","00000","00000"),
"—": ("00000","00000","00000","11111","00000","00000","00000"),
"Æ": ("01111","10001","10001","11111","10101","10001","10001"),
"Þ": ("11100","10101","10101","11110","10100","10100","10100"),
"Ø": ("01110","10001","10101","10011","10101","10001","01110"),
"Ð": ("01110","10001","10001","11111","10001","10001","01110"),
"É": ("00100","00000","11111","10000","11110","10000","11111"),
"Á": ("00100","00000","01110","10001","11111","10001","10001"),
"Ú": ("00100","00000","10001","10001","10001","10001","01110"),
"Í": ("00100","00000","01110","00100","00100","00100","01110"),
})

# --- raster engine ---
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg[0] for _ in range(w * h))
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3:i * 3 + 3] = bytes(bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return tuple(self.px[i:i + 3])

    def blend(self, x, y, c, a):
        """Blend colour c over pixel with alpha a (0..1)."""
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            for k in range(3):
                self.px[i + k] = int(self.px[i + k] * (1 - a) + c[k] * a)

    def rect(self, x0, y0, x1, y1, c):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            row = bytes(c) * (x1 - x0)
            self.px[i:i + len(row)] = row

    def hline(self, x0, x1, y, c, th=1):
        for t in range(th):
            self.rect(x0, y + t, x1, y + t + 1, c)

    def vline(self, x, y0, y1, c, th=1):
        for t in range(th):
            self.rect(x + t, y0, x + t + 1, y1, c)

    def line(self, x0, y0, x1, y1, c, th=1):
        dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(th):
                for b in range(th):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(x, y, c)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, fill=True):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                v = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if fill:
                    if v <= 1.0:
                        self.set(x, y, c)
                else:
                    if 0.85 <= v <= 1.15:
                        self.set(x, y, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
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
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), y, int(xs[k + 1]) + 1, y + 1, c)

    def rrect(self, x0, y0, x1, y1, r, c, fill=False, th=2):
        if fill:
            self.rect(x0 + r, y0, x1 - r, y1, c)
            self.rect(x0, y0 + r, x1, y1 - r, c)
            for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                           (x0 + r, y1 - r), (x1 - r, y1 - r)):
                self.circle(cx, cy, r, c)
            return
        self.hline(x0 + r, x1 - r, y0, c, th)
        self.hline(x0 + r, x1 - r, y1 - th, c, th)
        self.vline(x0, y0 + r, y1 - r, c, th)
        self.vline(x1 - th, y0 + r, y1 - r, c, th)
        import math
        corners = ((x0 + r, y0 + r, 180, 270), (x1 - r, y0 + r, 270, 360),
                   (x0 + r, y1 - r, 90, 180), (x1 - r, y1 - r, 0, 90))
        for cx, cy, a0, a1 in corners:
            for a in range(a0, a1 + 1, 4):
                t = math.radians(a)
                self.set(int(cx + r * math.cos(t)), int(cy + r * math.sin(t)), c)


def paper_noise(cv, x0, y0, x1, y1, amt=5):
    """Deterministic paper grain from a hash of (x, y)."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            h = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
            h ^= h >> 13
            h = (h * 1274126177) & 0xFFFFFFFF
            n = (h >> 24) % (amt * 2 + 1) - amt
            if n:
                r, g, b = cv.get(x, y)
                cv.set(x, y, (max(0, min(255, r + n)),
                              max(0, min(255, g + n)),
                              max(0, min(255, b + n))))


# --- PNG writer (filter 0, deterministic) ---
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)

# --- text ---
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color, bold=False):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            cv.set(cx + gx * scale + dx, y + gy * scale + dy, color)
                            if bold:
                                cv.set(cx + gx * scale + dx + 1, y + gy * scale + dy, color)
        cx += 6 * scale
    return cx


def draw_center(cv, cx, y, s, scale, color, bold=False):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color, bold)


def wrap_text(cv, x, y, s, scale, color, max_w, lh=None, bold=False):
    """Greedy word wrap; returns y after last line."""
    lh = lh or (9 * scale)
    words = s.split(" ")
    line = ""
    for wd in words:
        trial = (line + " " + wd).strip()
        if text_w(trial, scale) <= max_w or not line:
            line = trial
        else:
            draw_text(cv, x, y, line, scale, color, bold)
            y += lh
            line = wd
    if line:
        draw_text(cv, x, y, line, scale, color, bold)
        y += lh
    return y


def field(cv, x, y, label, sub, value, vscale=2, w=200):
    """Label (small caps + Merroweg sub) above a value with baseline rule."""
    draw_text(cv, x, y, label, 1, INK_SOFT)
    if sub:
        draw_text(cv, x + text_w(label, 1) + 8, y, sub, 1, GOLD)
    draw_text(cv, x, y + 10, value, vscale, INK, bold=(vscale >= 2))
    cv.hline(x, x + w, y + 10 + 7 * vscale + 4, RULE)
    return y + 10 + 7 * vscale + 10

# --- coat of arms: lighthouse tower + waves + two stars ---
def draw_arms(cv, cx, cy, s):
    """s = overall size (height). Navy + gold emblem."""
    u = s / 40.0
    # shield outline
    pts = [(cx - 16 * u, cy - 18 * u), (cx + 16 * u, cy - 18 * u),
           (cx + 16 * u, cy + 6 * u), (cx, cy + 20 * u),
           (cx - 16 * u, cy + 6 * u)]
    cv.poly([(int(a), int(b)) for a, b in pts], (226, 214, 178))
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.line(int(x0), int(y0), int(x1), int(y1), GOLD, 2)
    # two stars
    for sx in (cx - 9 * u, cx + 9 * u):
        cv.circle(int(sx), int(cy - 12 * u), int(2.2 * u), GOLD)
    # lighthouse tower
    tx0, tx1 = cx - 4 * u, cx + 4 * u
    cv.poly([(int(tx0), int(cy + 10 * u)), (int(tx1), int(cy + 10 * u)),
             (int(cx + 2.5 * u), int(cy - 6 * u)),
             (int(cx - 2.5 * u), int(cy - 6 * u))], INK)
    cv.rect(int(cx - 5 * u), int(cy - 10 * u), int(cx + 5 * u), int(cy - 6 * u), GOLD)
    cv.circle(int(cx), int(cy - 11 * u), int(2 * u), GOLD)
    # light rays
    cv.line(int(cx - 6 * u), int(cy - 9 * u), int(cx - 13 * u), int(cy - 12 * u), GOLD, 1)
    cv.line(int(cx + 6 * u), int(cy - 9 * u), int(cx + 13 * u), int(cy - 12 * u), GOLD, 1)
    # waves
    for wy in (cy + 12 * u, cy + 16 * u):
        for k in range(-14, 15, 4):
            cv.line(int(cx + k * u), int(wy), int(cx + (k + 2) * u), int(wy), INK, 1)


# --- portrait: lighthouse keeper, flat colours ---
def draw_portrait(cv, x0, y0, x1, y1, ghost=False):
    """Portrait inside frame (x0,y0)-(x1,y1). ghost=True: low-opacity silhouette."""
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) // 2
    if ghost:
        # soft silhouette: head + shoulders + bun, blended faintly
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                d_head = ((xx - cx) / (w * 0.30)) ** 2 + ((yy - (y0 + h * 0.42)) / (h * 0.26)) ** 2
                d_bun = ((xx - cx) / (w * 0.13)) ** 2 + ((yy - (y0 + h * 0.13)) / (h * 0.11)) ** 2
                d_sh = ((xx - cx) / (w * 0.48)) ** 2 + ((yy - (y0 + h * 0.95)) / (h * 0.42)) ** 2
                if d_head <= 1 or d_bun <= 1 or d_sh <= 1:
                    cv.blend(xx, yy, INK_SOFT, 0.13)
        return
    cv.rect(x0, y0, x1, y1, SEA_GREY)
    # faint horizon + sea lines in background
    cv.hline(x0, x1, y0 + int(h * 0.62), (150, 162, 166), 2)
    cv.hline(x0, x1, y0 + int(h * 0.70), (138, 150, 156), 2)
    # shoulders / navy uniform
    sh_y = y0 + int(h * 0.66)
    cv.poly([(x0, y1), (x1, y1), (x1, sh_y + 14),
             (cx + int(w * 0.30), sh_y), (cx - int(w * 0.30), sh_y),
             (x0, sh_y + 14)], UNIFORM)
    # collar V + brass button
    cv.poly([(cx - 16, sh_y + 2), (cx + 16, sh_y + 2), (cx, sh_y + 34)], (240, 236, 222))
    cv.poly([(cx - 16, sh_y + 2), (cx, sh_y + 34), (cx - 16, sh_y + 40)], (200, 196, 182))
    cv.poly([(cx + 16, sh_y + 2), (cx, sh_y + 34), (cx + 16, sh_y + 40)], (200, 196, 182))
    cv.circle(cx, sh_y + 52, 5, GOLD)
    cv.circle(cx, sh_y + 52, 2, (140, 104, 40))
    # neck
    cv.rect(cx - 11, y0 + int(h * 0.52), cx + 11, sh_y + 4, SKIN_DARK)
    # head
    hy = y0 + int(h * 0.34)
    cv.ellipse(cx, hy, int(w * 0.26), int(h * 0.22), SKIN)
    # jaw shading
    cv.ellipse(cx, hy + int(h * 0.10), int(w * 0.20), int(h * 0.12), SKIN_DARK)
    cv.ellipse(cx, hy + int(h * 0.04), int(w * 0.22), int(h * 0.14), SKIN)
    # hair: dark, swept back + bun (hairline kept above the brows)
    cv.ellipse(cx, hy - int(h * 0.14), int(w * 0.27), int(h * 0.10), HAIR)
    cv.circle(cx, y0 + int(h * 0.10), int(w * 0.11), HAIR)
    cv.rect(cx - int(w * 0.27), hy - int(h * 0.18), cx - int(w * 0.20), hy - int(h * 0.05), HAIR)
    cv.rect(cx + int(w * 0.20), hy - int(h * 0.18), cx + int(w * 0.27), hy - int(h * 0.05), HAIR)
    # forehead re-carve so the hairline curves and the brows show
    cv.ellipse(cx, hy - int(h * 0.03), int(w * 0.20), int(h * 0.06), SKIN)
    # eyes
    for ex in (cx - int(w * 0.11), cx + int(w * 0.11)):
        cv.ellipse(ex, hy - int(h * 0.02), 5, 3, (255, 255, 255))
        cv.circle(ex, hy - int(h * 0.02), 2, (30, 32, 40))
        cv.hline(ex - 6, ex + 6, hy - int(h * 0.045), HAIR, 2)
    # brows, nose, mouth
    cv.line(cx - int(w * 0.15), hy - int(h * 0.075), cx - int(w * 0.07), hy - int(h * 0.085), HAIR, 2)
    cv.line(cx + int(w * 0.07), hy - int(h * 0.085), cx + int(w * 0.15), hy - int(h * 0.075), HAIR, 2)
    cv.line(cx, hy + int(h * 0.01), cx - 2, hy + int(h * 0.07), SKIN_DARK, 2)
    cv.line(cx - 8, hy + int(h * 0.13), cx + 8, hy + int(h * 0.13), (150, 84, 74), 2)
    # cheek blush
    cv.ellipse(cx - int(w * 0.17), hy + int(h * 0.07), 7, 4, (206, 140, 118))
    cv.ellipse(cx + int(w * 0.17), hy + int(h * 0.07), 7, 4, (206, 140, 118))
    # tiny lighthouse pin on collar
    cv.rect(cx + 22, sh_y + 18, cx + 26, sh_y + 30, GOLD)
    cv.circle(cx + 24, sh_y + 15, 2, GOLD)

# --- guilloche + signature ---
def guilloche(cv, x0, y0, x1, y1):
    import math
    faint = (228, 221, 202)
    for k in range(-(y1 - y0), x1 - x0, 14):
        prev = None
        for t in range(0, (y1 - y0) + 1, 6):
            x = x0 + k + t
            y = y0 + t + int(3 * math.sin(t / 18.0))
            if x0 <= x < x1 and y0 <= y < y1:
                if prev is not None:
                    cv.line(prev[0], prev[1], x, y, faint, 1)
                prev = (x, y)
            else:
                prev = None


def draw_signature(cv, x0, y0, x1, y1):
    """Flowing cursive-ish signature stroke for Elara Voss."""
    ink = (32, 54, 110)
    w, h = x1 - x0, y1 - y0
    # capital E loop
    pts = [(0.06, 0.55), (0.10, 0.30), (0.16, 0.22), (0.22, 0.30),
           (0.16, 0.48), (0.10, 0.55), (0.18, 0.62), (0.24, 0.55),
           (0.20, 0.75), (0.12, 0.80)]
    # 'lara' humps
    pts += [(0.28, 0.60), (0.32, 0.40), (0.36, 0.60), (0.40, 0.42),
            (0.44, 0.60), (0.48, 0.40), (0.52, 0.62)]
    # tall 'V' of Voss + 'oss' humps
    pts += [(0.58, 0.25), (0.62, 0.70), (0.68, 0.25), (0.72, 0.60),
            (0.76, 0.42), (0.80, 0.60), (0.84, 0.42), (0.88, 0.60)]
    # underline flourish
    pts += [(0.94, 0.45), (0.70, 0.85), (0.40, 0.88), (0.10, 0.82)]
    for i in range(len(pts) - 1):
        ax = x0 + int(pts[i][0] * w); ay = y0 + int(pts[i][1] * h)
        bx = x0 + int(pts[i + 1][0] * w); by = y0 + int(pts[i + 1][1] * h)
        cv.line(ax, ay, bx, by, ink, 2)


def draw_mrz(cv, cx, y, s, scale_y=2):
    """MRZ with 9px pitch, glyph 5 wide x 14 tall."""
    for line, yy in ((MRZ1, y), (MRZ2, y + 26)):
        x = cx - (44 * 9 - 3) // 2
        for ch in line:
            glyph = FONT.get(ch, FONT[" "])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        for dy in range(scale_y):
                            cv.set(x + gx, yy + gy * scale_y + dy, INK)
            x += 9

# --- left page: data page ---
def draw_left_page(cv):
    x0, y0, x1, y1 = 40, 40, 500, 984
    cv.rect(x0, y0, x1, y1, PAGE)
    guilloche(cv, x0 + 10, y0 + 10, x1 - 10, y1 - 10)
    # faint watermark emblem at centre
    wc = (232, 226, 210)
    cv.circle(270, 640, 95, wc, fill=False)
    cv.circle(270, 640, 82, wc, fill=False)
    cv.poly([(262, 690), (278, 690), (274, 600), (266, 600)], wc)
    cv.rect(260, 592, 280, 600, wc)
    # borders
    cv.rect(x0 + 6, y0 + 6, x1 - 6, y1 - 6, PAGE_EDGE)
    cv.rect(x0 + 6, y0 + 6, x1 - 6, y1 - 6, PAGE)
    for bx0, by0, bx1, by1 in ((x0 + 10, y0 + 10, x1 - 10, y1 - 10),
                               (x0 + 14, y0 + 14, x1 - 14, y1 - 14)):
        cv.hline(bx0, bx1, by0, GOLD, 2)
        cv.hline(bx0, bx1, by1 - 2, GOLD, 2)
        cv.vline(bx0, by0, by1, GOLD, 2)
        cv.vline(bx1 - 2, by0, by1, GOLD, 2)
    # coat of arms + headings
    draw_arms(cv, 270, 92, 62)
    draw_center(cv, 270, 132, "REPUBLIC OF MERROWAY", 2, INK, bold=True)
    draw_center(cv, 270, 156, "FARARBRÉF · PASSPORT", 2, GOLD)
    cv.hline(90, 450, 182, INK_SOFT, 2)
    # portrait
    cv.rect(66, 206, 254, 434, INK)
    draw_portrait(cv, 70, 210, 250, 430)
    draw_center(cv, 160, 440, "PHOTOGRAPH / MYND", 1, INK_SOFT)
    # fields right of portrait
    fx, fw = 272, 196
    y = 206
    y = field(cv, fx, y, "SURNAME", "ÆTTARNAMN", "VOSS", 2, fw)
    y = field(cv, fx, y, "GIVEN NAMES", "FORNAMN", "ELARA MAREN", 2, fw)
    y = field(cv, fx, y, "NATIONALITY", "ÞJÓÐERNI", "MERROWAY", 2, fw)
    y = field(cv, fx, y, "DATE OF BIRTH", "FØÐINGARDAGUR", "14 JUN 1987", 2, fw)
    y = field(cv, fx, y, "SEX", "KYN", "F", 2, fw)
    # lower fields, two columns
    y2 = 478
    field(cv, 70, y2, "PLACE OF BIRTH", "FØÐINGARSTAÐUR", "TIDEHAVEN", 2, 190)
    field(cv, 280, y2, "DATE OF ISSUE", "ÚTGÁFUDAGUR", "12 MAR 2024", 2, 188)
    y2 = 528
    field(cv, 70, y2, "DATE OF EXPIRY", "GILDISTÍMI", "12 MAR 2034", 2, 190)
    field(cv, 280, y2, "PASSPORT NO.", "", "MRW482917", 2, 188)
    y2 = 578
    field(cv, 70, y2, "AUTHORITY", "YFIRVALD", "TIDEHAVEN PASSPORT OFFICE", 2, 398)
    # occupation line
    draw_text(cv, 70, 636, "OCCUPATION", 1, INK_SOFT)
    draw_text(cv, 70, 650, "LIGHTHOUSE KEEPER, TIDEHAVEN LIGHT", 1, INK)
    # signature box (left) + ghost portrait (right)
    draw_text(cv, 70, 700, "SIGNATURE / UNDIRSKRIFT", 1, INK_SOFT)
    cv.rect(70, 714, 300, 796, (255, 255, 255))
    cv.hline(70, 300, 714, INK_SOFT, 1)
    cv.hline(70, 300, 795, INK_SOFT, 1)
    cv.vline(70, 714, 796, INK_SOFT, 1)
    cv.vline(299, 714, 796, INK_SOFT, 1)
    draw_signature(cv, 80, 722, 292, 788)
    draw_text(cv, 330, 700, "GHOST IMAGE", 1, INK_SOFT)
    cv.rect(330, 714, 470, 796, (250, 247, 238))
    draw_portrait(cv, 330, 714, 470, 796, ghost=True)
    # MRZ strip
    cv.rect(56, 884, 484, 968, STRIP)
    cv.hline(56, 484, 884, INK_SOFT, 2)
    draw_mrz(cv, 270, 898, 2)

# --- right page: visas / stamps ---
STAMPS = [
    ("SELKIE", "ENTRY", "PORT SELKIE", "02 APR 2024"),
    ("SELKIE", "EXIT", "PORT SELKIE", "09 APR 2024"),
    ("KERGALLEN", "ENTRY", "KERGALLEN HARBOUR", "19 JUN 2025"),
    ("KERGALLEN", "EXIT", "KERGALLEN HARBOUR", "26 JUN 2025"),
    ("SELKIE", "ENTRY", "PORT SELKIE", "07 OCT 2026"),
    ("MERROWAY", "ENTRY", "TIDEHAVEN", "14 OCT 2026"),
]


def draw_stamp(cv, x0, y0, x1, y1, name, kind, port, date):
    cv.rrect(x0, y0, x1, y1, 10, STAMP_BLUE, th=2)
    # anchor glyph
    ax, ay = x0 + 26, y0 + 30
    cv.circle(ax, ay - 6, 4, STAMP_BLUE)
    cv.vline(ax, ay - 2, ay + 16, STAMP_BLUE, 2)
    cv.hline(ax - 10, ax + 10, ay + 12, STAMP_BLUE, 2)
    cv.line(ax - 10, ay + 12, ax - 6, ay + 4, STAMP_BLUE, 2)
    cv.line(ax + 10, ay + 12, ax + 6, ay + 4, STAMP_BLUE, 2)
    tx = x0 + 48
    draw_text(cv, tx, y0 + 12, name, 2, STAMP_BLUE, bold=True)
    draw_text(cv, tx, y0 + 32, kind, 2, STAMP_BLUE, bold=True)
    draw_text(cv, x0 + 12, y0 + 64, port, 1, STAMP_FADE)
    draw_text(cv, x0 + 12, y0 + 78, date, 1, STAMP_BLUE, bold=True)
    # officer scribble
    sx = x0 + 12
    sy = y1 - 18
    pts = [(sx, sy), (sx + 12, sy - 5), (sx + 24, sy + 2),
           (sx + 36, sy - 4), (sx + 48, sy + 1), (sx + 58, sy - 3)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], STAMP_FADE, 1)


def draw_right_page(cv):
    x0, y0, x1, y1 = 524, 40, 984, 984
    cv.rect(x0, y0, x1, y1, PAGE)
    paper_noise(cv, x0, y0, x1, y1, amt=3)
    for bx0, by0, bx1, by1 in ((x0 + 10, y0 + 10, x1 - 10, y1 - 10),
                               (x0 + 14, y0 + 14, x1 - 14, y1 - 14)):
        cv.hline(bx0, bx1, by0, GOLD, 2)
        cv.hline(bx0, bx1, by1 - 2, GOLD, 2)
        cv.vline(bx0, by0, by1, GOLD, 2)
        cv.vline(bx1 - 2, by0, by1, GOLD, 2)
    draw_center(cv, 754, 62, "VISAS / VEGABRÉF", 2, INK, bold=True)
    cv.hline(590, 918, 88, INK_SOFT, 2)
    # visa box
    vx0, vy0, vx1, vy1 = 560, 108, 948, 268
    cv.rect(vx0, vy0, vx1, vy1, (252, 248, 238))
    cv.hline(vx0, vx1, vy0, RED_BROWN, 3)
    cv.hline(vx0, vx1, vy1 - 3, RED_BROWN, 3)
    cv.vline(vx0, vy0, vy1, RED_BROWN, 3)
    cv.vline(vx1 - 3, vy0, vy1, RED_BROWN, 3)
    draw_center(cv, 754, 122, "VISITOR VISA — KERGALLEN", 2, RED_BROWN, bold=True)
    draw_center(cv, 754, 150, "ISSUED 03 JUN 2025", 2, INK)
    draw_center(cv, 754, 176, "VALID 03 JUN 2025 - 03 DEC 2025", 2, INK)
    draw_center(cv, 754, 202, "SINGLE ENTRY", 2, INK)
    draw_center(cv, 754, 232, "VALID FOR TRAVEL BY SEA ONLY —", 1, RED_BROWN, bold=True)
    draw_center(cv, 754, 246, "MERROWAY HAS NO AIRFIELD", 1, RED_BROWN, bold=True)
    # tide notice
    tx0, ty0, tx1, ty1 = 560, 288, 948, 372
    cv.rect(tx0, ty0, tx1, ty1, (250, 248, 240))
    cv.hline(tx0, tx1, ty0, INK, 2)
    cv.hline(tx0, tx1, ty1 - 2, INK, 2)
    cv.vline(tx0, ty0, ty1, INK, 2)
    cv.vline(tx1 - 2, ty0, ty1, INK, 2)
    draw_center(cv, 754, 300, "TIDE NOTICE", 2, INK, bold=True)
    draw_center(cv, 754, 326, "HOLDERS CROSSING BY THE CAUSEWAY", 1, INK)
    draw_center(cv, 754, 340, "MUST CROSS BEFORE 17:40 — THE", 1, INK)
    draw_center(cv, 754, 354, "ROAD FLOODS AT HIGH TIDE.", 1, INK)
    # stamps: 2 columns x 3 rows
    sw, sh = 186, 116
    for i, (name, kind, port, date) in enumerate(STAMPS):
        col, row = i % 2, i // 2
        sx0 = 560 + col * (sw + 16)
        sy0 = 400 + row * (sh + 22)
        draw_stamp(cv, sx0, sy0, sx0 + sw, sy0 + sh, name, kind, port, date)
    # fee stamp
    fx0, fy0, fx1, fy1 = 560, 876, 948, 932
    cv.rrect(fx0, fy0, fx1, fy1, 6, RED_BROWN, th=2)
    draw_center(cv, 754, 898, "FEE PAID — 12 KERGALLEN CROWNS — 03 JUN 2025", 1, RED_BROWN, bold=True)

# --- book assembly + main ---
def main():
    cv = Canvas(W, H, NAVY_DESK)
    # desk vignette: soft darker corners
    for y in range(H):
        for x in range(W):
            d = max(abs(x - 512), abs(y - 512))
            if d > 470:
                cv.blend(x, y, (10, 14, 24), min(0.35, (d - 470) / 120.0))
    # centre gutter shadow
    cv.rect(500, 40, 524, 984, (120, 110, 88))
    cv.rect(504, 40, 520, 984, (96, 88, 70))
    cv.rect(498, 40, 500, 984, (60, 54, 44))
    cv.rect(524, 40, 526, 984, (60, 54, 44))
    draw_left_page(cv)
    draw_right_page(cv)
    # gutter shadow over the page seam
    for x in range(500, 524):
        a = 0.28 * (1 - abs(x - 512) / 12.0)
        for y in range(40, 984):
            cv.blend(x, y, (40, 34, 26), a)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    write_png(cv, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
