"""SHARE/OTMへの出退勤打刻を行うモジュール。

SHARE/OTMはフレーム構成の画面で、メインメニュー（左側のフレーム）の
「打刻」リンクをクリックすると、結果がDATA_FRAMEという名前のフレームに
表示される。URLを直接開くとエラーになるため、必ずメニューのリンクを
クリックして画面を開く必要がある。
"""

from playwright.sync_api import Frame, Page

from newtools.inandout.models import StampInfo

TOP_URL = "https://we.scskinfo.jp/otm2/OTMServlet?controllerId=010401"
STAMP_MENU_LINK_TEXT = "打刻"
DATA_FRAME_NAME = "DATA_FRAME"


class StampScreenError(Exception):
    """打刻画面の表示・解析に失敗した場合に発生する例外。"""


class NoStampNeededError(Exception):
    """打刻すべき対象が無い場合（既に出退勤とも打刻済みの場合）に発生する例外。"""


def _data_frame(page: Page) -> Frame:
    frame = page.frame(name=DATA_FRAME_NAME)
    if frame is None:
        raise StampScreenError(f"{DATA_FRAME_NAME} フレームが見つかりませんでした。")
    return frame


def open_top_page(page: Page) -> None:
    """SHARE/OTMのトップページ（メニュー付き画面）を開く。"""
    page.goto(TOP_URL)
    page.wait_for_load_state("networkidle")


def open_stamp_screen(page: Page) -> Frame:
    """メニューの「打刻」リンクをクリックし、結果が表示されるフレームを返す。"""
    page.get_by_role("link", name=STAMP_MENU_LINK_TEXT).click()
    page.wait_for_load_state("networkidle")
    frame = _data_frame(page)

    content = frame.content()
    if "システム障害" in content or "データの不整合" in content:
        raise StampScreenError(
            "打刻画面の取得に失敗しました（システム障害またはデータ不整合）。"
            "もう一度実行し直してください。"
        )
    return frame


def read_stamp_info(frame: Frame) -> StampInfo:
    """打刻画面のフレームから、対象日付と区分（出勤/退勤）を読み取る。"""
    ymd = frame.locator('input[name="ymd"]').get_attribute("value")
    if not ymd:
        raise StampScreenError("打刻対象の日付が取得できませんでした。")

    jiyuu_input = frame.locator('input[name="jiyuu"]')
    if jiyuu_input.count() == 0:
        raise NoStampNeededError("打刻すべき対象がありません（既に打刻済みです）。")

    jiyuu_label = jiyuu_input.locator("xpath=..").inner_text().strip()
    return StampInfo(ymd=ymd, jiyuu_label=jiyuu_label)


def submit_stamp(frame: Frame, reason: str) -> None:
    """打刻画面の「理由」欄に入力し、打刻を確定する。"""
    frame.locator('input[name="riyuu"]').fill(reason)
    frame.locator('input[type="submit"]').click()
    frame.page.wait_for_load_state("networkidle")
