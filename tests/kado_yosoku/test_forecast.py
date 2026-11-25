"""forecast モジュールのテスト。"""

from newtools.kado_yosoku.forecast import forecast_kadoritsu, linear_forecast
from newtools.kado_yosoku.reader import EmployeeMonthRecord


def test_linear_forecast_increasing_trend():
    # 等差数列であれば、次の値も正確に予測できる
    assert linear_forecast([1.0, 2.0, 3.0]) == 4.0


def test_linear_forecast_constant_values():
    assert linear_forecast([5.0, 5.0, 5.0]) == 5.0


def test_forecast_kadoritsu_per_employee_and_team_average():
    monthly_records = {
        "8月": [EmployeeMonthRecord("Aさん", mokuyasu_hours=90.0, zangyo_hours=0.0, standard_hours=100.0)],
        "9月": [EmployeeMonthRecord("Aさん", mokuyasu_hours=95.0, zangyo_hours=0.0, standard_hours=100.0)],
        "10月": [EmployeeMonthRecord("Aさん", mokuyasu_hours=100.0, zangyo_hours=0.0, standard_hours=100.0)],
    }

    result = forecast_kadoritsu(monthly_records, ["8月", "9月", "10月"])

    assert result["per_employee"]["Aさん"]["history"] == [0.9, 0.95, 1.0]
    assert result["per_employee"]["Aさん"]["predicted"] == 1.05
    assert result["team_average_predicted"] == 1.05
