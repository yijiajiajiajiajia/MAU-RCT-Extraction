import os
import json
import pandas as pd
from openai import OpenAI
from pathlib import Path
import re
from collections import defaultdict
import time
import requests

# ----------------------------
# 新增：JSON格式修复函数
# ----------------------------
def fix_json_format(json_text):
    """
    修复常见的JSON格式问题
    1. 处理未闭合的引号
    2. 处理未闭合的括号
    3. 修复转义字符问题
    4. 处理截断的JSON
    """
    if not json_text:
        return json_text
    
    text = json_text.strip()
    
    # 尝试解析，如果成功直接返回
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError as e:
        print(f"JSON解析失败，尝试修复: {e}")
    
    # 修复1: 确保文本以[或{开头
    if not text.startswith('[') and not text.startswith('{'):
        # 找到第一个[或{
        for i, char in enumerate(text):
            if char in '[{':
                text = text[i:]
                break
    
    # 修复2: 确保引号闭合
    quote_count = text.count('"')
    if quote_count % 2 != 0:
        # 奇数个引号，添加一个闭合引号
        last_quote = text.rfind('"')
        if last_quote != -1:
            # 检查引号后面是否有逗号或结束符
            next_char = text[last_quote + 1] if last_quote + 1 < len(text) else ''
            if next_char not in [',', '}', ']', ':', ' ']:
                text = text + '"'
    
    # 修复3: 处理转义字符
    # 确保反斜杠被正确转义
    text = text.replace('\\', '\\\\')
    # 但不要转义已经转义过的
    text = text.replace('\\\\\\\\', '\\\\')
    
    # 修复4: 确保JSON结构闭合
    open_brackets = text.count('[') - text.count(']')
    open_braces = text.count('{') - text.count('}')
    
    # 添加缺失的闭合括号
    if open_brackets > 0:
        text += ']' * open_brackets
    if open_braces > 0:
        text += '}' * open_braces
    
    # 修复5: 处理常见的截断模式
    # 如果以逗号结尾，去掉逗号
    if text.endswith(','):
        text = text.rstrip(',')
    
    # 修复6: 处理缺少逗号的对象分隔
    # 查找模式: "value": ... } {  (缺少逗号)
    pattern = r'"\s*:\s*[^,}]+[^,]\s*}\s*{'
    if re.search(pattern, text):
        text = re.sub(pattern, lambda m: m.group(0).replace('} {', '}, {'), text)
    
    # 修复7: 最后尝试提取最长的有效JSON对象
    try:
        # 查找最长的从{到}或[到]的子串
        stack = []
        max_start = 0
        max_end = 0
        max_length = 0
        
        for i, char in enumerate(text):
            if char in '[{':
                stack.append(char)
                if len(stack) == 1:
                    start = i
            elif char in ']}':
                if stack:
                    last = stack.pop()
                    if (last == '[' and char == ']') or (last == '{' and char == '}'):
                        if not stack and (i - start + 1) > max_length:
                            max_length = i - start + 1
                            max_start = start
                            max_end = i + 1
        
        if max_length > 0:
            text = text[max_start:max_end]
    except:
        pass
    
    return text

def safe_json_parse(json_text, default_value=None):
    """
    安全解析JSON，尝试多种方法
    """
    if not json_text:
        return default_value
    
    # 方法1: 直接解析
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        pass
    
    # 方法2: 修复后解析
    fixed_text = fix_json_format(json_text)
    try:
        return json.loads(fixed_text)
    except json.JSONDecodeError:
        pass
    
    # 方法3: 尝试提取JSON部分
    try:
        # 查找第一个{到最后一个}之间的内容
        start = fixed_text.find('{')
        end = fixed_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            extracted = fixed_text[start:end+1]
            return json.loads(extracted)
    except:
        pass
    
    # 方法4: 尝试解析为列表
    try:
        start = fixed_text.find('[')
        end = fixed_text.rfind(']')
        if start != -1 and end != -1 and end > start:
            extracted = fixed_text[start:end+1]
            return json.loads(extracted)
    except:
        pass
    
    # 方法5: 如果所有方法都失败，返回默认值并打印调试信息
    print(f"警告: 无法解析JSON，使用默认值")
    print(f"原始文本前500字符: {json_text[:500]}")
    return default_value

