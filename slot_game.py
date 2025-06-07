import tkinter as tk
import random
import time
import threading

import pygame

# ← Trueにするとdebug_buttonが表示される
DEBUG = False

pygame.mixer.init()

# スロット絵柄
symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

# GUIセットアップ
root = tk.Tk()
root.title("iV Slot")
root.geometry("400x250")

if DEBUG:
    root.geometry("400x300")

root.configure(bg="black")

# グローバル変数
stop_sound = pygame.mixer.Sound("sound/stop.mp3")
big_sound = pygame.mixer.Sound("sound/big_win.mp3")
small_sound = pygame.mixer.Sound("sound/small_win.mp3")
lose_sound = pygame.mixer.Sound("sound/lose.mp3")

spin_button = None
debug_button = None

# スロットリール
slots = [tk.Label(root, text="❔", font=("Segoe UI Emoji", 48), bg="black", fg="white") for _ in range(3)]
for i, label in enumerate(slots):
    label.grid(row=1, column=i, padx=20, pady=(10, 0))  # 行を1に、余白調整

# 判定ラベル
result_label = tk.Label(root, text="", font=("Helvetica", 24, "bold"), bg="black", fg="white")
result_label.grid(row=2, column=0, columnspan=3, pady=(10, 20))

# スロットを1リールずつ停止させるアニメーション
def spin_individual_reels(force_win=False):
    global spin_button, debug_button

    #ボタン無効化
    spin_button.config(state="disabled")
    if DEBUG:
        debug_button.config(state="disabled")

    result_label.config(text="")
    final = []
    # 各リールの回転数
    spin_times = [10, 10, 10]  

    for reel in range(3):
            for i in range(spin_times[reel]):
                symbol = random.choice(symbols)
                slots[reel].config(text=symbol)
                root.update()
                time.sleep(0.05 + i * 0.0015)

            if force_win:
                smbl = "💎"
                slots[reel].config(text=smbl)
                final.append(smbl)  # 最終絵柄を保存
            else:
                final.append(slots[reel].cget("text"))  # 最終絵柄を保存
        
            stop_sound.play()

    # 判定
    if final[0] == final[1] == final[2]:
        result_label.config(text="🎉 大当たり！")
        big_sound.play()

    elif final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        result_label.config(text="✨ 小当たり！")
        small_sound.play()

    else:
        result_label.config(text="🙃 はずれ！")
        lose_sound.play()

    #ボタン無効化
    spin_button.config(state="normal")
    if DEBUG:
        debug_button.config(state="normal")

# スレッド起動用
def start_spin(force_win=False):
    threading.Thread(target=spin_individual_reels, args=(force_win,)).start()

def main():
    global spin_button, debug_button

    # スタートボタン
    spin_button = tk.Button(root, text="スロットを回す", font=("Helvetica", 16), padx=16, pady=6, command=start_spin)
    spin_button.grid(row=3, column=0, columnspan=3, pady=(0, 20))

    if DEBUG:
        # DEBUGボタン
        debug_button = tk.Button(root, text="大当たりチェック", font=("Helvetica", 10), padx=10, pady=4, command=lambda: start_spin(True))
        debug_button.grid(row=4, column=1, columnspan=1, pady=(0, 10))

    # 起動
    root.mainloop()

if __name__ == "__main__":
    main()