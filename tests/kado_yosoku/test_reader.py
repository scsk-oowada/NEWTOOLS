"""reader モジュールのテスト。"""

from datetime import time, timedelta

import openpyxl

from newtools.kado_yosoku.reader import read_sheet


def _build_workbook(tmp_path):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "8月"
    # 1-2行目はヘッダー（内容は読み込み対象外）
    worksheet.append(["氏名"])
    worksheet.append([])
    # 3行目: 氏名(1), ..., 残業当月(8), ..., 目安時間(19), ..., 標準総労働時間(21)
    row = ["Aさん"] + [None] * 18
    row[7] = time(9, 43)  # 残業(当月) 列8
    row[18] = timedelta(days=4, hours=9)  # 目安時間 列19
    row.append(None)  # 不足時間 列20（未使用）
    row.append(timedelta(days=5))  # 標準総労働時間 列21
    worksheet.append(row)
    path = tmp_path / "sample.xlsx"
    workbook.save(path)
    return path


def test_read_sheet_converts_durations_to_hours(tmp_path):
    path = _build_workbook(tmp_path)

    records = read_sheet(path, "8月")

    assert len(records) == 1
    record = records[0]
    assert record.name == "Aさん"
    assert record.zangyo_hours == 9 + 43 / 60
    assert record.mokuyasu_hours == 4 * 24 + 9
    assert record.standard_hours == 5 * 24
