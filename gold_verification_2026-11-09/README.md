# Gold standard re-verification (2026-11-09)

Every value in the 88 included gold-standard files (Design_Info and Atomic_Outcomes, plus the participant counts in Study_Info) was compared cell by cell with the source PDF. text5-17 and text5-20 are the two excluded studies and have no arm/outcome rows.

- `per_paper_summary.csv` — per paper: cells checked, and how many were ok / wrong / derived (computable from the PDF, e.g. counts from percentages, weeks from months) / format (rounding, label or sign convention) / unverifiable (not findable in the PDF) / ambiguous / omission (reported outcome with no gold row).
- Every `wrong` cell that has a printed value in the PDF was corrected in the gold files; each correction is a row in `../gold_change_log.csv` (reason opens with "Full re-verification … found this problem; corrected." and quotes the PDF).
- Nine files had whole blocks of columns shifted by one header (text4-23, text4-51, text5-4, text5-13, text5-14, text5-18, text5-21, text7-8 in Atomic_Outcomes; text4-21, text4-23 in Study_Info). The values were moved back under their headers; one log row per sheet row.
- `open_items.csv` — open items: 16 wrong cells whose correct value is not printed in the PDF; these were emptied on 2026-11-10 (rule: a value that is not printed in the article is not filled in) and are logged in `gold_change_log.csv` (text4-5 effect sizes that are t/F statistics, text4-30 per-arm relapse counts, text7-4 pooled n, text4-2 row 29, text4-28 row 27), plus all omission / ambiguous / unverifiable findings, for the authors to decide.
- Scanned PDFs (text4-8, text4-23, text4-46, text4-50, text4-25) were read from page images; their evidence strings are transcriptions.

## 2026-11-10 follow-up

Rule confirmed by the authors and stated in the paper: only values that can be located directly in the article are kept in the gold standard; a value that is not printed is left empty; unit conversions (months to weeks) are kept. Applied to the findings above: the 16 wrong cells without a printed value, 17 values calculated during the re-verification, and 258 cells marked `derived` or `unverifiable` were emptied. Kept: `followup_weeks`, sex counts in single-sex trials, zero counts stated in words, unit labels. Every cell is logged in `gold_change_log.csv`.
