from discord.ext import commands
import subprocess
import sys
from typing import Optional, Tuple
import random


async def setup(bot):
    await bot.add_cog(Admin(bot))


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_guild_diag(self, ctx):
        out = ''
        out += f'Logged into **{len(self.bot.guilds)}** guilds:\n'
        for guild in list(self.bot.guilds):
            out += f'    {guild.name} : {str(guild.id)[:5]}\n'
        await ctx.send(out)

    async def send_message_diag(self, ctx):
        await ctx.send(f'There are currently {len(self.bot.cached_messages)} cached messages.')

    async def send_vc_diag(self, ctx):
        await ctx.send(f'There are currently {len(self.bot.voice_clients)} cached voice clients.')

    async def send_latency_diag(self, ctx):
        latency = self.bot.latency * 1000
        await ctx.send(f'Current websocket latency: {latency:.5} ms')

    async def send_emoji_diag(self, ctx):
        out = f'JermaBot has access to {len(self.bot.emojis)} emojis including '
        e = random.sample(self.bot.emojis, 3)
        out += f'{e[0]}, {e[1]}, and {e[2]}.'
        await ctx.send(out)

    @commands.is_owner()
    @commands.command()
    async def diag(self, ctx, lightweight: Optional[bool]):
        await self.send_guild_diag(ctx)
        await self.send_message_diag(ctx)
        await self.send_vc_diag(ctx)
        await self.send_latency_diag(ctx)
        if not lightweight:
            await self.send_emoji_diag(ctx)
    
    @commands.is_owner()
    @commands.command()
    async def usercount(self, ctx):
        count = 0
        for guild in self.bot.guilds:
            count += guild.member_count
        await ctx.send(count)
