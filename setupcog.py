from typing import Optional

import discord
from discord.ext import commands

def setup(bot):
    bot.add_cog(SetupCog(bot))

class SetupCog(commands.Cog):
    """Cog for when the bot is added to a new server."""

    def __init__(self, bot):
        self.bot = bot
        pass
