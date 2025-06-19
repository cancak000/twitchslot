@echo off
echo 🎰 TwitchSlot をビルドします...

pyinstaller ^
  --onefile ^
  --noconsole ^
  --name twitchslot_gui ^
  --add-data "image;image" ^
  --add-data "sound;sound" ^
  --add-data "setting.env;." ^
  slot_game_with_flask.py

echo ✅ ビルド完了！distフォルダを確認してください。
pause