"""config モジュールのテスト。"""

import newtools.rizab_my_schedule.config as config_module
from newtools.rizab_my_schedule.config import Config, load_config, save_config


def test_save_and_load_config_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "config.bin")

    config = Config(group_id="abc123", password="secret", my_name="矢野")
    save_config(config)

    assert load_config() == config


def test_load_config_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "missing.bin")

    assert load_config() is None
