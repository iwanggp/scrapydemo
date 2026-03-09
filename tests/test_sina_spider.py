from universal_scraper.spiders.sina_latest_comments_spider import SinaLatestCommentsSpider


def build_spider() -> SinaLatestCommentsSpider:
    return SinaLatestCommentsSpider(
        target_date="2026-03-09",
        max_pages=1,
        roll_page_size=10,
        comment_page_size=5,
        max_comment_pages=2,
        include_empty_comments=False,
        lid=2509,
    )


def test_parse_comment_id() -> None:
    spider = build_spider()
    assert spider._parse_comment_id("cj:comos-nhqknrn9882248:0") == {
        "comment_channel": "cj",
        "comment_newsid": "comos-nhqknrn9882248",
        "comment_group": "0",
    }


def test_normalize_comments() -> None:
    spider = build_spider()
    rows = [
        {
            "mid": "1",
            "time": "2026-03-09 15:00:00",
            "nick": "tester",
            "uid": "42",
            "area": "Shanghai",
            "content": "hello",
            "agree": "3",
            "against": "1",
            "count_layer": "2",
            "is_hot": "0",
            "is_top": "0",
        }
    ]
    normalized = spider._normalize_comments(rows)
    assert normalized[0]["content"] == "hello"
    assert normalized[0]["agree"] == 3
    assert normalized[0]["reply_count"] == 2


def test_max_comment_pages_is_capped() -> None:
    spider = build_spider()
    assert spider._max_comment_pages_for_article(0) == 1
    assert spider._max_comment_pages_for_article(4) == 1
    assert spider._max_comment_pages_for_article(6) == 2
