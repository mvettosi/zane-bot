import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    COLOUR = int('3a6778', 16)

    async def send_bot_help(self, mapping):
        title = self.context.bot.description if self.context.bot.description else 'Zane Bot Commands'
        desc = f"Type `{self.clean_prefix}{self.invoked_with} command` for more info on a command.\n" \
               f"You can also type `{self.clean_prefix}{self.invoked_with} category` for more info on a category."
        embed = discord.Embed(title=title, description=desc, colour=self.COLOUR)

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
        embed = discord.Embed(title=title, description=cog.description, colour=self.COLOUR)

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            field_name = self.get_command_signature(command)
            field_desc = command.short_doc or 'No short description yet'
            embed.add_field(name=field_name, value=field_desc, inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        title = f'Command: {command.name}'
        embed = discord.Embed(title=title, description=command.help, colour=self.COLOUR)
        await self.get_destination().send(embed=embed)
