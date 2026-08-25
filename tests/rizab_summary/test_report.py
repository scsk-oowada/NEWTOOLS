"""report モジュールのテスト。"""

from datetime import date

from newtools.rizab_summary.models import Reservation
from newtools.rizab_summary.report import format_report, group_by_reserver


def _reservation(reserver, day, start_time, room="会議室A"):
    return Reservation(
        reserver=reserver,
        date=date(2026, 8, day),
        start_time=start_time,
        end_time="12:00",
        location="宇都宮",
        room=room,
    )


def test_group_by_reserver_sorts_within_group_and_by_name():
    reservations = [
        _reservation("矢野", 26, "10:00"),
        _reservation("矢野", 25, "09:00"),
        _reservation("五百木", 25, "09:00"),
    ]

    grouped = group_by_reserver(reservations)

    assert list(grouped.keys()) == ["五百木", "矢野"]
    assert [r.date.day for r in grouped["矢野"]] == [25, 26]


def test_format_report_empty():
    assert format_report([]) == "該当する会議室予約はありません。\n"


def test_format_report_contains_reserver_and_room():
    report = format_report([_reservation("矢野", 25, "10:00", room="会議室2")])

    assert "■ 矢野" in report
    assert "会議室2" in report
    assert "10:00-12:00" in report
