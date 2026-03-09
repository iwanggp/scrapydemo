from pathlib import Path

from run_sina_latest_comments import infer_feed_format


def test_infer_feed_format_from_suffix() -> None:
    assert infer_feed_format(Path("out.csv"), None) == "csv"
    assert infer_feed_format(Path("out.json"), None) == "json"
    assert infer_feed_format(Path("out.jsonl"), None) == "jsonlines"


def test_infer_feed_format_explicit_override() -> None:
    assert infer_feed_format(Path("out.jsonl"), "csv") == "csv"
