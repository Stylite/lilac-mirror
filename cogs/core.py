#!/usr/bin/env python
import time

import discord
from discord.ext import commands

from cogs.util.devnotif import DevNotif, notify_devs


class Core:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check(self, ctx):
        """Checks if the bot is up."""
        await ctx.send('Bot is up and running!')

    @commands.command()
    async def feedback(self, ctx):
        """Returns a link to the Google Forms feedback form.

        Do not spam the form!"""
        await ctx.send('__**Feedback & Bug Reporting Form:**__\nhttps://goo.gl/forms/jMmS8JPg1CX4E0Li2' +
                       '\n\n**__Valid__** feedback would be greatly appreciated!')


def setup(bot):
    bot.add_cog(Core(bot))
