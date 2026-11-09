# Gold standard version note

**Current version: gold_v2 (2026-11-09).** The gold-standard files in commit `f62c788` were not the final version; a review found problems that are corrected here. Use gold_v2 for all re-analysis and new experiments. `f62c788` is kept unchanged for traceability only.

## What changed from gold_v1 to gold_v2

Every change is listed cell by cell in [`gold_change_log.csv`](gold_change_log.csv) (study, file, sheet, cell, field, old value, new value, reason with bibliographic evidence).

| Study | Field | gold_v1 | gold_v2 | Why |
|---|---|---|---|---|
| text3-5 | year | 2024 | 2022 | Toesca et al., Ann Surg 2022 (online 2021). The input text contains no year; 2024 was unsupported. |
| text3-1 | doi | 10.1016/j.ejso.2020.08.013 | 10.1016/j.suronc.2020.09.022 | Previous DOI resolves to a different article. Input text contains no DOI. |
| text3-1 | journal | "Elsevier (journal not explicitly named…)" | Surgical Oncology | Placeholder replaced by the journal of record. |
| text4-15 | year | 1972 | 1973 | Acta Psychiatr Scand Suppl 1973;241; the gold journal field itself says 1973. |
| text4-16 | year | 1974-75 | 1980 | "1974-75" is the enrolment period quoted in the text; the article was published in 1980. |
| text3-3, text4-19, text4-32, text4-54 | doi | (empty) | DOI printed in the article header/footer | The input TXT now carries the line (restored 2026-11-09, see `txt_change_log.csv`); an empty gold cell would score a correct extraction as a hallucination. |
| text5-17, text5-20, text4-3 | year, doi, journal (12 cells in all) | (empty) | value printed in the article header/footer | Same reason; text5-20's TXT already contained the DOI line. |
| text7-7 | whole file | previous file was not the final version | replaced (2026-11-09) | Review found the previous file did not correspond to the text7-7 report; replaced with a record extracted from the source PDF (Piqueras et al., J Rehabil Med 2013;45:392-396): 1 study record, 2 arms, 38 outcome records. |

## How the check was done

All 90 gold-standard `Study_Info` records (title, year, DOI) were compared with Crossref and PubMed on 2026-11-09. 85 records matched. In addition, three records have a printed year that differs by one from the journal's publication year (text4-43: printed 1968 / published 1969; text7-8: 2017 online / 2018 print; text7-1: 2019 online / 2020 print). These were **not** changed; the gold standard keeps the year printed in the source document.

## text7-7 extraction conventions

- Per-arm age is not reported in the paper and is left empty; gender counts are derived from the reported percentages (17% men of 70 controls, 37.5% men of 72 IVT).
- Table II values are stored as within-group change from baseline (mean, SD) with the between-group p-value; the 3-month IVT column is labelled "Control (n=68)" in the printed table (typesetting error).
- Muscle-strength outcomes are included although they are outside the configured outcome-domain list; `domain_match` says so.

## What was NOT checked

Only study-level bibliographic fields were verified against external sources. Arm-level and outcome-level numerical values (Design_Info, Atomic_Outcomes) have not been re-verified against the source PDFs in this pass. That is a separate step (sampled source re-check) in the revision plan.

## Reproducibility note

Model outputs (`Results in JSON Format`, `Excel File of Results …`) are historical outputs of the submitted system and were **not** modified. Files under `Gold Standard/` changed as listed above; 21 processed TXT files gained their missing header/footer citation lines (txt_v2, see [`INPUT_TEXT_VERSION.md`](INPUT_TEXT_VERSION.md)).
