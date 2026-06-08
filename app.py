"""
招生智能体系统 - 主应用
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from datetime import datetime

from data_processor import load_data, get_stats, get_all_courses
from agents.lead_scorer import score_leads
from agents.followup_agent import get_followup_strategy, STATUS_LABELS
from agents.analysis_agent import generate_insights

app = FastAPI(title="招生智能体系统")
templates = Jinja2Templates(directory="templates")
DATA_CACHE = {}
COURSE_MATCH_CACHE = get_all_courses()


def _clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "item"):
        try:
            v = v.item()
            if isinstance(v, float) and math.isnan(v):
                return None
        except:
            pass
    if isinstance(v, list):
        return [_clean_val(x) for x in v]
    if isinstance(v, dict):
        return {k: _clean_val(x) for k, x in v.items()}
    return v


def safe_str(v, default=""):
    if v is None:
        return default
    s = str(v)
    if s in ("nan", "NaT", "<NA>", "<N/A>", ""):
        return default
    try:
        if isinstance(v, float) and math.isnan(v):
            return default
    except:
        pass
    try:
        if hasattr(v, "strftime"):
            return str(v.date()) if hasattr(v, "date") else s
    except:
        pass
    return s


def get_data():
    if "df" not in DATA_CACHE:
        df = load_data()
        DATA_CACHE["df"] = df
        DATA_CACHE["scores"] = score_leads(df)
    return DATA_CACHE["df"], DATA_CACHE["scores"]


@app.get("/api/leads")
async def get_leads():
    df, scores = get_data()
    leads = []
    for i, (_, row) in enumerate(df.iterrows()):
        score_info = scores[i] if i < len(scores) else {}
        lead = {
            "id": i,
            "姓名": safe_str(row.get("姓名"), "未留名"),
            "联系电话": safe_str(row.get("联系电话"), "未留电话"),
            "咨询专业": safe_str(row.get("咨询专业"), "未填写"),
            "咨询日期": safe_str(row.get("咨询日期"), "未知"),
            "课程意愿": safe_str(row.get("课程意愿")),
            "学习地点": safe_str(row.get("学习地点")),
            "跟进状态": safe_str(row.get("跟进状态"), "new"),
            "痛点": row.get("痛点") or [],
            "推荐策略": row.get("推荐策略") or [],
            "回访记录": safe_str(row.get("回访记录"))[:120],
            "总分": score_info.get("总分", 0),
            "等级": score_info.get("等级", "D"),
            "评分原因": score_info.get("评分原因", ""),
        }
        leads.append(lead)
    return JSONResponse(_clean_val(leads))


@app.get("/api/stats")
async def get_stats_api():
    df, scores = get_data()
    stats, course_dist = get_stats(df)
    insights, suggestions = generate_insights(df)
    return JSONResponse(_clean_val({
        "stats": stats,
        "course_dist": course_dist,
        "insights": insights,
        "suggestions": suggestions,
    }))


@app.get("/api/lead/{lead_id}")
async def get_lead(lead_id: int):
    df, scores = get_data()
    if lead_id < 0 or lead_id >= len(df):
        return JSONResponse({"error": "Not found"}, status_code=404)

    _, row = df.iloc[lead_id], df.iloc[lead_id]
    score_info = scores[lead_id] if lead_id < len(scores) else {}

    raw_status = row.get("跟进状态")
    if not isinstance(raw_status, str):
        raw_status = "new"
    raw_name = row.get("姓名")
    if not isinstance(raw_name, str):
        raw_name = None
    raw_course = row.get("咨询专业")
    if not isinstance(raw_course, str):
        raw_course = "相关课程"
    strategy = get_followup_strategy(
        raw_status or "new",
        raw_name or "同学",
        raw_course or "相关课程",
    )

    return JSONResponse(_clean_val({
        "id": lead_id,
        "姓名": safe_str(row.get("姓名"), "未留名"),
        "联系电话": safe_str(row.get("联系电话"), "未留电话"),
        "咨询专业": safe_str(row.get("咨询专业"), "未填写"),
        "咨询日期": safe_str(row.get("咨询日期"), "未知"),
        "课程意愿": safe_str(row.get("课程意愿")),
        "学习地点": safe_str(row.get("学习地点")),
        "学习时间": safe_str(row.get("学习时间")),
        "预算": safe_str(row.get("预算")),
        "学员背景": safe_str(row.get("学员背景")),
        "更多需求": safe_str(row.get("更多需求")),
        "跟进状态": safe_str(row.get("跟进状态"), "new"),
        "痛点": row.get("痛点") or [],
        "推荐策略": row.get("推荐策略") or [],
        "回访记录": safe_str(row.get("回访记录")),
        "总分": score_info.get("总分", 0),
        "等级": score_info.get("等级", "D"),
        "等级说明": score_info.get("等级说明", ""),
        "评分明细": score_info.get("评分明细", []),
        "评分原因": score_info.get("评分原因", ""),
        "跟进策略": strategy,
    }))


@app.get("/api/report")
async def get_report():
    df, scores = get_data()
    order = {"A": 0, "B": 1, "C": 2, "D": 3}
    report = []
    for i, (_, row) in enumerate(df.iterrows()):
        s = scores[i]
        report.append({
            "id": i,
            "name": safe_str(row.get("姓名"), "未留名"),
            "phone": safe_str(row.get("联系电话"), ""),
            "course": safe_str(row.get("咨询专业"), ""),
            "status": safe_str(row.get("跟进状态"), "new"),
            "pains": row.get("痛点") or [],
            "record": safe_str(row.get("回访记录")),
            "score": s.get("总分", 0),
            "level": s.get("等级", "D"),
        })
    report.sort(key=lambda x: (order.get(x["level"], 99), -x["score"]))
    return JSONResponse(_clean_val({
        "total": len(report),
        "a_list": [r for r in report if r["level"] == "A"],
        "b_list": [r for r in report if r["level"] == "B"],
        "silent_list": [r for r in report if r["status"] in ("silent", "no_show")],
        "enrolled_list": [r for r in report if r["status"] == "enrolled"],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }))


@app.get("/api/courses")
async def get_courses():
    return JSONResponse(_clean_val(COURSE_MATCH_CACHE))


@app.get("/api/statuses")
async def get_statuses():
    return JSONResponse(_clean_val([{"id": k, "label": v} for k, v in STATUS_LABELS.items()]))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/leads", response_class=HTMLResponse)
async def leads_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/workflow", response_class=HTMLResponse)
async def workflow_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/{path:path}", response_class=HTMLResponse)
async def spa_fallback(request: Request, path: str):
    if path in ("leads", "workflow", "analysis", "report"):
        return templates.TemplateResponse(request, "index.html", {"request": request})
    return HTMLResponse("Not Found", status_code=404)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
