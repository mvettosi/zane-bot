import os
from os import listdir
from os.path import isfile, join

import sys, traceback

import discord
from discord.ext import commands


DIRNAME = os.path.dirname(__file__)
BOT_PREFIX = '!'
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_DESC = os.getenv('BOT_DESCRIPTION')
COGS_DIR = 'cogs'


bot = commands.Bot(command_prefix=BOT_PREFIX, description=BOT_DESC)

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(COGS_DIR) if isfile(join(COGS_DIR, f))]:
        try:
            bot.load_extension(COGS_DIR + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()


@bot.event
async def on_ready():
    print('-' * 10)
    print(f'Bot successfully loaded\n'
          f'Using discord.py version: {discord.__version__}')
    print('-' * 10)


bot.run(BOT_TOKEN, bot=True, reconnect=True)
