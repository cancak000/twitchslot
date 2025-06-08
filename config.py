from dotenv import load_dotenv
import os

# .envを読み込む
load_dotenv()

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

# OAuth情報
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_CODE = os.getenv("AUTH_CODE")