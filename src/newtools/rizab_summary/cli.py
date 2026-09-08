"""りざぶ郎の会議室予約を予約者ごとに集計するCLIエントリポイント。"""

import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

from newtools.rizab_summary.report import format_report
from newtools.rizab_summary.scraper import login, scrape_days

GROUP_ID_ENV = "RIZABU_GROUP_ID"
PASSWORD_ENV = "RIZABU_PASSWORD"


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def main() -> None:
    parser = argparse.ArgumentParser(description="りざぶ郎の会議室予約（宇都宮・大宮）を予約者ごとに集計する")
    parser.add_argument(
        "--start",
        type=_parse_date,
        default=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        help="集計開始日 (YYYY-MM-DD)。省略時は本日",
    )
    parser.add_argument(
        "--end",
        type=_parse_date,
        help="集計終了日 (YYYY-MM-DD、この日を含む)。省略時は開始日から7日後",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="出力するTXTファイルのパス (省略時は rizab_schedule_<開始日>_<終了日>.txt)",
    )
    parser.add_argument(
        "--register-outlook",
        action="store_true",
        help="取得した予約をOutlook予定表にも登録する",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="ブラウザ画面を表示して実行する (動作確認用)",
    )
    parser.add_argument(
        "--debug-pause",
        action="store_true",
        help="ログイン後、予約取得を始める前にPlaywright Inspectorで一時停止する (動作確認用、--headedと併用)",
    )
    args = parser.parse_args()

    group_id = os.environ.get(GROUP_ID_ENV)
    password = os.environ.get(PASSWORD_ENV)
    if not group_id or not password:
        print(f"環境変数 {GROUP_ID_ENV} と {PASSWORD_ENV} を設定してください。")
        return

    start = args.start.date()
    end = (args.end.date() if args.end else start + timedelta(days=7))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        page = browser.new_page()
        login(page, group_id, password)
        if args.debug_pause:
            page.pause()
        reservations = scrape_days(page, group_id, start, end)
        browser.close()

    output_path = args.output or Path(f"rizab_schedule_{start.isoformat()}_{end.isoformat()}.txt")
    output_path.write_text(format_report(reservations), encoding="utf-8")
    print(f"予約者ごとの一覧を出力しました: {output_path}")

    if args.register_outlook:
        from newtools.rizab_summary.outlook_register import register_events

        created, skipped = register_events(reservations)
        print(f"Outlook予定表に登録しました（新規 {created} 件 / 既存のためスキップ {skipped} 件）。")


if __name__ == "__main__":
    main()
