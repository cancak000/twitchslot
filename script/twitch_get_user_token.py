import requests

CLIENT_ID = "クライアントID"
CLIENT_SECRET = "クライアントSecret"
REDIRECT_URI = "http://localhost:5000"
AUTH_CODE = ""

def get_user_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": AUTH_CODE,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(url, data=data)
    token_data = response.json()

    if "access_token" in token_data:
        print("✅ アクセストークン取得成功！")
        print("Access Token:", token_data["access_token"])
        print("Refresh Token:", token_data["refresh_token"])
    else:
        print("❌ 失敗しました：", token_data)

get_user_access_token()