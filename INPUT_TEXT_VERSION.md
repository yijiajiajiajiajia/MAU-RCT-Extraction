# Input text (processed TXT) version note

**Current version: txt_v2 (2026-11-09).** The processed TXT files in the commits up to `9db15ad` are the texts the submitted system actually read. A review found that in 21 of the 93 files (two of them also missing their title and author lines) the journal/year/DOI lines printed in the source PDF's header, footer or margin were missing from the TXT; they are restored here. Use txt_v2 for re-runs and new experiments. The earlier version is kept unchanged in git history for traceability.

## What changed

Every change is listed in [`txt_change_log.csv`](txt_change_log.csv) (study, file, inserted lines, where they sit in the PDF, note). Rules:

- Lines were copied verbatim from the PDF text layer (`pdftotext`). Nothing else in the files was edited; `git diff --numstat` shows only added lines.
- A line was inserted only if it was absent from the TXT. Where a citation was line-wrapped in the PDF margin the wrapped pieces were joined (text5-3, text6-11); where a citation shared a line with body text only the citation part was taken (text5-2, text4-32).
- Lines go right after the `### Text Content …` marker, or at the top when the file has no marker, so they sit where the page-1 header sits in the article.
- OCR'd scans were inserted as the text layer reads (text4-15 `-Acts psychiat. scand. (1973)…`, text4-31 `Volume IX` / `1968`); the OCR was not corrected.
- Four reports have no journal/year/DOI line anywhere in the PDF text layer and were left unchanged: text3-1 (accepted-manuscript PDF), text4-25 (scan), text6-2, text7-2. Three more (text3-5, text5-4, text5-20) already contained every line the PDF has.
- The three `text2-*` files in the comparative-analysis dataset were not checked: their PDFs are not in the local source folder.

## Gold standard follow-up

Twelve `Study_Info` cells (year / DOI / journal) in seven gold files were empty although the TXT now states the value (text3-3, text4-3, text4-19, text4-32, text4-54, text5-17, text5-20). They were filled and logged in [`gold_change_log.csv`](gold_change_log.csv); see [`GOLD_STANDARD_VERSION.md`](GOLD_STANDARD_VERSION.md).

## Second pass: title and author lines (same day)

text4-9 and text4-13 started at the Introduction / Abstract: the page-1 title, author and affiliation lines were also missing. They were restored from the PDF text layer with the same rules (verbatim; for text4-9, an OCR'd scan, runs of spaces inside a line were collapsed; for text4-13 two stray superscript digits that the text layer puts on lines of their own were not inserted). Logged in `txt_change_log.csv`.
