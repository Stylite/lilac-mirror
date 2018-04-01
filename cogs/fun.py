#!/usr/bin/env python
import random
import asyncio

from cogs.util.image import retrieve, resize
from PIL import Image

from discord.ext import commands
import discord

class Fun:
    """Fun commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def disability(self, ctx, *, image_url: str):
        """Command that gives an image a disability.
        
        Note: This command is not meant to be offensive."""
        async with ctx.message.channel.typing():
            image = await retrieve(image_url)
            resized = resize(image, (230, 160))

            template = Image.open('templates/disability.png')
            template.paste(image, (int(255-(resized.size[0]/2)), int((450-resized.size[1]/2))), image)

            final_image = Image.open('templates/disability_white.png')
            final_image.paste(template, (0, 0), template)

            final_image.save('img/disability.png')

            await ctx.send(file=discord.File('img/disability.png'))
        
        
    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: str):
        """Spins a Magic 8 Ball!
        
        Please don't use this command to actually decide real
        decisions."""
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
        
        await self.bot.send(ctx, 'The Magic 8 Ball is spinning...')
        await asyncio.sleep(1)
        await self.bot.send(ctx, ':8ball: **The Magic 8 Ball says:** ```{}```'.format(choice))
        
def setup(bot):
    bot.add_cog(Fun(bot))