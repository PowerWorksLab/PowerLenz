"""The Sixteen Amps identity: colours, type, and logo layouts as merged vector outlines.

Needs KiCad's pcbnew module (polygon union), PangoCairo, and the files in fonts/.
"""
import json
import math
import os
import re
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent

# let Pango see the bundled fonts without installing them (must happen before outline is imported)
_conf = Path(tempfile.mkdtemp()) / "fonts.conf"
_conf.write_text(f'<?xml version="1.0"?><fontconfig><dir>{SRC}/fonts/ttf</dir><cachedir>{_conf.parent}</cachedir></fontconfig>')
os.environ["FONTCONFIG_FILE"] = str(_conf)

import pcbnew  # noqa: E402

from outline import outline  # noqa: E402

NAVY, BRASS, TINT, PAPER, WHITE, BLACK = "#14213D", "#C9A66B", "#F1EADB", "#F7F5F0", "#FFFFFF", "#000000"
QUIET = "#68748F"   # secondary chart bars
DATA = {"Normal": "#1A9D5C", "High": "#F2A900", "Fault": "#C62828", "Other": "#8F949E"}
# variant name -> (logo colour, colour of the dot on the i)
VARIANTS = {"navy": (NAVY, NAVY), "on-navy": (WHITE, BRASS), "black": (BLACK, BLACK), "white": (WHITE, WHITE)}

WEBFONTS = json.loads((SRC / "fonts/fonts.json").read_text())
FONT_CSS = "".join(WEBFONTS.values())

SYMBOL = re.search(r' d="([^"]+)"', (SRC / "symbol.svg").read_text()).group(1)
TRACK, SIZE, GAP, SC = -0.02, 200, 58, 1000


def text(s, weight):
    return outline(s, weight, TRACK, SIZE)


def _wordmark():
    first = "sıxteen "
    period = text(".", 600)[1]
    advance = text(first + ".", 600)[1][2] - period[2]          # where "amps" starts
    d1, b1 = text("sıxteen", 600)
    d2, b2 = text("amps", 600)
    stem = text("ı", 600)[1]
    before = text("s.", 600)[1][2] - period[2]
    r = (stem[2] - stem[0]) * 0.64
    dot = (before + (stem[0] + stem[2]) / 2, stem[1] - r * 1.55, r)
    box = (b1[0], min(b1[1], b2[1], dot[1] - r), advance + b2[2], max(b1[3], b2[3]))
    return [(d1, 0, 0, 1), (d2, advance, 0, 1)], dot, box, -text("l", 600)[1][1], stem[2] - stem[0]


_PIECES, _DOT, _BOX, ASC, STEM = _wordmark()
SYM_H = ASC * 1.04
SYM_W = SYM_H * 174 / 171


def _symbol(x, y, h):
    s = h / 171
    return (SYMBOL, x - 13 * s, y - 10 * s, s)


def _move(layout, dx, dy, k=1.0):
    pieces, dots, box = layout
    return ([(d, dx + x * k, dy + y * k, s * k) for d, x, y, s in pieces],
            [(dx + x * k, dy + y * k, r * k) for x, y, r in dots],
            (dx + box[0] * k, dy + box[1] * k, dx + box[2] * k, dy + box[3] * k))


def _union(*boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def _layouts():
    name = (list(_PIECES), [_DOT], _BOX)
    x = _BOX[0] - GAP - SYM_W
    logo = ([_symbol(x, -SYM_H, SYM_H)] + _PIECES, [_DOT], (x, min(_BOX[1], -SYM_H), _BOX[2], _BOX[3]))
    w = (_BOX[2] - _BOX[0]) * 0.22
    h = w * 171 / 174
    top = _BOX[1] - ASC * 0.42 - h
    stacked = ([_symbol(_BOX[0] + (_BOX[2] - _BOX[0] - w) / 2, top, h)] + _PIECES, [_DOT], (_BOX[0], top, _BOX[2], _BOX[3]))
    symbol = ([_symbol(0, 0, 171)], [], (0, 0, 174, 171))
    d, b = text("by", 500)
    shift = logo[2][0] - GAP - b[2]
    endorsement = ([(d, shift, 0, 1)] + logo[0], logo[1], _union(logo[2], (shift + b[0], b[1], shift + b[2], b[3])))
    d, b = text("PowerLenz", 700)
    k = 0.5
    small = _move(endorsement, b[0] - endorsement[2][0] * k, b[3] + 46 - endorsement[2][1] * k, k)
    lockup = ([(d, 0, 0, 1)] + small[0], small[1], _union(b, small[2]))
    return {"logo": logo, "stacked": stacked, "wordmark": name, "symbol": symbol,
            "endorsement": endorsement, "powerlenz-lockup": lockup}


def _contours(d, tx, ty, s):
    """Flattens absolute M, L, C, Z path data into point lists."""
    out, pts, cur = [], [], (0.0, 0.0)

    def at(x, y):
        return (x * s + tx, y * s + ty)

    for cmd, args in re.findall(r"([MLCZ])([^MLCZ]*)", d):
        v = [float(a) for a in re.findall(r"-?\d+(?:\.\d+)?", args)]
        if cmd == "M":
            if pts:
                out.append(pts)
            cur = (v[0], v[1])
            pts = [at(*cur)]
        elif cmd == "L":
            for i in range(0, len(v), 2):
                cur = (v[i], v[i + 1])
                pts.append(at(*cur))
        elif cmd == "C":
            for i in range(0, len(v), 6):
                p = [cur, (v[i], v[i + 1]), (v[i + 2], v[i + 3]), (v[i + 4], v[i + 5])]
                for k in range(1, 49):
                    u = k / 48
                    pts.append(at(*[(1 - u) ** 3 * p[0][j] + 3 * (1 - u) ** 2 * u * p[1][j]
                                    + 3 * (1 - u) * u * u * p[2][j] + u ** 3 * p[3][j] for j in (0, 1)]))
                cur = p[3]
        elif cmd == "Z" and pts:
            out.append(pts)
            pts = []
    if pts:
        out.append(pts)
    return [c for c in out if len(c) > 2]


def _area(p):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1])) / 2


