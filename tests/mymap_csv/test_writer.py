"""writer モジュールのテスト。"""

import csv

from newtools.mymap_csv.parser import Pin
from newtools.mymap_csv.writer import write_csv


def test_write_csv_contains_header_and_rows(tmp_path):
    pins = [
        Pin(latitude=35.681236, longitude=139.767125, name="東京駅"),
        Pin(latitude=34.702485, longitude=135.495951, name="34.702485,135.495951"),
    ]
    output_path = tmp_path / "pins.csv"

    write_csv(pins, output_path)

    with output_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    assert rows[0] == ["名前", "緯度", "経度"]
    assert rows[1] == ["東京駅", "35.681236", "139.767125"]
    assert rows[2] == ["34.702485,135.495951", "34.702485", "135.495951"]
