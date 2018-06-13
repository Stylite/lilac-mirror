#!/usr/bin/env python
import asyncio 
import yaml
from cogs.util.checks import manage_usrs, manage_guild, manage_roles, manage_messages

from discord.ext import commands
import discord


class Mod:
    """Moderation Commands"""

    def __init__(self, bot):
        self.bot = bot

        dbcur = self.bot.database.cursor()
        dbcur.execute('''
            CREATE TABLE IF NOT EXISTS 
            autoroles(guild_id INTEGER, role_id INTEGER)''')
        dbcur.execute('''
            CREATE TABLE IF NOT EXISTS 
            selfroles(guild_id INTEGER, role_id INTEGER)''')
        dbcur.execute('''
            CREATE TABLE IF NOT EXISTS
            welcomes(guild_id INTEGER, message TEXT, channel_id INTEGER)''')
        dbcur.execute('''
            CREATE TABLE IF NOT EXISTS
            goodbyes(guild_id INTEGER, message TEXT, channel_id INTEGER)''')
        dbcur.execute('''
            CREATE TABLE IF NOT EXISTS
            logs(guild_id INTEGER, channel_id INTEGER)''')        
        
        self.bot.database.commit()
        dbcur.close()

    @commands.command()
    @manage_usrs()
    async def mute(self, ctx, mention: str):
        """Mutes a user.
        
        Creates a role name `lilac-mute`, loops through
        all the channels and sets the role to be unable to
        speak, and gives mentioned person the role."""
        to_mute = None
        if ctx.message.mentions:
            to_mute = ctx.message.mentions[0]
        else:
            await self.bot.send(ctx, ':warning: You did not mention a user to mute.')

        mute_role = None
        guild = ctx.message.guild
        if 'lilac-mute' not in [r.name for r in guild.roles]:
            mute_role = await guild.create_role(name='lilac-mute', reason='create mute role')
        else:
            for role in guild.roles:
                if role.name == 'lilac-mute':
                    mute_role = role
            if mute_role in to_mute.roles:
                await self.bot.send(ctx, f':warning: `{str(to_mute)}` is already muted!')
                return

        perm_overwrite_pair = (mute_role, discord.PermissionOverwrite(send_messages=False, \
                                send_tts_messages=False))
        for channel in guild.channels:
            if perm_overwrite_pair not in channel.overwrites:
                await channel.set_permissions(perm_overwrite_pair[0], overwrite=perm_overwrite_pair[1])

        await to_mute.add_roles(mute_role)
        await self.bot.send(ctx, f':white_check_mark: I\'ve muted `{str(to_mute)}`! You can unmute them'+\
                        ' by removing their `lilac-mute` role, or by running `unmute @user`.')

    @commands.command()
    @manage_usrs()
    async def unmute(self, ctx, *, user_mention: str):
        """Unmutes a user."""
        to_unmute = None
        if ctx.message.mentions:
            to_unmute = ctx.message.mentions[0]
        else:
            await self.bot.send(ctx, ':warning: You did not mention a user to unmute.')

        if 'lilac-mute' not in [r.name for r in to_unmute.roles]:
            await self.bot.send(ctx, ':warning: That user is not currently muted!')
            return

        mute_role = None
        for role in ctx.message.guild.roles:
            if role.name == 'lilac-mute':
                mute_role = role 

        await to_unmute.remove_roles(mute_role)
        
        await self.bot.send(ctx, f':white_check_mark: I\'ve unmuted `{str(to_unmute)}`! They can now speak!')
            

    @commands.command()
    @manage_usrs()
    async def ban(self, ctx, *, mention: str):
        """Bans a user. 

        You must provide a mention for the bot to ban."""
        to_ban = None
        if ctx.message.mentions:
            to_ban = ctx.message.mentions[0]
        else:
            await self.bot.send(ctx, ':warning: You did not mention a user to ban.')
            return

        await ctx.message.guild.ban(to_ban)
        await self.bot.send(ctx, ':white_check_mark: Successfully banned user `{}#{}`'
                       .format(to_ban.name, to_ban.discriminator))

    @commands.command()
    @manage_usrs()
    async def kick(self, ctx, *, mention: str):
        """Kicks a user. 

        You must provide a mention for the bot to kick."""
        to_kick = None
        if ctx.message.mentions:
            to_kick = ctx.message.mentions[0]
        else:
            await self.bot.send(ctx, ':warning: You did not mention a user to kick.')
            return

        await ctx.message.guild.kick(to_kick)
        await self.bot.send(ctx, ':white_check_mark: Successfully kicked user `{}#{}`.'
                       .format(to_kick.name, to_kick.discriminator))

    @commands.group()
    async def autorole(self, ctx):
        """Manages autoroles.

        To create an autorole, do `autorole add <role-name>`. [Requires ManageRoles]
        To remove an autorole, do `autorole remove <role-name>`. [Requires ManageRoles]
        To list autoroles, do `autorole list`."""
        if ctx.invoked_subcommand is None:
            await self.bot.send(ctx, 
                "To create an autorole, do `autorole add <role-name>`. [Requires ManageRoles]\n"+\
                "To remove an autorole, do `autorole remove <role-name>`. [Requires ManageRoles]\n"+\
                "To list autoroles, do `autorole list`.\n"
            )
            return

    @autorole.command(name='add')
    @manage_roles()
    async def _aradd(self, ctx, *, role_name: str):
        dbcur = self.bot.database.cursor()

        to_add = None
        for role in ctx.message.guild.roles:
            if role_name.lower() == role.name.lower():
                to_add = role
                break
        else:
            await self.bot.send(ctx, f':warning: Role `{role_name}` not found.')
            dbcur.close()
            return

        dbcur.execute(f'SELECT role_id FROM autoroles WHERE guild_id={ctx.message.guild.id}')
        if to_add.id in [x[0] for x in dbcur.fetchall()]:
            await self.bot.send(ctx, ':warning: That role is already an autorole!')
            dbcur.close()
            return

        dbcur.execute('INSERT INTO autoroles(guild_id,role_id) VALUES (?,?)',
                        (ctx.message.guild.id, to_add.id))

        self.bot.database.commit()
        dbcur.close()
            
        await self.bot.send(ctx, f':white_check_mark: Role `{to_add.name}` added to autoroles.')

    @autorole.command(name='remove')
    @manage_roles()
    async def _arremove(self, ctx, *, role_name: str):
        dbcur = self.bot.database.cursor()

        to_remove = None
        for role in ctx.message.guild.roles:
            if role_name.lower() == role.name.lower():
                to_remove = role
                break
        else:
            await self.bot.send(ctx, f':warning: Role `{role_name}` not found.')
            dbcur.close()
            return

        dbcur.execute(f'SELECT * FROM autoroles WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) > 0:
            dbcur.execute(f'SELECT role_id FROM autoroles WHERE guild_id={ctx.message.guild.id}')

            autorole_ids = [x[0] for x in dbcur.fetchall()]
            if to_remove.id in autorole_ids:
                dbcur.execute(f'DELETE FROM autoroles WHERE role_id={to_remove.id}')
            else:
                await self.bot.send(ctx, ':warning: That role is not an autorole.')
                dbcur.close()
                return
        else:
            await self.bot.send(ctx, ':warning: You currently do not have any autoroles.')
            dbcur.close()
            return

        await self.bot.send(ctx, f':white_check_mark: Removed role `{to_remove.name}` from autoroles.')
        
    @autorole.command(name='list')
    async def _arlist(self, ctx):
        dbcur = self.bot.database.cursor()

        dbcur.execute(f'SELECT * FROM autoroles WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, ':warning: This guild does not have any autoroles.')
            dbcur.close()
            return

        dbcur.execute(f'SELECT role_id FROM autoroles WHERE guild_id={ctx.message.guild.id}')
        autorole_ids = [x[0] for x in dbcur.fetchall()]
        autorole_names = []

        for r_id in autorole_ids:
            for r in ctx.message.guild.roles:
                if r_id == r.id:
                    autorole_names.append(r.name)
                    break
            else:
                dbcur.execute(f'DELETE FROM autoroles WHERE role_id={r_id}')

        if len(autorole_names) == 0:
            await self.bot.send(ctx, 'This guild does not have any autoroles.')
            return

        msg = 'This server\'s autoroles are: ```'
        for role in autorole_names:
            msg += f'• {role}\n'
        msg += '```'

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, msg)

    @commands.group()
    @manage_roles()
    async def selfrole(self, ctx):
        """Manages selfroles.

        To create a selfrole, do `,selfrole add <role_name>`. [Requires ManageRoles] 
        To remove a selfrole, do `,selfrole remove <role_name>`. [Requires ManageRoles]
        To list selfroles, do `,selfrole list`."""
        if ctx.invoked_subcommand is None:
            await self.bot.send(ctx, 
                "To create a selfrole, do `,selfrole add <role_name>`. [Requires ManageRoles]\n"+\
                "To remove a selfrole, do `,selfrole remove <role_name>`. [Requires ManageRoles]\n"+\
                "To list selfroles, do `,selfrole list`."
            )
            return
        
    @selfrole.command(name='add')
    @manage_roles()
    async def _sradd(self, ctx, *, role_name: str):
        dbcur = self.bot.database.cursor()

        role = None
        for r in ctx.message.guild.roles:
            if r.name.lower() == role_name.lower():
                role = r
                break
        else:
            await self.bot.send(ctx, f':warning: Role `{role_name}` was not found.')
            return

        dbcur.execute('INSERT INTO selfroles(guild_id, role_id) VALUES (?,?)',
                     (ctx.message.guild.id, role.id))

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, f':white_check_mark: I have added `{role_name}` to selfroles!')

    @selfrole.command(name='remove')
    @manage_roles()
    async def _srremove(self, ctx, *, role_name: str):
        dbcur = self.bot.database.cursor()

        role = None
        for r in ctx.message.guild.roles:
            if r.name.lower() == role_name.lower():
                role = r
                break
        else:
            await self.bot.send(ctx, f':warning: Role `{role_name}` was not found.')
            return

        dbcur.execute(f'SELECT * FROM selfroles WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, f':warning: Your guild does not have any selfroles. ' +
                            'Thus, I cannot remove a role from the nonexistent selfroles list.')
            return

        dbcur.execute(f'DELETE FROM selfroles WHERE role_id={role.id}')
        
        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, f':white_check_mark: Role `{role_name}` was removed from the selfroles!')

    @selfrole.command(name='list')
    async def _srlist(self, ctx):
        """Lists all the selfroles for a guild."""
        dbcur = self.bot.database.cursor()
        
        dbcur.execute(f'SELECT * FROM selfroles WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, ':warning: This guild does not have any selfroles.')
            return

        dbcur.execute(f'SELECT role_id FROM selfroles WHERE guild_id={ctx.message.guild.id}')
        selfrole_ids = [x[0] for x in dbcur.fetchall()]
        selfrole_names = []

        for r_id in selfrole_ids:
            for r in ctx.message.guild.roles:
                if r_id == r.id:
                    selfrole_names.append(r.name)
                    break
            else:
                dbcur.execute(f'DELETE FROM selfroles WHERE role_id={r_id}')

        if len(selfrole_names) == 0:
            await self.bot.send(ctx, ':warning: This guild does not have any selfroles.')
            return

        msg = 'This server\'s selfroles are: ```'
        for role in selfrole_names:
            msg += f'• {role}\n'
        msg += '```'

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, msg)

    @commands.group()
    async def welcome(self, ctx):
        """Manages the welcome message.
        
        To set the welcome message, do `welcome set <message>`.
           - To mention the user who joined, use `%mention%` in the message.
        To set the welcome channel, do `welcome channel <channel-mention>.`
        To disable welcome messages, do `welcome disable.`"""
        if ctx.invoked_subcommand is None:
            await self.bot.send(ctx, 
                "To set the welcome message, do `welcome set <message>`.\n"+\
                "    - To mention the user who joined, use `%mention%` in the message.\n"+\
                "To set the welcome channel, do `welcome channel <channel-mention>.`\n"+\
                "To disable welcome messages, do `welcome disable`."
            )
            return

    @welcome.command(name='set')
    @manage_guild()
    async def _wmset(self, ctx, *, message: str):
        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM welcomes WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            dbcur.execute(f'INSERT INTO welcomes(guild_id,message,channel_id) VALUES (?,?,?)',\
                         (ctx.message.guild.id, message, 0))
        else:
            dbcur.execute(f'''UPDATE welcomes SET message="{message}"
                              WHERE guild_id={ctx.message.guild.id}''')

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, ':white_check_mark: Set the welcome message for this guild.')

    @welcome.command(name='channel')
    @manage_guild()
    async def _wmchannel(self, ctx, *, channel_mention: str):
        """Sets the welcome channel for user join messages.

        You must mention the channel."""
        dbcur = self.bot.database.cursor()

        dbcur.execute(f'SELECT * FROM welcomes WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, ':warning: You need to set a welcome message before setting the ' +\
                           'welcome channel.')
            return

        if len(ctx.message.channel_mentions) == 0:
            await self.bot.send(ctx, ':warning: You have not provided a channel mention for your welcome channel.')
            return

        dbcur.execute(f'''UPDATE welcomes SET channel_id={ctx.message.channel_mentions[0].id}
                          WHERE guild_id={ctx.message.guild.id}''')

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, ':white_check_mark: Set your welcome channel to `{}`.'
                       .format(ctx.message.channel_mentions[0]))

    @welcome.command(name='disable')
    @manage_guild()
    async def _wmdisable(self, ctx):
        dbcur = self.bot.database.cursor()

        dbcur.execute(f'SELECT * FROM welcomes WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, ':stop_sign: This guild does not have welcome messages enabled!')
            return
        
        dbcur.execute(f'DELETE FROM welcomes WHERE guild_id={ctx.message.guild.id}')

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, ':thumbsup: Disabled welcome messages for this guild!')

    @commands.group()
    async def goodbye(self, ctx):
        """Manages the goodbye message.
        
        To set the goodbye message, do `goodbye set <message>`.
           - To get the username of the member who left, use `%name%` in the message.
        To set the goodbye channel, do `goodbye channel <channel-mention>.`
        To disable goodbye messages, do `goodbye disable`."""
        if ctx.invoked_subcommand is None:
            await self.bot.send(ctx, 
                "To set the goodbye message, do `goodbye set <message>`.\n"+\
                "    - To get the username of the member who left, use `%name%` in the message.\n"+\
                "To set the goodbye channel, do `goodbye channel <channel-mention>.`\n"+\
                "To disable goodbye messages, do `goodbye disable`."
            )
            return

    @goodbye.command(name='set')
    @manage_guild()
    async def _gbmset(self, ctx, *, message: str):
        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM goodbyes WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            dbcur.execute(f'INSERT INTO goodbyes(guild_id,message,channel_id) VALUES (?,?,?)',\
                         (ctx.message.guild.id, message, 0))
        else:
            dbcur.execute(f'''UPDATE goodbyes SET message="{message}"
                              WHERE guild_id={ctx.message.guild.id}''')

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, ':white_check_mark: Set the goodbye message for this guild.')

    @goodbye.command(name='channel')
    @manage_guild()
    async def _gbmchannel(self, ctx, *, channel_mention: str):
        dbcur = self.bot.database.cursor()

        dbcur.execute(f'SELECT * FROM goodbyes WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, ':warning: You need to set a goodbye message before setting the ' +\
                           'goodbye channel.')
            return

        if len(ctx.message.channel_mentions) == 0:
            await self.bot.send(ctx, ':warning: You have not provided a channel mention for your goodbye channel.')
            return

        dbcur.execute(f'''UPDATE goodbyes SET channel_id={ctx.message.channel_mentions[0].id}
                          WHERE guild_id={ctx.message.guild.id}''')

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, ':white_check_mark: Set your goodbye channel to `{}`.'
                       .format(ctx.message.channel_mentions[0]))

    @goodbye.command(name='disable')
    @manage_guild()
    async def _gbmdisable(self, ctx):
        dbcur = self.bot.database.cursor()

        dbcur.execute(f'SELECT * FROM goodbyes WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, ':stop_sign: This guild does not have goodbye messages enabled!')
            return
        
        dbcur.execute(f'DELETE FROM goodbyes WHERE guild_id={ctx.message.guild.id}')

        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, ':thumbsup: Disabled goodbye messages for this guild!')

    @commands.command()
    async def getrole(self, ctx, *, role_name: str):
        """Gets a selfrole."""
        dbcur = self.bot.database.cursor()

        role = None
        for r in ctx.message.guild.roles:
            if r.name.lower() == role_name.lower():
                role = r
                break
        else:
            await self.bot.send(ctx, f':warning: Role `{role_name}` was not found.')
            return

        if role in ctx.message.author.roles:
            await self.bot.send(ctx, ':warning: You already have that role.')
            return

        dbcur.execute(f'SELECT * FROM selfroles WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, ':warning: That role isn\'t a selfrole -- in fact, this guild ' +
                           'doesn\'t even have any selfroles.')
            return

        dbcur.execute(f'SELECT role_id FROM selfroles WHERE guild_id={ctx.message.guild.id}')
        if role.id not in [x[0] for x in dbcur.fetchall()]:
            await self.bot.send(ctx, ':warning: That role isn\'t a selfrole.')
            return

        dbcur.close()

        await ctx.message.author.add_roles(role)
        await self.bot.send(ctx, f':white_check_mark: **{ctx.message.author.name}**, you now have `{role.name}` role.')

    @commands.command(aliases=['loserole'])
    async def droprole(self, ctx, *, role_name: str):
        """Removes a selfrole."""
        dbcur = self.bot.database.cursor()

        role = None
        for r in ctx.message.guild.roles:
            if r.name.lower() == role_name.lower():
                role = r
                break
        else:
            await self.bot.send(ctx, f':warning: Role `{role_name}` was not found.')
            return

        if role not in ctx.message.author.roles:
            await self.bot.send(ctx, ':warning: You do not have that role.')
            return

        dbcur.execute(f'SELECT * FROM selfroles WHERE guild_id={ctx.message.guild.id}')
        if len(dbcur.fetchall()) == -0:
            await self.bot.send(ctx, ':warning: That role isn\'t a selfrole -- in fact, this guild ' +
                           'doesn\'t even have any selfroles.')
            return

        dbcur.execute(f'SELECT role_id FROM selfroles WHERE guild_id={ctx.message.guild.id}')
        if role.id not in [x[0] for x in dbcur.fetchall()]:
            await self.bot.send(ctx, ':warning: That role isn\'t a selfrole.')
            return

        dbcur.close()

        await ctx.message.author.remove_roles(role)
        await self.bot.send(ctx, f':white_check_mark: **{ctx.message.author.name}**, you no longer have `{role.name}` role.')

    @commands.command()
    @manage_guild()
    async def prefix(self, ctx, *, new_prefix: str):
        """Sets the prefix for the guild."""
        self.bot.prefixes[ctx.message.guild.id] = new_prefix
        yaml.dump(self.bot.prefixes, open('data/prefixes.yml', 'w'))

        await self.bot.send(ctx, f':white_check_mark: Changed this guild\'s prefix to `{new_prefix}`')

    @commands.command(aliases=['clear'])
    @manage_messages()
    async def purge(self, ctx, *, number: int):
        """Purges a number of messages.
        
        Number must be between 1 & 100."""
        if number < 1 or number > 100:
            await self.bot.send(ctx, ':warning: I can only purge between 1 and 100 messages!') 
            return
        
        await ctx.channel.purge(limit=number+1, bulk=True)

    @commands.group(aliases=['modlog'])
    @manage_guild()
    async def log(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("WIP")

    @log.command()
    @manage_guild()
    async def enable(self, ctx):
        guild = ctx.message.guild

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM logs WHERE guild_id={guild.id}')
        if len(dbcur.fetchall()) > 0:
            await self.bot.send(ctx, f'{self.bot.emotes.xmark} Your guild already has modlogs enabled!')
            return

        dbcur.execute(f'INSERT INTO logs(guild_id, channel_id) VALUES ({guild.id}, null)')
        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, f'{self.bot.emotes.check} Enabled logs for this guild.')

    @log.command()
    @manage_guild()
    async def disable(self, ctx):
        guild = ctx.message.guild

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM logs WHERE guild_id={guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, f'{self.bot.emotes.xmark} Your guild does not have modlogs enabled!')
            return

        dbcur.execute(f'DELETE FROM logs WHERE guild_id={guild.id}')
        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, f'{self.bot.emotes.check} Disabled logs for this guild.')

    @log.command()
    @manage_guild()
    async def channel(self, ctx, *, channel_mention: str):
        if not ctx.message.channel_mentions:
            await self.bot.send(ctx, f'{self.bot.emotes.xmark} You must mention a channel for modlogs.')
            return
        channel = ctx.message.channel_mentions[0]
        guild = ctx.message.guild
        
        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM logs WHERE guild_id={guild.id}')
        if len(dbcur.fetchall()) == 0:
            await self.bot.send(ctx, f'{self.bot.emotes.xmark} Your guild must have modlogs'+\
                                ' enabled before setting the log channel.')
            return
        
        dbcur.execute(f'UPDATE logs SET channel_id={channel.id} WHERE guild_id={guild.id}')
        self.bot.database.commit()
        dbcur.close()

        await self.bot.send(ctx, f'{self.bot.emotes.check} Set {channel.mention} as this'+\
                            ' guild\'s modlog channel.')

def setup(bot):
    bot.add_cog(Mod(bot))
