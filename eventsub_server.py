from flask import Flask, request
import json
import hmac
import hashlib
import os

# slotgameとの連動
from slot_game import trigger_slot_spin

app = Flask(__name__)

# Twitch Developer 設定
TWITCH_CLIENT_ID = "あなたのTwitch ClientID"
TWITCH_SECRET = "あなたのTwitch Secret"

# EventSub の検証用 secret（自由に決めてOK）
WEBHOOK_SECRET = "ivslotsecret"

@app.route("/", methods=["GET"])
def index():
    return "iV Slot EventSub Webhook is running!"

@app.route("/eventsub", methods=["POST"])
def eventsub():
    # Twitch署名の検証
    message_id = request.headers.get("Twitch-Eventsub-Message-Id")
    timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp")
    message_type = request.headers.get("Twitch-Eventsub-Message-Type")
    body = request.data.decode("utf-8")

    hmac_message = message_id + timestamp + body
    expected = hmac.new(WEBHOOK_SECRET.encode(), hmac_message.encode(), hashlib.sha256).hexdigest()
    actual = request.headers.get("Twitch-Eventsub-Message-Signature", "").split("sha256=")[-1]

    if not hmac.compare_digest(expected, actual):
        print("❌ 署名検証失敗")
        return "Invalid signature", 403

    # イベントタイプ別処理
    body_json = json.loads(body)

    if message_type == "webhook_callback_verification":
        print("✅ EventSub 登録確認")
        return body_json["challenge"], 200

    if message_type == "notification":
        event = body_json["event"]
        print("🎮 チャネポ使用検知！ユーザー：", event["user_name"])

        # slotを回す
        trigger_slot_spin() 

        return "", 200

    print("通知を受信:", body_json)
    return "", 204

if __name__ == "__main__":
    app.run(port=5000)