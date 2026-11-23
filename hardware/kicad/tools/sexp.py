"""Minimal S-expression reader and writer for KiCad files (no third-party packages)."""


def parse(text):
    """Parse KiCad S-expression text into nested lists. Strings keep a Str wrapper so quotes can be restored."""
    pos = 0
    n = len(text)

    def skip():
        nonlocal pos
        while pos < n and text[pos] in " \t\r\n":
            pos += 1

    def read():
        nonlocal pos
        skip()
        c = text[pos]
        if c == "(":
            pos += 1
            items = []
            while True:
                skip()
                if text[pos] == ")":
                    pos += 1
                    return items
                items.append(read())
        if c == '"':
            pos += 1
            buf = []
            while text[pos] != '"':
                if text[pos] == "\\":
                    buf.append(text[pos:pos + 2])
                    pos += 2
                else:
                    buf.append(text[pos])
                    pos += 1
            pos += 1
            return Str("".join(buf))
        start = pos
        while pos < n and text[pos] not in " \t\r\n()":
            pos += 1
        return text[start:pos]

    return read()


class Str(str):
    """A quoted string atom."""


def dump(node, indent=0):
    """Write nested lists back as KiCad-style text."""
    pad = "\t" * indent
    if isinstance(node, Str):
        return '"%s"' % node
    if isinstance(node, str):
        return node
    if all(not isinstance(x, list) for x in node):
        return "(" + " ".join(dump(x) for x in node) + ")"
    head = [x for x in node if not isinstance(x, list)]
    rest = [x for x in node if isinstance(x, list)]
    # keep leading atoms on the first line, children on their own lines
    first = []
    for x in node:
        if isinstance(x, list):
            break
        first.append(dump(x))
    out = "(" + " ".join(first)
    for x in node[len(first):]:
        out += "\n" + "\t" * (indent + 1) + dump(x, indent + 1)
    out += "\n" + pad + ")"
    return out


def find(node, name):
    """All direct children lists whose first atom is name."""
    return [c for c in node if isinstance(c, list) and c and c[0] == name]


def first(node, name):
    r = find(node, name)
    return r[0] if r else None
