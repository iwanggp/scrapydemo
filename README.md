# Sina News Comments Scraper

一个基于 Scrapy 的独立爬虫项目，用于采集新浪滚动新闻的文章元数据及最新公开评论。

## 功能简介

- 从新浪公开 Roll Feed API 拉取指定日期的最新新闻文章
- 按 UTC+08:00 时区过滤目标日期的文章
- 解析每篇文章的评论标识符，并调用公开评论 API 获取最新评论
- 支持导出为 `jsonlines`、`json`、`csv` 三种格式
- 内置自动限速（AutoThrottle）、延迟控制与 robots.txt 遵守

## 项目结构

```text
scrapydemo/
├── .github/
│   └── workflows/         # CI/CD 工作流（自动测试 & 定时采集）
├── tests/
│   ├── conftest.py        # 共享测试 fixtures
│   ├── test_sina_spider.py  # Spider 核心逻辑单元测试
│   └── test_sina_runner.py  # 入口脚本单元测试
├── universal_scraper/
│   ├── items.py
│   ├── settings.py
│   └── spiders/
│       └── sina_latest_comments_spider.py
├── run_sina_latest_comments.py  # 命令行入口
├── requirements.txt
├── pyproject.toml
└── scrapy.cfg
```

## 安装

```bash
pip install -r requirements.txt
```

## 快速上手

### 采集今天的文章与评论（默认输出 JSONL）

```bash
python run_sina_latest_comments.py
```

### 采集指定日期，输出 JSONL

```bash
python run_sina_latest_comments.py --date 2026-03-09 --output outputs/sina_2026-03-09.jsonl
```

### 采集指定日期，输出 CSV

```bash
python run_sina_latest_comments.py \
  --date 2026-03-09 \
  --output outputs/sina_2026-03-09.csv \
  --format csv
```

### 完整参数示例

```bash
python run_sina_latest_comments.py \
  --date 2026-03-09 \
  --max-pages 3 \
  --roll-page-size 50 \
  --comment-page-size 20 \
  --max-comment-pages 2 \
  --with-empty-comments \
  --log-level DEBUG \
  --output outputs/sina_full.jsonl
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--date` | 今天 (UTC+08:00) | 目标日期，格式 `YYYY-MM-DD` |
| `--output` | `outputs/sina_latest_comments.jsonl` | 输出文件路径 |
| `--format` | 根据后缀推断 | `jsonlines` / `json` / `csv` |
| `--max-pages` | `3` | 最多抓取多少页 Roll Feed |
| `--roll-page-size` | `50` | 每页 Roll Feed 请求的文章数 |
| `--comment-page-size` | `20` | 每篇文章每页请求的评论数 |
| `--max-comment-pages` | `1` | 每篇文章最多抓取的评论页数 |
| `--with-empty-comments` | False | 保留评论数为 0 的文章 |
| `--lid` | `2509` | 新浪 Roll Feed 频道 ID |
| `--log-level` | `INFO` | Scrapy 日志级别 |

## 输出字段说明

| 字段 | 说明 |
|------|------|
| `article_title` | 文章标题 |
| `article_url` | 文章链接 |
| `article_published_at` | 发布时间（ISO 8601，UTC+08:00）|
| `article_media_name` | 媒体来源 |
| `article_docid` | 文章 DocID |
| `comment_count_total` | 总评论数 |
| `comment_count_visible` | 可见评论数 |
| `comments_fetched` | 实际抓取评论数 |
| `comments_latest_json` | 最新评论（JSON 字符串，CSV 友好）|
| `target_date` | 目标采集日期 |

## 运行测试

```bash
pip install pytest
pytest tests/ -v
```

## CI/CD

- **CI**：每次 Push 自动安装依赖、运行单元测试（`pytest`）
- **CD**：可按计划或手动触发，运行爬虫并将数据集上传为 GitHub Actions Artifact

## 注意事项

- 本项目仅访问新浪**公开 API**，遵守 `robots.txt` 规则
- 内置请求延迟与 AutoThrottle，避免对服务器造成过大压力
- 敏感信息（如 Cookie、Token）请通过环境变量传入，切勿硬编码到代码中
