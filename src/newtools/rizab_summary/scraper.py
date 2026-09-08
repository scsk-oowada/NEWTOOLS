"""Playwrightでりざぶ郎にログインし、内部APIから会議室予約を取得するモジュール。

りざぶ郎の予約表画面はキャンバス風にHTML要素を絶対座標で描画するため、画面表示
から直接データを読み取る方式は不安定（要素をクリックしてポップアップを開く必要が
あり、遅く、取りこぼしのリスクもある）。そのため、画面が内部で呼び出している
Ajax API（main.aspxの日付ジャンプ、a.aspxのGetItems/GetSchedules）を直接呼び出し、
タブ区切りテキストとして返る確実な構造化データから予約情報を取得する。

これらのAPIはりざぶ郎の公開仕様ではなく、画面のJavaScript（main.js）を解析して
判明したもの。ログイン後のHTMLに埋め込まれる `statusId` をセッション状態として
やり取りする必要がある。
"""

import re
from collections.abc import Callable
from datetime import date, timedelta

from playwright.sync_api import Page

from newtools.rizab_summary.models import Reservation, is_target_room, parse_schedule_row

LOGIN_URL = "https://www.r326.com/b/login.aspx"
MAIN_URL_TEMPLATE = "https://www.r326.com/b/main.aspx?g={group_id}"
API_URL = "https://www.r326.com/b/a.aspx"

_STATUS_ID_RE = re.compile(r'var statusId="([^"]+)"')
_SEL_ITEM_RE = re.compile(r"selItem=(\d+)")

# 対象アイテム名・予約者名を受け取り、集計対象に含めるかどうかを返す関数の型
ShouldInclude = Callable[[str, str], bool]


def login(page: Page, group_id: str, password: str) -> None:
    """りざぶ郎にログインし、指定した予約表を開く。"""
    page.goto(MAIN_URL_TEMPLATE.format(group_id=group_id))

    password_field = page.locator('input[type="password"]')
    if password_field.count() == 0:
        if "r326.com" not in page.url:
            # 会社のSSO（Microsoft Entra ID等）のログイン画面に割り込まれた状態。
            # 短時間に何度もログインを試みた場合などに発生することがある。
            raise ValueError(
                f"りざぶ郎以外のページにリダイレクトされました（{page.url}）。"
                "会社のSSOログインが求められている可能性があります。"
                "時間を置いてから再実行してください。"
            )
        return  # 既にログイン済みの予約表が開いている

    password_field.first.fill(password)

    login_button = page.locator(
        'input[type="image"][alt*="ログイン"], input[type="submit"], button:has-text("ログイン")'
    )
    if login_button.count() > 0:
        login_button.first.click()
    else:
        password_field.first.press("Enter")

    page.wait_for_load_state("networkidle")


def _extract_status_id(html: str) -> str:
    match = _STATUS_ID_RE.search(html)
    if not match:
        raise ValueError("ページからstatusIdを取得できませんでした。ログインに失敗している可能性があります。")
    return match.group(1)


def _extract_sel_item(html: str) -> str:
    match = _SEL_ITEM_RE.search(html)
    if not match:
        raise ValueError("ページからselItemを取得できませんでした。")
    return match.group(1)


def fetch_items(page: Page, status_id: str) -> dict[str, str]:
    """会議室・アイテムのID→名称マッピングを取得する（GetItems API）。"""
    response = page.request.post(API_URL, form={"status": status_id, "c": "GetItems"})
    items: dict[str, str] = {}
    for line in response.text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0] == "m":
            items[parts[1]] = parts[2]
    return items


def jump_to_date(page: Page, group_id: str, status_id: str, sel_item: str, target: date) -> str:
    """予約表を指定日付に直接移動し、新しいstatusIdを返す。"""
    date_text = f"{target.year}/{target.month}/{target.day}"
    response = page.request.post(
        MAIN_URL_TEMPLATE.format(group_id=group_id),
        form={"date": date_text, "status": status_id, "itemid": sel_item},
    )
    return _extract_status_id(response.text())


def fetch_schedules_text(page: Page, status_id: str) -> str:
    """現在の表示日の予約一覧をタブ区切りテキストで取得する（GetSchedules API）。"""
    response = page.request.post(
        API_URL, form={"status": status_id, "c": "GetSchedules", "hv": "1"}
    )
    return response.text()


def parse_schedules_text(text: str, items: dict[str, str], should_include: ShouldInclude) -> list[Reservation]:
    """GetSchedules APIのレスポンスをReservationのリストに変換する。"""
    reservations: list[Reservation] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 10 or parts[0] != "s":
            continue
        item_name = items.get(parts[2], "")
        reserver = parts[9].strip()
        if not should_include(item_name, reserver):
            continue
        reservations.append(parse_schedule_row(parts, item_name))
    return reservations


def _default_should_include(item_name: str, reserver: str) -> bool:
    return is_target_room(item_name)


def scrape_days(
    page: Page,
    group_id: str,
    start: date,
    end: date,
    should_include: ShouldInclude = _default_should_include,
) -> list[Reservation]:
    """ログイン済みのpageに対し、指定期間（startからendを含む）の会議室予約を取得する。"""
    html = page.content()
    status_id = _extract_status_id(html)
    sel_item = _extract_sel_item(html)

    items = fetch_items(page, status_id)

    reservations: list[Reservation] = []
    num_days = (end - start).days + 1
    for day_offset in range(num_days):
        target = start + timedelta(days=day_offset)
        status_id = jump_to_date(page, group_id, status_id, sel_item, target)
        schedules_text = fetch_schedules_text(page, status_id)
        reservations.extend(parse_schedules_text(schedules_text, items, should_include))

    return reservations


def scrape_range(
    page: Page,
    group_id: str,
    password: str,
    start: date,
    end: date,
    should_include: ShouldInclude = _default_should_include,
) -> list[Reservation]:
    """指定期間（startからendを含む）の会議室予約を取得する。"""
    login(page, group_id, password)
    return scrape_days(page, group_id, start, end, should_include)
