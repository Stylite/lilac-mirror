#!/usr/bin/env python
import sys
import os
import subprocess
import asyncio
import importlib as il

from discord.ext import commands
import discord

from cogs.util.checks import is_cleared

class Dev:
    """Developer commands. (For EJC and Adam)."""
    def __init__(self, bot):
        self.bot = bot
    
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
    @is_cleared()
    async def restart(self, ctx):
        """Restarts the bot.
        
        Developer only command."""
        await ctx.send(':warning: Rebooting Lilac...')
        os.execl(sys.executable, sys.executable, * sys.argv)
        await ctx.send(':white_check_mark: Done rebooting!')

    @commands.command(aliases=['evaluate'])
    @is_cleared()
    async def debug(self, ctx, *, code: str):
        """Evaluates some code.
    
        Must be an expression."""
        try:
            res = eval(code)
        except Exception as e:
            await ctx.send(f':warning: Error: ```{str(e)}```')
            return
        else:
            await ctx.send(f':white_check_mark: Execution successful. Result: ```{str(res)}```')

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
            fetch_process = subprocess.run('git pull origin master', stdout=subprocess.PIPE)
            
            output = fetch_process.stdout
        else:
            fetch_process = await asyncio.create_subprocess_exec('git', 'pull', 'origin', 'master', \
                                                                    stdout=subprocess.PIPE)
            output = fetch_process.stdout
        
        output = '\n'.join(output.decode().splitlines())
        await ctx.send('**Git Response:** ```{}```'.format(output))

    @commands.command(aliases=['bl'])
    @is_cleared()
    async def blacklist(self, ctx, *, user_id: int):
        """Blacklists a user from using Lilac commands.
        
        Prevents a user from using Lilac commands.
        **Do not mention the user**, use the user id."""
        user = self.bot.get_user(user_id)
        if user is None:
            await ctx.send(':warning: I couldn\'t find that user.')
            return

        if user_id in self.bot.blacklist:
            await ctx.send(':warning: That user has alreaady been blacklisted!')

        self.bot.blacklist.append(user_id)
        with open('data/gblacklist.txt', 'a') as blacklist_file:
            blacklist_file.write(str(user_id) + '\n')
        await ctx.send(f':white_check_mark: **{ctx.message.author.name}**'+\
                f', I\'ve blacklisted `{user}` from using Lilac commands!')
        
        await user.send('You\'ve been blacklisted from using Lilac commands globally.' +\
                    ' Contact one of the devs to appeal.')

    @commands.command(aliases=['wl'])
    @is_cleared()
    async def whitelist(self, ctx, *, user_id: int):
        """Whitelists a blacklisted user.
        
        Allows them to use Lilac commands again. 
        **Do not mention the user**, use the user id."""
        user = self.bot.get_user(user_id)
        if user is None:
            await ctx.send(':warning: I couldn\'t find that user.')
            return

        if user_id not in self.bot.blacklist:
            await ctx.send(':warning: That user is not blacklisted!'+\
                            ' You cannot whitelist someone who has not been blacklisted.')
            return

        self.bot.blacklist.remove(user_id)
        with open('data/gblacklist.txt', 'w') as blacklist_file:
            blacklist_file.writelines([str(uid) for uid in self.bot.blacklist])

        await ctx.send(f':white_check_mark: I\'ve whitelisted `{user}`.'+\
                        ' They are now able to use Lilac commands.')

        await user.send('You\'ve been whitelisted to use Lilac commands, which means you are now '+\
                        'unblacklisted -- you can use Lilac commands.')

    @commands.command()
    @is_cleared()
    async def dm(self, ctx, user_id: int, *, message: str):
        user = self.bot.get_user(user_id)
        if user is None:
            await ctx.send(':warning: I couldn\'t find that user!')

        to_send = discord.Embed()
        to_send.colour = 0xbd8cbf
        to_send.description = message
        to_send.set_footer(text='A message from the developers of Lilac.')

        await user.send(embed=to_send)
        await ctx.send(':white_check_mark: I\'ve DMed that user with your message!')


def setup(bot):
    bot.add_cog(Dev(bot))