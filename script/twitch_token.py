import requests

# ここに自分のクライアント情報を入れる
CLIENT_ID = "クライアントID"
CLIENT_SECRET = "クライアントSECRET"

def get_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, params=params)
    data = response.json()

    print("Access Token:", data["access_token"])
    return data["access_token"]

if __name__ == "__main__":
    get_access_token()