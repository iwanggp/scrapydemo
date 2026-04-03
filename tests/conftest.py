"""共享测试夹具（fixtures）。"""
from __future__ import annotations

import pytest
from universal_scraper.spiders.sina_latest_comments_spider import SinaLatestCommentsSpider


@pytest.fixture()
def spider() -> SinaLatestCommentsSpider:
    """返回一个用于测试的 Spider 实例（不启动 Scrapy 引擎）。"""
    return SinaLatestCommentsSpider(
        target_date="2026-03-09",
        max_pages=2,
        roll_page_size=10,
        comment_page_size=5,
        max_comment_pages=2,
        include_empty_comments=False,
        lid=2509,
    )
