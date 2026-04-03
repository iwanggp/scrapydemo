"""针对 run_sina_latest_comments 入口脚本的单元测试。"""
from __future__ import annotations

from pathlib import Path
from run_sina_latest_comments import infer_feed_format


class TestInferFeedFormat:
    def test_csv_suffix(self):
        assert infer_feed_format(Path("out.csv"), None) == "csv"

    def test_json_suffix(self):
        assert infer_feed_format(Path("out.json"), None) == "json"

    def test_jsonl_suffix_returns_jsonlines(self):
        assert infer_feed_format(Path("out.jsonl"), None) == "jsonlines"

    def test_unknown_suffix_defaults_to_jsonlines(self):
        assert infer_feed_format(Path("out.txt"), None) == "jsonlines"

    def test_no_suffix_defaults_to_jsonlines(self):
        assert infer_feed_format(Path("outputfile"), None) == "jsonlines"

    def test_explicit_csv_overrides_jsonl_suffix(self):
        assert infer_feed_format(Path("out.jsonl"), "csv") == "csv"

    def test_explicit_json_overrides_csv_suffix(self):
        assert infer_feed_format(Path("out.csv"), "json") == "json"

    def test_uppercase_csv_suffix(self):
        assert infer_feed_format(Path("out.CSV"), None) == "csv"

    def test_uppercase_json_suffix(self):
        assert infer_feed_format(Path("out.JSON"), None) == "json"
