import random
import time

# スロットの絵柄
symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

# スロットを回す関数
def spin_slot():
    result = [random.choice(symbols) for _ in range(3)]
    print("スロットを回します...")
    for i in range(3):
        time.sleep(0.5)
        print(result[i], end=" ", flush=True)
    print()

    if result[0] == result[1] == result[2]:
        print("🎉 大当たり！3つ揃った！")
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        print("✨ 小当たり！2つ揃った！")
    else:
        print("🙃 はずれ！")

# メイン処理
def main():
    while True:
        input("\nEnterキーでスロットを回す（終了するには Ctrl+C）")
        spin_slot()

if __name__ == "__main__":
    main()
