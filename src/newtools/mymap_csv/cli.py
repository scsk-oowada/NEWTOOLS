"""座標リストからGoogle My Maps用インポートCSVを作成するCLIエントリポイント。"""

import argparse
from pathlib import Path

from newtools.mymap_csv.parser import parse_text
from newtools.mymap_csv.writer import write_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="座標リスト（緯度,経度 または 緯度,経度,地名）からGoogle My Maps用のインポートCSVを作成する"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="座標リストのテキストファイル (1行1件、緯度,経度 または 緯度,経度,地名)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="出力するCSVファイルのパス (省略時は入力ファイル名に基づく)",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"入力ファイルが見つかりません: {args.input}")
        return

    text = args.input.read_text(encoding="utf-8")

    try:
        pins = parse_text(text)
    except ValueError as exc:
        print(f"入力の解析に失敗しました: {exc}")
        return

    if not pins:
        print("座標が1件も見つかりませんでした。")
        return

    output_path = args.output or args.input.with_suffix(".csv")
    write_csv(pins, output_path)
    print(f"{len(pins)}件のピンを出力しました: {output_path}")
    print("Google My Mapsで「インポート」からこのCSVファイルを読み込んでください。")


if __name__ == "__main__":
    main()
