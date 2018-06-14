#!/usr/bin/env python
import discord
import datetime

class ModlogHandler(object):
    def __init__(self, bot):
        self.bot = bot

    async def send_to_modlog(self, guild, to_send: discord.Embed):
        dbcur = self.bot.database.cursor()
        dbcur.execute(f'SELECT * FROM logs WHERE guild_id={guild.id}')

        res = dbcur.fetchall()
        if len(res) == 0:
            return
        channel = guild.get_channel(res[0][1])

        await channel.send(embed=to_send)  

    async def handle_event(self, event, data):
        if event == 'message_delete':
            await self.message_deleted(data)
        elif event == 'message_edit':
            if data[0].author.bot:
                return  
            await self.message_edit(data[0], data[1])
        elif event == 'guild_channel_create':
            await self.guild_channel_create(data)
        elif event == 'guild_channel_delete':
            await self.guild_channel_delete(data)
        elif event == 'member_join':
            await self.member_join(data)
        elif event == 'member_remove':
            await self.member_remove(data)

    async def message_deleted(self, msg):
        embed = discord.Embed(title="Message Deleted", colour=0xff0000)
        if msg.attachments:
            embed.set_thumbnail(url=msg.attachments[0].proxy_url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name="Sent By", value=f'{msg.author} ({msg.author.mention})', inline=True)
        embed.add_field(name="In Channel", value=f'{msg.channel.mention}', inline=True)
        embed.add_field(
            name="Content",
            value=(f"```{msg.content}```" if msg.content else "N/A"), 
            inline=False
        )

        await self.send_to_modlog(msg.guild, embed)

    async def message_edit(self, old_msg, new_msg):
        embed = discord.Embed(title="Message Edited", colour=0xffc200)
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name="Sent By", value=f'{new_msg.author} ({new_msg.author.mention})', inline=True)
        embed.add_field(name="In Channel", value=f'{new_msg.channel.mention}', inline=True)
        embed.add_field(
            name="Old Content",
            value=(f"```{old_msg.content}```" if old_msg.content else "N/A"), 
            inline=False
        )
        embed.add_field(
            name="New Content",
            value=(f"```{new_msg.content}```" if new_msg.content else "N/A"), 
            inline=False
        )

        await self.send_to_modlog(new_msg.guild, embed)

    async def guild_channel_create(self, channel):
        if isinstance(channel, discord.TextChannel):
            channel_type = "Text"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "Voice"
        else:
            channel_type = "Category"

        embed = discord.Embed(title="Channel Created", colour=0x00cbff)
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name="Name", value=f"{channel.name} ({channel.mention})", inline=False)
        embed.add_field(name="Channel Type", value=channel_type, inline=False)
        embed.add_field(name="Category", value=channel.category.name if channel.category else "N/A", inline=False)

        await self.send_to_modlog(channel.guild, embed)

    async def guild_channel_delete(self, channel):
        if isinstance(channel, discord.TextChannel):
            channel_type = "Text"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "Voice"
        else:
            channel_type = "Category"

        embed = discord.Embed(title="Channel Deleted", colour=0xff3400)
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name="Name", value=f"{channel.name}", inline=False)
        embed.add_field(name="Channel Type", value=channel_type, inline=False)
        embed.add_field(name="Category", value=channel.category.name if channel.category else "N/A", inline=False)

        await self.send_to_modlog(channel.guild, embed)

    async def member_join(self, member):
        created_at = member.created_at.strftime("%m/%d/%y")

        embed = discord.Embed(title="Member Joined", colour=0x00ff1d)
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name="Username", value=f"{member} ({member.mention})", inline=False)
        embed.add_field(name="Created At (mm/dd/yy)", value=created_at, inline=False)
        embed.set_thumbnail(url=member.avatar_url)

        await self.send_to_modlog(member.guild, embed)

    async def member_remove(self, member):
        embed = discord.Embed(title="Member Left", colour=0xff0000)
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name="Username", value=f"{member} ({member.mention})")
        embed.set_thumbnail(url=member.avatar_url)

        await self.send_to_modlog(member.guild, embed)
