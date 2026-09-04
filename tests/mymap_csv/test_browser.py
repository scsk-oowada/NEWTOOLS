"""browser モジュールのテスト。"""

import pytest

from newtools.mymap_csv.browser import import_csv_to_map


def test_import_csv_to_map_raises_when_no_login_session(tmp_path):
    storage_state_path = tmp_path / "session.json"
    csv_path = tmp_path / "pins.csv"
    csv_path.write_text("名前,緯度,経度\n", encoding="utf-8-sig")

    with pytest.raises(RuntimeError, match="ログイン状態が保存されていません"):
        import_csv_to_map(
            "https://www.google.com/maps/d/edit?mid=dummy",
            csv_path,
            storage_state_path=storage_state_path,
        )
