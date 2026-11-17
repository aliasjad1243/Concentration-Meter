"""Calibration curve and repeatability from the meter's logged readings.

    python calibrate.py ../data/readings.csv ../data/standards.csv --json calibrations.json

readings.csv  - from tools/log_serial.py, label = <standard>_rep<NN> (e.g. S3_rep07)
standards.csv - standard,conc   (S0..S5, mg/L)

Absorbance A = log10(blank / raw). Each repeat's log lines are averaged into one value.
Fits A = m*conc + b (Beer-Lambert), then the inverse conc = k*A + c that the meter uses.
Repeatability = CV of the repeats on each standard (S0 skipped, its mean is ~0).
--json writes an entry in the meter's calibrations.json format (polyval order).
"""
import argparse
import csv
import json
import math
import re
from collections import defaultdict
from statistics import mean, stdev


def load(path):
    reps = defaultdict(lambda: defaultdict(list))
    with open(path) as fh:
        for r in csv.DictReader(l for l in fh if l.strip() and not l.startswith("#")):
            m = re.match(r"^(S\d+)_rep(\d+)$", r["label"])
            if m:
                reps[m.group(1)][int(m.group(2))].append(math.log10(float(r["blank"]) / float(r["raw"])))
    return {s: [mean(v) for _, v in sorted(rr.items())] for s, rr in reps.items()}


def fit(x, y):
    mx, my = mean(x), mean(y)
    m = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    b = my - m * mx
    ss_res = sum((yy - (m * xx + b)) ** 2 for xx, yy in zip(x, y))
    ss_tot = sum((yy - my) ** 2 for yy in y)
    return m, b, 1 - ss_res / ss_tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("readings")
    ap.add_argument("standards")
    ap.add_argument("--name", default="FD&C Blue 1")
    ap.add_argument("--units", default="mg/L")
    ap.add_argument("--json")
    a = ap.parse_args()

    absorb = load(a.readings)
    conc = {r["standard"]: float(r["conc"]) for r in csv.DictReader(open(a.standards))}
    names = [s for s in conc if s in absorb]
    x = [conc[s] for s in names]
    y = [mean(absorb[s]) for s in names]

    m, b, r2 = fit(x, y)
    k, c, _ = fit(y, x)
    print(f"A = {m:.5f} * conc {b:+.5f}   R^2 = {r2:.5f}")
    print(f"meter fit: conc = {k:.4f} * A {c:+.4f} {a.units}")

    print("\nstandard  conc   n   mean A    SD      CV %")
    cvs = []
    for s in names:
        v = absorb[s]
        cv = 100 * stdev(v) / mean(v) if len(v) > 1 and conc[s] > 0 else float("nan")
        if not math.isnan(cv):
            cvs.append(cv)
        print(f"{s:8s} {conc[s]:5.2f} {len(v):3d}  {mean(v):.4f}  {stdev(v) if len(v) > 1 else 0:.4f}  {cv:6.2f}")
    if cvs:
        print(f"\nworst CV across standards: {max(cvs):.2f} %  (target <= 2 %)")

    if a.json:
        entry = {"units": a.units, "led": "630", "fit_type": "linear",
                 "fit_coef": [round(k, 6), round(c, 6)], "range": {"min": 0.0, "max": round(max(y) * 1.05, 3)}}
        json.dump({a.name: entry}, open(a.json, "w"), indent=2)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
