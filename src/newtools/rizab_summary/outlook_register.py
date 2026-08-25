"""りざぶ郎の会議室予約をOutlook予定表にイベント登録するモジュール。"""

from datetime import datetime

import win32com.client

from newtools.rizab_summary.models import Reservation

OL_FOLDER_CALENDAR = 9
OL_APPOINTMENT_ITEM = 1


def _build_subject(reservation: Reservation) -> str:
    return f"[{reservation.reserver}] {reservation.room}"


def _to_datetime(reservation: Reservation, time_text: str) -> datetime:
    hour, minute = (int(v) for v in time_text.split(":"))
    return datetime.combine(reservation.date, datetime.min.time()).replace(hour=hour, minute=minute)


def _exists(calendar_items, subject: str, start: datetime) -> bool:
    restriction = (
        f"[Start] = '{start.strftime('%m/%d/%Y %H:%M')}' "
        f"AND [Subject] = '{subject}'"
    )
    return calendar_items.Restrict(restriction).Count > 0


def register_events(reservations: list[Reservation]) -> tuple[int, int]:
    """予約一覧をOutlook予定表にイベント登録する。

    同じ件名・開始時刻の予定が既に存在する場合は二重登録せずスキップする。
    戻り値は (登録件数, スキップ件数)。
    """
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    calendar = namespace.GetDefaultFolder(OL_FOLDER_CALENDAR)
    calendar_items = calendar.Items

    created = 0
    skipped = 0
    for reservation in reservations:
        subject = _build_subject(reservation)
        start = _to_datetime(reservation, reservation.start_time)
        end = _to_datetime(reservation, reservation.end_time)

        if _exists(calendar_items, subject, start):
            skipped += 1
            continue

        appointment = outlook.CreateItem(OL_APPOINTMENT_ITEM)
        appointment.Subject = subject
        appointment.Start = start
        appointment.End = end
        appointment.ReminderSet = False
        appointment.Save()
        created += 1

    return created, skipped
