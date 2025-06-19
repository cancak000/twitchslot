import requests
import json

# 必要情報
CLIENT_ID = "あなたのClient ID"
ACCESS_TOKEN = "アクセストークン"
USER_ID = "TwitchのUserID"
WEBHOOK_URL = "ngrokのWebhook URL"
WEBHOOK_SECRET = "WebhookのSecret (ユーザーが作れる)"

def subscribe():
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "type": "channel.channel_points_custom_reward_redemption.add",
        "version": "1",
        "condition": {
            "broadcaster_user_id": USER_ID
        },
        "transport": {
            "method": "webhook",
            "callback": WEBHOOK_URL,
            "secret": WEBHOOK_SECRET
        }
    }

    response = requests.post("https://api.twitch.tv/helix/eventsub/subscriptions",
                             headers=headers, data=json.dumps(payload))

    print("✅ ステータス:", response.status_code)
    print("📦 レスポンス:", response.json())

if __name__ == "__main__":
    subscribe()