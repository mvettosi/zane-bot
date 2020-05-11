import logging
import re
from discord.ext import commands
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
        if not bool(re.match(r'.*{.*}.*', message.content)):
            return

        queries = re.findall(r'(?<={)([^{}]*?)(?=})', message.content)

        for query in queries:
            result = await database.search(query, 1)
            first_result = result[0]
            name = first_result['name']
            desc = first_result['description']
            is_skill = 'exclusive' in first_result
            await message.channel.send(
                f'Result for query `{query}`:\n```Name = {name}\nDescription = {desc}\nIs a skill = {is_skill}```')
