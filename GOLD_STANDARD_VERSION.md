# Gold standard version note

**Current version: gold_v14 (2026-11-14).** gold_v14 = gold_v13 after one more check of every row and every cell against the article, this time including the study and arm description fields and a search for configured outcomes that had no row (see "gold_v14" below).

**gold_v13 (2026-11-14).** gold_v13 = gold_v12 after a row-by-row scope check against the configured outcome list; 80 rows outside the list were removed (see "gold_v13" below).

**gold_v12 (2026-11-13).** gold_v12 = gold_v11 after a final review in which every row and every filled cell was checked once more against the article (see "gold_v12" below).

**gold_v11 (2026-11-13).** gold_v11 = gold_v10 after a seventh review in which every row was re-extracted from the article without looking at the gold values and then compared with them (see "gold_v11" below).

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

## gold_v10 (2026-11-12): sixth paper-by-paper review and check of the description cells

**Sixth review (same five checks as the fifth).** No filled outcome value was found to differ from the article.

- 2 cells emptied: nephropathy counts in text6-4 (the article prints these counts for microalbuminuria, where they already are; for nephropathy it prints percentages only).
- 15 empty cells filled with printed values: text4-40 (six patients with extrapyramidal symptoms in the soluble-tablet group, stated in words), text6-9 (hazard ratio, CI and p for all-cause mortality), text6-8 (p values for two heart-failure outcomes).
- 2 rows added: all-cause withdrawals in the run-in and stabilisation phases of text4-45 (flow chart). 2 rows removed: one out-of-scope row without a value (text4-43) and one row without a count (text4-51).
- text5-15: higher_is_better corrected to 0 on the two rows that hold numbers of deaths. 11 labels made consistent between arms.

**Description cells.** Earlier reviews concentrated on the numeric cells. In this round every number, comparison sign and unit inside the free-text cells of Study_Info and Design_Info (criteria, setting, drop-out reasons, intervention and control details, duration, frequency, adherence) was compared with the article for all 87 trials (about 3,400 numbers; scanned PDFs on the page images). 23 fragments in 14 trials were corrected:

- wrong number: text5-11 (dose 0.70 → 0.76), text7-8 (drop-outs per group), text4-43 (age 20 → 19, an OCR misreading), text5-8 (block size 12 missing);
- lost sign or wrong unit: text5-13 (−2 SD), text5-15 (class ≥ II), text6-7 (> 120%), text4-54 (≤ 18), text5-6 (1 mcg, not 1 mg; ≥ 500), text6-8 (> 75%);
- not printed in the article: computed percentages removed (text5-16, text7-4); dosing frequency "once daily" removed (text4-3, text6-8); the word "mean" removed from a per-patient threshold (text4-42).

The gold standard holds 87 trials and 1,987 outcome rows.

## gold_v11 (2026-11-13): seventh review, blind re-extraction of every row

**Method.** The six earlier reviews compared the gold values with the articles. In this round the direction was reversed: for all 87 trials, every outcome row (1,987) and every arm of Design_Info (254) was given to a reader as labels only (arm, outcome, time point), the values were read from the article again, and the answers were compared with the gold cells by script. Every difference was then checked against the article by a second reader; for scanned articles on the page images. A difference was applied only when the article confirmed it.

**Wrong values (5 trials).**

- text4-18: the denominator of the 40 side-effect rows was 16; the table title prints n = 32 (crossover trial, all 32 patients received each drug). Corrected.
- text4-49: four p values had lost the "<" (p<0.003, p<0.0001). Corrected.
- text4-9: total_participants of Group A held the number analysed (15); the article prints 17 entered. Corrected.
- text4-44: one p_value cell held a sentence instead of a printed p value. Emptied.
- text7-9: number analysed per group (15) is not printed in the article. Emptied.

**Printed in the article but not entered (17 trials).**

- Effect sizes with confidence intervals on 20 rows: text4-28 (12 cause-specific hazard ratios), text7-1 (4 between-group differences), text4-7 (2 relative risks), text4-10 (log-rank statistic on 2 arm rows).
- 112 p values: text6-2 (42, comparisons with placebo), text4-29 (35, overall p of the three-group comparison), text7-1 (12), text4-44 (7), text4-49 (5), text4-28 (5), and one or two each in text4-10, text4-38, text4-42, text4-54.
- 19 Design_Info cells in 6 trials: age and SD (text3-2, text4-2, text4-35), number of men (text4-2, text4-9, text4-35), arm size (text5-19, text6-10).

