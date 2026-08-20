"""Outlook COM経由でのカレンダーイベント取得（Azure AD認証不要）。"""

from datetime import datetime

import win32com.client

OL_FOLDER_CALENDAR = 9
TEAMS_MEETING_MARKER = "teams.microsoft.com/meet"


def _format_ol_datetime(dt: datetime) -> str:
    """Outlookの検索フィルタ（Restrict）で使う日時文字列に変換する。"""
    return dt.strftime("%m/%d/%Y %H:%M")


def list_events(start: datetime, end: datetime) -> list[dict]:
    """指定期間のOutlookカレンダーイベント一覧を取得する。"""
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    calendar = namespace.GetDefaultFolder(OL_FOLDER_CALENDAR)

    items = calendar.Items
    items.IncludeRecurrences = True
    items.Sort("[Start]")

    restriction = (
        f"[Start] >= '{_format_ol_datetime(start)}' "
        f"AND [Start] <= '{_format_ol_datetime(end)}'"
    )

    events = []
    for item in items.Restrict(restriction):
        events.append(
            {
                "subject": item.Subject or "(件名なし)",
                "start": item.Start.strftime("%Y-%m-%d %H:%M"),
                "end": item.End.strftime("%Y-%m-%d %H:%M"),
                "is_teams": TEAMS_MEETING_MARKER in (item.Body or ""),
            }
        )
    return events
