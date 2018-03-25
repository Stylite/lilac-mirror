#!/usr/bin/env python
import time
import os
import psutil

import discord
from discord.ext import commands

from cogs.util.devnotif import DevNotif, notify_devs


class Core:
    """Core commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check(self, ctx):
        """Checks if the bot is up."""
        await self.bot.send(ctx, 'Bot is up and running!')

    @commands.command()
    async def feedback(self, ctx):
        """Returns a link to the Google Forms feedback form.

        Do not spam the form!"""
        await self.bot.send(ctx, '__**Feedback & Bug Reporting Form:**__\nhttps://goo.gl/forms/jMmS8JPg1CX4E0Li2' +
                       '\n\n**__Valid__** feedback would be greatly appreciated!\n\n'+\
                       'You can also make suggestions or bug reports by visiting our support server, '+\
                       'which you can get an invite to by doing `support`.')

    @commands.command()
    async def support(self, ctx):
        """Gives you an invite to the support server."""
        to_send = discord.Embed(title="Support Server", description="https://discord.gg/EcW7kfa",\
                                colour=0xbd8cbf)
        await self.bot.send(ctx, embed=to_send)
    
    @commands.command()
    async def info(self, ctx):
        """Gives you statistics about the bot."""
        cmdsexec = self.bot.info['commands']
        memuse = str(round(psutil.Process(os.getpid()).memory_info().rss/1000000, 1)) + ' MB'
        shardnum = ctx.message.guild.shard_id
        uptime = str(round((time.time() - self.bot.up_at)/60, 1)) + ' min'
        guildcount = len(self.bot.guilds)
        usercount = len(self.bot.users)

        to_send = discord.Embed(title="Lilac Info/Stats", description="Statistics and information about Lilac.", color=0xbd8cbf)
        to_send.set_thumbnail(url="https://cdn.discordapp.com/avatars/405231585051410442/297df0d5c6f0cfbbaed347e4832d23fa.jpg?size=2048")
        to_send.add_field(name="Commands Executed", value=cmdsexec, inline=True)
        to_send.add_field(name="Memory Usage", value=memuse, inline=True)
        to_send.add_field(name="Shard #", value=shardnum, inline=True)
        to_send.add_field(name="Uptime", value=uptime, inline=True)
        to_send.add_field(name="Guilds", value=guildcount, inline=True)
        to_send.add_field(name="Users", value=usercount, inline=True)

        await self.bot.send(ctx, embed=to_send)


def setup(bot):
    bot.add_cog(Core(bot))
