"""Google My Mapsへのログイン状態を保存し、CSVをインポートして地図を表示するモジュール。

Google My MapsのUIには公式のAPIも自動テスト用の仕組みもなく、構造やラベルが
将来のUI変更で変わる可能性がある。そのためここでの要素の特定は、アイコン
ボタンのtitle属性やボタンのテキストなど、比較的変わりにくい情報を優先して
使っている。インポート後に表示される列選択ウィザードは自動でクリックを試みる
が、UI変更などで想定通りに進まなかった場合も例外にはせず、ブラウザを開いた
まま呼び出し元に処理を返す。ユーザーが表示されたブラウザで残りの操作を
手動で確認・完了できるようにするためである。
"""

from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

MYMAPS_TOP_URL = "https://www.google.com/maps/d/u/0/"
DEFAULT_STORAGE_STATE_PATH = Path.home() / ".newtools" / "mymap_csv_session.json"

_IMPORT_WIZARD_BUTTON_TEXTS = ("続行", "完了")


def save_login_session(storage_state_path: Path = DEFAULT_STORAGE_STATE_PATH) -> None:
    """ブラウザを表示し、ユーザーが手動で行ったGoogleへのログイン状態を保存する。"""
    storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(MYMAPS_TOP_URL)

        print("表示されたブラウザでGoogleアカウントにログインしてください。")
        print("My Mapsの地図一覧が表示されたら、このターミナルに戻ってEnterキーを押してください。")
        input()

        context.storage_state(path=str(storage_state_path))
        browser.close()

    print(f"ログイン状態を保存しました: {storage_state_path}")


def _add_layer(page: Page) -> None:
    """マップ編集画面で新しいレイヤーを追加する。"""
    page.get_by_title("レイヤーを追加").click()
    page.wait_for_timeout(1000)


def _click_import_button(page: Page) -> None:
    """追加した（一覧の末尾にある）レイヤーの「インポート」ボタンをクリックする。"""
    page.get_by_title("インポート").last.click()


def _click_through_import_wizard(page: Page) -> None:
    """列選択ウィザードの「続行」「完了」ボタンを可能な範囲で自動的にクリックする。"""
    for button_text in _IMPORT_WIZARD_BUTTON_TEXTS:
        try:
            page.get_by_role("button", name=button_text).click(timeout=5000)
            page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            break


def import_csv_to_map(
    map_url: str,
    csv_path: Path,
    storage_state_path: Path = DEFAULT_STORAGE_STATE_PATH,
) -> None:
    """保存済みのログイン状態で既存のMy Mapsを開き、CSVを新規レイヤーとしてインポートする。

    インポート完了後もブラウザは閉じず、ユーザーがEnterキーを押すまで地図を
    表示したままにする。
    """
    if not storage_state_path.is_file():
        raise RuntimeError(
            f"ログイン状態が保存されていません。先に `mymap-csv --login` を実行してください: {storage_state_path}"
        )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(storage_state_path))
        page = context.new_page()
        page.goto(map_url)
        page.wait_for_load_state("networkidle")

        _add_layer(page)
        with page.expect_file_chooser() as file_chooser_info:
            _click_import_button(page)
        file_chooser_info.value.set_files(str(csv_path))

        page.wait_for_timeout(2000)
        _click_through_import_wizard(page)

        print("地図を表示しました。内容を確認したら、このターミナルに戻ってEnterキーを押すとブラウザを閉じます。")
        print("（列選択などのウィザードが途中で止まっている場合は、表示されたブラウザで操作を完了してください）")
        input()

        browser.close()
