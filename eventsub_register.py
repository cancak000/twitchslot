import requests
import json
from config import TWITCH_CLIENT_ID, TWITCH_SECRET, USER_ID, WEBHOOK_URL, WEBHOOK_SECRET
reward_ids = [
    "d4738510-bc14-48c5-b474-5782e7bec011",  # スロットを回す
    "8588cee9-69c9-42a9-a782-75651080d4c1",  # スロットを回す　中
    "49feda18-9faa-403e-a128-ed8eb720f741"   # スロットを回す　大
]

def get_app_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_SECRET,
        "grant_type": "client_credentials"
    }
    res = requests.post(url, params=params)
    res.raise_for_status()
    return res.json()["access_token"]

def register_eventsub(token):
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    for reward_id in reward_ids:
        payload = {
            "type": "channel.channel_points_custom_reward_redemption.add",
            "version": "1",
            "condition": {
                "broadcaster_user_id": USER_ID,
                "reward_id": reward_id
            },
            "transport": {
                "method": "webhook",
                "callback": WEBHOOK_URL,
                "secret": WEBHOOK_SECRET
            }
        }

        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 202:
            print(f"✅ EventSub 登録完了: {reward_id}")
        else:
            print(f"❌ 登録失敗: reward_id = {reward_id}, {res.status_code} {res.text}")

def register_eventsub_with_user_token(token):

    for reward_id in reward_ids:
        payload = {
            "type": "channel.channel_points_custom_reward_redemption.add",
            "version": "1",
            "condition": {
                "broadcaster_user_id": USER_ID,
                "reward_id": reward_id
            },
            "transport": {
                "method": "webhook",
                "callback": WEBHOOK_URL,
                "secret": WEBHOOK_SECRET
            }
        }

        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        res = requests.post("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers, data=json.dumps(payload))
        if res.status_code == 202:
            print(f"✅ 登録成功: {reward_id}")
        else:
            print(f"❌ 登録失敗: {reward_id} {res.status_code} {res.text}")

if __name__ == "__main__":
    from config import ACCESS_TOKEN_USER  # config.py に保存したユーザーOAuthトークン

    register_eventsub_with_user_token(ACCESS_TOKEN_USER)
