#!/usr/bin/env python
from discord.ext import commands
import discord

class Misc:
    """Miscellaneous Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *args):
        send = discord.Embed()
        if len(args) == 0:
            send.title = "Lilac Help"
            send.description = "To get the commands in each category, use ```l!help <category-name>```"
            cats = [cog for cog in self.bot.cogs]
            cats.sort()
            for cat in cats:
                cat_cmds = self.bot.get_cog_commands(cat)
                send.add_field(name=cat, value='{} commands'.format(str(len(cat_cmds))), \
                                inline=True)
                

        await ctx.send(embed=send)
                

def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Misc(bot))
