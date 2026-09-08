"""outlook_register モジュールのテスト（純粋関数部分・Outlook COMをモックした _exists）。"""

from datetime import date, datetime

from newtools.rizab_my_schedule.outlook_register import _build_location, _build_subject, _exists
from newtools.rizab_summary.models import Reservation


class _FakeItem:
    def __init__(self, subject, start):
        self.Subject = subject
        self.Start = start


class _FakeItems:
    def __init__(self, items):
        self._items = items

    def Restrict(self, filter_str):
        subject = filter_str.split("'")[1].replace("''", "'")
        return [item for item in self._items if item.Subject == subject]


def _reservation(subject="", room="会議室2（右から2番目）", location="宇都宮"):
    return Reservation(
        reserver="矢野",
        date=date(2026, 9, 8),
        start_time="10:00",
        end_time="11:00",
        location=location,
        room=room,
        subject=subject,
    )


def test_build_subject_uses_meeting_subject_when_present():
    assert _build_subject(_reservation(subject="MS113課会")) == "MS113課会"


def test_build_subject_falls_back_to_location_and_room():
    assert _build_subject(_reservation()) == "宇都宮 会議室2（右から2番目）"


def test_build_location():
    assert _build_location(_reservation()) == "宇都宮 会議室2（右から2番目）"


def test_exists_true_when_subject_and_start_match():
    items = _FakeItems([_FakeItem("会議室A", datetime(2026, 9, 8, 10, 0))])

    assert _exists(items, "会議室A", datetime(2026, 9, 8, 10, 0)) is True


def test_exists_false_when_start_differs():
    items = _FakeItems([_FakeItem("会議室A", datetime(2026, 9, 8, 10, 0))])

    assert _exists(items, "会議室A", datetime(2026, 9, 8, 11, 0)) is False
