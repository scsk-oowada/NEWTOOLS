"""りざぶ郎のログイン情報（グループID・パスワード・自分の氏名）を
Windows DPAPIで暗号化してローカルに保存・読み込みするモジュール。

exe化してダブルクリックだけで実行できるようにするため、環境変数ではなく
初回実行時に入力した内容をファイルに保存する。DPAPIで暗号化するため、
実行したユーザー・PCでなければ復号できない。
"""

import json
import os
from dataclasses import asdict, dataclass
from getpass import getpass
from pathlib import Path

import win32crypt

_CRYPTPROTECT_UI_FORBIDDEN = 0x1

CONFIG_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "newtools" / "rizab_my_schedule"
CONFIG_PATH = CONFIG_DIR / "config.bin"


@dataclass(frozen=True)
class Config:
    """りざぶ郎のログイン情報。"""

    group_id: str
    password: str
    my_name: str


def load_config() -> Config | None:
    """保存済みの設定を読み込む。未設定の場合はNoneを返す。"""
    if not CONFIG_PATH.exists():
        return None
    encrypted = CONFIG_PATH.read_bytes()
    _, decrypted = win32crypt.CryptUnprotectData(
        encrypted, None, None, None, _CRYPTPROTECT_UI_FORBIDDEN
    )
    data = json.loads(decrypted.decode("utf-8"))
    return Config(**data)


def save_config(config: Config) -> None:
    """設定をDPAPIで暗号化してローカルファイルに保存する。"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(config)).encode("utf-8")
    encrypted = win32crypt.CryptProtectData(
        payload, "rizab_my_schedule", None, None, None, _CRYPTPROTECT_UI_FORBIDDEN
    )
    CONFIG_PATH.write_bytes(encrypted)


def prompt_config() -> Config:
    """初回実行時にログイン情報を対話入力で受け取る。"""
    print("初回実行のため、りざぶ郎のログイン情報を設定します。")
    print("（次回以降はこの入力なしで自動実行されます）")
    group_id = input("グループID（予約表URLの g= の値）: ").strip()
    password = getpass("パスワード: ").strip()
    my_name = input("りざぶ郎の予約者表示に一致する、あなたの氏名（名字のみ）: ").strip()
    return Config(group_id=group_id, password=password, my_name=my_name)


def load_or_create_config() -> Config:
    """保存済みの設定があれば読み込み、なければ入力を受けて保存する。"""
    config = load_config()
    if config is not None:
        return config
    config = prompt_config()
    save_config(config)
    print(f"設定を保存しました: {CONFIG_PATH}")
    return config
