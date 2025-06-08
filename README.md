# 🎰 Twitch iV Slot

"iV Slot" は、Twitch配信と連携できるスロットゲームです。
配信者のチャンネルポイントでスロットを回すことができ、視覚・聴覚的に楽しめるエフェクト付きのGUIアプリケーションです。

---

## 📸 スクリーンショット

![screenshot](screenshots/demo.jpg)

---

## 🔧 特徴

* GUIでスロット演出
* 1リールずつアニメーション付きで停止
* 効果音付き（stop / win / lose）
* デバッグモード（大当たり強制モード）
* Twitch配信やOBS画面に表示して使える
* EventSub webhook連携によりチャンネルポイント連動

---

## 💽 必要環境

* Python 3.8 以上（推奨：3.13）
* `pygame`
* `tkinter`（標準で含まれている）
* `Flask`（Twitch連携時）

---

## 📦 インストール

```bash
pip install pygame flask python-dotenv requests
```

---

## ▶️ 使い方

### 🔁 クローン版（スタンドアロン）

```bash
python slot_game.py
```

### 🌐 Twitch EventSub連携版

```bash
python slot_game_with_flask.py
```

チャンネルポイントの報酬がトリガーとなり、自動的にスロットが回ります。

---

## 🐞 デバッグモードをONにする

```python
# slot_game.py または slot_game_with_flask.py の冒頭
DEBUG = True
```

これにより「大当たりチェック」ボタンがGUIに表示されます。

---

## 🎵 効果音ファイルについて

`/sound` フォルダ内に以下の音声ファイルが必要です：

```
sound/
├── stop.mp3
├── big_win.mp3
├── small_win.mp3
└── lose.mp3
```

---

## ⚙️ Web連携の設定方法（.env）

`.env` ファイルをプロジェクト直下に配置します：

```env
# Twitch Developer
TWITCH_CLIENT_ID=your_client_id
TWITCH_SECRET=your_client_secret
ACCESS_TOKEN_APP=your_app_access_token
ACCESS_TOKEN_USER=your_user_access_token

# Twitch Webhook
USER_ID=your_twitch_user_id
WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app/eventsub
WEBHOOK_SECRET=your_webhook_secret

# OAuth2
REDIRECT_URI=http://localhost:5000
AUTH_CODE=your_oauth_code
```

`.env.template` も参考にしてください。

---

## 🛠️ EXE化（Windows）

```bash
pyinstaller slot_game.py --noconsole --onefile --add-data "sound;sound"
```

* 音声ファイルは `sound/` にまとめておくこと
* `.spec` ファイルで細かい制御も可能

---

## 📁 主なディレクトリ構成

```
twitchslot/
├── sound/                        # サウンドデータ
├── slot_game.py                 # クローン版
├── slot_game_with_flask.py     # Twitch連携版
├── eventsub_register.py        # EventSub登録
├── eventsub_regist_check.py    # 登録チェック
├── eventsub_regist_del.py      # 削除
├── config.py                   # 環境変数読み込み
├── .env.template               # 設定テンプレート
├── .gitignore
└── README.md
```

---

## 🙋‍♂️ 製作者

**イヴ\_ライバル**（Twitch / Python Dev / Streamer）

* X: [https://x.com/almriv4](https://x.com/almriv4)
* Twitch: [https://www.twitch.tv/ivrival](https://www.twitch.tv/ivrival)

---

## 📜 ライセンス

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
