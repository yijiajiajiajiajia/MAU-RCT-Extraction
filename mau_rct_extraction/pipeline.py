import time
from pathlib import Path

from openai import OpenAI

from .config import load_config
from .exporters import export_results
from .minimal_units import extract_minimal_units_with_source
from .outcomes import extract_outcomes_for_unit_with_source
from .quality import check_timepoint_consistency
from .runtime import configure_runtime
from .study_info import extract_study_info_with_source
from .user_inputs import collect_meta_analysis_parameters


def run_extraction(config, meta_analysis_parameters):
    intervention_arm_definition = meta_analysis_parameters["intervention_arm_definition"]
    comparator_arm_definition = meta_analysis_parameters["comparator_arm_definition"]
    outcome_domain = meta_analysis_parameters["outcome_domain"]
    outcome_types = meta_analysis_parameters["outcome_types"]
    primary_timepoint = meta_analysis_parameters["primary_timepoint"]
    allowed_comparison_type = meta_analysis_parameters["allowed_comparison_type"]
    allowed_study_designs = meta_analysis_parameters["allowed_study_designs"]

    TXT_PATH = config.txt_path
    OUTPUT_JSON_PATH = config.output_json_path
    OUTPUT_EXCEL_PATH = config.output_excel_path
    OUTPUT_EXCEL_PATH_WITH_SOURCE = config.output_excel_path_with_source
    model_name = config.model_name

    # ----------------------------
    # 读取文本文件
    # ----------------------------
    print(f"\n正在读取文本文件: {TXT_PATH}")
    with open(TXT_PATH, 'r', encoding='utf-8') as f:
        article_text = f.read()

    study_id = Path(TXT_PATH).stem  # 文件名作为 study_id
    print(f"已读取文本内容，字符数: {len(article_text)}")

    # ----------------------------
    # 主流程
    # ----------------------------
    # 提取静态研究信息（检查研究设计）
    if allowed_study_designs:
        print(f"\n正在提取研究基本信息，检查是否符合 {allowed_study_designs} 设计...")
    else:
        print(f"\n正在提取研究基本信息（不限制研究设计）...")
    study_info, study_info_sources = extract_study_info_with_source(article_text, study_id, allowed_study_designs)

    # 检查研究是否符合纳入标准
    if study_info.get("meets_inclusion_criteria") is False:
        exclusion_reason = study_info.get("exclusion_reason", "研究设计不符合要求")
        print(f"警告: 本研究不符合纳入标准 - {exclusion_reason}")
        print("是否继续提取？(y/n)")
        continue_choice = input().strip().lower()
        if continue_choice != 'y':
            print("已停止提取。")
            exit()
    else:
        print("✓ 研究设计符合要求或未限制")

    # 提取最小原子单元
    print("正在提取最小原子单元...")
    minimal_units, minimal_units_sources = extract_minimal_units_with_source(
        article_text, study_id, intervention_arm_definition, comparator_arm_definition
    )

    # 检查是否成功提取到单元
    if not minimal_units:
        print("警告: 未找到任何试验组或对照组")
        print("是否继续提取？(y/n)")
        continue_choice = input().strip().lower()
        if continue_choice != 'y':
            print("已停止提取。")
            exit()

    print(f"找到 {len(minimal_units)} 个最小原子单元")

    # 为minimal_units添加trial_arm_id和is_shared_comparator字段（用于Atomic_Outcomes表）
    for i, unit in enumerate(minimal_units):
        # 为每个单元分配唯一的trial_arm_id
        unit['trial_arm_id'] = i + 1
        # 根据arm_type判断是否为共享对照
        if unit.get('arm_type', '').lower() in ['control', 'comparator', 'placebo']:
            unit['is_shared_comparator'] = True
        else:
            unit['is_shared_comparator'] = False

    # 给每个最小单元添加 outcomes
    print(f"\n正在为 {len(minimal_units)} 个单元提取结局指标...")
    print(f"提取参数:")
    print(f"  - 结局领域: {outcome_domain if outcome_domain else '所有领域'}")
    print(f"  - 结局指标类型: {', '.join(outcome_types) if outcome_types else '所有类型'}")
    print(f"  - 主要时间点: {primary_timepoint if primary_timepoint else '所有时间点'}")
    print(f"  - 允许的对比类型: {allowed_comparison_type if allowed_comparison_type else '所有对比类型'}")

    total_outcomes = 0
    all_outcomes_values = []
    all_outcomes_sources = []

    for i, unit in enumerate(minimal_units):
        print(f"  处理第 {i+1}/{len(minimal_units)} 个单元 ({unit.get('arm_name', '未知')})...")
        outcomes_values, outcomes_sources = extract_outcomes_for_unit_with_source(
            unit, article_text, outcome_domain, outcome_types, primary_timepoint, allowed_comparison_type
        )

        # 将outcomes添加到unit中
        unit['outcomes'] = outcomes_values

        # 保存outcomes的sources
        for j, outcome_values in enumerate(outcomes_values):
            outcome_sources = outcomes_sources[j] if j < len(outcomes_sources) else {}
            all_outcomes_values.append(outcome_values)
            all_outcomes_sources.append(outcome_sources)

        total_outcomes += len(outcomes_values)
        print(f"    找到 {len(outcomes_values)} 个符合要求的结局指标")
        # 添加短暂延迟避免频繁调用
        time.sleep(1)

    print(f"\n总计提取到 {total_outcomes} 个符合荟萃分析参数的结局指标")

    # 执行时间点一致性检查
    all_timepoints = check_timepoint_consistency(minimal_units, primary_timepoint)

    export_results(
        study_info=study_info,
        study_info_sources=study_info_sources,
        minimal_units=minimal_units,
        minimal_units_sources=minimal_units_sources,
        all_outcomes_values=all_outcomes_values,
        all_outcomes_sources=all_outcomes_sources,
        total_outcomes=total_outcomes,
        all_timepoints=all_timepoints,
        output_json_path=OUTPUT_JSON_PATH,
        output_excel_path=OUTPUT_EXCEL_PATH,
        output_excel_path_with_source=OUTPUT_EXCEL_PATH_WITH_SOURCE,
        model_name=model_name,
        meta_analysis_parameters=meta_analysis_parameters,
    )


def main():
    # ----------------------------
    # 配置
    # ----------------------------
    print("=== OpenAI GPT 模型配置 ===")

    config = load_config()

    # OpenAI GPT 配置
    api_key = config.api_key  # 替换为你的 OpenAI Key
    base_url = config.base_url  # OpenAI API 端点
    model_name = config.model_name
    print("已选择 OpenAI GPT 模型")

    # 创建客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,  # 增加超时时间
        max_retries=3   # 增加重试次数
    )
    configure_runtime(client, model_name)

    meta_analysis_parameters = collect_meta_analysis_parameters()
    run_extraction(config, meta_analysis_parameters)
