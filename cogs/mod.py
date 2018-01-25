#!/usr/bin/env python
from discord.ext import commands
import discord
import yaml
from cogs.util.checks import manage_usrs, manage_guild

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
        await ctx.send(':white_check_mark: Successfully banned user {}#{}'\
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

        await ctx.message.kick(to_kick)
        await ctx.send(':white_check_mark: Successfully kicked user {}#{}'\
                            .format(to_kick.name, to_kick.discriminator))

    @commands.command()
    @manage_guild()
    async def setwelcome(self, ctx, *, welcome_message: str):
        """Sets the welcome message for user joins.
        
        To mention the user joined in your welcome message, use
        %user%."""
        self.bot.welcomes[ctx.message.guild.id] = [None, welcome_message]
        yaml.dump(self.bot.welcomes, open('data/welcomes.yml', 'w'))

        await ctx.send(':white_check_mark: Set the welcome message for this guild. Please set' +\
                ' the welcome message channel next, using the `setwelcomechannel` command.')

    @commands.command(aliases=['welcomechannel', 'welcomechnl'])
    @manage_guild()
    async def setwelcomechannel(self, ctx, *, channel_mention: str):
        """Sets the welcome channel for user join messages.
        
        You must mention the channel."""
        if len(ctx.message.channel_mentions) == 0:
            await ctx.send(':warning: You have not provided a channel mention for your welcome channel.')
            return
        self.bot.welcomes[ctx.message.guild.id][0] = ctx.message.channel_mentions[0]
        yaml.dump(self.bot.welcomes, open('data/welcomes.yml', 'w'))

        await ctx.send(':white_check_mark: Set your welcome channel to {}'\
                    .format(self.bot.welcomes[ctx.message.guild.id][0].name))


def setup(bot):
    bot.add_cog(Mod(bot))