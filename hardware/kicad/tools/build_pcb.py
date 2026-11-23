"""Builds powerlenz.kicad_pcb from the schematic netlist: footprints placed on a board outline, pads assigned to nets.
No copper tracks are routed (placement only). Run from hardware/kicad:  python3 tools/build_pcb.py
"""
import math
import os
import subprocess
import sys
import tempfile
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexp import parse, dump, find, first, Str

ROOT = os.path.join(HERE, "..")
SYS_FP = "/usr/share/kicad/footprints"
OUT = os.path.join(ROOT, "powerlenz.kicad_pcb")
VERSION = "20260206"

BOARD_W, BOARD_H = 162.0, 104.0
BARRIER_X = 66.0

# ref -> (x, y, rotation). Rough placement for a 3D picture; not a routed design.
PLACE = {
    # --- mains side ---
    "J1": (10, 20, 90), "F1": (30, 12, 0), "RV1": (60, 14, 0),
    "R1": (22, 34, 0), "R2": (22, 42, 0), "R3": (22, 50, 0), "C1": (50, 42, 0),
    "T1": (66, 62, 180), "PS1": (36, 84, 0), "C2": (80, 96, 0),
    # --- analog front end (low voltage) ---
    "J2": (150, 22, 90), "R4": (132, 18, 0), "R5": (132, 25, 0),
    "R6": (84, 56, 0), "R7": (84, 68, 0),
    "R8": (84, 24, 0), "D1": (96, 24, 0), "D2": (104, 24, 0), "R9": (116, 24, 0),
    "R10": (84, 32, 0), "D3": (96, 32, 0), "D4": (104, 32, 0), "R11": (116, 32, 0),
    "R12": (84, 40, 0), "D5": (96, 40, 0), "D6": (104, 40, 0), "R13": (116, 40, 0),
    "R14": (84, 48, 0), "D7": (96, 48, 0), "D8": (104, 48, 0), "R15": (116, 48, 0),
    "C3": (126, 28, 90), "C4": (126, 44, 90),
    # --- ADC, supply and header ---
    "U2": (140, 66, 0), "U1": (98, 80, 0),
    "C5": (88, 80, 90), "C6": (108, 80, 90), "C7": (128, 56, 90), "C8": (150, 56, 90), "C9": (152, 76, 90),
    "J3": (156, 36, 0),
}

# schematic pin -> footprint pad, where they differ (assumed mappings are flagged in the part notes)
PADMAP = {
    "ZMPT107-1": {"1": "2", "2": "1", "3": "3", "4": "4"},  # windings A = pads 2,1; B = pads 3,4
    "BAT54": {"1": "1", "2": "3"},                          # K = pad 1, A = pad 3 (ASSUMED)
}


def uid():
    return str(uuid.uuid4())


def num(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def netlist():
    with tempfile.TemporaryDirectory() as d:
        net = os.path.join(d, "n.net")
        subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net,
                        os.path.join(ROOT, "powerlenz.kicad_sch")], check=True, capture_output=True)
        t = parse(open(net, encoding="utf-8").read())
    comps = {}
    for c in find(first(t, "components"), "comp"):
        ref = str(first(c, "ref")[1])
        fp = first(c, "footprint")
        comps[ref] = {"value": str(first(c, "value")[1]), "fp": str(fp[1]) if fp else ""}
    pin_net = {}
    for n in find(first(t, "nets"), "net"):
        name = str(first(n, "name")[1]).lstrip("/")
        for nd in find(n, "node"):
            pin_net[(str(first(nd, "ref")[1]), str(first(nd, "pin")[1]))] = name
    return comps, pin_net


def load_footprint(libid):
    lib, name = libid.split(":")
    if lib == "powerlenz":
        path = os.path.join(ROOT, "footprints", "powerlenz.pretty", name + ".kicad_mod")
    else:
        path = os.path.join(SYS_FP, lib + ".pretty", name + ".kicad_mod")
    return parse(open(path, encoding="utf-8").read())


def walk_add_uuid(node):
    """Give every graphic or pad item a uuid, as board files expect."""
    out = []
    for c in node:
        out.append(c)
    return out


def place_fp(ref, comp, x, y, rot, netid, pin_net):
    libid = comp["fp"]
    fp = load_footprint(libid)
    name = libid.split(":")[1]
    padmap = PADMAP.get(comp["value"], {})
    inv = {v: k for k, v in padmap.items()}  # pad -> schematic pin
    items = ["footprint", Str(libid)]
    items.append(["layer", Str("F.Cu")])
    items.append(["uuid", Str(uid())])
    items.append(["at", num(x), num(y)] + ([num(rot)] if rot else []))
    for c in fp[2:]:
        if not isinstance(c, list) or not c:
            continue
        tag = c[0]
        if tag in ("version", "generator", "generator_version", "layer"):
            continue
        if tag == "property":
            c = list(c)
            if c[1] == "Reference":
                c[2] = Str(ref)
            elif c[1] == "Value":
                c[2] = Str(comp["value"])
            if first(c, "uuid") is None:
                c.append(["uuid", Str(uid())])
            items.append(c)
            continue
        c = list(c)
        if tag == "pad":
            pad = str(c[1])
            pin = inv.get(pad, pad)
            net = pin_net.get((ref, pin))
            if net is not None:
                c.append(["net", str(netid.setdefault(net, len(netid) + 1)), Str(net)])
            if first(c, "uuid") is None:
                c.append(["uuid", Str(uid())])
        elif tag.startswith("fp_") and first(c, "uuid") is None:
            c.append(["uuid", Str(uid())])
        items.append(c)
    return items


