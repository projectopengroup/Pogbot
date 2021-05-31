import sqlite3
from datetime import datetime

import discord
import base64
import os
import asyncio
import aiohttp
from discord.ext import commands
from utils.pogfunctions import get_prefix, send_embed


class Music(commands.Cog, name="music"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Music(bot))
