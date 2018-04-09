#!/usr/bin/env python
import emoji
import time
import asyncio

from discord.ext import commands
import discord

class Plants:
    def __init__(self, bot):
        self.bot = bot
        self.lilac = '<:lilac:419730009234866176>'
        
        dbcur = self.bot.database.cursor()
        dbcur.execute('''
                CREATE TABLE IF NOT EXISTS 
                plants(id INTEGER, plant TEXT, name TEXT, planted_at REAL)''')
        dbcur.close()

    @commands.command()
    async def plant(self, ctx, plant, *, plant_name):
        """Plants a plant."""
        user = ctx.message.author
        if len(plant) > 1:
            await self.bot.send(ctx, ':warning: You must choose a single emoji for your plant!')
            return
        
        if not plant in emoji.UNICODE_EMOJI:
            await self.bot.send(ctx, ':warning: You must choose a Unicode emoji as your plant!')
            return

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM plants WHERE id={user.id} AND name="{plant_name}"')
        
        if len(dbcur.fetchall()) > 0:
            await self.bot.send(ctx, ':no_entry: You already have a plant with that name!')
            dbcur.close()
            return

        dbcur.execute(f'SELECT balance FROM economy WHERE id={user.id}')
        
        eco_results = dbcur.fetchall()
        if len(eco_results) == 0  or eco_results[0][0] < 20:
            await self.bot.send(ctx, f':no_entry: You don\'t have enough {self.lilac}'+\
                                ' to purchase a plant to plant!') 
            return
        message = await self.bot.send(ctx, f"Planting a plant will cost {self.lilac}20."+\
                                        " Do you wish to continue? ")
        await message.add_reaction('✅')
        await message.add_reaction('❌')

        def check(reaction, reacted_user):
            return user == reacted_user

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await self.bot.send(ctx, 'Canceled plant purchase.')
            dbcur.close()
            return
        else:
            if reaction.emoji == '✅':
                pass
            else:
                await self.bot.send(ctx, 'Canceled plant purchase.')
                dbcur.close()
                return
        
        dbcur.execute(f'UPDATE economy SET balance=balance-20 WHERE id={user.id}')

        # zord is a very good person and i love him a lot
        # :)))))

        dbcur.execute('INSERT INTO plants(id, plant, name, planted_at) VALUES (?,?,?,?)',
                    (user.id, plant, plant_name, round(time.time())))

        await self.bot.send(ctx, f":white_check_mark: I've planted a {plant}"+\
                            f' for you with name **{plant_name}**!')

def setup(bot):
    bot.add_cog(Plants(bot))