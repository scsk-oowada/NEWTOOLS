"""scanner モジュールのテスト。"""

from newtools.file_stats.scanner import format_size, scan_directory


def test_scan_directory(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "b.txt").write_text("world!!")
    (tmp_path / "c.log").write_text("x")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "d.txt").write_text("y")

    stats = scan_directory(tmp_path)

    assert stats[".txt"]["count"] == 3
    assert stats[".txt"]["total_size"] == len("hello") + len("world!!") + len("y")
    assert stats[".log"]["count"] == 1
    assert stats[".log"]["total_size"] == len("x")


def test_format_size():
    assert format_size(500) == "500.0B"
    assert format_size(2048) == "2.0KB"
