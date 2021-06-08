from datetime import datetime

import discord
from discord.ext import commands

from utils.pogfunctions import send_embed
from utils.pogesquelle import get_prefix, get_log_item


class Moderator(commands.Cog, name="Moderator"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='purge', aliases=['clean', 'clear'], brief='Deletes messages in bulk.',
                      description="Deletes the number of messages you'd like to clear.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        embedpurge = discord.Embed(description=f'<:Check:845178458426179605> **Purged {amount} messages...**',
                                 color=0x08d5f7)

        await ctx.channel.purge(limit=amount + 1)
        purgemsg = await ctx.send(embed=embedpurge)
        await purgemsg.delete()
        DeleteChannelID = get_log_item(ctx.author.guild.id, "BulkDelete")
        if DeleteChannelID != 0:
            channel = self.bot.get_channel(DeleteChannelID)
            await send_embed(channel, send_option=0, author=ctx.author,
                             author_pfp=ctx.author.avatar_url_as(format="png"), color=0xff6e6e,
                             description=f"{ctx.author.mention} **purged {amount} messages** "
                                         f"in {ctx.channel.mention}",
                             fields=[('Messages Purged', f"{amount}", True),
                                     ('User ', f"{ctx.author}", False),
                                     ('User ID', f"{ctx.author.id}", False),
                                     ('Channel', f"{ctx.channel}", True),
                                     ('Channel ID', f"{ctx.channel.id}", True)],
                             timestamp=(datetime.utcnow()),
                             footer=f"Purge")

    @commands.command(name='ban', aliases=['bannish', 'votedofftheisland'], brief='Bans a user.',
                      description="Bans a user from the discord server.")
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
