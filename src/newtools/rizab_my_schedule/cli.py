"""りざぶ郎にログインし、自分の会議室予約を取得してOutlook予定表に登録するCLI。

exe化してダブルクリックするだけで実行できるようにすることを想定している。
初回実行時にりざぶ郎のログイン情報を入力させ、以降はその設定を使って
確認なしで自動実行する。
"""

import os
import traceback
from datetime import date, timedelta

# exe化（PyInstaller）した場合、Playwrightのドライバがexe展開先の一時ディレクトリ
# 相対でブラウザを探しに行ってしまい見つからないため、実行環境に
# `playwright install chromium` でインストールされたブラウザの場所を明示する。
os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH", os.path.expandvars(r"%LOCALAPPDATA%\ms-playwright")
)

from playwright.sync_api import sync_playwright

from newtools.rizab_my_schedule.config import load_or_create_config
from newtools.rizab_my_schedule.outlook_register import register_events
from newtools.rizab_summary.models import is_target_room
from newtools.rizab_summary.scraper import login, scrape_days

FETCH_DAYS = 30


def _make_should_include(my_name: str):
    def _should_include(item_name: str, reserver: str) -> bool:
        return is_target_room(item_name) and reserver == my_name

    return _should_include


def run() -> None:
    config = load_or_create_config()

    start = date.today()
    end = start + timedelta(days=FETCH_DAYS - 1)

    print(f"{config.my_name} さんの予約を {start} から {end} まで取得します...")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        login(page, config.group_id, config.password)
        reservations = scrape_days(
            page, config.group_id, start, end, _make_should_include(config.my_name)
        )
        browser.close()

    print(f"{len(reservations)} 件の予約を取得しました。")

    created, skipped = register_events(reservations)
    print(f"Outlook予定表に登録しました（新規 {created} 件 / 既存のためスキップ {skipped} 件）。")


def main() -> None:
    try:
        run()
    except Exception:
        traceback.print_exc()
        print("\nエラーが発生しました。上記の内容を確認してください。")
    input("\n完了しました。Enterキーを押すと終了します。")


if __name__ == "__main__":
    main()
