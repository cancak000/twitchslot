import tkinter as tk
from tkinter import Toplevel
import math
import traceback
import sqlite3
from PIL import Image, ImageTk
from utils import resource_path

# SQLite接続（スコア表示用）
conn = sqlite3.connect("slot_scores.db", check_same_thread=False)
cursor = conn.cursor()

slot_images = [None, None, None]

# Tkinterルート作成
root = tk.Tk()
root.title("iV Slot")
root.geometry("520x350")
root.configure(bg="black")

slots = []
for i in range(3):
    label = tk.Label(root, bg="black")
    label.grid(row=1, column=i, padx=20, pady=(10, 0))
    slots.append(label)

# 例外ログ出力
def tk_exception_logger(exc, val, tb):
    with open("slot_tkinter_error_log.txt", "w", encoding="utf-8") as f:
        f.write("Tkinter 例外:\n")
        f.write("".join(traceback.format_exception(exc, val, tb)))

root.report_callback_exception = tk_exception_logger


# ステータス表示
status_label = tk.Label(root, text="初期化中...", font=("Helvetica", 14), bg="black", fg="white")
status_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))

# ラベル各種
username_label = tk.Label(root, text="", font=("Helvetica", 14, "bold"), bg="black", fg="cyan")
username_label.grid(row=0, column=0, columnspan=3, pady=(10, 0))

result_label = tk.Label(root, text="", font=("Helvetica", 24, "bold"), bg="black", fg="white")
result_label.grid(row=2, column=0, columnspan=3, pady=(10, 20))

# スロット画像を表示するラベル（画像は後から設定）
slots = []
for i in range(3):
    label = tk.Label(root, bg="black")
    label.grid(row=1, column=i, padx=20, pady=(10, 0))
    slots.append(label)

# 背景用Canvas（爆発用）
canvas = tk.Canvas(root, width=520, height=300, bg="black", highlightthickness=0)
canvas.place_forget()

# スロット画像のロード
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

def load_images():
    return {
        key: ImageTk.PhotoImage(Image.open(resource_path(path)).resize((128, 128)))
        for key, path in image_paths.items()
    }

def update_label_with_image(label, image_key, reel_index=None):
    path = resource_path(image_paths[image_key])
    pil_img = Image.open(path).resize((128, 128))
    img = ImageTk.PhotoImage(pil_img)

    label.config(image=img)
    label.image = img
    if reel_index is not None:
        slot_images[reel_index] = img

def reset_backgrounds():
    root.configure(bg="black")
    for label in [username_label, result_label] + slots:
        label.configure(bg="black")

def flash_background(times=6, interval=150):
    def toggle(i):
        bg_color = "white" if i % 2 == 0 else "black"
        root.configure(bg=bg_color)
        for label in [username_label, result_label] + slots:
            label.configure(bg=bg_color)
        if i < times:
            root.after(interval, toggle, i + 1)
        else:
            root.after(interval, reset_backgrounds)
    toggle(0)

def blink_reels(times=6, interval=150):
    def toggle(i):
        for label in slots:
            label.grid_remove() if i % 2 == 0 else label.grid()
        if i < times:
            root.after(interval, toggle, i + 1)
    toggle(0)

def explosion_effect(duration=800):
    def draw_explosion():
        canvas.lift(root)
        canvas.place(x=0, y=0)
        canvas.delete("all")
        for i in range(20):
            angle = i * (360 / 20)
            x = 260 + 200 * math.cos(math.radians(angle))
            y = 150 + 200 * math.sin(math.radians(angle))
            canvas.create_line(260, 150, x, y, fill="yellow", width=2)
        canvas.create_oval(240, 130, 280, 170, fill="gold", outline="white")
        root.after(duration, lambda: canvas.place_forget())
    root.after(0, draw_explosion)

def show_ranking_window():
    ranking_win = Toplevel(root)
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

def reset_backgrounds():
    root.configure(bg="black")
    for label in [username_label, result_label] + slots:
        label.configure(bg="black")

