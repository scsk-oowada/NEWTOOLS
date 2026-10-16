"""browser モジュールのテスト（Edgeプロファイルのパス解決部分のみ）。"""

from pathlib import Path

import pytest

from newtools.inandout.browser import default_edge_user_data_dir


def test_default_edge_user_data_dir(monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", "C:\\Users\\test\\AppData\\Local")

    result = default_edge_user_data_dir()

    assert result == Path("C:\\Users\\test\\AppData\\Local") / "Microsoft" / "Edge" / "User Data"


def test_default_edge_user_data_dir_requires_localappdata(monkeypatch):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    with pytest.raises(RuntimeError):
        default_edge_user_data_dir()
