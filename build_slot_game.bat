@echo off
echo === スロットゲームのビルドを開始します ===

REM 仮想環境などがあれば activate

REM .exe ビルド（sound フォルダを同梱）
pyinstaller --noconfirm --noconsole --onefile --add-data "sound;sound" slot_game.py

REM 実行ファイルを開く（任意）
start dist\slot_game.exe

echo.
echo ✅ スロットゲームのビルドと起動が完了しました！
pause
