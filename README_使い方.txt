# 🎰 iV Slot の使い方

## ✅ セットアップ手順

1. `ngrok.exe` を `twitchslot_gui.exe` と同じフォルダに配置します。
2. `setting.env` をテキストエディタで開き、自分の Twitch 情報を記入します（詳しくは下記）。
3. `twitchslot_gui.exe` をダブルクリックで実行します。
4. Twitch のチャンネルポイント報酬に「スロットを回す」などのリワードを作成します。

> ⚠️ `twitchslot_gui.exe` と同じ場所に `setting.env` を置いてください。ファイルがないと起動時にエラーになります。
> ⚠️ 初回起動時は Windows ファイアウォールの警告が出ることがあります。

---

## 📄 setting.env の設定方法（詳しく）

このアプリを使うには、Twitch連携用の設定ファイル `setting.env` を準備する必要があります。
以下の手順に従って、各項目を設定してください。

### 🔧 1. Twitchアプリを作成する


1. [Twitch Developer Console](https://dev.twitch.tv/console/apps) にアクセス
2. 新規アプリケーションを作成：「アプリケーションを登録」

項目設定は
名前：任意

OAuthのリダイレクトURL
http://localhost:5000 を追加してください

カテゴリー
Application Integration を設定してください

クライアントのタイプ
●機密保持について

reCAPTCHAを認証

でてきた　クライアントIDが　クライアントIDの部分です。
クライアントの秘密部分が
TWITCH_SECRETになります。

3. 作成後に以下の情報を取得し、`setting.env` に記述します：

| 項目名                   | 説明                                                        |
| --------------------- | --------------------------------------------------------- |
| `TWITCH_CLIENT_ID`    | アプリ作成後に表示される「Client ID」                                   |
| `TWITCH_SECRET`       | アプリ作成後に生成される「Client Secret」                               |
| `TWITCH_CALLBACK_URL` | 自動で取得されるため、入力不要です。 |
| `REDIRECT_URI`        | `http://localhost:5000`（固定値でOK）                           |

### 👤 2. 自分のTwitch情報を取得する

| 項目名              | 説明                                  |
| ---------------- | ----------------------------------- |
| `USER_ID`        | 自分の Twitch の「ユーザーID（数値）」            |
| `WEBHOOK_SECRET` | 任意の文字列。EventSub検証用。例：`ivslotsecret` |

USER_IDの取得方法は
https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
こちらでUSERIDを入力して取得してください。

### 🔐 3. アクセストークン・リフレッシュトークンを取得

OAuth2フローで取得し、以下の情報を `setting.env` に追記します：

| 項目名                    | 説明                         |
| ---------------------- | -------------------------- |
| `ACCESS_TOKEN_APP`     | App Access Token（アプリとして使う） |
| `ACCESS_TOKEN_USER`    | EventSub 用のユーザー認証トークン      |
| `TWITCH_REFRESH_TOKEN` | トークン更新用                    |
| `AUTH_CODE`            | OAuth の認可コード（必要に応じて）       |

アクセストークンは同梱してある
get_token_gui.exe
を使って、TWITCH_CLIENT_IDとTWITCH_CLIENT_SECRETを入力して取得します。


client_id部分を先ほどのTWITCH_CLIENTIDに
client_secret部分を先ほどのTWITCH_SECRETに設定したところに

AUTH_CODEは 認可URLボタンをクリックした際にURL内にある AUTH_CODE 部分になります。
http://localhost:5000/?code="AUTH_CODE"& ~~~

これをコピペして設定した後にACCESS_TOKEN_USERを取得と押すと取得ができます。


### 📝 setting.env の記述例

```env
TWITCH_CLIENT_ID=your_client_id
TWITCH_SECRET=your_client_secret
ACCESS_TOKEN_APP=your_app_token
ACCESS_TOKEN_USER=your_user_token
TWITCH_CALLBACK_URL=https://xxxxx.ngrok-free.app/eventsub
TWITCH_REFRESH_TOKEN=your_refresh_token
USER_ID=123456789
WEBHOOK_SECRET=ivslotsecret
REDIRECT_URI=http://localhost:5000
AUTH_CODE=
```

---

## 🎮 チャンネルポイント報酬を設定する

Twitch ダッシュボードから、以下の報酬を作成してください：

| 報酬名         | 説明               |
| ----------- | ---------------- |
| スロットを回す     | スロットを実行するためのトリガー |
| スロット中確率     | スロット中の確率を操作（任意）  |
| スロット大当たりフラグ | ジャックポット強制演出（任意）  |

※ 各報酬の `Reward ID` はログ (`log.txt`) に出力されるか、手動で取得してください。

---

## 📌 注意事項

* `.env` や `setting.env` は GitHub 等にアップロードしないよう注意してください（**機密情報が含まれます**）
* `ngrok` の公開URLは再起動ごとに変わるため、`TWITCH_CALLBACK_URL` の再設定が必要になる場合があります
* `.exe` 版でも `setting.env` を**同じフォルダに配置**してください

---

以上で設定は完了です！お疲れさまでした 🙌
