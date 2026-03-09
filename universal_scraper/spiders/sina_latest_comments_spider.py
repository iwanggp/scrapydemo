from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import scrapy

from universal_scraper.items import ScrapedRecord


UTC_PLUS_8 = timezone(timedelta(hours=8))


class SinaLatestCommentsSpider(scrapy.Spider):
    name = "sina_latest_comments"

    roll_api = "https://feed.mix.sina.com.cn/api/roll/get"
    comment_api = "https://comment.sina.com.cn/page/info"

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "CONCURRENT_REQUESTS": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RETRY_HTTP_CODES": [408, 429, 500, 502, 503, 504],
    }

    def __init__(
        self,
        target_date: str | None = None,
        max_pages: int = 3,
        roll_page_size: int = 50,
        comment_page_size: int = 20,
        max_comment_pages: int = 1,
        include_empty_comments: bool = False,
        lid: int = 2509,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.target_date = (
            datetime.strptime(target_date, "%Y-%m-%d").date()
            if target_date
            else datetime.now(UTC_PLUS_8).date()
        )
        self.max_pages = max(1, int(max_pages))
        self.roll_page_size = max(1, int(roll_page_size))
        self.comment_page_size = max(1, int(comment_page_size))
        self.max_comment_pages = max(1, int(max_comment_pages))
        self.include_empty_comments = bool(include_empty_comments)
        self.lid = int(lid)
        self.pageid = 153

    async def start(self) -> Any:
        for request in self.start_requests():
            yield request

    def start_requests(self) -> Any:
        yield self._build_roll_request(page=1)

    def parse_roll_page(self, response: scrapy.http.Response) -> Any:
        payload = response.json()
        rows = payload.get("result", {}).get("data", [])
        if not isinstance(rows, list):
            self.logger.warning("Unexpected roll payload shape on page %s", response.meta["roll_page"])
            return

        saw_older_article = False

        for row in rows:
            article_date = self._parse_article_date(row.get("ctime"))
            if article_date is None:
                continue

            if article_date < self.target_date:
                saw_older_article = True
                continue

            if article_date != self.target_date:
                continue

            comment_meta = self._parse_comment_id(row.get("commentid", ""))
            if comment_meta is None:
                continue

            article = {
                "article_title": row.get("title"),
                "article_url": row.get("url"),
                "article_wap_url": row.get("wapurl"),
                "article_intro": row.get("intro") or row.get("summary"),
                "article_media_name": row.get("media_name"),
                "article_docid": row.get("docid"),
                "article_oid": row.get("oid"),
                "article_ctime": int(row.get("ctime")),
                "article_published_at": self._format_epoch(row.get("ctime")),
                "article_keywords": row.get("keywords"),
                "article_comment_id": row.get("commentid"),
                "roll_lid": self.lid,
                "roll_page": response.meta["roll_page"],
                "target_date": self.target_date.isoformat(),
                **comment_meta,
            }

            yield self._build_comment_request(article=article, page=1, comments_accumulator=[])

        if saw_older_article:
            self.logger.info(
                "Roll page %s already contains articles older than %s.",
                response.meta["roll_page"],
                self.target_date.isoformat(),
            )
            return

        current_page = int(response.meta["roll_page"])
        if current_page < self.max_pages and rows:
            yield self._build_roll_request(page=current_page + 1)

    def parse_comments(
        self,
        response: scrapy.http.Response,
        article: dict[str, Any],
        page: int,
        comments_accumulator: list[dict[str, Any]],
    ) -> Any:
        payload = response.json().get("result", {})
        count = payload.get("count", {})
        total_comments = int(count.get("total", 0) or 0)
        visible_comments = int(count.get("show", 0) or 0)

        cmntlist = payload.get("cmntlist") or []
        if not isinstance(cmntlist, list):
            cmntlist = []

        comments_accumulator.extend(self._normalize_comments(cmntlist))

        if page < self._max_comment_pages_for_article(visible_comments) and len(cmntlist) == self.comment_page_size:
            yield self._build_comment_request(
                article=article,
                page=page + 1,
                comments_accumulator=comments_accumulator,
            )
            return

        if total_comments == 0 and not self.include_empty_comments:
            return

        item = {
            **article,
            "comment_count_total": total_comments,
            "comment_count_visible": visible_comments,
            "comments_latest": comments_accumulator,
            "comments_latest_json": json.dumps(comments_accumulator, ensure_ascii=False),
            "comments_fetched": len(comments_accumulator),
            "_source_url": article["article_url"],
            "_crawl_target_date": self.target_date.isoformat(),
            "_comment_api": response.url,
            "_comment_pages_fetched": page,
        }
        yield ScrapedRecord(item)

    def _build_comment_request(
        self,
        article: dict[str, Any],
        page: int,
        comments_accumulator: list[dict[str, Any]],
    ) -> scrapy.Request:
        params = {
            "version": 1,
            "format": "json",
            "channel": article["comment_channel"],
            "newsid": article["comment_newsid"],
            "group": article["comment_group"],
            "compress": 0,
            "ie": "utf-8",
            "oe": "utf-8",
            "page": page,
            "page_size": self.comment_page_size,
            "thread": 1,
        }
        return scrapy.Request(
            url=f"{self.comment_api}?{urlencode(params)}",
            callback=self.parse_comments,
            cb_kwargs={
                "article": article,
                "page": page,
                "comments_accumulator": comments_accumulator,
            },
        )

    def _build_roll_request(self, page: int) -> scrapy.Request:
        params = {
            "pageid": self.pageid,
            "lid": self.lid,
            "num": self.roll_page_size,
            "page": page,
        }
        return scrapy.Request(
            url=f"{self.roll_api}?{urlencode(params)}",
            callback=self.parse_roll_page,
            meta={"roll_page": page},
        )

    def _parse_comment_id(self, comment_id: str) -> dict[str, Any] | None:
        parts = [part for part in comment_id.split(":") if part != ""]
        if len(parts) < 2:
            return None

        return {
            "comment_channel": parts[0],
            "comment_newsid": parts[1],
            "comment_group": parts[2] if len(parts) >= 3 else "0",
        }

    def _parse_article_date(self, ctime: Any) -> datetime.date | None:
        try:
            return datetime.fromtimestamp(int(ctime), tz=UTC_PLUS_8).date()
        except (TypeError, ValueError, OSError):
            return None

    def _format_epoch(self, ctime: Any) -> str | None:
        try:
            return datetime.fromtimestamp(int(ctime), tz=UTC_PLUS_8).isoformat()
        except (TypeError, ValueError, OSError):
            return None

    def _normalize_comments(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for row in rows:
            normalized.append(
                {
                    "mid": row.get("mid"),
                    "time": row.get("time"),
                    "nick": row.get("nick"),
                    "uid": row.get("uid"),
                    "area": row.get("area"),
                    "content": row.get("content"),
                    "agree": self._to_int(row.get("agree")),
                    "against": self._to_int(row.get("against")),
                    "reply_count": self._to_int(row.get("count_layer")),
                    "is_hot": row.get("is_hot"),
                    "is_top": row.get("is_top"),
                }
            )
        return normalized

    def _max_comment_pages_for_article(self, visible_comments: int) -> int:
        estimated_pages = max(1, math.ceil(visible_comments / self.comment_page_size))
        return min(self.max_comment_pages, estimated_pages)

    def _to_int(self, value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
