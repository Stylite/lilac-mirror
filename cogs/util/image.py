#!/usr/bin/env python
import aiohttp
from io import BytesIO
from PIL import Image, ImageFilter

import discord

async def retrieve(url):
    """Retrieves an image from a URL.
    
    retrieve(string) -> PIL.Image"""
    image = None
    try:
        with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                image = Image.open(BytesIO(await r.read()))
    except OSError:
        raise OSError

    return image.convert('RGBA')

def resize(image, dimensions):
    """Resizes an image.
    
    resize(PIL.Image, tuple(int, int)) -> PIL.Image"""
    # lmao why are we abstracting a simple method further 
    image.thumbnail(dimensions)
    return image


        


