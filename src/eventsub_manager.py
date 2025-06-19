import os
import requests
from dotenv import load_dotenv

ENV_FILE = "setting.env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_SECRET")
USER_ID = os.getenv("USER_ID")
TWITCH_CALLBACK_URL = os.getenv("TWITCH_CALLBACK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


def get_existing_eventsubs(app_token):
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {app_token}"
    }
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("data", [])
    print("❌ EventSub取得失敗:", res.status_code, res.text)
    return []


def delete_existing_matching_eventsubs(app_token, reward_ids):
    subs = get_existing_eventsubs(app_token)
    for sub in subs:
        if sub["type"] == "channel.channel_points_custom_reward_redemption.add":
            condition = sub.get("condition", {})
            if condition.get("reward_id") in reward_ids:
                sub_id = sub["id"]
                url = f"https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}"
                headers = {
                    "Client-ID": CLIENT_ID,
                    "Authorization": f"Bearer {app_token}"
                }
                res = requests.delete(url, headers=headers)
                print(f"🧹 削除済: {sub_id}, status={res.status_code}")


def register_eventsub(app_token, reward_ids):
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {app_token}",
        "Content-Type": "application/json"
    }
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"

    for reward_id in reward_ids:
        data = {
            "type": "channel.channel_points_custom_reward_redemption.add",
            "version": "1",
            "condition": {
                "broadcaster_user_id": USER_ID,
                "reward_id": reward_id
            },
            "transport": {
                "method": "webhook",
                "callback": TWITCH_CALLBACK_URL,
                "secret": WEBHOOK_SECRET
            }
        }

        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 202:
            print(f"✅ 登録成功: reward_id = {reward_id}")
        else:
            print("=====================")
            print(TWITCH_CALLBACK_URL)
            print("=====================")
            print(f"❌ 登録失敗: reward_id = {reward_id}, {res.status_code} {res.text}")


def get_reward_ids(user_access_token):
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {user_access_token}"
    }
    url = f"https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id={USER_ID}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        rewards = res.json().get("data", [])
        return [reward["id"] for reward in rewards]
    print("❌ リワードID取得失敗:", res.status_code, res.text)
    return []


if __name__ == "__main__":
    from token_manager import refresh_user_token, get_app_token

    print("🔄 EventSub再登録処理中...")
    user_token = refresh_user_token()
    app_token = get_app_token()

    if user_token and app_token:
        reward_ids = get_reward_ids(user_token)
        delete_existing_matching_eventsubs(app_token, reward_ids)
        register_eventsub(app_token, reward_ids)
    else:
        print("❌ トークンの取得に失敗しました")