#!/usr/bin/env python
import sys
import os
import subprocess
import asyncio
import importlib as il
import yaml

from discord.ext import commands
import discord

from cogs.util.checks import is_cleared


class Dev:
    """Developer commands. (For EJC and Adam)."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_cleared()
    async def sql(self, ctx, *, code: str):
        """Executes SQL on the database. Very dangerous."""
        dbcur = self.bot.database.cursor()
        dbcur.execute(code)
        res = dbcur.fetchall()
        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, f':white_check_mark: Executed. ```{res}```')

    @commands.command()
    @is_cleared()
    async def reload(self, ctx, *, cog):
        """Reloads a cog of the bot. 

        Developer only command."""
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await self.bot.send(ctx, ':warning: Failed to reload cog `{}`, because:```{}```'.format(cog, str(e)))
            self.bot.logger.log('LOAD', f'Failed to reload cog `{cog}`, because:\n\t{str(e)}')
        else:
            await self.bot.send(ctx, f':white_check_mark: Reloaded cog `{cog}`')
            self.bot.logger.log('LOAD', f'Reloaded cog `{cog}`')

    @commands.command(aliases=['reboot'])
    @is_cleared()
    async def restart(self, ctx):
        """Restarts the bot.

        Developer only command."""
        await self.bot.send(ctx, ':warning: Rebooting Lilac...')
        os.execl(sys.executable, sys.executable, * sys.argv)

    @commands.command(aliases=['shutdown'])
    async def shutoff(self, ctx):
        """Shuts the bot off."""
        await self.bot.send(ctx, ':white_check_mark: Shutting down!')
        sys.exit()

    @commands.command(aliases=['evaluate'])
    @is_cleared()
    async def debug(self, ctx, *, code: str):
        """Executes some code."""
        try:
            env = {}
            to_exec = 'async def func(ctx):\n'
            for line in code.splitlines():
                to_exec += f'  {line}\n'

            exec(to_exec, env)

            func = env['func']
            res = await func(ctx)
        except Exception as e:
            await self.bot.send(ctx, f':warning: Error: ```{str(e)}```')
            return
        else:
            if res is None:
                await ctx.message.add_reaction('✅')
            else:
                await self.bot.send(ctx, f':white_check_mark: Executed successfully. ```{res}```')

    @commands.command(aliases=['pgit'])
    @is_cleared()
    async def pull(self, ctx):
        """Pulls from Git.

        Developer only command.
        This will pull code from Git, effectively overwriting
        all local changes not pushed to Git."""
        await self.bot.send(ctx, ':warning: Pulling from Git! This will overwrite all local changes!')

        output = []
        outerr = []
        if sys.platform == 'win32':
            pull_process = subprocess.run(
                'git pull origin master', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output = pull_process.stdout
            outerr = pull_process.stderr
        else:
            pull_process = await asyncio.create_subprocess_exec('git', 'pull', 'origin', 'master',
                                                                 stdout=subprocess.PIPE, \
                                                                 stderr=subprocess.PIPE)
            output = pull_process.stdout
            outerr = pull_process.stderr

        output = '+ ' + '\n+ '.join(output.decode().splitlines())
        print(output)
        print(outerr)
        if not outerr is None:
            outerr = '- ' + '\n- '.join(outerr.decode().splitlines())
        else:
            outerr = ''
        await self.bot.send(ctx, f'**Git Response:** ```diff\n{output}{outerr}```')

    @commands.command(aliases=['bl'])
    @is_cleared()
    async def blacklist(self, ctx, *, user_id: int):
        """Blacklists a user from using Lilac commands.

        Prevents a user from using Lilac commands.
        **Do not mention the user**, use the user id."""
        user = self.bot.get_user(user_id)
        if user is None:
            await self.bot.send(ctx, ':warning: I couldn\'t find that user.')
            return

        if user_id in self.bot.blacklist:
            await self.bot.send(ctx, ':warning: That user has alreaady been blacklisted!')

        self.bot.blacklist.append(user_id)
        with open('data/gblacklist.txt', 'a') as blacklist_file:
            blacklist_file.write(str(user_id) + '\n')
        await self.bot.send(ctx, f':white_check_mark: **{ctx.message.author.name}**' +
                       f', I\'ve blacklisted `{user}` from using Lilac commands!')

        await self.bot.send(user, 'You\'ve been blacklisted from using Lilac commands globally.' +
                        ' Contact one of the devs to appeal.')

    @commands.command(aliases=['wl'])
    @is_cleared()
    async def whitelist(self, ctx, *, user_id: int):
        """Whitelists a blacklisted user.

        Allows them to use Lilac commands again. 
        **Do not mention the user**, use the user id."""
        user = self.bot.get_user(user_id)
        if user is None:
            await self.bot.send(ctx, ':warning: I couldn\'t find that user.')
            return

        if user_id not in self.bot.blacklist:
            await self.bot.send(ctx, ':warning: That user is not blacklisted!' +
                           ' You cannot whitelist someone who has not been blacklisted.')
            return

        self.bot.blacklist.remove(user_id)
        with open('data/gblacklist.txt', 'w') as blacklist_file:
            blacklist_file.writelines([str(uid) for uid in self.bot.blacklist])

        await self.bot.send(ctx, f':white_check_mark: I\'ve whitelisted `{user}`.' +
                       ' They are now able to use Lilac commands.')

        await self.bot.send(user, 'You\'ve been whitelisted to use Lilac commands, which means you are now ' +
                        'unblacklisted -- you can use Lilac commands.')

    @commands.command()
    @is_cleared()
    async def dm(self, ctx, user_id: int, *, message: str):
        """DMs any user accessible by the bot a message.

        Use their user ID."""
        user = self.bot.get_user(user_id)
        if user is None:
            await self.bot.send(ctx, ':warning: I couldn\'t find that user!')

        to_send = discord.Embed()
        to_send.colour = 0xbd8cbf
        to_send.description = message
        to_send.set_footer(text='A message from the developers of Lilac.')

        await self.bot.send(user, embed=to_send)
        await self.bot.send(ctx, ':white_check_mark: I\'ve DMed that user with your message!')

    @commands.command()
    @is_cleared()
    async def hoistuser(self, ctx, *, user_name: str):
        """Gets a user's information from their username & discrim."""
        found_user = None
        users = self.bot.get_all_members()
        for user in users:
            if str(user).lower() == user_name.lower():
                found_user = user
                break
        else:
            await self.bot.send(ctx, ':warning: I couldn\'t find that user!')
            return

        to_send = discord.Embed(title='Result found for user')
        to_send.colour = 0xbd8cbf 
        to_send.set_thumbnail(url=found_user.avatar_url)
        to_send.add_field(name='Username', value=str(found_user))
        to_send.add_field(name="User ID", value=str(found_user.id))
        to_send.add_field(name="Part of Guild", value=str(found_user.guild.name))
        to_send.add_field(name="Account Created", value=str(found_user.created_at))

        await self.bot.send(ctx, embed=to_send)

    @commands.command()
    @is_cleared()
    async def hoistguild(self, ctx, *, search_term: str):
        """Gets a guild's information."""
        found_guild = None
        for guild in self.bot.guilds:
            if search_term.lower() in guild.name.lower():
                found_guild = guild
                break
        else:
            await self.bot.send(ctx, ':warning: I couldn\'t find that guild!')
            return

        try:
            invite = await found_guild.channels[0].create_invite()
            invite = invite.url
        except:
            invite = 'N/A'
        
        verification_lvl = str(found_guild.verification_level)

        to_send = discord.Embed(title=found_guild.name)
        to_send.colour = 0xbd8cbf
        to_send.set_thumbnail(url=found_guild.icon_url)
        to_send.add_field(name='Owner', value=str(found_guild.owner))
        to_send.add_field(name='Invite Link', value=invite)
        to_send.add_field(name='# of Members', value=len(found_guild.members))
        to_send.add_field(name='# of Channels', value=len(found_guild.channels))
        to_send.add_field(name='Verification Level', value=str(verification_lvl))
        to_send.add_field(name='Region', value=str(found_guild.region))

        await self.bot.send(ctx, embed=to_send)

    @commands.command()
    @is_cleared()
    async def getlog(self, ctx, *, count: int):
        """Gets the last <count> log items."""
        logs = self.bot.logger.get_log(count)
        await self.bot.send(ctx, f'Here are the last **{count}** log items:\n```css\n{logs}\n```')

    @commands.command()
    @is_cleared()
    async def cmd(self, ctx, *, command: str):
        """Executes a command in CMD.
        
        [Windows]"""
        try:
            os.system(command)
        except Exception as e:
            await self.bot.send(ctx, f':warning: Error occured in executing command: `{str(e)}`')
        else:
            await self.bot.send(ctx, ':white_check_mark: Successfully executed command.')
        

    @commands.command()
    @is_cleared()
    async def edityml(self, ctx, file_name: str, key: str, val: str):
        """Edits the content of a YML file.
        
        Do not edit the contents of config.yml with this
        command."""
        def safe_eval(string):
            """Safely evaluates an int, bool, str, etc."""
            res = None
            try:
                res = eval(string)
            except NameError as e:
                return f'"{string}"'
            else:
                return res

        def edit_dict(d, keys, val):
            """Edits a value from a dict from a list of keys."""
            to_eval = 'd'
            for key in keys:
                to_eval += f'[{key}]'
            to_eval += f' = {val}'
            exec(to_eval)

            return d
            
        yml_file = yaml.load(open(file_name, 'r'))
        yml_file = edit_dict(yml_file, [safe_eval(k) for k in key.split('|')], \
                            safe_eval(val))
        yaml.dump(yml_file, open(file_name, 'w'))
        self.bot.load_files()

        await self.bot.send(
            ctx, 
            ':white_check_mark:'+\
            '```'+\
            f'"{file_name}"[{key}] = {val}'+\
            '```'
        )

def setup(bot):
    bot.add_cog(Dev(bot))
