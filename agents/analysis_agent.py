"""
分析Agent - 生成数据洞察和报表
"""
import pandas as pd
from collections import Counter


def generate_insights(df):
    """生成数据洞察报告"""
    insights = []

    # 总体转化率
    total = len(df)
    enrolled = len(df[df["跟进状态"] == "enrolled"])
    conversion_rate = round(enrolled / total * 100, 1) if total > 0 else 0
    insights.append({
        "type": "conversion",
        "title": "整体转化率",
        "value": f"{conversion_rate}%",
        "detail": f"共{total}条线索，已报名{enrolled}人",
        "priority": "high"
    })

    # 静默线索占比
    silent = len(df[df["跟进状态"] == "silent"])
    silent_rate = round(silent / total * 100, 1) if total > 0 else 0
    insights.append({
        "type": "warning",
        "title": "静默失联率",
        "value": f"{silent_rate}%",
        "detail": f"共{silent}条线索处于失联状态，建议启动唤醒策略",
        "priority": "high"
    })

    # 热门课程TOP3
    if "咨询专业" in df.columns:
        course_counts = df["咨询专业"].value_counts()
        top_courses = course_counts.head(3).to_dict()
        insights.append({
            "type": "trend",
            "title": "热门咨询课程TOP3",
            "value": " | ".join(list(top_courses.keys())[:3]),
            "detail": f"设计培训({top_courses.get('设计培训', 0)})、影视后期({top_courses.get('影视后期培训', 0)})、计算机等级({top_courses.get('计算机等级考试', 0)+top_courses.get('计算机二级考试', 0)})",
            "priority": "medium"
        })

    # 价格敏感分析
    price_sensitive = len(df[df["跟进状态"] == "price_sensitive"])
    if price_sensitive > 0:
        insights.append({
            "type": "opportunity",
            "title": "价格敏感客户数",
            "value": f"{price_sensitive}人",
            "detail": "可通过分期付款/优惠活动进行二次转化",
            "priority": "medium"
        })

    # 地域问题流失
    no_show_count = len(df[df["跟进状态"] == "no_show"])
    if no_show_count > 0:
        insights.append({
            "type": "opportunity",
            "title": "爽约未到客户",
            "value": f"{no_show_count}人",
            "detail": "建议在邀约时强调试听价值，提供交通指引或线上替代方案",
            "priority": "medium"
        })

    # 跟进状态分布
    status_dist = df["跟进状态"].value_counts().to_dict()
    insights.append({
        "type": "distribution",
        "title": "跟进状态分布",
        "value": "、" .join([f"{k}:{v}" for k, v in sorted(status_dist.items(), key=lambda x: -x[1])[:5]]),
        "detail": "各阶段客户分布情况",
        "priority": "low"
    })

    # 建议
    suggestions = []
    if silent_rate > 20:
        suggestions.append("⚠️ 静默率超过20%，建议启动批量唤醒活动")
    if conversion_rate < 10:
        suggestions.append("🎯 转化率偏低，建议优化初次联系话术和跟进节奏")
    if price_sensitive > 3:
        suggestions.append("💰 价格敏感客户较多，可考虑推出限时优惠或分期方案")

    return insights, suggestions
