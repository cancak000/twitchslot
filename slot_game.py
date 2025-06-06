import tkinter as tk
import random
import time
import threading

# 絵柄一覧
symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

# ウィンドウ作成
root = tk.Tk()
root.title("スロットマシン")
root.geometry("400x200")
root.configure(bg="black")

# ラベル（スロット表示）
slots = [tk.Label(root, text="❔", font=("Helvetica", 48), bg="black", fg="white") for _ in range(3)]
for i, label in enumerate(slots):
    label.grid(row=0, column=i, padx=20)

# 結果表示ラベル
result_label = tk.Label(root, text="", font=("Helvetica", 20), bg="black", fg="white")
result_label.grid(row=1, column=0, columnspan=3, pady=10)

# スロット回転処理?（別スレッドで回す）
def spin():
    result_label.config(text="")
    final = []

    for i in range(15):  # 回転回数
        current = [random.choice(symbols) for _ in range(3)]
        for j in range(3):
            slots[j].config(text=current[j])
        root.update()
        time.sleep(0.1 + i * 0.02)
        final = current

    # 判定
    if final[0] == final[1] == final[2]:
        result_label.config(text="🎉 大当たり！")
    elif final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        result_label.config(text="✨ 小当たり！")
    else:
        result_label.config(text="🙃 はずれ！")

# スタートボタン
def start_spin():
    threading.Thread(target=spin).start()

spin_button = tk.Button(root, text="スロットを回す", font=("Helvetica", 16), command=start_spin)
spin_button.grid(row=2, column=0, columnspan=3, pady=10)

# 起動
root.mainloop()