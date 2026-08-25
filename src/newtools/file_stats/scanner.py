"""指定フォルダを再帰的に走査し、拡張子別のファイル数・合計サイズを集計する。"""

from pathlib import Path

_SIZE_UNITS = ("B", "KB", "MB", "GB", "TB")


def scan_directory(root: Path) -> dict[str, dict[str, int]]:
    """root配下を再帰的に走査し、拡張子別の集計結果（件数・合計サイズ）を返す。"""
    stats: dict[str, dict[str, int]] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        extension = path.suffix.lower() or "(拡張子なし)"
        entry = stats.setdefault(extension, {"count": 0, "total_size": 0})
        entry["count"] += 1
        entry["total_size"] += path.stat().st_size
    return stats


def format_size(size: int) -> str:
    """バイト数を読みやすい単位（B/KB/MB/...）の文字列に変換する。"""
    value = float(size)
    for unit in _SIZE_UNITS:
        if value < 1024 or unit == _SIZE_UNITS[-1]:
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}{_SIZE_UNITS[-1]}"
