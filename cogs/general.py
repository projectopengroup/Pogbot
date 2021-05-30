import sqlite3
import discord
import base64
import os
import asyncio
from discord.ext import commands


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', aliases=['latency'], brief='Responds with latency.', description='This command '
                                                                                                    'will respond '
                                                                                                    'with the '
                                                                                                    'bots latency')
    # Look for a command called ping.
    async def ping(self, ctx):
        # Responds with the bots latency in a embed.
        embedping = discord.Embed(
            description=f"<:Check:845178458426179605> **Pogbot's latency is {round(self.bot.latency * 100)}ms**",
            color=0x08d5f7)
        # Edit the original message
        await ctx.send(embed=embedping)

    @commands.command()
    # Look for a command called github.
    async def github(self, ctx):
        # Sends the link to the bot github page when the github command is used.
        await ctx.send("https://github.com/projectopengroup/Pogbot")

    @commands.command()
    # Look for a command called codeck.
    async def codeck(self, ctx):
        # Sends the link to the bot codeck page when the codeck command is used.
        await ctx.send("https://open.codecks.io/pog")

    @commands.command()
    # Look for a command called echo
    async def echo(self, ctx, *, arg):
        # Send an echo of the keyword-only argument.
        await ctx.send(arg)

    @commands.command()
    # Look for a command called icon.
    async def icon(self, ctx):
        # Send pogbot icon
        await ctx.send(self.bot.user.avatar_url)

    @commands.command(name='avatar', aliases=['av', 'pfp'])
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

    @commands.command(name='userid', aliases=['id', 'uid'])
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

    @commands.command()
    # Look for a command called userid and collects optional user parameter, so if no user given, user = None.
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


async def send_embed(ctx, send_option=0, title=None, description=None, author=None, author_pfp=None,
                     color=discord.Colour.default(), footer=None, thumbnail=None, image=None, url=None, fields=None):
    if title is None and description is None:
        print("[Error]: Error creating embed. No title or description specified.")
    else:
        # Initializes new_embed variable
        new_embed = discord.Embed(colour=color)

        # Checks if title, description, and url are 'None'. If None, that element isn't added to the embed
        if title is not None:
            new_embed.title = title
        if description is not None:
            new_embed.description = description
        if url is not None:
            new_embed.url = url

        # Checks if each argument is 'None'. If None, the argument is ignored. But if not None, then the element is
        # added to the embed.
        if image is not None:
            new_embed.set_image(url=image)
        if footer is not None:
            new_embed.set_footer(text=footer)
        if thumbnail is not None:
            new_embed.set_thumbnail(url=thumbnail)
        if author is not None and author_pfp is not None:
            new_embed.set_author(name=author, icon_url=author_pfp)
        elif author is not None and author_pfp is None:
            new_embed.set_author(name=author)

        if fields is not None:
            for field in fields:
                new_embed.add_field(name=field[0], value=field[1], inline=field[2])

        if send_option == 0:
            await ctx.send(embed=new_embed)
        elif send_option == 1:
            return await ctx.send(embed=new_embed)
        elif send_option == 2:
            return new_embed
