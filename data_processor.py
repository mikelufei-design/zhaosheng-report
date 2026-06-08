"""
数据处理器 - 读取、清洗和分析咨询信息表数据
"""
import pandas as pd
import re
from datetime import datetime, timedelta
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "咨询信息表.xlsx"

COURSE_CATEGORIES = {
    "设计培训": ["设计", "平面设计", "室内设计", "UI设计", "视觉设计"],
    "影视后期": ["影视后期", "视频剪辑", "剪辑", "拍摄", "短视频", "后期", "特效"],
    "办公软件": ["办公软件", "办公", "office", "PPT", "Excel", "Word", "企业培训"],
    "计算机等级": ["计算机二级", "计算机等级", "二级", "NIT", "计算机考试"],
    "CAD": ["CAD", "制图", "绘图"],
    "3DMAX": ["3DMAX", "3D", "三维"],
    "AIGC/AI": ["AIGC", "AI", "人工智能", "AI漫剧", "AI视频"],
    "编程/自动化": ["编程", "自动化", "软件"],
    "职场技能": ["职场", "通用技能", "新媒体", "运营"],
}

INTENT_LEVELS = {
    "A": "高意向 - 近期有明确预算和需求，可能已报名或即将报名",
    "B": "中意向 - 有明确需求但有些顾虑（时间/地点/价格），需要跟进",
    "C": "低意向 - 有咨询但暂时无法转化（在外地/预算不足/课程不匹配）",
    "D": "无效/静默 - 不回复/不需要/无法联系",
}


def load_data():
    df = pd.read_excel(DATA_PATH)
    df.columns = ["日期", "姓名", "联系电话", "咨询专业", "回访记录"]
    df = df.iloc[1:].reset_index(drop=True)

    def parse_date(val):
        if pd.isna(val):
            return None
        try:
            if isinstance(val, (int, float)):
                base = datetime(1899, 12, 30)
                return base + timedelta(days=int(val))
            return pd.to_datetime(str(val))
        except:
            return None

    df["咨询日期"] = df["日期"].apply(parse_date)
    df = _extract_structured_info(df)
    return df


def _extract_structured_info(df):
    records = []
    for _, row in df.iterrows():
        record = {
            "姓名": row.get("姓名"),
            "联系电话": str(int(row["联系电话"])) if pd.notna(row["联系电话"]) else None,
            "咨询专业": row.get("咨询专业"),
            "回访记录": row.get("回访记录"),
            "咨询日期": row.get("咨询日期"),
            "课程意愿": _extract_field(row.get("回访记录"), "意向课程"),
            "学习地点": _extract_field(row.get("回访记录"), "位置"),
            "学习时间": _extract_field(row.get("回访记录"), "学习时间"),
            "预算": _extract_field(row.get("回访记录"), "预算"),
            "学员背景": _extract_field(row.get("回访记录"), "学员背景"),
            "更多需求": _extract_field(row.get("回访记录"), "更多需求"),
            "沟通方式": _extract_field(row.get("回访记录"), "沟通方式"),
        }
        record["跟进状态"] = _infer_followup_status(row.get("回访记录"))
        record["痛点"] = _infer_pain_points(row.get("回访记录"))
        record["推荐策略"] = _infer_strategy(record["跟进状态"], record["痛点"])
        records.append(record)
    return pd.DataFrame(records)


def _extract_field(text, field_name):
    if pd.isna(text):
        return None
    pattern = rf"{field_name}[：:]\s*([^；;]*)"
    match = re.search(pattern, str(text))
    if match:
        return match.group(1).strip()
    return None


