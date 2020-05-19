import logging
import re
import traceback
# noinspection PyPackageRequirements
from discord import Forbidden
from discord.ext import commands
from discord.ext.commands import CommandInvokeError

from modules import database, messages
from pprint import pformat

BOT_INFORMATION = ('I am a Yu-Gi-Oh! Duel Links card bot made by [CwC] Drackmord#9541.'
                   '\n\nTo search cards and skills, simply add their name or part of their name in curly brackets, '
                   'like for example `{blue-eyes white dragon}` or `{no mortal can resist}`.'
                   '\n\nI currently don\'t support incomplete words or typos, but you can use only part of the words, '
                   'for example `{lara}`.'
                   '\n\nAlso, you can force a search to match a skill only like this `{!destiny draw}`, and a card only'
                   ' using `{?destiny draw}`.'
                   '\n\nAs I\'m very new, please don\'t hesitate to mention or pm my creator for bugs or suggestions!')
AUTHOR_ID = 351861715283214338


def setup(bot):
    bot.add_cog(SearchCog(bot))


def discord_item(q):
    return q.startswith(('!', ':', 'a:', '@', '#', '://'))


def get_queries(message_content):
    # Find {...} queries
    curly_queries = re.findall(r'(?<={)([^{}]*?)(?=})', message_content)
    # Find <...> queries
    angular_queries = re.findall(r'(?<=<)([^<>]*?)(?=>)', message_content)
    # Remove fake queries from discord special items (emotes/mentions/channels)
    angular_queries = [q for q in angular_queries if not discord_item(q)]
    # Remove duplicates and return
    return list(dict.fromkeys(curly_queries + angular_queries))


async def delete_message(context):
    try:
        await context.message.delete()
    except Forbidden:
        logging.error(f'Error deleting message "{context.message}"')
        await context.send('I need permission to delete this message, it\'s not safe to keep it around!')


class SearchCog(commands.Cog, name='Search'):
    """Commands related to searching cards and skills"""

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

        if self.bot.user.mentioned_in(message):
            await message.channel.send(BOT_INFORMATION)

        queries = get_queries(message.content)
        if not queries:
            return

        if len(queries) > 3:
            await message.channel.send('Sorry, max 3 requests per message =/')
            return

        for query in queries:
            # Try first with a perfect match
            result_list = await database.search(query, 1, True)
            if not result_list:
                result_list = await database.search(query, 1)
            if not result_list:
                await message.channel.send(f'Sorry, I could not find any card or skill including `{query}`. I '
                                           f'currently don\'t support incomplete words or typos, but you can use only '
                                           f'part of the words, for example `{{lara}}`')
            else:
                await self.show_result(message, query, result_list[0])

    @commands.command(hidden=True)
    async def match(self, context, *, args=''):
        await context.send(f'(Work in progress) Searching for `{args}`')

    @commands.command(hidden=True)
    async def update_db(self, context):
        await delete_message(context)
        await context.send('Checking for database updates...')
        await database.check_updates()
        await context.send('Database updated!')

    @commands.command(hidden=True)
    async def rebuild_db(self, context):
        await delete_message(context)
        await context.send('Deleting all database...')
        await database.clean_md5s()
        await database.check_updates()
        await context.send('Database rebuilt!')

    async def show_result(self, message, query, result):
        logging.info('')
        server_name = message.channel.guild.name
        channel_name = message.channel.name
        author_name = message.author.name
        logging.info(f'{server_name}, #{channel_name}, {author_name}, query: {query}')
        try:
            result_embed = await messages.get_embed(result)
            await message.channel.send(embed=result_embed)
            result_name = result['name']
            logging.info(f'Showing result: {result_name}')
            logging.debug(f'Full body:\n{pformat(result)}')
        except Exception as e:
            user = self.bot.get_user(AUTHOR_ID)
            trace = traceback.format_exc()
            if len(trace) > 2000:
                trace = trace[0:2000]
            result_name = result['name']
            logging.error(f'Error processing "{result_name}" for query "{query}"')
            await user.send(f'Query = `{query}`\nCard pulled = {result_name}\n```{trace}```')
            await message.channel.send(f'Sorry, some internal error occurred. I\'m still in testing but don\'t worry, '
                                       f'I just pinged my author with the details so this will be fixed soon!')
