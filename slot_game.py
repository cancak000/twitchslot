import random
import time
import sys

symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

def spin_animated():
    print("🎰 スロットを回しています...")
    final = [random.choice(symbols) for _ in range(3)]
    for i in range(10):  # アニメーション回数
        current = [random.choice(symbols) for _ in range(3)]
        sys.stdout.write("\r" + " ".join(current))
        sys.stdout.flush()
        time.sleep(0.1 + i*0.02)
    sys.stdout.write("\r" + " ".join(final) + "\n")

    # 判定
    if final[0] == final[1] == final[2]:
        print("🎉 大当たり！")
    elif final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        print("✨ 小当たり！")
    else:
        print("🙃 はずれ！")

# 実行
if __name__ == "__main__":
    spin_animated()