def gr_line(x1, y1, x2, y2, layer, width=0.15, dashed=False):
    return ("\t(gr_line\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width %s)\n\t\t\t(type %s)\n\t\t)\n\t\t(layer \"%s\")\n\t\t(uuid \"%s\")\n\t)"
            % (num(x1), num(y1), num(x2), num(y2), num(width), "dash" if dashed else "solid", layer, uid()))


def gr_text(s, x, y, layer, size=1.2, bold=False):
    return ("\t(gr_text \"%s\"\n\t\t(at %s %s 0)\n\t\t(layer \"%s\")\n\t\t(uuid \"%s\")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n\t\t\t\t(thickness %s)\n\t\t\t)\n\t\t\t(justify left)\n\t\t)\n\t)"
            % (s, num(x), num(y), layer, uid(), num(size), num(size), num(size / 6 if not bold else size / 4)))


def main():
    comps, pin_net = netlist()
    netid = {}
    # pre-assign net numbers in a stable order
    for (ref, pin), net in sorted(pin_net.items(), key=lambda kv: kv[1]):
        netid.setdefault(net, len(netid) + 1)
    fps = []
    missing = [r for r in comps if r not in PLACE]
    if missing:
        raise SystemExit("no placement for: %s" % missing)
    for ref in sorted(comps, key=lambda r: (r.rstrip("0123456789"), int("".join(ch for ch in r if ch.isdigit())))):
        x, y, rot = PLACE[ref]
        fps.append(dump(place_fp(ref, comps[ref], x, y, rot, netid, pin_net), 1))
    # mounting holes
    for mi, (hx, hy) in enumerate([(4, 4), (BOARD_W - 4, 4), (4, BOARD_H - 4), (BOARD_W - 4, BOARD_H - 4)], 1):
        mh = load_footprint("MountingHole:MountingHole_3.2mm_M3")
        items = ["footprint", Str("MountingHole:MountingHole_3.2mm_M3"), ["layer", Str("F.Cu")], ["uuid", Str(uid())], ["at", num(hx), num(hy)]]
        for c in mh[2:]:
            if isinstance(c, list) and c and c[0] not in ("version", "generator", "generator_version", "layer"):
                c = list(c)
                if c[0] == "property":
                    if c[1] == "Reference":
                        c[2] = Str("MH%d" % mi)
                    if first(c, "uuid") is None:
                        c.append(["uuid", Str(uid())])
                elif (c[0] == "pad" or c[0].startswith("fp_")) and first(c, "uuid") is None:
                    c.append(["uuid", Str(uid())])
                items.append(c)
        fps.append(dump(items, 1))
    graphics = [
        gr_line(0, 0, BOARD_W, 0, "Edge.Cuts", 0.1), gr_line(BOARD_W, 0, BOARD_W, BOARD_H, "Edge.Cuts", 0.1),
        gr_line(BOARD_W, BOARD_H, 0, BOARD_H, "Edge.Cuts", 0.1), gr_line(0, BOARD_H, 0, 0, "Edge.Cuts", 0.1),
        gr_line(BARRIER_X, 2, BARRIER_X, BOARD_H - 2, "F.SilkS", 0.25, dashed=True),
        gr_text("MAINS SIDE 230 V", 8, 6, "F.SilkS", 1.5, True),
        gr_text("LOW VOLTAGE", 80, 6, "F.SilkS", 1.5, True),
        gr_text("ISOLATION BARRIER", BARRIER_X + 2, 11, "F.SilkS", 1.0),
        gr_text("PowerLenz v0.1  placement only, not routed", 80, BOARD_H - 3, "F.SilkS", 1.0),
    ]
    nets = ['\t(net 0 "")'] + ['\t(net %d "%s")' % (i, n) for n, i in sorted(netid.items(), key=lambda kv: kv[1])]
    layers = open(os.path.join(HERE, "pcb_layers.txt"), encoding="utf-8").read().rstrip("\n")
    text = ('(kicad_pcb\n\t(version %s)\n\t(generator "pcbnew")\n\t(generator_version "10.0")\n\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n'
            '\t(paper "A3")\n%s\n\t(setup\n\t\t(pad_to_mask_clearance 0)\n\t\t(allow_soldermask_bridges_in_footprints no)\n\t\t(tenting front back)\n\t)\n%s\n%s\n%s\n\t(embedded_fonts no)\n)\n'
            % (VERSION, layers, "\n".join(nets), "\n".join(fps), "\n".join(graphics)))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("wrote", os.path.abspath(OUT), "-", len(comps), "parts,", len(netid), "nets")


if __name__ == "__main__":
    main()
