#!/usr/bin/env python
import asyncio
import aiohttp

def run_coro(coro, bot):
    future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        future.result()
    except:
        pass

async def unsplash_api_request(query):
    headers = {
        'Authorization': 'Client-ID b85945748519f0c1e96c6e09207579a1797c3ae634e368ca11f78264126b3f75'
    }
    body = {
        'query': query
    }
    async with aiohttp.ClientSession() as session:
        res = await session.get('https://api.unsplash.com/photos/random', params=body, headers=headers)
        json_resp = await res.json()

    if not 200 <= res.status < 300:
        return False
    return json_resp['urls']['regular'] 