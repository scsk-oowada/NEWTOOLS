"""cli モジュールのテスト（フィルタ条件の判定部分のみ）。"""

from newtools.rizab_my_schedule.cli import _make_should_include


def test_should_include_matches_target_room_and_name():
    should_include = _make_should_include("矢野")

    assert should_include("宇都宮 会議室2（右から2番目）", "矢野")
    assert not should_include("宇都宮 会議室2（右から2番目）", "五百木")
    assert not should_include("社用車 フィット", "矢野")
