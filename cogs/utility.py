#!/usr/bin/env python
import requests

from weather import Weather, Unit
from PIL import Image, ImageFilter
import googletrans

from discord.ext import commands
import discord

class Utility:
    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()
        self.weather_obj = Weather(unit=Unit.CELSIUS)

    @commands.command()
    async def blur(self, ctx, *, image_url: str):
        """Blurs an image.
        
        Image URL must be a valid url the bot can get an image from."""
        image = None
        try:
            image = Image.open(requests.get(image_url, stream=True).raw)
        except OSError:
            await self.bot.send(ctx, ":warning: I couldn't find an image at that URL!")
            return

        blurred_image = image.filter(ImageFilter.BLUR)
        blurred_image.save('img/blur.png')

        await ctx.send(file=discord.File('img/blur.png'))

    @commands.command()
    async def emote(self, ctx, *, emote: str):
        """Gets information on a custom emote."""
        emote_id = None
        try:
            emote_id = int(emote.split(':')[2][0:-1])
        except IndexError:
            await self.bot.send(ctx, ':warning: That\'s not a custom emote!')
            return

        emote_obj = self.bot.get_emoji(emote_id)
        if emote_obj is None:
            await self.bot.send(ctx, ':warning: I couldn\'t get any information on that emote!')
            return

        to_send = discord.Embed(title=f'Info on emote {str(emote_obj)}', colour=0xbd8cbf)
        to_send.set_thumbnail(url=emote_obj.url)
        to_send.add_field(name='Emote Name', value=emote_obj.name, inline=True)
        to_send.add_field(name='ID', value=emote_obj.id, inline=True)
        to_send.add_field(name='From Guild', value=emote_obj.guild.name, inline=True)
        to_send.add_field(name='Created At', value=str(emote_obj.created_at).split('.')[0], inline=True)

        await self.bot.send(ctx, embed=to_send)

    @commands.command()
    async def weather(self, ctx, *, location: str):
        location = self.weather_obj.lookup_by_location(location)
        if location is None:
            await self.bot.send(ctx, ':x: I couldn\'t find any results for that location!')
            return

        wind_dir = ['north', 'east', 'south', 'west', 'north'][round(float(location.wind()["direction"])/90)]
        
        to_send = f'__**Weather in `{location.location().city()}, {location.location().country()}`**:__\n'+\
                  f':white_small_square: | **Condition:** {location.condition().text()}\n'+\
                  f':thermometer: | **Temperature:** {location.condition().temp()}°C\n'+\
                  f':droplet: | **Humidity:** {location.atmosphere()["humidity"]}%\n'+\
                  f':dash: | **Wind:** Blowing {wind_dir}; {round(0.277 * float(location.wind()["speed"]), 1)} m/s'

        await self.bot.send(ctx, to_send)

    @commands.command()
    async def translate(self, ctx, translate_to: str, *, to_translate: str):
        """Translates something from one language to another.
        
        The `translate_to` parameter must be a language. The available languages
        are located at https://pastebin.com/8BMHExpj."""
        translated = None
        try:
            translated = self.translator.translate(to_translate, dest=translate_to)
        except ValueError as e:
            await self.bot.send(ctx, ':warning: That\'s not a valid language you can translate to.')
            return
        except:
            await self.bot.send(ctx, ':warning: An error occured while attempting to contact Google Translate!')
            return
        
        to_send = discord.Embed(title='Translator Result', colour=0xbd8cbf)
        to_send.add_field(name=f'Input [{translated.src}]', value=f'```{to_translate}```', inline=False)
        to_send.add_field(name=f'Output [{translated.dest}]', value=f'```{translated.text}```', inline=False)

        await self.bot.send(ctx, embed=to_send)

def setup(bot):
    bot.add_cog(Utility(bot))
