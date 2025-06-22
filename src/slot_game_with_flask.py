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

from gui import root, canvas, slots, username_label, loaded_images, result_label, status_label, update_label_with_image, flash_background, blink_reels, explosion_effect, show_ranking_window
from sound_manager import get_sounds
from score_manager import add_score
from slot_logic import check_combo, choose_weighted_result
DEBUG = False

# 
import sys
from utils import setup_logger
logger = setup_logger("slot_game_with_flask", "logs/slot_game_with_flask.log", level=logging.INFO)

sounds = get_sounds()
spin_lock = threading.Lock()


reel_symbols = list(loaded_images.keys())

for i in range(3):
    label = tk.Label(root, image=loaded_images["GENIE"], bg="black")
    label.image = loaded_images["GENIE"]
    label.grid(row=1, column=i, padx=20, pady=(10, 0))
    slots.append(label)

ranking_button = tk.Button(root, text="🏆 ランキングを見る", font=("Helvetica", 10),
                           command=lambda: show_ranking_window())
ranking_button.grid(row=3, column=1, pady=(0, 10))

# 🔁 スロット演出を順番に処理するワーカー
def slot_queue_worker():
    while True:
        try:
            username, force_level = username_queue.get()
            print(f"▶️ スロット順番待ち中: {username}")
            root.after(0, lambda u=username, f=force_level: start_spin_with_user(u, f))
            spin_lock.acquire()
            spin_lock.release()
            username_queue.task_done()
        except Exception as e:
            print("❌ キューワーカーエラー:", e)

threading.Thread(target=slot_queue_worker, daemon=True).start()

def start_spin_with_user(username, force_level=0):
    acquired = spin_lock.acquire(timeout=2)
    if not acquired:
        print(f"⚠️ スロットがロック中：{username}はスキップされました")
        return
    threading.Thread(target=spin_individual_reels_with_user, args=(username, force_level)).start()

def spin_individual_reels_with_user(username, force_level=0):
    try:
        root.after(0, lambda: canvas.place_forget())
        root.after(0, lambda: canvas.delete("all"))
        root.after(0, lambda: canvas.configure(bg="black"))
        root.after(0, lambda: root.configure(bg="black"))
        for label in [username_label, result_label] + slots:
            root.after(0, lambda l=label: l.configure(bg="black"))
        for i, label in enumerate(slots):
            root.after(0, lambda l=label, i=i: l.grid(row=1, column=i, padx=20, pady=(10, 0)))

        root.after(0, lambda: username_label.config(text=f"{username} さんが \n スロットを回しています"))
        result_label.config(text="")
        final = choose_weighted_result(force_level)

        for reel, symbol in enumerate(final):
            for i in range(10):
                temp_symbol = random.choice(reel_symbols)
                root.after(0, lambda r=reel, s=temp_symbol: update_label_with_image(slots[r], s))
                time.sleep(0.05 + i * 0.0015)
            root.after(0, lambda r=reel, s=symbol: update_label_with_image(slots[r], s))
            root.after(0, lambda: sounds["stop"].play())
            time.sleep(0.1)

        message, sound_obj, score = check_combo(final)
        root.after(0, lambda: result_label.config(text=message))
        root.after(0, lambda: sound_obj.play())
        if score >= 50:
            flash_background()
            blink_reels()
            explosion_effect()
        elif score >= 10:
            blink_reels()
            flash_background()
        elif score > 0:
            blink_reels(times=2, interval=100)

        add_score(username, score)

    finally:
        spin_lock.release()

# グローバルDEBUG切り替え用関数
def toggle_debug():
    global DEBUG
    DEBUG = not DEBUG
    debug_button.config(text=f"🛠 DEBUG: {'ON' if DEBUG else 'OFF'}")
    print(f"🛠 DEBUGモード {'有効' if DEBUG else '無効'} に切り替えました")

# GUI下部にボタン追加（ranking_buttonの下あたり）
debug_button = tk.Button(root, text=f"🛠 DEBUG: {'ON' if DEBUG else 'OFF'}", font=("Helvetica", 10),
                         command=toggle_debug)
debug_button.grid(row=3, column=2, pady=(0, 10))
def semi_match_combo():
    base = random.choice(reel_symbols)
    diff = random.choice([s for s in reel_symbols if s != base])
    combo = [base, base, diff]
    random.shuffle(combo)
    return combo

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
        sys.exit(0) 
