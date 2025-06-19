import requests
from config import TWITCH_CLIENT_ID, ACCESS_TOKEN

# 削除対象のsubscription_idリストを置き換えること
subscription_ids = [
    "e95e4fb2-2b54-4184-83cc-3b6d6264b52e",
    "1950f91b-91b8-40a3-a2a3-86a178fc72fd"
]

# ヘッダー設定
headers = {
    "Client-ID": TWITCH_CLIENT_ID,
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# 削除実行
for sub_id in subscription_ids:
    url = f"https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}"
    response = requests.delete(url, headers=headers)
    print(f"🗑️ 削除 {sub_id} -> {response.status_code}")