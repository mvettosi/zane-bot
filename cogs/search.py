from discord.ext import commands
import asyncio
import logging
from modules import database


def setup(bot):
    bot.add_cog(SearchCog(bot))


class SearchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await database.check_updates()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.author.bot:
            return

        await message.channel.send(f'Received: `{message.content}`')
