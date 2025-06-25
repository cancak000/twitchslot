# slot用
import tkinter as tk
import random
import time
import threading
import queue
import traceback
from PIL import Image, ImageTk
from config import TWITCH_CLIENT_ID, TWITCH_SECRET, WEBHOOK_SECRET, ACCESS_TOKEN_USER
import logging
username_queue = queue.Queue()

from gui import root, slot_window, slots, username_label, loaded_images, flash_background, blink_reels, explosion_effect, show_ranking_window
from sound_manager import get_sounds
from slot_animator import start_spin_with_user

DEBUG = False
SOUND_ENABLED = True
# 
import sys
from utils import setup_logger
logger = setup_logger("slot_game_with_flask", "logs/slot_game_with_flask.log", level=logging.INFO)

sounds = get_sounds()
spin_lock = threading.Lock()


reel_symbols = list(loaded_images.keys())

for i in range(3):
    label = tk.Label(slot_window, image=loaded_images["GENIE"], bg="black")
    label.image = loaded_images["GENIE"]
    label.grid(row=1, column=i, padx=20, pady=(10, 0))
    slots.append(label)

ranking_button = tk.Button(root, text="🏆 ランキングを見る", font=("Helvetica", 10),
                           command=lambda: show_ranking_window(slot_window))
ranking_button.grid(row=4, column=0, padx=10, pady=5)

# 🔁 スロット演出を順番に処理するワーカー
def slot_queue_worker():
    global DEBUG, SOUND_ENABLED
    while True:
        try:
            username, force_level = username_queue.get()
            print(f"▶️ スロット順番待ち中: {username}")
            force_level = 3 if DEBUG else force_level
            sound_enable = True if SOUND_ENABLED else False

            # 🔒 ロックを獲得（次の処理は演出が終わるまで待たせる）
            acquired = spin_lock.acquire(timeout=2)
    if not acquired:
        print(f"⚠️ スロットがロック中：{username}はスキップされました")
        return

            slot_window.after(
                0,
                lambda u=username, f=force_level, r=reel_symbols, s=sounds:
                    start_spin_with_user(
                        root, slots, u, f, r, s, sound_enable,
                        username_queue, spin_lock
                    )
            )
        except Exception as e:
            print("❌ キューワーカーエラー:", e)

threading.Thread(target=slot_queue_worker, daemon=True).start()


# グローバルDEBUG切り替え用関数
def toggle_debug():
    global DEBUG
    DEBUG = not DEBUG
    debug_button.config(text=f"🛠 DEBUG: {'ON ' if DEBUG else 'OFF'}")
    print(f"🛠 DEBUGモード {'有効' if DEBUG else '無効'} に切り替えました")

# GUI下部にボタン追加（ranking_buttonの下あたり）
debug_button = tk.Button(root, text=f"🛠 DEBUG: {'ON' if DEBUG else 'OFF'}", font=("Helvetica", 10),
                         command=toggle_debug)
debug_button.grid(row=4, column=1, padx=10, pady=5)

def manual_spin():
    force = 3 if DEBUG else 0
    sound_enable = True if SOUND_ENABLED else False
    username_queue.put(("配信者", force))

# 手動でスロットを回すボタン
manual_button = tk.Button(root, text="🎰 手動でスロットを回す", font=("Helvetica", 10),
                          command=manual_spin)
manual_button.grid(row=5, column=0, padx=10, pady=5)

# 音のオンオフ切り替え
def toggle_sound():
    global SOUND_ENABLED
    SOUND_ENABLED = not SOUND_ENABLED
    sound_button.config(text=f"🔊 SOUND: {'ON ' if SOUND_ENABLED else 'OFF'}")
    print(f"🔊 音の設定を {'有効' if SOUND_ENABLED else '無効'} に切り替えました")

# GUI下部にボタン追加（ranking_buttonの下あたり）
sound_button = tk.Button(root, text=f"🔇 SOUND: {'ON' if SOUND_ENABLED else 'OFF'}", font=("Helvetica", 10),
                         command=toggle_sound)
sound_button.grid(row=5, column=1, padx=10, pady=5)

def main():
    import threading
    import time
    from start_ngrok import (
        start_ngrok,
        wait_for_ngrok_ready,
        update_env_url,
    )
    from eventsub_manager import (
        get_reward_ids,
        register_eventsub,
        delete_existing_matching_eventsubs,
    )
    from token_manager import (
        refresh_user_token,
        get_app_token,
    )
    from flask_server import start_flask_server, wait_for_flask_ready

    logger.info("✨ 起動中...")

    # トークン取得（早めにしておく）
    user_token = refresh_user_token()
    app_token = get_app_token()

    if not user_token or not app_token:
        logger.error("❌ トークン取得に失敗しました。終了します。")
        return

    # ngrok 起動 → URL取得
    public_url = start_ngrok()
    if not public_url:
        logger.error("❌ ngrok URLの取得に失敗しました。終了します。")
        return

    # .env 更新 & 再読み込み
    update_env_url(public_url)
    from dotenv import load_dotenv
    load_dotenv("setting.env", override=True)

    # Flask サーバを別スレッドで起動
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()

    # Flask の /eventsub が立ち上がるのを待つ
    wait_for_flask_ready("http://localhost:5000/eventsub", timeout=10)

    # ngrok 越しでアクセスできるか確認
    wait_for_ngrok_ready(public_url, timeout=10)

    # EventSub 登録
    reward_ids = get_reward_ids(user_token)
    delete_existing_matching_eventsubs(app_token, reward_ids)
    register_eventsub(app_token, reward_ids, public_url)
    logger.info("✅ EventSubの登録が完了しました")

    # GUI ループ開始
    logger.info("🖥️ GUI を起動します")
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("slot_crash_log.txt", "w", encoding="utf-8") as f:
            f.write("【致命的エラー】\n")
            f.write(traceback.format_exc())
        logging.critical("致命的な例外が発生しました", exc_info=True)
        sys.exit(1)
    finally:
        from start_ngrok import stop_ngrok
        logging.info("🛑 スロットゲームを終了します")

        stop_ngrok()    
        root.quit()
        slot_window.quit()
        sys.exit(0) 
