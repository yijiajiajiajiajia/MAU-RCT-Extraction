# ----------------------------
# Study_Info表格的18个固定字段
# ----------------------------
STUDY_INFO_FIELDS = [
    "study_id", "title", "authors", "year", "journal", "country", "doi",
    "study_design", "inclusion_criteria", "exclusion_criteria", 
    "study_setting", "source_of_recruitment", 
    "number_of_participants_randomized", "number_of_participants_analyzed",
    "dropout_reasons", "meets_inclusion_criteria", "exclusion_reason"
]

# ----------------------------
# Design_Info表格的17个固定字段（已修改）
# ----------------------------
DESIGN_INFO_FIELDS = [
    "study_id", "arm_name", "arm_type", "timepoint", "subgroup", 
    "total_participants", "gender_male_count", "gender_female_count",
    "mean_age", "age_sd", "intervention_details", "intervention_duration", 
    "intervention_frequency", "control_details", "adherence_to_control", 
    "adherence_to_intervention", "number_of_participants_analyzed"
]

# ----------------------------
# Atomic_Outcomes表格的32个固定字段（增加了mean_ci_lower和mean_ci_upper）
# ----------------------------
ATOMIC_OUTCOMES_FIELDS = [
    # 研究标识 (4个)
    "study_id", "arm_name", "trial_arm_id", "is_shared_comparator",
    
    # 结局基本信息 (5个)
    "outcome_name", "scale_name", "outcome_type", "outcome_unit", "domain_match",
    
    # 时间点信息 (1个)
    "time_point",
    
    # 对比属性 (2个)
    "comparison_type", "comparison_targets",
    
    # 描述性统计 (11个) - 增加了mean_ci_lower和mean_ci_upper
    "mean", "sd", "median", "iqr",
    "event_count", "total_count", "participants_analyzed",
    "mean_ci_lower", "mean_ci_upper",  # 新增：均值的置信区间
    
    # 效应量信息 (6个)
    "effect_size_type", "effect_size_definition", "effect_size_value", 
    "ci_lower", "ci_upper", "p_value",
    
    # 其他属性 (7个)
    "outcome_role", "time_point_role", "followup_weeks", "higher_is_better"
]
