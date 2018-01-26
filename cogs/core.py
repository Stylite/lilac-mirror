#!/usr/bin/env python
import subprocess
import sys
import os
import asyncio

import discord
from discord.ext import commands

from cogs.util.checks import is_cleared

class Core:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check(self, ctx):
        """Checks if the bot is up."""
        await ctx.send('Bot is up and running!')

    @commands.command()
    @is_cleared()
    async def reload(self, ctx, *, cog):
        """Reloads a cog of the bot. 
        
        Developer only command."""
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(':warning: Failed to reload cog `{}`, because:```{}```'.format(cog, str(e)))
            print('[LOAD] Failed to reload cog `{}`, because: '.format(cog))
            print(e)
        else:
            await ctx.send(':white_check_mark: Reloaded cog `{}`'.format(cog))
            print('[LOAD] Reloaded cog `{}`'.format(cog))

    @commands.command(aliases=['reboot'])
    async def restart(self, ctx):
        """Restarts the bot.
        
        Developer only command."""
        await ctx.send(':warning: Rebooting Lilac...')
        os.execl(sys.executable, sys.executable, * sys.argv)
        await ctx.send(':white_check_mark: Done rebooting!')

    @commands.command(aliases=['pgit'])
    @is_cleared()
    async def pull(self, ctx):
        """Pulls from Git.
        
        Developer only command.
        This will pull code from Git, effectively overwriting
        all local changes not pushed to Git."""
        await ctx.send(':warning: Pulling from Git! This will overwrite all local changes!')

        output = []
        if sys.platform == 'win32':
            fetch_process = subprocess.run('git pull', stdout=subprocess.PIPE)
            
            output = fetch_process.stdout
        else:
            fetch_process = await asyncio.create_subprocess_exec('git', 'pull', \
                                                                    stdout=subprocess.PIPE)
            output = fetch_process.stdout
        
        output[0] = '\n'.join(output.decode().splitlines())
        await ctx.send('**Git Response:** ```{}```'.format(output))


def setup(bot):
    bot.add_cog(Core(bot))

