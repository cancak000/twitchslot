import random
import time
import threading
from gui import root, canvas, username_label, result_label, slots, flash_background, blink_reels, explosion_effect
from slot_logic import check_combo, choose_weighted_result
from score_manager import add_score
import queue

spin_lock = threading.Lock()
username_queue = queue.Queue()

# GUI背景リセット

def reset_gui():
    root.after(0, lambda: canvas.place_forget())
    root.after(0, lambda: canvas.delete("all"))
    root.after(0, lambda: canvas.configure(bg="black"))
    root.after(0, lambda: root.configure(bg="black"))
    for label in [username_label, result_label] + slots:
        root.after(0, lambda l=label: l.configure(bg="black"))
    for i, label in enumerate(slots):
        root.after(0, lambda l=label, i=i: l.grid(row=1, column=i, padx=20, pady=(10, 0)))

# スロット回転処理

def spin_individual_reels(username="ゲスト", force_level=0, loaded_images=None, sounds=None, update_label_with_image=None):
    try:
        reset_gui()

        root.after(0, lambda: username_label.config(text=f"{username} さんが \n スロットを回しています"))
        result_label.config(text="")
        final = choose_weighted_result(force_level)
        reel_symbols = list(loaded_images.keys())

        for reel, symbol in enumerate(final):
            for i in range(10):
                temp_symbol = random.choice(reel_symbols)
                root.after(0, lambda r=reel, s=temp_symbol: update_label_with_image(slots[r], s))
                time.sleep(0.05 + i * 0.0015)
            root.after(0, lambda r=reel, s=symbol: update_label_with_image(slots[r], s))
            root.after(0, lambda: sounds["stop"].play())
            time.sleep(0.1)

        message, sound, score = check_combo(final)
        root.after(0, lambda: result_label.config(text=message))
        root.after(0, lambda: sound.play())

        if score >= 50:
            flash_background()
            blink_reels()
            explosion_effect()
        elif score >= 10:
            blink_reels()
            flash_background()
        elif score > 0:
            blink_reels(times=2, interval=100)

        add_score(username, score)

    finally:
        spin_lock.release()


def start_spin(force_level=0, loaded_images=None, sounds=None, update_label_with_image=None):
    
    acquired = spin_lock.acquire(timeout=2)
    if not acquired:
        print("⚠️ スロットがロック中で取得できませんでした")
        return

    try:
        username = username_queue.get_nowait()
    except queue.Empty:
        username = "ゲスト"

    threading.Thread(target=spin_individual_reels, args=(
        username, force_level, loaded_images, sounds, update_label_with_image)).start()

def start_spin_with_user(username, force_level=0, loaded_images=None, sounds=None, update_label_with_image=None):
    acquired = spin_lock.acquire(timeout=2)
    if not acquired:
        print(f"⚠️ スロットがロック中：{username}はスキップされました")
        return
    threading.Thread(target=spin_individual_reels, args=(username, force_level, loaded_images, sounds, update_label_with_image)).start()