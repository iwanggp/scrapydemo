from __future__ import annotations

import argparse
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

from universal_scraper.spiders.sina_latest_comments_spider import SinaLatestCommentsSpider


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Crawl Sina roll news articles and their latest public comments."
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Target date in YYYY-MM-DD. Defaults to today in UTC+08:00.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/sina_latest_comments.jsonl"),
        help="Output path for exported records.",
    )
    parser.add_argument(
        "--format",
        choices=("jsonlines", "json", "csv"),
        default=None,
        help="Export format. Defaults to inferring from the output suffix.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=3,
        help="Maximum roll-feed pages to fetch.",
    )
    parser.add_argument(
        "--roll-page-size",
        type=int,
        default=50,
        help="How many news items to request per roll-feed page.",
    )
    parser.add_argument(
        "--comment-page-size",
        type=int,
        default=20,
        help="How many latest comments to request per article page.",
    )
    parser.add_argument(
        "--max-comment-pages",
        type=int,
        default=1,
        help="How many comment pages to fetch per article.",
    )
    parser.add_argument(
        "--with-empty-comments",
        action="store_true",
        help="Keep articles even if the public comment count is 0.",
    )
    parser.add_argument(
        "--lid",
        type=int,
        default=2509,
        help="Sina roll feed lid. Default 2509 is the all-channel latest feed.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Scrapy log level. Example: INFO, DEBUG, WARNING.",
    )
    return parser


def infer_feed_format(output_path: Path, explicit_format: str | None) -> str:
    if explicit_format:
        return explicit_format

    suffix = output_path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    return "jsonlines"


def build_settings(output_path: Path, feed_format: str, log_level: str) -> Settings:
    settings = Settings(get_project_settings())
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    settings.set("LOG_LEVEL", log_level.upper())
    settings.set(
        "FEEDS",
        {
            str(output_path): {
                "format": feed_format,
                "encoding": "utf-8",
                "overwrite": True,
            }
        },
    )
    if feed_format == "csv":
        settings.set(
            "FEED_EXPORT_FIELDS",
            [
                "article_title",
                "article_url",
                "article_published_at",
                "article_media_name",
                "article_docid",
                "article_comment_id",
                "comment_count_total",
                "comment_count_visible",
                "comments_fetched",
                "comments_latest_json",
                "target_date",
                "roll_lid",
                "roll_page",
                "_comment_pages_fetched",
                "_comment_api",
            ],
        )
    settings.set("ROBOTSTXT_OBEY", True)
    settings.set("CONCURRENT_REQUESTS", 2)
    settings.set("DOWNLOAD_DELAY", 1.0)
    settings.set("AUTOTHROTTLE_ENABLED", True)

    return settings


def main() -> None:
    args = build_arg_parser().parse_args()
    feed_format = infer_feed_format(args.output, args.format)
    settings = build_settings(args.output, feed_format, args.log_level)

    process = CrawlerProcess(settings=settings)
    process.crawl(
        SinaLatestCommentsSpider,
        target_date=args.date,
        max_pages=args.max_pages,
        roll_page_size=args.roll_page_size,
        comment_page_size=args.comment_page_size,
        max_comment_pages=args.max_comment_pages,
        include_empty_comments=args.with_empty_comments,
        lid=args.lid,
    )
    process.start()


if __name__ == "__main__":
    main()
