"""Playwrightでりざぶ郎にログインし、会議室予約を取得するモジュール。

りざぶ郎は予約枠をcanvas風にHTML要素で描画するため、一覧画面から直接
表形式のデータを読み取ることはできない。そのため、日ごとに表示されている
予約枠（.sche要素）を1件ずつクリックして開く詳細ポップアップ
（日時・対象・予約者などが記載された画面）から情報を読み取る。
"""

from datetime import date, timedelta

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from newtools.rizab_summary.models import Reservation, is_target_room, parse_reservation

LOGIN_URL = "https://www.r326.com/b/login.aspx"
MAIN_URL_TEMPLATE = "https://www.r326.com/b/main.aspx?g={group_id}"

_POPUP_LABELS = ("日時", "対象", "予約者（登録者）")


def login(page: Page, group_id: str, password: str) -> None:
    """りざぶ郎にログインし、指定した予約表を開く。"""
    page.goto(MAIN_URL_TEMPLATE.format(group_id=group_id))

    password_field = page.locator('input[type="password"]')
    if password_field.count() == 0:
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


def _read_popup_fields(page: Page, sche_box) -> dict[str, str] | None:
    box = sche_box.bounding_box()
    if box is None:
        print(f"  -> bounding_boxが取得できずスキップ: {sche_box.inner_text()!r}")
        return None

    center_x = box["x"] + box["width"] / 2
    center_y = box["y"] + box["height"] / 2

    # 1回目のクリックで予約枠が選択状態になり、選択済みの状態で2回目のクリックを
    # 行うと詳細ポップアップが開く。
    page.mouse.click(center_x, center_y)
    page.wait_for_timeout(300)
    try:
        with page.expect_popup(timeout=8000) as popup_info:
            page.mouse.click(center_x, center_y)
        popup = popup_info.value
    except PlaywrightTimeoutError:
        print(f"  -> ポップアップが開きませんでした（座標: {center_x:.0f}, {center_y:.0f}）。")
        return None
    popup.wait_for_load_state("networkidle")

    fields: dict[str, str] = {}
    rows = popup.locator("tr")
    for i in range(rows.count()):
        cells = rows.nth(i).locator("td")
        if cells.count() < 2:
            continue
        label = cells.nth(0).inner_text().strip()
        value = cells.nth(1).inner_text().strip()
        if label in _POPUP_LABELS:
            fields[label] = value

    popup.close()

    if not all(label in fields for label in _POPUP_LABELS):
        return None
    return fields


def scrape_current_day(page: Page) -> list[Reservation]:
    """現在表示中の1日分の会議室予約を取得する。"""
    reservations = []
    boxes = page.locator(".sche")
    count = boxes.count()
    print(f"予約枠を {count} 件検出しました。")
    for i in range(count):
        box = boxes.nth(i)
        print(f"  [{i}] {box.inner_text()!r} をクリックします...")
        fields = _read_popup_fields(page, box)
        if fields is None:
            print("  -> 詳細情報を取得できませんでした。")
            continue
        if not is_target_room(fields["対象"]):
            print(f"  -> 対象外のアイテムのためスキップ: {fields['対象']!r}")
            continue
        reservations.append(parse_reservation(fields))
    return reservations


def go_to_next_day(page: Page) -> None:
    page.evaluate("OnButtonUndercal3()")
    page.wait_for_load_state("networkidle")


def go_to_prev_day(page: Page) -> None:
    page.evaluate("OnButtonUndercal1()")
    page.wait_for_load_state("networkidle")


def scrape_days(page: Page, start: date, end: date) -> list[Reservation]:
    """ログイン済みのpageに対し、指定期間（startからendを含む）の会議室予約を取得する。"""
    today = date.today()
    delta_from_today = (start - today).days
    for _ in range(delta_from_today):
        go_to_next_day(page)
    for _ in range(-delta_from_today):
        go_to_prev_day(page)

    reservations: list[Reservation] = []
    num_days = (end - start).days + 1
    for day_offset in range(num_days):
        reservations.extend(scrape_current_day(page))
        if day_offset < num_days - 1:
            go_to_next_day(page)

    return reservations


def scrape_range(page: Page, group_id: str, password: str, start: date, end: date) -> list[Reservation]:
    """指定期間（startからendを含む）の会議室予約を取得する。"""
    login(page, group_id, password)
    return scrape_days(page, start, end)
