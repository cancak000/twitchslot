import tkinter as tk
from tkinter import Toplevel
import math
import traceback
import sqlite3
from PIL import Image, ImageTk
from utils import resource_path

import logging
from utils import setup_logger

logger = setup_logger("gui", "logs/gui.log", level=logging.INFO)


# SQLite接続（スコア表示用）
conn = sqlite3.connect("slot_scores.db", check_same_thread=False)
cursor = conn.cursor()

slot_images = [None, None, None]

# 🎮 メインウィンドウ（常時表示：操作パネル用）
root = tk.Tk()
root.title("iV Slot Control Panel")
root.geometry("300x100")
root.configure(bg="gray20")

# 🎰 スロット表示用ウィンドウ（非表示からスタート）
slot_window = Toplevel(root)
slot_window.title("iV Slot")
slot_window.geometry("520x300")
slot_window.configure(bg="black")
slot_window.withdraw()  # ← 初期は非表示
slot_window.iconify() # アイコン化しておく

slots = []

# GUIエラー用ログ設定
def tk_exception_logger(exc, val, tb):
    with open("slot_tkinter_error_log.txt", "w", encoding="utf-8") as f:
        f.write("Tkinter 例外:\n")
        f.write("".join(traceback.format_exception(exc, val, tb)))

root.report_callback_exception = tk_exception_logger

canvas = tk.Canvas(slot_window, width=520, height=300, bg="black", highlightthickness=0)
canvas.place_forget()

status_label = tk.Label(slot_window, text="初期化中...", font=("Helvetica", 14), bg="black", fg="white")
status_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))

result_label = tk.Label(slot_window, text="", font=("Helvetica", 24, "bold"), bg="black", fg="white")
result_label.grid(row=2, column=0, columnspan=3, pady=(10, 20))

username_label = tk.Label(slot_window, text="", font=("Helvetica", 14, "bold"), bg="black", fg="cyan")
username_label.grid(row=0, column=0, columnspan=3, pady=(10, 0))



image_paths = {
    "GENIE": "image/jinny.png",
    "PALACE": "image/castle.png",
    "MOON": "image/moon.png",
    "LAMP": "image/ramp.png",
    "CARPET": "image/carpet.png",
    "COIN": "image/coin.png",
    "SCORPION": "image/scorpion.png",
    "CAMEL": "image/camel.png"
}

loaded_images = {
    key: ImageTk.PhotoImage(Image.open(resource_path(path)).resize((128, 128)))
    for key, path in image_paths.items()
}

def update_label_with_image(label, image_key):
    label.config(image=loaded_images[image_key])
    label.image = loaded_images[image_key]

def reset_backgrounds():
    slot_window.configure(bg="black")
    for label in [username_label, result_label] + slots:
        label.configure(bg="black")

def flash_background(times=6, interval=150):
    def toggle(i):
        bg_color = "white" if i % 2 == 0 else "black"
        slot_window.configure(bg=bg_color)
        for label in [username_label, result_label] + slots:
            label.configure(bg=bg_color)
        if i < times:
            slot_window.after(interval, toggle, i + 1)
        else:
            slot_window.after(interval, reset_backgrounds)
    toggle(0)


def blink_reels(times=6, interval=150):
    def toggle(i):
        for label in slots:
            label.grid_remove() if i % 2 == 0 else label.grid()
        if i < times:
            slot_window.after(interval, toggle, i + 1)
    toggle(0)

def explosion_effect(duration=800):
    def draw_explosion():
        canvas.lift(slot_window)  # 明示的に root の中で最前面へ
        canvas.place(x=0, y=0)
        canvas.delete("all")
        for i in range(20):
            angle = i * (360 / 20)
            x = 260 + 200 * math.cos(math.radians(angle))
            y = 150 + 200 * math.sin(math.radians(angle))
            canvas.create_line(260, 150, x, y, fill="yellow", width=2)
        canvas.create_oval(240, 130, 280, 170, fill="gold", outline="white")
        slot_window.after(duration, lambda: canvas.place_forget())
    slot_window.after(0, draw_explosion)

def show_ranking_window():
    ranking_win = tk.Toplevel(slot_window)
    ranking_win.title("スコアランキング")
    ranking_win.configure(bg="black")
    ranking_win.geometry("300x300")

    tk.Label(ranking_win, text="🏆 スコアランキング", font=("Helvetica", 14, "bold"),
             bg="black", fg="gold").pack(pady=10)

    cursor.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()

    for i, (user, score) in enumerate(rows, start=1):
        entry = f"{i}. {user}：{score} 点"
        tk.Label(ranking_win, text=entry, font=("Helvetica", 12),
                 bg="black", fg="white").pack(anchor="w", padx=20)

def bring_to_front():
    slot_window.deiconify()
    slot_window.lift()
    slot_window.attributes('-topmost', True)
    slot_window.after(1000, lambda: slot_window.attributes('-topmost', False))

def hide_window():
    slot_window.withdraw()      # ウィンドウを非表示にする（完全に隠れる）
    slot_window.iconify()