import discord
from discord.ext import commands

from modules import config


class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return self.clean_prefix + f' | {self.clean_prefix}'.join([command.name] + command.aliases)

    async def send_bot_help(self, mapping):
        title = self.context.bot.description if self.context.bot.description else 'Zane Bot Commands'
        desc = f"Type `{self.clean_prefix}{self.invoked_with} command` for more info on a command.\n" \
               f"You can also type `{self.clean_prefix}{self.invoked_with} category` for more info on a category."
        embed = discord.Embed(title=title, description=desc, colour=config.BOT_COLOR)

        for cog, cog_commands in mapping.items():
            name = 'Others' if cog is None else cog.qualified_name
            filtered = await self.filter_commands(cog_commands, sort=True)
            if filtered:
                value = ', '.join([f'`.{cmd}`' for cmd in filtered])
                if cog and cog.description:
                    value = f'{cog.description}\n{value}'
                embed.add_field(name=name, value=value, inline=False)

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        title = f'{cog.qualified_name} Commands'
        embed = discord.Embed(title=title, description=cog.description, colour=config.BOT_COLOR)

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            field_name = self.get_command_signature(command)
            field_desc = command.short_doc or 'No short description yet'
            embed.add_field(name=field_name, value=field_desc, inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        title = f'Command: {command.name}'
        desc = command.help
        if command.aliases:
            desc = f'{desc}\n\nAlso usable with: `{self.clean_prefix}' \
                   + f'`, `{self.clean_prefix}'.join(command.aliases) + '`'
        embed = discord.Embed(title=title, description=desc, colour=config.BOT_COLOR)
        await self.get_destination().send(embed=embed)
