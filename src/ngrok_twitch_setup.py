# setup_and_register.py
import subprocess
import time
import requests
import json
import os
import hmac
import hashlib
from config import TWITCH_CLIENT_ID, TWITCH_SECRET, USER_ID, WEBHOOK_SECRET

# ----- 設定値 -----
NGROK_PATH = "ngrok.exe"  # ngrok実行ファイルのパス
PORT = 5000

# 1. ngrokを起動
def start_ngrok():
    subprocess.Popen([NGROK_PATH, "http", str(PORT)])
    time.sleep(3)  # 起動待ち

# 2. ngrokの公開URLを取得
def get_ngrok_url():
    try:
        res = requests.get("http://localhost:4040/api/tunnels")
        res.raise_for_status()
        tunnels = res.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("❌ ngrok URL取得失敗:", e)
    return None

# 3. Twitchアクセストークン取得
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

# 4. EventSubを登録
def register_eventsub(token, callback_url):
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
            "callback": f"{callback_url}/eventsub",
            "secret": WEBHOOK_SECRET
        }
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code == 202:
        print("✅ EventSub 登録完了")
    else:
        print(f"❌ EventSub登録失敗: {res.status_code} {res.text}")

if __name__ == "__main__":
    print("🚀 ngrok起動中...")
    start_ngrok()
    url = get_ngrok_url()
    if url:
        print(f"🌐 公開URL: {url}")
        token = get_app_token()
        register_eventsub(token, url)
    else:
        print("❌ 公開URLが取得できませんでした")
