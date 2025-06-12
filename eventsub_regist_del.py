import requests
from config import TWITCH_CLIENT_ID, ACCESS_TOKEN

# 削除対象のsubscription_idリストを置き換えること
subscription_ids = [
    "1aaa182b-a60b-4966-9d0a-fdf334d78b76",
    "e0cd508b-e037-44a5-a578-e6e159875f2b",
    "c3b386c5-9d50-46aa-83bb-7f302dceadf8",
    "1851dfcb-580c-456c-a022-edaf2465dd51",
    "bf11f36c-2e9e-436e-975f-958fefe7afea"
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