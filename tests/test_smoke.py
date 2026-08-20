"""動作確認用のスモークテスト。"""

import newtools


def test_version():
    assert newtools.__version__ == "0.1.0"
