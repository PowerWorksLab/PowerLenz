# PowerLenz

PowerLenz - Power monitoring, management and analytics platform.

PowerLenz is a Sense-style energy monitor for Indian single-phase homes (230 V, 50 Hz). A clamp-on current sensor and a voltage sensor feed a 24-bit simultaneous-sampling ADC and an ESP32-S3, which finds appliance switching events and sends them to the cloud for classification. The hardware design is at paper stage: it is datasheet-checked, but nothing has been built or bench-tested yet.

## Documentation

Start with **[documentation/README.md](documentation/README.md)**. It gives the reading order, the design and its decisions, the bill of materials summary, safety notes and what is still open.

| Where | What it holds |
|---|---|
| [documentation/README.md](documentation/README.md) | The whole design in one page, with the reading order |
| [documentation/findings/](documentation/findings/) | Design reasoning, the datasheet verification checklist, datasheet links and the [bill of materials](documentation/findings/bill-of-materials.md) |
| [documentation/datasheets/](documentation/datasheets/README.md) | Local copies of the manufacturer datasheets, organised by function |
| [documentation/diagrams/](documentation/diagrams/) | Circuit diagrams and the calculation page |
| [documentation/presentations/](documentation/presentations/) | The slide deck and the scripts that build it |

## Safety

The mains side of the design is live 230 V. Nothing here is ready to be powered from the mains. Use an enclosure, correct clearance and creepage, and have the board reviewed by someone with mains-design experience first.
