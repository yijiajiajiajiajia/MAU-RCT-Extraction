

# MAU-RCT-Extraction

This repository contains the Minimal Atomic Unit (MAU) extraction pipeline and the multi-domain datasets used for meta-analysis data extraction experiments.

The original single-file script has been reorganized into a small Python package. The extraction logic and prompt templates are preserved; the refactor only separates configuration, runtime setup, extraction functions, post-processing, and export code into clearer modules.

## Project Structure

```
├── MAU-MetaData.py                  # Backward-compatible script entry point
├── main.py                          # Package entry point
├── mau_rct_extraction/
│   ├── config.py                    # Environment-based runtime configuration
│   ├── user_inputs.py               # Interactive meta-analysis requirement prompts
│   ├── runtime.py                   # OpenAI client runtime and retry wrapper
│   ├── json_utils.py                # JSON repair and parsing helpers
│   ├── fields.py                    # Fixed Study/Design/Outcome field schemas
│   ├── study_info.py                # Level 1 study information extraction
│   ├── minimal_units.py             # Level 2 MAU/group extraction
│   ├── outcomes.py                  # Level 3 atomic outcome extraction
│   ├── normalization.py             # Time point, effect size, and outcome normalization
│   ├── quality.py                   # Consistency checks
│   └── exporters.py                 # JSON and Excel export
├── .env.example                     # Runtime configuration template
├── requirements.txt                 # Python dependencies
└── README.md
```

The dataset folders are organized by clinical domain. Each domain contains processed source TXT files, gold standards, model outputs with and without source evidence, and JSON results. Publisher article PDFs are intentionally not redistributed in this repository; users should retrieve the cited articles through their own lawful access.

## Setup

Create a Python environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

Fill in `OPENAI_API_KEY` and update the input/output paths as needed. Before running the script, load the variables into your shell:

```bash
set -a
source .env
set +a
```

## Usage

Run either entry point:

```bash
python MAU-MetaData.py
```

or:

```bash
python main.py
```

or:

```bash
python -m mau_rct_extraction
```

The script will ask for optional meta-analysis requirements, including intervention arm definition, comparator arm definition, outcome domain, outcome type, primary time point, comparison type, and study design. If a requirement is left blank, the pipeline extracts all relevant content for that category.

## Outputs

The pipeline produces:

* A JSON file with study information, MAUs, extraction parameters, and summary metadata.
* A standard Excel file with `Study_Characteristics`, `Group_Baseline`, and `Atomic_Outcomes` sheets.
* An Excel file with source sentences for each extracted field.

## Dataset Notes

* **Gold Standard**: Curated extraction targets used for evaluation. The current version is **gold_v3** (2026-11-09: bibliographic corrections plus a cell-by-cell re-verification of all arm and outcome values against the source PDFs, see [`gold_verification_2026-11-09/`](gold_verification_2026-11-09/)); see [`GOLD_STANDARD_VERSION.md`](GOLD_STANDARD_VERSION.md) and the cell-level [`gold_change_log.csv`](gold_change_log.csv). The version used for the submitted manuscript is preserved unchanged in commit `f62c788`.
* **Original PDF and Processed TXT**: Processed text files used by the extraction pipeline. The current version is **txt_v2** (2026-11-09): 21 files had their journal/year/DOI header lines restored from the source PDFs; see [`INPUT_TEXT_VERSION.md`](INPUT_TEXT_VERSION.md) and [`txt_change_log.csv`](txt_change_log.csv). The texts read by the submitted system are preserved in commits up to `9db15ad`. Despite the legacy folder name, publisher article PDFs are not distributed in this repository.
* **Excel & JSON Results**: Structured model outputs with or without source evidence.
* **API key**: No API key is committed. Users must provide their own key through environment variables.

## License

The extraction software in this repository is available under the [MIT License](LICENSE). This software license does not grant permission to redistribute third-party publications or other third-party material represented in the research datasets.
