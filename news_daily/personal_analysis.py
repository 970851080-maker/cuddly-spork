from __future__ import annotations

from typing import Any, Iterable


def _get(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _text(item: Any) -> str:
    parts = [
        _get(item, "title", "") or "",
        _get(item, "summary_zh", "") or "",
    ]
    return " ".join(parts)


def _title(item: Any, limit: int = 34) -> str:
    title = (_get(item, "title", "") or "").replace("\n", " ").strip()
    if len(title) <= limit:
        return title
    return title[:limit].rstrip() + "..."


def _has_any(text: str, keywords: Iterable[str]) -> bool:
    lower = text.lower()
    return any(k.lower() in lower for k in keywords)


def build_personal_insights(items: Iterable[Any], max_lines: int = 5) -> list[str]:
    candidates: list[tuple[int, str]] = []
    seen: set[str] = set()
    skip_markers = [
        "cookie",
        "language",
        "纪检监察专题网站",
        "投资者关系",
        "信息公开",
        "网站地图",
        "数字能源业务网站",
        "专题网站",
        "主题教育",
        "语言",
    ]

    rules = [
        (
            100,
            ["住建部", "城市更新", "房地产", "保障房", "老旧小区", "工程建设", "施工", "中建", "中国建筑"],
            "工程口机会：{title}。这类信息要看有没有项目清单、资金来源、招投标和验收标准，和你做工程管理最直接。",
        ),
        (
            95,
            ["交通运输部", "铁路", "公路", "轨道交通", "机场", "桥梁", "隧道", "市政", "中铁"],
            "基建口机会：{title}。交通、市政、轨道类消息通常会传到总包、机电分包和现场履约，值得盯后续招标。",
        ),
        (
            90,
            ["山西", "太原", "晋中", "大同", "运城", "吕梁", "长治"],
            "回太原线索：{title}。山西相关政策和项目要单独收藏，后面看岗位、项目经理机会和稳定回流路径。",
        ),
        (
            88,
            ["武汉", "湖北", "哈尔滨", "黑龙江"],
            "区域对照：{title}。武汉/哈尔滨的项目、财政和城市更新动向，可以拿来和太原比较机会密度。",
        ),
        (
            86,
            ["暖通", "机电", "能源", "电力", "国家电网", "节能", "低碳", "双碳", "设备", "制冷", "供热", "建筑运营"],
            "暖通机电相关：{title}。重点看能耗标准、设备选型、电价和运维要求，最后都会落到方案、成本和验收。",
        ),
        (
            82,
            ["财政部", "专项债", "国债", "预算", "资金", "融资", "央行", "美联储", "利率", "银行"],
            "钱袋子信号：{title}。财政、债券、利率和银行监管会影响基建资金面，也影响回款节奏和合同风险。",
        ),
        (
            78,
            ["新闻联播", "国务院", "发改委", "重大工程", "消费", "就业", "人口", "公共服务"],
            "新闻联播信号：{title}。这类中央口径通常不是孤立新闻，后面可能对应地方执行、项目包装或资金安排。",
        ),
        (
            74,
            ["AI", "人工智能", "NVIDIA", "英伟达", "华为", "数字", "自动化", "智能体", "机器人"],
            "技术工具线索：{title}。AI 和数字化可以优先想怎么用在进度跟踪、资料整理、成本复盘和一建学习上。",
        ),
        (
            70,
            ["考试", "教育", "课程", "Khan Academy", "学习", "认知", "一建", "建造师"],
            "备考提醒：{title}。把当天政策、工程和资金新闻当案例背景，法规、管理、经济会更容易串起来。",
        ),
    ]

    for item in items:
        text = _text(item)
        if not text:
            continue
        raw_title = _get(item, "title", "") or ""
        if any(marker.lower() in raw_title.lower() for marker in skip_markers):
            continue
        for priority, keywords, template in rules:
            if not _has_any(text, keywords):
                continue
            title = _title(item)
            if not title or title in seen:
                continue
            seen.add(title)
            candidates.append((priority, template.format(title=title)))
            break

    candidates.sort(key=lambda x: -x[0])
    insights = [line for _, line in candidates[:max_lines]]
    if insights:
        return insights

    return [
        "今天没有特别贴近工程管理/机电/太原回流的强信号，先保持观察，把政策、资金和基建栏目当重点看。",
        "如果某个领域连续几天出现同类消息，再判断它是不是机会，而不是被单条新闻带节奏。",
    ]
