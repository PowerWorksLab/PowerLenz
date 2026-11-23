# KiCad design

The PowerLenz schematic, written as code and checked with KiCad's own electrical rules check (ERC).

| File | What it is |
|---|---|
| `powerlenz.kicad_pro` | KiCad project |
| `powerlenz.kicad_sch` | The schematic. **Generated**: edit `tools/build_schematic.py`, then re-run it. Hand edits in KiCad are overwritten. |
| `tools/build_schematic.py` | Describes the circuit, one function per block |
| `tools/kicad_gen.py`, `sexp.py`, `libinfo.py` | A small generator that takes symbols from KiCad's installed libraries |
| `sym-lib-table`, `fp-lib-table` | Library paths for the project |

## Rebuild and check

```
cd hardware/kicad
python3 tools/build_schematic.py
kicad-cli sch erc --format json --severity-all -o erc.json powerlenz.kicad_sch
kicad-cli sch export netlist --format kicadsexpr -o powerlenz.net powerlenz.kicad_sch
kicad-cli sch export pdf -o powerlenz.pdf powerlenz.kicad_sch
```

Needs KiCad 10 (`kicad-cli`) and Python 3. Connections are made with net labels and power symbols: every pin carrying the same net name is connected.

## Status

The schematic is built block by block. Each block is committed once its ERC is clean. Footprints are not assigned yet. Nothing here has been built or tested; the open items in `documentation/README.md` still apply, and the mains side needs a design review before it is ever powered.
