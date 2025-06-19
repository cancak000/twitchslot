import requests
import config  # ← config.py をインポート

headers = {
    "Client-ID": config.TWITCH_CLIENT_ID,
    "Authorization": f"Bearer {config.ACCESS_TOKEN}"
}

url = "https://api.twitch.tv/helix/eventsub/subscriptions"
response = requests.get(url, headers=headers)

print(f"✅ Status Code: {response.status_code}")
print("📦 登録中のサブスクリプション一覧（整形表示）:")
print(response.text)