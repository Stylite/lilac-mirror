#!/usr/bin/env python
import time as time_module
import discord

async def notify_devs(ctx, notif):
    """Notifies developers about something.
    Params:
      ctx: commands.Context()
      notif: cogs.util.DevNotif()
      
    notify_devs(ctx, notif) -> None"""
    devs = []
    for uid in ctx.bot.config['cleared']:
        members = ctx.bot.get_all_members()
        for member in members:
            if member.id == uid:
                devs.append(member)
    for dev in devs:
        await dev.send(embed=notif.format_into_embed())
        

class DevNotif:
    def __init__(self, body, notif_type, guild, channel, user, time):
        """Creates a DevNotif class.
        
        Params:
          body: str
          notif_type: str
          guild: discord.Guild()
          channel: discord.Channel()
          user: discord.User()
          time: int
          
        DevNotif() -> None"""
        self.body = body

        if notif_type not in ['Error', 'Feedback', 'Misc']:
            self.notif_type = 'Invalid'
        else:
            self.notif_type = notif_type

        self.guild, self.channel, self.user = guild, channel, user
        self.time = time_module.strftime("%D/%m/%Y %T PST", time)

    def format_into_embed(self):
        """Formats the DevNotif into an embed, and returns it.
            DevNotif.format_into_embed() -> discord.Embed()"""
        embed = discord.Embed()

        if self.notif_type == 'Error':
            embed.colour = 0xff0000
        elif self.notif_type == 'Feedback':
            embed.colour = 0x00efef
        elif self.notif_type == 'Misc':
            embed.colour = 0x2fef00

        embed.title = 'Notification (Thing Occured!):'
        embed.author = f'{self.user.name}#{self.user.discrim} [{self.user.id}]'

        embed.add_field(name='Type:', value=self.notif_type)
        embed.add_field(name='In Guild:', value=self.guild.name)
        embed.add_field(name='In Channel:', value=self.channel.name)
        embed.add_field(name='At Time:', value=self.time)
        embed.add_field(name='Message:', value=self.body, inline=False)

        return embed

