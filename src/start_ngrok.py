import os
import subprocess
import time
import requests
from dotenv import load_dotenv
import logging

PORT = 5000
NGROK_PATH = os.getenv("NGROK_PATH", "ngrok")
ngrok_process = None

from utils import setup_logger
logger = setup_logger("start_ngrok", "slot_game.log", level=logging.INFO)


# --- 関数定義 ---

def get_public_url():
    try:
        res = requests.get("http://localhost:4040/api/tunnels")
        tunnel_info = res.json()
        return tunnel_info["tunnels"][0]["public_url"]
    except Exception as e:
        logger.warning(f"🌐 ngrokのURL取得失敗: {e}")
        return None

def get_public_url_with_wait(retry=10, wait=1):
    for i in range(retry):
        url = get_public_url()
        if url:
            logger.info(f"✅ ngrok URL 取得成功（{i+1}回目）: {url}")
            return url
        logger.info(f"⏳ ngrokのURL待機中... ({i+1}/{retry})")
        time.sleep(wait)
    logger.error("❌ ngrokのURL取得に失敗しました")
    return None

def start_ngrok():
    global ngrok_process
    # すでに起動していれば再利用
    url = get_public_url()
    if url:
        logger.info("🔄 ngrokは既に起動済みです")
        return url
    
    ngrok_process = subprocess.Popen([NGROK_PATH, "http", str(PORT)])
    logger.info("🚀 ngrokを新規起動しました")

    return get_public_url_with_wait()

def stop_ngrok():
    global ngrok_process
    if ngrok_process:
        ngrok_process.terminate()
        logger.info("🛑 ngrok停止処理を実行しました")

def update_env_url(new_url: str, env_path="setting.env"):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(env_path, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("TWITCH_CALLBACK_URL="):
                    f.write(f"TWITCH_CALLBACK_URL={new_url}/eventsub\n")
                else:
                    f.write(line)

        load_dotenv(env_path, override=True)
        logger.info(f"✅ {env_path} を更新: {new_url}/eventsub")
    except Exception as e:
        logger.error(f"❌ {env_path} の更新に失敗: {e}")

def wait_for_ngrok_ready(public_url, timeout=10):
    logger.info(f"⏳ Ngrok({public_url}/eventsub) の公開確認中...")
    for _ in range(timeout):
        try:
            res = requests.options(public_url + "/eventsub")
            if res.status_code in [200, 405]:
                logger.info("✅ Ngrok 公開URL 応答確認成功")
                return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"📡 OPTIONS失敗: {e}")
        time.sleep(1)
    logger.error("❌ ngrokの公開URLが起動しませんでした")
    raise RuntimeError("❌ ngrokトンネル未応答")