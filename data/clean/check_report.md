# Check report

2522 rows checked. Failures: 0.

- PASS UK monthly series has every month from 2004-03 to 2021-09 (211 months)
- PASS UK: every month has at least as many licences as licence holders (one person can hold several licences)
- PASS UK: the 8 sector columns add up to 'Active Licences' in every month except 2018-04, where the source itself differs by 1 licence (kept as published)
- INFO UK: where the 2021 and 2026 releases overlap:
    2020-01-02: quarterly headcount 360,116 vs monthly series 359,891 for 2020-01 (difference +225, 0.06%)
    2020-04-01: quarterly headcount 364,724 vs monthly series 364,808 for 2020-04 (difference -84, 0.02%)
    2020-07-01: quarterly headcount 362,300 vs monthly series 362,398 for 2020-07 (difference -98, 0.03%)
    2020-10-01: quarterly headcount 363,828 vs monthly series 363,962 for 2020-10 (difference -134, 0.04%)
    2021-01-04: quarterly headcount 369,113 vs monthly series 369,213 for 2021-01 (difference -100, 0.03%)
    2021-04-01: quarterly headcount 375,111 vs monthly series 375,413 for 2021-04 (difference -302, 0.08%)
    2021-07-01: quarterly headcount 380,781 vs monthly series 381,004 for 2021-07 (difference -223, 0.06%)
- PASS UK: the two releases agree within 1% wherever they overlap (largest gap 0.08%)
- PASS Japan 2021-2025: regular plus temporary guards equals the total in every year
- PASS Japan: 12 years appear in more than one publication and all agree
- PASS Japan: clean table matches the sources for every year
- PASS Japan 2025 total matches the report text (令和７年12月末現在、59万6,985人)
- PASS Australia: summed rows match the ABS's own Table 1 for all 80 November-quarter figures checked
- PASS US: the spreadsheet figures match the BLS web tables for all 16 figures read both ways (2016-2023)
- PASS Every value is positive
- PASS No country, period and measure appears twice
