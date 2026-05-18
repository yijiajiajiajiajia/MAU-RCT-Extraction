import json
import re

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
