"""cli モジュールのテスト（フィルタ条件の判定・表整形部分のみ）。"""

from datetime import date

import pytest

from newtools.rizab_my_schedule.cli import (
    _make_should_include,
    _prompt_missing_titles,
    _render_selector,
)
from newtools.rizab_summary.models import Reservation


def test_should_include_matches_target_room_and_name():
    should_include = _make_should_include("矢野")

    assert should_include("宇都宮 会議室2（右から2番目）", "矢野")
    assert not should_include("宇都宮 会議室2（右から2番目）", "五百木")
    assert not should_include("社用車 フィット", "矢野")


def test_should_include_matches_full_name_reserver():
    should_include = _make_should_include("大和田")

    assert should_include("大宮 会議室1（6人用）", "大和田圭祐")


def _reservation(date_=date(2026, 9, 8), start_time="10:00", end_time="11:00", subject=""):
    return Reservation(
        reserver="矢野",
        date=date_,
        start_time=start_time,
        end_time=end_time,
        location="宇都宮",
        room="会議室2（右から2番目）",
        subject=subject,
    )


def test_render_selector_includes_date_time_and_room():
    table = _render_selector([_reservation()], checked=[True], cursor=0)

    assert "2026-09-08" in table
    assert "10:00-11:00" in table
    assert "宇都宮 会議室2（右から2番目）" in table


def test_render_selector_marks_checked_and_unchecked_rows():
    reservations = [_reservation(), _reservation(start_time="13:00", end_time="14:00")]

    table = _render_selector(reservations, checked=[True, False], cursor=0)
    lines = [line for line in table.splitlines() if "10:00-11:00" in line or "13:00-14:00" in line]

    assert "[x]" in lines[0]
    assert "[ ]" in lines[1]


def test_render_selector_marks_cursor_position():
    reservations = [_reservation(), _reservation(start_time="13:00", end_time="14:00")]

    table = _render_selector(reservations, checked=[True, True], cursor=1)
    lines = [line for line in table.splitlines() if "10:00-11:00" in line or "13:00-14:00" in line]

    assert not lines[0].startswith(">")
    assert lines[1].startswith(">")


def test_render_selector_shows_title_when_present():
    table = _render_selector([_reservation(subject="MS113課会")], checked=[True], cursor=0)

    assert "MS113課会" in table


def test_render_selector_shows_placeholder_when_title_missing():
    table = _render_selector([_reservation()], checked=[True], cursor=0)

    assert "(未入力)" in table


def test_prompt_missing_titles_keeps_existing_title(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: pytest.fail("入力済みタイトルでは呼ばれないはず"))

    result = _prompt_missing_titles([_reservation(subject="MS113課会")])

    assert result[0].subject == "MS113課会"


def test_prompt_missing_titles_applies_entered_title(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "追記したタイトル")

    result = _prompt_missing_titles([_reservation()])

    assert result[0].subject == "追記したタイトル"


def test_prompt_missing_titles_keeps_blank_when_not_entered(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")

    result = _prompt_missing_titles([_reservation()])

    assert result[0].subject == ""
