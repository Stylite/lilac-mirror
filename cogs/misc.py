#!/usr/bin/env python
from discord.ext import commands
import discord

class Misc:
    """Miscellaneous Commands"""
    def __init__(self, bot):
        self.bot = bot

    def usage(self, cmd: commands.command):
        params_string = ''
        params = list(cmd.clean_params.items())
        for param in params:
            params_string += '<{}> '.format(param[0])
        
        return f'{self.bot.command_prefix}{cmd.name} {params_string}' 


    @commands.command()
    async def help(self, ctx, *args):
        """Shows the help message.
        
        What did you expect?!"""
        send = discord.Embed()
        send.colour = 0xbd8cbf

        cats = [cog for cog in self.bot.cogs]
        cats.sort()
        for cat in cats:
            if cat == 'Dev' and ctx.message.author.id not in self.bot.config['cleared']:
                cats.remove('Dev')

        all_cmds = []
        for cog in self.bot.cogs:
            if cog == 'Dev' and ctx.message.author.id not in self.bot.config['cleared']:
                continue

            cmds = self.bot.get_cog_commands(cog)
            all_cmds += cmds

        if len(args) == 0:
            send.title = "Lilac Help"
            send.description = "To get the commands in each category, use ```l!help <category-name>```"
            for cat in cats:
                cat_cmds = self.bot.get_cog_commands(cat)
                send.add_field(name=cat, value='{} commands'.format(str(len(cat_cmds))), inline=False)

        elif len(args) == 1:
            found = [False, False]
            search_term = args[0]
            for cat in cats:
                if cat.lower() == search_term.lower():
                    found[0] = True
                    cat_cmds = self.bot.get_cog_commands(cat)

                    send.title = '{} Commands'.format(cat)
                    send.description = 'To get more details about each command, use ' +\
                                     '```l!help <command-name>```'

                    for cmd in cat_cmds:
                        if cmd.brief is None and cmd.help is not None:
                            cmd.brief = cmd.help.split('\n')[0]
                        if cmd.help is None:
                            cmd.brief = 'No help message found.'
                        send.add_field(name=cmd.name, value=cmd.brief, inline=False)
                    break
            
            for cmd in all_cmds:
                if cmd.name.lower() == search_term.lower():
                    found[1] = True
                    
                    send.title = 'Help for command `{}`'.format(cmd.name)

                    cmd_help = cmd.help
                    if not cmd.help:
                        cmd_help = 'No help message for this command...'

                    send.description = 'Usage: {}\n\n{}'.format(self.usage(cmd), cmd_help)
                    break

            if found == [False, False]:
                ctx.send('Sorry, but I couldn\'t find that category/command!')
                return
        
        else:
            ctx.send(':warning: Too many arguments.')
            return
        
        await ctx.send(embed=send)
                

def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Misc(bot))