**Made uniform.**

- text4-29: six cells held a pairwise p value while the other arms of the same outcome held the overall p value; all arm rows of an outcome now hold the printed overall p value.
- text4-19: four rows held four time points in one cell; split into one row per time point (16 rows, values unchanged).
- 91 labels that were in Chinese (time point "baseline", "pre-intervention", "post-intervention"; one arm name "Placebo") written in English; one outcome label in text6-10 made exact ("requiring medical assistance").

**Checked and not changed.** In about 15 trials the blind reading gave the number randomised for total_participants where the gold holds the number of the analysis set printed in the baseline table (for example text4-21, text4-27, text4-32, text5-9, text6-6). Both numbers are printed; these cells were left as they are. Values printed only for a pooled factorial margin (text5-3) and test statistics (t, F, chi-square) are not entered.

The gold standard holds 87 trials and 1,999 outcome rows.

Every change is logged in `gold_change_log.csv`. Scores reported in the paper were computed with the earlier gold standard and have to be recomputed with the current gold standard.

## Reproducibility note

Model outputs (`Results in JSON Format`, `Excel File of Results …`) are historical outputs of the submitted system and were **not** modified. Files under `Gold Standard/` changed as listed above; 21 processed TXT files gained their missing header/footer citation lines (txt_v2, see [`INPUT_TEXT_VERSION.md`](INPUT_TEXT_VERSION.md)).

## gold_v12 (2026-11-13): final review of every row and every filled cell

All 87 trials were checked again, one row at a time (254 arm rows, 1,999 outcome rows, no sampling). For each filled cell the reviewer had to find the value in the article for that arm, outcome and time point; scanned tables were read from page images. Each reported difference was then checked against the article before anything was changed. For the number of participants per arm, the review recorded for every arm whether the value is printed and which number it is (randomised, or the set shown in the baseline table).

182 cells changed in 26 trials; every change is in `gold_change_log.csv` (reason starts with "Final review").

- **Wrong value (2 cells, text5-6).** Placebo cardiovascular events and myocardial infarction held the number of episodes (6 and 2); the article also prints the number of patients (5 and 1), which is what the field holds.
- **Value not printed, emptied (53 cells).** Zero counts that were only implied by other groups' numbers or by a printed 0.0% (text4-2, text4-3, text4-40); "any extrapyramidal symptom" counts taken from narrative subsets (text4-40); female counts worked out as total minus male (text7-2); numbers analysed that the article does not print (text7-2 adherence rows, text7-9 all outcome rows, text6-12 arm rows, text4-46 death rows).
- **Printed but empty, filled (96 cells).** p values on the second arm of a comparison or printed in a table (text3-5, text4-9, text4-28, text4-30, text4-42, text4-49, text5-21); arm size and number analysed (text3-4, text4-2); median age (text5-4, text5-7, text5-15); follow-up in weeks (text6-7, text6-12); between-group mean change (text7-8).
- **Unadjusted result entered (text4-7).** The relapse hazard ratio was the multivariate one (0.37); the article names no main model, so the univariate one that goes with the arm counts is entered (0.41, 0.26 to 0.65).
- **Labels (27 cells).** "reported adjusted HR" changed to "reported HR (unadjusted Cox model)" where the article says the model is unadjusted (text6-8, text6-11); text6-2 late-reported deaths and text4-19 within-group p value labelled as what they are.

Number of participants per arm: every filled value is printed in the article. In 167 arm rows it is the number randomised; in the others it is the number in the baseline table or analysis set, mostly because the article prints no per-arm randomised number.

Result: 87 trials, 1,999 outcome rows.

## gold_v13 (2026-11-14): scope check of every outcome row against the configured outcome list

Every outcome row of gold_v12 (1,999 rows) was compared with the outcome list configured for its clinical area. Rows whose outcome is a different outcome from the ones on the list were put to the first author, who decided each group. Rule used: a row stays if it is an outcome on the list measured or worded differently (for example mean change instead of a rate, a sub-item, a synonym); it goes if it is a different outcome.

Removed, 80 rows in 19 psychiatry trials (each row is in `gold_change_log.csv`, reason starts with "Scope check"):

