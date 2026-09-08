"""models モジュールのテスト。"""

from datetime import date

from newtools.rizab_summary.models import format_date_jp, is_target_room, parse_schedule_row


def test_parse_schedule_row():
    # ["s", 予約ID, アイテムID, 開始日時, 終了日時, 件名, 内部ID, フラグ, フラグ, 予約者名]
    fields = ["s", "162495048", "1110684", "202609081000", "202609081100", "", "13434879", "0", "0", "矢野"]

    reservation = parse_schedule_row(fields, "宇都宮 会議室4（右から4番目）")

    assert reservation.reserver == "矢野"
    assert reservation.date == date(2026, 9, 8)
    assert reservation.start_time == "10:00"
    assert reservation.end_time == "11:00"
    assert reservation.location == "宇都宮"
    assert reservation.room == "会議室4（右から4番目）"
    assert reservation.subject == ""


def test_parse_schedule_row_with_subject():
    fields = ["s", "157040520", "1260312", "202609081000", "202609081130", "MS113課会", "13434879", "0", "0", "髙田"]

    reservation = parse_schedule_row(fields, "大宮 会議室４ (10人用)")

    assert reservation.subject == "MS113課会"


def test_format_date_jp():
    assert format_date_jp(date(2026, 8, 25)) == "2026-08-25(火)"


def test_is_target_room_includes_meeting_rooms():
    assert is_target_room("宇都宮 大会議室")
    assert is_target_room("大宮 会議室１ (６人用)")


def test_is_target_room_excludes_vehicles_and_other_locations():
    assert not is_target_room("宇都宮 S-810405")
    assert not is_target_room("豊洲 S-813674")
    assert not is_target_room("豊洲 ｹﾞｽﾄｶｰﾄﾞ№1")
