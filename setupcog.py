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
        os.makedirs(os.path.join('dlogger', 'exported', str(guild.id)), exist_ok=True)
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
        msg = await channel.send("Sup! I'm UsBot, nice to meet me. Before we get started, we need to go through some setup." +
                    "\nI work by analyzing all the messages of channels I have access to. So, if you don't see me on the membe " +
                    " list on the right, I won't be able to use that channel to make new messages. That leads us to step 1:"
                    "\n**1.** Make sure that I have access to all the channels you'd like to be incorporated" +
                    " (and similarly, make sure I have no access to channels you don't want appearing in my messages ||i **strongly** recommend removing me" +
                    " from your bot spam channel, if you have one||)." +
                    "\n**2.** Once you have done that, click the checkmark reaction on this message to let me know that I can begin analyzing." +
                    " This can take some time depending on how many messages are in each channel, so be patient. It may take as long as an hour 😳" +
                    "\n\nAlso, once a week, the logs will be updated, which means there will be a weekly period of downtime while I crunch the numbers 🤓" +
                    "\nFinally, I take your privacy _very seriously_. Your chat logs will never be read by _anyone_. " +
                    " The only messages the dev can see are the ones you prefix with `us.`.")

        await msg.add_reaction('✅')

        def check(reaction, user):
            return self.has_setup_perms(channel, user) and str(reaction.emoji) == '✅'

        message = await self.bot.wait_for('reaction_add', check=check)

        await channel.send('Beginning analysis! I will let you know once I\'m done')

        self.begin_download(guild)

        await channel.send('Analysis complete! You can now send me commands like `us.get`!')


    def begin_download(self, guild):
        self.bot.get_cog('LogCog').log(guild)