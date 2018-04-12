#!/usr/bin/env python
import time
import os
import sys
import sqlite3 as sqlite
import traceback

import yaml

from cogs.util.logging import Logger
import cogs.util.sender as sender_module

from discord.ext import commands
import discord

"""Main source file for Lilac -- run this to start the bot."""

class Lilac(commands.AutoShardedBot):
    """Bot class for Lilac."""

    DATAFILES = [
        'data/database.db',
        'data/info.yml',
        'data/gblacklist.txt',
        'data/prefixes.yml'
    ]

    def __init__(self):
        self.load_files()
        
        self.logger = Logger()
        sys.stderr = self.logger
        sys.stdout = self.logger
        
        self.send = sender_module.send

        self.up_at = time.time()

        super().__init__(
            command_prefix='',
            description='A bot made for moderation, fun, and verifying KnowYourMeme accounts with Discord.',
            shard_count=1
        )

    def create_data_files(self):
        """Creates the data dir; since it doesn't exist"""
        os.makedirs('data/')
        for file_name in self.DATAFILES:
            f = open(file_name, 'a')
            if '.yml' in file_name:
                f.write('null: null\n')
            f.close()

    def update_data_files(self):
        """Updates data files; ensures all are in place"""
        if not os.path.exists('data/'):
            self.create_data_files()
        if not os.path.exists('img/'):
            os.makedirs('img/')

        for file_name in self.DATAFILES:
            if not os.path.exists(file_name):
                with open(file_name, 'a') as f:
                    if '.yml' in file_name:
                        f.write('null: null\n')

    def load_files(self):
        """Loads all data files."""
        self.update_data_files()

        if not os.path.exists('config.yml'):
            raise FileNotFoundError(
                'The config.yml file is not present; reclone Lilac.')

        self.config = {}
        self.info = {}
        self.blacklist = list(map(int, [s.strip() for s in open('data/gblacklist.txt').readlines()]))
        self.prefixes = {}
    
        self.database = sqlite.connect('data/database.db')

        with open('config.yml', 'r') as config:
            self.config = yaml.load(config)
        with open('data/info.yml', 'r') as info:
            self.info = yaml.load(info) 
        with open('data/prefixes.yml', 'r') as prefixes:
            self.prefixes = yaml.load(prefixes)

    async def get_prefix(self, message):
        if self.config['debug']:
            return "~"

        if message.guild.id in self.prefixes:
            return self.prefixes[message.guild.id]
        else:
            return ","

    async def on_ready(self):
        """Function executes once a shard is ready."""
        shard_ready = len(self.shards)-1
        self.logger.log('INFO', f'Shard {shard_ready} is ready!')

        await self.change_presence(activity=discord.Game(name=f",help"))

    async def on_command_error(self, ctx, exception):
        """Function executes once bot encounters an error."""
        err = None
        if isinstance(exception, commands.CommandInvokeError):
            err = traceback.format_exception(type(exception.original), exception.original,
                                             exception.original.__traceback__, chain=False)
            err = '\n'.join(err)
        else:
            err = traceback.format_exception(type(exception), exception,
                                             exception.__traceback__, chain=False)
            err = '\n'.join(err)

        if isinstance(exception, commands.CommandInvokeError):
            exception = exception.original
            if isinstance(exception, discord.Forbidden):
                await self.send(ctx, ':warning: I don\'t have enough perms to do that.')
            else:
                await self.send(ctx, \
                    f':warning: `CommandInvokeError`: ```{err}```'+
                    ' This should never happen, please report this to one of the developers.'
                )
        elif isinstance(exception, commands.errors.BadArgument):
            await self.send(ctx, f':warning: One or more of the arguments you just gave me are invalid.')
        elif isinstance(exception, commands.errors.MissingRequiredArgument):
            fmt_error = ''.join(exception.args)
            await self.send(ctx, f':warning: {fmt_error}')
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.errors.CheckFailure):
            await self.send(ctx, ':warning: You don\'t have enough perms to perform that action.')
        elif isinstance(exception, commands.CommandOnCooldown):
            await self.send(ctx, ':timer: Command is on cooldown for'+\
                            f' {int(exception.retry_after)} more seconds!')
        else:
            await self.send(ctx, ':warning: An error occured! ```{err}``` This should never happen;' +
                           ' please report this to one of the developers.')
            self.logger.log('ERR', f'Error Occured:\n{err}')

    async def on_member_join(self, member):
        """on_member_join event; handle welcome messages and autoroles"""
        # handle welcome messages
        dbcur = self.database.cursor()

        dbcur.execute(f'SELECT * FROM welcomes WHERE guild_id={member.guild.id}')
        if len(dbcur.fetchall()) == 1:
            dbcur.execute(f'SELECT * FROM welcomes WHERE guild_id={member.guild.id}')
            welcome_config = dbcur.fetchall()[0]

            welcome_channel = None
            if welcome_config[2] != 0:
                welcome_channel = member.guild.get_channel(welcome_config[2])
            else:
                return

            fmt_welcome_message = welcome_config[1].replace(
                '%mention%', member.mention)
            await welcome_channel.send(fmt_welcome_message)

        # handle autoroles
        dbcur.execute(f'SELECT role_id FROM autoroles WHERE guild_id={member.guild.id}')
        autoroles = [x[0] for x in dbcur.fetchall()]
        for role in autoroles:
            to_add = [x for x in member.guild.roles if x.id == role][0]
            await member.add_roles(to_add)

        dbcur.close()

    async def on_member_remove(self, member):
        """on_member_remove event; handle goodbye messages"""
        dbcur = self.database.cursor()

        dbcur.execute(f'SELECT * FROM goodbyes WHERE guild_id={member.guild.id}')
        if len(dbcur.fetchall()) == 1:
            dbcur.execute(f'SELECT * FROM goodbyes WHERE guild_id={member.guild.id}')
            goodbye_config = dbcur.fetchall()[0]

            goodbye_channel = None
            if goodbye_config[2] != 0:
                goodbye_channel = member.guild.get_channel(goodbye_config[2])
            else:
                return

            fmt_goodbye_message = goodbye_config[1].replace(
                '%name%', member.name)
            await goodbye_channel.send(fmt_goodbye_message)
            
        dbcur.close()

    async def on_message(self, message):
        """Handles on_message event."""
        user_executing = message.author
        if user_executing.id in self.blacklist:  # check if user is blacklisted
            return
        elif user_executing.bot:
            return
        elif isinstance(message.channel, discord.DMChannel):
            return
        else:
            await self.process_commands(message)

    async def on_command(self, ctx):
        if 'commands' not in self.info:
            self.info['commands'] = 0

        self.info['commands'] += 1
        yaml.dump(self.info, open('data/info.yml', 'w'))

    def run(self):
        """Run function for Lilac. Loads cogs and runs the bot."""
        cogs = self.config['cogs']

        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                self.logger.log('LOAD', f'Failed to load cog {cog}:\n\t{e}')
            else:
                self.logger.log('LOAD', f'Loaded cog {cog}')

        if self.config['debug']:
            super().run(self.config['debug_token'])
        else:
            super().run(self.config['token'])


Bot = Lilac()
Bot.run()
