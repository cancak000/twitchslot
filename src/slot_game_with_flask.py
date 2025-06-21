# slot用
import tkinter as tk
import random
import time
import threading
import queue
from flask import Flask, request
import json
import hmac
import hashlib
import os
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

# Flask アプリのセットアップ
app = Flask(__name__)
app.config['DEBUG'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False

# ログ設定
logging.basicConfig(
    filename="slot_game_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

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

@app.route("/", methods=["GET"])
def index():
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write("GET iVTest \n")
    return "iV Slot EventSub Webhook is running!"

@app.route("/eventsub", methods=["POST"])
def eventsub():
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write("POST iVTest \n")
    try:
        message_id = request.headers.get("Twitch-Eventsub-Message-Id")
        timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp")
        message_type = request.headers.get("Twitch-Eventsub-Message-Type", "").lower()
        signature_header = request.headers.get("Twitch-Eventsub-Message-Signature", "")
        body = request.data.decode("utf-8")
        print("====")
        print(body)
        try:
            body_json = json.loads(body)
        except Exception as e:
            print(e)
        hmac_message = message_id + timestamp + body
        expected = hmac.new(WEBHOOK_SECRET.encode(), hmac_message.encode(), hashlib.sha256).hexdigest()
        actual = signature_header.split("sha256=")[-1]
        if not hmac.compare_digest(expected, actual):
            print("❌ 署名検証失敗")
            return "Invalid signature", 403
        body_json = json.loads(body)
        if message_type == "webhook_callback_verification":
            print("✅ EventSub 登録確認")
            return body_json["challenge"], 200
        
        if message_type == "notification":
            event = body_json["event"]
            reward_title = event["reward"]["title"]
            reward_cost = event["reward"]["cost"]

            # 🎯 対象のリワード名だけ許可
            valid_titles = {"スロットを回す", "スロット中確率", "スロット大当たりフラグ"}
            if reward_title not in valid_titles:
                print(f"⚠️ 無効なリワード「{reward_title}」は無視されました")
                return "", 204

            if reward_title == "スロット大当たりフラグ":
                force_level = 3
            elif reward_title == "スロット中確率":
                force_level = 2
            else:
                force_level = 0

            username = event["user_name"]
            print(f"🎮 {username} が「{reward_title}」({reward_cost}pt) を使用！ force_level={force_level}")
            username_queue.put((username, force_level))
            return "", 200

        print("通知を受信:", body_json)
        return "", 204
    except Exception as e:
        print("❌ エラー発生:", e)
        traceback.print_exc()
        return "Internal Server Error", 500

@app.route("/routes")
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(f"{rule.methods} {rule.rule}")
    return "<br>".join(output)

def start_flask_server():
    app.run(port=5000, use_reloader=False, threaded=True)

# GUI処理などは別関数で定義（仮のもの）
def start_flask_server():
    app.run()

def main():
    from start_ngrok import start_ngrok, update_env_url
    from eventsub_manager import get_reward_ids, register_eventsub, delete_existing_matching_eventsubs
    from token_manager import refresh_user_token, get_app_token

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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("slot_crash_log.txt", "w", encoding="utf-8") as f:
            f.write("【致命的エラー】\n")
            f.write(traceback.format_exc())
        logging.critical("致命的な例外が発生しました", exc_info=True)
        sys.exit(1)
