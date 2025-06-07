
# 🎰 Twitch Slot Machine

Twitch配信やOBS連携に使える、Python製のスロットマシンです。  
GUIは `tkinter`、効果音再生は `pygame` を使用しています。

---

## 📸 スクリーンショット

![screenshot](screenshots/demo.png)  
※スクリーンショットは任意で追加してください（`screenshots` フォルダを作るとよいです）

---

## 🔧 特徴

- GUIでスロット演出
- 1リールずつアニメーション付きで停止
- 効果音付き（stop / win / lose）
- デバッグモード（大当たり強制モード）
- Twitch配信やOBS画面に表示して使える

---

## 💽 必要環境

- Python 3.8 以上  
- `pygame`  
- `tkinter`（標準で含まれている）

---

## 📦 インストール

```bash
pip install pygame
```

---

## ▶️ 使い方

```bash
python slot_machine.py
```

---

## 🐞 デバッグモードをONにする

```python
# slot_machine.py の冒頭で設定
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

## 📁 ディレクトリ構成（例）

```
twitchslot/
├── slot_machine.py
├── sound/
│   ├── stop.mp3
│   ├── big_win.mp3
│   ├── small_win.mp3
│   └── lose.mp3
└── README.md
```

---

## 📜 ライセンス

MITライセンス
