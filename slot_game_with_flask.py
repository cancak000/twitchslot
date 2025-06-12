# slot用
import tkinter as tk
import random
import time
import threading
import pygame

# server用
from flask import Flask, request
import json
import hmac
import hashlib
import os

from config import TWITCH_CLIENT_ID, TWITCH_SECRET, WEBHOOK_SECRET
#log用
import traceback

# USERNAMEの追加
import queue
username_queue = queue.Queue()

# 設定
DEBUG = False

# Flaskセットアップ
app = Flask(__name__)

# GUIセットアップ
root = tk.Tk()
root.title("iV Slot")
root.geometry("400x350" if DEBUG else "400x250")

root.configure(bg="black")

# スロット絵柄
symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]


# pygameサウンド初期化
pygame.mixer.init()

stop_sound = pygame.mixer.Sound("sound/stop.mp3")
big_sound = pygame.mixer.Sound("sound/big_win.mp3")
small_sound = pygame.mixer.Sound("sound/small_win.mp3")
lose_sound = pygame.mixer.Sound("sound/lose.mp3")


#UI 

# スロットリール
slots = [tk.Label(root, text="❔", font=("Segoe UI Emoji", 48), bg="black", fg="white") for _ in range(3)]
for i, label in enumerate(slots):
    label.grid(row=1, column=i, padx=20, pady=(10, 0))  

# 判定ラベル
result_label = tk.Label(root, text="", font=("Helvetica", 24, "bold"), bg="black", fg="white")
result_label.grid(row=2, column=0, columnspan=3, pady=(10, 20))

# 視聴者名表示ラベル
username_label = tk.Label(root, text="", font=("Helvetica", 14, "bold"), bg="black", fg="cyan")
username_label.grid(row=0, column=0, columnspan=3, pady=(10, 0))

debug_button = None
if DEBUG:
    debug_button = tk.Button(root, text="大当たりチェック", font=("Helvetica", 10),
                             padx=10, pady=4, command=lambda: start_spin(True))
    debug_button.grid(row=4, column=1, pady=(0, 10))


# スロットを1リールずつ停止させるアニメーション
def spin_individual_reels(force_win=False):

    # 視聴者名の表示処理
    try:
        username = username_queue.get_nowait()
        root.after(0, lambda: username_label.config(text=f"{username} さんが \n スロットを回しています"))
    except queue.Empty:
        root.after(0, lambda: username_label.config(text=""))

    def set_result(text, sound):
        result_label.config(text=text)
        root.after(0, lambda: sound.play())

    def update_label(label, text):
        label.config(text=text)

    # ラベル初期化
    # GUI操作をメインスレッドに投げる
    root.after(0, lambda: result_label.config(text=""))

    final = []
    # 各リールの回転数
    spin_times = [10, 10, 10]  

    for reel in range(3):
        for i in range(spin_times[reel]):
            symbol = random.choice(symbols)
            root.after(0, lambda r=reel, s=symbol: update_label(slots[r], s))
            time.sleep(0.05 + i * 0.0015)

        if force_win:
            smbl = "💎"
        else:
            smbl = random.choice(symbols)

        final.append(smbl)
        root.after(0, lambda r=reel, s=smbl: update_label(slots[r], s))
        root.after(0, lambda: stop_sound.play())
        time.sleep(0.1)

    # 判定（メインスレッドに投げる）
    if final[0] == final[1] == final[2]:
        root.after(0, lambda: set_result("🎉 大当たり！", big_sound))
    elif final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        root.after(0, lambda: set_result("✨ 小当たり！", small_sound))
    else:
        root.after(0, lambda: set_result("🙃 はずれ！", lose_sound))

# スレッド起動用
def start_spin(force_win=False):
    threading.Thread(target=spin_individual_reels, args=(force_win,)).start()

# ngrokのWebhookトリガー用
def trigger_slot_spin(force_win=False):
    root.after(0, lambda: start_spin(force_win))


#############Flask##################

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
        # ヘッダー取得
        message_id = request.headers.get("Twitch-Eventsub-Message-Id")
        timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp")
        message_type = request.headers.get("Twitch-Eventsub-Message-Type", "").lower()
        signature_header = request.headers.get("Twitch-Eventsub-Message-Signature", "")
        body = request.data.decode("utf-8")

        print("====")
        print(body)

        # --- JSONロード前 --- #
        try:
            body_json = json.loads(body)
        except Exception as e:
            print(e)

        # Twitch署名の検証
        hmac_message = message_id + timestamp + body
        expected = hmac.new(WEBHOOK_SECRET.encode(), hmac_message.encode(), hashlib.sha256).hexdigest()
        actual = signature_header.split("sha256=")[-1]

        # 署名が一致しない場合（今は一時的にスキップ中）
        if not hmac.compare_digest(expected, actual):
            print("❌ 署名検証失敗")
            return "Invalid signature", 403

        body_json = json.loads(body)

        if message_type == "webhook_callback_verification":
            print("✅ EventSub 登録確認")
            return body_json["challenge"], 200

        if message_type == "notification":
            event = body_json["event"]
            username = event["user_name"]
            print("🎮 チャネポ使用検知！ユーザー：", event["user_name"])
            username_queue.put(username)
            trigger_slot_spin()
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


if __name__ == "__main__":
    app.config['DEBUG'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = False
    print("✅ スクリプト起動") 
    threading.Thread(target=start_flask_server, daemon=True).start()
    root.mainloop()
