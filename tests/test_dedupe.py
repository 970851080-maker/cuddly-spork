from news_daily.dedupe import is_near_duplicate


def test_near_duplicate_true():
    assert is_near_duplicate("住建部发布城市更新新政", "城市更新新政：住建部发布")


def test_near_duplicate_false():
    assert not is_near_duplicate("苹果发布新手机", "住建部发布城市更新新政")

