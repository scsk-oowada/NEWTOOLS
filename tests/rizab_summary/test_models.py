"""models モジュールのテスト。"""

from datetime import date

from newtools.rizab_summary.models import format_date_jp, is_target_room, parse_reservation


def test_parse_reservation():
    fields = {
        "日時": "2026.8.25(火)\n10:00～11:00",
        "対象": "宇都宮 会議室2（右から2番目）",
        "予約者（登録者）": "矢野\n[2026/8/25  9:56]",
    }
    reservation = parse_reservation(fields)

    assert reservation.reserver == "矢野"
    assert reservation.date == date(2026, 8, 25)
    assert reservation.start_time == "10:00"
    assert reservation.end_time == "11:00"
    assert reservation.location == "宇都宮"
    assert reservation.room == "会議室2（右から2番目）"


def test_format_date_jp():
    assert format_date_jp(date(2026, 8, 25)) == "2026-08-25(火)"


def test_is_target_room_includes_meeting_rooms():
    assert is_target_room("宇都宮 大会議室")
    assert is_target_room("大宮 会議室１ (６人用)")


def test_is_target_room_excludes_vehicles_and_other_locations():
    assert not is_target_room("宇都宮 S-810405")
    assert not is_target_room("豊洲 S-813674")
    assert not is_target_room("豊洲 ｹﾞｽﾄｶｰﾄﾞ№1")
