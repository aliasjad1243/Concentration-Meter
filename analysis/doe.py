"""One-factor DOE: which of the 3 tube-holder designs works best.

    python doe.py ../data/doe_holders.csv

doe_holders.csv: design,rep,absorbance,dark_raw
  - same S3 tube removed and re-seated 10 times per design -> absorbance
  - LED off, tube in place -> dark_raw (outside light leaking into the sensor)

Factor: holder design (A, B, C). Two responses:
  1. seating consistency - one-way ANOVA on |absorbance - design median| (Brown-Forsythe)
  2. stray light         - one-way ANOVA on dark counts
"""
import csv
import sys
from collections import defaultdict
from statistics import mean, median, stdev


def anova(groups):
    allv = [v for g in groups.values() for v in g]
    grand = mean(allv)
    k, n = len(groups), len(allv)
    ssb = sum(len(g) * (mean(g) - grand) ** 2 for g in groups.values())
    ssw = sum(sum((v - mean(g)) ** 2 for v in g) for g in groups.values())
    f = (ssb / (k - 1)) / (ssw / (n - k))
    try:
        from scipy.stats import f as fdist
        p = fdist.sf(f, k - 1, n - k)
    except ImportError:
        p = None
    return f, k - 1, n - k, p


def show(title, groups):
    f, d1, d2, p = anova(groups)
    ptxt = f"p = {p:.4f}" if p is not None else "(install scipy for p)"
    print(f"{title}: F({d1},{d2}) = {f:.2f}  {ptxt}")


def main():
    absorb, dark = defaultdict(list), defaultdict(list)
    for r in csv.DictReader(open(sys.argv[1])):
        if r["absorbance"]:
            absorb[r["design"]].append(float(r["absorbance"]))
        if r.get("dark_raw"):
            dark[r["design"]].append(float(r["dark_raw"]))

    for d, v in sorted(absorb.items()):
        print(f"design {d}: n={len(v)}  mean A={mean(v):.4f}  SD={stdev(v):.4f}  CV={100 * stdev(v) / mean(v):.2f} %"
              + (f"  dark={mean(dark[d]):.0f} counts" if dark[d] else ""))
    show("seating consistency", {d: [abs(x - median(v)) for x in v] for d, v in absorb.items()})
    if dark:
        show("stray light", dict(dark))


if __name__ == "__main__":
    main()
