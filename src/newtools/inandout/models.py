"""SHARE/OTMの打刻画面から読み取った情報を扱う純粋なロジック。"""

from dataclasses import dataclass
from datetime import date

REASON_TEXT = "Claude Code自動打刻"


@dataclass(frozen=True)
class StampInfo:
    """打刻画面から読み取った、打刻対象の日付と区分（出勤/退勤）。"""

    ymd: str
    jiyuu_label: str

    @property
    def target_date(self) -> date:
        return date(int(self.ymd[0:4]), int(self.ymd[4:6]), int(self.ymd[6:8]))


def format_date_jp(d: date) -> str:
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    return f"{d.year}-{d.month:02d}-{d.day:02d}({weekdays[d.weekday()]})"


def format_confirm_message(info: StampInfo) -> str:
    """打刻前にユーザーへ確認する内容を1行のメッセージに整形する。"""
    return f"{format_date_jp(info.target_date)} の「{info.jiyuu_label}」を打刻します。よろしいですか？"
