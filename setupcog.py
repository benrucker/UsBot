from typing import Optional

import discord
from discord.ext import commands
import os


def setup(bot):
    bot.add_cog(SetupCog(bot))


class SetupCog(commands.Cog):
    """Cog for when the bot is added to a new server."""

    def __init__(self, bot):
        self.bot = bot
        pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Initialize directory for new guild."""
        os.makedirs(os.path.join('dlogger', 'exported',
                    str(guild.id)), exist_ok=True)
        print(f'Added to {guild.name}:{guild.id}!')
        await self.on_new_guild(guild)

    @commands.command()
    async def t(self, ctx):
        for cog in self.bot.cogs:
            await ctx.send(cog)

    @commands.is_owner()
    @commands.command()
    async def testjoin(self, ctx):
        await self.on_new_guild(ctx.guild)

    def has_setup_perms(self, channel, user):
        perm = channel.permissions_for(user).manage_channels
        return perm

    async def on_new_guild(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await self.do_welcome_routine(guild, channel)
                break

    async def do_welcome_routine(self, guild, channel):
        msg = await channel.send(
            """Sup! I'm UsBot, nice to meet me. I send new messages that kinda sound like what you might say. In order to copy your style, I analyze all the messages of channels I have access to. So, if you don't see me on the member list on the right, I won't be able to use that channel to make new messages. Once a week, the logs will be updated, which means there will be a weekly period of downtime while I crunch the numbers :nerd:
_As a note, I take your privacy very seriously. Your chat logs will never be read by anyone. The only messages the dev can see are the ones you prefix with `us.`_

Before we begin, we need to do some setup:
**1.** Make sure that I have access to all the channels you'd like to be incorporated.
**2.** Use the command `us.blockchannel #text-channel1 #text-channel2 ...` to block specific channels from being loaded. You should block any spam channel that is used for bot commands or other non-conversational things. Note that any new channel created will automatically be analyzed; if you create a new spam channel, use `us.blockchannel` again to block it.
**3.** Once you have done that, click the checkmark reaction on this message to let me know that I can begin analyzing. This can take some time depending on how many messages are in each channel, so be patient. It may take as long as an hour :flushed:
**4.** Remove my ability to @ everyone by modifying my permissions in the channel that you will use `us.get` in ||unless you're a little crazy||
"""
        )

        await msg.add_reaction('✅')

        def check(reaction, user):
            return self.has_setup_perms(channel, user) and str(reaction.emoji) == '✅'

        message = await self.bot.wait_for('reaction_add', check=check)

        await channel.send('Beginning analysis! I will let you know once I\'m done')

        await self.download_guild(guild)

        await channel.send('Analysis complete! You can now send me commands like `us.get`!')

    async def download_guild(self, guild):
        await self.bot.get_cog('LogCog').log(guild.id)
        await self.bot.get_cog('LogCog').update_guild_models(guild.id)
