"""Build the clean tables from the files in data/raw/.

Writes:
  data/clean/security_workforce.csv   every figure, one row per country, period and measure
  data/clean/annual_by_country.csv    one comparable figure per country and year
  data/raw/australia/eq08_protective_service_extract.csv  (the rows used from the 56 MB ABS file)

Usage: python code/02_build.py
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

COLS = ["country", "period", "period_type", "workforce", "measure", "value", "unit",
        "rse_pct", "source", "source_file", "source_location"]
rows = []


def add(**k):
    r = {c: "" for c in COLS}
    r.update(k)
    rows.append(r)


def num(x):
    return int(str(x).replace(",", "").strip())


# ---------------------------------------------------------------- UK
SIA = "Security Industry Authority (UK), FOI release on GOV.UK"
f = "uk/sia-licences-applications-licence-holders-by-year.ods"
uk = pd.read_excel(RAW / f, engine="odf")
sector_cols = {
    "Active Licences": "active_licences_all_sectors",
    "Active Licences - Security Guarding": "active_licences_security_guarding",
    "Active Licences - Door Supervision": "active_licences_door_supervision",
    "Active Licence - Public Space Surveillance": "active_licences_cctv",
    "Active Licences - Close Protection": "active_licences_close_protection",
    "Active Licence - Cash and Valuables in Transit": "active_licences_cash_in_transit",
    "Active Licence Key Holding": "active_licences_key_holding",
    "Active Licences - Vehicle Immobilisation": "active_licences_vehicle_immobilisation",
    "Active Licences - Non Frontline": "active_licences_non_frontline",
}
for _, r in uk.iterrows():
    period = pd.Timestamp(r["Month"]).strftime("%Y-%m")
    add(country="United Kingdom", period=period, period_type="month", workforce="private_security",
        measure="licence_holders", value=int(r["Active Licence Holders"]), unit="persons",
        source=SIA, source_file=f, source_location="column 'Active Licence Holders'")
    for col, m in sector_cols.items():
        add(country="United Kingdom", period=period, period_type="month", workforce="private_security",
            measure=m, value=int(r[col]), unit="licences",
            source=SIA, source_file=f, source_location=f"column '{col}'")

f = "uk/sia-2a-headcount.csv"
with open(RAW / f, encoding="utf-8-sig") as fh:
    rd = csv.reader(fh)
    next(rd)
    for line in rd:
        if not line or not line[0].strip():
            continue
        d, m, y = line[0].strip().split("/")
        add(country="United Kingdom", period=f"{y}-{m}-{d}", period_type="date",
            workforce="private_security", measure="licence_holders", value=num(line[1]), unit="persons",
            source=SIA + " (FOI 0585, data as of 22 January 2026)", source_file=f,
            source_location="column 'Active Licence Holders'")

# ---------------------------------------------------------------- Japan
NPA = "National Police Agency (Japan)"
jp_guards, jp_cos = {}, {}   # year -> (value, file, location); later files overwrite earlier


def jp_era(label):
    label = str(label).strip()
    if label.startswith("令和元"):
        return 2019
    m = re.match(r"(平成|令和)?\s*(\d+)", label.replace(".0", ""))
    if not m:
        return None
    n = int(m.group(2))
    era = m.group(1)
    return 2018 + n if era == "令和" else 1988 + n


def jp_wp_xls(f, era_default):
    t = pd.read_excel(RAW / f, header=None)
    hdr = t.iloc[2].tolist()
    for i in range(t.shape[0]):
        lab = str(t.iloc[i, 0])
        target = jp_cos if "警備業者数" in lab else jp_guards if "警備員数" in lab else None
        if target is None:
            continue
        for j in range(1, t.shape[1]):
            if pd.isna(hdr[j]) or pd.isna(t.iloc[i, j]):
                continue
            n = int(float(hdr[j]))
            year = 1988 + n if era_default == "平成" else 2018 + n
            target[year] = (int(t.iloc[i, j]), f, f"row '{lab}', column {int(float(hdr[j]))}")


jp_wp_xls("japan/npa_whitepaper_h29_table2-46.xls", "平成")
jp_wp_xls("japan/npa_whitepaper_r01_table2-46.xls", "平成")

f = "japan/npa_whitepaper_r04_table2-44.csv"
lines = list(csv.reader(open(RAW / f, encoding="cp932")))
hdr = lines[2]
era = None
years = []
for h in hdr[1:]:
    h = h.strip()
    if h.startswith("平成"):
        era = "平成"
    elif h.startswith("令和"):
        era = "令和"
    if h.startswith("令和元"):
        years.append(2019)
        continue
    n = int(re.sub(r"\D", "", h))
    years.append(1988 + n if era == "平成" else 2018 + n)
for line in lines[3:]:
    lab = line[0]
    target = jp_cos if "警備業者数" in lab else jp_guards if "警備員数" in lab else None
    if target is None:
        continue
    for y, v in zip(years, line[1:]):
        target[y] = (num(v), f, f"row '{lab}'")

f = "japan/npa_reiwa7data.csv"
lines = list(csv.reader(open(RAW / f, encoding="utf-8-sig")))
jp_reg, jp_temp = {}, {}
for i, line in enumerate(lines):
    if any("雇用別警備員数の年別推移" in c for c in line):
        hdr = lines[i + 1]
        yrs = [2018 + int(re.sub(r"\D", "", c)) for c in hdr if re.match(r"R\d+年", c.strip())]
        for line2 in lines[i + 2:i + 12]:
            lab = (line2[2] if len(line2) > 2 else "").replace(" ", "").replace("　", "")
            vals = [c for c in line2[3:] if c.strip()][:len(yrs)]
            if lab.startswith("総数"):
                for y, v in zip(yrs, vals):
                    jp_guards[y] = (num(v), f, "table 雇用別警備員数の年別推移, row 総数")
            elif lab.startswith("常用警備員"):
                for y, v in zip(yrs, vals):
                    jp_reg[y] = (num(v), f, "table 雇用別警備員数の年別推移, row 常用警備員")
            elif lab.startswith("臨時警備員"):
                for y, v in zip(yrs, vals):
                    jp_temp[y] = (num(v), f, "table 雇用別警備員数の年別推移, row 臨時警備員")
        break
# 2025 company count is stated in the report text: 令和７年12月末現在、１万949業者
jp_cos[2025] = (10949, "japan/npa_reiwa7keibigaikyo.pdf", "page 1, section 1(1): 令和７年12月末現在、１万949業者")

for d, m, unit, loc_note in [(jp_guards, "guards", "persons", ""), (jp_reg, "guards_regular_employment", "persons", ""),
                             (jp_temp, "guards_temporary_employment", "persons", ""), (jp_cos, "security_companies", "companies", "")]:
    for y in sorted(d):
        v, f, loc = d[y]
        add(country="Japan", period=str(y), period_type="year_end", workforce="private_security",
            measure=m, value=v, unit=unit, source=NPA, source_file=f, source_location=loc)

# ---------------------------------------------------------------- Australia
ABS = "Australian Bureau of Statistics, Labour Force, Australia, Detailed (EQ08)"
ext = RAW / "australia" / "eq08_protective_service_extract.csv"
codes = {"4422 Security Officers and Guards": ("private_security", "guards_employed"),
         "4413 Police": ("police", "police_employed")}
if (RAW / "australia" / "EQ08.xlsx").exists():
    import openpyxl
    wb = openpyxl.load_workbook(RAW / "australia" / "EQ08.xlsx", read_only=True)
    agg = defaultdict(float)
    for r in wb["Data 1"].iter_rows(min_row=5, values_only=True):
        if r[3] in codes and r[4] is not None:
            agg[(r[0].strftime("%Y-%m"), r[3])] += r[4]
    with open(ext, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mid_quarter_month", "occupation", "employed_thousands"])
        for k in sorted(agg):
            w.writerow([k[0], k[1], f"{agg[k]:.6f}"])
au = defaultdict(dict)
for r in csv.DictReader(open(ext)):
    wf, m = codes[r["occupation"]]
    v = float(r["employed_thousands"])
    au[m][r["mid_quarter_month"]] = v
    add(country="Australia", period=r["mid_quarter_month"], period_type="mid_quarter_month", workforce=wf,
        measure=m, value=f"{v:.3f}", unit="thousand persons", source=ABS,
        source_file="australia/EQ08.xlsx (rows summed in australia/eq08_protective_service_extract.csv)",
        source_location=f"sheet 'Data 1', occupation '{r['occupation']}', all sexes and states summed")

# ---------------------------------------------------------------- US
BLS = "U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics (OEWS), May estimates"
us = defaultdict(dict)
for r in csv.DictReader(open(RAW / "us" / "bls_oews_national_extract.csv")):
    wf, m = ("private_security", "guards_employed") if r["occ_code"] == "33-9032" else ("police", "police_employed")
    us[m][int(r["year"])] = int(r["tot_emp"])
    add(country="United States", period=r["year"] + "-05", period_type="month", workforce=wf, measure=m,
        value=int(r["tot_emp"]), unit="persons", rse_pct=r["emp_prse_pct"], source=BLS,
        source_file=r["source_url"], source_location=f"{r['source_file']}, OCC_CODE {r['occ_code']}, TOT_EMP")

# ---------------------------------------------------------------- South Africa
PSIRA = "Private Security Industry Regulatory Authority (South Africa), annual reports as tabled in Parliament"
za = {}
f = "south_africa/psira_active_security_officers.csv"
for r in csv.DictReader(open(RAW / f)):
    v = int(r["active_registered_security_officers"])
    za[int(r["year_end"][:4])] = v
    add(country="South Africa", period=r["year_end"], period_type="date", workforce="private_security",
        measure="active_registered_security_officers", value=v, unit="persons", source=PSIRA,
        source_file=r["source_url"], source_location=f"{r['source_report']}, PDF page {r['source_pdf_page']} (financial year {r['financial_year']})")

with open(CLEAN / "security_workforce.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)

# ---------------------------------------------------------------- annual comparison
ACOLS = ["country", "year", "reference_point", "private_security", "private_security_measure",
         "police", "police_measure", "guards_per_police_officer", "note"]
ann = []
uk_hold = {r["period"]: int(r["value"]) for r in rows
           if r["country"] == "United Kingdom" and r["measure"] == "licence_holders"}
for y in range(2005, 2027):
    m = f"{y}-01"
    if m in uk_hold:
        v, ref = uk_hold[m], "January (monthly series, FOI release 2021)"
    else:
        dates = sorted(p for p in uk_hold if p.startswith(f"{y}-01-"))
        if not dates:
            continue
        v, ref = uk_hold[dates[0]], f"{dates[0]} (quarterly headcount, FOI release 2026)"
    ann.append(dict(country="United Kingdom", year=y, reference_point=ref, private_security=v,
                    private_security_measure="people holding at least one active SIA licence",
                    note="Police not included: no single UK-wide police headcount in the sources used"))
for y in sorted(jp_guards):
    ann.append(dict(country="Japan", year=y, reference_point="31 December",
                    private_security=jp_guards[y][0],
                    private_security_measure="security guards employed by authorised security companies (警備員数)",
                    note="Police not included: the National Police Agency tables used do not give a police headcount"))
for y in range(1987, 2026):
    qs = [f"{y}-{mm}" for mm in ("02", "05", "08", "11")]
    if all(q in au["guards_employed"] for q in qs) and all(q in au["police_employed"] for q in qs):
        g = sum(au["guards_employed"][q] for q in qs) / 4 * 1000
        p = sum(au["police_employed"][q] for q in qs) / 4 * 1000
        ann.append(dict(country="Australia", year=y, reference_point="average of the four quarters",
                        private_security=round(g, -2), private_security_measure="employed as Security Officers and Guards (ANZSCO 4422), survey estimate",
                        police=round(p, -2), police_measure="employed as Police (ANZSCO 4413), survey estimate",
                        guards_per_police_officer=f"{g / p:.2f}",
                        note="Both from the same survey; rounded to the nearest 100"))
for y in sorted(za):
    ann.append(dict(country="South Africa", year=y, reference_point="31 March (end of the financial year)",
                    private_security=za[y], private_security_measure="security officers registered with PSIRA and recorded as employed (active)",
                    note="Police not included: PSIRA does not count police"))
for y in sorted(us["guards_employed"]):
    g, p = us["guards_employed"][y], us["police_employed"][y]
    ann.append(dict(country="United States", year=y, reference_point="May",
                    private_security=g, private_security_measure="employed as Security Guards (SOC 33-9032)",
                    police=p, police_measure="employed as Police and Sheriff's Patrol Officers (SOC 33-3051)",
                    guards_per_police_officer=f"{g / p:.2f}", note="Both from the same survey"))
with open(CLEAN / "annual_by_country.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=ACOLS)
    w.writeheader()
    for r in ann:
        r2 = {c: r.get(c, "") for c in ACOLS}
        if isinstance(r2["private_security"], float):
            r2["private_security"] = int(r2["private_security"])
        if isinstance(r2["police"], float):
            r2["police"] = int(r2["police"])
        w.writerow(r2)
print(f"{len(rows)} rows in security_workforce.csv, {len(ann)} rows in annual_by_country.csv")
