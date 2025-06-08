import requests

ACCESS_TOKEN = "アクセストークン"  
CLIENT_ID = "クライアントID"

def get_user_id():
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Client-Id": CLIENT_ID
    }
    response = requests.get("https://api.twitch.tv/helix/users", headers=headers)
    data = response.json()
    print("ユーザーID:", data["data"][0]["id"])
    print("表示名:", data["data"][0]["display_name"])
    return data["data"][0]["id"]

get_user_id()