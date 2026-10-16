"""SHARE/OTMの出退勤打刻を自動化するCLI。

普段使っているEdgeのプロファイル（SSOログイン済みの状態）を使って打刻画面を
開き、打刻対象（出勤/退勤）の内容を確認してから打刻する。未処理の打刻が
複数残っている場合は、1件ずつ確認しながら処理する。
"""

import traceback

from newtools.inandout import browser, otm
from newtools.inandout.models import REASON_TEXT, format_confirm_message


def run() -> None:
    user_data_dir = browser.default_edge_user_data_dir()

    with browser.sync_playwright() as playwright:
        context = browser.launch_edge_context(playwright, user_data_dir)
        try:
            page = context.pages[0] if context.pages else context.new_page()

            while True:
                otm.open_top_page(page)
                frame = otm.open_stamp_screen(page)

                try:
                    info = otm.read_stamp_info(frame)
                except otm.NoStampNeededError:
                    print("打刻すべき対象はありません。")
                    break

                answer = input(f"{format_confirm_message(info)} (y/n): ").strip().lower()
                if answer not in ("y", "yes"):
                    print("打刻を中止しました。")
                    break

                otm.submit_stamp(frame, REASON_TEXT)
                print(f"{info.jiyuu_label}を打刻しました。")
        finally:
            context.close()


def main() -> None:
    try:
        run()
    except browser.EdgeProfileLockedError as exc:
        print(f"\n{exc}")
    except Exception:
        traceback.print_exc()
        print("\nエラーが発生しました。上記の内容を確認してください。")

    input("\n完了しました。Enterキーを押すと終了します。")


if __name__ == "__main__":
    main()
