#!/usr/bin/env python
import random
import yaml

from discord.ext import commands
import discord

class Economy:
    def __init__(self, bot):
        self.bot = bot
        self.lilac = None
        
        for guild in self.bot.guilds:
            if guild.name == 'Workshop':
                for emoji in guild.emojis:
                    if emoji.name == 'lilac':
                        self.lilac = str(emoji)


    def update_file(self):
        yaml.dump(self.bot.economy, open('data/economy.yml', 'w'))

    def create_bank_account(self, member):
        """Creates a Lilac bank account."""
        self.bot.economy[member.id] = {
            'balance': 0,
            'daily': 0
        }

    @commands.command(aliases=['bal'])
    async def balance(self, ctx):
        user = ctx.message.author
        if user.id not in self.bot.economy:
            self.create_bank_account(user)

        bal = self.bot.economy[user.id]['balance']
        await ctx.send(f'**{user.name}**, your balance is **{bal}**{self.lilac}.')


def setup(bot):
    bot.add_cog(Economy(bot))