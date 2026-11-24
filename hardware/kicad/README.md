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

## PCB and 3D model

`tools/build_pcb.py` builds `powerlenz.kicad_pcb` from the schematic netlist: all parts are placed on a compact 154 x 86 mm board (with the ESP32-S3 DevKitC plugged into two 1x22 sockets; its outline and 22.86 mm row spacing are assumed) with a mains zone and a low-voltage zone, and every pad is assigned its net. `tools/route.py` then routes it with Freerouting in two separate runs (needs Java and the Freerouting jar in `~/tools`, not stored in the repo): the low-voltage side (0.25 mm signals, 0.5 mm power, 0.2 mm clearance, GND pour on the back copper) and the mains nets `L_IN`, `L_FUSED`, `N`, `ZA_P`, `ZP1`, `ZP2` (0.8 mm tracks, 3 mm clearance, the `Mains` net class in `powerlenz.kicad_pro`). Two 1 mm slots are milled along the isolation line at x = 56 mm (Edge.Cuts); `powerlenz.kicad_dru` relaxes the rule only for the terminal block J1, whose own pad gap is 2.48 mm.

**DRAFT: the mains clearance, the slot and the isolation spacing are my starting values (roughly IEC 60664-1 basic creepage for 250 V, pollution degree 2, plus margin) and have not been reviewed by anyone with mains-design experience.** Do not build this board. DRC reports no clearance, short or unconnected errors, only silkscreen and library-copy warnings.

```
python3 tools/build_pcb.py        # after the schematic is built
python3 tools/route.py            # needs ~/tools/freerouting*.jar; removes old tracks, then routes
kicad-cli pcb render --side top --width 2400 --height 1500 --quality high --rotate '-50,0,-25' --perspective --zoom 0.9 -o exports/3d/powerlenz-pcb-3d.png powerlenz.kicad_pcb
kicad-cli pcb export glb --subst-models -o exports/3d/powerlenz-pcb.glb powerlenz.kicad_pcb
python3 tools/make_step_models.py   # STEP stand-ins for the ZMPT107-1, DevKitC and fuse clip
kicad-cli pcb export step --subst-models --include-tracks --include-pads --include-zones --include-silkscreen --include-soldermask -o exports/3d/powerlenz-pcb.step powerlenz.kicad_pcb
```

| File | What it is |
|---|---|
| `exports/3d/powerlenz-pcb-3d.png`, `powerlenz-pcb-top.png` | Rendered pictures of the board |
| `exports/3d/powerlenz-pcb.glb` | The full 3D model (open in Blender, or any glTF viewer) |
| `exports/3d/powerlenz-pcb.step` | STEP for SolidWorks and other mechanical CAD, with copper, pads, silkscreen, solder mask and every part. The ZMPT107-1, the DevKitC and the fuse clip are simple coloured boxes from `tools/make_step_models.py` (assumed sizes, not manufacturer geometry); the other parts are KiCad library models. In SolidWorks use Open, Options, Import as assembly. |

Things to know about the 3D model:
- The ZMPT107-1 is a simple box (19 x 10 x 18.2 mm) with four pins, from the manufacturer's drawing, with its footprint taken from the same drawing and not yet checked against a real part.
- The varistor uses a 12 mm disc footprint as the nearest match for the 10 mm 10D561K.
- The BAT54 and BAV199 SOT-23 pad mappings are assumed (see the part notes).
- The mains and low-voltage zones are marked on the board. A real board also needs an isolation slot and proper creepage and clearance, reviewed by someone with mains-design experience.

## ERC notes

- `same_local_global_label` is set to ignore in `powerlenz.kicad_pro`. A few pins use a plain net label with the same name as a power net (for example +3V3A or GND) to keep stacked power symbols from overlapping. The nets are the same either way, and the exported netlist was compared before and after to confirm that.
- Footprints are not assigned yet, so the board stage is still ahead.

## Exports

`exports/powerlenz-schematic.pdf` and `exports/powerlenz-bom.csv` are generated with `kicad-cli` (see above). Re-export after any change.

## Status

The schematic is built block by block. Each block is committed once its ERC is clean. Footprints are not assigned yet. Nothing here has been built or tested; the open items in `documentation/README.md` still apply, and the mains side needs a design review before it is ever powered.
