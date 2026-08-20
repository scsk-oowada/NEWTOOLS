"""outlook_calendar モジュールのテスト。"""

from datetime import datetime

from newtools.outlook_calendar import _format_ol_datetime


def test_format_ol_datetime():
    assert _format_ol_datetime(datetime(2026, 1, 2, 9, 30)) == "01/02/2026 09:30"