def _infer_followup_status(record_text):
    if pd.isna(record_text):
        return "new"
    text = str(record_text)
    if "已报名" in text or "以报名" in text:
        return "enrolled"
    if "不回复" in text or "发消息不回复" in text:
        return "silent"
    if "没来" in text:
        return "no_show"
    if "考虑" in text or "再决定" in text:
        return "considering"
    if "加微信" in text:
        return "contacted"
    if "太贵" in text:
        return "price_sensitive"
    if "不符合" in text or "没有这个项目" in text:
        return "not_matching"
    if "了解" in text or "咨询" in text or "学习" in text:
        return "interested"
    if "一直没空" in text or "没时间" in text:
        return "busy"
    if "联系" in text:
        return "contacted"
    return "new"


def _infer_pain_points(record_text):
    if pd.isna(record_text):
        return []
    text = str(record_text)
    points = []
    if "太贵" in text or "价格" in text:
        points.append("价格敏感")
    if "没时间" in text or "一直没空" in text:
        points.append("时间冲突")
    if "不符合" in text or "不匹配" in text:
        points.append("课程不匹配")
    if "不会" in text or "担心" in text:
        points.append("学习焦虑/信心不足")
    if "外地" in text or "在宝鸡" in text or "在云南" in text:
        points.append("地域限制")
    if "不回复" in text:
        points.append("失联/静默")
    if "孩子" in text:
        points.append("家长代咨询")
    if "包过" in text:
        points.append("证书导向")
    if "上班" in text or "在职" in text:
        points.append("在职学习")
    if "大一" in text or "高中" in text or "大三" in text:
        points.append("在校学生")
    if "基础" in text or "零基础" in text:
        points.append("零基础")
    if not points:
        points.append("明确需求")
    return points


def _infer_strategy(status, pain_points):
    strategies = []
    if status == "enrolled":
        strategies.append("已转化 - 转教务跟进，无需重复联系")
    elif status == "no_show":
        strategies.append("重新邀约 - 了解未到原因，提供试听激励")
    elif status == "silent":
        strategies.append("冷却唤醒 - 隔3-5天发送有价值内容而非直接推销")
    elif status == "considering":
        strategies.append("价值培育 - 发送成功案例+课程价值点，降低决策门槛")
    elif status == "price_sensitive":
        strategies.append("价格策略 - 强调分期/优惠活动/性价比对比")
    elif status == "not_matching":
        strategies.append("需求再挖掘 - 深入了解真实需求，推荐替代课程")
    elif status == "busy":
        strategies.append("时间管理 - 提供弹性学习方案，录播+直播选项")
    elif status == "interested":
        strategies.append("加速转化 - 提供限时优惠/试听名额，推动决策")
    else:
        strategies.append("初次接触 - 了解需求，建立信任，推荐试听")
    if "地域限制" in pain_points:
        strategies.append("远程方案 - 推荐线上课程或分校区")
    if "学习焦虑" in pain_points:
        strategies.append("打消顾虑 - 提供免费试听+入门指导")
    return strategies


def get_course_match(need_keywords):
    matches = {}
    for category, keywords in COURSE_CATEGORIES.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in str(need_keywords).lower():
                score += 1
        if score > 0:
            matches[category] = min(score, 5)
    return matches


def get_all_courses():
    return list(COURSE_CATEGORIES.keys())


def get_stats(df_all):
    status_counts = df_all["跟进状态"].value_counts()
    stats = {
        "total_leads": len(df_all),
        "enrolled": int(status_counts.get("enrolled", 0)),
        "silent": int(status_counts.get("silent", 0)),
        "no_show": int(status_counts.get("no_show", 0)),
        "considering": int(status_counts.get("considering", 0)),
        "interested": int(status_counts.get("interested", 0)),
        "contacted": int(status_counts.get("contacted", 0)),
        "price_sensitive": int(status_counts.get("price_sensitive", 0)),
        "not_matching": int(status_counts.get("not_matching", 0)),
        "busy": int(status_counts.get("busy", 0)),
        "new": int(status_counts.get("new", 0)),
    }
    course_dist = df_all["咨询专业"].value_counts().to_dict()
    return stats, course_dist
