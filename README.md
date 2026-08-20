# newtools

新規案件向けのツール作成プロジェクト。

## セットアップ

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## ディレクトリ構成

```
NEWTOOLS/
├── pyproject.toml   ← パッケージ定義
├── README.md        ← このファイル
├── src/
│   └── newtools/    ← ソースコード本体
├── tests/           ← テストコード
└── .venv/           ← 仮想環境（Git管理外）
```

## テスト実行

```bash
pytest
```

## ツール一覧

- `teams-schedule` — Outlookカレンダーの予定一覧を取得するCLI。使い方は [docs/usage.html](docs/usage.html) を参照。
