"""座標リストからGoogle My Maps用インポートCSVを作成するCLIエントリポイント。"""

import argparse
import os
from pathlib import Path

from newtools.mymap_csv.parser import parse_text
from newtools.mymap_csv.writer import write_csv

MAP_URL_ENV = "MYMAP_URL"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="座標リスト（緯度,経度 または 緯度,経度,地名）からGoogle My Maps用のインポートCSVを作成する"
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=None,
        help="座標リストのテキストファイル (1行1件、緯度,経度 または 緯度,経度,地名)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="出力するCSVファイルのパス (省略時は入力ファイル名に基づく)",
    )
    parser.add_argument(
        "--map-url",
        type=str,
        default=os.environ.get(MAP_URL_ENV),
        help=(
            "CSVをインポートする既存のGoogle My MapsのURL "
            f"(省略時は環境変数 {MAP_URL_ENV} を使用)。指定すると、CSV作成後に"
            "ブラウザでその地図を開き、新しいレイヤーとしてCSVをインポートして表示する"
        ),
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="Googleへ手動でログインし、その状態を保存する (--map-url を使う前に一度だけ実行する)",
    )
    args = parser.parse_args()

    if args.login:
        from newtools.mymap_csv.browser import save_login_session

        save_login_session()
        return

    if args.input is None:
        parser.error("input（座標リストのテキストファイル）を指定してください。")

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

    if not args.map_url:
        print("Google My Mapsで「インポート」からこのCSVファイルを読み込んでください。")
        return

    from newtools.mymap_csv.browser import import_csv_to_map

    try:
        import_csv_to_map(args.map_url, output_path)
    except RuntimeError as exc:
        print(str(exc))


if __name__ == "__main__":
    main()
