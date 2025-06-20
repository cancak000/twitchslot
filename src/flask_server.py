# flask_server.py
from flask import Flask, request
import json, hmac, hashlib, traceback
import logging
from config import WEBHOOK_SECRET
from queue import Queue

# 外部に共有するキュー（main側と共有するため）
username_queue = Queue()

# Flask アプリ
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "iV Slot EventSub Webhook is running!"

@app.route("/eventsub", methods=["POST"])
def eventsub():
    try:
        print("✅ POST 受信しました")
        print("📦 headers:", dict(request.headers))
        print("📦 raw body:", request.data.decode("utf-8"))

        # Twitchからの署名検証
        message_id = request.headers.get("Twitch-Eventsub-Message-Id")
        timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp")
        message_type = request.headers.get("Twitch-Eventsub-Message-Type", "").lower()
        signature_header = request.headers.get("Twitch-Eventsub-Message-Signature", "")
        body = request.data.decode("utf-8")

        hmac_message = message_id + timestamp + body
        expected = hmac.new(WEBHOOK_SECRET.encode(), hmac_message.encode(), hashlib.sha256).hexdigest()
        actual = signature_header.split("sha256=")[-1]

        # JSONロード＆出力
        body_json = json.loads(body)
        print("📦 受信内容（body_json）:", body_json)

        if not hmac.compare_digest(expected, actual):
            print("❌ 署名検証失敗")
            return "Invalid signature", 403

        if message_type == "webhook_callback_verification":
            print("📡 webhook検証リクエストを受信")
            return body_json["challenge"], 200

        if message_type == "notification":
            event = body_json["event"]
            reward_title = event["reward"]["title"]
            username = event["user_name"]
            valid_titles = {"スロットを回す", "スロット中確率", "スロット大当たりフラグ"}
            if reward_title not in valid_titles:
                print(f"⚠️ 無効なリワード「{reward_title}」")
                return "", 204

            force_level = {
                "スロット大当たりフラグ": 3,
                "スロット中確率": 2,
                "スロットを回す": 0
            }.get(reward_title, 0)

            print(f"🎮 {username} が「{reward_title}」使用！ force_level={force_level}")
            username_queue.put((username, force_level))
            return "", 200

        return "", 204

    except Exception:
        logging.exception("❌ EventSub 処理中に例外")
        return "Internal Server Error", 500


@app.route("/routes")
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(f"{rule.methods} {rule.rule}")
    return "<br>".join(output)


def start_flask_server():
    app.run(host="0.0.0.0", port=5000, use_reloader=False, threaded=True)
