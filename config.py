import os

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "client_secrets.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "musicas")
FONT_DIR = os.path.join(BASE_DIR, "fonts")
OUTPUT_DIR = os.path.join(BASE_DIR, "videos")
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
