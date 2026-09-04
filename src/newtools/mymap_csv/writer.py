"""ピン情報をGoogle My Mapsインポート用CSVに書き出すモジュール。"""

import csv
from pathlib import Path

from newtools.mymap_csv.parser import Pin

CSV_HEADER = ("名前", "緯度", "経度")


def write_csv(pins: list[Pin], output_path: Path) -> None:
    """ピン情報をMy Mapsの「インポート」機能で読み込めるCSVとして書き出す。"""
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for pin in pins:
            writer.writerow((pin.name, pin.latitude, pin.longitude))
