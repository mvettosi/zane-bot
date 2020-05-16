import os
from os import listdir
from os.path import isfile, join

import sys
import traceback

import discord
from discord.ext import commands

import logging
from modules import config


COGS_DIR = 'cogs'


logging.basicConfig(level=logging.INFO)
logging.getLogger("discord").setLevel(logging.WARNING)
bot = commands.Bot(command_prefix=config.BOT_PREFIX,
                   description=config.BOT_DESC)

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(COGS_DIR) if isfile(join(COGS_DIR, f))]:
        try:
            bot.load_extension(COGS_DIR + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logging.error(f'Failed to load extension {extension}.')
            traceback.print_exc()


@bot.event
async def on_ready():
    logging.info('-------------------------------------------------')
    logging.info(f'Bot successfully loaded')
    logging.info(f'Using discord.py version: {discord.__version__}')
    logging.info(f'Template by Matteo Vettosi (github.com/mvettosi)')
    logging.info('-------------------------------------------------')


bot.run(config.BOT_TOKEN, bot=True, reconnect=True)
