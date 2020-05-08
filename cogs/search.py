from discord.ext import commands
import asyncio
import logging
from modules import download


def setup(bot):
    bot.add_cog(SearchCog(bot))


class SearchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        skills_download = download.download(download.FileType.SKILLS)
        logging.info(f'Downloaded file: {skills_download}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.author.bot:
            return

        await message.channel.send(f'Received: `{message.content}`')
