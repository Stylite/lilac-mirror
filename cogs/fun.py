#!/usr/bin/env python
import random
import asyncio

from discord.ext import commands
import discord

class Fun:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: str):
        choices = [
            'It is certain',
            'It is decidedly so',
            'Without a doubt',
            'Yes definitely',
            'You may rely on it',
            'As I see it, yes',
            'Most likely',
            'Outlook good',
            'Yes',
            'Signs point to yes',
            'Reply hazy try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            'Don\'t count on it',
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful'
        ]
        
        random.seed(question)
        choice = random.choice(choices)
        
        await ctx.send('The Magic 8 Ball is spinning...')
        await asyncio.sleep(1)
        await ctx.send(':8ball: **The Magic 8 Ball says:** ```{}```'.format(choice))
        
def setup(bot):
    bot.add_cog(Fun(bot))