"""りざぶ郎から取得した自分の会議室予約をOutlook予定表にイベント登録するモジュール。"""

from datetime import datetime

import win32com.client

from newtools.rizab_summary.models import Reservation

OL_FOLDER_CALENDAR = 9
OL_APPOINTMENT_ITEM = 1


def _build_location(reservation: Reservation) -> str:
    return f"{reservation.location} {reservation.room}".strip()


def _build_subject(reservation: Reservation) -> str:
    if reservation.subject:
        return reservation.subject
    return _build_location(reservation)


def _to_datetime(reservation: Reservation, time_text: str) -> datetime:
    hour, minute = (int(v) for v in time_text.split(":"))
    return datetime.combine(reservation.date, datetime.min.time()).replace(hour=hour, minute=minute)


def _format_for_outlook(dt: datetime) -> str:
    """Outlookのappointment.Start/Endに渡す文字列を作る。

    タイムゾーン情報のないdatetimeをそのまま代入すると、pywin32のCOM変換で
    UTCとして扱われてしまい、実際の予定がローカルタイムゾーン分（日本では9時間）
    早い時刻で登録されてしまう。文字列で渡すとOutlook側の日時解析でシステムの
    ローカルタイムゾーンとして正しく解釈されるため、これを利用する。
    """
    return dt.strftime("%Y/%m/%d %H:%M")


def _exists(calendar_items, subject: str, start: datetime) -> bool:
    """同じ件名・開始時刻の予定が既に存在するか判定する。

    [Start]をRestrictの日時リテラルで直接比較すると、Outlookのロケール依存の
    日時解析によりヒットしないことがあるため、件名のみでRestrictし、開始時刻は
    Python側で比較する。pywin32がitem.Startに返すdatetimeはtzinfoにUTCが
    付与されているが、実体はローカルタイムゾーンの値（上記の文字列代入によって
    正しく保存された値）なので、タイムゾーン変換はせずtzinfoを外すだけでよい。
    """
    subject_escaped = subject.replace("'", "''")
    candidates = calendar_items.Restrict(f"[Subject] = '{subject_escaped}'")
    for item in candidates:
        item_start = item.Start.replace(tzinfo=None)
        if item_start == start:
            return True
    return False


def register_events(reservations: list[Reservation]) -> tuple[int, int]:
    """自分の予約一覧をOutlook予定表にイベント登録する。

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
        appointment.Location = _build_location(reservation)
        appointment.Start = _format_for_outlook(start)
        appointment.End = _format_for_outlook(end)
        appointment.ReminderSet = False
        appointment.Save()
        created += 1

    return created, skipped
