# Build and test notes

## Wiring

```
Feather (CircuitPython) ──Stemma QT──> LED board J1 ──J2──> TSL2591 breakout
   GND ─ 3V3 ─ SDA ─ SCL                (pass-through)        GND ─ VIN ─ SDA ─ SCL
```

The LED board only uses 3V3 and GND from the connector; SDA/SCL pass straight through to the
TSL2591 (I²C address 0x29). The cuvette sits between the LED and the sensor.

## LED and resistor

FD&C Blue No. 1 absorbs most strongly near 630 nm, so the board uses a 630 nm red LED
(V_f ≈ 2.0 V). Target about 16 mA from the 3.3 V rail:

```
R  = (3.3 V − 2.0 V) / 0.016 A = 81 Ω   → nearest E12 value 82 Ω
I  = 1.3 V / 82 Ω               = 15.9 mA
P_R   = 15.9 mA² × 82 Ω         = 21 mW   (a 1/8 W through-hole resistor is plenty)
P_LED = 2.0 V × 15.9 mA         = 32 mW
```

The LED is always on, so the blank reading is taken with the same current every time.

## Dye standards (from a 100 mg/L stock, made up to 50 mL)

| Standard | mg/L | Stock (mL) |
|---|---|---|
| S0 | 0 | 0 (water only, also the blank) |
| S1 | 1.5 | 0.75 |
| S2 | 3.0 | 1.50 |
| S3 | 4.5 | 2.25 |
| S4 | 6.0 | 3.00 |
| S5 | 7.5 | 3.75 |

7.5 mg/L stays inside the meter's 0–0.81 absorbance range for Blue 1.

## Calibration run

1. Turn on `serial_log` in `configuration.json`, start `tools/log_serial.py`.
2. Blank with S0, then for each standard set `log_label` to `S<n>_rep<NN>`, seat the tube,
   wait for 3 log lines, remove. 10 repeats per standard.
3. `python analysis/calibrate.py data/readings.csv data/standards.csv --json calibrations.json`
4. Copy the entry into the meter's `calibrations.json` so it reads mg/L directly.

## Holder DOE

Three holder designs (A, B, C) modeled in Creo and 3D printed. For each: re-seat the same S3
tube 10 times and record absorbance, then turn the LED off with the tube in and record the
dark count (outside light). `python analysis/doe.py data/doe_holders.csv`
