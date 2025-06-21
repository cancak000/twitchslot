import random
from sound_manager import get_sounds

reel_symbols = [
    "GENIE", "PALACE", "MOON", "LAMP",
    "CARPET", "COIN", "SCORPION", "CAMEL"
]
sounds = get_sounds()


def check_combo(combo):
    if combo == ["GENIE"] * 3:
        return "🎊 ジーニー揃い！", sounds["big"], 100
    elif combo == ["COIN"] * 3:
        return "💰 コイン大当たり！", sounds["big"], 50
    elif combo == ["CAMEL"] * 3:
        return "🐪 ラクダ中当たり！", sounds["small"], 20
    elif combo == ["MOON"] * 3:
        return "🌙 月の神秘！", sounds["small"], 10
    elif combo[0] == combo[1] or combo[1] == combo[2] or combo[0] == combo[2]:
        return "✨ 小当たり！", sounds["small"], 5
    else:
        return "🙃 はずれ！", sounds["lose"], 0

def semi_match_combo():
    base = random.choice(reel_symbols)
    diff = random.choice([s for s in reel_symbols if s != base])
    combo = [base, base, diff]
    random.shuffle(combo)
    return combo
    
def choose_weighted_result(force_level):
    roll = random.random()

    if force_level == 3:  # 超高確率
        if roll < 0.25:
            return ["GENIE"] * 3
        elif roll < 0.5:
            return ["COIN"] * 3
        elif roll < 0.75:
            return ["CAMEL"] * 3
        elif roll < 0.90:
            return semi_match_combo()
    elif force_level == 2:  # 高確率
        if roll < 0.15:
            return ["GENIE"] * 3
        elif roll < 0.35:
            return ["COIN"] * 3
        elif roll < 0.55:
            return ["CAMEL"] * 3
        elif roll < 0.75:
            return semi_match_combo()
    elif force_level == 1:  # 中確率
        if roll < 0.1:
            return ["GENIE"] * 3
        elif roll < 0.25:
            return ["COIN"] * 3
        elif roll < 0.4:
            return ["CAMEL"] * 3
        elif roll < 0.6:
            return semi_match_combo()

    # 通常 or ハズレ
    return [random.choice(reel_symbols) for _ in range(3)]
