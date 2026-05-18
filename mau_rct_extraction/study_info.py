from .fields import STUDY_INFO_FIELDS
from .json_utils import safe_json_parse
from .runtime import call_api_with_retry


# ----------------------------
# API 提取静态研究信息（检查研究设计）
# ----------------------------
def extract_study_info_with_source(text, study_id, allowed_study_designs):
    """提取研究信息，同时提取原文原句"""
    # 如果没有指定研究设计，则不进行检查
    if not allowed_study_designs:
        check_design = False
        design_requirement = "不限制研究设计"
    else:
        check_design = True
        design_requirement = allowed_study_designs
    
    # 在提示词中指定18个固定字段，要求同时提取原文原句
    prompt = f"""
    你是一个医学数据提取助手。请根据下面的文章文本，提取研究的静态信息，并为每个字段提供原文依据。
    
    {f"**重要：本研究需要符合 {allowed_study_designs} 设计。请先判断研究设计是否符合要求。**" if check_design else "**注意：不限制研究设计，请提取所有相关信息。**"}
    
    请生成一个 JSON 对象，每个字段都是一个对象，包含两个属性：
    1. "value": 字段的值
    2. "source": 原文中原句（直接从原文中引用，不要修改）
    
    请提取以下18个固定字段：
    {{
        "study_id": {{"value": "{study_id}", "source": "文件名"}},
        "title": {{"value": null, "source": null}},
        "authors": {{"value": null, "source": null}},
        "year": {{"value": null, "source": null}},
        "journal": {{"value": null, "source": null}},
        "country": {{"value": null, "source": null}},
        "doi": {{"value": null, "source": null}},
        "study_design": {{"value": null, "source": null}},
        "inclusion_criteria": {{"value": null, "source": null}},
        "exclusion_criteria": {{"value": null, "source": null}},
        "study_setting": {{"value": null, "source": null}},
        "source_of_recruitment": {{"value": null, "source": null}},
        "number_of_participants_randomized": {{"value": null, "source": null}},
        "number_of_participants_analyzed": {{"value": null, "source": null}},
        "dropout_reasons": {{"value": null, "source": null}},
        "meets_inclusion_criteria": {{"value": null, "source": null}},
        "exclusion_reason": {{"value": null, "source": null}}
    }}
    
    对于study_design字段，请详细说明具体是运用了什么方法进行的随机（例如：计算机随机、数字表法随机、奇数偶数随机分组、根据入院时间分组，或者是没有详细说明）。
    
    **关键步骤：**
    {f"1. 首先判断研究设计是否符合 {allowed_study_designs} 要求" if check_design else "1. 提取研究设计信息"}
    {f"2. 如果符合，meets_inclusion_criteria 设为 true，exclusion_reason 设为 null" if check_design else "2. meets_inclusion_criteria 设为 true，exclusion_reason 设为 null（因为不限制研究设计）"}
    {f"3. 如果不符合，meets_inclusion_criteria 设为 false，exclusion_reason 说明原因" if check_design else ""}
    
    **重要要求：**
    1. 对于每个字段，必须提供原文依据（source）
    2. source字段必须是原文中的原句，不要修改
    3. 如果找不到原文依据，source设为null
    
    文章文本: {text}  # 限制文本长度
    
    **JSON格式要求：**
    1. 必须返回完全符合JSON语法的对象
    2. 所有字符串必须用双引号
    3. 不能有尾随逗号
    4. 不能有注释
    
    请尽可能提取完整信息。
    返回标准 JSON 对象。
    
    Output valid JSON only.
    Do not use LaTeX, Markdown, or backslash escape sequences (e.g., \(, \_).
    Use plain text such as vitamin D3.
    """
    
    try:
        response = call_api_with_retry([{"role": "user", "content": prompt}])
        
        if response:
            result_text = response.choices[0].message.content
            # 使用安全的JSON解析
            study_info_with_source = safe_json_parse(result_text, create_default_study_info_with_source(study_id))
        else:
            study_info_with_source = create_default_study_info_with_source(study_id)
            
    except Exception as e:
        print(f"提取研究信息时出错: {e}")
        study_info_with_source = create_default_study_info_with_source(study_id)
    
    # 分离值和原文
    study_info_values = {}
    study_info_sources = {}
    
    for field in STUDY_INFO_FIELDS:
        if field in study_info_with_source:
            field_data = study_info_with_source[field]
            if isinstance(field_data, dict):
                study_info_values[field] = field_data.get("value")
                study_info_sources[field] = field_data.get("source")
            else:
                study_info_values[field] = field_data
                study_info_sources[field] = None
        else:
            study_info_values[field] = None
            study_info_sources[field] = None
    
    # 如果不限制研究设计，确保 meets_inclusion_criteria 为 true
    if not check_design and study_info_values.get("meets_inclusion_criteria") is None:
        study_info_values["meets_inclusion_criteria"] = True
        study_info_values["exclusion_reason"] = None
        
    return study_info_values, study_info_sources

def create_default_study_info_with_source(study_id):
    """创建默认的研究信息结构（包含source）"""
    result = {}
    for field in STUDY_INFO_FIELDS:
        if field == "study_id":
            result[field] = {"value": study_id, "source": "文件名"}
        else:
            result[field] = {"value": None, "source": None}
    return result
