#!/usr/bin/env python
import asyncio 

import discord

async def send(destination, *args, **kwargs):
    """Sends any message as an embed."""
    to_send = None

    if not args:
        try:
            to_send = kwargs['embed']
        except KeyError:
            raise TypeError('Required argument embed is missing;'+\
                            ' since a string-send has not been specified.')
    else:
        to_send = discord.Embed()
        to_send.colour = 0xbd8cbf
        to_send.description = args[0]

    message = await destination.send(embed=to_send)
    return message

async def confirm_message(ctx, message: str, timeout: float):
    initial_message = await send(ctx, message)
    await initial_message.add_reaction('✅')
    await initial_message.add_reaction('❌')

    def check(reaction_added, user_reacted):
        return user_reacted == ctx.message.author and\
                reaction_added.message.id == initial_message.id

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        await initial_message.delete()
        return False
    else:
        await initial_message.delete()
        if reaction.emoji == '✅':
            return True
        elif reaction.emoji == '❌':
            return False
    
        