- antiparkinsonian / anticholinergic drug use, 58 rows (not on the list; only an indirect sign of extrapyramidal symptoms);
- BPRS and PER-C psychiatric rating items in text4-44, 18 rows (not an extrapyramidal-symptom measure);
- weight loss in text4-50, 4 rows (the configured outcome is substantial weight gain).

Kept after review: time to relapse and days in remission; mean change in weight, body-mass index, glucose and prolactin; suicidal ideation and self-injury; ischaemic heart disease and cardiovascular disease incidence; composite end points, diabetes-related death and sudden death; nephropathy, creatinine and albuminuria rows; intermittent claudication, retinal haemorrhages and worsening heart failure; the late-reported deaths in text6-2; timed up-and-go, two-minute walk, numeric pain rating, KOOS JR and time to reach a range of motion; discontinuation by reason, KOOS / WOMAC subscales and relapse subgroups.

Result: 87 trials, 1,919 outcome rows.

## gold_v14 (2026-11-14): re-check of every row and every cell, text fields and missing rows included

All 87 trials were gone through again, one paper at a time: every row of Study_Info, Design_Info and Atomic_Outcomes (254 arm rows, 1,919 outcome rows) was compared with the article, tables and figures were read from the page image wherever the text layer was scanned or garbled, and each point raised was checked against the article again before anything was changed. Two things were added to the earlier checks: the text fields (title, authors, journal, year, country) were compared with the first page, and each article was searched for configured outcomes that are printed with numbers but had no row.

No filled number was found to differ from the article. The 348 logged changes (42 trials; reason starts with "Final re-check" in `gold_change_log.csv`) are:

- filled, 114 cells: the value is printed but the cell was empty. Mostly the second arm row of a comparison lacking the group size, p value or test statistic that the first arm row carries (text4-3, text4-14, text4-49, text6-9, text6-10, text7-5 and others); median and interquartile range in text4-28; the 25% quantile of time to relapse in text4-34 and text4-45; discontinuation counts printed in the flow chart of text4-21; rehospitalisation mean, SD and between-group difference in text7-1; title, authors, journal or year in text4-3, text4-10, text4-41 and text6-2;
- rows added, 41: configured outcomes printed with numbers that had no row. Discontinuation by reason from the flow chart of text4-21 (23 rows) and death as a reason in text4-32 (2); any-reason discontinuation risk ratio in text4-11 (2); interim-analysis relapse in text4-45 (2); the haloperidol row of weight increase >5% in text4-8 (1); myocardial infarction risk reduction in text6-6 (1); leg revascularisation in text6-8 (2); renal failure in text6-11 (2); pain change to 6 weeks in text7-1 (2); pre-operative knee extension moment in text7-2 (4);
- restored, 37 cells that gold_v12 had emptied although the number is printed: the analysed number 15 per group in text7-9 (printed in Figure 1, which the text layer does not contain) and the zero dropouts of the soluble-tablet group in text4-40 (stated in words);
- labels, 73 cells: outcome names, units, time points and comparison labels made to match what the numbers are (for example text4-45 mean weight increase in kg, text7-4 values measured only after treatment, text7-2 differences in change from pre-op, text5-6 counts of patients);
- p values printed as 0.000, 32 cells in text7-6 and text7-9: the cell held the number 0 and now holds the printed form;
- follow-up in weeks, 32 cells: converted with the same factor as in the other trials (text5-16, text6-7, text7-6) and counted from the first measurement in text7-9;
- text fields corrected, 16 cells: misspelt or misread author names, a title and a journal abbreviation (text4-14, text4-15, text4-23, text4-32, text4-38, text4-40, text4-43, text4-47, text5-13, text6-8, text6-13);
- other, 3 cells: the same p value form on both arm rows (text3-2), the chi-squared of the 80 mg group (text4-1), the between-group p value on the post-intervention row (text7-9).

Not changed, by rule: outcomes for which the article prints only a percentage, a second analysis of an outcome that already has a row, results printed for pooled groups that are not arms of the file, and antiparkinsonian drug use (removed in gold_v13) were not added. In text6-13 the article gives the macrovascular hazard ratio as 0.61 (0.40-0.94) in the abstract, Figure 4 and the discussion and as 0.60 (0.40-0.92) in the results text; the gold standard keeps 0.61.

Result: 87 trials, 254 arm rows, 1,960 outcome rows.
