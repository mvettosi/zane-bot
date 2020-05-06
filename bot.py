import os
from os import listdir
from os.path import isfile, join

import sys, traceback

import discord
from discord.ext import commands

import logging


DIRNAME = os.path.dirname(__file__)
BOT_PREFIX = os.getenv('BOT_PREFIX')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_DESC = os.getenv('BOT_DESCRIPTION')
COGS_DIR = 'cogs'


logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix=BOT_PREFIX, description=BOT_DESC)

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(COGS_DIR) if isfile(join(COGS_DIR, f))]:
        try:
            bot.load_extension(COGS_DIR + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logging.error(f'Failed to load extension {extension}.')
            traceback.print_exc()


@bot.event
async def on_ready():
    logging.info('-' * 10)
    logging.info(f'Bot successfully loaded')
    logging.info(f'Using discord.py version: {discord.__version__}')
    logging.info(f'Template by Matteo Vettosi (github.com/mvettosi)')
    logging.info('-' * 10)


bot.run(BOT_TOKEN, bot=True, reconnect=True)
