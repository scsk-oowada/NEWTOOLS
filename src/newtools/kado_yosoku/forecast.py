"""月次の稼働率から、線形トレンドで翌月の稼働率を予測する。"""

from newtools.kado_yosoku.reader import EmployeeMonthRecord


def linear_forecast(values: list[float]) -> float:
    """等間隔の数値列に対して最小二乗法の直線を当てはめ、次の1点を予測する。"""
    n = len(values)
    xs = list(range(1, n + 1))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        return mean_y
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values)) / denominator
    intercept = mean_y - slope * mean_x
    next_x = n + 1
    return slope * next_x + intercept


def forecast_kadoritsu(
    monthly_records: dict[str, list[EmployeeMonthRecord]], sheet_order: list[str]
) -> dict:
    """月別シート名の順に稼働率を並べ、従業員ごと・チーム全体の翌月予測を返す。"""
    base_names = [record.name for record in monthly_records[sheet_order[0]]]

    per_employee = {}
    for name in base_names:
        history = []
        for sheet_name in sheet_order:
            record = next(r for r in monthly_records[sheet_name] if r.name == name)
            history.append(record.kadoritsu)
        per_employee[name] = {
            "history": history,
            "predicted": linear_forecast(history),
        }

    team_average_predicted = sum(v["predicted"] for v in per_employee.values()) / len(per_employee)

    return {
        "per_employee": per_employee,
        "team_average_predicted": team_average_predicted,
    }


def forecast_hours_per_employee(
    monthly_records: dict[str, list[EmployeeMonthRecord]], sheet_order: list[str], attr: str
) -> dict[str, float]:
    """従業員ごとに、指定した時間項目（属性名）の月次系列から翌月の値を線形予測する。"""
    base_names = [record.name for record in monthly_records[sheet_order[0]]]
    result = {}
    for name in base_names:
        history = []
        for sheet_name in sheet_order:
            record = next(r for r in monthly_records[sheet_name] if r.name == name)
            history.append(getattr(record, attr))
        result[name] = linear_forecast(history)
    return result


def forecast_standard_hours(
    monthly_records: dict[str, list[EmployeeMonthRecord]], sheet_order: list[str]
) -> float:
    """チーム共通の標準総労働時間の月次系列から翌月の値を線形予測する。"""
    history = [monthly_records[sheet_name][0].standard_hours for sheet_name in sheet_order]
    return linear_forecast(history)
