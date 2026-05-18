import os
from dataclasses import dataclass


DEFAULT_TXT_PATH = r"D:\python_code\demo\texts\text2-3.txt"
DEFAULT_OUTPUT_JSON_PATH = r"D:\python_code\demo\texts\meta_analysis_results_text2-3.json"
DEFAULT_OUTPUT_EXCEL_PATH = r"D:\python_code\demo\texts\meta_analysis_results_text2-3.xlsx"
DEFAULT_OUTPUT_EXCEL_PATH_WITH_SOURCE = r"D:\python_code\demo\texts\meta_analysis_results_text2-3_with_source.xlsx"


@dataclass
class AppConfig:
    api_key: str
    base_url: str
    model_name: str
    txt_path: str
    output_json_path: str
    output_excel_path: str
    output_excel_path_with_source: str


def load_config():
    return AppConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model_name=os.getenv("OPENAI_MODEL", "gpt-4.1"),
        txt_path=os.getenv("TXT_PATH", DEFAULT_TXT_PATH),
        output_json_path=os.getenv("OUTPUT_JSON_PATH", DEFAULT_OUTPUT_JSON_PATH),
        output_excel_path=os.getenv("OUTPUT_EXCEL_PATH", DEFAULT_OUTPUT_EXCEL_PATH),
        output_excel_path_with_source=os.getenv(
            "OUTPUT_EXCEL_PATH_WITH_SOURCE",
            DEFAULT_OUTPUT_EXCEL_PATH_WITH_SOURCE,
        ),
    )
