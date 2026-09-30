"""りざぶ郎にログインし、自分の会議室予約を取得してOutlook予定表に登録するCLI。

exe化してダブルクリックするだけで実行できるようにすることを想定している。
初回実行時にりざぶ郎のログイン情報を入力させ、以降はその設定を使って
確認なしで自動実行する。
"""

import msvcrt
import os
import re
import traceback
from datetime import date, timedelta

from playwright.sync_api import APIRequestContext, sync_playwright

from newtools.rizab_my_schedule.config import delete_config, load_or_create_config
from newtools.rizab_my_schedule.outlook_register import register_events
from newtools.rizab_summary.models import Reservation, format_date_jp, is_target_room
from newtools.rizab_summary.scraper import (
    MAIN_URL_TEMPLATE,
    InvalidCredentialsError,
    scrape_days,
)

FETCH_DAYS = 30

_INPUT_TAG_RE = re.compile(r"<input\b[^>]*>", re.IGNORECASE)
_INPUT_ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


class _HttpPage:
    """scraper.scrape_daysが必要とするPageのAPI（.content()と.request）だけを
    提供する軽量なラッパー。ブラウザを起動せずAPIRequestContextで完結させるために使う。
    """

    def __init__(self, request_context: APIRequestContext, html: str):
        self.request = request_context
        self._html = html

    def content(self) -> str:
        return self._html


def _parse_form_fields(html: str) -> dict[str, str]:
    """HTML中の<input>タグから、チェックボックス・ラジオ・イメージボタンを除いた
    name=valueの組を取り出す（りざぶ郎のASP.NETログインフォームを再送信するため）。
    """
    fields: dict[str, str] = {}
    for tag in _INPUT_TAG_RE.findall(html):
        attrs = dict(_INPUT_ATTR_RE.findall(tag))
        name = attrs.get("name")
        if not name:
            continue
        if attrs.get("type", "text").lower() in ("checkbox", "radio", "image"):
            continue
        fields[name] = attrs.get("value", "")
    return fields


def _login_via_http(request_context: APIRequestContext, group_id: str, password: str) -> str:
    """ブラウザを起動せず、HTTPリクエストのみでりざぶ郎にログインする。

    りざぶ郎の予約データ取得自体はAjax APIへの直接リクエストで完結するため、
    ログインもASP.NETのログインフォームをそのままPOSTすれば代替でき、
    Chromiumの起動待ち（数秒〜十数秒）を丸ごとなくせる。
    """
    main_url = MAIN_URL_TEMPLATE.format(group_id=group_id)
    html = request_context.get(main_url).text()

    fields = _parse_form_fields(html)
    fields["text_pw"] = password
    request_context.post(f"https://www.r326.com/b/login.aspx?g={group_id}", form=fields)

    html = request_context.get(main_url).text()
    if 'type="password"' in html:
        raise InvalidCredentialsError(
            "ログインに失敗しました。グループIDまたはパスワードが正しいか確認してください。"
        )
    return html


def _make_should_include(my_name: str):
    # りざぶ郎の予約者表示は「名字のみ」の場合と「名字＋名前」の場合が
    # 混在しているため、完全一致ではなく前方一致で判定する。
    def _should_include(item_name: str, reserver: str) -> bool:
        return is_target_room(item_name) and reserver.startswith(my_name)

    return _should_include


def _render_selector(reservations: list[Reservation], checked: list[bool], cursor: int) -> str:
    """予約一覧を、カーソル位置・チェック状態付きの表形式の文字列に整形する。"""
    lines = [
        "Outlook/Teamsに登録するスケジュールを選択してください。",
        "　>を矢印キーで動かし、登録する場合はSpaceキーを入力すると登録対象に × が付きます",
        "↑↓:移動  スペース:登録するか切り替え  Enter:確定",
        "",
        "    日付\t\t時間\t\t会議室",
    ]
    for i, r in enumerate(reservations):
        pointer = ">" if i == cursor else " "
        box = "[x]" if checked[i] else "[ ]"
        lines.append(
            f"{pointer} {box} {format_date_jp(r.date)}\t{r.start_time}-{r.end_time}\t{r.location} {r.room}"
        )
    return "\n".join(lines)


def _select_reservations(reservations: list[Reservation]) -> list[Reservation]:
    """矢印キー（↑↓）とスペースキーで、Outlookに登録する予約を1件ずつ選択させる。

    Windowsコンソール専用（msvcrtを使用）。デフォルトは全件チェック済みとし、
    不要な予約だけチェックを外して除外できるようにする。
    """
    reservations = sorted(reservations, key=lambda r: (r.date, r.start_time))
    checked = [True] * len(reservations)
    cursor = 0

    while True:
        os.system("cls")
        print(_render_selector(reservations, checked, cursor))
        key = msvcrt.getch()
        if key == b"\xe0":
            direction = msvcrt.getch()
            if direction == b"H":  # ↑
                cursor = (cursor - 1) % len(reservations)
            elif direction == b"P":  # ↓
                cursor = (cursor + 1) % len(reservations)
        elif key == b" ":
            checked[cursor] = not checked[cursor]
        elif key in (b"\r", b"\n"):
            break

    return [r for r, is_checked in zip(reservations, checked) if is_checked]


def run() -> None:
    config = load_or_create_config()

    start = date.today()
    end = start + timedelta(days=FETCH_DAYS - 1)

    print(f"{config.my_name} さんの予約を {start} から {end} まで取得します...")
    with sync_playwright() as playwright:
        request_context = playwright.request.new_context()
        html = _login_via_http(request_context, config.group_id, config.password)
        page = _HttpPage(request_context, html)
        reservations = scrape_days(
            page, config.group_id, start, end, _make_should_include(config.my_name)
        )
        request_context.dispose()

    print(f"{len(reservations)} 件の予約を取得しました。")
    if not reservations:
        return

    selected = _select_reservations(reservations)
    if not selected:
        print("登録する予約が選択されなかったため、登録を中止しました。")
        return

    created, skipped = register_events(selected)
    print(f"Outlook予定表に登録しました（新規 {created} 件 / 既存のためスキップ {skipped} 件）。")


def main() -> None:
    while True:
        try:
            run()
        except InvalidCredentialsError as exc:
            print(f"\n{exc}")
            delete_config()
            print("保存済みの設定を削除しました。次回実行時にグループID・パスワードを再入力してください。")
        except Exception:
            traceback.print_exc()
            print("\nエラーが発生しました。上記の内容を確認してください。")

        answer = input("\n完了しました。再実行しますか？ (y/n): ").strip().lower()
        if answer not in ("y", "yes"):
            break


if __name__ == "__main__":
    main()
