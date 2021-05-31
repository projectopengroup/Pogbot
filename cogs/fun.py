import sqlite3
from datetime import datetime

import discord
import base64
import os
import asyncio
import aiohttp
import json
from discord.ext import commands
from utils.pogfunctions import get_prefix, send_embed


# https://some-random-api.ml/

class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cat', aliases=['cats'], brief='Responds with a picture of a cat.',
                      description="Responds with a picture of a random cat.")
    # Look for a command called cat
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://thecatapi.com/api/images/get')
            url = request.url
        await send_embed(ctx, title="Cats", description='Random cat picture', image=f'{url}',
                         color=0x08d5f7)

    @commands.command(name='dog', aliases=['dogs'], brief='Responds with a picture of a dog.',
                      description="Responds with a picture of a random dog.")
    # Look for a command called cat
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://thedogapi.com/api/images/get')
            url = request.url
        await send_embed(ctx, title="Dogs", description='Random dog picture', image=f'{url}',
                         color=0x08d5f7)


def setup(bot):
    bot.add_cog(Fun(bot))
