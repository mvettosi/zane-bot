# import asyncio
# import datetime
# import json
import os
from os import listdir
from os.path import isfile, join

import sys, traceback
# from pathlib import Path

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
    print(f'Bot successfully loaded'
          f'Using discord.py version: {discord.__version__}\n')
    print('-' * 10)


bot.run(BOT_TOKEN, bot=True, reconnect=True)

# class Bot(commands.Bot):
#     def __init__(self, **kwargs):
#         super().__init__(
#             command_prefix=BOT_PREFIX,
#             description=kwargs.pop('description')
#         )
#
#         self.loaded_extensions = set()
#
#         self.app_info = None
#
#         self.loop.create_task(self.track_start())
#         self.loop.create_task(self.load_all_extensions())
#
#     async def load_all_extensions(self):
#         """
#         Attempts to load all bot extensions
#         """
#         # Load all .py files in /cogs/ as cog extensions
#         await self.wait_until_ready()
#         # ensure that on_ready has completed and finished printing
#         await asyncio.sleep(1)
#         cogs = [x.stem for x in Path(f"{DIRNAME}/cogs").glob('*.py')]
#         for extension in cogs:
#             try:
#                 extension_name = f'cogs.{extension}'
#                 self.loaded_extensions.add(extension_name)
#                 self.load_extension(extension_name)
#                 print(f'Cog {extension} loaded')
#             except Exception as e:
#                 error = f'{extension}\n {type(e).__name__} : {e}'
#                 print(f'failed to load extension {error}')
#             print('-' * 10)
#
#     async def on_ready(self):
#         """
#         This event is called every time the bot connects or resumes connection.
#         """
#         print('-' * 10)
#         self.app_info = await self.application_info()
#         print(f'Logged in as: {self.user.name}\n'
#               f'Using discord.py version: {discord.__version__}\n'
#               f'Owner: {self.app_info.owner}\n'
#               f'Template Maker: SourSpoon / Spoon#7805')
#         print('-' * 10)
#
#     async def on_message(self, message):
#         """
#         This event triggers on every message received by the bot. Including one's that it sent itself.
#         If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
#         always ignore bots.
#         """
#         if message.author.bot:
#             return  # ignore all bots
#         await self.process_commands(message)
#
#
# if __name__ == '__main__':
#     bot = Bot(description=BOT_DESC)
#     bot.run(BOT_TOKEN)
