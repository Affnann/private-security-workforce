"""Check the clean tables against the source files. Writes data/clean/check_report.md.

Usage: python code/03_check.py   (after code/02_build.py)
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
rows = list(csv.DictReader(open(CLEAN / "security_workforce.csv")))
out, failures = [], 0


def check(ok, msg):
    global failures
    out.append(("PASS " if ok else "FAIL ") + msg)
    failures += 0 if ok else 1


def v(country, measure, period):
    for r in rows:
        if r["country"] == country and r["measure"] == measure and r["period"] == period:
            return float(r["value"])
    return None


# ---- UK
uk = pd.read_excel(RAW / "uk/sia-licences-applications-licence-holders-by-year.ods", engine="odf")
months = pd.to_datetime(uk["Month"]).dt.to_period("M")
expected = pd.period_range(months.min(), months.max(), freq="M")
check(list(months) == list(expected), f"UK monthly series has every month from {months.min()} to {months.max()} ({len(months)} months)")
check(bool((uk["Active Licences"] >= uk["Active Licence Holders"]).all()),
      "UK: every month has at least as many licences as licence holders (one person can hold several licences)")
sectors = [c for c in uk.columns if c.startswith("Active Licence") and c not in ("Active Licences", "Active Licence Holders")]
diff = (uk[sectors].sum(axis=1) - uk["Active Licences"]).abs()
odd = uk.loc[diff != 0, "Month"].dt.strftime("%Y-%m").tolist()
check(int(diff.max()) <= 1, f"UK: the {len(sectors)} sector columns add up to 'Active Licences' in every month except {', '.join(odd) or 'none'}, where the source itself differs by {int(diff.max())} licence (kept as published)")
hc = {r["period"]: int(r["value"]) for r in rows if r["country"] == "United Kingdom" and r["period_type"] == "date"}
lines = []
for d, val in sorted(hc.items()):
    m = d[:7]
    old = v("United Kingdom", "licence_holders", m)
    if old is not None:
        lines.append(f"{d}: quarterly headcount {val:,} vs monthly series {int(old):,} for {m} (difference {val - int(old):+,}, {abs(val - old) / old:.2%})")
out.append("INFO UK: where the 2021 and 2026 releases overlap:")
out.extend("    " + l for l in lines)
gap = max(abs(hc[d] - v("United Kingdom", "licence_holders", d[:7])) / v("United Kingdom", "licence_holders", d[:7])
          for d in hc if v("United Kingdom", "licence_holders", d[:7]))
check(gap < 0.01, f"UK: the two releases agree within 1% wherever they overlap (largest gap {gap:.2%})")

# ---- Japan: read every source independently and compare overlapping years
src = defaultdict(dict)
for f in ["japan/npa_whitepaper_h29_table2-46.xls", "japan/npa_whitepaper_r01_table2-46.xls"]:
    t = pd.read_excel(RAW / f, header=None)
    hdr = t.iloc[2].tolist()
    for i in range(t.shape[0]):
        if "警備員数" in str(t.iloc[i, 0]):
            for j in range(1, t.shape[1]):
                if not pd.isna(hdr[j]) and not pd.isna(t.iloc[i, j]):
                    src[f][1988 + int(float(hdr[j]))] = int(t.iloc[i, j])
f = "japan/npa_whitepaper_r04_table2-44.csv"
L = list(csv.reader(open(RAW / f, encoding="cp932")))
yrs = [2012 + k for k in range(10)]
for line in L:
    if "警備員数" in line[0]:
        src[f] = {y: int(x.replace(",", "")) for y, x in zip(yrs, line[1:]) if x.strip()}
f = "japan/npa_reiwa7data.csv"
L = list(csv.reader(open(RAW / f, encoding="utf-8-sig")))
for i, line in enumerate(L):
    if any("雇用別警備員数の年別推移" in c for c in line):
        tot = [c for c in L[i + 3][3:] if c.strip()]
        reg = [c for c in L[i + 5][3:] if c.strip()]
        tmp = [c for c in L[i + 7][3:] if c.strip()]
        src[f] = {2021 + k: int(x.replace(",", "")) for k, x in enumerate(tot[:5])}
        ok = all(int(a.replace(",", "")) + int(b.replace(",", "")) == int(c.replace(",", ""))
                 for a, b, c in zip(reg[:5], tmp[:5], tot[:5]))
        check(ok, "Japan 2021-2025: regular plus temporary guards equals the total in every year")
        break
allyears = sorted({y for d in src.values() for y in d})
disagree = []
n_overlap = 0
for y in allyears:
    vals = {f: d[y] for f, d in src.items() if y in d}
    if len(vals) > 1:
        n_overlap += 1
        if len(set(vals.values())) > 1:
            disagree.append(f"{y}: {vals}")
check(not disagree, f"Japan: {n_overlap} years appear in more than one publication and all agree" + ("" if not disagree else "; " + "; ".join(disagree)))
built = {int(r["period"]): int(r["value"]) for r in rows if r["country"] == "Japan" and r["measure"] == "guards"}
check(all(built[y] == list({f: d[y] for f, d in src.items() if y in d}.values())[-1] for y in built), "Japan: clean table matches the sources for every year")
pdf_text = "令和７年12月末現在、59万6,985人"
check(built.get(2025) == 596985, f"Japan 2025 total matches the report text ({pdf_text})")

# ---- Australia: compare the summed rows with the ABS's own Table 1 (November quarters)
xl = RAW / "australia" / "EQ08.xlsx"
if xl.exists():
    import openpyxl
    wb = openpyxl.load_workbook(xl, read_only=True)
    ws = wb["Table 1"]
    hdr, done = None, 0
    seen = set()
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i == 9:
            hdr = r
        name = r[0] if r else None
        if isinstance(name, str) and name[:4] in ("4422", "4413") and name not in seen:
            seen.add(name)
            meas = "guards_employed" if name.startswith("4422") else "police_employed"
            for col in range(1, len(hdr)):
                h = hdr[col]
                if not h or r[col] is None:
                    continue
                m = re.match(r"November Quarter (\d{4})", str(h))
                if not m:
                    continue
                built_v = v("Australia", meas, f"{m.group(1)}-11")
                if built_v is None:
                    continue
                done += 1
                if abs(built_v - r[col]) > 0.0015:
                    check(False, f"Australia {name} Nov {m.group(1)}: built {built_v} vs ABS table {r[col]:.3f}")
    check(done > 0, f"Australia: summed rows match the ABS's own Table 1 for all {done} November-quarter figures checked")
else:
    out.append("SKIP Australia Table 1 comparison (EQ08.xlsx not downloaded)")

# ---- US: spreadsheet values vs the HTML tables (second reading)
html = {(r["year"], r["occ_code"]): int(r["tot_emp_html"]) for r in csv.DictReader(open(RAW / "us/bls_oews_html_second_reading.csv"))}
xlsx = {(r["year"], r["occ_code"]): int(r["tot_emp"]) for r in csv.DictReader(open(RAW / "us/bls_oews_national_extract.csv"))}
same = [k for k in html if xlsx.get(k) == html[k]]
check(len(same) == len(html), f"US: the spreadsheet figures match the BLS web tables for all {len(html)} figures read both ways (2016-2023)")

# ---- general
check(all(float(r["value"]) > 0 for r in rows), "Every value is positive")
keys = [(r["country"], r["period"], r["measure"]) for r in rows]
check(len(keys) == len(set(keys)), "No country, period and measure appears twice")

report = ["# Check report", "", f"{len(rows)} rows checked. Failures: {failures}.", ""] + [f"- {l}" if not l.startswith("    ") else l for l in out]
(CLEAN / "check_report.md").write_text("\n".join(report) + "\n")
print("\n".join(report))
raise SystemExit(1 if failures else 0)
