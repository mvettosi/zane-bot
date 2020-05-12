import logging
import re
# noinspection PyPackageRequirements
from discord.ext import commands
from modules import database, messages
from pprint import pformat


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
            result_list = await database.search(query, 1)
            if not result_list:
                await message.channel.send(f'Sorry, I could not find any card or skill including "{query}". I '
                                           f'currently don\'t support incomplete words or typos, but you can use only '
                                           f'part of the words, for example `{{lara}}`')
            else:
                result = result_list[0]
                result_embed = messages.get_embed(result)
                await message.channel.send(embed=result_embed)
                logging.debug(f'\n\nSearch result:\n{pformat(result)}')
