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
    async def feedback(self, ctx, *, feedback: str):
        """Sends feedback to the devs.
        
        Please do not spam this command! You will 
        be blacklisted if you do."""
        notif = DevNotif(feedback, 'Feedback', ctx.guild, ctx.channel, ctx.message.author)
        await notify_devs(ctx, notif)

def setup(bot):
    bot.add_cog(Core(bot))

