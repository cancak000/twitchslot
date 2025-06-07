import tkinter as tk
import random
import time
import threading

import pygame

pygame.mixer.init()

# スロット絵柄
symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

# GUIセットアップ
root = tk.Tk()
root.title("スロットマシン")
root.geometry("400x250")
root.configure(bg="black")

stop_sound = pygame.mixer.Sound("sound/stop.mp3")
big_sound = pygame.mixer.Sound("sound/big_win.mp3")
small_sound = pygame.mixer.Sound("sound/small_win.mp3")
lose_sound = pygame.mixer.Sound("sound/lose.mp3")

# スロットリール表示
slots = [tk.Label(root, text="❔", font=("Helvetica", 48), bg="black", fg="white") for _ in range(3)]
for i, label in enumerate(slots):
    label.grid(row=0, column=i, padx=20)

# 結果表示
result_label = tk.Label(root, text="", font=("Helvetica", 20), bg="black", fg="white")
result_label.grid(row=1, column=0, columnspan=3, pady=10)

# スロットを1リールずつ停止させるアニメーション
def spin_individual_reels(force_win=False):
    result_label.config(text="")
    final = []

    spin_times = [10, 10, 10]  # 各リールの回転数

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

# スレッド起動用
def start_spin(prm):
    threading.Thread(target=spin_individual_reels, args=(prm,)).start()

# スタートボタン
# スタートボタン（修正後）
tk.Button(root, text="スロットを回す", font=("Helvetica", 16), command=lambda: start_spin(False)).grid(row=2, column=0, columnspan=3, pady=10)

# デバッグボタン（修正後）
tk.Button(root, text="大当たりチェック", font=("Helvetica", 8), command=lambda: start_spin(True)).grid(row=3, column=1, columnspan=3, pady=5)

# 起動
root.mainloop()