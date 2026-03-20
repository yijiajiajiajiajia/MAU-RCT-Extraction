

# Meta-Analysis Multi-Domain Dataset Repository

## Overview

This repository provides a comprehensive dataset designed to support prompt engineering and multi-domain validation for meta-analysis data extraction. It includes both:

* **Prompt Development Dataset** – curated to assist in the design, testing, and refinement of LLM-based extraction prompts.
* **Multi-Domain Validation Dataset** – spanning multiple clinical domains to ensure the robustness and generalizability of automated extraction systems.

The datasets are organized by clinical domain and contain both raw source materials and processed outputs to facilitate reproducible research and benchmarking.

## File Structure

```
├── Breast Cancer Meta-Dataset
│   ├── Excel File of Results Including Source
│   ├── Excel File of Results Without Source
│   ├── Gold Standard
│   ├── Original PDF and Processed TXT
│   └── Results in JSON Format
│
├── Cardiovascular Meta-Dataset
│   ├── Excel File of Results Including Source
│   ├── Excel File of Results Without Source
│   ├── Gold Standard
│   ├── Original PDF and Processed TXT
│   └── Results in JSON Format
│
├── Diabetes Meta-Dataset
│   ├── Excel File of Results Including Source
│   ├── Excel File of Results Without Source
│   ├── Gold Standard
│   ├── Original PDF and Processed TXT
│   └── Results in JSON Format
│
├── Large-Scale Psychiatry Meta-Dataset
│   ├── Excel File of Results Including Source
│   ├── Excel File of Results Without Source
│   ├── Gold Standard
│   ├── Original PDF and Processed TXT
│   └── Results in JSON Format
│
├── Minimal Atomic Unit Comparative Analysis Dataset
│   ├── Excel File of Results Including Source
│   ├── Excel File of Results Without Source
│   ├── Gold Standard
│   ├── Original PDF and Processed TXT
│   └── Results in JSON Format
│
└── Orthopedic Rehabilitation Meta-Dataset
    ├── Excel File of Results Including Source
    ├── Excel File of Results Without Source
    ├── Gold Standard
    ├── Original PDF and Processed TXT
    └── Results in JSON Format
```

**Notes:**

* **Gold Standard**: Curated dataset verified by dual experts to ensure high-quality, reliable extraction.
* **Original PDF and Processed TXT**: Raw source documents and their preprocessed text versions, ready for automated extraction pipelines.
* **Excel & JSON Results**: Structured outputs from the automated extraction system, with or without reference to the original sources.
* **API**: The `api_key` in the code belongs to the author and has been removed due to cost considerations. Readers who wish to reproduce the results need to provide their own API key.



