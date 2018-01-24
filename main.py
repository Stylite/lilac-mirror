#!/usr/bin/env python
from discord.ext import commands
import yaml
import traceback
import discord

class Lilac(commands.Bot):
    def __init__(self):
        self.config = {}
        with open('config.yml', 'r') as config:
            self.config = yaml.load(config)

        super().__init__(
            command_prefix='l!',
            description='A bot made for Ethan J. Campbell\'s Lilac Discord server.'
        )

    async def on_ready(self):
        print('[INFO] Lilac is ready!')
        print('[INFO] Logged in as {}#{}'.format(self.user.name, self.user.discriminator))

    async def on_command_error(self, ctx, exception):
        err = traceback.format_exception(type(exception), exception, exception.__traceback__, chain=False)
        err = '\n'.join(err)

        await ctx.send(':warning: An error occured: ```{}```'.format(str(exception)))
        print('[ERR] Error:')
        print(err)

    def run(self):
        cogs = self.config['cogs']

        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                print('[LOAD] Failed to load cog ' + cog)
                print(e)
            else:
                print('[LOAD] Loaded cog {}'.format(cog))

        super().run(self.config['token'])

Bot = Lilac()
Bot.run()

    