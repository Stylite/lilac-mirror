#!/usr/bin/env python
import discord
from discord.ext import commands

class Core:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check(self, ctx):
        """Checks if the bot is up."""
        await ctx.send('Bot is up and running!')

def setup(bot):
    bot.add_cog(Core(bot))

