import time
import random
import threading
from gui import canvas, username_label, result_label, update_label_with_image, flash_background, blink_reels, explosion_effect, bring_to_front, hide_window
from slot_logic import check_combo, choose_weighted_result
from score_manager import add_score
from utils import resource_path

# GUI背景リセット

def reset_gui(root, slots):
    root.after(0, lambda: canvas.place_forget())
    root.after(0, lambda: canvas.delete("all"))
    root.after(0, lambda: canvas.configure(bg="black"))
    root.after(0, lambda: root.configure(bg="black"))
    for label in [username_label, result_label] + slots:
        root.after(0, lambda l=label: l.configure(bg="black"))
    for i, label in enumerate(slots):
        root.after(0, lambda l=label, i=i: l.grid(row=1, column=i, padx=20, pady=(10, 0)))

# スロット回転処理

def spin_individual_reels(root, slots, username="ゲスト", force_level=0, reel_symbols=None, sounds=None, sound_enabled=True, username_queue=None, spin_lock=None):
    try:
        bring_to_front() 
        reset_gui(root, slots)
        root.after(0, lambda: username_label.config(text=f"{username} さんが \n スロットを回しています"))
        root.after(0, lambda: result_label.config(text=""))

        final = choose_weighted_result(force_level)

        for reel, symbol in enumerate(final):
            for i in range(10):
                temp_symbol = random.choice(reel_symbols)
                root.after(0, lambda r=reel, s=temp_symbol: update_label_with_image(slots[r], s))
                time.sleep(0.05 + i * 0.0015)
            root.after(0, lambda r=reel, s=symbol: update_label_with_image(slots[r], s))
            if sound_enabled: 
                root.after(0, lambda: sounds["stop"].play())
            time.sleep(0.1)
        
        def show_result():
            message, sound_obj, score = check_combo(final)
            result_label.config(text=message)
            if sound_enabled:
                sound_obj.play()

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
            root.after(3000, lambda: reset_gui(root, slots))
    finally:
        root.after(1000, show_result)
        root.after(6000, lambda: reset_gui(root, slots))
        root.after(5000, lambda: hide_window() if username_queue.empty() else None)

def start_spin_with_user(root, slots, username, force_level=0, reel_symbols=None, sounds=None, sound_enabled=True, username_queue=None, spin_lock=None):
    def thread_func():
        if not spin_lock.acquire(timeout=2):
            print(f"⚠️ スロットがロック中：{username}はスキップされました")
            return
        try:
            spin_individual_reels(root, slots, username, force_level, reel_symbols, sounds, sound_enabled, username_queue, spin_lock)
        finally:
            if spin_lock.locked():
                spin_lock.release()
    t = threading.Thread(target=thread_func)
    t.start()
