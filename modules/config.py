import os
import json

BOT_PREFIX = os.getenv('BOT_PREFIX')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_DESC = os.getenv('BOT_DESCRIPTION')
BOT_COLOR = int('3a6778', 16)
DB_CONNECTION_URL = os.getenv('DB_CONNECTION_URL')
DB_NAME = os.getenv('DB_NAME')

with open('data/emotes.json') as emotes_file:
    EMOTES = json.load(emotes_file)

with open('data/colors.json') as colors_file:
    COLORS = json.load(colors_file)
