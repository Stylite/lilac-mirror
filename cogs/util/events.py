#!/usr/bin/env python
import inspect

class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_message_delete(self, msg):
        await self.bot.loghandler.handle_event('message_delete', msg)

    async def on_message_edit(self, old_msg, new_msg):
        await self.bot.loghandler.handle_event('message_edit', [old_msg, new_msg])

    async def on_guild_channel_create(self, channel):
        await self.bot.loghandler.handle_event('guild_channel_create', channel)

    async def on_guild_channel_delete(self, channel):
        await self.bot.loghandler.handle_event('guild_channel_delete', channel)

    async def on_member_join(self, member):
        """on_member_join event; handle welcome messages and autoroles"""
        # handle welcome messages
        dbcur = self.bot.database.cursor()

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

        await self.bot.loghandler.handle_event('member_join', member)

    async def on_member_remove(self, member):
        """on_member_remove event; handle goodbye messages"""
        dbcur = self.bot.database.cursor()

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

        await self.bot.loghandler.handle_event('member_remove', member)

    async def on_guild_role_create(self, role):
        await self.bot.loghandler.handle_event('guild_role_create', role)
    
    async def on_guild_role_delete(self, role):
        await self.bot.loghandler.handle_event('guild_role_delete', role)

    async def on_member_ban(self, guild, user):
        await self.bot.loghandler.handle_event('member_ban', [guild, user])

    async def on_member_unban(self, guild, user):
        await self.bot.loghandler.handle_event('member_unban', [guild, user])

def setup(bot):
    events = Events(bot)

    for m in inspect.getmembers(events):
        if m[0].startswith('on_'):
            setattr(bot, m[0], m[1])

    bot.logger.log('LOAD', 'Loaded event listeners.')

