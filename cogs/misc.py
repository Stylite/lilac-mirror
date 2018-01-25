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

        cats = [cog for cog in self.bot.cogs]
        cats.sort()
        all_cmds = []
        for cog in self.bot.cogs:
            cmds = self.bot.get_cog_commands(cog)
            all_cmds += cmds

        if len(args) == 0:
            send.title = "Lilac Help"
            send.description = "To get the commands in each category, use ```l!help <category-name>```"
            for cat in cats:
                cat_cmds = self.bot.get_cog_commands(cat)
                send.add_field(name=cat, value='{} commands'.format(str(len(cat_cmds))), \
                                inline=True)

        elif len(args) == 1:
            search_term = args[0]
            for cat in cats:
                if cat.lower() == search_term.lower():
                    cat_cmds = self.bot.get_cog_commands(cat)
                    send.title = '{} Commands'.format(cat)
                    send.description = 'To get more details about each command, use ' +\
                                     '```l!help <command-name>```'
                    for cmd in cat_cmds:
                        send.add_field(name=cmd.name, value=cmd.brief, inline=True)
                    
        
        await ctx.send(embed=send)
                

def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Misc(bot))
