#!/usr/bin/env python
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
        