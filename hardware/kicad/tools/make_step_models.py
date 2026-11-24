"""Writes the simple STEP stand-in models used by the board (box solids with colours, units mm, y up as KiCad expects).

KiCad cannot put VRML models into a STEP export, so the parts that have no library STEP model get one from here:
  ZMPT107-1, ESP32-S3-DevKitC-1 (mechanical stand-in) and the 5x20 mm fuse clip with a fuse.
Sizes are the same ASSUMED ones as in the footprints; they are stand-ins, not manufacturer geometry.
Run from hardware/kicad:  python3 tools/make_step_models.py
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "footprints", "powerlenz.3dshapes")


class Step:
    def __init__(self):
        self.n = 0
        self.lines = []

    def e(self, text):
        self.n += 1
        self.lines.append("#%d=%s;" % (self.n, text))
        return "#%d" % self.n

    def pt(self, x, y, z):
        return self.e("CARTESIAN_POINT('',(%.6f,%.6f,%.6f))" % (x, y, z))

    def d(self, x, y, z):
        return self.e("DIRECTION('',(%.1f,%.1f,%.1f))" % (x, y, z))

    def box(self, cx, cy, cz, dx, dy, dz):
        """An axis-aligned box solid, returns the MANIFOLD_SOLID_BREP id."""
        lo = (cx - dx / 2, cy - dy / 2, cz - dz / 2)
        size = (dx, dy, dz)
        vp = {}
        for i in range(8):
            b = ((i >> 0) & 1, (i >> 1) & 1, (i >> 2) & 1)
            p = self.pt(*[lo[k] + b[k] * size[k] for k in range(3)])
            vp[b] = self.e("VERTEX_POINT('',%s)" % p)
        edges = {}  # (a, b) with a < b along one axis -> (edge_curve id)
        for ax in range(3):
            for i in range(8):
                b0 = ((i >> 0) & 1, (i >> 1) & 1, (i >> 2) & 1)
                if b0[ax] == 1:
                    continue
                b1 = tuple(1 if k == ax else b0[k] for k in range(3))
                dirv = [0.0, 0.0, 0.0]
                dirv[ax] = 1.0
                start = self.pt(*[lo[k] + b0[k] * size[k] for k in range(3)])
                vec = self.e("VECTOR('',%s,%.6f)" % (self.d(*dirv), size[ax]))
                line = self.e("LINE('',%s,%s)" % (start, vec))
                edges[(b0, b1)] = self.e("EDGE_CURVE('',%s,%s,%s,.T.)" % (vp[b0], vp[b1], line))
        faces = []
        for ax in range(3):
            u, v = (ax + 1) % 3, (ax + 2) % 3
            for side in (0, 1):
                ring = []
                for (a, b) in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                    p = [0, 0, 0]
                    p[ax], p[u], p[v] = side, a, b
                    ring.append(tuple(p))
                if side == 0:
                    ring = ring[::-1]
                oriented = []
                for i in range(4):
                    p, q = ring[i], ring[(i + 1) % 4]
                    if (p, q) in edges:
                        oriented.append(self.e("ORIENTED_EDGE('',*,*,%s,.T.)" % edges[(p, q)]))
                    else:
                        oriented.append(self.e("ORIENTED_EDGE('',*,*,%s,.F.)" % edges[(q, p)]))
                loop = self.e("EDGE_LOOP('',(%s))" % ",".join(oriented))
                bound = self.e("FACE_OUTER_BOUND('',%s,.T.)" % loop)
                n = [0.0, 0.0, 0.0]
                n[ax] = 1.0 if side else -1.0
                r = [0.0, 0.0, 0.0]
                r[u] = 1.0
                org = self.pt(*[lo[k] + (side if k == ax else 0) * size[k] for k in range(3)])
                plane = self.e("PLANE('',%s)" % self.e("AXIS2_PLACEMENT_3D('',%s,%s,%s)" % (org, self.d(*n), self.d(*r))))
                faces.append(self.e("ADVANCED_FACE('',(%s),%s,.T.)" % (bound, plane)))
        shell = self.e("CLOSED_SHELL('',(%s))" % ",".join(faces))
        return self.e("MANIFOLD_SOLID_BREP('',%s)" % shell)


def write(name, boxes):
    s = Step()
    app = s.e("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
    s.e("APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,%s)" % app)
    pdc = s.e("PRODUCT_DEFINITION_CONTEXT('part definition',%s,'design')" % app)
    prc = s.e("PRODUCT_CONTEXT('',%s,'mechanical')" % app)
    prod = s.e("PRODUCT('%s','%s','',(%s))" % (name, name, prc))
    s.e("PRODUCT_RELATED_PRODUCT_CATEGORY('part','',(%s))" % prod)
    pdf = s.e("PRODUCT_DEFINITION_FORMATION('','',%s)" % prod)
    pd = s.e("PRODUCT_DEFINITION('design','',%s,%s)" % (pdf, pdc))
    pds = s.e("PRODUCT_DEFINITION_SHAPE('','',%s)" % pd)
    lu = s.e("(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))")
    au = s.e("(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.))")
    su = s.e("(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT())")
    unc = s.e("UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-05),%s,'distance_accuracy_value','')" % lu)
    ctx = s.e("(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((%s)) GLOBAL_UNIT_ASSIGNED_CONTEXT((%s,%s,%s)) REPRESENTATION_CONTEXT('ID1','3D'))" % (unc, lu, au, su))
    solids, styled = [], []
    for (cx, cy, cz, dx, dy, dz, rgb) in boxes:
        sol = s.box(cx, cy, cz, dx, dy, dz)
        solids.append(sol)
        col = s.e("COLOUR_RGB('',%.3f,%.3f,%.3f)" % rgb)
        fill = s.e("FILL_AREA_STYLE('',(%s))" % s.e("FILL_AREA_STYLE_COLOUR('',%s)" % col))
        ssfa = s.e("SURFACE_STYLE_FILL_AREA(%s)" % fill)
        side = s.e("SURFACE_SIDE_STYLE('',(%s))" % ssfa)
        usage = s.e("SURFACE_STYLE_USAGE(.BOTH.,%s)" % side)
        psa = s.e("PRESENTATION_STYLE_ASSIGNMENT((%s))" % usage)
        styled.append(s.e("STYLED_ITEM('',(%s),%s)" % (psa, sol)))
    origin = s.e("AXIS2_PLACEMENT_3D('',%s,%s,%s)" % (s.pt(0, 0, 0), s.d(0, 0, 1), s.d(1, 0, 0)))
    rep = s.e("ADVANCED_BREP_SHAPE_REPRESENTATION('',(%s,%s),%s)" % (origin, ",".join(solids), ctx))
    s.e("SHAPE_DEFINITION_REPRESENTATION(%s,%s)" % (pds, rep))
    s.e("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(%s),%s)" % (",".join(styled), ctx))
    text = ("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('PowerLenz stand-in model'),'2;1');\n"
            "FILE_NAME('%s.step','2026-11-24T00:00:00',('PowerLenz'),(''),'powerlenz-gen','','');\n"
            "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n%s\nENDSEC;\nEND-ISO-10303-21;\n"
            % (name, "\n".join(s.lines)))
    with open(os.path.join(OUT, name + ".step"), "w") as fh:
        fh.write(text)
    print("wrote", name + ".step", len(boxes), "solids")


NAVY, SILVER = (0.10, 0.18, 0.32), (0.85, 0.85, 0.85)
# model coordinates: x right, y UP (= minus the PCB y), z up from the board; footprint origin = (0, 0)
write("ZMPT107-1", [(0, 0, 9.1, 19, 10, 18.2, NAVY)] +
      [(sx * 8.15, sy * 3.6, -2.0, 0.8, 0.8, 4.0, SILVER) for sx in (-1, 1) for sy in (-1, 1)])

# DevKitC: origin = pin 1 of the left socket row; board 25.4 x 69.4 mm, sits on 8.5 mm sockets
cx, y0, L, z0 = 11.43, -4.0, 69.4, 8.5
write("ESP32-S3-DevKitC-1", [
    (cx, -(y0 + L / 2), z0 + 0.8, 25.4, L, 1.6, (0.05, 0.30, 0.20)),
    (cx, -(y0 + 9), z0 + 3.2, 18.0, 25.5, 3.2, (0.15, 0.15, 0.15)),
    (cx - 6, -(y0 + L - 3), z0 + 3.2, 8.0, 9.0, 3.2, (0.75, 0.75, 0.78)),
    (cx + 6, -(y0 + L - 3), z0 + 3.2, 8.0, 9.0, 3.2, (0.75, 0.75, 0.78)),
])

# 5x20 mm fuse clip (Bel FC-203-22 footprint, pads at x = 0 and 17.8, y = 0 and 5) with a 1 A fuse in it
write("FuseClip-5x20", [
    (0.0, -2.5, 4.0, 4.0, 6.0, 8.0, (0.75, 0.55, 0.20)),
    (17.8, -2.5, 4.0, 4.0, 6.0, 8.0, (0.75, 0.55, 0.20)),
    (8.9, -2.5, 4.5, 20.0, 5.0, 5.0, (0.85, 0.85, 0.70)),
])
