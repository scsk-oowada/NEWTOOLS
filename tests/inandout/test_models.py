"""models モジュールのテスト（打刻画面の情報整形部分のみ）。"""

from datetime import date

from newtools.inandout.models import StampInfo, format_confirm_message, format_date_jp


def test_target_date_parses_ymd():
    info = StampInfo(ymd="20261016", jiyuu_label="退勤")

    assert info.target_date == date(2026, 10, 16)


def test_format_date_jp_includes_weekday():
    assert format_date_jp(date(2026, 10, 16)) == "2026-10-16(金)"


def test_format_confirm_message_includes_date_and_label():
    info = StampInfo(ymd="20261016", jiyuu_label="退勤")

    message = format_confirm_message(info)

    assert "2026-10-16(金)" in message
    assert "退勤" in message
