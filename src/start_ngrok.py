import subprocess
import requests
import time
import json
import os
from dotenv import load_dotenv

NGROK_PATH = "ngrok.exe"  # 同梱
PORT = 5000

ngrok_process = None

def get_public_url():
    try:
        res = requests.get("http://localhost:4040/api/tunnels")
        tunnel_info = res.json()
        return tunnel_info["tunnels"][0]["public_url"]
    except:
        return None

def get_public_url_with_wait(retry=10, wait=1):
    for i in range(retry):
        url = get_public_url()
        if url:
            return url
        print(f" ngrokのURL待機中... ({i+1}/{retry})")
        time.sleep(wait)
    print("ngrokのURL取得に失敗しました")
    return None

def start_ngrok():
    global ngrok_process
    # 既にngrokが起動しているか確認してURL取得
    if get_public_url():
        print("ngrokは既に起動済みです。")
        return get_public_url()
    
    ngrok_process = subprocess.Popen([NGROK_PATH, "http", str(PORT)])
    print("ngrokを起動しました。URL取得中...")

    return get_public_url_with_wait()

def stop_ngrok():
    global ngrok_process
    if ngrok_process:
        ngrok_process.terminate()

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

