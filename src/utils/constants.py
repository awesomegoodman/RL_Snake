import os
import sys
from typing import Literal
from .utils import find_root_dir


APP_NAME = 'Snake Game'
ICON_FILE = 'icon.ico'
TXT_FILE = f"{APP_NAME}.txt"
GAME_WIDTH = 700
GAME_HEIGHT = 600
SPEED = 100 # Reduce this value to increase the game speed.
SPACE_SIZE = 50
BODY_PARTS = 3
SNAKE_COLOR = "#800080"
SNAKE_HEAD_COLOR = "#8367C7"
FOOD_COLOR = "#FFFFFF"
BACKGROUND_COLOR = "#000000"
BACKGROUND_MUSIC_FILES = [
    '' # TODO: Include background music to game
]

RL_AGENT: Literal['RL_Agent'] = 'RL_Agent'
HUMAN_AGENT: Literal['Human_Agent'] = 'Human_Agent'

episodes = 1000


root_dir = find_root_dir(os.path.dirname(__file__))

# Check if running in a bundled exe or as a script
if getattr(sys, 'frozen', False):
    # Running in a bundle (specific to Pyinstaller)
    base_path = sys._MEIPASS # type: ignore
else:
    # Running as a script
    base_path = root_dir
    
icon_file_path = os.path.join(base_path, 'assets', 'icons', ICON_FILE)
soundtrack_path = os.path.join(base_path, 'assets', 'soundtrack', BACKGROUND_MUSIC_FILES[0])
text_file_dir = os.path.join(base_path, "saved")
weights_dir = os.path.join(base_path, "weights")
os.makedirs(text_file_dir, exist_ok=True)
os.makedirs(weights_dir, exist_ok=True)
text_file_path = os.path.join(text_file_dir, TXT_FILE)
q_table_file_path = os.path.join(weights_dir, "q_table.pkl")
    