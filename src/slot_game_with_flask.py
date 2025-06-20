import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue
import sys
import logging
import traceback
import random

from utils import resource_path
from gui import root, canvas, username_label, result_label, status_label, flash_background, blink_reels, explosion_effect, load_images, show_ranking_window, update_label_with_image
from score_manager import add_score, get_score
from slot_logic import check_combo, choose_weighted_result
from sound_manager import get_sounds
from flask_server import start_flask_server, username_queue
from slot_animator import start_spin, spin_individual_reels, start_spin_with_user

DEBUG = False

loaded_images = load_images()
sounds = get_sounds()
reel_symbols = []

canvas = tk.Canvas(root, width=520, height=300, bg="black", highlightthickness=0)
canvas.place_forget()


# 🔁 スロット演出を順番に処理するワーカー
def slot_queue_worker():
    while True:
        try:
            username, force_level = username_queue.get()
            print(f"▶️ スロット順番待ち中: {username}")
            root.after(0, lambda u=username, f=force_level, s=sounds, up=update_label_with_image: start_spin_with_user(u, f, s, up))
            spin_lock.acquire()
            spin_lock.release()
            username_queue.task_done()
        except Exception as e:
            print("❌ キューワーカーエラー:", e)

threading.Thread(target=slot_queue_worker, daemon=True).start()

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

spin_lock = threading.Lock()

def trigger_slot_spin(force_level=0):
    if DEBUG:
        force_level = 3

    username = "🎮手動プレイヤー"
    root.after(0, lambda: start_spin_with_user(username, force_level, loaded_images, sounds, update_label_with_image))

def main():
    from start_ngrok import start_ngrok, update_env_url
    from eventsub_manager import get_reward_ids, register_eventsub, delete_existing_matching_eventsubs
    from token_manager import refresh_user_token, get_app_token

    global loaded_images, reel_symbols
    loaded_images = load_images()
    reel_symbols = list(loaded_images.keys())

    # スロットリール画像を作成
#    for i in range(3):
#        label = tk.Label(root, image=loaded_images["GENIE"], bg="black")
#        label.image = loaded_images["GENIE"]  # 参照保持
#        label.grid(row=1, column=i, padx=20, pady=(10, 0))
#        slots.append(label)

    # 🔘 スロットを回すボタン（ユーザー手動用）
    spin_button = tk.Button(root, text="🎰 スロットを回す", font=("Helvetica", 12, "bold"),
                            command=lambda: trigger_slot_spin(force_level=0))
    spin_button.grid(row=3, column=0, pady=(0, 10))

    ranking_button = tk.Button(root, text="🏆 ランキングを見る", font=("Helvetica", 10), command=show_ranking_window)
    ranking_button.grid(row=3, column=1, pady=(0, 10))

    logging.info("✅ スクリプト起動")
    status_label.config(text="ngrok起動中...")

    public_url = start_ngrok()
    if public_url:
        update_env_url(public_url)
        status_label.config(text="トークン取得中...")

        user_token = refresh_user_token()
        app_token = get_app_token()

        if not user_token or not app_token:
            logging.error("❌ トークンの取得に失敗しました")
            status_label.config(text="トークン取得失敗。終了します。")
            root.after(3000, root.quit)
            return

        reward_ids = get_reward_ids(user_token)
        delete_existing_matching_eventsubs(app_token, reward_ids)
        register_eventsub(app_token, reward_ids)

        threading.Thread(target=start_flask_server, daemon=True).start()

        root.mainloop()  # ✅ GUIループをここで開始

    else:
        logging.error("❌ 公開URLの取得に失敗したため、起動を中止します。")
        status_label.config(text="URL取得失敗。終了します。")
        root.after(3000, root.quit)

    status_label.config(text="")

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
        stop_ngrok()  # ←ここで即実行する
        logging.info("🛑 ngrok停止処理を実行しました")