def _polyset(points):
    ps = pcbnew.SHAPE_POLY_SET()
    ps.NewOutline()
    for x, y in points:
        ps.Append(int(round(x * SC)), int(round(y * SC)))
    return ps


def merge(pieces, dots=()):
    """Union of all pieces (and optionally the dots) with letter holes preserved."""
    total = pcbnew.SHAPE_POLY_SET()
    for d, x, y, s in pieces:
        contours = _contours(d, x, y, s)
        solid_sign = math.copysign(1, _area(max(contours, key=lambda c: abs(_area(c)))))
        solid, holes = pcbnew.SHAPE_POLY_SET(), pcbnew.SHAPE_POLY_SET()
        for c in contours:
            (solid if _area(c) * solid_sign > 0 else holes).BooleanAdd(_polyset(c))
        solid.BooleanSubtract(holes)
        total.BooleanAdd(solid)
    for cx, cy, r in dots:
        total.BooleanAdd(_polyset([(cx + r * math.cos(a * math.pi / 64), cy + r * math.sin(a * math.pi / 64)) for a in range(128)]))
    return total


def path_data(ps):
    def ring(chain):
        return "M" + "L".join(f"{chain.CPoint(i).x / SC:.2f} {chain.CPoint(i).y / SC:.2f}" for i in range(chain.PointCount())) + "Z"
    return "".join(ring(ps.Outline(i)) + "".join(ring(ps.Hole(i, j)) for j in range(ps.HoleCount(i)))
                   for i in range(ps.OutlineCount()))


class Art:
    """One logo layout: merged outline, dot(s), bounding box, and a one-piece polygon set for fabrication."""

    def __init__(self, pieces, dots, box):
        self.d = path_data(merge(pieces))
        self.dots, self.box = dots, box
        self.solid = merge(pieces, dots)
        self.w, self.h = box[2] - box[0], box[3] - box[1]

    def body(self, colour, dot):
        circles = "".join(f'<circle fill="{dot}" cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}"/>' for x, y, r in self.dots)
        return f'<path fill="{colour}" fill-rule="evenodd" d="{self.d}"/>{circles}'

    def svg(self, variant="navy", pad=6, size=None, cls=None):
        x0, y0 = self.box[0] - pad, self.box[1] - pad
        w, h = self.w + 2 * pad, self.h + 2 * pad
        dim = f' width="{size[0]}" height="{size[1]}"' if size else ""
        extra = f' class="{cls}"' if cls else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}"{dim}{extra} '
                f'role="img" aria-label="Sixteen Amps">{self.body(*VARIANTS[variant])}</svg>')

    def place(self, x, y, width, variant="navy"):
        """A group `width` units wide with its top-left corner at (x, y)."""
        s = width / self.w
        return f'<g transform="translate({x - self.box[0] * s:.3f} {y - self.box[1] * s:.3f}) scale({s:.5f})">{self.body(*VARIANTS[variant])}</g>'

    def height_for(self, width):
        return width * self.h / self.w


ARTS = {name: Art(*layout) for name, layout in _layouts().items()}
STEM_RATIO = STEM / ARTS["logo"].w      # letter stem width as a share of the logo width


def variants_for(name):
    return [v for v in VARIANTS if not (name == "symbol" and v == "on-navy")]


def _linear(h):
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))]


def contrast(a, b):
    la, lb = (sum(w * c for w, c in zip((0.2126, 0.7152, 0.0722), _linear(h))) for h in (a, b))
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def cmyk(h):
    r, g, b = (v / 255 for v in rgb(h))
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    return tuple(round(v * 100) for v in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k))
