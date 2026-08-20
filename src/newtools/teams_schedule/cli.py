"""newtools コマンドラインエントリポイント。"""

import argparse
from datetime import datetime, timedelta

from newtools.teams_schedule.outlook_calendar import list_events


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
    parser.add_argument(
        "--exclude-cancelled",
        action="store_true",
        help="キャンセル済みの予定を表示から除外する",
    )
    parser.add_argument(
        "--teams-only",
        action="store_true",
        help="Teams会議のみを表示する",
    )
    args = parser.parse_args()

    start = args.start
    end_date = args.end or start + timedelta(days=7)
    end = end_date + timedelta(days=1)  # 終了日を含めるため翌日0時までを範囲とする

    events = list_events(start, end)

    if args.exclude_cancelled:
        events = [event for event in events if not event["is_cancelled"]]
    if args.teams_only:
        events = [event for event in events if event["is_teams"]]

    if not events:
        print("該当する予定はありません。")
        return

    for event in events:
        markers = " ".join(
            marker
            for marker, condition in (
                ("[Teams]", event["is_teams"]),
                ("[Canceled]", event["is_cancelled"]),
            )
            if condition
        )
        print(f"{event['start']} - {event['end']} {markers} {event['subject']}")


if __name__ == "__main__":
    main()
