"""予約一覧を予約者ごとに整理し、TXT形式に整形するモジュール。"""

from newtools.rizab_summary.models import Reservation, format_date_jp


def group_by_reserver(reservations: list[Reservation]) -> dict[str, list[Reservation]]:
    """予約一覧を予約者名ごとにまとめ、日時順に並べ替える。"""
    grouped: dict[str, list[Reservation]] = {}
    for reservation in reservations:
        grouped.setdefault(reservation.reserver, []).append(reservation)

    for items in grouped.values():
        items.sort(key=lambda r: (r.date, r.start_time))

    return dict(sorted(grouped.items()))


def format_report(reservations: list[Reservation]) -> str:
    """予約一覧を予約者ごとのTXTレポート文字列に整形する。"""
    grouped = group_by_reserver(reservations)

    if not grouped:
        return "該当する会議室予約はありません。\n"

    lines = []
    for reserver, items in grouped.items():
        lines.append(f"■ {reserver}")
        for item in items:
            lines.append(
                f"  {format_date_jp(item.date)} {item.start_time}-{item.end_time}"
                f"  {item.location} {item.room}"
            )
        lines.append("")

    return "\n".join(lines)
