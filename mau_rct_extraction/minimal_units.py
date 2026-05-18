from .fields import DESIGN_INFO_FIELDS
from .json_utils import safe_json_parse
from .runtime import call_api_with_retry


# ----------------------------
# API 提取最小原子单元（根据干预组和对照组定义）- 改进版
# ----------------------------
def extract_minimal_units_with_source(text, study_id, intervention_arm_definition, comparator_arm_definition):
    """提取最小原子单元，同时提取原文原句"""
    # 根据是否有限制条件调整提示词
    intervention_text = f"**干预组定义: {intervention_arm_definition}**" if intervention_arm_definition else "**不限制干预组定义，请提取文章中所有的试验组**"
    comparator_text = f"**对照组定义: {comparator_arm_definition}**" if comparator_arm_definition else "**不限制对照组定义，请提取文章中所有的对照组**"
    
    prompt = f"""
    你是一个医学数据提取助手。请根据下面的文章文本，提取研究中最小原子单元（实验组或对照组）的基础信息，并为每个字段提供原文依据。
    
    **组别定义：**
    {intervention_text}
    {comparator_text}
    
    **重要：必须返回有效的JSON数组，每个元素是一个对象，包含以下17个字段。**
    
    **请生成 JSON 列表，每个元素表示一个最小单元，每个字段都是一个对象，包含：**
    1. "value": 字段的值
    2. "source": 原文中原句（直接从原文中引用，不要修改）
    
    每个单元包含以下17个固定字段：
    {{
        "study_id": {{"value": "{study_id}", "source": "文件名"}},
        "arm_name": {{"value": null, "source": null}},
        "arm_type": {{"value": null, "source": null}},
        "timepoint": {{"value": null, "source": null}},
        "subgroup": {{"value": null, "source": null}},
        "total_participants": {{"value": null, "source": null}},
        "gender_male_count": {{"value": null, "source": null}},
        "gender_female_count": {{"value": null, "source": null}},
        "mean_age": {{"value": null, "source": null}},
        "age_sd": {{"value": null, "source": null}},
        "intervention_details": {{"value": null, "source": null}},
        "intervention_duration": {{"value": null, "source": null}},
        "intervention_frequency": {{"value": null, "source": null}},
        "control_details": {{"value": null, "source": null}},
        "adherence_to_control": {{"value": null, "source": null}},
        "adherence_to_intervention": {{"value": null, "source": null}},
        "number_of_participants_analyzed": {{"value": null, "source": null}}
    }}
    
    **关键要求：**
    1. {"根据干预组定义识别干预组" if intervention_arm_definition else "识别文章中所有的试验组"}
    2. {"根据对照组定义识别对照组" if comparator_arm_definition else "识别文章中所有的对照组"}
    3. 对于每个单元，设置arm_type字段，说明该单元是干预组还是对照组
    4. 提取详细的人口统计学信息和干预/对照措施信息
    5. {"只提取与上述定义相关的组" if intervention_arm_definition or comparator_arm_definition else "提取文章中所有相关的试验组和对照组"}
    
    **字段说明：**
    - arm_type: 可以是 "intervention", "control", "comparator", "placebo" 等
    - timepoint: 如 "baseline", "post-intervention", "follow-up" 等
    - subgroup: 如果有亚组分析，请提取亚组信息
    - intervention_details: 详细描述干预措施，包括具体方法、剂量、强度等
    - control_details: 详细描述对照措施
    - adherence_to_control/adherence_to_intervention: 依从性数据，如百分比、人数等
    
    **重要要求：**
    1. 对于每个字段，必须提供原文依据（source）
    2. source字段必须是原文中的原句，不要修改
    3. 如果找不到原文依据，source设为null
    
    **JSON格式要求：**
    1. 必须返回完全符合JSON语法的数组
    2. 所有字符串必须用双引号
    3. 不能有尾随逗号
    4. 不能有注释
    5. 确保JSON结构完整闭合
    
    文章文本: {text}  # 限制文本长度
    
    请尽可能根据文本提取完整信息。
    返回标准 JSON 数组。
    
    Output valid JSON only.
    Do not use LaTeX, Markdown, or backslash escape sequences (e.g., \(, \_).
    Use plain text such as vitamin D3.
    """
    
    try:
        response = call_api_with_retry([{"role": "user", "content": prompt}])
        
        if response:
            result_text = response.choices[0].message.content
            # 使用安全的JSON解析
            units_with_source = safe_json_parse(result_text, [])
            
            if not isinstance(units_with_source, list):
                print(f"警告: 返回的不是列表，而是 {type(units_with_source)}，尝试转换为列表")
                units_with_source = [units_with_source] if units_with_source else []
        else:
            units_with_source = []
            
    except Exception as e:
        print(f"提取最小单元时出错: {e}")
        units_with_source = []
    
    # 分离值和原文
    units_values = []
    units_sources = []
    
    for unit_with_source in units_with_source:
        unit_values = {}
        unit_sources = {}
        
        for field in DESIGN_INFO_FIELDS:
            if field in unit_with_source:
                field_data = unit_with_source[field]
                if isinstance(field_data, dict):
                    unit_values[field] = field_data.get("value")
                    unit_sources[field] = field_data.get("source")
                else:
                    unit_values[field] = field_data
                    unit_sources[field] = None
            else:
                unit_values[field] = None
                unit_sources[field] = None
        
        units_values.append(unit_values)
        units_sources.append(unit_sources)
    
    return units_values, units_sources
