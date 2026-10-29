# Data sources

All sources were accessed on 29 October 2026. File addresses, sizes and SHA-256 fingerprints are in [`raw/download_log.json`](raw/download_log.json).

## United Kingdom: Security Industry Authority (SIA)

| File | What it is | Published |
|---|---|---|
| `raw/uk/sia-licences-applications-licence-holders-by-year.ods` | SIA response to a Freedom of Information request: active licences, active licence holders and licences by sector, every month from March 2004 to September 2021 | 23 September 2021, [GOV.UK](https://www.gov.uk/government/publications/sia-licences-applications-and-licence-holders-by-year) |
| `raw/uk/sia-2a-headcount.csv` | SIA response to Freedom of Information request FOI 0585: quarterly headcount of active licence holders, January 2020 to January 2026 (data as of 22 January 2026) | 31 March 2026, [GOV.UK](https://www.gov.uk/government/publications/statistical-data-about-sia-licence-holders-2020-to-2025) |

**Terms:** Crown copyright, Open Government Licence v3.0. Contains public sector information licensed under the Open Government Licence v3.0.

## Japan: National Police Agency (警察庁)

| File | What it is |
|---|---|
| `raw/japan/npa_reiwa7keibigaikyo.pdf` | 「令和７年における警備業の概況」 (Security business overview for 2025), with guards at the end of each year 2021-2025 and the number of authorised security companies at the end of 2025 |
| `raw/japan/npa_reiwa7data.csv` | The data file published with that report |
| `raw/japan/npa_whitepaper_r04_table2-44.csv` | 令和４年警察白書 statistics table 2-44: security companies and guards, 2012-2021 |
| `raw/japan/npa_whitepaper_r01_table2-46.xls` | 令和元年警察白書 statistics table 2-46: security companies and guards, 2008-2018 |
| `raw/japan/npa_whitepaper_h29_table2-46.xls` | 平成29年警察白書 statistics table 2-46: security companies and guards, 2007-2016 |

Each year in the clean table is taken from the most recent publication that covers it; every overlapping year agrees across publications (see `clean/check_report.md`). Japanese years are converted from the Japanese calendar (平成 1 = 1989, 令和 1 = 2019).

**Terms:** Public Data License 1.0 (公共データ利用規約（第1.0版）), as stated on the National Police Agency's site. 出典：「警備業の概況」「警察白書」（警察庁）を加工して作成. The clean table is edited from these files and is not an official National Police Agency product.

## Australia: Australian Bureau of Statistics (ABS)

| File | What it is |
|---|---|
| `raw/australia/EQ08.xlsx` (not stored in the repository, 56 MB) | *Labour Force, Australia, Detailed*, data cube EQ08: employed persons by occupation unit group of main job (ANZSCO 2013 v1.2), sex, and state and territory, August 1986 onwards; released 26 March 2026 |
| `raw/australia/eq08_protective_service_extract.csv` | The rows used, summed across sexes and states, made by `code/02_build.py`: unit groups 4422 Security Officers and Guards and 4413 Police |

**Terms:** Creative Commons Attribution 4.0 International. Source: Australian Bureau of Statistics, *Labour Force, Australia, Detailed*.

## United States: Bureau of Labor Statistics (BLS)

| File | What it is |
|---|---|
| `raw/us/bls_oews_national_extract.csv` | National employment (TOT_EMP) and its relative standard error (EMP_PRSE) for 33-9032 Security Guards and 33-3051 Police and Sheriff's Patrol Officers, May 2014 to May 2025, from the national Occupational Employment and Wage Statistics files `oesmYYnat.zip` (the address of each file is in the table) |
| `raw/us/bls_oews_html_second_reading.csv` | The same figures for 2016-2023 read separately from the BLS web tables `oes/YYYY/may/oes_nat.htm`, used as a check |

The BLS site refuses automated downloads, so these figures were read from the official files in a web browser; each row gives the file it came from.

**Terms:** Works of the US government, in the public domain.

## Not included

- **South Africa:** the Private Security Industry Regulatory Authority's annual reports could not be read from this workspace (the site's certificate fails to verify, and the reports are PDF files the browser could not extract). Planned for a later version.
- **Police for the UK and Japan:** the sources used give no police headcount measured the same way as their guard counts.
