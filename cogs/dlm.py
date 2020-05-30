import asyncio
import re
from itertools import groupby

from discord.ext import commands

from modules import download, messages
from modules.download import HttpMethod
from modules.messages import PREV_BUTTON, NEXT_BUTTON, LadderType
from modules.pagination import Paginator

REV_MANIFEST_URL = 'https://www.duellinksmeta.com/rev-manifest.json'
SEASON_BASE_URL = 'https://www.duellinksmeta.com/data-hashed/'
LADDER_REGEX = re.compile(r'tpc-ladders/season-(.+).json')
PLAYER_GROUP_MAX = 5
LADDER_PAGE_SIZE = 16
LADDER_ELEMENT_KEY = 'players'


def setup(bot):
    bot.add_cog(DlmCog(bot))


async def get_ladder():
    manifest = await download.json(REV_MANIFEST_URL, HttpMethod.GET)
    all_seasons = [
        int(LADDER_REGEX.sub(r'\1', season)) for season in manifest.keys() if 'tpc-ladders/season-' in season
    ]
    current_season = max(all_seasons)
    current_season_key = f'tpc-ladders/season-{current_season}.json'
    current_season_value = manifest[current_season_key]
    ladder_url = SEASON_BASE_URL + current_season_value
    return await download.json(ladder_url, HttpMethod.GET)


async def group_players(players, sort_by='total_points'):
    players_grouped = []
    rank = 0
    for k, v in groupby(players, key=lambda x: x[sort_by]):
        players_in_group = list(v)
        rank_min = rank + 1
        rank_max = rank + 1
        if len(players_in_group) > 1:
            rank_max = rank_min + len(players_in_group) - 1
        while len(players_in_group) > 0:
            players_grouped.append({
                LADDER_ELEMENT_KEY: players_in_group[:PLAYER_GROUP_MAX],
                'rank_min': rank_min,
                'rank_max': rank_max
            })
            players_in_group = players_in_group[PLAYER_GROUP_MAX:]
        rank = rank_max
    return players_grouped


async def process_players(bot, context, paginator, ladder_type):
    embed = messages.get_ladder_page(paginator.get_page(), ladder_type, paginator.current_page,
                                     paginator.pages_number())
    message = await context.send(embed=embed)
    await message.add_reaction(PREV_BUTTON)
    await message.add_reaction(NEXT_BUTTON)

    def check(reaction_to_check, user_to_check):
        return user_to_check == context.message.author and str(reaction_to_check.emoji) in [PREV_BUTTON, NEXT_BUTTON] \
               and reaction_to_check.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            await message.remove_reaction(reaction, user)
            if reaction.emoji == PREV_BUTTON:
                embed = messages.get_ladder_page(paginator.prev_page(), ladder_type, paginator.current_page,
                                                 paginator.pages_number())
                await message.edit(embed=embed)
            elif reaction.emoji == NEXT_BUTTON:
                embed = messages.get_ladder_page(paginator.next_page(), ladder_type, paginator.current_page,
                                                 paginator.pages_number())
                await message.edit(embed=embed)
        except asyncio.exceptions.TimeoutError:
            await message.clear_reactions()
            break


class DlmCog(commands.Cog, name='DLM'):
    """Commands pulling various types of information from the Duel Links Meta website"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ladder(self, context):
        """Command to display info on each player in the Duel Links Meta ladder, ordered by rank from high to low"""
        ladder = await get_ladder()
        players = ladder['players']
        players.reverse()
        groups = await group_players(players)
        players_paginated = Paginator(groups, LADDER_PAGE_SIZE, LADDER_ELEMENT_KEY)
        await process_players(self.bot, context, players_paginated, LadderType.TOP_PLAYER)

    @commands.command(aliases=['anytimeladder', 'anytime-ladder'])
    async def anytimes(self, context):
        """Command to display info on each player in the Duel Links Meta anytime tournament ladder, \
        ordered by rank from high to low"""
        ladder = await get_ladder()
        players = ladder['anytime_wins'][1]['players']
        groups = await group_players(players, 'wins')
        players_paginated = Paginator(groups, LADDER_PAGE_SIZE, LADDER_ELEMENT_KEY)
        await process_players(self.bot, context, players_paginated, LadderType.ANYTIME)
