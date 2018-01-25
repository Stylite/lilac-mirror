#!/usr/bin/env python
from discord.ext import commands
import yaml
import traceback
import discord

class Lilac(commands.Bot):
    def __init__(self):
        self.config, self.welcomes = {}, {}
        with open('config.yml', 'r') as config:
            self.config = yaml.load(config)
        with open('data/welcomes.yml') as welcomes:
            self.welcomes = yaml.load(welcomes)

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

    async def on_member_join(self, member):
        if member.guild.id in self.welcomes:
            welcome_config = self.welcomes[member.guild.id]

            welcome_channel = None
            if welcome_config[0] is not None:
                welcome_channel = member.guild.get_channel(welcome_config[0])
            else:
                return

            fmt_welcome_message = welcome_config[1].replace('%mention%', member.mention)
            await welcome_channel.send(fmt_welcome_message)


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

    