#!/usr/bin/env python
from weather import Weather, Unit
import googletrans

from discord.ext import commands
import discord

class Utility:
    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()
        self.weather_obj = Weather(unit=Unit.CELSIUS)

    @commands.command()
    async def weather(self, ctx, *, location: str):
        location = self.weather_obj.lookup_by_location(location)
        if location is None:
            await ctx.send(':x: I couldn\'t find any results for that location!')
            return

        wind_dir = ['north', 'east', 'south', 'west', 'north'][round(float(location.wind()["direction"])/90)]
        
        to_send = f'__**Weather in `{location.location().city()}, {location.location().country()}`**:__\n'+\
                  f':white_small_square: | **Condition:** {location.condition().text()}\n'+\
                  f':thermometer: | **Temperature:** {location.condition().temp()}°C\n'+\
                  f':droplet: | **Humidity:** {location.atmosphere()["humidity"]}%\n'+\
                  f':dash: | **Wind:** Blowing {wind_dir}; {round(0.277 * float(location.wind()["speed"]), 1)} m/s'

        await ctx.send(to_send)

    @commands.command()
    async def translate(self, ctx, translate_to: str, *, to_translate: str):
        """Translates something from one language to another.
        
        The `translate_to` parameter must be a language. The available languages
        are located at https://pastebin.com/8BMHExpj."""
        translated = None
        try:
            translated = self.translator.translate(to_translate, dest=translate_to)
        except ValueError as e:
            await ctx.send(':warning: That\'s not a valid language you can translate to.')
            return
        except:
            await ctx.send(':warning: An error occured while attempting to contact Google Translate!')
            return
        
        to_send = discord.Embed(title='Translator Result', colour=0xbd8cbf)
        to_send.add_field(name=f'Input [{translated.src}]', value=f'```{to_translate}```', inline=False)
        to_send.add_field(name=f'Output [{translated.dest}]', value=f'```{translated.text}```', inline=False)

        await ctx.send(embed=to_send)

def setup(bot):
    bot.add_cog(Utility(bot))
