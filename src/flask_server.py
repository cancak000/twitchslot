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
        message_id = request.headers.get("Twitch-Eventsub-Message-Id")
        timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp")
        message_type = request.headers.get("Twitch-Eventsub-Message-Type", "").lower()
        signature_header = request.headers.get("Twitch-Eventsub-Message-Signature", "")
        body = request.data.decode("utf-8")

        hmac_message = message_id + timestamp + body
        expected = hmac.new(WEBHOOK_SECRET.encode(), hmac_message.encode(), hashlib.sha256).hexdigest()
        actual = signature_header.split("sha256=")[-1]

        print("📦 受信内容:", request.json)

        if not hmac.compare_digest(expected, actual):
            print("\u274c 署名検証失敗")
            return "Invalid signature", 403

        body_json = json.loads(body)

        if message_type == "webhook_callback_verification":
            return body_json["challenge"], 200

        if message_type == "notification":
            event = body_json["event"]
            reward_title = event["reward"]["title"]
            username = event["user_name"]

            valid_titles = {"スロットを回す", "スロット中確率", "スロット大当たりフラグ"}
            if reward_title not in valid_titles:
                print(f"\u26a0\ufe0f \u7121\u52b9\u306a\u30ea\u30ef\u30fc\u30c9\uff1a{reward_title}")
                return "", 204

            force_level = {
                "\u30b9\u30ed\u30c3\u30c8\u5927\u5f53\u305f\u308a\u30d5\u30e9\u30b0": 3,
                "\u30b9\u30ed\u30c3\u30c8\u4e2d\u78ba\u7387": 2,
                "\u30b9\u30ed\u30c3\u30c8\u3092\u56de\u3059": 0
            }.get(reward_title, 0)

            print(f"\U0001f3ae {username} \u304c\u300c{reward_title}\u300d\u3092\u4f7f\u7528\uff08force_level={force_level}\uff09")
            username_queue.put((username, force_level))
            return "", 200

        return "", 204

    except Exception as e:
        logging.exception("\u274c EventSub\u51e6\u7406\u4e2d\u306b\u30a8\u30e9\u30fc\u767a\u751f")
        return "Internal Server Error", 500


def start_flask_server():
    app.run(port=5000, use_reloader=False, threaded=True)
