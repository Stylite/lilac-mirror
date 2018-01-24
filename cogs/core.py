#!/usr/bin/env python
from discord.ext import commands
from cogs.util.checks import is_cleared
import discord

class Core:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check(self):
        """Checks if the bot is up."""
        await self.bot.say('Bot is up and running!')

    @commands.command()
    @is_cleared()
    async def reload(self, *, cog):
        """Reloads a cog of the bot. Developer only."""
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await self.bot.say(':warning: Failed to reload cog `{}`'.format(cog))
            print('[LOAD] Failed to reload cog `{}`, because: '.format(cog))
            print(e)
        else:
            await self.bot.say(':white_check_mark: Reloaded cog `{}`'.format(cog))
            print('[LOAD] Reloaded cog `{}`'.format(cog))

def setup(bot):
    bot.add_cog(Core(bot))

