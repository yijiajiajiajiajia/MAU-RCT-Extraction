import json

from .fields import ATOMIC_OUTCOMES_FIELDS
from .json_utils import safe_json_parse
from .normalization import (
    determine_effect_size_definition,
    determine_effect_size_type,
    determine_higher_is_better,
    determine_time_point_role,
    extract_followup_weeks,
    normalize_outcome_names,
    standardize_time_point,
)
from .runtime import call_api_with_retry


# ----------------------------
# API 提取每个最小单元的结局指标（根据荟萃分析参数）- 改进版
# ----------------------------
def extract_outcomes_for_unit_with_source(unit, text, outcome_domain, outcome_types, 
                                        primary_timepoint, allowed_comparison_type):
    """提取结局指标，同时提取原文原句 - 改进版"""
    # 获取arm_name和arm_type
    arm_name = unit.get('arm_name', '未知')
    arm_type = unit.get('arm_type', '')
    
    # 根据参数是否有限制来调整提示词
    domain_text = f"**结局领域: {outcome_domain}**" if outcome_domain else "**不限制结局领域，提取所有领域的结局指标**"
    type_text = f"**结局指标类型: {', '.join(outcome_types) if outcome_types else '所有类型'}**" if outcome_types else "**不限制结局指标类型，提取所有类型的结局指标**"
    timepoint_text = f"**主要时间点: {primary_timepoint}**" if primary_timepoint else "**不限制时间点，提取所有时间点的结局指标**"
    comparison_text = f"**允许的对比类型: {allowed_comparison_type}**" if allowed_comparison_type else "**不限制对比类型，提取所有类型的对比**"
    
    prompt = f"""
    你是医学数据抽取助手。下面是一个最小原子单元：
    {json.dumps({k: v for k, v in unit.items() if k not in ['trial_arm_id', 'is_shared_comparator']}, ensure_ascii=False, indent=2)}
    
    **当前处理的组别：{arm_name} ({arm_type})**
    
    **重要警告：**
    1. **严禁将实验组数据误套用到对照组**：如果原文没有提供该组（{arm_name}）的数据，相关字段必须留空
    2. **严格区分两种置信区间**：
       - 均值的置信区间（描述性统计）：存储为 mean_ci_lower 和 mean_ci_upper
       - 效应量的置信区间（推断性统计）：存储为 ci_lower 和 ci_upper
    3. **数值与组别严格匹配**：确保提取的数值与该组（{arm_name}）完全对应
    
    **荟萃分析参数要求：**
    1. {domain_text}
    2. {type_text}
    3. {timepoint_text}
    4. {comparison_text}
    
    请根据文章文本，提取该单元对应的结局指标(outcomes)。
    
    **提取规则：**
    {f"1. **领域匹配**：只提取与'{outcome_domain}'相关的结局指标" if outcome_domain else "1. **领域不限制**：提取所有领域的结局指标"}
    {f"2. **类型匹配**：只提取以下类型的结局指标: {', '.join(outcome_types)}" if outcome_types else "2. **类型不限制**：提取所有类型的结局指标"}
    {f"3. **时间点优先**：优先提取'{primary_timepoint}'时间点的数据，如果没有则提取最接近的时间点" if primary_timepoint else "3. **时间点不限制**：提取所有时间点的数据"}
    {f"4. **对比类型限制**：只提取'{allowed_comparison_type}'类型的对比" if allowed_comparison_type else "4. **对比类型不限制**：提取所有类型的对比"}
    5. **结局角色判断**：根据文章描述判断结局指标的角色（主要/次要/探索性）
    
    **重要规则：**
    1. **统计值与对比属性必须一一对应**
    2. **数值与时间点必须正确匹配** - 确保每个时间点的指标数值正确对应，避免时间维度错配
    3. **效应量类型识别**：根据统计值判断效应量类型
    4. **数据完整性原则**：如果原文没有提供该组的数据，相关字段必须留空，而不是使用其他组的数据
    
    **每个 outcome 必须包含以下字段（32个固定字段），每个字段都是一个对象，包含：**
    1. "value": 字段的值
    2. "source": 原文中原句（直接从原文中引用，不要修改）
    
    **核心描述字段：**
    1. "outcome_name": 结局指标名称
    2. "outcome_unit": 结局指标单位
    3. "outcome_type": 结局指标类型 ({', '.join(outcome_types) if outcome_types else '可以是continuous/dichotomous/ordinal/time_to_event'})
    4. "outcome_role": 结局指标角色 (primary/secondary/exploratory) - 根据文章描述判断
    5. "scale_name": 说明该结局指标使用的量表名称
    6. "time_point": 说明结局指标测量的时间点{f"（优先提取'{primary_timepoint}'）" if primary_timepoint else ""}
    7. "time_point_role": 时间点角色 (baseline/post/followup) - 根据时间点描述判断
    8. "followup_weeks": 随访周数（如果有） - 从时间点描述中提取
    9. "higher_is_better": 高分是否更好 (true/false) - 根据指标性质判断
    10. "domain_match": 说明该指标如何匹配"{outcome_domain if outcome_domain else '相应'}领域"
    
    **描述性统计字段（描述单个组的特征）- 必须与该组（{arm_name}）严格对应：**
    11. "mean": 均值 (连续变量) - **必须与time_point对应，且必须是{arm_name}组的数据**
    12. "sd": 标准差 (连续变量) - **必须与time_point对应，且必须是{arm_name}组的数据**
    13. "median": 中位数 (非正态分布连续变量) - **必须与time_point对应，且必须是{arm_name}组的数据**
    14. "iqr": 四分位距 (非正态分布连续变量) - **必须与time_point对应，且必须是{arm_name}组的数据**
    15. "event_count": 事件发生数 (二分类变量) - **必须与time_point对应，且必须是{arm_name}组的数据**
    16. "total_count": 总人数 (二分类变量) - **必须与time_point对应，且必须是{arm_name}组的数据**
    17. "participants_analyzed": 分析人数 - **必须与time_point对应，且必须是{arm_name}组的数据**
    18. "mean_ci_lower": **均值的置信区间下限** - 描述性统计，必须是{arm_name}组均值的置信区间
    19. "mean_ci_upper": **均值的置信区间上限** - 描述性统计，必须是{arm_name}组均值的置信区间
    
    **对比属性字段（必须唯一确定每个统计值的背景）：**
    20. "comparison_type": 明确统计对比的类型{f"（应该为'{allowed_comparison_type}'或类似表述）" if allowed_comparison_type else ""}
    21. "comparison_targets": 明确具体对比的对象
    
    **效应量相关字段（推断性统计）- 必须与对比属性严格对应：**
    22. "effect_size_type": 效应量类型 (MD/SMD/HEDGES_G/RR/OR/HR) - 根据统计值判断
    23. "effect_size_definition": 效应量定义 (between-group post-intervention difference/between-group change score difference/reported adjusted HR)
    
    **统计结果字段（必须与对比属性一一对应，且是推断性统计）：**
    24. "p_value": 对比的显著性结果（数值），如: 0.80, <0.01, 0.026
    25. "effect_size_value": 对比的效应量/统计量结果（数值），如: 5.82（F值）, 0.58（SMD）, 2.45（OR）
    26. "ci_lower": **效应量的置信区间下限** - 推断性统计，必须是效应量的置信区间
    27. "ci_upper": **效应量的置信区间上限** - 推断性统计，必须是效应量的置信区间
    
    **关键规则：**
    1. **数据来源严格匹配**：
       - 如果原文没有提供{arm_name}组的描述性统计数据（如mean, sd），这些字段必须留空
       - 严禁将其他组的数据误填到{arm_name}组
       
    2. **置信区间严格区分**：
       - 均值的置信区间（描述性统计）：mean_ci_lower 和 mean_ci_upper
       - 效应量的置信区间（推断性统计）：ci_lower 和 ci_upper
       - 两者不能混淆，必须严格区分
       
    3. **一一对应规则**: 
       - 先确定「对比属性」（comparison_type + comparison_targets），再找原文中"这个对比"对应的p_value/effect_size_value
       - 一个「对比属性组合」只能对应一组p_value/effect_size_value/ci_lower/ci_upper
       - 一个p_value/effect_size_value只能归属到一个「对比属性组合」
    
    4. **参数匹配规则**:
       {f"- 严格按指定的类型提取: {', '.join(outcome_types)}" if outcome_types else "- 不限制类型，提取所有类型"}
       {f"- 优先提取'{primary_timepoint}'时间点" if primary_timepoint else "- 不限制时间点，提取所有时间点"}
       {f"- 只提取'{allowed_comparison_type}'对比类型" if allowed_comparison_type else "- 不限制对比类型，提取所有对比类型"}
    
    5. **效应量类型判断规则**:
       - 连续变量: MD（均数差）或 SMD（标准化均数差）
       - 二分类变量: RR（相对危险度）或 OR（比值比）
       - 生存分析: HR（风险比）
       - 注意识别Hedges' g校正的SMD
    
    **JSON格式要求：**
    1. 必须返回完全符合JSON语法的数组
    2. 所有字符串必须用双引号
    3. 不能有尾随逗号
    4. 不能有注释
    5. 确保JSON结构完整闭合
    
    **重要要求：**
    1. 对于每个字段，必须提供原文依据（source）
    2. source字段必须是原文中的原句，不要修改
    3. 如果找不到原文依据，source设为null
    4. **特别注意：如果原文没有提供{arm_name}组的数据，相关字段必须留空，而不是使用其他组的数据**
    
    文章文本: {text}  # 限制文本长度
    
    返回 JSON 列表，只包含符合上述参数的结局指标。
    如果没有符合的指标，返回空列表 []。
    
    请根据文本中的统计信息，严格遵守提取规则，特别是数据来源匹配和置信区间区分。
    返回标准 JSON 列表。
    
    Output valid JSON only.
    Do not use LaTeX, Markdown, or backslash escape sequences (e.g., \(, \_).
    Use plain text such as vitamin D3.
    """
    
    try:
        response = call_api_with_retry([{"role": "user", "content": prompt}])
        
        if response:
            result_text = response.choices[0].message.content
            # 使用安全的JSON解析
            outcomes_with_source = safe_json_parse(result_text, [])
            
            if not isinstance(outcomes_with_source, list):
                print(f"警告: 返回的不是列表，而是 {type(outcomes_with_source)}，尝试转换为列表")
                outcomes_with_source = [outcomes_with_source] if outcomes_with_source else []
        else:
            outcomes_with_source = []
            
    except Exception as e:
        print(f"提取结局指标时出错: {e}")
        outcomes_with_source = []
    
    # 对提取的结局指标进行后处理和标准化
    processed_outcomes_values = []
    processed_outcomes_sources = []
    
    for outcome_with_source in outcomes_with_source:
        # 分离值和原文
        outcome_values = {}
        outcome_sources = {}
        
        for field in ATOMIC_OUTCOMES_FIELDS:
            if field in ['study_id', 'arm_name', 'trial_arm_id', 'is_shared_comparator']:
                # 这些字段从单元中获取
                if field == 'study_id':
                    outcome_values[field] = unit.get('study_id')
                    outcome_sources[field] = None
                elif field == 'arm_name':
                    outcome_values[field] = unit.get('arm_name')
                    outcome_sources[field] = None
                elif field == 'trial_arm_id':
                    outcome_values[field] = unit.get('trial_arm_id')
                    outcome_sources[field] = None
                elif field == 'is_shared_comparator':
                    outcome_values[field] = unit.get('is_shared_comparator')
                    outcome_sources[field] = None
            else:
                if field in outcome_with_source:
                    field_data = outcome_with_source[field]
                    if isinstance(field_data, dict):
                        outcome_values[field] = field_data.get("value")
                        outcome_sources[field] = field_data.get("source")
                    else:
                        outcome_values[field] = field_data
                        outcome_sources[field] = None
                else:
                    outcome_values[field] = None
                    outcome_sources[field] = None
        
        # 1. 时间点标准化
        if 'time_point' in outcome_values and outcome_values['time_point']:
            outcome_values['time_point'] = standardize_time_point(outcome_values['time_point'], primary_timepoint)
        
        # 2. 判断时间点角色
        if 'time_point' in outcome_values and 'time_point_role' not in outcome_values:
            outcome_values['time_point_role'] = determine_time_point_role(outcome_values['time_point'], primary_timepoint)
        
        # 3. 提取随访周数
        if 'time_point' in outcome_values and 'followup_weeks' not in outcome_values:
            outcome_values['followup_weeks'] = extract_followup_weeks(outcome_values['time_point'])
        
        # 4. 判断高分是否更好
        if 'outcome_name' in outcome_values and 'higher_is_better' not in outcome_values:
            outcome_values['higher_is_better'] = determine_higher_is_better(outcome_values['outcome_name'])
        
        # 5. 如果outcome_types为None，不需要检查类型匹配
        if outcome_types and 'outcome_type' in outcome_values:
            extracted_type = outcome_values['outcome_type'].lower() if outcome_values['outcome_type'] else ''
            allowed = False
            for allowed_type in outcome_types:
                if allowed_type.lower() in extracted_type or extracted_type in allowed_type.lower():
                    allowed = True
                    break
            if not allowed:
                # 如果类型不匹配，跳过这个outcome
                continue
        
        # 6. 判断效应量类型（如果未提供或需要校正）
        if 'effect_size_value' in outcome_values and ('effect_size_type' not in outcome_values or outcome_values['effect_size_type'] is None):
            outcome_type_val = outcome_values.get('outcome_type', '')
            outcome_name_val = outcome_values.get('outcome_name', '')
            comparison_type_val = outcome_values.get('comparison_type', '')
            effect_size_value_val = outcome_values.get('effect_size_value')
            
            if effect_size_value_val is not None:
                effect_size_type = determine_effect_size_type(
                    effect_size_value_val, outcome_type_val, outcome_name_val, comparison_type_val
                )
                outcome_values['effect_size_type'] = effect_size_type
                
                # 根据效应量类型确定效应量定义
                if 'effect_size_definition' not in outcome_values or outcome_values['effect_size_definition'] is None:
                    outcome_values['effect_size_definition'] = determine_effect_size_definition(
                        effect_size_type, comparison_type_val, outcome_type_val
                    )
        
        # 7. 数据完整性检查：如果arm_type是control但描述性统计字段有值，检查是否是本组的数据
        if arm_type.lower() in ['control', 'comparator', 'placebo']:
            # 检查是否有描述性统计字段被误填
            desc_fields = ['mean', 'sd', 'median', 'iqr', 'event_count', 'total_count', 'mean_ci_lower', 'mean_ci_upper']
            for field in desc_fields:
                if field in outcome_values and outcome_values[field] is not None:
                    # 检查source中是否明确提到这是对照组的数据
                    source_text = outcome_sources.get(field, '')
                    if source_text and (arm_name.lower() in source_text.lower() or 'control' in source_text.lower() or '对照' in source_text.lower()):
                        # 如果source中明确提到了对照组，保留数据
                        pass
                    else:
                        # 如果没有明确提到是对照组的数据，可能被误填，发出警告
                        print(f"警告: {arm_name}组的{field}字段可能不是本组数据，source中未明确提到{arm_name}或对照组")
                        # 这里不自动清除，因为可能是正确的
        
        processed_outcomes_values.append(outcome_values)
        processed_outcomes_sources.append(outcome_sources)
    
    # 归一化结局指标名称，避免重复
    if processed_outcomes_values:
        processed_outcomes_values = normalize_outcome_names(processed_outcomes_values)
        # 归一化后需要重新匹配sources
        # 这里简化处理：如果归一化后数量不变，保持原有sources
        # 如果数量变化，重新分配sources（可能不准确，但这是简化处理）
        if len(processed_outcomes_sources) != len(processed_outcomes_values):
            # 如果归一化导致数量变化，重新创建sources
            processed_outcomes_sources = []
            for _ in processed_outcomes_values:
                # 创建空的sources字典
                sources_dict = {}
                for field in ATOMIC_OUTCOMES_FIELDS:
                    sources_dict[field] = None
                processed_outcomes_sources.append(sources_dict)
    
    # 如果allowed_comparison_type为None，不进行过滤
    if processed_outcomes_values and allowed_comparison_type:
        filtered_values = []
        filtered_sources = []
        for i, outcome_values in enumerate(processed_outcomes_values):
            comp_type = outcome_values.get('comparison_type', '')
            if allowed_comparison_type in comp_type:
                filtered_values.append(outcome_values)
                filtered_sources.append(processed_outcomes_sources[i])
            elif allowed_comparison_type == "组间横向对比" and "vs" in outcome_values.get('comparison_targets', ''):
                # 如果对比目标包含"vs"，也认为是组间对比
                filtered_values.append(outcome_values)
                filtered_sources.append(processed_outcomes_sources[i])
            elif allowed_comparison_type == "组内前后对比" and any(keyword in outcome_values.get('comparison_targets', '') for keyword in ['前 vs 后', 'pre vs post', 'baseline vs']):
                # 如果对比目标包含前后对比关键词，认为是组内对比
                filtered_values.append(outcome_values)
                filtered_sources.append(processed_outcomes_sources[i])
        processed_outcomes_values = filtered_values
        processed_outcomes_sources = filtered_sources
    
    return processed_outcomes_values, processed_outcomes_sources
