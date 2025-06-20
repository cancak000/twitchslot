import requests
import json

url = "https://a532-240f-45-22e0-1-7055-9542-a989-e83e.ngrok-free.app/eventsub"

headers = {
    "Content-Type": "application/json",
    "Twitch-Eventsub-Message-Id": "test-id",
    "Twitch-Eventsub-Message-Timestamp": "2025-06-20T00:00:00Z",
    "Twitch-Eventsub-Message-Type": "notification",
    "Twitch-Eventsub-Message-Signature": "sha256=dummy"  # 署名検証は失敗するが、とりあえず送る
}

payload = {
    "subscription": {
        "type": "channel.channel_points_custom_reward_redemption.add"
    },
    "event": {
        "user_name": "テストユーザー",
        "reward": {
            "title": "スロットを回す"
        }
    }
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")