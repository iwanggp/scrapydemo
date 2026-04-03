"""针对 SinaLatestCommentsSpider 的单元测试。"""
from __future__ import annotations

from datetime import date
from universal_scraper.spiders.sina_latest_comments_spider import SinaLatestCommentsSpider


def build_spider(**kwargs) -> SinaLatestCommentsSpider:
    defaults = dict(
        target_date="2026-03-09", max_pages=2, roll_page_size=10,
        comment_page_size=5, max_comment_pages=2,
        include_empty_comments=False, lid=2509,
    )
    defaults.update(kwargs)
    return SinaLatestCommentsSpider(**defaults)


class TestSpiderInit:
    def test_target_date_parsed(self):
        assert build_spider(target_date="2026-03-09").target_date == date(2026, 3, 9)

    def test_default_date_is_today(self):
        assert build_spider(target_date=None).target_date is not None

    def test_max_pages_minimum_is_one(self):
        assert build_spider(max_pages=0).max_pages == 1

    def test_roll_page_size_minimum_is_one(self):
        assert build_spider(roll_page_size=0).roll_page_size == 1

    def test_comment_page_size_minimum_is_one(self):
        assert build_spider(comment_page_size=-5).comment_page_size == 1

    def test_include_empty_comments_flag(self):
        assert build_spider(include_empty_comments=True).include_empty_comments is True


class TestParseCommentId:
    def test_standard_three_part_id(self):
        result = build_spider()._parse_comment_id("cj:comos-nhqknrn9882248:0")
        assert result == {"comment_channel": "cj", "comment_newsid": "comos-nhqknrn9882248", "comment_group": "0"}

    def test_two_part_id_defaults_group_to_zero(self):
        assert build_spider()._parse_comment_id("cj:comos-abc123")["comment_group"] == "0"

    def test_empty_string_returns_none(self):
        assert build_spider()._parse_comment_id("") is None

    def test_single_part_returns_none(self):
        assert build_spider()._parse_comment_id("onlyone") is None

    def test_colons_only_returns_none(self):
        assert build_spider()._parse_comment_id("::") is None


class TestParseArticleDate:
    def test_valid_epoch(self):
        assert isinstance(build_spider()._parse_article_date(1741478400), date)

    def test_string_epoch(self):
        assert isinstance(build_spider()._parse_article_date("1741478400"), date)

    def test_none_returns_none(self):
        assert build_spider()._parse_article_date(None) is None

    def test_invalid_string_returns_none(self):
        assert build_spider()._parse_article_date("not-a-timestamp") is None


class TestFormatEpoch:
    def test_returns_iso_string(self):
        result = build_spider()._format_epoch(1741478400)
        assert isinstance(result, str) and "T" in result

    def test_none_returns_none(self):
        assert build_spider()._format_epoch(None) is None

    def test_invalid_value_returns_none(self):
        assert build_spider()._format_epoch("bad") is None


class TestNormalizeComments:
    SAMPLE_ROW = {
        "mid": "1001", "time": "2026-03-09 15:00:00", "nick": "测试用户",
        "uid": "42", "area": "上海", "content": "这是一条测试评论",
        "agree": "10", "against": "2", "count_layer": "3",
        "is_hot": "1", "is_top": "0",
    }

    def test_basic_fields_preserved(self):
        row = build_spider()._normalize_comments([self.SAMPLE_ROW])[0]
        assert row["content"] == "这是一条测试评论"
        assert row["nick"] == "测试用户"

    def test_numeric_fields_converted_to_int(self):
        row = build_spider()._normalize_comments([self.SAMPLE_ROW])[0]
        assert row["agree"] == 10
        assert row["against"] == 2
        assert row["reply_count"] == 3

    def test_empty_list_returns_empty_list(self):
        assert build_spider()._normalize_comments([]) == []

    def test_missing_fields_return_none(self):
        row = build_spider()._normalize_comments([{}])[0]
        assert row["content"] is None
        assert row["agree"] is None

    def test_multiple_rows(self):
        rows = [dict(self.SAMPLE_ROW, mid=str(i)) for i in range(5)]
        assert len(build_spider()._normalize_comments(rows)) == 5


class TestMaxCommentPages:
    def test_zero_visible_returns_one(self):
        assert build_spider(max_comment_pages=2, comment_page_size=5)._max_comment_pages_for_article(0) == 1

    def test_two_pages_needed_and_allowed(self):
        assert build_spider(max_comment_pages=2, comment_page_size=5)._max_comment_pages_for_article(6) == 2

    def test_capped_by_max_comment_pages(self):
        assert build_spider(max_comment_pages=1, comment_page_size=5)._max_comment_pages_for_article(100) == 1


class TestToInt:
    def test_integer_value(self):
        assert build_spider()._to_int(5) == 5

    def test_string_integer(self):
        assert build_spider()._to_int("42") == 42

    def test_none_returns_none(self):
        assert build_spider()._to_int(None) is None

    def test_non_numeric_string_returns_none(self):
        assert build_spider()._to_int("abc") is None

    def test_float_string_returns_none(self):
        assert build_spider()._to_int("3.5") is None
