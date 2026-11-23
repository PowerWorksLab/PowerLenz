"""Read symbols from KiCad's installed symbol libraries."""
import os
from sexp import parse, find, first, Str

SYMDIR = "/usr/share/kicad/symbols"
_cache = {}


def load_lib(name):
    if name not in _cache:
        path = os.path.join(SYMDIR, name + ".kicad_sym")
        _cache[name] = parse(open(path, encoding="utf-8").read())
    return _cache[name]


def get_symbol(lib, sym):
    """Return a self-contained symbol (extends resolved) as a list, named sym."""
    root = load_lib(lib)
    table = {c[1]: c for c in find(root, "symbol")}
    s = table[sym]
    ext = first(s, "extends")
    if ext:
        base = get_symbol(lib, ext[1])
        # derived symbol: take base graphics/pins, override properties from derived
        merged = [Str(sym) if False else "symbol", Str(sym)]
        derived_props = {p[1]: p for p in find(s, "property")}
        for item in base[2:]:
            if isinstance(item, list) and item[0] == "property" and item[1] in derived_props:
                merged.append(derived_props[item[1]])
            elif isinstance(item, list) and item[0] == "symbol":
                sub = list(item)
                sub[1] = Str(item[1].replace(base[1], sym, 1))
                merged.append(sub)
            else:
                merged.append(item)
        return merged
    return s


def pins(sym):
    """List of (number, name, x, y, angle, etype) for every pin of a symbol (all units, no de-dup)."""
    out = []
    for sub in find(sym, "symbol"):
        for p in find(sub, "pin"):
            at = first(p, "at")
            nm = first(p, "name")
            num = first(p, "number")
            out.append((str(num[1]), str(nm[1]), float(at[1]), float(at[2]), float(at[3]), p[1], sub[1]))
    return out


if __name__ == "__main__":
    import sys
    lib, sy = sys.argv[1], sys.argv[2]
    s = get_symbol(lib, sy)
    for pr in pins(s):
        print(pr)
