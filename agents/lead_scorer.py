"""
线索评分Agent - 基于多维特征对咨询线索进行智能评分
"""
import pandas as pd
import re
from datetime import datetime


def score_leads(df):
    """对线索进行A/B/C/D四级评分"""
    scores = []
    for _, row in df.iterrows():
        s = _score_single_lead(row)
        scores.append(s)
    return scores


def _score_single_lead(row):
    """对单条线索评分，返回评分详情"""
    total = 0
    details = []
    reasons = []

    # 1. 需求明确度评分 (0-30分)
    clarity_score, clarity_reason = _eval_demand_clarity(row)
    total += clarity_score
    details.append(("需求明确度", clarity_score, 30))
    reasons.append(clarity_reason)

    # 2. 跟进状态评分 (0-25分)
    status_score, status_reason = _eval_status(row.get("跟进状态", ""))
    total += status_score
    details.append(("跟进状态", status_score, 25))
    reasons.append(status_reason)

    # 3. 预算和地域 (0-25分)
    budget_score, budget_reason = _eval_budget_location(row)
    total += budget_score
    details.append(("预算与地域", budget_score, 25))
    reasons.append(budget_reason)

    # 4. 互动意愿 (0-20分)
    engagement_score, engagement_reason = _eval_engagement(row)
    total += engagement_score
    details.append(("互动意愿", engagement_score, 20))
    reasons.append(engagement_reason)

    # 等级评定
    if total >= 80:
        level = "A"
        level_desc = "高意向 - 优先跟进，建议24小时内联系"
    elif total >= 60:
        level = "B"
        level_desc = "中意向 - 近期跟进，制定针对性方案"
    elif total >= 40:
        level = "C"
        level_desc = "低意向 - 长期培育，定期发送价值内容"
    else:
        level = "D"
        level_desc = "待观察 - 先尝试唤醒，无效则归档"

    return {
        "姓名": row.get("姓名"),
        "联系电话": row.get("联系电话"),
        "总分": total,
        "等级": level,
        "等级说明": level_desc,
        "评分明细": details,
        "评分原因": " | ".join(reasons),
    }


def _eval_demand_clarity(row):
    """评估需求明确度"""
    score = 0
    record = str(row.get("回访记录", ""))
    zhuan_ye = row.get("咨询专业")

    # 有明确的咨询专业
    if pd.notna(zhuan_ye) and str(zhuan_ye).strip():
        score += 10

    # 有结构化需求描述
    if "学习课程" in record:
        score += 8
    if "意向课程" in record:
        score += 5
    if "预算" in record and "有" in record:
        score += 7

    # 有时间预期
    if "近期" in record or "尽快" in record:
        score += 5
    elif "了解" in record or "咨询" in record:
        score += 3

    reason = f"需求明确度得分{score}/30"
    return min(score, 30), reason


def _eval_status(status):
    """评估跟进状态"""
    status_score_map = {
        "enrolled": 25,
        "interested": 20,
        "contacted": 15,
        "considering": 15,
        "new": 12,
        "busy": 10,
        "price_sensitive": 10,
        "no_show": 8,
        "not_matching": 5,
        "silent": 0,
    }
    score = status_score_map.get(status, 5)
    reason = f"跟进状态得分{score}/25"
    return score, reason


def _eval_budget_location(row):
    """评估预算和地域条件"""
    score = 0
    record = str(row.get("回访记录", ""))
    location = row.get("学习地点")

    # 预算
    if "预算" in record and "有" in record:
        score += 10
    elif "太贵" in record or "价格" in record:
        score += 5

    # 地域
    if pd.notna(location):
        if "西安" in str(location):
            score += 10
        elif "宝鸡" in str(location) or "云南" in str(location):
            score += 3
        else:
            score += 5
    else:
        # 默认加合理分数
        score += 7

    reason = f"预算与地域得分{score}/25"
    return min(score, 25), reason


def _eval_engagement(row):
    """评估互动意愿"""
    score = 0
    record = str(row.get("回访记录", ""))
    name = row.get("姓名")

    if "已报名" in record or "以报名" in record:
        score += 20
    if "加微信" in record:
        score += 8
    if "试听" in record and "没来" not in record:
        score += 8
    if pd.notna(name) and name not in ["先生", "女士", "同学", "学员", "W", "w", "家长"]:
        score += 5
    # 有详细回访记录的
    if len(record) > 30:
        score += 3

    reason = f"互动意愿得分{score}/20"
    return min(score, 20), reason
