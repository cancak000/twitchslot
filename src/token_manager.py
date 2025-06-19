import os
import requests
from dotenv import load_dotenv

ENV_FILE = "setting.env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_CODE = os.getenv("AUTH_CODE")  # 無ければ None
REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")

def get_user_access_token():
    if not AUTH_CODE:
        print("⚠️ AUTH_CODE が .env に存在しません。手動で取得してください。")
        return None

    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": AUTH_CODE,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        token_data = res.json()
    except requests.exceptions.RequestException as e:
        print("❌ トークン取得失敗:", e)
        return None

    print("✅ 新しいトークンを取得しました")
    update_env({
        "ACCESS_TOKEN_USER": token_data["access_token"],
        "TWITCH_REFRESH_TOKEN": token_data["refresh_token"]
    })

    return token_data["access_token"]

def get_app_token():
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        token_data = res.json()
        return token_data["access_token"]
    except requests.exceptions.RequestException as e:
        print("❌ Appトークン取得失敗:", e)
        return None

def refresh_user_token():
    if not REFRESH_TOKEN:
        print("⚠️ REFRESH_TOKEN が見つかりません")
        return None

    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        token_data = res.json()
    except requests.exceptions.RequestException as e:
        print("❌ リフレッシュ失敗:", e)
        return None

    print("♻️ リフレッシュトークンで再取得完了")
    update_env({
        "ACCESS_TOKEN_USER": token_data["access_token"],
        "TWITCH_REFRESH_TOKEN": token_data["refresh_token"]
    })

    return token_data["access_token"]

def update_env(new_values: dict):
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    keys_updated = set()
    for line in lines:
        if "=" in line:
            key, _ = line.strip().split("=", 1)
            if key in new_values:
                new_lines.append(f"{key}={new_values[key]}\n")
                keys_updated.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    for key, value in new_values.items():
        if key not in keys_updated:
            new_lines.append(f"{key}={value}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    token = get_user_access_token()
    if token is None:
        refresh_user_token()