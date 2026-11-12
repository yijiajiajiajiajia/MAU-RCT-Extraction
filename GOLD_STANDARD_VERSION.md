# Gold standard version note

**Current version: gold_v9 (2026-11-12).** gold_v9 = gold_v8 after a fifth paper-by-paper review of all 87 trials (see "gold_v9" below).

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

**text4-52 removed (2026-11-10).** The source file stored as text4-52 was a second copy of the text4-51 article (Simon et al. 1978; identical PDF), so one trial had been included twice. The text4-52 input TXT, model outputs and gold-standard file were removed. The validation set now has 87 trials (psychiatry: 43).

## gold_v5 (2026-11-10): second paper-by-paper review

All 87 trials were read again against the article, one paper at a time, under the same two rules (only printed values, unit conversions kept; only configured outcomes).

- 126 cells emptied: values not printed for that arm (computed mean differences or risk ratios, counts computed from percentages or sums, a whole-sample or pooled value stored under a single arm, zeros that the article does not state).
- About 120 cells corrected: values that did not match the article (including a minus sign lost in the PDF text layer, text4-29), counts stored in the wrong column (text5-13), text in numeric cells, and labels that differed between the arms of the same outcome. In text7-6 the label of the printed t statistic was corrected (36 cells).
- 60 rows removed because they held no outcome value (the article does not report that outcome for that arm), and 16 rows removed as outside the configured outcome list.
- 721 rows and 107 cells added: configured outcomes that the article prints but the gold standard had no row or value for. Printed values only; every added value was checked to occur in the quoted article text.
- text4-51: the third randomised arm (standard neuroleptics, n = 63) was missing and was added.
- Not entered: numbers that can only be read from the low-resolution figures of text6-6 and text6-7 (UKPDS 33 and 34), because the digits cannot be read with certainty.
- Kept as they were: a median age stored in the age column (printed value), overall p values of multi-arm comparisons, single-sex counts and zeros stated in words.
- text5-4: the article prints "171 of 1131 (1.5%)" for cardiovascular events in the vitamin D group; the gold standard records the printed number 171.

## gold_v6 (2026-11-10): third paper-by-paper review

All 87 trials were read a third time against the article, including every row added in gold_v5 (value, arm column, time point and sign were checked on rendered page images where the table has three or more arm columns or change scores).

- No value added in gold_v5 was found to be wrong.
- 2 cells emptied (not printed for that arm) and 3 cells corrected (two dropout-reason texts with the arms swapped, text5-18 and text6-13; one participant number).
- 6 confidence-interval cells moved to the CI columns used by the other arm of the same outcome (text4-29, text4-34).
- 73 rows removed: 62 held no outcome value (mostly rows left empty after pooled values were emptied; text5-21 now has no outcome row because the article reports events only for the pooled factorial groups), 9 were exact duplicates of another row (text4-23, text5-16), 2 were outside the configured outcome list (text5-8).
- 117 rows and 6 cells added (configured outcomes printed in the article that still had no row).
- 170 labels made consistent between the arms of the same outcome (outcome name, outcome role, time-point role, follow-up weeks, arm name).
- Formatting: study_id filled in on the rows added in earlier versions (714 rows), and numbers stored as text converted to numbers (891 cells; values unchanged).

## gold_v7 (2026-11-10): fourth paper-by-paper review

All 87 trials were read a fourth time. More than 50 trials had no finding. No value added in gold_v5 or gold_v6 was found to be wrong.

- Two errors came from the OCR text layer of scanned PDFs and were found by reading the page images: text4-43 group size 250 corrected to 210 (9 cells) and text6-4 mean age 41 corrected to 47. Because of this, every number of the scanned PDFs that had so far been checked only against the text layer (15 trials, about 1,000 numbers) was compared with the page image; one further cell was emptied (text5-2, total analysed, not printed) and nothing else differed.
- 7 cells emptied or corrected because the value did not belong to the row (text4-40, text4-31, text4-32, text5-15, text6-9), 3 confidence-interval cells moved to the CI columns (text4-45), and one relative risk that is printed only in a low-resolution figure replaced by the risk reduction printed in the text (text6-7).
- 9 rows removed (8 duplicated control rows in text7-2, 1 mislabelled row in text4-31); 6 rows and 2 cells added.
- 83 labels made consistent between the arms of the same outcome.

Rows for which the article gives only a percentage, a p value or a qualitative statement are kept without a value (69 rows): the outcome is reported, but no count or mean is printed for the arm.

## gold_v8 (2026-11-10): two author decisions

- **text5-21** (2×2 factorial trial). The article reports death, myocardial infarction and stroke only for the pooled comparison groups of Table 3 (vitamin D versus no vitamin D; calcium versus no calcium), never for the randomized groups, so after gold_v5 the trial had no outcome row. The four pooled groups are now entered as arms (group sizes as printed in the table header) with the printed counts and p values: 4 design rows and 12 outcome rows added.
- **text4-18**. Six cells held the counts of four time points together (extrapyramidal symptoms, Table 4). They are split into one row per symptom and time point: 6 rows replaced by 40 rows. No value changed; the table was checked on the page image.

The gold standard now holds 87 trials and 1,988 outcome rows.

## gold_v9 (2026-11-12): fifth paper-by-paper review

All 87 trials were read a fifth time with the same five checks for every paper (values match the article; nothing that is not printed; no out-of-scope, empty or duplicate rows; consistent labels across arms; no configured outcome left out). 67 trials had no finding. No filled value was found to differ from the article.

- 4 rows removed: duration of the first rehospitalisation in text4-12 (2 rows; length of stay is not a configured outcome) and 2 rows without any value in text4-44.
- 3 rows added: prolactin-related adverse events of Table 4 in text4-21 (2 rows) and the vitamin D arm of the time-to-death outcome in text5-19 (1 row).
- 2 empty cells filled with printed values: text4-40 (one placebo patient became suicidal, stated in words) and text4-51 (analysed number of the third arm, read on the page image).
- 62 labels made consistent between the arms of the same outcome (outcome names, time_point_role, higher_is_better).

Points raised by the review and left unchanged on purpose: text7-1 cost difference (-2745; the article prints "$2,745 lower"), text7-9 p values on the post-intervention rows of the experimental group (the printed between-group p), text5-11 analysed numbers (the printed arm size).

The gold standard now holds 87 trials and 1,987 outcome rows.

Every change is logged in `gold_change_log.csv`. Scores reported in the paper were computed with the earlier gold standard and have to be recomputed with the current gold standard.

## Reproducibility note

Model outputs (`Results in JSON Format`, `Excel File of Results …`) are historical outputs of the submitted system and were **not** modified. Files under `Gold Standard/` changed as listed above; 21 processed TXT files gained their missing header/footer citation lines (txt_v2, see [`INPUT_TEXT_VERSION.md`](INPUT_TEXT_VERSION.md)).
