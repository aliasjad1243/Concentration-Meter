# Liquid Concentration Meter

My contributions to the **[Open Colorimeter](https://github.com/iorodeo/open_colorimeter)** by
IO Rodeo, an open-source handheld colorimeter. It shines an LED of one color through a liquid
sample and measures how much light gets through with a TSL2591 light sensor. The darker the
dye, the less light reaches the sensor, so the reading can be turned into a concentration.

I built the device as a proof of concept from IO Rodeo's LED board and firmware, changed the
firmware so every reading streams to a laptop, and wrote the script that builds the calibration
curve and checks repeatability.
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

## My contributions (what I did → where to look)

1. **Assembly:** hand-soldered the KiCad LED board and wired the TSL2591 light sensor on the I²C
   bus (630 nm LED for FD&C Blue 1, 82 Ω resistor on 3.3 V) → [`docs/build-and-test.md`](docs/build-and-test.md)
2. **Firmware: readings streamed over USB serial for live logging in Python:** new
   `serial_logger.py` module hooked into the main loop, plus two small fixes to the stock
   config/calibration error handling → [`firmware/`](firmware/); laptop logger
   → [`tools/log_serial.py`](tools/log_serial.py)
3. **Calibration in Python:** 6 dye standards × 10 repeats, linear fit, repeatability (CV) per
   standard (target ≤ 2 %), exported straight into the meter's `calibrations.json`
   → [`analysis/calibrate.py`](analysis/calibrate.py), [`data/standards.csv`](data/standards.csv)

## Files

```
firmware/
  serial_logger.py              new module: one CSV line per reading over USB
  colorimeter-logging.patch     changes to colorimeter.py and configuration.py
  configuration.json            example config with logging turned on
tools/log_serial.py             saves the serial stream to a CSV on the laptop
analysis/calibrate.py           calibration curve, repeatability, JSON export
tests/test_meter.py             pytest tests for the logger and calibration math
docs/build-and-test.md          wiring, LED resistor math, standards, calibration procedure
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
```

`tools/log_serial.py` needs `pyserial`. Tests (no hardware needed): `pip install pytest`, then `pytest tests/`.

## Try it with example data

`data/example/` has **simulated** files (generated, not measured) so the scripts can be run without the hardware; see [`data/example/README.md`](data/example/README.md).

## License

My code is MIT, matching the Open Colorimeter software ([`LICENSE`](LICENSE)). The hardware
I built from is IO Rodeo's, under CC-BY-4.0.
