#!/usr/bin/env python
from discord.ext import commands
import discord
import yaml
from cogs.util.checks import manage_usrs, manage_guild, manage_roles


class Mod:
    """Moderation Commands"""

    def __init__(self, bot):
        self.bot = bot

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
        await ctx.send(':white_check_mark: Successfully kicked user `{}#{}`'
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

        await ctx.send(':white_check_mark: Set your welcome channel to `{}`'
                       .format(ctx.message.channel_mentions[0]))

    @commands.command()
    @manage_roles()
    async def autorole(self, ctx, action: str, *, role_name: str):
        """Creates/removes autoroles.

        To create an autorole, do `,autorole add <role-name>`.
        To remove an autorole, do `,autorole remove <role-name>`"""

        if action.lower() == 'add':
            to_add = None
            for role in ctx.message.guild.roles:
                if role_name.lower() == role.name.lower():
                    to_add = role
                    break
            else:
                await ctx.send(f':warning: Role `{role_name}` not found.')
                return

            if ctx.message.guild.id in self.bot.autoroles:
                self.bot.autoroles[ctx.message.guild.id].append(to_add.id)
            else:
                self.bot.autoroles[ctx.message.guild.id] = [to_add.id]
            yaml.dump(self.bot.autoroles, open('data/autoroles.yml', 'w'))
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

            if ctx.message.guild.id in self.bot.autoroles:
                if to_remove.id in self.bot.autoroles[ctx.message.guild.id]:
                    self.bot.autoroles[ctx.message.guild.id].remove(
                        to_remove.id)
                else:
                    await ctx.send(':warning: That role is not an autorole.')
                    return
            else:
                await ctx.send(':warning: You currently do not have any autoroles.')
                return

            await ctx.send(f':white_check_mark: Removed role `{to_remove.name}` from autoroles.')
            yaml.dump(self.bot.autoroles, open('data/autoroles.yml', 'w'))

        else:
            await ctx.send(':warning: Invalid action. The valid actions are `add` and `remove`')

    @commands.command()
    @manage_roles()
    async def autoroles(self, ctx):
        """Lists current autoroles."""
        if ctx.message.guild.id not in self.bot.autoroles:
            await ctx.send(':x: You currently do not have any autoroles.')
            return

        autorole_id_list = self.bot.autoroles[ctx.message.guild.id]

        if len(autorole_id_list) == 0:
            await ctx.send(':x: You currently do not have any autoroles.')
            return

        autorole_list = []
        for role_id in autorole_id_list:
            role = None
            for r in ctx.message.guild.roles:
                if r.id == role_id:
                    role = r
                    break
            autorole_list.append(role.name)

        message = 'This guild\'s current autoroles are: ```'
        for autorole in autorole_list:
            message += f'• {autorole}\n'
        message += '```'

        await ctx.send(message)

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

        await ctx.send(':white_check_mark: Set your goodbye channel to `{}`'
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

        if len(selfrole_ids) == 0:
            await ctx.send('This guild does not have any selfroles.')
            return

        for r_id in selfrole_ids:
            for r in ctx.message.guild.roles:
                if r_id == r.id:
                    selfrole_names.append(r.name)

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


def setup(bot):
    bot.add_cog(Mod(bot))
