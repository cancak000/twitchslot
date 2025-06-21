import pygame
from utils import resource_path

pygame.mixer.init()
stop_sound = pygame.mixer.Sound(resource_path("sound/stop.mp3"))
big_sound = pygame.mixer.Sound(resource_path("sound/big_win.mp3"))
small_sound = pygame.mixer.Sound(resource_path("sound/small_win.mp3"))
lose_sound = pygame.mixer.Sound(resource_path("sound/lose.mp3"))

# サウンドをまとめて返す関数
def get_sounds():
    return {
        "stop": stop_sound,
        "big": big_sound,
        "small": small_sound,
        "lose": lose_sound
    }