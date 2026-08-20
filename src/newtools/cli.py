"""newtools コマンドラインエントリポイント。"""

import argparse
from datetime import datetime, timedelta

from newtools.outlook_calendar import list_events


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def main() -> None:
    parser = argparse.ArgumentParser(description="Teams会議（Outlookカレンダーイベント）の一覧を取得する")
    parser.add_argument(
        "--start",
        type=_parse_date,
        default=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        help="開始日 (YYYY-MM-DD)。省略時は本日",
    )
    parser.add_argument(
        "--end",
        type=_parse_date,
        help="終了日 (YYYY-MM-DD、この日を含む)。省略時は開始日から7日後",
    )
    args = parser.parse_args()

    start = args.start
    end_date = args.end or start + timedelta(days=7)
    end = end_date + timedelta(days=1)  # 終了日を含めるため翌日0時までを範囲とする

    events = list_events(start, end)

    if not events:
        print("該当する予定はありません。")
        return

    for event in events:
        marker = "[Teams]" if event["is_teams"] else ""
        print(f"{event['start']} - {event['end']} {marker} {event['subject']}")


if __name__ == "__main__":
    main()
