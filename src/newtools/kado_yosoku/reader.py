"""フレックス管理表（Excel）から従業員ごとの月次勤怠データを読み込む。"""

from dataclasses import dataclass
from datetime import time, timedelta
from pathlib import Path

import openpyxl

# データ行のレイアウト（1始まりの列番号）
COL_NAME = 1  # 氏名
COL_ZANGYO_TOUGETSU = 8  # 残業（当月）
COL_MOKUYASU = 19  # フレックス目安時間
COL_HYOUJUN_SOUROU = 21  # フレックス総労働時間（標準・チーム共通）
DATA_START_ROW = 3


@dataclass
class EmployeeMonthRecord:
    """1名・1ヶ月分の勤怠レコード。"""

    name: str
    mokuyasu_hours: float
    zangyo_hours: float
    standard_hours: float

    @property
    def kadoritsu(self) -> float:
        """稼働率 = (目安時間 + 残業時間) ÷ 標準総労働時間。"""
        if self.standard_hours == 0:
            return 0.0
        return (self.mokuyasu_hours + self.zangyo_hours) / self.standard_hours


def _to_hours(value: object) -> float:
    """セルの値（timedelta/time/数値/文字列）を時間数（float）に変換する。"""
    if value is None:
        return 0.0
    if isinstance(value, timedelta):
        return value.total_seconds() / 3600
    if isinstance(value, time):
        return value.hour + value.minute / 60 + value.second / 3600
    if isinstance(value, (int, float)):
        return float(value) * 24  # Excelのシリアル値（日単位）を時間に変換
    if isinstance(value, str):
        text = value.strip()
        if text in ("", "-"):
            return 0.0
        parts = text.split(":")
        try:
            hours = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0.0
            seconds = float(parts[2]) if len(parts) > 2 else 0.0
            return hours + minutes / 60 + seconds / 3600
        except ValueError:
            return 0.0
    return 0.0


def read_sheet(path: Path, sheet_name: str) -> list[EmployeeMonthRecord]:
    """指定シートを読み込み、従業員ごとの月次勤怠レコード一覧を返す。"""
    workbook = openpyxl.load_workbook(path, data_only=True)
    worksheet = workbook[sheet_name]

    records: list[EmployeeMonthRecord] = []
    row = DATA_START_ROW
    while True:
        name = worksheet.cell(row=row, column=COL_NAME).value
        if name is None or str(name).strip() == "":
            break
        records.append(
            EmployeeMonthRecord(
                name=str(name).strip(),
                mokuyasu_hours=_to_hours(worksheet.cell(row=row, column=COL_MOKUYASU).value),
                zangyo_hours=_to_hours(worksheet.cell(row=row, column=COL_ZANGYO_TOUGETSU).value),
                standard_hours=_to_hours(worksheet.cell(row=row, column=COL_HYOUJUN_SOUROU).value),
            )
        )
        row += 1
    return records


def read_monthly_records(path: Path, sheet_names: list[str]) -> dict[str, list[EmployeeMonthRecord]]:
    """複数シート（月ごと）の勤怠レコードを読み込む。"""
    return {sheet_name: read_sheet(path, sheet_name) for sheet_name in sheet_names}
