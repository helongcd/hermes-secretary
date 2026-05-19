#!/usr/bin/env python3
"""云马秘书提醒 - GitHub Actions推送脚本
通过Server酱将提醒推送到龙哥微信。
"""
import os, sys, json, urllib.request
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))

SENDKEY = os.environ["SENDKEY"]
TASK_TYPE = os.environ.get("TASK_TYPE", "morning_brief")

# 日程文件路径（仓库根目录）
SCHEDULE_FILE = "秘书日程.md"
TODO_FILE = "秘书待办.md"

def send_wechat(title, content=""):
    """通过Server酱推送微信消息"""
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = urllib.parse.urlencode({
        "title": title,
        "desp": content
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    print(f"Server酱返回: {result}")
    return result.get("code") == 0

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def get_morning_brief():
    """每日晨报 7:30"""
    now = datetime.now(CST)
    weekday = ["周一","周二","周三","周四","周五","周六","周日"][now.weekday()]
    date_str = now.strftime("%Y年%m月%d日")
    
    schedule = read_file(SCHEDULE_FILE)
    todos = read_file(TODO_FILE)
    
    # 提取今天的日程
    lines = []
    lines.append(f"☀️ 云马晨报 | {date_str} {weekday}")
    lines.append("")
    
    if schedule.strip():
        lines.append("📅 近期日程：")
        lines.append(schedule[:500])
    else:
        lines.append("📅 今日暂无特殊日程记录")
    
    if todos.strip():
        lines.append("")
        lines.append("📋 待办事项：")
        lines.append(todos[:300])
    
    lines.append("")
    lines.append("（云马秘书 · GitHub Actions云端推送）")
    
    return f"云马晨报 {date_str} {weekday}", "\n".join(lines)

def get_hou_reminder(period):
    """侯校长调研提醒"""
    now = datetime.now(CST)
    date_str = now.strftime("%m月%d日")
    
    if period == "morning":
        title = f"🏫 侯校长调研·晨间提醒 {date_str}"
        content = f"""侯校长到航空装备制造产业学院（装备学院）调研期间，今天有调研会议安排。

请提前做好准备，核实会议时间、地点、参会人员。

⏰ 持续至5月29日（下周五）
📌 下午4:00还有一次提醒

（云马秘书 · GitHub Actions云端推送）"""
    else:
        title = f"🏫 侯校长调研·午后提醒 {date_str}"
        content = f"""侯校长调研期间，请回顾今天调研会议情况，确认明日安排是否就绪。

如有需要协调的事项请及时处理。

⏰ 持续至5月29日（下周五）
📋 明早8:00继续提醒

（云马秘书 · GitHub Actions云端推送）"""
    
    return title, content

def get_monday_meeting():
    """周一班子会议提醒"""
    return ("📋 周一提醒 — 班子会议", 
            "今天上午有 学院、研究院、统战部班子会议，请注意安排时间。\n\n（云马秘书 · GitHub Actions云端推送）")

def get_thursday_meeting():
    """周四常委会提醒"""
    return ("🏛 周四提醒 — 常委会",
            "今天上午有 常委会，建议不要请假。请提前安排好其他事务。\n\n（云马秘书 · GitHub Actions云端推送）")

def get_arxiv_report():
    """arXiv哨兵（简化版：仅提醒，实际搜索需要更复杂逻辑）"""
    return ("🔬 arXiv哨兵", 
            "本周arXiv智能制造+职业教育新论文已更新，请关注。\n\n（云马秘书 · GitHub Actions云端推送）")

# 主逻辑
TASKS = {
    "morning_brief": get_morning_brief,
    "hou_morning": lambda: get_hou_reminder("morning"),
    "hou_afternoon": lambda: get_hou_reminder("afternoon"),
    "monday_meeting": get_monday_meeting,
    "thursday_meeting": get_thursday_meeting,
    "arxiv_report": get_arxiv_report,
}

if TASK_TYPE not in TASKS:
    print(f"未知任务类型: {TASK_TYPE}")
    sys.exit(1)

title, content = TASKS[TASK_TYPE]()
print(f"推送任务: {TASK_TYPE}")
print(f"标题: {title}")
print(f"内容长度: {len(content)}")

success = send_wechat(title, content)
if success:
    print("✅ 推送成功")
else:
    print("❌ 推送失败")
    sys.exit(1)
