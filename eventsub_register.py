import requests
import json
from config import TWITCH_CLIENT_ID, TWITCH_SECRET, USER_ID, WEBHOOK_URL, WEBHOOK_SECRET

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

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code == 202:
        print("✅ EventSub 登録完了")
    else:
        print(f"❌ 登録失敗: {res.status_code} {res.text}")

if __name__ == "__main__":
    token = get_app_token()
    register_eventsub(token)