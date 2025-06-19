import tkinter as tk
from tkinter import messagebox
import requests
import webbrowser


class TwitchTokenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitch トークン一括取得ツール")
        self.root.geometry("520x620")

        # Client ID & Secret
        tk.Label(root, text="Client ID:").pack()
        self.client_id_entry = tk.Entry(root, width=60)
        self.client_id_entry.pack()

        tk.Label(root, text="Client Secret:").pack()
        self.client_secret_entry = tk.Entry(root, width=60, show='*')
        self.client_secret_entry.pack()

        # App Token
        tk.Button(root, text="① App Access Token 取得", command=self.get_app_token).pack(pady=10)
        tk.Label(root, text="ACCESS_TOKEN_APP:").pack()
        self.app_token_box = tk.Text(root, height=2, width=60)
        self.app_token_box.pack()

        # OAuth
        tk.Button(root, text="② 認可URLを開く (ユーザートークン)", command=self.open_auth_url).pack(pady=10)
        tk.Label(root, text="AUTH_CODE:").pack()
        self.auth_code_entry = tk.Entry(root, width=60)
        self.auth_code_entry.pack()

        # User Token
        tk.Button(root, text="③ ACCESS_TOKEN_USER を取得", command=self.get_user_token).pack(pady=10)
        tk.Label(root, text="ACCESS_TOKEN_USER:").pack()
        self.user_token_box = tk.Text(root, height=2, width=60)
        self.user_token_box.pack()

        tk.Label(root, text="TWITCH_REFRESH_TOKEN:").pack()
        self.refresh_token_box = tk.Text(root, height=2, width=60)
        self.refresh_token_box.pack()

    def get_app_token(self):
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        url = 'https://id.twitch.tv/oauth2/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        try:
            res = requests.post(url, data=data)
            res.raise_for_status()
            token = res.json().get("access_token", "")
            self.app_token_box.delete("1.0", tk.END)
            self.app_token_box.insert(tk.END, token)
        except Exception as e:
            messagebox.showerror("App Token 取得失敗", str(e))

    def open_auth_url(self):
        client_id = self.client_id_entry.get()
        scopes = "channel:read:redemptions channel:manage:redemptions user:read:email"
        url = (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri=http://localhost:5000"
            f"&response_type=code"
            f"&scope={scopes.replace(' ', '+')}"
        )
        webbrowser.open(url)

    def get_user_token(self):
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        auth_code = self.auth_code_entry.get()
        url = "https://id.twitch.tv/oauth2/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:5000",
        }
        try:
            res = requests.post(url, data=data)
            res.raise_for_status()
            result = res.json()
            self.user_token_box.delete("1.0", tk.END)
            self.user_token_box.insert(tk.END, result.get("access_token", ""))
            self.refresh_token_box.delete("1.0", tk.END)
            self.refresh_token_box.insert(tk.END, result.get("refresh_token", ""))
        except Exception as e:
            messagebox.showerror("ユーザー Token 取得失敗", str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app = TwitchTokenApp(root)
    root.mainloop()