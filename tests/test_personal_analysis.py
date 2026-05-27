from news_daily.personal_analysis import build_personal_insights


def test_personal_insights_prioritize_engineering():
    items = [
        {
            "title": "住建部部署城市更新和老旧小区改造工作",
            "summary_zh": "",
            "source_name": "住建部",
            "categories": ["工程技术"],
        }
    ]
    insights = build_personal_insights(items)
    assert insights
    assert "工程" in insights[0]


def test_personal_insights_fallback():
    insights = build_personal_insights([])
    assert "保持观察" in insights[0]
