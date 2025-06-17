import requests
from config import TWITCH_CLIENT_ID, TWITCH_SECRET, REDIRECT_URI, AUTH_CODE

def get_user_token():
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_SECRET,
        "code": "s8u623hjfbclcuiscvc660yinymiow",
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    res = requests.post(url, data=data)
    res.raise_for_status()

    print("✅ ユーザーアクセストークン取得完了:")
    print(res.json())  # 必要なら保存

if __name__ == "__main__":
    get_user_token()