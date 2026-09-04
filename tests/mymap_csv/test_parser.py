"""parser モジュールのテスト。"""

import pytest

from newtools.mymap_csv.parser import parse_line, parse_text


def test_parse_line_without_name_uses_coordinates_as_name():
    pin = parse_line("35.681236,139.767125", 1)

    assert pin.latitude == 35.681236
    assert pin.longitude == 139.767125
    assert pin.name == "35.681236,139.767125"


def test_parse_line_with_name():
    pin = parse_line("35.681236,139.767125,東京駅", 1)

    assert pin.name == "東京駅"


def test_parse_line_with_fullwidth_comma():
    pin = parse_line("35.681236，139.767125，東京駅", 1)

    assert pin.latitude == 35.681236
    assert pin.name == "東京駅"


def test_parse_line_blank_returns_none():
    assert parse_line("", 1) is None
    assert parse_line("   ", 1) is None


def test_parse_line_invalid_format_raises():
    with pytest.raises(ValueError):
        parse_line("35.681236", 1)


def test_parse_line_non_numeric_raises():
    with pytest.raises(ValueError):
        parse_line("東京,大阪", 1)


def test_parse_text_multiple_lines_skips_blank():
    text = "35.681236,139.767125,東京駅\n\n34.702485,135.495951\n"
    pins = parse_text(text)

    assert len(pins) == 2
    assert pins[0].name == "東京駅"
    assert pins[1].name == "34.702485,135.495951"
