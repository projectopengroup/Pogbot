import sqlite3
import discord
import base64
import os
import asyncio
from discord.ext import commands
from utils.pogfunctions import send_embed


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='github', brief="Responds with github link.",
                      description="Responds with the link to Pogbot's github.")
    # Look for a command called github.
    async def github(self, ctx):
        # Sends the link to the bot github page when the github command is used.
        await ctx.send("https://github.com/projectopengroup/Pogbot")

    @commands.command(name='codeck', aliases=['deck'], brief='Responds with codeck link.',
                      description="Responds with the link to Pogbot's codeck.")
    # Look for a command called codeck.
    async def codeck(self, ctx):
        # Sends the link to the bot codeck page when the codeck command is used.
        await ctx.send("https://open.codecks.io/pog")

    @commands.command(name='echo', brief='Responds with the argument provided.',
                      description="Replies with the same text argument that's provided by the user.")
    # Look for a command called echo
    async def echo(self, ctx, *, arg):
        # Send an echo of the keyword-only argument.
        await ctx.send(arg)

    @commands.command(name='icon', brief="Responds with Pogbot's avatar.", description="Responds with Pogbot's avatar.")
    # Look for a command called icon.
    async def icon(self, ctx):
        # Send pogbot icon
        await ctx.send(self.bot.user.avatar_url)

    @commands.command(name='avatar', aliases=['av', 'pfp'], brief='Responds with an avatar.',
                      description="Responds with the avatar of a user provided, if none provided, responds with the "
                                  "avatar of the user that called the command.")
    # Look for a command called avatar and collects optional user parameter, so if no user given, user = None.
    async def avatar(self, ctx, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author
        # Defining pfp from user's avatar_url.
        pfp = user.avatar_url
        # Creating an embed response using an f string to insert the author long name by using our variable 'user',
        # setting the description to '**Avatar**', the color to match the bot, and the image to the specified user's
        # pfp.
        await send_embed(ctx, title=f'**{user}**', description='**Avatar**', color=0x08d5f7, image=pfp)

    @commands.command(name='userid', aliases=['id', 'uid'], brief='Responds with a users ID.',
                      description="Responds with the ID of a user provided, if none provided, responds with the"
                                  " ID of the user that called the command.")
    # Look for a command called userid and collects optional user parameter, so if no user given, user = None.
    async def userid(self, ctx, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author
        # Creates a discord embed with the elements: title (Which gets the user's tag),
        # description (Which gets the user's id), and color (which is the bot's color).
        await send_embed(ctx, author=f"{user}'s ID", author_pfp=user.avatar_url, description=f'**{user.id}**',
                         color=0x08d5f7)

    @commands.command(name='whois', aliases=['info'], brief='Responds with information on a user.',
                      description="Responds with the information of a user provided, if none provided, responds "
                                  "with the information of the user that called the command.")
    # Look for a command called whois and collects optional user parameter, so if no user given, user = None.
    async def whois(self, ctx, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author

        # Checks if the user is a bot and stores it in a variable
        isBot = "No"
        if user.bot:
            isBot = "Yes"

        # Checks if the user has a nickname set by taking the username, removing the # and numbers, and comparing it
        # with the display name.
        usernameFull = str(user)
        username, usertag = usernameFull.split("#")
        nickname = user.display_name
        if username == nickname:
            nickname = "None"

        # Creates and sends an embed with various user info by adding them as fields. When getting dates, the format
        # as to be converted so that it is easier to read.
        await send_embed(ctx, title=f"**{username}**", thumbnail=user.avatar_url,
                         fields=[(f'**Username:**', usernameFull, True), (f'**Nickname:**', nickname, True),
                                 (f'**User ID:**', str(user.id), True),
                                 (f'**Registered:**', str(user.created_at.strftime("%b %d, %Y")), True),
                                 (f'**Joined Server:**', str(user.joined_at.strftime("%b %d, %Y")), True),
                                 (f'**Is Bot:**', isBot, True)],
                         color=0x08d5f7)


def setup(bot):
    bot.add_cog(General(bot))
