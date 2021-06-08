import discord
from discord.ext import commands

from utils.pogfunctions import send_embed
from utils.pogesquelle import get_prefix


class Moderator(commands.Cog, name="Moderator"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User = None, *, reason=None):
        if user is None:
            justprefix = await get_prefix(self.bot, ctx.message)
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**You must provide a user.**"
                                         f"\nTry ```{justprefix[2]}ban User```",
                             color=0x08d5f7)
            return
        try:
            if user.top_role >= ctx.author.top_role:
                await send_embed(ctx, send_option=0,
                                 description=f"<:Pogbot_X:850089728018874368> "
                                             f"**The user must have a role below you.**",
                                 color=0x08d5f7)

                return
        except AttributeError:
            print("We can't check non members for roles.")
        if reason is None:
            message = f"You've been banned from **{ctx.guild.name}**."
            await user.send(message)
            await ctx.guild.ban(user)
            await send_embed(ctx, send_option=0,
                             description=f"<:Check:845178458426179605> "
                                         f"**{user} has been banned.**",
                             color=0x08d5f7)
            return
        message = f"You've been banned from **{ctx.guild.name}** for **{reason}**."
        await user.send(message)
        await ctx.guild.ban(user, reason=reason)
        await send_embed(ctx, send_option=0,
                         description=f"<:Check:845178458426179605> "
                                     f"**{user} has been banned.**",
                         color=0x08d5f7)
        return


def setup(bot):
    bot.add_cog(Moderator(bot))
