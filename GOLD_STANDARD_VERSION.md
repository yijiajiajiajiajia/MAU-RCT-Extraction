# Gold standard version note

**Current version: gold_v4 (2026-11-10).** gold_v4 = gold_v3 with the gold-standard rules applied consistently (see "gold_v4" below).

**gold_v3 (2026-11-09).** gold_v3 = gold_v2 plus the full numeric re-verification described under "Full re-verification (gold_v3)" below.

**gold_v2 (2026-11-09).** The gold-standard files in commit `f62c788` were not the final version; a review found problems that are corrected here. Use gold_v2 for all re-analysis and new experiments. `f62c788` is kept unchanged for traceability only.

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

## Full re-verification (gold_v3)

After gold_v2, every Design_Info and Atomic_Outcomes value of the 88 included studies (plus the participant counts in Study_Info) was compared cell by cell with the source PDF. Totals: 9,613 cells checked; 340 wrong; 449 derived; 192 format; 99 unverifiable; 124 ambiguous; 212 reported outcomes without a gold row. Details, per-paper counts and the list of items left open are in [`gold_verification_2026-11-09/`](gold_verification_2026-11-09/). Every wrong cell with a printed PDF value was corrected and logged in `gold_change_log.csv`; nine files had blocks of columns shifted by one header and were realigned. 16 wrong cells whose correct value is not printed in the article were emptied on 2026-11-10 (rule: a value that is not printed is not filled in; each is logged in `gold_change_log.csv`). For the same reason, 17 values that had been calculated and entered during the re-verification (11 SDs converted from standard errors, 6 counts or differences worked out from printed percentages or group values) were emptied again. On 2026-11-10 the same rule was applied to the values already in the gold standard that the re-verification had marked as calculated or not found in the article: 258 cells were emptied (counts worked out from percentages or by subtraction, values of a whole group copied to its sub-arms, overall mean age copied to each arm, deaths entered as 0 when the article does not mention deaths). Kept: follow-up duration converted to weeks (a unit conversion), sex counts in single-sex trials, zero counts the article states in words, and unit labels. In text7-4 four rows whose role fields sat seven columns to the left were moved back. Omission and ambiguous items are listed in `gold_verification_2026-11-09/open_items.csv` and were not changed.

**Rule for the gold standard:** only values that can be located directly in the article are kept. A value that is not printed is left empty, so that a model output in that cell is counted as a hallucination. Unit conversions (for example months to weeks) are kept.

## gold_v4 (2026-11-10)

Two rules, both stated in the paper, were applied to every file:

1. **Only printed values.** A value that is not printed in the article is left empty; unit conversions (months to weeks) are kept. 291 cells were emptied (see above).
2. **Only configured outcomes.** Each clinical area has a configured list of outcomes to extract (below). Rows for other outcomes were removed (47 rows in 9 files). Outcomes on the list that the article prints but the gold standard had no row for were added (208 rows and 10 cells in 33 files, printed values only; each row was checked against the PDF text or page image). One further wrong cell found on the way was corrected (text4-18, tremor at week 14).

Configured outcome lists:
- Breast cancer surgery: total operative time; nipple necrosis rate; overall wound-related complications; length of hospital stay.
- Schizophrenia: relapse rate; hospital admission rate; discontinuation rate; extrapyramidal symptoms; substantial weight gain; abnormally elevated serum glucose concentration / glucose intolerance; hyperprolactinaemia; death; suicide attempts.
- Cardiovascular: major adverse cardiovascular events; myocardial infarction; stroke or cerebrovascular events; cardiovascular disease mortality; all-cause mortality.
- Type 2 diabetes: myocardial infarction; stroke; retinopathy; photocoagulation; visual deterioration or blindness; microalbuminuria; renal failure; all-cause mortality; death from cardiovascular causes; congestive heart failure; peripheral vascular events; neuropathy; amputation; severe hypoglycaemia.
- Orthopedic rehabilitation: pain intensity (VAS); disease-specific functional indices (WOMAC, KOOS); balance ability; postural stability parameters; global proprioception; knee flexion–extension range of motion; active knee flexion angle; five-times sit-to-stand time; gait-related parameters (knee extension moment, functional weight-bearing symmetry); walking speed; timed standing task completion time; LEFS; ABC scale; HSS knee score; rehabilitation program adherence; hospital readmission rate; patient satisfaction; healthcare costs.

Later on 2026-11-10 the items the re-verification had marked `ambiguous` were reviewed: 48 cells that held a pooled or whole-group value under a single arm (or a count the article does not print) were emptied, and 13 cells were corrected against the article (direction flag of extrapyramidal and discontinuation outcomes in text4-3 and text4-13, baseline follow-up week and p value in text4-13, arm size of the 25 mg arm in text4-2). Where the article itself prints two different numbers (table versus text), the gold standard keeps the value it had.

Every change is logged in `gold_change_log.csv`. Scores reported in the paper were computed with the earlier gold standard and have to be recomputed with gold_v4.

## Reproducibility note

Model outputs (`Results in JSON Format`, `Excel File of Results …`) are historical outputs of the submitted system and were **not** modified. Files under `Gold Standard/` changed as listed above; 21 processed TXT files gained their missing header/footer citation lines (txt_v2, see [`INPUT_TEXT_VERSION.md`](INPUT_TEXT_VERSION.md)).