# ----------------------------
# 配置
# ----------------------------
print("=== OpenAI GPT 模型配置 ===")

# OpenAI GPT 配置
api_key = "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"  # 替换为你的 OpenAI Key
base_url = "https://api.openai.com/v1"  # OpenAI API 端点
model_name = "gpt-4.1"
print("已选择 OpenAI GPT 模型")

# 创建客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,  # 增加超时时间
    max_retries=3   # 增加重试次数
)

# ----------------------------
# 用户输入荟萃分析参数
# ----------------------------
print("\n=== 荟萃分析参数设置 ===")
print("请按提示输入荟萃分析所需的参数（可直接按回车跳过，将提取文章中所有相关内容）：")

# 1. Intervention arm definition
print("\n1. 干预组定义 (Intervention arm definition)：")
print("描述您的干预组特征，例如：接受机器人辅助训练的患者、使用特定药物治疗的患者等")
print("如不输入，将提取文章中所有的干预组")
intervention_arm_definition = input("请输入干预组定义（直接回车跳过）: ").strip()
if not intervention_arm_definition:
    intervention_arm_definition = None
    print("将提取文章中所有的干预组")

# 2. Comparator arm definition
print("\n2. 对照组定义 (Comparator arm definition)：")
print("描述您的对照组特征，例如：接受常规康复训练的患者、使用安慰剂的患者等")
print("如不输入，将提取文章中所有的对照组")
comparator_arm_definition = input("请输入对照组定义（直接回车跳过）: ").strip()
if not comparator_arm_definition:
    comparator_arm_definition = None
    print("将提取文章中所有的对照组")

# 3. outcome_domain
print("\n3. 结局领域 (outcome_domain)：")
print("描述您关注的结局领域，例如：运动功能、认知功能、日常生活能力、疼痛程度等")
print("如不输入，将提取文章中所有领域的结局指标")
outcome_domain = input("请输入结局领域（直接回车跳过）: ").strip()
if not outcome_domain:
    outcome_domain = None
    print("将提取文章中所有领域的结局指标")

# 4. outcome_type - 允许多个结局指标类型，用分号分隔
print("\n4. 结局指标类型 (outcome_type)：")
print("请选择您需要的结局指标类型（可以多选，用分号分隔）：")
print("1. continuous - 连续变量（如量表评分）")
print("2. dichotomous - 二分类变量（如有效/无效）")
print("3. ordinal - 有序变量（如等级评分）")
print("4. time_to_event - 时间到事件数据（如生存时间）")
print("示例：1;2 或 continuous;dichotomous")
print("如不输入，将提取所有类型的结局指标")
outcome_type_input = input("请输入结局指标类型 (1-4 或类型名称，用分号分隔，直接回车跳过): ").strip()

# 处理用户输入的结局指标类型
outcome_types = []
if outcome_type_input:
    # 分割输入
    input_items = [item.strip() for item in outcome_type_input.split(';')]
    
    # 映射数字到类型名称
    outcome_type_mapping = {
        "1": "continuous",
        "2": "dichotomous", 
        "3": "ordinal",
        "4": "time_to_event"
    }
    
    # 转换所有输入项为标准化类型
    for item in input_items:
        if item in outcome_type_mapping:
            outcome_types.append(outcome_type_mapping[item])
        elif item.lower() in ["continuous", "dichotomous", "ordinal", "time_to_event"]:
            outcome_types.append(item.lower())
        else:
            print(f"警告: 未知的结局指标类型 '{item}'，已忽略")
    
    # 如果没有有效的类型，设置为None
    if not outcome_types:
        outcome_types = None
        print("将提取所有类型的结局指标")
