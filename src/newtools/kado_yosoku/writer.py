"""予測結果を、元のシートと同じレイアウトの新しいシートとしてExcelに書き出す。"""

from datetime import timedelta
from pathlib import Path

import openpyxl

from newtools.kado_yosoku.forecast import forecast_hours_per_employee, forecast_standard_hours
from newtools.kado_yosoku.reader import (
    COL_HYOUJUN_SOUROU,
    COL_MOKUYASU,
    COL_NAME,
    COL_ZANGYO_TOUGETSU,
    DATA_START_ROW,
    read_monthly_records,
)

_DURATION_FORMAT = "[h]:mm:ss"
_KEPT_COLUMNS = {COL_NAME, COL_ZANGYO_TOUGETSU, COL_MOKUYASU, COL_HYOUJUN_SOUROU}


def append_forecast_sheet(
    source_path: Path, sheet_order: list[str], target_label: str, output_path: Path
) -> None:
    """直近のシートの体裁を引き継いだ予測シートを追加し、別ファイルとして保存する。"""
    monthly_records = read_monthly_records(source_path, sheet_order)
    forecast_zangyo = forecast_hours_per_employee(monthly_records, sheet_order, "zangyo_hours")
    forecast_mokuyasu = forecast_hours_per_employee(monthly_records, sheet_order, "mokuyasu_hours")
    forecast_standard = forecast_standard_hours(monthly_records, sheet_order)

    workbook = openpyxl.load_workbook(source_path)
    source_worksheet = workbook[sheet_order[-1]]
    new_worksheet = workbook.copy_worksheet(source_worksheet)
    new_worksheet.title = target_label

    names = [record.name for record in monthly_records[sheet_order[-1]]]
    max_column = source_worksheet.max_column
    row = DATA_START_ROW
    for name in names:
        for column in range(1, max_column + 1):
            if column not in _KEPT_COLUMNS:
                new_worksheet.cell(row=row, column=column).value = None

        _set_duration(new_worksheet, row, COL_ZANGYO_TOUGETSU, forecast_zangyo[name])
        _set_duration(new_worksheet, row, COL_MOKUYASU, forecast_mokuyasu[name])
        _set_duration(new_worksheet, row, COL_HYOUJUN_SOUROU, forecast_standard)
        row += 1

    workbook.save(output_path)


def _set_duration(worksheet, row: int, column: int, hours: float) -> None:
    """時間数（float）を、元シートと同じ時刻表示形式でセルに書き込む。"""
    cell = worksheet.cell(row=row, column=column)
    cell.value = timedelta(hours=hours)
    cell.number_format = _DURATION_FORMAT
