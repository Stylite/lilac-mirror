#!/usr/bin/env python
import asyncio 
import yaml
from cogs.util.checks import manage_usrs, manage_guild, manage_roles

from discord.ext import commands
import discord


class Mod:
    """Moderation Commands"""

    def __init__(self, bot):
        self.bot = bot

        dbcur = self.bot.database.cursor()
        dbcur.execute('''
            CREATE TABLE IF NOT EXISTS 
            autoroles(guild_id INTEGER, role_ids TEXT)''')
        dbcur.execute('''
            CREATE TABLE IF NOT EXISTS 
            selfroles(guild_id INTEGER, role_ids TEXT)''')
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
            await ctx.send(':warning: You did not mention a user to mute.')

        mute_role = None
        guild = ctx.message.guild
        if 'lilac-mute' not in [r.name for r in guild.roles]:
            mute_role = await guild.create_role(name='lilac-mute', reason='create mute role')
        else:
            for role in guild.roles:
                if role.name == 'lilac-mute':
                    mute_role = role
            if mute_role in to_mute.roles:
                await ctx.send(f':warning: `{str(to_mute)}` is already muted!')
                return

        perm_overwrite_pair = (mute_role, discord.PermissionOverwrite(send_messages=False, \
                                send_tts_messages=False))
        for channel in guild.channels:
            if perm_overwrite_pair not in channel.overwrites:
                await channel.set_permissions(perm_overwrite_pair[0], overwrite=perm_overwrite_pair[1])

        await to_mute.add_roles(mute_role)
        await ctx.send(f':white_check_mark: I\'ve muted `{str(to_mute)}`! You can unmute them'+\
                        ' by removing their `lilac-mute` role, or by running `unmute @user`.')

    @commands.command()
    @manage_usrs()
    async def unmute(self, ctx, *, user_mention: str):
        """Unmutes a user."""
        to_unmute = None
        if ctx.message.mentions:
            to_unmute = ctx.message.mentions[0]
        else:
            await ctx.send(':warning: You did not mention a user to unmute.')

        if 'lilac-mute' not in [r.name for r in to_unmute.roles]:
            await ctx.send(':warning: That user is not currently muted!')
            return

        mute_role = None
        for role in ctx.message.guild.roles:
            if role.name == 'lilac-mute':
                mute_role = role 

        await to_unmute.remove_roles(mute_role)
        
        await ctx.send(f':white_check_mark: I\'ve unmuted `{str(to_unmute)}`! They can now speak!')
            

    @commands.command()
    @manage_usrs()
    async def ban(self, ctx, *, mention: str):
        """Bans a user. 

        You must provide a mention for the bot to ban."""
        to_ban = None
        if ctx.message.mentions:
            to_ban = ctx.message.mentions[0]
        else:
            await ctx.send(':warning: You did not mention a user to ban.')
            return

        await ctx.message.guild.ban(to_ban)
        await ctx.send(':white_check_mark: Successfully banned user `{}#{}`'
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
            await ctx.send(':warning: You did not mention a user to kick.')
            return

        await ctx.message.guild.kick(to_kick)
        await ctx.send(':white_check_mark: Successfully kicked user `{}#{}`.'
                       .format(to_kick.name, to_kick.discriminator))

    @commands.command()
    @manage_guild()
    async def welcome(self, ctx, *, welcome_message: str):
        """Sets the welcome message for user joins.

        To mention the user joined in your welcome message, use
        %mention%."""

        if ctx.message.guild.id not in self.bot.welcomes:
            self.bot.welcomes[ctx.message.guild.id] = [None, None]

        self.bot.welcomes[ctx.message.guild.id][1] = welcome_message
        yaml.dump(self.bot.welcomes, open('data/welcomes.yml', 'w'))

        await ctx.send(':white_check_mark: Set the welcome message for this guild.')

    @commands.command(aliases=['welcomechnl'])
    @manage_guild()
    async def welcomechannel(self, ctx, *, channel_mention: str):
        """Sets the welcome channel for user join messages.

        You must mention the channel."""
        if ctx.message.guild.id not in self.bot.welcomes:
            await ctx.send(':warning: You need to set a welcome message before setting the ' +
                           'welcome channel.')
            return
        if len(ctx.message.channel_mentions) == 0:
            await ctx.send(':warning: You have not provided a channel mention for your welcome channel.')
            return
        self.bot.welcomes[ctx.message.guild.id][0] = ctx.message.channel_mentions[0].id
        yaml.dump(self.bot.welcomes, open('data/welcomes.yml', 'w'))

        await ctx.send(':white_check_mark: Set your welcome channel to `{}`.'
                       .format(ctx.message.channel_mentions[0]))

    @commands.command()
    @manage_roles()
    async def autorole(self, ctx, action: str, *, role_name: str):
        """Creates/removes autoroles.

        To create an autorole, do `,autorole add <role-name>`.
        To remove an autorole, do `,autorole remove <role-name>`"""

        dbcur = self.bot.database.cursor()

        if action.lower() == 'add':
            to_add = None
            for role in ctx.message.guild.roles:
                if role_name.lower() == role.name.lower():
                    to_add = role
                    break
            else:
                await ctx.send(f':warning: Role `{role_name}` not found.')
                return

            dbcur.execute(f'SELECT * FROM autoroles WHERE guild_id={ctx.message.guild.id}')
            if len(dbcur.fetchall()) > 0:
                dbcur.execute(f"""UPDATE autoroles SET role_ids=role_ids||' {to_add.id}' 
                              WHERE guild_id={ctx.message.guild.id}""")
            else:
                dbcur.execute('INSERT INTO autoroles(guild_id,role_ids) (?,?)',
                             (ctx.message.guild.id, str(to_add.id)))
                
            await ctx.send(f':white_check_mark: Role `{to_add.name}` added to autoroles.')

        elif action.lower() == 'remove':
            to_remove = None
            for role in ctx.message.guild.roles:
                if role_name.lower() == role.name.lower():
                    to_remove = role
                    break
            else:
                await ctx.send(f':warning: Role `{role_name}` not found.')
                return

            dbcur.execute(f'SELECT * FROM autoroles WHERE guild_id={ctx.message.guild.id}')
            if len(dbcur.fetchall()) > 0:
                dbcur.execute(f'SELECT role_ids FROM autoroles WHERE guild_id={ctx.message.guild.id}')
                autorole_ids = [int(role_id) for role_id in dbcur.fetchall()[0].split()]
                if to_remove.id in autorole_ids:
                    new_rid_str = ' '.join([str(r_id) for r_id in autorole_ids.remove(to_remove.id)])
                    dbcur.execute(f'''UPDATE autoroles SET role_ids={new_rid_str} 
                                  WHERE guild_id={ctx.message.guild.id}''')
                else:
                    await ctx.send(':warning: That role is not an autorole.')
                    return
            else:
                await ctx.send(':warning: You currently do not have any autoroles.')
                return

            await ctx.send(f':white_check_mark: Removed role `{to_remove.name}` from autoroles.')

        else:
            await ctx.send(':warning: Invalid action. The valid actions are `add` and `remove`.')

        self.bot.database.commit()
        dbcur.close()

    @commands.command()
    @manage_roles()
    async def autoroles(self, ctx):
        """Lists current autoroles."""
        if ctx.message.guild.id not in self.bot.autoroles:
            await ctx.send('This guild does not have any autoroles.')
            return

        autorole_ids = self.bot.autoroles[ctx.message.guild.id]
        autorole_names = []

        for r_id in autorole_ids:
            for r in ctx.message.guild.roles:
                if r_id == r.id:
                    autorole_names.append(r.name)
                    break
            else:
                self.bot.autoroles[ctx.message.guild.id].remove(r_id)
                yaml.dump(self.bot.autoroles, open('data/autoroles.yml', 'w'))

        if len(autorole_names) == 0:
            await ctx.send('This guild does not have any autoroles.')
            return

        msg = 'This server\'s autoroles are: ```'
        for role in autorole_names:
            msg += f'• {role}\n'
        msg += '```'

        await ctx.send(msg)

    @commands.command()
    @manage_guild()
    async def goodbye(self, ctx, *, goodbye_message: str):
        """Sets the goodbye message for user leaves.

        To use the username of the user who left in your goodbye message, use
        %name%."""

        if ctx.message.guild.id not in self.bot.goodbyes:
            self.bot.goodbyes[ctx.message.guild.id] = [None, None]

        self.bot.goodbyes[ctx.message.guild.id][1] = goodbye_message
        yaml.dump(self.bot.welcomes, open('data/goodbyes.yml', 'w'))

        await ctx.send(':white_check_mark: Set the goodbye message for this guild.')

    @commands.command(aliases=['goodbyechnl'])
    @manage_guild()
    async def goodbyechannel(self, ctx, *, channel_mention: str):
        """Sets the goodbye channel for user leave messages.

        You must mention the channel."""
        if ctx.message.guild.id not in self.bot.goodbyes:
            await ctx.send(':warning: You need to set a goodbye message before setting the ' +
                           'goodbye channel.')
            return
        if len(ctx.message.channel_mentions) == 0:
            await ctx.send(':warning: You have not provided a channel mention for your goodbye channel.')
            return
        self.bot.goodbyes[ctx.message.guild.id][0] = ctx.message.channel_mentions[0].id
        yaml.dump(self.bot.welcomes, open('data/goodbyes.yml', 'w'))

        await ctx.send(':white_check_mark: Set your goodbye channel to `{}`.'
                       .format(ctx.message.channel_mentions[0]))

    @commands.command()
    @manage_roles()
    async def selfrole(self, ctx, action: str, *, role_name: str):
        """Creates/removes selfroles (self-assignable roles).

        To create a selfrole, do `,selfrole add <role_name>`.
        To remove a selfrole, do `,selfrole remove <role_name>`"""
        if action.lower() == 'add':
            role = None
            for r in ctx.message.guild.roles:
                if r.name.lower() == role_name.lower():
                    role = r
                    break
            else:
                await ctx.send(f':warning: Role `{role_name}` was not found.')
                return

            if ctx.message.guild.id in self.bot.selfroles:
                self.bot.selfroles[ctx.message.guild.id].append(role.id)
            else:
                self.bot.selfroles[ctx.message.guild.id] = [role.id]

            yaml.dump(self.bot.selfroles, open('data/selfroles.yml', 'w'))
            await ctx.send(f':white_check_mark: I have added `{role_name}` to selfroles!')

        elif action.lower() == 'remove':
            role = None
            for r in ctx.message.guild.roles:
                if r.name.lower() == role_name.lower():
                    role = r
                    break
            else:
                await ctx.send(f':warning: Role `{role_name}` was not found.')
                return

            if ctx.message.guild.id not in self.bot.selfroles:
                await ctx.send(f':warning: Your guild does not have any selfroles. ' +
                               'Thus, I cannot remove a role from the nonexistent selfroles list.')
                return

            self.bot.selfroles[ctx.message.guild.id].remove(role.id)
            yaml.dump(self.bot.selfroles, open('data/autoroles.yml', 'w'))

            await ctx.send(f':white_check_mark: Role `{role_name}` was removed from the selfroles!')

        else:
            await ctx.send(f':warning: That\'s not a valid argument.')

    @commands.command()
    async def selfroles(self, ctx):
        """Lists all the selfroles for a guild."""
        if ctx.message.guild.id not in self.bot.selfroles:
            await ctx.send('This guild does not have any selfroles.')
            return

        selfrole_ids = self.bot.selfroles[ctx.message.guild.id]
        selfrole_names = []

        for r_id in selfrole_ids:
            for r in ctx.message.guild.roles:
                if r_id == r.id:
                    selfrole_names.append(r.name)
                    break
            else:
                self.bot.selfroles[ctx.message.guild.id].remove(r_id)
                yaml.dump(self.bot.selfroles, open('data/selfroles.yml', 'w'))

        if len(selfrole_names) == 0:
            await ctx.send('This guild does not have any selfroles.')
            return

        msg = 'This server\'s selfroles are: ```'
        for role in selfrole_names:
            msg += f'• {role}\n'
        msg += '```'

        await ctx.send(msg)

    @commands.command()
    async def getrole(self, ctx, *, role_name: str):
        """Gets a selfrole."""
        role = None
        for r in ctx.message.guild.roles:
            if r.name.lower() == role_name.lower():
                role = r
                break
        else:
            await ctx.send(f':warning: Role `{role_name}` was not found.')
            return

        if role in ctx.message.author.roles:
            await ctx.send(':warning: You already have that role.')
            return

        if ctx.message.guild.id not in self.bot.selfroles:
            await ctx.send(':warning: That role isn\'t a selfrole -- in fact, this guild ' +
                           'doesn\'t even have any selfroles.')
            return

        if role.id not in self.bot.selfroles[ctx.message.guild.id]:
            await ctx.send(':warning: That role isn\'t a selfrole.')
            return

        await ctx.message.author.add_roles(role)
        await ctx.send(f':white_check_mark: **{ctx.message.author.name}**, you now have `{role.name}` role.')

    @commands.command(aliases=['loserole'])
    async def droprole(self, ctx, *, role_name: str):
        """Removes a selfrole."""
        role = None
        for r in ctx.message.guild.roles:
            if r.name.lower() == role_name.lower():
                role = r
                break
        else:
            await ctx.send(f':warning: Role `{role_name}` was not found.')
            return

        if role not in ctx.message.author.roles:
            await ctx.send(':warning: You do not have that role.')
            return

        if ctx.message.guild.id not in self.bot.selfroles:
            await ctx.send(':warning: That role isn\'t a selfrole -- in fact, this guild ' +
                           'doesn\'t even have any selfroles.')
            return

        if role.id not in self.bot.selfroles[ctx.message.guild.id]:
            await ctx.send(':warning: That role isn\'t a selfrole.')
            return

        await ctx.message.author.remove_roles(role)
        await ctx.send(f':white_check_mark: **{ctx.message.author.name}**, you no longer have `{role.name}` role.')

    @commands.command()
    @manage_guild()
    async def prefix(self, ctx, *, new_prefix: str):
        """Sets the prefix for the guild."""
        self.bot.prefixes[ctx.message.guild.id] = new_prefix
        yaml.dump(self.bot.prefixes, open('data/prefixes.yml', 'w'))

        await ctx.send(f':white_check_mark: Changed this guild\'s prefix to `{new_prefix}`')

    @commands.command()
    async def purge(self, ctx, *, number: int):
        """Purges a number of messages.
        
        Number must be between 1 & 100."""
        if number < 1 or number > 100:
            await ctx.send(':warning: I can only purge between 1 and 100 messages!') 
            return
        
        async for message in ctx.message.channel.history(limit=number):
            await message.delete()
            await asyncio.sleep(0.2)

        notif_msg = await ctx.send(f':white_check_mark: I\'ve purged {number} messages for you!')
        await asyncio.sleep(7.0)
        await notif_msg.delete()

def setup(bot):
    bot.add_cog(Mod(bot))
