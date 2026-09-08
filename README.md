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
├── pyproject.toml       ← パッケージ定義
├── README.md            ← このファイル
├── docs/                ← 各ツールの使い方ドキュメント
├── src/
│   └── newtools/
│       └── teams_schedule/  ← ツールごとのサブパッケージ
├── tests/
│   └── teams_schedule/  ← ツールごとのテスト
└── .venv/               ← 仮想環境（Git管理外）
```

ツールを追加する場合は `src/newtools/<ツール名>/` にサブパッケージを作り、`pyproject.toml` の `[project.scripts]` にエントリポイントを追加する。

## テスト実行

```bash
pytest
```

## ツール一覧

- `teams-schedule` — Outlookカレンダーの予定一覧を取得するCLI。使い方は [docs/usage.html](docs/usage.html) を参照。
- `file-stats` — 指定フォルダ内のファイルを拡張子別に集計するCLI。使い方は [docs/file_stats_usage.html](docs/file_stats_usage.html) を参照。
- `rizab-summary` — りざぶ郎（宇都宮・大宮の会議室予約）を予約者ごとに集計してTXT出力し、Outlook予定表への登録も行うCLI。使い方は [docs/rizab_summary_usage.html](docs/rizab_summary_usage.html) を参照。
- `mymap-csv` — 座標リストからGoogle My Maps用のインポートCSVを作成するCLI。使い方は [docs/mymap_csv_usage.html](docs/mymap_csv_usage.html) を参照。
- `rizab-my-schedule` — りざぶ郎から自分の会議室予約だけを取得してOutlook予定表に登録するCLI。exe化してダブルクリック実行することを想定。使い方は [docs/rizab_my_schedule_usage.html](docs/rizab_my_schedule_usage.html) を参照。
