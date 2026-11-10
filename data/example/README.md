# Example data (Concentration Meter)

**⚠ Simulated data, not measurements.** Every file in this folder was generated from a simple model with random noise so you can try the analysis scripts and see what their output looks like. None of it was recorded from the device. Real results go in `data/` (outside this folder).

## Files

- `simulated_readings.csv`: 6 standards × 10 repeats × 3 log lines, same format `firmware/serial_logger.py` prints

## Try it

```
python analysis/calibrate.py data/example/simulated_readings.csv data/standards.csv
```

Output:

```
A = 0.09574 * conc +0.00999   R^2 = 0.99921
meter fit: conc = 10.4365 * A -0.1013 mg/L

standard  conc   n   mean A    SD      CV %
S0        0.00  10  0.0002  0.0053     nan
S1        1.50  10  0.1563  0.0020    1.29
S2        3.00  10  0.3049  0.0040    1.31
S3        4.50  10  0.4479  0.0040    0.88
S4        6.00  10  0.5853  0.0034    0.59
S5        7.50  10  0.7195  0.0024    0.34

worst CV across standards: 1.31 %  (target <= 2 %)
```
