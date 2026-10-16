"""普段使っているMicrosoft Edgeのプロファイルを使ってブラウザを起動するモジュール。

SHARE/OTMは社内SSO（Microsoft Entra ID等）でログインするため、ツール専用の
ブラウザではSSOのセッションを持っていない。普段使っているEdgeのプロファイル
（Cookie等）をそのまま使うことで、SSOログイン済みの状態を引き継ぐ。

Edgeプロファイルは多重起動を許さないため、実行前に普段使っているEdgeを
すべて終了しておく必要がある。
"""

import os
from pathlib import Path

from playwright.sync_api import BrowserContext, sync_playwright

DEFAULT_PROFILE_DIRECTORY = "Default"


class EdgeProfileLockedError(Exception):
    """Edgeプロファイルが別のEdgeプロセスに使用中の場合に発生する例外。"""


def default_edge_user_data_dir() -> Path:
    """Edgeのユーザーデータディレクトリ（プロファイルの格納先）を返す。"""
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        raise RuntimeError("環境変数 LOCALAPPDATA が取得できません。")
    return Path(local_appdata) / "Microsoft" / "Edge" / "User Data"


def launch_edge_context(
    playwright, user_data_dir: Path, profile_directory: str = DEFAULT_PROFILE_DIRECTORY
) -> BrowserContext:
    """普段使っているEdgeのプロファイルで、Edgeを起動してBrowserContextを返す。"""
    try:
        return playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            channel="msedge",
            headless=False,
            args=[f"--profile-directory={profile_directory}"],
        )
    except Exception as exc:
        if "ProcessSingleton" in str(exc) or "already running" in str(exc).lower():
            raise EdgeProfileLockedError(
                "Edgeのプロファイルが使用中です。普段使っているEdgeをすべて終了してから再実行してください。"
            ) from exc
        raise


__all__ = [
    "EdgeProfileLockedError",
    "default_edge_user_data_dir",
    "launch_edge_context",
    "sync_playwright",
]
