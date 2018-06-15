#!/usr/bin/env python
import os
import numpy as np

from weather import Weather, Unit
from PIL import Image, ImageFilter
import matplotlib.pyplot as plot
from matplotlib.gridspec import GridSpec
import googletrans
import aiohttp

from cogs.util.image import retrieve, resize

from discord.ext import commands
import discord

class Utility:
    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()
        self.weather_obj = Weather(unit=Unit.CELSIUS)

    @commands.command()
    async def song(self, ctx, *, song_name: str):
        """Gets info about a song."""
        search_term = '%20'.join(song_name.split())
        request_url = f'https://api.genius.com/search?q={search_term}'

        auth_token = self.bot.config['genius_token']
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }

        res = None
        json_resp = None
        try:
            async with ctx.message.channel.typing():
                async with aiohttp.ClientSession() as session:
                    res = await session.get(request_url, headers=headers)
                    search_json_resp = await res.json()
        except Exception as e:
            print(e)
            await self.bot.send(ctx, (':warning: An error occured while'
                        ' attempting to contact the Genius Lyrics API!'))
            return

        if not 200 <= res.status < 300:
            await self.bot.send(ctx, (':warning: An error occured while attempting'
                                     ' to contact the Genius Lyrics API!'))
            return

        if len(search_json_resp['response']['hits']) == 0:
            await self.bot.send(ctx, (':warning: I couldn\'t find any results for that song!'))
            return

        try:
            async with ctx.message.channel.typing():
                async with aiohttp.ClientSession() as session:
                    song_endpoint = 'https://api.genius.com'+\
                                f'{search_json_resp["response"]["hits"][0]["result"]["api_path"]}'
                    print(song_endpoint)
                    res = await session.get(song_endpoint, \
                                             headers=headers)
                    json_resp = await res.json()
        except Exception as e:
            print(str(e))
            await self.bot.send(ctx, (':warning: An error occured while'
                        ' attempting to contact the Genius Lyrics API!'))
            return

        if res.status == 404:
            await self.bot.send(ctx, ':warning: I couldn\'t find any results for that song!')
            return

        print(json_resp)
        song_json = json_resp['response']['song']

        song_info = {
            'title': song_json['title'],
            'artist': song_json['primary_artist']['name'],
            'songwriters': ', '.join(writer['name'] for writer in song_json['writer_artists']),
            'release_date': song_json['release_date'],
            'song_url': song_json['url'],
            'image': song_json['song_art_image_thumbnail_url'],
        }

        for s_info in song_info:
            if not song_info[s_info] or len(song_info[s_info]) == 0:
                song_info[s_info] = 'Not found'

        to_send = discord.Embed(title=song_info['title'], colour=0x0f9fff)
        to_send.set_thumbnail(url=song_info['image'])
        to_send.add_field(name='Artist', value=song_info['artist'])
        to_send.add_field(name='Songwriters', value=song_info['songwriters'], inline=False)
        to_send.add_field(name='Release Date', value=song_info['release_date'])
        to_send.add_field(name='Lyrics', value=f'[Click here for song lyrics]({song_info["song_url"]})')

        await self.bot.send(ctx, embed=to_send)    

    @commands.command()
    @commands.cooldown(1, 30.0, commands.BucketType.guild)
    async def blur(self, ctx, *, image_url: str):
        """Blurs an image.
        
        Image URL must be a valid url the bot can get an image from."""
        image = await retrieve(image_url)

        blurred_image = image.filter(ImageFilter.BLUR)
        blurred_image.save('img/blur.png')

        await ctx.send(file=discord.File('img/blur.png'))

    @commands.command()
    @commands.cooldown(1, 30.0, commands.BucketType.guild)
    async def sharpen(self, ctx, *, image_url: str):
        """Sharpens an image.
        
        Image URL must be a valid url the bot can get an image from."""
        image = await retrieve(image_url)

        sharpened_image = image.filter(ImageFilter.SHARPEN)
        sharpened_image.save('img/sharpen.png')

        await ctx.send(file=discord.File('img/sharpen.png'))

    @commands.command()
    @commands.cooldown(1, 15.0, commands.BucketType.guild)
    async def pieplot(self, ctx, title, *, data):
        """Makes a nice pieplot with labels and values and a title.
        
        Put the title before the data. Title must not contain spaces.

        **In the data:**
        Seperate the labels and values with `:`, and seperate the different 
        labels and values with `|`. Values must be numbers.
        
        **Examples:**
        `pieplot Voting Trump:400|Clinton:400`
        `pieplot Pets Dogs:1000|Cats:1220|Birds:400`"""
        labels = [v.split(':')[0] for v in data.split('|')]
        try:
            values = [float(v.split(':')[1]) for v in data.split('|')]
        except ValueError:
            await self.bot.send(ctx, f'{self.bot.emotes.xmark}'+\
                                ' All of the values provided must be numbers.')
            return

        grid = GridSpec(1, 1)
        plot.subplot(grid[0,0], aspect=1)
        plot.title(title)
        plot.pie(values, labels=labels, radius=1)
        plot.savefig('img/pieplot.png')

        await ctx.send(file=discord.File('img/pieplot.png'))

    @commands.command()
    @commands.cooldown(1, 15.0, commands.BucketType.guild)
    async def bargraph(self, ctx, title: str, ylabel: str, *, data: str):
        """Makes a bargraph.
        
        Put the title and yaxis label before the data. Title must not contain spaces.

        **In the data:**
        Seperate the labels and values with `:`, and seperate the different 
        labels and values with `|`. Values must be numbers.
        
        **Example:**
        `bargraph ServerUptime Hours Server 1:50|Server 2:30`"""
        labels = [v.split(':')[0] for v in data.split('|')]
        try:
            values = [float(v.split(':')[1]) for v in data.split('|')]
        except ValueError:
            await self.bot.send(ctx, f'{self.bot.emotes.xmark}'+\
                                ' All of the values provided must be numbers.')
            return

        fig, ax = plot.subplots()
        ind = np.arange(1, len(values)+1)

        plot.bar(ind, values)
        ax.set_xticks(ind)
        ax.set_xticklabels(labels)
        ax.set_title(title)
        ax.set_ylim([0, max(values)+10])
        ax.set_ylabel(ylabel)

        plot.savefig('img/bargraph.png')

        await ctx.send(file=discord.File('img/bargraph.png'))


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
        """Gets the weather for a location."""
        location = self.weather_obj.lookup_by_location(location)
        if location is None:
            await self.bot.send(ctx, ':x: I couldn\'t find any results for that location!')
            return

        wind_dir = ['north', 'east', 'south', 'west', 'north'][round(float(location.wind.direction)/90)]
        
        to_send = f'__**Weather in `{location.location.city}, {location.location.country}`**:__\n'+\
                  f':white_small_square: | **Condition:** {location.condition.text}\n'+\
                  f':thermometer: | **Temperature:** {location.condition.temp}°C\n'+\
                  f':droplet: | **Humidity:** {location.atmosphere["humidity"]}%\n'+\
                  f':dash: | **Wind:** Blowing {wind_dir}; {round(0.277 * float(location.wind.speed), 1)} m/s'

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
