from news_daily.textutil import norm_title, norm_url


def test_norm_title_basic():
    assert norm_title("  住建部：发布新规！ ") == "住建部 发布新规"


def test_norm_url_strips_query_fragment():
    assert norm_url("https://example.com/a?x=1#t") == "https://example.com/a"

