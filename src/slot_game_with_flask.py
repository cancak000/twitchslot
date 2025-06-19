# slot用
import tkinter as tk
import random
import time
import threading
import pygame
import sqlite3
import queue
import math
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

DEBUG = False

# 
import sys

def resource_path(relative_path):
    try:
        # PyInstallerで実行されているときは、展開ディレクトリを使う
        base_path = sys._MEIPASS
    except AttributeError:
        # 通常のスクリプト実行時（Git構成）：srcから1階層上に移動
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

# SQLite接続はスレッドセーフに
conn = sqlite3.connect("slot_scores.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    username TEXT PRIMARY KEY,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

def add_score(username, delta):
    cursor.execute("INSERT OR IGNORE INTO scores (username) VALUES (?)", (username,))
    cursor.execute("UPDATE scores SET score = score + ? WHERE username = ?", (delta, username))
    conn.commit()

def get_score(username):
    cursor.execute("SELECT score FROM scores WHERE username = ?", (username,))
    row = cursor.fetchone()
    return row[0] if row else 0

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

# GUIエラー用ログ設定
def tk_exception_logger(exc, val, tb):
    with open("slot_tkinter_error_log.txt", "w", encoding="utf-8") as f:
        f.write("Tkinter 例外:\n")
        f.write("".join(traceback.format_exception(exc, val, tb)))


# GUI
root = tk.Tk()
root.report_callback_exception = tk_exception_logger
root.title("iV Slot")
root.geometry("520x300")
root.configure(bg="black")
status_label = tk.Label(root, text="初期化中...", font=("Helvetica", 14), bg="black", fg="white")
status_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))  # ← pack → grid に変更

image_paths = {
    "GENIE": "image/jinny.png",
    "PALACE": "image/castle.png",
    "MOON": "image/moon.png",
    "LAMP": "image/ramp.png",
    "CARPET": "image/carpet.png",
    "COIN": "image/coin.png",
    "SCORPION": "image/scorpion.png",
    "CAMEL": "image/camel.png"
}

loaded_images = {
    key: ImageTk.PhotoImage(Image.open(resource_path(path)).resize((128, 128)))
    for key, path in image_paths.items()
}

reel_symbols = list(loaded_images.keys())

pygame.mixer.init()
stop_sound = pygame.mixer.Sound(resource_path("sound/stop.mp3"))
big_sound = pygame.mixer.Sound(resource_path("sound/big_win.mp3"))
small_sound = pygame.mixer.Sound(resource_path("sound/small_win.mp3"))
lose_sound = pygame.mixer.Sound(resource_path("sound/lose.mp3"))

slots = []
for i in range(3):
    label = tk.Label(root, image=loaded_images["GENIE"], bg="black")
    label.image = loaded_images["GENIE"]
    label.grid(row=1, column=i, padx=20, pady=(10, 0))
    slots.append(label)

result_label = tk.Label(root, text="", font=("Helvetica", 24, "bold"), bg="black", fg="white")
result_label.grid(row=2, column=0, columnspan=3, pady=(10, 20))

username_label = tk.Label(root, text="", font=("Helvetica", 14, "bold"), bg="black", fg="cyan")
username_label.grid(row=0, column=0, columnspan=3, pady=(10, 0))
ranking_button = tk.Button(root, text="🏆 ランキングを見る", font=("Helvetica", 10),
                           command=lambda: show_ranking_window())
ranking_button.grid(row=3, column=1, pady=(0, 10))

canvas = tk.Canvas(root, width=520, height=300, bg="black", highlightthickness=0)
canvas.place_forget()

def reset_backgrounds():
    root.configure(bg="black")
    for label in [username_label, result_label] + slots:
        label.configure(bg="black")

def flash_background(times=6, interval=150):
    def toggle(i):
        bg_color = "white" if i % 2 == 0 else "black"
        root.configure(bg=bg_color)
        for label in [username_label, result_label] + slots:
            label.configure(bg=bg_color)
        if i < times:
            root.after(interval, toggle, i + 1)
        else:
            root.after(interval, reset_backgrounds)
    toggle(0)

def blink_reels(times=6, interval=150):
    def toggle(i):
        for label in slots:
            label.grid_remove() if i % 2 == 0 else label.grid()
        if i < times:
            root.after(interval, toggle, i + 1)
    toggle(0)

