import os
import json

BOT_PREFIX = "."
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_DESC = "A bot to retrieve various YuGiOh information"
BOT_COLOR = int('3a6778', 16)
DB_CONNECTION_URL = os.getenv('DB_CONNECTION_URL')
DB_NAME = os.getenv('DB_NAME')
CARD_ANNOTATOR_URL = os.getenv('CARD_ANNOTATOR_URL')

with open('data/emotes.json') as emotes_file:
    EMOTES = json.load(emotes_file)

with open('data/colors.json') as colors_file:
    COLORS = json.load(colors_file)
