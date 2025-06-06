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

# スロットリール表示
slots = [tk.Label(root, text="❔", font=("Helvetica", 48), bg="black", fg="white") for _ in range(3)]
for i, label in enumerate(slots):
    label.grid(row=0, column=i, padx=20)

# 結果表示
result_label = tk.Label(root, text="", font=("Helvetica", 20), bg="black", fg="white")
result_label.grid(row=1, column=0, columnspan=3, pady=10)

# スロットを1リールずつ停止させるアニメーション
def spin_individual_reels():
    result_label.config(text="")
    final = []

    spin_times = [10, 10, 10]  # 各リールの回転数（段階的に長く）

    for reel in range(3):
        for i in range(spin_times[reel]):
            symbol = random.choice(symbols)
            slots[reel].config(text=symbol)
            root.update()
            time.sleep(0.05 + i * 0.0015)
        final.append(slots[reel].cget("text"))  # 最終絵柄を保存
        pygame.mixer.music.load("sound/stop.mp3")
        pygame.mixer.music.play()

    # 判定
    if final[0] == final[1] == final[2]:
        result_label.config(text="🎉 大当たり！")
        pygame.mixer.music.load("sound/big_win.mp3")
        pygame.mixer.music.play()

    elif final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        result_label.config(text="✨ 小当たり！")
        pygame.mixer.music.load("sound/small_win.mp3")
        pygame.mixer.music.play()

    else:
        result_label.config(text="🙃 はずれ！")
        pygame.mixer.music.load("sound/lose.mp3")
        pygame.mixer.music.play()

# スレッド起動用
def start_spin():
    threading.Thread(target=spin_individual_reels).start()

# スタートボタン
spin_button = tk.Button(root, text="スロットを回す", font=("Helvetica", 16), command=start_spin)
spin_button.grid(row=2, column=0, columnspan=3, pady=10)

# 起動
root.mainloop()