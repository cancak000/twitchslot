@echo off
REM スロットアプリを exe 化
REM image/ sound/ setting.env を含めてビルド

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --add-data "image;image" ^
  --add-data "sound;sound" ^
  --add-data "setting.env;." ^
  src/slot_game_with_flask.py

pause