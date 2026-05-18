def collect_meta_analysis_parameters():
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

    return {
        "intervention_arm_definition": intervention_arm_definition,
        "comparator_arm_definition": comparator_arm_definition,
        "outcome_domain": outcome_domain,
        "outcome_types": outcome_types,
        "primary_timepoint": primary_timepoint,
        "allowed_comparison_type": allowed_comparison_type,
        "allowed_study_designs": allowed_study_designs,
    }
