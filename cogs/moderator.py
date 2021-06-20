import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from utils.pogfunctions import send_embed, TimeConverter
from utils.pogesquelle import get_prefix, get_log_item


class Moderator(commands.Cog, name="Moderator"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='unmute', aliases=['unsilence'], brief='Unmutes a user.',
                      description="Removes the Muted role from a user.")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member = None):
        justprefix = await get_prefix(self.bot, ctx.message)
        if user is None:
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**You must provide a user.**"
                                         f"\nTry ```{justprefix[2]}unmute User```",
                             color=0x08d5f7)
            return
        role = discord.utils.get(user.guild.roles, name="Muted")
        if role is None:
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**No Muted role found, try running the mute command first.**",
                             color=0x08d5f7)
            return
        if role not in user.roles:
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**User must be muted first.**",
                             color=0x08d5f7)
            return

        await user.remove_roles(role)
        await send_embed(ctx, send_option=0,
                         description=f"<:Check:845178458426179605> "
                                     f"**{user} has been unmuted.**",
                         color=0x08d5f7)
        MutedChannelID = get_log_item(ctx.author.guild.id, "Mute")
        if MutedChannelID != 0:
            if user != "":
                channel = self.bot.get_channel(MutedChannelID)
                membercreated = str(user.created_at.strftime("%b %d, %Y"))
                await send_embed(channel, send_option=0, author=f"{user} was unmuted.",
                                 author_pfp=user.avatar_url_as(format="png"), color=0x5eff89,
                                 description=f"**{user.mention}** was unmuted.",
                                 fields=[('User', f"{user}", True),
                                         ('ID', f"{user.id}", True),
                                         ('Unmuted by', f"{ctx.message.author}", False),
                                         ('Account Created', f"{membercreated}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Unmute")

    @commands.command(name='mute', aliases=['silence'], brief='Mutes a user.',
                      description="Gives a user the muted role.")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user: discord.Member = None, time: TimeConverter = None, *, reason=None):
        if user is None:
            justprefix = await get_prefix(self.bot, ctx.message)
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**You must provide a user.**"
                                         f"\nTry ```{justprefix[2]}mute User```",
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
        role = discord.utils.get(user.guild.roles, name="Muted")
        if role is None:
            muted = await ctx.guild.create_role(name="Muted")
            roles = ctx.me.roles
            roles.reverse()
            toprole = roles[0]
            print(toprole.position)
            position = toprole.position - 1
            await muted.edit(position=position)
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted, send_messages=False, read_messages=False,
                                              read_message_history=False)

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                muted: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            mutedchannel = await ctx.guild.create_text_channel('muted', overwrites=overwrites)
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**No muted role found, so one was created.**",
                             color=0x08d5f7)

            await user.add_roles(muted)
            await send_embed(ctx, send_option=0,
                             description=f"<:Check:845178458426179605> "
                                         f"**{user} has been muted.** *{reason}*",
                             color=0x08d5f7)
            MutedChannelID = get_log_item(ctx.author.guild.id, "Mute")
            if MutedChannelID != 0:
                if user != "":
                    channel = self.bot.get_channel(MutedChannelID)
                    membercreated = str(user.created_at.strftime("%b %d, %Y"))
                    await send_embed(channel, send_option=0, author=f"{user} was muted.",
                                     author_pfp=user.avatar_url_as(format="png"), color=0x404040,
                                     description=f"**{user.mention}** was muted.",
                                     fields=[('User', f"{user}", True),
                                             ('ID', f"{user.id}", True),
                                             ('Duration', f"{time}", True),
                                             ('Reason', f"{reason}", True),
                                             ('Account Created', f"{membercreated}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Mute")
            if time:
                await asyncio.sleep(time)
                await user.remove_roles(role)
                MutedChannelID = get_log_item(ctx.author.guild.id, "Mute")
                if MutedChannelID != 0:
                    if user != "":
                        channel = self.bot.get_channel(MutedChannelID)
                        membercreated = str(user.created_at.strftime("%b %d, %Y"))
                        await send_embed(channel, send_option=0, author=f"{user} was unmuted.",
                                         author_pfp=user.avatar_url_as(format="png"), color=0x5eff89,
                                         description=f"**{user.mention}** was unmuted.",
                                         fields=[('User', f"{user}", True),
                                                 ('ID', f"{user.id}", True),
                                                 ('Account Created', f"{membercreated}", False),
                                                 ('Unmuted by', f"Duration Expired", True)],
                                         timestamp=(datetime.utcnow()),
                                         footer=f"Unmute")
        # If the Muted role did exist
        else:
            await user.add_roles(role)
            await send_embed(ctx, send_option=0,
                             description=f"<:Check:845178458426179605> "
                                         f"**{user} has been muted.** *{reason}*",
                             color=0x08d5f7)
            MutedChannelID = get_log_item(ctx.author.guild.id, "Mute")
            if MutedChannelID != 0:
                if user != "":
                    channel = self.bot.get_channel(MutedChannelID)
                    membercreated = str(user.created_at.strftime("%b %d, %Y"))
                    await send_embed(channel, send_option=0, author=f"{user} was muted.",
                                     author_pfp=user.avatar_url_as(format="png"), color=0x404040,
                                     description=f"**{user.mention}** was muted.",
                                     fields=[('User', f"{user}", True),
                                             ('ID', f"{user.id}", True),
                                             ('Duration', f"{time}", False),
                                             ('Reason', f"{reason}", True),
                                             ('Account Created', f"{membercreated}", False)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Mute")
            if time:
                await asyncio.sleep(time)
                await user.remove_roles(role)
                MutedChannelID = get_log_item(ctx.author.guild.id, "Mute")
                if MutedChannelID != 0:
                    if user != "":
                        channel = self.bot.get_channel(MutedChannelID)
                        membercreated = str(user.created_at.strftime("%b %d, %Y"))
                        await send_embed(channel, send_option=0, author=f"{user} was unmuted.",
                                         author_pfp=user.avatar_url_as(format="png"), color=0x5eff89,
                                         description=f"**{user.mention}** was unmuted.",
                                         fields=[('User', f"{user}", True),
                                                 ('ID', f"{user.id}", True),
                                                 ('Account Created', f"{membercreated}", True)],
                                         timestamp=(datetime.utcnow()),
                                         footer=f"Unmute")
            return

    @commands.command(name='kick', aliases=['boot'], brief='Kicks a user.',
                      description="Kicks a user from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User = None, *, reason=None):
        if user is None:
            justprefix = await get_prefix(self.bot, ctx.message)
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**You must provide a user.**"
                                         f"\nTry ```{justprefix[2]}kick User```",
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
            # I've put these here with the idea of building a switch here in the future.
            # message = f"You've been banned from **{ctx.guild.name}**."
            # await user.send(message)
            await ctx.guild.kick(user)
            await send_embed(ctx, send_option=0,
                             description=f"<:Check:845178458426179605> "
                                         f"**{user} has been kicked.**",
                             color=0x08d5f7)
            KickedChannelID = get_log_item(ctx.author.guild.id, "Kick")
            if KickedChannelID != 0:
                if user != "":
                    channel = self.bot.get_channel(KickedChannelID)
                    membercreated = str(user.created_at.strftime("%b %d, %Y"))
                    await send_embed(channel, send_option=0, author=f"{user} was kicked.",
                                     author_pfp=user.avatar_url_as(format="png"), color=0xa83232,
                                     description=f"**{user.mention}** was kicked.",
                                     fields=[('User', f"{user}", True),
                                             ('ID', f"{user.id}", True),
                                             ('Account Created', f"{membercreated}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Kick")
            return
        # I've put these here with the idea of building a switch here in the future.
        # message = f"You've been banned from **{ctx.guild.name}** for **{reason}**."
        # await user.send(message)
        await ctx.guild.kick(user, reason=reason)
        await send_embed(ctx, send_option=0,
                         description=f"<:Check:845178458426179605> "
                                     f"**{user} has been kicked.**",
                         color=0x08d5f7)
        KickedChannelID = get_log_item(ctx.author.guild.id, "Kick")
        if KickedChannelID != 0:
            if user != "":
                channel = self.bot.get_channel(KickedChannelID)
                membercreated = str(user.created_at.strftime("%b %d, %Y"))
                await send_embed(channel, send_option=0, author=f"{user} was kicked.",
                                 author_pfp=user.avatar_url_as(format="png"), color=0xa83232,
                                 description=f"**{user.mention}** was kicked.",
                                 fields=[('User', f"{user}", True),
                                         ('ID', f"{user.id}", True),
                                         ('Account Created', f"{membercreated}", True),
                                         ('Reason', reason, True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Kick")
        return

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
            # I've put these here with the idea of building a switch here in the future.
            # message = f"You've been banned from **{ctx.guild.name}**."
            # await user.send(message)
            await ctx.guild.ban(user)
            await send_embed(ctx, send_option=0,
                             description=f"<:Check:845178458426179605> "
                                         f"**{user} has been banned.**",
                             color=0x08d5f7)
            return
        # I've put these here with the idea of building a switch here in the future.
        # message = f"You've been banned from **{ctx.guild.name}** for **{reason}**."
        # await user.send(message)
        await ctx.guild.ban(user, reason=reason)
        await send_embed(ctx, send_option=0,
                         description=f"<:Check:845178458426179605> "
                                     f"**{user} has been banned.**",
                         color=0x08d5f7)
        return

    @commands.command(name='unban', aliases=['unbannish', 'unvotedofftheisland'], brief='Unbans a user.',
                      description="Unbans a user from the discord server.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User = None):
        if user is None:
            justprefix = await get_prefix(self.bot, ctx.message)
            await send_embed(ctx, send_option=0,
                             description=f"<:Pogbot_X:850089728018874368> "
                                         f"**You must provide a user.**"
                                         f"\nTry ```{justprefix[2]}unban User```",
                             color=0x08d5f7)
            return
        # I've put these here with the idea of building a switch here in the future.
        # message = f"You've been unbanned from **{ctx.guild.name}**."
        # await user.send(message)
        await ctx.guild.unban(user)
        await send_embed(ctx, send_option=0,
                         description=f"<:Check:845178458426179605> "
                                     f"**{user} has been unbanned.**",
                         color=0x08d5f7)
        return


def setup(bot):
    bot.add_cog(Moderator(bot))
