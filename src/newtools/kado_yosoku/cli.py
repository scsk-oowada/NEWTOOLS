"""newtools 稼働率予測CLI エントリポイント。"""

import argparse
from pathlib import Path

from newtools.kado_yosoku.forecast import forecast_kadoritsu
from newtools.kado_yosoku.reader import read_monthly_records
from newtools.kado_yosoku.writer import append_forecast_sheet


def main() -> None:
    parser = argparse.ArgumentParser(
        description="フレックス管理表（Excel）の稼働率履歴から翌月の稼働率を予測する"
    )
    parser.add_argument("path", type=Path, help="対象のExcelファイル")
    parser.add_argument(
        "--sheets",
        default="8月,9月,10月",
        help="集計対象シート名をカンマ区切り・時系列順で指定する (既定: 8月,9月,10月)",
    )
    parser.add_argument(
        "--target-label",
        default="11月",
        help="予測対象月の表示ラベル (既定: 11月)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="予測シートを追加した新しいExcelファイルの保存先 (省略時は画面表示のみ)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="--output の保存先が既に存在する場合でも上書きする",
    )
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"ファイルが見つかりません: {args.path}")
        return

    if args.output is not None and args.output.exists() and not args.force:
        print(f"保存先が既に存在します（上書きするには --force を指定）: {args.output}")
        return

    sheet_order = [s.strip() for s in args.sheets.split(",") if s.strip()]
    monthly_records = read_monthly_records(args.path, sheet_order)
    result = forecast_kadoritsu(monthly_records, sheet_order)

    header = "氏名".ljust(10) + "".join(f"{s:>10}" for s in sheet_order) + f"{args.target_label + '予測':>12}"
    print(header)
    for name, data in result["per_employee"].items():
        history_str = "".join(f"{h * 100:>9.1f}%" for h in data["history"])
        print(f"{name:<10}{history_str}{data['predicted'] * 100:>11.1f}%")

    print()
    print(f"チーム全体の{args.target_label}平均稼働率予測: {result['team_average_predicted'] * 100:.1f}%")

    if args.output is not None:
        append_forecast_sheet(args.path, sheet_order, args.target_label, args.output)
        print(f"\n「{args.target_label}」シートを追加したファイルを保存しました: {args.output}")


if __name__ == "__main__":
    main()
