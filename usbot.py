import logging
import random as r
import sys
import time
import traceback as tb
from typing import Optional

import discord
from discord.ext import commands

from dlogger import dlogger

logging.basicConfig(level=logging.INFO)

class UsBot(commands.Bot):
    """Discord-interacting UsBot class."""

    def __init__(self, **kwargs):
        self.updating = False
        super().__init__(**kwargs, command_prefix=commands.when_mentioned_or('us.'))

    async def on_ready(self):
        print('reddy')

if __name__ == '__main__':
    bot = UsBot()
    file = open('secret.txt')
    secret = file.read()
    file.close()
    bot.load_extension('msgcog')
    bot.load_extension('setupcog')
    dlogger.setup(bot)
    bot.run(secret)

    @bot.check
    def block_while_updating(ctx):
        return bot.updating == False