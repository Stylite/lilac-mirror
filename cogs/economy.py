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

    @commands.command()
    async def tribute(self, ctx, *, amount: int):
        """Tributes some amount of <:lilac:419730009234866176> to the gods.

        If the gods like your offering, they'll reward you with more money.
        If not, they'll take your money.

        And yes, you can be left with a negative amount of money."""
        user = ctx.message.author
        if user.id not in self.bot.economy:
            self.create_bank_account(user)
        if amount > self.bot.economy[user.id]['balance']:
            await ctx.send(':warning: You don\'t have enough money to make that tribute!')
            return
        if amount < 0:
            await ctx.send(f':warning: You can\'t tribute less than {self.lilac}**0**!')

        random.seed(str(amount) + str(time.time()))
        self.bot.economy[user.id]['balance'] -= amount 

        gods_like = random.randrange(0, 4)
        if gods_like != 0:
            take_away = random.randrange(0, 500)
            self.bot.economy[user.id]['balance'] -= take_away
            bal = self.bot.economy[user.id]['balance']

            await ctx.send(f':exclamation: The gods don\'t like your offering of {self.lilac}**{amount}**!\n' +\
                           f'They take away {self.lilac}**{take_away}** from you, leaving you with' +\
                           f' {self.lilac}**{bal}**!')
        else:
            give_to = random.randrange(0, 1000)
            self.bot.economy[user.id]['balance'] += give_to
            bal = self.bot.economy[user.id]['balance']

            await ctx.send(f':thumbsup: The gods love your offering of {amount}!\n' +\
                           f'They give you {self.lilac}**{give_to}**, leaving you with' +\
                           f' {self.lilac}**{bal}**!')

        self.update_file()


def setup(bot):
    bot.add_cog(Economy(bot))
