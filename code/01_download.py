"""Download the official source files into data/raw/.

UK, Japan and Australia download directly. The US Bureau of Labor Statistics
blocks automated downloads, so its two figures per year were read from the
official files listed in data/raw/us/ (see data/README.md); this script only
prints those addresses.

Usage: python code/01_download.py
"""
import hashlib
import json
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
UA = {"User-Agent": "Mozilla/5.0 (research data download)"}

FILES = {
    "uk/sia-licences-applications-licence-holders-by-year.ods":
        "https://assets.publishing.service.gov.uk/media/614b16e5e90e077a368ffbfc/sia-licences-applications-licence-holders-by-year.ods",
    "uk/sia-2a-headcount.csv":
        "https://assets.publishing.service.gov.uk/media/69cb9f2fb5ac47b0874f3f1d/sia-2a-headcount.csv",
    "japan/npa_reiwa7data.csv":
        "https://www.npa.go.jp/publications/statistics/safetylife/reiwa7data.csv",
    "japan/npa_reiwa7keibigaikyo.pdf":
        "https://www.npa.go.jp/publications/statistics/safetylife/reiwa7keibigaikyo.pdf",
    "japan/npa_whitepaper_r04_table2-44.csv":
        "https://www.npa.go.jp/hakusyo/r04/toukei/02/44.csv",
    "japan/npa_whitepaper_r01_table2-46.xls":
        "https://www.npa.go.jp/hakusyo/r01/toukei/02/46.xls",
    "japan/npa_whitepaper_h29_table2-46.xls":
        "https://www.npa.go.jp/hakusyo/h29/toukei/02/46.xls",
    "australia/EQ08.xlsx":
        "https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia-detailed/mar-2026/EQ08.xlsx",
}

US_FILES = [f"https://www.bls.gov/oes/special-requests/oesm{y:02d}nat.zip" for y in range(14, 26)]


def main():
    log = {}
    for rel, url in FILES.items():
        dest = RAW / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
        dest.write_bytes(data)
        log[rel] = {"url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        print(f"{rel}: {len(data):,} bytes")
    (RAW / "download_log.json").write_text(json.dumps(log, indent=2))
    print("\nUS figures come from these official files (download them in a browser):")
    for u in US_FILES:
        print(" ", u)


if __name__ == "__main__":
    main()
