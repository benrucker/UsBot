import random as r
import sys
import time
import traceback as tb
from typing import Optional

import discord
from discord.ext import commands

import markov

def setup(bot):
    bot.add_cog(MsgCog(bot))

class MsgCog(commands.Cog):

    def __init__(self, bot):
        self.do_tts = False
        self.bot = bot
        pass

    @commands.is_owner()
    @commands.command()
    async def load(self, ctx, ext: str):
        self.bot.load_extension(ext)
        await ctx.send('Loading 99% complete.')

    @commands.is_owner()
    @commands.command()
    async def unload(self, ctx, ext: str):
        self.bot.unload_extension(ext)
        await ctx.send('Unloaded, pew pew.')

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, ext: str):
        self.bot.reload_extension(ext)
        await ctx.send('Reloadception complete.')

    @commands.is_owner()
    @commands.command()
    async def reset(self, ctx):
        markov.__init__()

    @commands.command()
    async def tts(self, ctx):
        self.do_tts = not self.do_tts
        await ctx.message.delete()
        await ctx.message.channel.send('TTS ' + ('Enabled' if self.do_tts else 'Disabled'), delete_after=5)

    @commands.command(name='list')
    async def _list(self, ctx):
        list = '\n'.join(markov.get_people())
        msg = '```' + list + '```'
        await ctx.message.author.send(msg)

    @commands.command()
    async def partyrockersinthehou(self, ctx):
        await ctx.message.channel.send('se tonight')

    @commands.command()
    async def blacklist(self, ctx, name: str):
        if not ctx.message.author.id == 173978157349601283:
            await send_error(ctx.channel, err_type='perms')

        username = self.name_from_command(ctx.message)
        success = markov.add_user_to_blacklist(username)
        msg_out = ''
        if success:
            msg_out = username + ' will no longer send messages here.'
        else:
            msg_out = username + ' could not be blacklisted or is already blacklisted.'
        await ctx.message.channel.send(msg_out)

    @commands.command()
    async def say(self, ctx, content: str):
        try:
            print(ctx.message.content)
            msg = ' '.join(ctx.message.content.split(' ')[1:])
            msg = markov.emojify(msg)
            print(msg)
            await ctx.message.channel.send(msg)
        except BaseException as e:
            print("error on testmessage")
            print(type(e), str(e))
            tb.print_exc()

    @commands.command()
    async def getstupid(self, ctx):
        """Send a message based on a specific user with a different text model."""
        _name = name_from_command(ctx.message)
        await self.command_get_specified(ctx.message, name=_name, num_tries=100000, stupid=True)
    
    @commands.command()
    async def debugemote(self, ctx):
        progress_text = await ctx.message.channel.send('This might take a while.')
        async with ctx.message.channel.typing():
            msg_data = markov.return_one_with_emote()
            print(msg_data)
            msg = self.format_message(msg_data)
        await progress_text.delete()
        await ctx.message.channel.send(msg, tts=self.do_tts)

    @commands.command()
    async def get(self, ctx, name: Optional[str]):
        if not name:
            await self.command_get_unspecified(ctx)
        else:
            await self.command_get_specified(ctx, name)

    async def command_get_specified(self, ctx: commands.Context, name, num_tries=500, stupid=False):
        """Send a message based on a specific user."""
        msg = ''
        async with ctx.channel.typing():
            if not name:
                msg = 'Error: specified user does not exist'
            else:
                msg = self.generate_message(name, num_tries=num_tries, stupid=stupid)
        await ctx.message.channel.send(msg, tts=self.do_tts)

    async def command_get_unspecified(self, message):
        """Send multiple messages based on randomly chosen users.

        Will not send a message based on a user more than once in one invocation.
        """
        names = []
        for x in range(int(r.random() * 3 + 2)):
            while True:
                with message.channel.typing():
                    name = self.get_random_name()
                    if name in names:
                        continue
                    names.append(name)
                    msg = self.generate_message(name, num_tries=250)
                    if msg.startswith('Error'):
                        print("failed, continuing")
                        continue
                    else:
                        print("succeeded")
                        print(msg)
                await message.channel.send(msg, tts=self.do_tts)
                break

    @commands.is_owner()
    @commands.command()
    async def die(self, ctx):
        sys.exit(0)

    def name_from_command(self, message):
        """Return a valid username given a username fragment in a command."""
        return markov.get_full_name(' '.join(message.content.split(' ')[1:]))

    def format_message(self, msg_data):
        """Format message data; return string."""
        return ''.join(msg_data)

    def generate_message(self, name, num_tries=250, stupid=False):
        """Return a new sentence based on user name."""
        msg = markov.return_one(name=name, num_tries=num_tries, stupid=stupid)
        if msg is not None:
            print('succeeded')
            print(msg)
            msg = self.format_message(msg)
        else:
            msg = 'Error: cannot create message from ' + name
        return msg

    def get_random_name(self):
        """Return a random full username that isn't blacklisted."""
        while True:
            name = r.choice(markov.get_people())
            if not markov.user_is_blacklisted(markov.user_from_name(name)):
                return name

    async def send_error(self, channel: discord.TextChannel, err_type='generic'):
        """User-facing error handler."""
        error = 'Error: '
        if err_type == 'generic':
            error += '¯\\_(ツ)_/¯'
        elif err_type == 'perms':
            error += 'you do not have permission to do that'
        await channel.send(error)
