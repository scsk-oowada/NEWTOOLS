"""scraper モジュールのテスト（ネットワークに依存しない解析部分のみ）。"""

from newtools.rizab_summary.scraper import _default_should_include, parse_schedules_text

_ITEMS = {
    "984214": "宇都宮 大会議室",
    "1129995": "社用車 フィット",
}

_SCHEDULES_TEXT = (
    "\r\n\r\n20260908\r\n\r\n\r\n"
    "s\t161433150\t984214\t202609081330\t202609081800\t\t13434879\t0\t0\t五百木\r\n"
    "s\t162227361\t1129995\t202609080900\t202609081500\t\t13434879\t0\t0\t廣谷\r\n"
)


def test_parse_schedules_text_extracts_reservations():
    reservations = parse_schedules_text(_SCHEDULES_TEXT, _ITEMS, _default_should_include)

    assert len(reservations) == 1
    assert reservations[0].reserver == "五百木"
    assert reservations[0].room == "大会議室"


def test_parse_schedules_text_excludes_non_target_items():
    reservations = parse_schedules_text(_SCHEDULES_TEXT, _ITEMS, _default_should_include)

    assert all(r.reserver != "廣谷" for r in reservations)


def test_parse_schedules_text_custom_filter():
    reservations = parse_schedules_text(
        _SCHEDULES_TEXT, _ITEMS, lambda item_name, reserver: reserver == "廣谷"
    )

    assert len(reservations) == 1
    assert reservations[0].reserver == "廣谷"
    assert reservations[0].room == "フィット"
