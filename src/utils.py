import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)


def setup_logger(name="slot_game", log_file="slot_game.log", level=logging.INFO, max_bytes=1024*1024, backup_count=3):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 二重追加防止
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, 'baseFilename', '') == log_file for h in logger.handlers):
        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger