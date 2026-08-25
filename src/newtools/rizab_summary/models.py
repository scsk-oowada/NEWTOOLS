"""りざぶ郎の予約詳細ポップアップから取得したテキストを解析するモジュール。"""

import re
from dataclasses import dataclass
from datetime import date

_WEEKDAY_JP = ("月", "火", "水", "木", "金", "土", "日")

_DATE_RE = re.compile(r"(\d{4})\.(\d{1,2})\.(\d{1,2})")
_TIME_RANGE_RE = re.compile(r"(\d{1,2}:\d{2})\s*[～〜]\s*(\d{1,2}:\d{2})")

_TARGET_LOCATIONS = ("宇都宮", "大宮")


@dataclass(frozen=True)
class Reservation:
    """会議室予約1件分の情報。"""

    reserver: str
    date: date
    start_time: str
    end_time: str
    location: str
    room: str


def format_date_jp(d: date) -> str:
    """日付を「2026-08-25(火)」形式の文字列に変換する。"""
    return f"{d.isoformat()}({_WEEKDAY_JP[d.weekday()]})"


def is_target_room(target_text: str) -> bool:
    """対象アイテムが集計対象の会議室（宇都宮・大宮）かどうかを判定する。"""
    return "会議室" in target_text and target_text.startswith(_TARGET_LOCATIONS)


def parse_reservation(fields: dict[str, str]) -> Reservation:
    """予約詳細ポップアップから抜き出したラベル別テキストをReservationに変換する。

    fields は {"日時": ..., "対象": ..., "予約者（登録者）": ...} の形式を想定する。
    """
    datetime_text = fields["日時"]
    date_match = _DATE_RE.search(datetime_text)
    time_match = _TIME_RANGE_RE.search(datetime_text)
    if not date_match or not time_match:
        raise ValueError(f"日時の解析に失敗しました: {datetime_text!r}")
    year, month, day = (int(v) for v in date_match.groups())
    start_time, end_time = time_match.groups()

    target_text = fields["対象"].strip()
    location, _, room = target_text.partition(" ")
    if not room:
        location, room = "", target_text

    reserver = fields["予約者（登録者）"].strip().splitlines()[0].strip()

    return Reservation(
        reserver=reserver,
        date=date(year, month, day),
        start_time=start_time,
        end_time=end_time,
        location=location,
        room=room,
    )
