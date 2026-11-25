"""writer モジュールのテスト。"""

from datetime import time, timedelta

import openpyxl

from newtools.kado_yosoku.writer import append_forecast_sheet


def _build_workbook(tmp_path):
    workbook = openpyxl.Workbook()
    del workbook["Sheet"]
    for sheet_name, zangyo, mokuyasu, standard in [
        ("8月", time(9, 0), timedelta(days=4, hours=9), timedelta(days=5)),
        ("9月", time(10, 0), timedelta(days=4, hours=20), timedelta(hours=126)),
        ("10月", time(11, 0), timedelta(days=5, hours=7), timedelta(hours=132)),
    ]:
        worksheet = workbook.create_sheet(sheet_name)
        worksheet.append(["氏名", "資格"])
        worksheet.append([])
        row = ["Aさん", "ランクX"] + [None] * 6
        row[7] = zangyo  # 列8: 残業(当月)
        row += [None] * (19 - len(row))
        row.append(mokuyasu)  # 列19: 目安時間
        row.append(None)  # 列20
        row.append(standard)  # 列21: 標準総労働時間
        worksheet.append(row)
    path = tmp_path / "source.xlsx"
    workbook.save(path)
    return path


def test_append_forecast_sheet_fills_only_forecast_columns(tmp_path):
    source_path = _build_workbook(tmp_path)
    output_path = tmp_path / "output.xlsx"

    append_forecast_sheet(source_path, ["8月", "9月", "10月"], "11月", output_path)

    workbook = openpyxl.load_workbook(output_path)
    assert "11月" in workbook.sheetnames
    new_worksheet = workbook["11月"]

    # 氏名・資格のヘッダー行は元シートを踏襲する
    assert new_worksheet.cell(row=1, column=1).value == "氏名"
    assert new_worksheet.cell(row=1, column=2).value == "資格"

    # 氏名列は維持し、資格など予測対象外の列は空白になる
    assert new_worksheet.cell(row=3, column=1).value == "Aさん"
    assert new_worksheet.cell(row=3, column=2).value is None

    # 残業(列8)・目安(列19)・標準総労働(列21)は timedelta で埋まる
    assert isinstance(new_worksheet.cell(row=3, column=8).value, timedelta)
    assert isinstance(new_worksheet.cell(row=3, column=19).value, timedelta)
    assert isinstance(new_worksheet.cell(row=3, column=21).value, timedelta)
    assert new_worksheet.cell(row=3, column=8).number_format == "[h]:mm:ss"

    # 元ファイルは変更されない
    original_workbook = openpyxl.load_workbook(source_path)
    assert "11月" not in original_workbook.sheetnames
