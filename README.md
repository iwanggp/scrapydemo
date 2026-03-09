# Sina News Comments Scraper

A standalone Scrapy project for collecting the latest public comments from Sina's latest news feed.

## What It Does

- Pulls the latest articles from Sina's public roll feed API
- Filters articles by a target date in UTC+08:00
- Resolves each article's public comment identifier
- Fetches the latest public comments from Sina's public comment API
- Exports data as `jsonlines`, `json`, or `csv`

## Project Layout

```text
sina-news-comments-project/
  .github/workflows/
  tests/
  requirements.txt
  scrapy.cfg
  run_sina_latest_comments.py
  universal_scraper/
    items.py
    settings.py
    spiders/
      sina_latest_comments_spider.py
```

## Install

```powershell
cd D:\deeplearningProjects\sina-news-comments-project
python -m pip install -r requirements.txt
```

## Run

Export to JSONL:

```powershell
python run_sina_latest_comments.py --date 2026-03-09 --output outputs\sina_2026-03-09.jsonl
```

Export to CSV:

```powershell
python run_sina_latest_comments.py --date 2026-03-09 --max-pages 1 --roll-page-size 50 --comment-page-size 20 --max-comment-pages 1 --output outputs\sina_2026-03-09.csv --format csv
```

## Key Arguments

- `--date`: target date in `YYYY-MM-DD`, defaults to today in UTC+08:00
- `--max-pages`: how many Sina roll-feed pages to scan
- `--roll-page-size`: how many articles to request per roll-feed page
- `--comment-page-size`: how many comments to fetch per article page
- `--max-comment-pages`: maximum comment pages per article
- `--with-empty-comments`: keep articles even when comment count is 0
- `--format`: `jsonlines`, `json`, or `csv`

## Output

Each record contains article metadata and a `comments_latest` array. When exporting to CSV, the same comment payload is also flattened into `comments_latest_json` for easier downstream processing.

## CI/CD

- `CI`: installs dependencies, runs a syntax check, and executes unit tests
- `CD`: runs the scraper on a schedule or on demand, then uploads the resulting dataset as a GitHub Actions artifact

## Notes

- This project targets public endpoints only.
- Actual GitHub repository creation and push still require GitHub authentication on the machine or a token-backed remote.
