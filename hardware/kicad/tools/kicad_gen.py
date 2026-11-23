"""Tiny KiCad 10 schematic generator.

Parts come from KiCad's installed symbol libraries. Connections are made with net labels
(and power symbols for power nets), so every pin on the same net name is connected.
"""
import math
import uuid
from sexp import dump, find, first, Str
from libinfo import get_symbol, pins

VERSION = "20260306"
POWER_SYMS = {  # net name -> (library symbol, orientation of stub)
    "GND": "GND",
    "+5V": "+5V",
    "+3V3A": "+3V3",
}


def uid():
    return str(uuid.uuid4())


def num(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Schematic:
    def __init__(self, title, paper="A3", rev="0.1", project="powerlenz"):
        self.title, self.paper, self.rev, self.project = title, paper, rev, project
        self.root_uuid = uid()
        self.libsyms = {}
        self.body = []
        self.counters = {}
        self.pwr_count = 0
        self.refs = {}
        self.foot = {}  # value -> footprint

    # ---------- library handling ----------
    def _embed(self, lib, sym):
        key = "%s:%s" % (lib, sym)
        if key not in self.libsyms:
            s = list(get_symbol(lib, sym))
            s[1] = Str(key)
            self.libsyms[key] = s
        return key

    # ---------- primitives ----------
    def wire(self, x1, y1, x2, y2):
        self.body.append(
            '\t(wire\n\t\t(pts\n\t\t\t(xy %s %s)\n\t\t\t(xy %s %s)\n\t\t)\n'
            '\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "%s")\n\t)'
            % (num(x1), num(y1), num(x2), num(y2), uid()))

    def label(self, name, x, y, angle):
        just = "left bottom" if angle in (0, 90) else "right bottom"
        self.body.append(
            '\t(label "%s"\n\t\t(at %s %s %d)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
            '\t\t\t(justify %s)\n\t\t)\n\t\t(uuid "%s")\n\t)' % (name, num(x), num(y), angle, just, uid()))

    def no_connect(self, x, y):
        self.body.append('\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)' % (num(x), num(y), uid()))

    def text(self, s, x, y, size=1.27, bold=False):
        b = "\t\t\t\t(bold yes)\n" if bold else ""
        self.body.append(
            '\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n%s\t\t\t)\n'
            '\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "%s")\n\t)' % (s.replace('"', "'"), num(x), num(y), num(size), num(size), b, uid()))

    def box(self, x1, y1, x2, y2):
        self.body.append(
            '\t(rectangle\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.2)\n\t\t\t(type dash)\n\t\t)\n'
            '\t\t(fill\n\t\t\t(type none)\n\t\t)\n\t\t(uuid "%s")\n\t)' % (num(x1), num(y1), num(x2), num(y2), uid()))

    # ---------- symbol instances ----------
    def _instance(self, lib, sym, ref, value, x, y, rot, footprint, extra, dnp, hide_props=False, pin_numbers=()):
        key = self._embed(lib, sym)
        libsym = self.libsyms[key]
        props = []
        for p in find(libsym, "property"):
            name = str(p[1])
            node = [c for c in p]
            at = first(node, "at")
            nx, ny = float(at[1]), float(at[2])
            rx, ry = self._rot(nx, ny, rot)
            newat = ["at", num(x + rx), num(y - ry), str((360 - rot) % 360 if rot else 0)]
            if rot in (90, 270) and name in ("Reference", "Value"):
                # horizontal two-pin part: keep the texts clear of the body
                newat = ["at", num(x), num(y - 3.2 if name == "Reference" else y + 3.6), str((360 - rot) % 360)]
            node = [newat if (isinstance(c, list) and c and c[0] == "at") else c for c in node]
            if name == "Reference":
                node[2] = Str(ref)
            elif name == "Value":
                node[2] = Str(value)
            elif name == "Footprint" and footprint:
                node[2] = Str(footprint)
            props.append(node)
        for k, v in (extra or {}).items():
            props.append(["property", Str(k), Str(v), ["at", num(x), num(y), "0"],
                          ["hide", "yes"], ["show_name", "no"], ["do_not_autoplace", "no"],
                          ["effects", ["font", ["size", "1.27", "1.27"]]]])
        out = ['\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %s %s %d)\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom %s)\n'
               '\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp %s)\n\t\t(uuid "%s")'
               % (key, num(x), num(y), rot, "yes" if not ref.startswith("#") else "no", "yes" if dnp else "no", uid())]
        for p in props:
            out.append("\t\t" + dump(p, 2))
        for n in pin_numbers:
            out.append('\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)' % (n, uid()))
        out.append('\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'
                   % (self.project, self.root_uuid, ref))
        self.body.append("\n".join(out))

    @staticmethod
    def _rot(px, py, rot):
        a = math.radians(rot)
        return (px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a))

    def pin_points(self, lib, sym, x, y, rot=0):
        """{pin number: (sch x, sch y, outward angle)}"""
        s = get_symbol(lib, sym)
        out = {}
        for num_, name, px, py, ang, etype, sub in pins(s):
            rx, ry = self._rot(px, py, rot)
            out[num_] = (round(x + rx, 4), round(y - ry, 4), (int(ang) + rot + 180) % 360, name)
        return out

    def part(self, lib, sym, value, at, nets=None, prefix="U", ref=None, footprint="", extra=None, dnp=False,
             rot=0, nc=(), flags=()):
        x, y = [round(v / 2.54) * 2.54 for v in at]
        if ref is None:
            self.counters[prefix] = self.counters.get(prefix, 0) + 1
            ref = "%s%d" % (prefix, self.counters[prefix])
        footprint = footprint or self.foot.get(value, "")
        pts = self.pin_points(lib, sym, x, y, rot)
        numbers = sorted(pts, key=lambda s: (len(s), s))
        self._instance(lib, sym, ref, value, x, y, rot, footprint, extra, dnp, pin_numbers=numbers)
        for pn, net in (nets or {}).items():
            px, py, out_ang, _ = pts[str(pn)]
            self._connect(net, px, py, out_ang, flag=(str(pn) in [str(f) for f in flags]))
        for pn in nc:
            px, py, _, _ = pts[str(pn)]
            self.no_connect(px, py)
        self.refs[ref] = (lib, sym, value)
        return ref

    def _connect(self, net, px, py, out_ang, flag=False):
        if net.startswith("~"):  # label only, no power symbol
            self.label(net[1:], px, py, out_ang)
            return
        dx = math.cos(math.radians(out_ang))
        dy = -math.sin(math.radians(out_ang))
        if net in POWER_SYMS or flag:
            ex, ey = px + 2.54 * round(dx), py + 2.54 * round(dy)
            self.wire(px, py, ex, ey)
            if flag:
                fx, fy = ex + 2.54 * round(dx), ey + 2.54 * round(dy)
                self.wire(ex, ey, fx, fy)
                self._power_symbol("power", "PWR_FLAG", "PWR_FLAG", fx, fy)
            if net in POWER_SYMS:
                self._power_symbol("power", POWER_SYMS[net], net, ex, ey)
            else:
                self.label(net, ex, ey, out_ang)
        else:
            self.label(net, px, py, out_ang)

    def _power_symbol(self, lib, sym, value, x, y):
        self.pwr_count += 1
        self._instance(lib, sym, "#PWR%02d" % self.pwr_count if sym != "PWR_FLAG" else "#FLG%02d" % self.pwr_count,
                       value, x, y, 0, "", None, False, pin_numbers=["1"])

    # ---------- output ----------
    def render(self):
        libs = "\n".join("\t\t" + dump(s, 2) for s in self.libsyms.values())
        head = ('(kicad_sch\n\t(version %s)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n\t(uuid "%s")\n\t(paper "%s")\n'
                '\t(title_block\n\t\t(title "%s")\n\t\t(rev "%s")\n\t\t(company "PowerLenz")\n\t)\n\t(lib_symbols\n%s\n\t)\n'
                % (VERSION, self.root_uuid, self.paper, self.title, self.rev, libs))
        tail = '\n\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n'
        return head + "\n".join(self.body) + tail

    def save(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.render())
