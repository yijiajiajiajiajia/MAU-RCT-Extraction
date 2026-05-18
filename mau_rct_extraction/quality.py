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
