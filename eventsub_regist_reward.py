import requests
from config import TWITCH_CLIENT_ID, USER_ID, ACCESS_TOKEN_USER  # ACCESS_TOKEN_USER = 上記で取得したaccess_token

def get_rewards():
    url = "https://api.twitch.tv/helix/channel_points/custom_rewards"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN_USER}"
    }
    params = {
        "broadcaster_id": USER_ID
    }

    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        data = res.json().get("data", [])
        if not data:
            print("⚠️ カスタムリワードが見つかりません")
        else:
            print("🎁 カスタムリワード一覧:")
            for reward in data:
                print(f"🔹 {reward['title']} -> {reward['id']}")
    else:
        print(f"❌ リワード取得失敗: {res.status_code} {res.text}")

if __name__ == "__main__":
    get_rewards()