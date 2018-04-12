#!/usr/bin/env python
import asyncio

def run_coro(coro, bot):
    future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        future.result()
    except:
        pass