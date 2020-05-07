from discord.ext import commands
import asyncio
import logging


def setup(bot):
    bot.add_cog(CardsCog(bot))


class CardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user: return
        if message.author.bot: return

        await message.channel.send(f'Received: `{message.content}`')
