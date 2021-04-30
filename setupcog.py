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

    async def on_new_guild(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("Sup! I'm UsBot, nice to meet me. Before we get started, we need to go through some setup." +
                                   "\nI work by analyzing all the messages of channels I have access to. So, if you don't see me on the member " +
                                   "list on the right, I won't be able to use that channel to make new messages. That leads us to step 1:"
                                   "\n**1.** Make sure that I have access to all the channels you'd like to be incorporated " +
                                   "(and similarly, make sure I have no access to channels you don't want appearing in my messages)." +
                                   "\n**2.** Once you have done that, click the checkmark reaction on this message to let me know that I can begin analyzing." +
                                   "This can take some time depending on how many messages are in each channel, so be patient. It may take as long as an hour" +
                                   "\nOnce a week, I will update the logs, which means there will be a weekly period of downtime while I crunch the numbers." +
                                   "\n\nFinally, I take your privacy _very seriously_. Your chat logs will never be read by _anyone_. " +
                                   "The only messages the dev can see are the ones you prefix with `us.`.")
                break