else:
    # 如果没有输入，设置为None
    outcome_types = None
    print("将提取所有类型的结局指标")

# 5. primary_timepoint
print("\n5. 主要时间点 (primary_timepoint)：")
print("描述您关注的主要测量时间点，例如：")
print("- 干预后立即 (immediately post-intervention)")
print("- 干预后1个月 (1-month post-intervention)")
print("- 干预后3个月 (3-month follow-up)")
print("- 最长随访时间 (longest follow-up)")
print("如不输入，将提取文章中所有时间点的结局指标")
primary_timepoint = input("请输入主要时间点（直接回车跳过）: ").strip()
if not primary_timepoint:
    primary_timepoint = None
    print("将提取文章中所有时间点的结局指标")

# 6. allowed_comparison_type
print("\n6. 允许的对比类型 (allowed_comparison_type)：")
print("请选择对比类型：")
print("1. 组间横向对比 (between-group comparison)")
print("2. 组内前后对比 (within-group comparison)")
print("3. 组间变化值对比 (between-group change score comparison)")
print("如不输入，将提取所有类型的对比")
comparison_choice = input("请选择对比类型 (1-3，直接回车跳过): ").strip()

if comparison_choice:
    comparison_mapping = {
        "1": "组间横向对比",
        "2": "组内前后对比",
        "3": "组间变化值对比"
    }
    allowed_comparison_type = comparison_mapping.get(comparison_choice, "组间横向对比")
else:
    allowed_comparison_type = None
    print("将提取所有类型的对比")

# 7. allowed_study_designs
print("\n7. 允许的研究设计 (allowed_study_designs)：")
print("请选择研究设计：")
print("1. RCT (随机对照试验)")
print("2. CCT (临床对照试验)")
print("3. Cohort (队列研究)")
print("4. Case-control (病例对照研究)")
print("如不输入，将不限制研究设计")
design_choice = input("请选择研究设计 (1-4，直接回车跳过): ").strip()

if design_choice:
    design_mapping = {
        "1": "RCT",
        "2": "CCT",
        "3": "Cohort",
        "4": "Case-control"
    }
    allowed_study_designs = design_mapping.get(design_choice, "RCT")
else:
    allowed_study_designs = None
    print("将不限制研究设计")

print("\n=== 参数汇总 ===")
print(f"干预组定义: {intervention_arm_definition if intervention_arm_definition else '不限制（提取所有干预组）'}")
print(f"对照组定义: {comparator_arm_definition if comparator_arm_definition else '不限制（提取所有对照组）'}")
print(f"结局领域: {outcome_domain if outcome_domain else '不限制（提取所有领域）'}")
print(f"结局指标类型: {', '.join(outcome_types) if outcome_types else '不限制（提取所有类型）'}")
print(f"主要时间点: {primary_timepoint if primary_timepoint else '不限制（提取所有时间点）'}")
print(f"允许的对比类型: {allowed_comparison_type if allowed_comparison_type else '不限制（提取所有对比类型）'}")
print(f"允许的研究设计: {allowed_study_designs if allowed_study_designs else '不限制（提取所有研究设计）'}")

# 文件路径配置
TXT_PATH = r"D:\python_code\demo\texts\text2-3.txt"
OUTPUT_JSON_PATH = r"D:\python_code\demo\texts\meta_analysis_results_text2-3.json"
OUTPUT_EXCEL_PATH = r"D:\python_code\demo\texts\meta_analysis_results_text2-3.xlsx"
OUTPUT_EXCEL_PATH_WITH_SOURCE = r"D:\python_code\demo\texts\meta_analysis_results_text2-3_with_source.xlsx"

# ----------------------------
# 读取文本文件
# ----------------------------
print(f"\n正在读取文本文件: {TXT_PATH}")
with open(TXT_PATH, 'r', encoding='utf-8') as f:
    article_text = f.read()

study_id = Path(TXT_PATH).stem  # 文件名作为 study_id
print(f"已读取文本内容，字符数: {len(article_text)}")

