import json
import os
import time

import pandas as pd

from .fields import ATOMIC_OUTCOMES_FIELDS, DESIGN_INFO_FIELDS, STUDY_INFO_FIELDS


def export_results(
    study_info,
    study_info_sources,
    minimal_units,
    minimal_units_sources,
    all_outcomes_values,
    all_outcomes_sources,
    total_outcomes,
    all_timepoints,
    output_json_path,
    output_excel_path,
    output_excel_path_with_source,
    model_name,
    meta_analysis_parameters,
):
    OUTPUT_JSON_PATH = output_json_path
    OUTPUT_EXCEL_PATH = output_excel_path
    OUTPUT_EXCEL_PATH_WITH_SOURCE = output_excel_path_with_source
    intervention_arm_definition = meta_analysis_parameters["intervention_arm_definition"]
    comparator_arm_definition = meta_analysis_parameters["comparator_arm_definition"]
    outcome_domain = meta_analysis_parameters["outcome_domain"]
    outcome_types = meta_analysis_parameters["outcome_types"]
    primary_timepoint = meta_analysis_parameters["primary_timepoint"]
    allowed_comparison_type = meta_analysis_parameters["allowed_comparison_type"]
    allowed_study_designs = meta_analysis_parameters["allowed_study_designs"]

    # ----------------------------
    # 保存 JSON
    # ----------------------------
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)

    # 创建完整的 JSON 结构（移除risk_of_bias相关字段）
    full_data = {
        "study_info": study_info,
        "minimal_units": minimal_units,
        "meta_analysis_parameters": {
            "intervention_arm_definition": intervention_arm_definition,
            "comparator_arm_definition": comparator_arm_definition,
            "outcome_domain": outcome_domain,
            "outcome_type": outcome_types if outcome_types else "all",  # 现在是一个列表或"all"
            "primary_timepoint": primary_timepoint,
            "allowed_comparison_type": allowed_comparison_type,
            "allowed_study_designs": allowed_study_designs
        },
        "model_used": model_name,
        "extraction_summary": {
            "total_units": len(minimal_units),
            "total_outcomes": total_outcomes,
            "timepoints_found": list(all_timepoints),
            "primary_timepoint_count": sum(1 for unit in minimal_units for outcome in unit.get('outcomes', []) 
                                           if outcome.get('time_point') and primary_timepoint and primary_timepoint.lower() in outcome.get('time_point', '').lower()) if primary_timepoint else 0,
            "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    print(f"\n已保存JSON文件: {OUTPUT_JSON_PATH}")

    # ----------------------------
    # 转 Excel（三张表，移除Risk_of_Bias表和Meta_Parameters表）- 标准版本
    # ----------------------------
    # 1. 静态研究信息 - 确保18个固定字段都输出
    df_study_info = pd.DataFrame([study_info])

    # 确保所有18个字段都存在
    for field in STUDY_INFO_FIELDS:
        if field not in df_study_info.columns:
            df_study_info[field] = None

    # 按固定顺序排列列
    df_study_info = df_study_info[STUDY_INFO_FIELDS]

    # 重命名列：按照要求修改列名
    df_study_info = df_study_info.rename(columns={
        'study_design': 'Study_Design_Description',
        'study_setting': 'Study_Setting_Description',
        'source_of_recruitment': 'Recruitment_Source_Description',
        'meets_inclusion_criteria': 'Eligible_for_Meta_Analysis'
    })

    # 2. 最小单元信息 - 确保17个固定字段都输出（已修改）
    design_data = []
    for unit in minimal_units:
        temp = unit.copy()
        temp.pop('outcomes', None)
        temp.pop('trial_arm_id', None)  # 移除trial_arm_id，不在Design_Info表中显示
        temp.pop('is_shared_comparator', None)  # 移除is_shared_comparator，不在Design_Info表中显示
        design_data.append(temp)
    df_design = pd.DataFrame(design_data)

    # 确保所有17个字段都存在
    for field in DESIGN_INFO_FIELDS:
        if field not in df_design.columns:
            df_design[field] = None

    # 按固定顺序排列列
    df_design = df_design[DESIGN_INFO_FIELDS]

    # 重命名 Group_Baseline 表的列（按要求）
    df_design = df_design.rename(columns={
        'arm_name': 'Study_Arm_Label',
        'arm_type': 'arm_role',
        'total_participants': 'arm_participant_count',
        'gender_male_count': 'arm_male_count',
        'gender_female_count': 'arm_female_count',
        'age_sd': 'arm_age_sd',
        'intervention_details': 'arm_intervention_details',
        'intervention_duration': 'arm_intervention_duration',
        'intervention_frequency': 'arm_intervention_frequency',
        'control_details': 'arm_control_details',
        'number_of_participants_analyzed': 'arm_participants_analyzed'
    })

    # 3. 原子化 outcomes - 确保32个固定字段都输出（增加了mean_ci_lower和mean_ci_upper）
    outcomes_data = []
    for unit in minimal_units:
        for outcome in unit.get('outcomes', []):
            row = outcome.copy()
            row['study_id'] = unit['study_id']
            row['arm_name'] = unit.get('arm_name', '未知')
            row['trial_arm_id'] = unit.get('trial_arm_id', None)
            row['is_shared_comparator'] = unit.get('is_shared_comparator', False)
            outcomes_data.append(row)

    # 创建DataFrame并确保所有32个字段都存在
    df_outcomes = pd.DataFrame(outcomes_data)

    # 确保所有32个字段都存在
    for field in ATOMIC_OUTCOMES_FIELDS:
        if field not in df_outcomes.columns:
            df_outcomes[field] = None

    # 按固定顺序排列列
    df_outcomes = df_outcomes[ATOMIC_OUTCOMES_FIELDS]

    # 重命名 Atomic_Outcomes 表的指定列
    df_outcomes = df_outcomes.rename(columns={
        'domain_match': 'outcome_domain_match',
        'participants_analyzed': 'arm_this_time_point_participants_analyzed'
    })

    # 保存到 Excel - 标准版本（删除Meta_Parameters表）
    try:
        with pd.ExcelWriter(OUTPUT_EXCEL_PATH, engine='openpyxl') as writer:
            df_study_info.to_excel(writer, sheet_name="Study_Characteristics", index=False)
            df_design.to_excel(writer, sheet_name="Group_Baseline", index=False)
            df_outcomes.to_excel(writer, sheet_name="Atomic_Outcomes", index=False)
            # 不再写入 Meta_Parameters 表
    
        print(f"\n已保存标准Excel文件: {OUTPUT_EXCEL_PATH}")
    
    except Exception as e:
        print(f"保存标准Excel文件时出错: {e}")
        import traceback
        traceback.print_exc()

    # ----------------------------
    # 转 Excel（三张表，包含原文原句）- 带原文版本
    # ----------------------------
    # 1. 静态研究信息 - 带原文原句
    study_info_with_source_data = []
    study_info_row = {}
    for field in STUDY_INFO_FIELDS:
        # 添加值列
        study_info_row[field] = study_info.get(field)
        # 添加原文原句列
        study_info_row[f"{field}_source"] = study_info_sources.get(field)
    study_info_with_source_data.append(study_info_row)

    df_study_info_with_source = pd.DataFrame(study_info_with_source_data)

    # 重命名 Study_Characteristics_with_Source 表的列（值和_source列）
    rename_dict = {
        'study_design': 'Study_Design_Description',
        'study_design_source': 'Study_Design_Description_source',
        'study_setting': 'Study_Setting_Description',
        'study_setting_source': 'Study_Setting_Description_source',
        'source_of_recruitment': 'Recruitment_Source_Description',
        'source_of_recruitment_source': 'Recruitment_Source_Description_source',
        'meets_inclusion_criteria': 'Eligible_for_Meta_Analysis',
        'meets_inclusion_criteria_source': 'Eligible_for_Meta_Analysis_source'
    }
    # 只重命名存在的列
    existing_rename = {old: new for old, new in rename_dict.items() if old in df_study_info_with_source.columns}
    df_study_info_with_source = df_study_info_with_source.rename(columns=existing_rename)

    # 2. 最小单元信息 - 带原文原句
    design_with_source_data = []
    for i, unit in enumerate(minimal_units):
        design_row = {}
        unit_sources = minimal_units_sources[i] if i < len(minimal_units_sources) else {}
    
        for field in DESIGN_INFO_FIELDS:
            # 添加值列
            design_row[field] = unit.get(field)
            # 添加原文原句列
            design_row[f"{field}_source"] = unit_sources.get(field)
    
        design_with_source_data.append(design_row)

    df_design_with_source = pd.DataFrame(design_with_source_data)

    # 重命名 Group_Baseline_with_Source 表的列（值和_source列）
    design_rename_dict = {
        'arm_name': 'Study_Arm_Label',
        'arm_name_source': 'Study_Arm_Label_source',
        'arm_type': 'arm_role',
        'arm_type_source': 'arm_role_source',
        'total_participants': 'arm_participant_count',
        'total_participants_source': 'arm_participant_count_source',
        'gender_male_count': 'arm_male_count',
        'gender_male_count_source': 'arm_male_count_source',
        'gender_female_count': 'arm_female_count',
        'gender_female_count_source': 'arm_female_count_source',
        'age_sd': 'arm_age_sd',
        'age_sd_source': 'arm_age_sd_source',
        'intervention_details': 'arm_intervention_details',
        'intervention_details_source': 'arm_intervention_details_source',
        'intervention_duration': 'arm_intervention_duration',
        'intervention_duration_source': 'arm_intervention_duration_source',
        'intervention_frequency': 'arm_intervention_frequency',
        'intervention_frequency_source': 'arm_intervention_frequency_source',
        'control_details': 'arm_control_details',
        'control_details_source': 'arm_control_details_source',
        'number_of_participants_analyzed': 'arm_participants_analyzed',
        'number_of_participants_analyzed_source': 'arm_participants_analyzed_source'
    }
    # 只重命名存在的列
    existing_design_rename = {old: new for old, new in design_rename_dict.items() if old in df_design_with_source.columns}
    df_design_with_source = df_design_with_source.rename(columns=existing_design_rename)

    # 3. 原子化 outcomes - 带原文原句
    outcomes_with_source_data = []
    for i, outcome_values in enumerate(all_outcomes_values):
        outcome_sources = all_outcomes_sources[i] if i < len(all_outcomes_sources) else {}
        outcome_row = {}
    
        for field in ATOMIC_OUTCOMES_FIELDS:
            # 添加值列
            outcome_row[field] = outcome_values.get(field)
            # 添加原文原句列
            outcome_row[f"{field}_source"] = outcome_sources.get(field)
    
        outcomes_with_source_data.append(outcome_row)

    df_outcomes_with_source = pd.DataFrame(outcomes_with_source_data)

    # 重命名 Atomic_Outcomes_with_Source 表的列（值和_source列）
    outcomes_rename_dict = {
        'domain_match': 'outcome_domain_match',
        'domain_match_source': 'outcome_domain_match_source',
        'participants_analyzed': 'arm_this_time_point_participants_analyzed',
        'participants_analyzed_source': 'arm_this_time_point_participants_analyzed_source'
    }
    # 只重命名存在的列
    existing_outcomes_rename = {old: new for old, new in outcomes_rename_dict.items() if old in df_outcomes_with_source.columns}
    df_outcomes_with_source = df_outcomes_with_source.rename(columns=existing_outcomes_rename)

    # 保存到 Excel - 带原文版本（删除Meta_Parameters表）
    try:
        with pd.ExcelWriter(OUTPUT_EXCEL_PATH_WITH_SOURCE, engine='openpyxl') as writer:
            df_study_info_with_source.to_excel(writer, sheet_name="Study_Characteristics_with_Source", index=False)
            df_design_with_source.to_excel(writer, sheet_name="Group_Baseline_with_Source", index=False)
            df_outcomes_with_source.to_excel(writer, sheet_name="Atomic_Outcomes_with_Source", index=False)
            # 不再写入 Meta_Parameters 表
    
        print(f"已保存带原文原句的Excel文件: {OUTPUT_EXCEL_PATH_WITH_SOURCE}")
    
        print(f"\n=== 荟萃分析数据提取完成 ===")
        print(f"  - 使用的模型: {model_name}")
        print(f"  - 研究设计检查: {'通过' if study_info.get('meets_inclusion_criteria') else '未通过'}")
        print(f"  - 最小单元数: {len(minimal_units)} 个")
        print(f"  - 结局指标数: {total_outcomes} 个")
        print(f"  - 主要时间点匹配: {primary_timepoint if primary_timepoint else '不限制'}")
        print(f"  - 对比类型限制: {allowed_comparison_type if allowed_comparison_type else '不限制'}")
        print(f"  - 结局领域: {outcome_domain if outcome_domain else '所有领域'}")
        print(f"  - 结局类型: {', '.join(outcome_types) if outcome_types else '所有类型'}")
        print(f"\n  - JSON文件: {OUTPUT_JSON_PATH}")
        print(f"  - 标准Excel文件: {OUTPUT_EXCEL_PATH}")
        print(f"  - 带原文原句Excel文件: {OUTPUT_EXCEL_PATH_WITH_SOURCE}")
    
        # 显示表格列数统计
        print(f"\n=== 表格列数统计 ===")
        print(f"  - Study_Characteristics: {len(df_study_info.columns)} 列 (固定: 18)")
        print(f"  - Group_Baseline: {len(df_design.columns)} 列 (固定: 17)")
        print(f"  - Atomic_Outcomes: {len(df_outcomes.columns)} 列 (固定: 32 - 增加了mean_ci_lower和mean_ci_upper)")
    
        print(f"\n=== 带原文原句表格列数统计 ===")
        print(f"  - Study_Characteristics_with_Source: {len(df_study_info_with_source.columns)} 列 (每个字段都有对应的_source列)")
        print(f"  - Group_Baseline_with_Source: {len(df_design_with_source.columns)} 列 (每个字段都有对应的_source列)")
        print(f"  - Atomic_Outcomes_with_Source: {len(df_outcomes_with_source.columns)} 列 (每个字段都有对应的_source列)")
    
        # 显示提取统计
        if not df_outcomes.empty:
            print(f"\n=== 提取统计 ===")
        
            # 按结局指标类型统计
            if 'outcome_type' in df_outcomes.columns:
                type_counts = df_outcomes['outcome_type'].value_counts()
                print(f"结局指标类型分布:")
                for outcome_type, count in type_counts.items():
                    if outcome_type:
                        print(f"  - {outcome_type}: {count} 个")
        
            # 按效应量类型统计
            if 'effect_size_type' in df_outcomes.columns:
                es_type_counts = df_outcomes['effect_size_type'].value_counts()
                print(f"\n效应量类型分布:")
                for es_type, count in es_type_counts.items():
                    if es_type:
                        print(f"  - {es_type}: {count} 个")
        
            # 按时间点角色统计
            if 'time_point_role' in df_outcomes.columns:
                role_counts = df_outcomes['time_point_role'].value_counts()
                print(f"\n时间点角色分布:")
                for role, count in role_counts.items():
                    if role:
                        print(f"  - {role}: {count} 个")
        
            # 按结局角色统计
            if 'outcome_role' in df_outcomes.columns:
                outcome_role_counts = df_outcomes['outcome_role'].value_counts()
                print(f"\n结局指标角色分布:")
                for role, count in outcome_role_counts.items():
                    if role:
                        print(f"  - {role}: {count} 个")
        
            # 显示提取的指标名称
            if 'outcome_name' in df_outcomes.columns:
                outcome_names = df_outcomes['outcome_name'].dropna().unique()
                print(f"\n提取的结局指标 (共 {len(outcome_names)} 种):")
                for name in outcome_names[:15]:  # 显示前15个
                    print(f"  - {name}")
                if len(outcome_names) > 15:
                    print(f"  ... 还有 {len(outcome_names) - 15} 种指标")
        
            # 显示置信区间字段填充情况
            print(f"\n=== 置信区间字段填充情况 ===")
            if 'mean_ci_lower' in df_outcomes.columns:
                mean_ci_count = df_outcomes['mean_ci_lower'].notna().sum()
                print(f"均值的置信区间下限 (mean_ci_lower): {mean_ci_count}/{len(df_outcomes)} 个")
        
            if 'mean_ci_upper' in df_outcomes.columns:
                mean_ci_count = df_outcomes['mean_ci_upper'].notna().sum()
                print(f"均值的置信区间上限 (mean_ci_upper): {mean_ci_count}/{len(df_outcomes)} 个")
        
            if 'ci_lower' in df_outcomes.columns:
                effect_ci_count = df_outcomes['ci_lower'].notna().sum()
                print(f"效应量的置信区间下限 (ci_lower): {effect_ci_count}/{len(df_outcomes)} 个")
        
            if 'ci_upper' in df_outcomes.columns:
                effect_ci_count = df_outcomes['ci_upper'].notna().sum()
                print(f"效应量的置信区间上限 (ci_upper): {effect_ci_count}/{len(df_outcomes)} 个")
    
    except Exception as e:
        print(f"保存带原文原句Excel文件时出错: {e}")
        import traceback
        traceback.print_exc()
