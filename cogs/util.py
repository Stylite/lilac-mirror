#!/usr/bin/env python
import googletrans

from discord.ext import commands
import discord

class Utility:
    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()

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
        to_send.add_field(name=f'Input [{translated.src}]', value=f'```{to_translate}```')
        to_send.add_field(name=f'Output [{translated.dest}]', value=f'```{translated.text}```')

        await ctx.send(embed=to_send)

def setup(bot):
    bot.add_cog(Utility(bot))
