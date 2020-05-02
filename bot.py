#!/usr/bin/env python3.7

import asyncio
import datetime
import json
import os
from pathlib import Path

import discord
from discord.ext import commands


dirname = os.path.dirname(__file__)


def config_load():
    with open(f"{dirname}/data/config.json", 'r', encoding='utf-8') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)


async def get_prefix_(bot, message):
    """
    A coroutine that returns a prefix.
    I have made this a coroutine just to show that it can be done. If you needed async logic in here it can be done.
    A good example of async logic would be retrieving a prefix from a database.
    """
    prefix = ['!']
    return commands.when_mentioned_or(*prefix)(bot, message)


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=get_prefix_,
            description=kwargs.pop('description')
        )

        self.config = kwargs.pop('config')

        self.loaded_extensions = set()

        self.start_time = None
        self.app_info = None

        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_all_extensions(self):
        """
        Attempts to load all bot extensions
        """
        # Load all .py files in /cogs/ as cog extensions
        await self.wait_until_ready()
        # ensure that on_ready has completed and finished printing
        await asyncio.sleep(1)
        cogs = [x.stem for x in Path(f"{dirname}/cogs").glob('*.py')]
        for extension in cogs:
            try:
                extension_name = f'cogs.{extension}'
                self.loaded_extensions.add(extension_name)
                self.load_extension(extension_name)
                print(f'Cog {extension} loaded')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'failed to load extension {error}')
            print('-' * 10)

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Using discord.py version: {discord.__version__}\n'
              f'Owner: {self.app_info.owner}\n'
              f'Template Maker: SourSpoon / Spoon#7805')
        print('-' * 10)

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        if message.author.bot:
            return  # ignore all bots
        await self.process_commands(message)


if __name__ == '__main__':
    config = config_load()
    bot = Bot(config=config, description=config['description'])
    bot.run(config['token'])
