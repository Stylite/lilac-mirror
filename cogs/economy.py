#!/usr/bin/env python
import random
import time
from cogs.util.checks import manage_guild

from discord.ext import commands
import discord


class Economy:
    """Economy commands"""
    def __init__(self, bot):
        self.bot = bot
        self.lilac = '<:lilac:419730009234866176>'

        dbcur = self.bot.database.cursor()
        dbcur.execute('''
                CREATE TABLE IF NOT EXISTS 
                economy(id INTEGER, balance INTEGER, daily REAL)''')
        dbcur.execute('''
                CREATE TABLE IF NOT EXISTS
                pools(guild_id INTEGER, pool INTEGER)''')
        dbcur.close()
        self.bot.database.commit()
        
    def create_bank_account(self, member):
        """Creates a Lilac bank account."""
        dbcur = self.bot.database.cursor()
        dbcur.execute(
            '''INSERT INTO economy(id,balance,daily) VALUES (?,?,?)''',
            (member.id, 0, 0.0))
        dbcur.close()
        self.bot.database.commit()

    def check_bank_account(self, member):
        """Checks if user has a bank account."""
        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM economy WHERE id={member.id}')
        if len(dbcur.fetchall()) == 0:
            self.create_bank_account(member)
        dbcur.close()

    @commands.command()
    @manage_guild()
    async def startpool(self, ctx):
        """Starts a pool of <:lilac:419730009234866176> for a guild. Need ManageGuild perms to run cmd.

        Once the pool is created, users should be notified that a pool
        has started, and be encouraged to donate to the pool, by doing
        `pool <some-amt>`. When the `poolout` command is executed, by an
        Admin, the pool's contents will be given to random member of the
        current guild."""
        dbcur = self.bot.database.cursor()
        dbcur.execute('INSERT INTO pools(guild_id,pool) VALUES (?,?)',(ctx.message.guild.id, 0))
        self.bot.database.commit()
        dbcur.close()

        await ctx.send(f':white_check_mark: I\'ve started a {self.lilac} pool! '+\
                        f'Members of this guild can put some {self.lilac} in the pool by doing '+\
                        f'`pool [some-amount]`. When you feel the pool has reached a high enough size, '+\
                        f'run `poolout` and all of the {self.lilac} in the pool will be given to a random '+\
                        f'member in this guild!')

    @commands.command()
    async def pool(self, ctx, *args):
        """Pools in <:lilac:419730009234866176> to the guild pool!
        
        To check how many<:lilac:419730009234866176> are currently in the pool,
        do `pool check` """
        user = ctx.message.author
        guild = ctx.message.guild

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM pools WHERE guild_id={guild.id}')
        if len(dbcur.fetchall()) == 0:
            await ctx.send(':x: This guild is not currently hosting a pool event!')
            dbcur.close()
            return

        if args[0] == 'check':
            dbcur.execute(f'SELECT * FROM pools WHERE guild_id={guild.id}')
            in_pool = dbcur.fetchall()[0][1]
            await ctx.send(f'This guild currently has {self.lilac}**{in_pool}** in its pool.')
            dbcur.close()
        else:
            amt = None
            try:
                amt = int(args[0])
            except ValueError:
                raise commands.errors.BadArgument()

            dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
            user_bal = dbcur.fetchall()[0][1]
            if amt > user_bal:
                await ctx.send(f':warning: You don\'t have enough {self.lilac} to make that pool contribution!')
                return
            if amt < 0:
                await ctx.send(f':warning: You can\'t put a negative number of {self.lilac} into the pool!')
                return

            dbcur.execute(f'UPDATE economy SET balance=balance-{amt} WHERE id={user.id}')
            dbcur.execute(f'UPDATE pools SET pool=pool+{amt} WHERE id={guild.id}')

            dbcur.close()
            self.bot.database.commit()

            await ctx.send(f':white_check_mark: I\'ve put {self.lilac}**{amt}** from your'+\
                            ' account into the pool!')
            
    @commands.command()
    @manage_guild()
    async def poolout(self, ctx):
        """Picks a random member and sends them the content of the pool! Need ManageGuild perm to run cmd."""
        guild = ctx.message.guild

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM pools WHERE guild_id={guild.id}')
        if len(dbcur.fetchall()) == 0:
            await ctx.send(':x: This guild is not currently hosting a pool event!')
            dbcur.close()
            return

        dbcur.execute(f'SELECT * FROM pools WHERE guild_id={guild.id}')
        winner = random.choice([m for m in guild.members if not m.bot])
        pool_total = dbcur.fetchall()[0][1]

        await ctx.send(f'**{str(winner)}** has won the pool! {self.lilac}**{pool_total}** goes to them!')

        self.check_bank_account(winner)

        dbcur.execute(f'UPDATE economy SET balance=balance+{pool_total} WHERE id={winner.id}')
        dbcur.execute(f'DELETE FROM pools WHERE guild_id={guild.id}')
        self.bot.database.commit()
        dbcur.close()

    @commands.command(aliases=['bal'])
    async def balance(self, ctx):
        """Gets your balance in <:lilac:419730009234866176>."""
        user = ctx.message.author
        self.check_bank_account(user)

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
        bal = dbcur.fetchall()[0][1]
        dbcur.close()

        await ctx.send(f'**{user.name}**, your balance is {self.lilac}**{bal}**.')

    @commands.command()
    async def daily(self, ctx):
        """Gives you your daily <:lilac:419730009234866176>.

        Refreshes every 20 hours. """
        user = ctx.message.author
        self.check_bank_account(user)

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
        daily_last_collected = dbcur.fetchall()[0][2]
        if time.time() - daily_last_collected >= 72000:
            daily_amt = random.randrange(50, 75)
            dbcur.execute(f'UPDATE economy SET balance=balance+{daily_amt} WHERE id={user.id}')
            dbcur.execute(f'UPDATE economy SET daily={time.time()} WHERE id={user.id}')

            await ctx.send(f':white_check_mark: **{user.name}**, you collected your' +
                           f' daily of {self.lilac}**{daily_amt}**!')
        else:
            remain = 72000 - (time.time() - daily_last_collected)
            remaining = [
                int((remain - remain % 3600)/3600),
                int((remain - (int((remain - remain % 3600)/3600)*3600))//60)
            ]

            await ctx.send(f':clock1030: You must wait another **{remaining[0]}** hours' +
                           f' and **{remaining[1]}** minutes before collecting your next daily.')

        self.bot.database.commit()
        dbcur.close()


    @commands.command()
    async def tribute(self, ctx, *, amount: int):
        """Tributes some amount of <:lilac:419730009234866176> to the gods.

        If the gods like your offering, they'll reward you with more money.
        If not, they'll take your money.

        Yes, you can be left with a negative amount of money, but it's capped
        at -5."""
        user = ctx.message.author
        self.check_bank_account(user)

        dbcur = self.bot.database.cursor()

        dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
        current_bal = dbcur.fetchall()[0][1]
        if amount > current_bal:
            await ctx.send(f':warning: You don\'t have enough {self.lilac} to make that tribute!')
            return
        if amount < 0:
            await ctx.send(f':warning: You can\'t tribute less than {self.lilac}**0**!')
            return 

        random.seed(str(amount) + str(time.time()))
        dbcur.execute(f'UPDATE economy SET balance=balance-{amount} WHERE id={user.id}')

        gods_like = random.randrange(0, 4)
        if gods_like != 0:
            take_away = random.randrange(0, 500)
            dbcur.execute(f'UPDATE economy SET balance=balance-{take_away} WHERE id={user.id}')

            dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
            if dbcur.fetchall()[0][1] < -5:
                dbcur.execute(f'UPDATE economy SET balance=-5 WHERE id={user.id}')

            dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
            bal = dbcur.fetchall()[0][1]
            await ctx.send(f':exclamation: The gods don\'t like your offering of {self.lilac}**{amount}**!\n' +\
                           f'They take away {self.lilac}**{take_away}** from you, leaving you with' +\
                           f' {self.lilac}**{bal}**!')
        else:
            give_to = random.randrange(0, 1000)
            dbcur.execute(f'UPDATE economy SET balance=balance+{give_to} WHERE id={user.id}')
            dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
            bal = dbcur.fetchall()[0][1]

            await ctx.send(f':thumbsup: The gods love your offering of {self.lilac}**{amount}**!\n' +\
                           f'They give you {self.lilac}**{give_to}**, leaving you with' +\
                           f' {self.lilac}**{bal}**!')

        self.bot.database.commit()
        dbcur.close()

    @commands.command()
    async def give(self, ctx, amt: int, user_mention: str):
        """Gives another user some amount of money.
        
        You must mention the user."""
        user = ctx.message.author
        self.check_bank_account(user)

        give_to = None
        if len(ctx.message.mentions) == 0:
            await ctx.send(f':warning: You must mention a user to give {self.lilac} to!')
            return
        else:
            give_to = ctx.message.mentions[0]

        dbcur = self.bot.database.cursor()

        dbcur.execute(f'SELECT * FROM economy WHERE id={user.id}')
        user_bal = dbcur.fetchall()[0][1]
        if user_bal < amt:
            await ctx.send(f':warning: You don\'t have enough {self.lilac} to make that transaction!')
            return

        self.check_bank_account(give_to)

        dbcur.execute(f'UPDATE economy SET balance=balance-{amt} WHERE id={user.id}')
        dbcur.execute(f'UPDATE economy SET balance=balance+{amt} WHERE id={give_to.id}')

        self.bot.database.commit()
        dbcur.close()

        await ctx.send(f':white_check_mark: I\'ve transferred {self.lilac}**{amt}**'+\
                        f' from your account into **{give_to.name}**\'s account!')

        

def setup(bot):
    bot.add_cog(Economy(bot))
