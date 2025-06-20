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
        root.after(0, lambda: result_label.config(text=""))

        final = choose_weighted_result(force_level)
        reel_symbols = list(loaded_images.keys())

        def spin_reel(reel_index, stop_symbol, delay_start=0):
            def spin_step(i):
                if i < 10:
                    temp_symbol = random.choice(reel_symbols)
                    update_label_with_image(slots[reel_index], temp_symbol, reel_index=reel_index)
                    root.after(50, lambda: spin_step(i + 1))  # 50msごとに次
                else:
                    update_label_with_image(slots[reel_index], stop_symbol)
                    sounds["stop"].play()

            root.after(delay_start, lambda: spin_step(0))

        for idx, symbol in enumerate(final):
            spin_reel(idx, symbol, delay_start=idx * 600)  # リールごとに600msずらし

        def show_result():
            message, sound, score = check_combo(final)
            result_label.config(text=message)
            sound.play()

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

        root.after(2000, show_result)

    finally:
        root.after(2500, spin_lock.release)

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