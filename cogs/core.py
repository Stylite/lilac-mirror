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
    async def check(self):
        """Checks if the bot is up."""
        await self.bot.say('Bot is up and running!')

    @commands.command()
    @is_cleared()
    async def reload(self, *, cog):
        """Reloads a cog of the bot. 
        
        Developer only command."""
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

    @commands.command(aliases=['reboot'])
    async def restart(self):
        """Restarts the bot.
        
        Developer only command."""
        await self.bot.say(':warning: Rebooting Lilac...')
        os.execl(sys.executable, sys.executable, * sys.argv)
        await self.bot.say(':white_check_mark: Done rebooting!')

    @commands.command(aliases=['pgit'])
    @is_cleared()
    async def pull(self):
        """Pulls from Git.
        
        Developer only command.
        This will pull code from Git, effectively overwriting
        all local changes not pushed to Git."""
        await self.bot.say(':warning: Pulling from Git! This will overwrite all local changes!')

        output = []
        if sys.platform == 'win32':
            fetch_process = subprocess.run('git fetch --all', stdout=subprocess.PIPE)
            reset_process = subprocess.run('git reset --hard origin/master', stdout=subprocess.PIPE)
            output = [fetch_process.stdout, reset_process.stdout]
        else:
            fetch_process = await asyncio.create_subprocess_exec('git', 'fetch', '--all', \
                                                                    stdout=subprocess.PIPE)
            reset_process = await asyncio.create_subprocess_exec('git', 'reset', '--hard', \
                                                    'origin/master', stdout=subprocess.PIPE)
            output = [fetch_process.stdout, reset_process.stdout]
        
        output[0] = '\n'.join(output[0].decode().splitlines())
        output[1] = '\n'.join(output[1].decode().splitlines())
        await self.bot.say('**Git Response:** ```{}``````{}```'.format(output[0], output[1]))


def setup(bot):
    bot.add_cog(Core(bot))

