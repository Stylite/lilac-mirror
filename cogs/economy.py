#!/usr/bin/env python
import random
import yaml
import time
from cogs.util.checks import manage_guild

from discord.ext import commands
import discord


class Economy:
    """Economy commands"""
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

    @commands.command()
    @manage_guild()
    async def startpool(self, ctx):
        """Starts a pool of <:lilac:419730009234866176> for a guild.
        
        Once the pool is created, users should be notified that a pool
        has started, and be encouraged to donate to the pool, by doing
        `pool <some-amt>`. When the `poolout` command is executed, by an
        Admin, the pool's contents will be given to random member of the
        current guild."""
        self.bot.economy['pools'][ctx.message.guild.id] = 0
        self.update_file()

        await ctx.send(f':white_check_mark: I\'ve started a {self.lilac} pool! '+\
                        f'Members of this guild can put some {self.lilac} in the pool by doing '+\
                        f'`pool [some-amount]`. When you feel the pool has reached a high enough size, '+\
                        f'run `poolout` and all of the {self.lilac} in the pool will be given to a random '+\
                        f'member in this guild!')

    @commands.command()
    async def pool(self, ctx, *, amt: int):
        """Pools in <:lilac:419730009234866176> to the guild pool!
        
        After some time, a random member will be selected and the
        contents of the pool will go out to them."""
        user = ctx.message.author
        guild = ctx.message.guild
        if guild.id not in self.bot.economy['pools']:
            await ctx.send(':x: This guild is not currently hosting a pool event!')
            return
        if self.bot.economy['pools'][guild.id] is None:
            await ctx.send(':x: This guild is not currently hosting a pool event!')
            return
        
        if amt > self.bot.economy[user.id]['balance']:
            await ctx.send(f':warning: You don\'t have enough {self.lilac} to make that pool contribution!')
            return
        if amt < 0:
            await ctx.send(f':warning: You can\'t put a negative number of {self.lilac} into the pool!')
            return

        self.bot.economy[user.id]['balance'] -= amt
        self.bot.economy['pools'][guild.id] += amt
        self.update_file()

        await ctx.send(f':white_check_mark: I\'ve put {self.lilac}**{amt}** from your'+\
                        ' account into the pool!')
            
    @commands.command()
    @manage_guild()
    async def poolout(self, ctx):
        """Picks a random member and sends them the content of the pool!"""
        guild = ctx.message.guild
        if guild.id not in self.bot.economy['pools']:
            ctx.send(':x: This guild is not currently hosting a pool event!')
            return
        if self.bot.economy['pools'][guild.id] is None:
            ctx.send(':x: This guild is not currently hosting a pool event!')
            return

        winner = random.choice(guild.members)
        pool_total = self.bot.economy['pools'][guild.id]

        await ctx.send(f'{winner.mention} has won the pool! {self.lilac}**{pool_total}** goes to them!')

        if winner.id not in self.bot.economy:
            self.create_bank_account(winner)

        self.bot.economy[winner.id]['balance'] += pool_total
        self.bot.economy['pools'][guild.id] = None
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
            return 

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
