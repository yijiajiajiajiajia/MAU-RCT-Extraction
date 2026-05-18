import re
from collections import defaultdict


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

