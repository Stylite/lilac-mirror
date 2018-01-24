#!/usr/bin/env python
from discord.ext import commands
import discord
from cogs.util.checks import manage_usrs

class Mod:
    """Moderation Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @manage_usrs()
    async def ban(self, ctx, *, mention: str):
        """Bans a user. 
        
        You must provide a mention for the bot to ban."""
        to_ban = None
        if ctx.message.mentions:
            to_ban = ctx.message.mentions[0]
        else:
            await self.bot.say(':warning: You did not mention a user to ban.')
            return

        await self.bot.send_message(to_ban, 'You have been banned on {}'.format(ctx.message.server.name))
        await self.bot.ban(to_ban)
        await self.bot.say(':white_check_mark: Successfully banned user {}#{}'\
                            .format(to_ban.name, to_ban.discriminator))

    @commands.command(pass_context=True)
    @manage_usrs()
    async def kick(self, ctx, *, mention: str):
        """Kicks a user. 
        
        You must provide a mention for the bot to kick."""
        to_kick = None
        if ctx.message.mentions:
            to_kick = ctx.message.mentions[0]
        else:
            await self.bot.say(':warning: You did not mention a user to kick.')
            return

        await self.bot.send_message(to_kick, 'You have been kicked from {}'.format(ctx.message.server.name))
        await self.bot.kick(to_kick)
        await self.bot.say(':white_check_mark: Successfully kicked user {}#{}'\
                            .format(to_kick.name, to_kick.discriminator))


def setup(bot):
    bot.add_cog(Mod(bot))