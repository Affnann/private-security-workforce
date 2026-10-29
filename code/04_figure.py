"""Draw figures/security_workforce.png from data/clean/annual_by_country.csv.

Usage: python code/04_figure.py
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader(open(ROOT / "data" / "clean" / "annual_by_country.csv")))
ps, ratio = defaultdict(dict), defaultdict(dict)
for r in rows:
    ps[r["country"]][int(r["year"])] = int(r["private_security"]) / 1000
    if r["guards_per_police_officer"]:
        ratio[r["country"]][int(r["year"])] = float(r["guards_per_police_officer"])

style = {"United States": ("#15171A", "-"), "Japan": ("#8B2E2E", "-"),
         "United Kingdom": ("#4A4F57", "--"), "South Africa": ("#8B2E2E", "--"), "Australia": ("#4A4F57", ":")}
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.25, 1]})
for c in ["United States", "Japan", "South Africa", "United Kingdom", "Australia"]:
    have = [x for x in sorted(ps[c]) if x >= 2008]  # UK licensing was still being taken up before 2008
    xs = list(range(have[0], have[-1] + 1))  # missing years are left as gaps, not joined up
    col, ls = style[c]
    a.plot(xs, [ps[c].get(x, float("nan")) for x in xs], color=col, ls=ls, lw=1.8, label=c, marker="o" if c == "South Africa" else None, ms=2.5)
a.set_title("Private security workforce (thousands)", loc="left", fontsize=11)
a.set_xlim(2008, 2026)
a.set_ylim(0, None)
a.legend(frameon=False, fontsize=9)
for c in ["United States", "Australia"]:
    xs = sorted(ratio[c])
    col, ls = style[c]
    b.plot(xs, [ratio[c][x] for x in xs], color=col, ls=ls, lw=1.8, label=c)
b.axhline(1, color="#D9D5CE", lw=1)
b.set_title("Security guards per police officer", loc="left", fontsize=11)
b.set_ylim(0, None)
b.legend(frameon=False, fontsize=9)
for ax in (a, b):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
fig.text(0.01, 0.01, "Counts measure different things in each country (licence holders, employees, survey estimates); "
         "see the README. Ratios only where one source counts both.", fontsize=8, color="#4A4F57")
fig.tight_layout(rect=(0, 0.04, 1, 1))
(ROOT / "figures").mkdir(exist_ok=True)
fig.savefig(ROOT / "figures" / "security_workforce.png", dpi=150)
print("figures/security_workforce.png")
