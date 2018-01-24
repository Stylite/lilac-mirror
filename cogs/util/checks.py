#!/usr/bin/env python
from discord.ext import commands
import yaml

def is_cleared():
    def predicate(ctx: commands.Context):
        config = yaml.load(open('config.yml', 'r'))
        cleared = config['cleared']
        if ctx.message.author.id in cleared:
            return True
        return False
    return commands.check(predicate)