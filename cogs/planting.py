#!/usr/bin/env python
import emoji
import time
import random
import asyncio

from cogs.util.sender import confirm_message

from discord.ext import commands
import discord

class Planting:
    def __init__(self, bot):
        self.bot = bot
        self.lilac = '<:lilac:419730009234866176>'
        
        dbcur = self.bot.database.cursor()
        dbcur.execute('''
                CREATE TABLE IF NOT EXISTS 
                plants(id INTEGER, plant TEXT, name TEXT, last_watered INTEGER, health INTEGER)''')
        dbcur.close()

    def find_plant(self, ctx, plant_name):
        user = ctx.message.author

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM plants WHERE id={user.id} AND name="{plant_name}"')
        plants_found = dbcur.fetchall()

        if len(plants_found) == 0:
            return None

        return plants_found[0]

    @commands.command()
    async def plant(self, ctx, plant, *, plant_name):
        """Plants a plant.
        
        The <plant> arg must be a single Unicode emoji."""
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

        dbcur.execute(f'SELECT * FROM plants WHERE id={user.id}')
        if len(dbcur.fetchall()) == 5:
            await self.bot.send(ctx, ':no_entry: You may only have 5 plants at one time.')
            return

        dbcur.execute(f'SELECT balance FROM economy WHERE id={user.id}')
        
        plant_price = random.randrange(50, 200)
        eco_results = dbcur.fetchall()
        if len(eco_results) == 0  or eco_results[0][0] < plant_price:
            await self.bot.send(ctx, ':no_entry: You found a deal for that plant that costed'+\
                                f' {self.lilac}**{plant_price}**, but you didn\'t have enough {self.lilac}'+\
                                ' to afford it. Maybe try again later for a better deal...?')
            dbcur.close()
            return
        
        confirmed = await confirm_message(
            ctx, 
            f"Planting this plant will cost {self.lilac}**{plant_price}**. Do you wish to continue?",
            30.0
        )

        if not confirmed:
            await self.bot.send(ctx, 'Canceled plant purchase.')
            dbcur.close()
            return
        
        dbcur.execute(f'UPDATE economy SET balance=balance-{plant_price} WHERE id={user.id}')

        # zord is a very good person and i love him a lot
        # :)))))

        dbcur.execute('INSERT INTO plants(id, plant, name, last_watered, health) VALUES (?,?,?,?,?)',
                    (user.id, plant, plant_name, 0, 0))

        await self.bot.send(ctx, f":white_check_mark: I've planted a \\{plant}"+\
                            f' for you with name **{plant_name}**!')

        self.bot.database.commit()
        dbcur.close()

    @commands.command()
    async def plants(self, ctx):
        """Shows you a list of your plants."""
        user = ctx.message.author

        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM plants WHERE id={user.id}')
        user_plants = dbcur.fetchall()

        if len(user_plants) == 0:
            await self.bot.send(ctx, ":x: You currently don't have any plants!")
            return

        to_send = discord.Embed(title='__**Your Plants**__', colour=0xffbf00, \
                                description='Here\'s a list of all your current plants!')
        for plant in user_plants:
            to_send.add_field(
                name=f'__**{plant[2]}**__ | \\{plant[1]}',
                value=f'**Health:** {plant[4]}'
            )
        
        await self.bot.send(ctx, embed=to_send)

    @commands.command()
    async def water(self, ctx, *, plant_name: str):
        """Waters one of your plants.
        
        This will increase the health of your plant
        by 1."""
        user = ctx.message.author 

        plant_found = self.find_plant(ctx, plant_name)

        if not plant_found:
            await self.bot.send(ctx, ':warning: I couldn\'t find that plant!')
            return

        dbcur = self.bot.database.cursor()
        
        if int(time.time()) - plant_found[3] >= 72000:
            dbcur.execute(f'UPDATE plants SET health=health+1 WHERE id={user.id} AND name="{plant_name}"')
            dbcur.execute(f'''UPDATE plants SET last_watered={int(time.time())} 
                            WHERE id={user.id} AND name="{plant_name}"''')

            await self.bot.send(
                ctx, 
                f':ok_hand: I\'ve watered **{plant_found[2]}**(\\{plant_found[1]}) for you!'+\
                f' It now has **{plant_found[4]+1}** health!'
            )

        else:
            remain = 72000 - (time.time() - plant_found[3])
            remaining = [
                int((remain - remain % 3600)/3600),
                int((remain - (int((remain - remain % 3600)/3600)*3600))//60)
            ]

            await self.bot.send(ctx, f':clock1: You must wait another **{remaining[0]}** hours' +
                           f' and **{remaining[1]}** minutes before watering this plant again.')
        
        self.bot.database.commit()
        dbcur.close()

    @commands.command()
    async def harvest(self, ctx, *, plant_name):
        """Harvests one of your plants.
        
        Once you harvest your plant, it will be sold off
        for some amount of <:lilac:419730009234866176>. However,
        if your plant has 0 health, no one will buy it
        and you will not gain any money."""
        user = ctx.message.author
        dbcur = self.bot.database.cursor()

        found_plant = self.find_plant(ctx, plant_name)

        if not found_plant:
            await self.bot.send(ctx, ':warning: I couldn\'t find that plant!')
            return

        try:
            profit = found_plant[4]*10 + \
                    random.randrange(found_plant[4]*10, found_plant[4]*random.randrange(2, 5)*10)
        except ValueError:
            profit = 0
            
        dbcur.execute(f'UPDATE economy SET balance=balance+{profit} WHERE id={user.id}')
        dbcur.execute(f'DELETE FROM plants WHERE id={user.id} AND name="{found_plant[2]}"')

        if profit <= 0:
            await self.bot.send(ctx, ':cry: Sad. You harvested your'+\
                                f' **{found_plant[2]}**(\\{found_plant[1]}), but no one'+\
                                ' wanted to buy it...')
            
        else:
            sold_it_to = random.choice([
                'a random guy on the street',
                'the Gucci Gang',
                'the devs of Lilac',
                'your mom',
                'a farmer\'s market',
                'a bank teller',
                'Donald Trump',
                'Discord Bot List'
            ])
            await self.bot.send(ctx, ':large_orange_diamond: You harvested and sold your '+\
                                f'**{found_plant[2]}**(\\{found_plant[1]}) to {sold_it_to} for '+\
                                f'{self.lilac}**{profit}**!')

        self.bot.database.commit()
        dbcur.close()

    @commands.command()
    async def fertilize(self, ctx, *, plant_name: str):
        """Fertilizes a plant.
        
        Fertilizer will cost anywhere from 40-60<:lilac:419730009234866176>.
        Beware, as there is only a 1 in 5 change that fertilizer
        will increase the health of your plant. It can poison your
        plant and drop its health down."""
        user = ctx.message.author

        plant_found = self.find_plant(ctx, plant_name)

        if not plant_found:
            await self.bot.send(ctx, ':warning: I couldn\'t find that plant!')
            return

        dbcur = self.bot.database.cursor()
        fertilizer_price = random.randrange(40, 60)

        dbcur.execute(f'SELECT balance FROM economy WHERE id={user.id}')
        eco_results = dbcur.fetchall()
        if len(eco_results) == 0 or eco_results[0][0] < fertilizer_price:
            await self.bot.send(ctx, f':no_entry: You don\'t have enough {self.lilac}'+\
                                ' to purchase fertilizer!') 
            dbcur.close()
            return

        confirmed = await confirm_message(
            ctx, 
            f"Using fertilizer will cost {self.lilac}**{fertilizer_price}**. Do you wish to continue?",
            30.0
        )

        if not confirmed:
            await self.bot.send(ctx, 'Canceled fertilizer purchase.')
            dbcur.close()
            return
        
        dbcur.execute(f'UPDATE economy SET balance=balance-{fertilizer_price} WHERE id={user.id}')

        succeeds = random.randrange(0, 4)
        if succeeds == 0:
            fertilizer_worked = random.choice([
                'worked magic on',
                'did the good stuff to',
                'growth\'d',
                'fertilization\'d'
            ])
            health_increase = random.randrange(2, 6)
            dbcur.execute(f'''UPDATE plants SET health=health+{health_increase} 
                            WHERE id={user.id} AND name="{plant_found[2]}"''')

            await self.bot.send(
                ctx,
                f':smile: The plant fertilizer {fertilizer_worked} your '+\
                f'**{plant_found[2]}**(\\{plant_found[1]}), and its health shot up to'+\
                f' **{plant_found[4]+health_increase}**!'
            )
        else:
            fertilizer_did = random.choice([
                'killed',
                'broke\'d',
                'rotted',
                'lasered'
            ])
            try:
                health_decrease = random.randrange(1, plant_found[4])
            except ValueError:
                health_decrease = 1
            
            dbcur.execute(f'''UPDATE plants SET health=health-{health_decrease}
                            WHERE id={user.id} AND name="{plant_found[2]}"''')

            await self.bot.send(
                ctx,
                f':cry: The plant fertilizer {fertilizer_did} your '+\
                f'**{plant_found[2]}**(\\{plant_found[1]}), and its health dropped down to'+\
                f' **{plant_found[4]-health_decrease}**!'
            )

        self.bot.database.commit()
        dbcur.close()
        
        
def setup(bot):
    bot.add_cog(Planting(bot))
