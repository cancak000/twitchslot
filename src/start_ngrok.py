import subprocess
import requests
import time
import json
import os
from dotenv import load_dotenv

NGROK_PATH = "ngrok.exe"  # 同梱
PORT = 5000

def start_ngrok():
    # 既にngrokが起動しているか確認してURL取得
    try:
        res = requests.get("http://localhost:4040/api/tunnels")
        tunnel_info = res.json()
        public_url = tunnel_info['tunnels'][0]['public_url']
        print("🌐 既存のngrok URL:", public_url)
        return public_url
    except:
        pass  # 起動してない場合は下に進む

    # 起動してなければ起動する
    subprocess.Popen([NGROK_PATH, "http", str(PORT)])
    print("⏳ ngrok 起動中...（数秒待ちます）")
    time.sleep(3)

    # 再度取得トライ
    try:
        res = requests.get("http://localhost:4040/api/tunnels")
        tunnel_info = res.json()
        public_url = tunnel_info['tunnels'][0]['public_url']
        print("🌐 公開URL:", public_url)
        return public_url
    except Exception as e:
        print("❌ ngrokのURL取得に失敗:", e)
        return None

def update_env_url(new_url: str, env_path="setting.env"):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(env_path, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("TWITCH_CALLBACK_URL="):
                f.write(f"TWITCH_CALLBACK_URL={new_url}/eventsub\n")
            else:
                f.write(line)

    print(f"✅ {env_path} を更新: {new_url}/eventsub")
    load_dotenv(env_path, override=True)