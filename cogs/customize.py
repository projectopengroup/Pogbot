import discord
import requests
import re
from discord.ext import commands
from utils.pogfunctions import send_embed, create_welcome_card
from utils.pogesquelle import get_prefix, set_welcome_message, \
    set_welcome_dm_message, set_welcome_role, set_welcome_card, \
    set_welcome_channel, reset_welcome_message, set_global_welcomeimg, \
    set_global_bannercolor, set_global_bgcolor, check_global_user


class Customize(commands.Cog, name="Customization"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='welcomecard', aliases=['wc', 'showcard', 'card', 'swc', 'showwelcomecard'],
                      brief='Displays your welcome card.', description="Displays your welcome card.")
    async def welcomecard(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        check_global_user(user.id)
        avatarRequest = (requests.get(user.avatar_url)).content
        # Testing create welcome card on message send right now, until we get it done.
        await ctx.send(file=create_welcome_card(avatarRequest, user, ctx.guild))

    @commands.command(name='cardbackground', aliases=['cardbg', 'cbg'], brief="Change default card background.",
                      description="Allows users to set their card backgrounds to image url or html color. \n"
                                  "**Color** must be HTML color code: e.g. #b3995d \n"
                                  '**Image** must be a valid url to an image file that ends in .jpg, .png, etc.\n \n'
                                  "Suggested size: \n Width: 1000 "
                                  " Height: 370")
    async def cbg(self, ctx, *, imageurlorcolor):
        user = ctx.author
        try:
            validate = requests.get(imageurlorcolor)
            set_global_welcomeimg(user.id, imageurlorcolor)
            set_global_bgcolor(user.id, "None")
            avatarRequest = (requests.get(user.avatar_url)).content
            await ctx.send(file=create_welcome_card(avatarRequest, user, ctx.guild))
        except requests.exceptions.MissingSchema as exception:
            checkcolor = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', imageurlorcolor)
            if checkcolor:
                set_global_bgcolor(user.id, imageurlorcolor)
                set_global_welcomeimg(user.id, "None")
                avatarRequest = (requests.get(user.avatar_url)).content
                await ctx.send(file=create_welcome_card(avatarRequest, user, ctx.guild))
            else:
                embederror = discord.Embed(
                    description=f"<:Pogbot_X:850089728018874368> **Not a valid URL or Color.**",
                    color=0x08d5f7)
                await ctx.send(embed=embederror)
        except requests.ConnectionError as exception:
            embederror = discord.Embed(
                description=f"<:Pogbot_X:850089728018874368> **Not a valid URL.**",
                color=0x08d5f7)
            await ctx.send(embed=embederror)

    @commands.command(name='cardbannercolor', aliases=['cbcolor', 'bannercolor', 'cardbcolor', 'cbc'],
                      brief="Change banner color.",
                      description="Allows users to set their card banner colors.\n"
                                  "Color must be a HTML color code: e.g. #b3995d")
    async def cbc(self, ctx, *, htmlcolorcode):
        checkcolor = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', htmlcolorcode)
        if checkcolor:
            user = ctx.author
            set_global_bannercolor(user.id, htmlcolorcode)
            avatarRequest = (requests.get(user.avatar_url)).content
            # Testing create welcome card on message send right now, until we get it done.
            await ctx.send(file=create_welcome_card(avatarRequest, user, ctx.guild))
        else:
            embederror = discord.Embed(
                description=f"<:Pogbot_X:850089728018874368> **Not a valid HTML color code.**",
                color=0x08d5f7)
            await ctx.send(embed=embederror)


def setup(bot):
    bot.add_cog(Customize(bot))
