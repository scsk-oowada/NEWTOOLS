"""outlook_register モジュールのテスト（Outlook COMをモックした _exists のみ）。"""

from datetime import datetime

from newtools.rizab_summary.outlook_register import _exists


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


def test_exists_true_when_subject_and_start_match():
    items = _FakeItems([_FakeItem("会議室A", datetime(2026, 9, 8, 10, 0))])

    assert _exists(items, "会議室A", datetime(2026, 9, 8, 10, 0)) is True


def test_exists_false_when_start_differs():
    items = _FakeItems([_FakeItem("会議室A", datetime(2026, 9, 8, 10, 0))])

    assert _exists(items, "会議室A", datetime(2026, 9, 8, 11, 0)) is False


def test_exists_false_when_no_matching_subject():
    items = _FakeItems([])

    assert _exists(items, "会議室A", datetime(2026, 9, 8, 10, 0)) is False
