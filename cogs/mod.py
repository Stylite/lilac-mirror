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
        await ctx.send(':white_check_mark: Successfully banned user {}#{}'
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
        await ctx.send(':white_check_mark: Successfully kicked user {}#{}'
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
    async def autorole(self, ctx, action: str, role_name: str):
        """Creates/removes autoroles.
        
        To create an autorole, do `l!autorole add <role-name>`.
        To remove an autorole, do `l!autorole remove <role-name>`"""

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
                    self.bot.autoroles.remove(to_remove.id)
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

def setup(bot):
    bot.add_cog(Mod(bot))
