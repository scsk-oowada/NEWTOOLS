"""座標情報テキストを解析し、ピン情報のリストに変換するモジュール。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pin:
    """Google My Mapsに登録するピン1件分の情報。"""

    latitude: float
    longitude: float
    name: str


def _normalize_line(line: str) -> str:
    return line.strip().replace("，", ",")


def parse_line(line: str, line_number: int) -> Pin | None:
    """1行分のテキストをPinに変換する。空行はNoneを返す。

    「緯度,経度」または「緯度,経度,地名」の形式を想定する。
    地名が省略された場合は「緯度,経度」の文字列をそのまま名前にする。
    """
    normalized = _normalize_line(line)
    if not normalized:
        return None

    parts = [p.strip() for p in normalized.split(",")]
    if len(parts) not in (2, 3):
        raise ValueError(f"{line_number}行目: 形式が不正です（緯度,経度 または 緯度,経度,地名）: {line!r}")

    latitude_text, longitude_text = parts[0], parts[1]
    try:
        latitude = float(latitude_text)
        longitude = float(longitude_text)
    except ValueError as exc:
        raise ValueError(f"{line_number}行目: 緯度・経度が数値ではありません: {line!r}") from exc

    if len(parts) == 3 and parts[2]:
        name = parts[2]
    else:
        name = f"{latitude_text},{longitude_text}"

    return Pin(latitude=latitude, longitude=longitude, name=name)


def parse_text(text: str) -> list[Pin]:
    """複数行の座標テキストをPinのリストに変換する。"""
    pins = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        pin = parse_line(line, line_number)
        if pin is not None:
            pins.append(pin)
    return pins
