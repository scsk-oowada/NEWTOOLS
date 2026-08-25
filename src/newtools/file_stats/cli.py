"""newtools フォルダ集計CLI エントリポイント。"""

import argparse
from pathlib import Path

from newtools.file_stats.scanner import format_size, scan_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="指定フォルダ内のファイルを拡張子別に集計する")
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path.cwd(),
        help="集計対象のフォルダ (省略時はカレントディレクトリ)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="表示する上位件数 (省略時は全件表示)",
    )
    args = parser.parse_args()

    if not args.path.is_dir():
        print(f"フォルダが見つかりません: {args.path}")
        return

    stats = scan_directory(args.path)

    if not stats:
        print("対象ファイルが見つかりません。")
        return

    rows = sorted(stats.items(), key=lambda item: item[1]["total_size"], reverse=True)
    if args.top is not None:
        rows = rows[: args.top]

    print(f"{'拡張子':<12}{'ファイル数':>10}{'合計サイズ':>12}")
    for extension, entry in rows:
        print(f"{extension:<12}{entry['count']:>10}{format_size(entry['total_size']):>12}")


if __name__ == "__main__":
    main()
