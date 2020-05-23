import re

from discord.ext import commands

from modules import download, messages
from modules.download import HttpMethod

REV_MANIFEST_URL = 'https://www.duellinksmeta.com/rev-manifest.json'
SEASON_BASE_URL = 'https://www.duellinksmeta.com/data-hashed/'
LADDER_REGEX = re.compile(r'tpc-ladders/season-(.+).json')


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


async def process_ladder(context, sort_by='total_points'):
    pass


class DlmCog(commands.Cog, name='DLM'):
    """Commands pulling various types of information from the Duel Links Meta website"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tpc-ladder', aliases=['tpcladder', 'tpcnext', 'tpc-next'])
    async def tpcladder(self, context):
        """Command to display the names of the next season's Top Player Council current candidates"""
        ladder = await get_ladder()
        result = messages.get_tpc(ladder['players'])
        await context.send(embed=result)
