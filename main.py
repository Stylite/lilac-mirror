#!/usr/bin/env python
from discord.ext import commands
import yaml
import traceback
import discord

class Lilac(commands.Bot):
    def __init__(self):
        self.config =  {}
        self.welcomes, self.goodbyes = {}, {}
        self.autoroles, self.selfroles = {}, {}
        with open('config.yml', 'r') as config:
            self.config = yaml.load(config)
        with open('data/welcomes.yml', 'r') as welcomes:
            self.welcomes = yaml.load(welcomes)
        with open('data/goodbyes.yml', 'r') as goodbyes:
            self.goodbyes = yaml.load(goodbyes)
        with open('data/autoroles.yml', 'r') as autoroles:
            self.autoroles = yaml.load(autoroles)
        with open('data/selfroles.yml', 'r') as selfroles:
            self.selfroles = yaml.load(selfroles)

        super().__init__(
            command_prefix='l!',
            description='A bot made for moderation, fun, and verifying KnowYourMeme accounts with Discord.'
        )

    async def on_ready(self):
        """Function executes once bot is ready."""
        print('[INFO] Lilac is ready!')
        print('[INFO] Logged in as {}#{}'.format(self.user.name, self.user.discriminator))

    async def on_command_error(self, ctx, exception):
        """Function executes once bot encounters an error"""
        if isinstance(exception, commands.CommandInvokeError):
            exception = exception.original

        err = traceback.format_exception(type(exception), exception, \
                                            exception.__traceback__, chain=False)
        err = '\n'.join(err)

        await ctx.send(':warning: An error occured: ```{}```'.format(str(exception)))
        print('[ERR] Error:')
        print(err)

    async def on_member_join(self, member):
        """Function executes once a member joins a guild."""
        # handle welcome messages
        if member.guild.id in self.welcomes:
            welcome_config = self.welcomes[member.guild.id]

            welcome_channel = None
            if welcome_config[0] is not None:
                welcome_channel = member.guild.get_channel(welcome_config[0])
            else:
                return

            fmt_welcome_message = welcome_config[1].replace('%mention%', member.mention)
            await welcome_channel.send(fmt_welcome_message)
        # handle autoroles
        if member.guild.id in self.autoroles:
            autoroles = self.autoroles[member.guild.id]
            for role_id in autoroles:
                to_add = None
                for role in member.guild.roles:
                    if role.id == role_id:
                        to_add = role
                        print(to_add.name)
                        break

                if to_add:
                    await member.add_roles(to_add)

    async def on_member_remove(self, member):
        if member.guild.id in self.goodbyes:
            goodbye_config = self.goodbyes[member.guild.id]

            goodbye_channel = None
            if goodbye_config[0] is not None:
                goodbye_channel = member.guild.get_channel(goodbye_config[0])
            else:
                return

            fmt_goodbye_message = goodbye_config[1].replace('%name%', member.name)
            await goodbye_channel.send(fmt_goodbye_message)


    def run(self):
        """Run function for Lilac. Loads cogs and runs the bot."""
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

    