import os
import shutil
from dotenv import load_dotenv

# .envの自動生成処理
TEMPLATE_FILE = ".env.template"
ENV_FILE = "setting.env"

if not os.path.exists(ENV_FILE):
    if os.path.exists(TEMPLATE_FILE):
        shutil.copyfile(TEMPLATE_FILE, ENV_FILE)
        print(f"✅ '{ENV_FILE}' を '{TEMPLATE_FILE}' から作成しました。")
    else:
        print(f"⚠️ '{TEMPLATE_FILE}' が存在しないため、'{ENV_FILE}' を作成できません。")

# .envファイル読み込み
load_dotenv(ENV_FILE)

# Twitch API関連
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_SECRET = os.getenv("TWITCH_SECRET")

# アクセストークン
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_APP")      # App Token
ACCESS_TOKEN_USER = os.getenv("ACCESS_TOKEN_USER")  # User Token

# ユーザー情報
USER_ID = os.getenv("USER_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# OAuth設定
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_CODE = os.getenv("AUTH_CODE")