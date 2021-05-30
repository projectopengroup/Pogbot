import sqlite3
import discord
import base64
import os
import asyncio
from discord.ext import commands
from utils.pogfunctions import get_prefix, send_embed


class Config(commands.Cog, name="config"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prefix(self, ctx):
        justprefix = await get_prefix(self.bot, ctx.message)
        await send_embed(ctx.message.channel, send_option=0, description=f"**The current prefix is {justprefix[2]}**",
                         color=0x08d5f7)


def setup(bot):
    bot.add_cog(Config(bot))
