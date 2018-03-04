#!/usr/bin/env python
import random
import yaml
import time

from discord.ext import commands
import discord


class Economy:
    def __init__(self, bot):
        self.bot = bot
        self.lilac = '<:lilac:419730009234866176>'

    def update_file(self):
        yaml.dump(self.bot.economy, open('data/economy.yml', 'w'))

    def create_bank_account(self, member):
        """Creates a Lilac bank account."""
        self.bot.economy[member.id] = {
            'balance': 0,
            'daily': 0
        }
        self.update_file()

    @commands.command(aliases=['bal'])
    async def balance(self, ctx):
        """Gets your balance in <:lilac:419730009234866176>."""
        user = ctx.message.author
        if user.id not in self.bot.economy:
            self.create_bank_account(user)

        bal = self.bot.economy[user.id]['balance']
        await ctx.send(f'**{user.name}**, your balance is {self.lilac}**{bal}**.')

    @commands.command()
    async def daily(self, ctx):
        """Gives you your daily <:lilac:419730009234866176>.

        Refreshes every 20 hours. """
        user = ctx.message.author
        if user.id not in self.bot.economy:
            self.create_bank_account(user)

        if time.time() - self.bot.economy[user.id]['daily'] >= 72000:
            daily_amt = random.randrange(50, 75)
            self.bot.economy[user.id]['balance'] += daily_amt
            self.bot.economy[user.id]['daily'] = time.time()

            await ctx.send(f':white_check_mark: **{user.name}**, you collected your' +
                           f' daily of {self.lilac}**{daily_amt}**!')
        else:
            remain = 72000 - (time.time() - self.bot.economy[user.id]['daily'])
            remaining = [
                int((remain - remain % 3600)/3600),
                int((remain - (int((remain - remain % 3600)/3600)*3600))//60)
            ]

            await ctx.send(f':clock1030: You must wait another **{remaining[0]}** hours' +
                           f' and **{remaining[1]}** minutes before collecting your next daily.')

        self.update_file()


def setup(bot):
    bot.add_cog(Economy(bot))