def explosion_effect(duration=800):
    def draw_explosion():
        canvas.lift(root)  # 明示的に root の中で最前面へ
        canvas.place(x=0, y=0)
        canvas.delete("all")
        for i in range(20):
            angle = i * (360 / 20)
            x = 260 + 200 * math.cos(math.radians(angle))
            y = 150 + 200 * math.sin(math.radians(angle))
            canvas.create_line(260, 150, x, y, fill="yellow", width=2)
        canvas.create_oval(240, 130, 280, 170, fill="gold", outline="white")
        root.after(duration, lambda: canvas.place_forget())
    root.after(0, draw_explosion)

def check_combo(combo):
    if combo == ["GENIE"] * 3:
        return "🎊 ジーニー揃い！", big_sound, 100
    elif combo == ["COIN"] * 3:
        return "💰 コイン大当たり！", big_sound, 50
    elif combo == ["CAMEL"] * 3:
        return "🐪 ラクダ中当たり！", small_sound, 20
    elif combo == ["MOON"] * 3:
        return "🌙 月の神秘！", small_sound, 10
    elif combo[0] == combo[1] or combo[1] == combo[2] or combo[0] == combo[2]:
        return "✨ 小当たり！", small_sound, 5
    else:
        return "🙃 はずれ！", lose_sound, 0

def update_label_with_image(label, image_key):
    label.config(image=loaded_images[image_key])
    label.image = loaded_images[image_key]

def show_ranking_window():
    ranking_win = tk.Toplevel(root)
    ranking_win.title("スコアランキング")
    ranking_win.configure(bg="black")
    ranking_win.geometry("300x300")

    tk.Label(ranking_win, text="🏆 スコアランキング", font=("Helvetica", 14, "bold"),
             bg="black", fg="gold").pack(pady=10)

    cursor.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()

    for i, (user, score) in enumerate(rows, start=1):
        entry = f"{i}. {user}：{score} 点"
        tk.Label(ranking_win, text=entry, font=("Helvetica", 12),
                 bg="black", fg="white").pack(anchor="w", padx=20)


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
            root.after(0, lambda: stop_sound.play())
            time.sleep(0.1)

        message, sound, score = check_combo(final)
        root.after(0, lambda: result_label.config(text=message))
        root.after(0, lambda: sound.play())
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
    
def choose_weighted_result(force_level):
    roll = random.random()

    if force_level == 3:  # 超高確率
        if roll < 0.25:
            return ["GENIE"] * 3
        elif roll < 0.5:
            return ["COIN"] * 3
        elif roll < 0.75:
            return ["CAMEL"] * 3
        elif roll < 0.90:
            return semi_match_combo()
    elif force_level == 2:  # 高確率
        if roll < 0.15:
            return ["GENIE"] * 3
        elif roll < 0.35:
            return ["COIN"] * 3
        elif roll < 0.55:
            return ["CAMEL"] * 3
        elif roll < 0.75:
            return semi_match_combo()
    elif force_level == 1:  # 中確率
        if roll < 0.1:
            return ["GENIE"] * 3
        elif roll < 0.25:
            return ["COIN"] * 3
        elif roll < 0.4:
            return ["CAMEL"] * 3
        elif roll < 0.6:
            return semi_match_combo()

    # 通常 or ハズレ
    return [random.choice(reel_symbols) for _ in range(3)]

def spin_individual_reels(force_level=0):
    try:
        try:
            username = username_queue.get_nowait()
        except queue.Empty:
            username = "ゲスト"

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
        final = []

        final = choose_weighted_result(force_level)
        for reel, symbol in enumerate(final):
            for i in range(10):
                temp_symbol = random.choice(reel_symbols)
                root.after(0, lambda r=reel, s=temp_symbol: update_label_with_image(slots[r], s))
                time.sleep(0.05 + i * 0.0015)
            root.after(0, lambda r=reel, s=symbol: update_label_with_image(slots[r], s))
            root.after(0, lambda: stop_sound.play())
            time.sleep(0.1)

        message, sound, score = check_combo(final)
        root.after(0, lambda: result_label.config(text=message))
        root.after(0, lambda: sound.play())
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

spin_lock = threading.Lock()

def start_spin(force_level=0):
    acquired = spin_lock.acquire(timeout=2)
    if not acquired:
        print("⚠️ スロットがロック中で取得できませんでした")
        return
    threading.Thread(target=spin_individual_reels, args=(force_level,)).start()

def trigger_slot_spin(force_level=0):
    if DEBUG:
        force_level = 3
    try:
        username = username_queue.get_nowait()
    except queue.Empty:
        return
    username_queue.put((username, force_level))
    if DEBUG:
        force_level = 3
    root.after(0, lambda: start_spin(force_level))

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
