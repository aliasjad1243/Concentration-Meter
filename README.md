# Liquid Concentration Meter

My contributions to the **[Open Colorimeter](https://github.com/iorodeo/open_colorimeter)** by
IO Rodeo, an open-source handheld colorimeter. It shines an LED of one color through a liquid
sample and measures how much light gets through with a TSL2591 light sensor. The darker the
dye, the less light reaches the sensor, so the reading can be turned into a concentration.

I built the device as a proof of concept from IO Rodeo's LED board and firmware, then changed
the firmware so every reading is streamed to a laptop, and wrote the scripts to build
calibration curves, check repeatability and compare tube-holder designs.
**This repo only holds the files I wrote or changed.** The boards, enclosure and stock firmware
are in IO Rodeo's repos.

## The original project

| Part | Repo |
|---|---|
| Main project | [iorodeo/open_colorimeter](https://github.com/iorodeo/open_colorimeter) |
| LED board (KiCad, incl. 630 nm version) | [iorodeo/basic_led](https://github.com/iorodeo/basic_led) |
| Cuvette holder | [iorodeo/cuvette_holder](https://github.com/iorodeo/cuvette_holder) |
| CircuitPython firmware | [iorodeo/open_colorimeter_firmware](https://github.com/iorodeo/open_colorimeter_firmware) |

Software is MIT; hardware and docs are CC-BY-4.0.

## What I did

- **Assembly:** hand-soldered the KiCad LED board and wired the TSL2591 sensor on the I²C bus
  → [`docs/build-and-test.md`](docs/build-and-test.md)
- **LED choice and resistor:** matched a 630 nm LED to FD&C Blue 1's absorption peak and sized
  the current-limiting resistor for the 3.3 V supply (82 Ω, ~16 mA)
- **Firmware logging:** added `serial_logger.py` and hooked it into the main loop so each reading
  streams over USB serial, and fixed two small bugs in the stock config/calibration error handling
  → [`firmware/`](firmware/)
- **Calibration:** 6 dye standards, 10 repeats each, linear fit, LOD/LOQ, CV per standard, and
  export straight into the meter's `calibrations.json` → [`analysis/calibrate.py`](analysis/calibrate.py)
- **Holder DOE:** one-factor comparison of 3 tube-holder designs modeled in Creo, on seating
  consistency and stray light → [`analysis/doe.py`](analysis/doe.py)

## Files

```
firmware/
  serial_logger.py              new module: one CSV line per reading over USB
  colorimeter-logging.patch     changes to colorimeter.py and configuration.py
  configuration.json            example config with logging turned on
tools/log_serial.py             saves the serial stream to a CSV on the laptop
analysis/calibrate.py           calibration curve, LOD/LOQ, repeatability, JSON export
analysis/doe.py                 one-way ANOVA across holder designs
docs/build-and-test.md          wiring, LED resistor math, standards, test procedure
data/standards.csv              standard concentrations (S0–S5)
```

## Using it with the stock firmware

```bash
git clone https://github.com/iorodeo/open_colorimeter_firmware
cd open_colorimeter_firmware
git apply /path/to/firmware/colorimeter-logging.patch
cp /path/to/firmware/serial_logger.py src/
```

Copy `src/`, `code.py` and `assets/` to the CIRCUITPY drive as in IO Rodeo's instructions, and
use `firmware/configuration.json` as the meter's `configuration.json`. Then:

```bash
python tools/log_serial.py COM7 data/readings.csv
python analysis/calibrate.py data/readings.csv data/standards.csv --json calibrations.json
python analysis/doe.py data/doe_holders.csv
```

`tools/log_serial.py` needs `pyserial`; `doe.py` uses `scipy` for p-values if it's installed.

## License

My code is MIT, matching the Open Colorimeter software ([`LICENSE`](LICENSE)). The hardware
I built from is IO Rodeo's, under CC-BY-4.0.
