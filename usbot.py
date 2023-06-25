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

INTENTS = discord.Intents.default()
INTENTS.message_content = True

class UsBot(commands.Bot):
    """Discord-interacting UsBot class."""

    def __init__(self, **kwargs):
        self.updating = False
        super().__init__(**kwargs, command_prefix=commands.when_mentioned_or('us.'))

    async def setup_hook(self) -> None:
        await self.load_extension('msgcog')
        await self.load_extension('setupcog')
        await self.load_extension('admincog')
        return await super().setup_hook()

    async def on_ready(self):
        print('reddy')

if __name__ == '__main__':
    file = open('secret.txt')
    secret = file.read()
    file.close()

    bot = UsBot(intents=INTENTS)
    dlogger.setup(bot)
    bot.run(secret)