# ----------------------------
# 带重试机制的 API 调用函数
# ----------------------------
def call_api_with_retry(messages, max_retries=3, initial_delay=2):
    """带重试机制的 API 调用"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0,
                timeout=120.0
            )
            return response
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError,
                Exception) as e:
            if attempt == max_retries - 1:  # 最后一次重试
                raise e
            delay = initial_delay * (2 ** attempt)  # 指数退避
            print(f"API调用失败，{delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
            time.sleep(delay)
    return None

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

# ----------------------------
# 结局指标归一化函数
# ----------------------------
def normalize_outcome_names(outcomes):
    """
    将相似的结局指标名称归一化，避免重复
    """
    # 定义常见指标的同义词映射
    synonym_mapping = {
        r'\bFMA\b': 'Fugl-Meyer Assessment',
        r'\bFMA score\b': 'Fugl-Meyer Assessment',
        r'\bFugl-Meyer\b': 'Fugl-Meyer Assessment',
        r'\bFugl Meyer\b': 'Fugl-Meyer Assessment',
        r'\bFugl-Meyer score\b': 'Fugl-Meyer Assessment',
        r'\bBI\b': 'Barthel Index',
        r'\bBarthel index\b': 'Barthel Index',
        r'\bMBI\b': 'Modified Barthel Index',
        r'\bMAS\b': 'Modified Ashworth Scale',
        r'\bAshworth scale\b': 'Modified Ashworth Scale',
        r'\bMMSE\b': 'Mini-Mental State Examination',
        r'\bMoCA\b': 'Montreal Cognitive Assessment',
        r'\bNIHSS\b': 'NIH Stroke Scale',
        r'\bARAT\b': 'Action Research Arm Test',
        r'\bVAS\b': 'Visual Analog Scale',
        r'\bNRS\b': 'Numeric Rating Scale',
        r'\bSF-36\b': 'Short Form-36',
        r'\bSIS\b': 'Stroke Impact Scale',
        r'\bEQ-5D\b': 'EuroQol-5 Dimensions',
        r'\bGCS\b': 'Glasgow Coma Scale',
        r'\bMRS\b': 'Modified Rankin Scale',
        r'\bADL\b': 'Activities of Daily Living',
    }
    
    # 按名称和单位分组结局指标，时间点作为关键分组条件
    outcome_groups = defaultdict(list)
    for outcome in outcomes:
        # 应用同义词映射
        normalized_name = outcome.get('outcome_name', '')
        if normalized_name:
            for pattern, replacement in synonym_mapping.items():
                normalized_name = re.sub(pattern, replacement, normalized_name, flags=re.IGNORECASE)
        else:
            normalized_name = ''
        
        # 获取时间点，确保一致性
        time_point = str(outcome.get('time_point', '')).strip().lower()
        
        # 创建分组键：包括名称、单位、时间点、arm_name、对比类型和对比目标
        group_key = (
            normalized_name.strip().lower(), 
            str(outcome.get('outcome_unit', '')).strip().lower(),
            time_point,
            str(outcome.get('arm_name', '')).strip().lower(),  # 加入arm_name
            str(outcome.get('comparison_type', '')).strip().lower(),
            str(outcome.get('comparison_targets', '')).strip().lower()
        )
        
        outcome_groups[group_key].append(outcome)
    
    # 合并每组中的结局指标
    merged_outcomes = []
    for group_key, group_outcomes in outcome_groups.items():
        if len(group_outcomes) == 1:
            # 如果只有一个结局指标，直接使用
            merged_outcome = group_outcomes[0]
            merged_outcome['outcome_name'] = group_key[0].title()  # 使用归一化后的名称
        else:
            # 如果有多个结局指标，合并它们
            merged_outcome = {}
            
            # 首先，确定统计值的一一对应关系
            stat_fields = ['p_value', 'effect_size_value', 'ci_lower', 'ci_upper', 'mean_ci_lower', 'mean_ci_upper']
            
            # 检查是否有冲突的统计值
            for stat_field in stat_fields:
                values = []
                for outcome in group_outcomes:
                    if outcome.get(stat_field) is not None:
                        values.append(outcome[stat_field])
                
                # 如果同一个对比属性组合下有多个不同的统计值，发出警告
                if len(set(values)) > 1:
                    print(f"警告: 对比属性组合 {group_key[4]} + {group_key[5]} 有多个不同的 {stat_field} 值: {values}")
            
            # 检查描述性统计字段的一致性（同一时间点应该相同）
            desc_fields = ['mean', 'sd', 'median', 'iqr', 'event_count', 'total_count', 'participants_analyzed']
            for desc_field in desc_fields:
                values = []
                for outcome in group_outcomes:
                    if outcome.get(desc_field) is not None:
                        values.append(outcome[desc_field])
                
                # 如果同一时间点的描述性统计值不同，发出警告
                if len(set(values)) > 1:
                    print(f"警告: 时间点 {group_key[2]} 的描述性统计字段 {desc_field} 有多个不同的值: {values}")
            
            # 合并其他字段
            for outcome in group_outcomes:
                for key, value in outcome.items():
                    if value is not None and value != '':
                        # 如果当前值为空但新值不为空，则更新
                        if key not in merged_outcome or merged_outcome[key] is None or merged_outcome[key] == '':
                            merged_outcome[key] = value
                        # 对于统计值字段，确保一一对应
                        elif key in stat_fields:
                            # 如果已经有一个统计值，不要覆盖
                            if merged_outcome[key] is not None:
                                # 如果有冲突，保持原值并警告
                                if str(merged_outcome[key]) != str(value):
                                    print(f"警告: 统计值冲突 - {key}: 原有值={merged_outcome[key]}, 新值={value}")
                            else:
                                merged_outcome[key] = value
                        # 对于描述性统计字段，如果有冲突，取第一个有效值
                        elif key in desc_fields:
                            # 这里简单取第一个有效值，因为同一时间点的描述性统计应该相同
                            if merged_outcome[key] is None:
                                merged_outcome[key] = value
                            elif str(merged_outcome[key]) != str(value):
                                print(f"注意: 描述性统计字段 {key} 有不同值，使用第一个值: {merged_outcome[key]} (忽略: {value})")
            
            # 确保所有必要字段都存在
            for key in ['outcome_name', 'outcome_unit', 'outcome_type', 'comparison_type', 'comparison_targets', 'time_point', 'arm_name']:
                if key not in merged_outcome:
                    merged_outcome[key] = group_outcomes[0].get(key)
            
            # 使用归一化后的名称
            merged_outcome['outcome_name'] = group_key[0].title() if group_key[0] else None
        
        merged_outcomes.append(merged_outcome)
    
    return merged_outcomes

# ----------------------------
# 时间点标准化函数
# ----------------------------
def standardize_time_point(time_str, primary_timepoint):
    """
    标准化时间点描述，确保一致性
    """
    if not time_str:
        return time_str
    
    time_str = str(time_str).strip().lower()
    
    # 首先检查是否是主要时间点（如果有主要时间点）
    if primary_timepoint:
        primary_lower = primary_timepoint.lower()
        if primary_lower in time_str:
            return primary_timepoint
    
    # 常见时间点映射
    time_mapping = {
        r'\b基线\b': '基线',
        r'\bbaseline\b': '基线',
        r'\b干预前\b': '干预前',
        r'\bpre-intervention\b': '干预前',
        r'\bpre intervention\b': '干预前',
        r'\b治疗前\b': '干预前',
        r'\bpretreatment\b': '干预前',
        r'\b干预后立即\b': '干预后立即',
        r'\b立即干预后\b': '干预后立即',
        r'\bimmediately post\b': '干预后立即',
        r'\b治疗后立即\b': '干预后立即',
        r'\b干预后\b': '干预后',
        r'\bpost-intervention\b': '干预后',
        r'\bpost intervention\b': '干预后',
        r'\b治疗后\b': '干预后',
        r'\bposttreatment\b': '干预后',
        r'\b随访1个月\b': '1个月随访',
        r'\b1个月随访\b': '1个月随访',
        r'\b1-month follow-up\b': '1个月随访',
        r'\b随访3个月\b': '3个月随访',
        r'\b3个月随访\b': '3个月随访',
        r'\b3-month follow-up\b': '3个月随访',
        r'\b随访6个月\b': '6个月随访',
        r'\b6个月随访\b': '6个月随访',
        r'\b6-month follow-up\b': '6个月随访',
        r'\b随访12个月\b': '12个月随访',
        r'\b12个月随访\b': '12个月随访',
        r'\b12-month follow-up\b': '12个月随访',
        r'\b短期随访\b': '短期随访',
        r'\bshort-term follow-up\b': '短期随访',
        r'\b中期随访\b': '中期随访',
        r'\bmid-term follow-up\b': '中期随访',
        r'\b长期随访\b': '长期随访',
        r'\blong-term follow-up\b': '长期随访',
    }
    
    for pattern, replacement in time_mapping.items():
        if re.search(pattern, time_str, flags=re.IGNORECASE):
            return replacement
    
    # 如果没有匹配，返回原始值但去除前后空格
    return time_str.strip()

# ----------------------------
# 时间点角色判断函数
# ----------------------------
def determine_time_point_role(time_point_str, primary_timepoint):
    """
    根据时间点描述判断其角色
    """
    if not time_point_str:
        return None
    
    time_str = str(time_point_str).lower()
    
    # 检查是否为基线
    if any(keyword in time_str for keyword in ['基线', 'baseline', '干预前', 'pre-intervention', '治疗前']):
        return 'baseline'
    
    # 检查是否为随访
    if any(keyword in time_str for keyword in ['随访', 'follow-up', 'follow up', 'month', '周', '周后', '月后']):
        return 'followup'
    
    # 检查是否为干预后（排除随访的情况）
    if any(keyword in time_str for keyword in ['干预后', 'post-intervention', '治疗后', 'posttreatment']):
        return 'post'
    
    # 如果包含主要时间点
    if primary_timepoint and primary_timepoint.lower() in time_str:
        return 'post'  # 主要时间点通常为干预后
    
    return None

# ----------------------------
# 效应量类型判断函数
# ----------------------------
def determine_effect_size_type(effect_size_value, outcome_type, outcome_name, comparison_type):
    """
    根据效应量值、结局类型、指标名称和对比类型判断效应量类型
    """
    if effect_size_value is None:
        return None
    
    # 尝试将effect_size_value转换为浮点数
    try:
        es_value = float(effect_size_value)
    except (ValueError, TypeError):
        return None
    
    # 检查是否为风险比或比值比（通常用于二分类结局）
    if outcome_type == 'dichotomous':
        if comparison_type and any(keyword in str(comparison_type).lower() for keyword in ['risk', 'hazard', 'survival']):
            # 生存分析相关
            if outcome_name and any(keyword in str(outcome_name).lower() for keyword in ['生存', '死亡', '复发', 'hazard', 'survival']):
                return 'HR'
            else:
                return 'RR' if abs(es_value) >= 0.1 else 'OR'
        else:
            # 一般二分类结局
            return 'RR' if abs(es_value) >= 0.1 else 'OR'
    
    # 连续变量结局
    elif outcome_type == 'continuous':
        # 检查是否为标准化均数差
        if abs(es_value) <= 3.0:  # SMD通常在-3到3之间
            # 检查是否为Hedges' g校正
            if outcome_name and 'hedges' in str(outcome_name).lower():
                return 'HEDGES_G'
            else:
                return 'SMD'
        else:
            # 较大的值可能是均数差
            return 'MD'
    
    # 有序变量结局
    elif outcome_type == 'ordinal':
        return 'SMD'  # 有序变量通常使用SMD
    
    # 时间到事件结局
    elif outcome_type == 'time_to_event':
        return 'HR'
    
    return None

# ----------------------------
# 效应量定义判断函数
# ----------------------------
def determine_effect_size_definition(effect_size_type, comparison_type, outcome_type):
    """
    根据效应量类型、对比类型和结局类型判断效应量定义
    """
    if not effect_size_type:
        return None
    
    if effect_size_type == 'HR':
        return 'reported adjusted HR'
    
    if comparison_type and 'change score' in str(comparison_type).lower():
        return 'between-group change score difference'
    
    # 默认情况
    return 'between-group post-intervention difference'

# ----------------------------
# 高分是否更好判断函数
# ----------------------------
def determine_higher_is_better(outcome_name):
    """
    根据结局指标名称判断高分是否更好
    """
    if not outcome_name:
        return None
    
    outcome_lower = str(outcome_name).lower()
    
    # 高分更好的指标
    higher_better = [
        '功能', '能力', '评分', '分数', '得分', '改善', '恢复',
        'fugl-meyer', 'barthel', 'bi', 'mbi', 'adl', 'sf-36', 'eq-5d',
        'moca', 'mmse', 'arat', '功能独立性', '生活质量'
    ]
    
    # 低分更好的指标
    lower_better = [
        '疼痛', '痉挛', '僵硬', '痉挛评分', '疼痛评分',
        'ashworth', 'mas', 'vas', 'nrs', 'nihss', 'mrs',
        '残疾', '障碍', '并发症', '不良事件', '死亡率'
    ]
    
    for keyword in higher_better:
        if keyword in outcome_lower:
            return True
    
    for keyword in lower_better:
        if keyword in outcome_lower:
            return False
    
    return None

# ----------------------------
# 随访周数提取函数
# ----------------------------
def extract_followup_weeks(time_point_str):
    """
    从时间点描述中提取随访周数
    """
    if not time_point_str:
        return None
    
    time_str = str(time_point_str)
    
    # 正则表达式匹配数字和单位
    patterns = [
        (r'(\d+)\s*周', 1),  # 数字+周
        (r'(\d+)\s*week', 1),  # 数字+week
        (r'(\d+)\s*month', 4.33),  # 数字+month，转换为周
        (r'(\d+)\s*月', 4.33),  # 数字+月
        (r'(\d+)\s*年', 52.14),  # 数字+年，转换为周
        (r'(\d+)\s*year', 52.14)  # 数字+year
    ]
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, time_str, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                return value * multiplier
            except ValueError:
                continue
    
    return None

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

# ----------------------------
# 时间点一致性检查
# ----------------------------
def check_timepoint_consistency(minimal_units, primary_timepoint):
    """检查时间点一致性"""
    if primary_timepoint:
        print(f"\n正在检查时间点一致性（主要时间点: {primary_timepoint}）...")
    else:
        print(f"\n正在检查时间点一致性（无主要时间点限制）...")
    
    all_timepoints = set()
    primary_timepoint_count = 0
    timepoint_issues = []
    
    for unit in minimal_units:
        for outcome in unit.get('outcomes', []):
            time_point = outcome.get('time_point')
            if time_point:
                all_timepoints.add(time_point)
                if primary_timepoint and primary_timepoint.lower() in time_point.lower():
                    primary_timepoint_count += 1
    
    print(f"发现的时间点数量: {len(all_timepoints)}")
    if all_timepoints:
        print(f"所有时间点: {', '.join(sorted(all_timepoints))}")
    
    if primary_timepoint:
        print(f"主要时间点 ({primary_timepoint}) 的指标数量: {primary_timepoint_count}")
        
        if primary_timepoint_count == 0:
            print(f"警告: 未找到主要时间点 ({primary_timepoint}) 的指标")
            print("将使用其他时间点的数据")
    
    return all_timepoints

# 执行时间点一致性检查
all_timepoints = check_timepoint_consistency(minimal_units, primary_timepoint)

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