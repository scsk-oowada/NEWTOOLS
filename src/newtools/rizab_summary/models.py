"""りざぶ郎の内部API（a.aspx）から取得したタブ区切りテキストを解析するモジュール。"""

import re
from dataclasses import dataclass, field
from datetime import date

_WEEKDAY_JP = ("月", "火", "水", "木", "金", "土", "日")

_TARGET_LOCATIONS = ("宇都宮", "大宮")

# GetSchedules APIが返す日時形式（YYYYMMDDHHMM）
_API_DATETIME_RE = re.compile(r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})")


@dataclass(frozen=True)
class Reservation:
    """会議室予約1件分の情報。"""

    reserver: str
    date: date
    start_time: str
    end_time: str
    location: str
    room: str
    subject: str = field(default="")


def format_date_jp(d: date) -> str:
    """日付を「2026-08-25(火)」形式の文字列に変換する。"""
    return f"{d.isoformat()}({_WEEKDAY_JP[d.weekday()]})"


def is_target_room(item_name: str) -> bool:
    """アイテムが集計対象の会議室（宇都宮・大宮）かどうかを判定する。"""
    return "会議室" in item_name and item_name.startswith(_TARGET_LOCATIONS)


def parse_api_datetime(text: str) -> tuple[date, str]:
    """API形式の日時文字列（YYYYMMDDHHMM）を日付と"HH:MM"形式の時刻に分解する。"""
    match = _API_DATETIME_RE.fullmatch(text)
    if not match:
        raise ValueError(f"日時の解析に失敗しました: {text!r}")
    year, month, day, hour, minute = (int(v) for v in match.groups())
    return date(year, month, day), f"{hour:02d}:{minute:02d}"


def parse_schedule_row(fields: list[str], item_name: str) -> Reservation:
    """GetSchedules APIの1行（タブ区切り済み）をReservationに変換する。

    fields は
    ["s", 予約ID, アイテムID, 開始日時, 終了日時, 件名, 内部ID, フラグ, フラグ, 予約者名]
    の形式を想定する。
    """
    reservation_date, start_time = parse_api_datetime(fields[3])
    _, end_time = parse_api_datetime(fields[4])
    subject = fields[5].strip()
    reserver = fields[9].strip()

    location, _, room = item_name.partition(" ")
    if not room:
        location, room = "", item_name

    return Reservation(
        reserver=reserver,
        date=reservation_date,
        start_time=start_time,
        end_time=end_time,
        location=location,
        room=room,
        subject=subject,
    )
