import sqlite3
import discord
import asyncio
import requests
import re
from discord.ext import commands
from utils.pogfunctions import send_embed, create_welcome_card
from utils.pogesquelle import get_prefix, set_welcome_message, \
    set_welcome_dm_message, set_welcome_role, set_welcome_card, \
    set_welcome_channel, reset_welcome_message, set_global_welcomeimg, \
    set_global_bannercolor, set_global_bgcolor, check_global_user, set_log_item, set_all_log_items, check_rolereactions, \
    set_rolelist, set_emojilist, get_emojilist, get_rolelist

current_users = set()


def setup_in_progress(ctx):
    if ctx.guild.id not in current_users:
        current_users.add(ctx.guild.id)
        return True
    return False


class Config(commands.Cog, name="Setup Command"):  # , hidden=True):
    def __init__(self, bot):
        self.bot = bot

    def is_int(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    @commands.command(name='setup', brief='Walks you through setup.',
                      description='Walks you through, and lists setup options for Pogbot.')
    # @commands.check(setup_in_progress)
    # Look for a command called setup
    async def setup(self, ctx):
        if setup_in_progress(ctx):
            # Check if the user using the setup command has administrator:
            if ctx.author.guild_permissions.administrator:
                # Sending a message embed that says running setup.
                embedorg = discord.Embed(description='<:Check:845178458426179605> **Running Setup...**',
                                         color=0x08d5f7)
                # Collecting the message ID into our global setup id var.
                pogsetupid = await ctx.send(embed=embedorg)
                # Sleep the thread for a little bit so we can edit the message.
                await asyncio.sleep(0.4)
                # Form the embed that we want to use for our edit.
                embededit = await send_embed(ctx, send_option=2, title=f"**Pogbot Setup**", color=0x08d5f7,
                                             thumbnail='https://i.imgur.com/rYKYpDw.png',
                                             description="Respond with any menu option to proceed.",
                                             fields=[('Settings', 'Basic server settings.', True),
                                                     ('Moderator', "Moderator settings.", True),
                                                     ('Reactions', "Setup role reactions.", True),
                                                     ('Commands', "Configure custom commands.", True),
                                                     ('Logs', "Enable event logs.", True),
                                                     ('Switcher', "Turn on/off commands.", True)])
                # Setting our global pogsetup var to true.
                # pogsetup = True

                # orginchannel = ctx.message.channel
                # Editing our original message into our new embed.
                await pogsetupid.edit(embed=embededit)
                # Delete the orignal message.
                await ctx.message.delete()
                trueprefix = await get_prefix(self.bot, ctx)

                def checkAuthor(message):
                    return message.author.id == ctx.author.id and message.guild.id == ctx.guild.id and f"{trueprefix[2]}setup" not in message.content

                while True:
                    await pogsetupid.edit(embed=embededit)
                    try:
                        reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                        if "set" in str(reply.content.lower()):
                            # If it's found then form our embed.
                            embededit = await send_embed(ctx, send_option=2, title=f"**Basic Settings**",
                                                         thumbnail='https://i.imgur.com/rYKYpDw.png', color=0x08d5f7,
                                                         description="Respond with any menu option to proceed.",
                                                         fields=[('Prefix', "Set the bots prefix.", True),
                                                                 ('Welcomes', "Setup welcome actions.",
                                                                  True)])
                            # Edit the original message.
                            await pogsetupid.edit(embed=embededit)
                            # Delete the message.
                            await reply.delete()
                            reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                        if "react" in str(reply.content.lower()):
                            while True:
                                # If found, then form the embed.
                                embededit = await send_embed(ctx, send_option=2, title=f"**Reaction Role Setup**",
                                                             description="**Set up reaction roles for your server "
                                                                         "members.** Respond with a reaction role "
                                                                         "option to continue.",
                                                             color=0x08d5f7,
                                                             thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                             fields=[('Respond with',
                                                                      "**create**, **delete**, or **back**", True)])
                                # Edit the message.
                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()

                                reply = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                                if "create" in str(reply.content.lower()):
                                    message_author = "bot"
                                    while True:
                                        embededit = await send_embed(ctx, send_option=2,
                                                                     title=f"**Reaction Role Setup**",
                                                                     description="Would you like members to react to a "
                                                                                 "user message or a bot message?",
                                                                     color=0x08d5f7,
                                                                     thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                     fields=[('Respond with',
                                                                              "**user**, **bot**, or **back**",
                                                                              True)])
                                        # Edit the message.
                                        await pogsetupid.edit(embed=embededit)
                                        await reply.delete()

                                        reply = await self.bot.wait_for('message', timeout=30, check=checkAuthor)
                                        if "user" in str(reply.content.lower()):
                                            message_author = "user"
                                            break
                                        elif "bot" in str(reply.content.lower()):
                                            message_author = "bot"
                                            break
                                        elif "back" in str(reply.content.lower()):
                                            break

                                    if "back" not in str(reply.content.lower()):
                                        embededit = await send_embed(ctx, send_option=2,
                                                                     title=f"**Reaction Role Setup**",
                                                                     description="Type the reaction role text that you "
                                                                                 "would like to display in this channel",
                                                                     color=0x08d5f7,
                                                                     thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                     fields=[('Example: ',
                                                                              "React to <:Check:845178458426179605> to get "
                                                                              "the ServerPings role, "
                                                                              "<:Shaka:843035933460267018> to get the "
                                                                              "EventPings role, and "
                                                                              "<:Pogbot:845176348661383188> to get the "
                                                                              "GiveawayPings role!",
                                                                              True)])
                                        # Edit the message.
                                        await pogsetupid.edit(embed=embededit)
                                        await reply.delete()

                                        rr_text = ""
                                        rr_emotes_roles = []

                                        reply = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                                        if reply:
                                            rr_text = reply.content
                                            rr_msg = None
                                            if message_author == "bot":
                                                rr_msg = await ctx.send(rr_text)
                                                await reply.delete()
                                            else:
                                                rr_msg = reply

                                            while True:
                                                embededit = await send_embed(ctx, send_option=2,
                                                                             title=f"**Reaction Role Setup**",
                                                                             description="**Respond with the name or "
                                                                                         "ID for the role you'd like to"
                                                                                         " hand out to users when they"
                                                                                         " react with the indicated "
                                                                                         "emote, or respond Done to "
                                                                                         "finish the setup.**",
                                                                             color=0x08d5f7,
                                                                             thumbnail='https://i.imgur.com/rYKYpDw.png')
                                                # Edit the message.
                                                await pogsetupid.edit(embed=embededit)
                                                g_role = None
                                                while True:
                                                    reply = await self.bot.wait_for('message', timeout=60,
                                                                                    check=checkAuthor)
                                                    if "done" in str(reply.content.lower()):
                                                        break
                                                    g_role = discord.utils.get(ctx.guild.roles, name=reply.content)
                                                    if not g_role and self.is_int(reply.content):
                                                        g_role = discord.utils.get(ctx.guild.roles,
                                                                                   id=int(reply.content))
                                                    if not g_role and "@&" in reply.content:
                                                        extra, role_id = reply.content.split("&")
                                                        if ">" in role_id:
                                                            role_id, end = role_id.split(">")
                                                            if self.is_int(role_id):
                                                                g_role = discord.utils.get(ctx.guild.roles,
                                                                                           id=int(role_id))
                                                    if not g_role:
                                                        embededit = await send_embed(ctx, send_option=2,
                                                                                     description=f"<:Pogbot_X"
                                                                                                 f":850089728018874368>"
                                                                                                 f" **Cannot find that "
                                                                                                 f"role.**",
                                                                                     color=0x08d5f7)
                                                        await pogsetupid.edit(embed=embededit)
                                                        await reply.delete()
                                                    else:
                                                        await reply.delete()
                                                        break
                                                if "done" in str(reply.content.lower()):
                                                    await reply.delete()
                                                    await pogsetupid.delete()
                                                    break
                                                rr_role = g_role.id
                                                embededit = await send_embed(ctx, send_option=2,
                                                                             title=f"**Reaction Role Setup**",
                                                                             description="**React to the reaction role "
                                                                                         "message with an emote you "
                                                                                         "would like to assign to a "
                                                                                         "role.**",
                                                                             color=0x08d5f7,
                                                                             thumbnail='https://i.imgur.com/rYKYpDw.png')
                                                # Edit the message.
                                                await pogsetupid.edit(embed=embededit)

                                                def reaction_check(reaction, user):
                                                    return reaction.message.id == rr_msg.id and user.id == ctx.author.id

                                                greaction, guser = await self.bot.wait_for('reaction_add', timeout=60,
                                                                                           check=reaction_check)
                                                await greaction.remove(guser)
                                                rr_emote = greaction.emoji
                                                rr_emotes_roles.append((str(rr_role), str(rr_emote)))

                                            for emote in rr_emotes_roles:
                                                await rr_msg.add_reaction(emote[1])
                                            rolelist_string = ""
                                            emojilist_string = ""
                                            for role in rr_emotes_roles:
                                                rolelist_string = rolelist_string + role[0] + "|"
                                            for emoji in rr_emotes_roles:
                                                emojilist_string = emojilist_string + emoji[1] + "|"
                                            check_rolereactions(rr_msg.id)
                                            set_rolelist(rr_msg.id, rolelist_string)
                                            set_emojilist(rr_msg.id, emojilist_string)
                                            current_users.remove(ctx.guild.id)
                                            return

                                elif "delete" in str(reply.content.lower()):
                                    while True:
                                        embededit = await send_embed(ctx, send_option=2,
                                                                     title=f"**Reaction Role Setup**",
                                                                     description="**Respond with the message id of the "
                                                                                 "reaction role message you would like "
                                                                                 "to delete, or type Back to go back.**",
                                                                     color=0x08d5f7,
                                                                     thumbnail='https://i.imgur.com/rYKYpDw.png')
                                        # Edit the message.
                                        await pogsetupid.edit(embed=embededit)
                                        await reply.delete()
                                        reply = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                                        if "back" in str(reply.content.lower()):
                                            break

                                        if self.is_int(reply.content):
                                            real_message = get_emojilist(int(reply.content))
                                            if real_message == 0:
                                                embededit = await send_embed(ctx, send_option=2,
                                                                             title=f"**Reaction Role Setup**",
                                                                             description="<:Pogbot_X:850089728018874368> "
                                                                                         "**Could not find message**",
                                                                             color=0x08d5f7,
                                                                             thumbnail='https://i.imgur.com/rYKYpDw.png')
                                                # Edit the message.
                                                await pogsetupid.edit(embed=embededit)
                                            else:
                                                rr_msg = await ctx.fetch_message(int(reply.content))
                                                if rr_msg:
                                                    await rr_msg.delete()
                                                    await reply.delete()
                                                    embededit = await send_embed(ctx, send_option=2,
                                                                                 title=f"**Reaction Role Setup**",
                                                                                 description="<:Check:845178458426179605> "
                                                                                             "**Successfully removed the "
                                                                                             "reaction role message**",
                                                                                 color=0x08d5f7,
                                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png')
                                                    # Edit the message.
                                                    await pogsetupid.edit(embed=embededit)
                                                    current_users.remove(ctx.guild.id)
                                                    return
                                                else:
                                                    embededit = await send_embed(ctx, send_option=2,
                                                                                 title=f"**Reaction Role Setup**",
                                                                                 description="<:Pogbot_X:850089728018874368> "
                                                                                             "**Could not find message**",
                                                                                 color=0x08d5f7,
                                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png')
                                                    # Edit the message.
                                                    await pogsetupid.edit(embed=embededit)
                                        else:
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         title=f"**Reaction Role Setup**",
                                                                         description="<:Pogbot_X:850089728018874368> "
                                                                                     "**Could not find message**",
                                                                         color=0x08d5f7,
                                                                         thumbnail='https://i.imgur.com/rYKYpDw.png')
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                elif "back" in str(reply.content.lower()):
                                    # If it's found then form our embed.
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Pogbot Setup**",
                                                                 color=0x08d5f7,
                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 description="Respond with any menu option to proceed.",
                                                                 fields=[('Settings', 'Basic server settings.', True),
                                                                         ('Moderator', "Moderator settings.", True),
                                                                         ('Reactions', "Setup role reactions.", True),
                                                                         ('Commands', "Configure custom commands.",
                                                                          True),
                                                                         ('Logs', "Enable event logs.", True),
                                                                         ('Switcher', "Turn on/off commands.", True)])
                                    # Edit the original message.
                                    await pogsetupid.edit(embed=embededit)
                                    # Delete the message.
                                    await reply.delete()
                                    break

                        # Look for logs in lowercase message.
                        if "log" in str(reply.content.lower()):
                            while True:
                                # If found, then form the embed.
                                embededit = await send_embed(ctx, send_option=2, title=f"**Event Log Setup**",
                                                             description="Select the type of event log you'd like to "
                                                                         "display in this channel.", color=0x08d5f7,
                                                             thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                             fields=[('Respond with',
                                                                      "**all**, **server**, **moderator**, "
                                                                      "**message**, **role**, **voice**"
                                                                      " or **back**",
                                                                      True)])
                                # Edit the message.
                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()
                                reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                                if "all" in str(reply.content.lower()):
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Logs Setup**",
                                                                 description="This will enable **all** logs on this "
                                                                             "channel or disable **all** logs on "
                                                                             "**all** channels:\n\n"
                                                                             "__Server Actions__\n"
                                                                             "Joins\n"
                                                                             "Leaves\n"
                                                                             "Nickname Changes\n"
                                                                             "Invite Information\n"
                                                                             "Channels Made\n"
                                                                             "Channels Deleted\n\n"

                                                                             "__Moderator Actions__\n"
                                                                             "Bans\n"
                                                                             "Unbans\n"
                                                                             "Kicks\n"
                                                                             "Warns\n"
                                                                             "Mutes\n\n"

                                                                             "__Message Actions__\n"
                                                                             "Edits\n"
                                                                             "Deletes\n"
                                                                             "Bulk Deletes\n\n"

                                                                             "__Role Actions__\n"
                                                                             "Roles Made\n"
                                                                             "Roles Deleted\n"
                                                                             "Roles Updated\n"
                                                                             "Roles Given\n"
                                                                             "Roles Removed\n\n"

                                                                             "__Voice Actions__\n"
                                                                             "Joined VC\n"
                                                                             "Left VC\n"
                                                                             "Moved VC\n\n"

                                                                 , color=0x08d5f7,

                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 fields=[('Respond with',
                                                                          "**enable**, **disable**, or **back**",
                                                                          True)])
                                    await pogsetupid.edit(embed=embededit)
                                    await reply.delete()

                                    reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                                    if reply:
                                        if "enable" in str(reply.content.lower()):
                                            set_all_log_items(ctx.guild.id, ctx.channel.id)
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Set all '
                                                                                     f'event logs to this channel.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "disable" in str(reply.content.lower()):
                                            set_all_log_items(ctx.guild.id, "0")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Removed all '
                                                                                     f'event logs from all channels.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                elif "server" in str(reply.content.lower()):
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Logs Setup**",
                                                                 description="This will enable **server** logs on this "
                                                                             "channel or disable **server** "
                                                                             "logs on all channels:\n\n"
                                                                             "__Server Actions__\n"
                                                                             "Joins\n"
                                                                             "Leaves\n"
                                                                             "Nickname Changes\n"
                                                                             "Invite Information\n"
                                                                             "Channels Made\n"
                                                                             "Channels Deleted\n\n"
                                                                 , color=0x08d5f7,

                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 fields=[('Respond with',
                                                                          "**enable**, **disable**, or **back**",
                                                                          True)])
                                    await pogsetupid.edit(embed=embededit)
                                    await reply.delete()

                                    reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                                    if reply:
                                        if "enable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Join")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Leave")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "NickChanged")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Invites")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "ChanMade")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "ChanDelete")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Set server '
                                                                                     f'event logs to this channel.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "disable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, "0", "Join")
                                            set_log_item(ctx.guild.id, "0", "Leave")
                                            set_log_item(ctx.guild.id, "0", "NickChanged")
                                            set_log_item(ctx.guild.id, "0", "Invites")
                                            set_log_item(ctx.guild.id, "0", "ChanMade")
                                            set_log_item(ctx.guild.id, "0", "ChanDelete")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Removed server '
                                                                                     f'event logs from all channels.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                elif "moderator" in str(reply.content.lower()):
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Logs Setup**",
                                                                 description="This will enable **moderator** logs on "
                                                                             "this channel or disable **moderator**"
                                                                             "logs on all channels:\n\n"
                                                                             "__Moderator Actions__\n"
                                                                             "Bans\n"
                                                                             "Unbans\n"
                                                                             "Kicks\n"
                                                                             "Warns\n"
                                                                             "Mutes\n\n"
                                                                 , color=0x08d5f7,

                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 fields=[('Respond with',
                                                                          "**enable**, **disable**, or **back**",
                                                                          True)])
                                    await pogsetupid.edit(embed=embededit)
                                    await reply.delete()

                                    reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                                    if reply:
                                        if "enable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Ban")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Unban")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Kick")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Warn")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Mute")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Set moderator '
                                                                                     f'event logs to this channel.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "disable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, "0", "Ban")
                                            set_log_item(ctx.guild.id, "0", "Unban")
                                            set_log_item(ctx.guild.id, "0", "Kick")
                                            set_log_item(ctx.guild.id, "0", "Warn")
                                            set_log_item(ctx.guild.id, "0", "Mute")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Removed moderator '
                                                                                     f'event logs from all channels.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                elif "message" in str(reply.content.lower()):
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Logs Setup**",
                                                                 description="This will enable **message** logs on "
                                                                             "this channel or disable **message** "
                                                                             "logs on all channels:\n\n"
                                                                             "__Message Actions__\n"
                                                                             "Edits\n"
                                                                             "Deletes\n"
                                                                             "Bulk Deletes\n\n"
                                                                 , color=0x08d5f7,

                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 fields=[('Respond with',
                                                                          "**enable**, **disable**, or **back**",
                                                                          True)])
                                    await pogsetupid.edit(embed=embededit)
                                    await reply.delete()

                                    reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                                    if reply:
                                        if "enable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Edit")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "Delete")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "BulkDelete")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Set message '
                                                                                     f'event logs to this channel.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "disable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, '0', "Edit")
                                            set_log_item(ctx.guild.id, '0', "Delete")
                                            set_log_item(ctx.guild.id, '0', "BulkDelete")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Removed message '
                                                                                     f'event logs from all channels.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                elif "role" in str(reply.content.lower()):
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Logs Setup**",
                                                                 description="This will enable **role** logs on this "
                                                                             "channel or disable **role** logs on"
                                                                             "all channels:\n\n"
                                                                             "__Role Actions__\n"
                                                                             "Roles Made\n"
                                                                             "Roles Deleted\n"
                                                                             "Roles Updated\n"
                                                                             "Roles Given\n"
                                                                             "Roles Removed\n\n"
                                                                 , color=0x08d5f7,

                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 fields=[('Respond with',
                                                                          "**enable**, **disable**, or **back**",
                                                                          True)])
                                    await pogsetupid.edit(embed=embededit)
                                    await reply.delete()

                                    reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                                    if reply:
                                        if "enable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, ctx.channel.id, "RoleMade")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "RoleDelete")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "RoleUpdated")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "RoleGiven")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "RoleRemoved")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Set role '
                                                                                     f'event logs to this channel.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "disable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, "0", "RoleMade")
                                            set_log_item(ctx.guild.id, "0", "RoleDelete")
                                            set_log_item(ctx.guild.id, "0", "RoleUpdated")
                                            set_log_item(ctx.guild.id, "0", "RoleGiven")
                                            set_log_item(ctx.guild.id, "0", "RoleRemoved")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Removed role '
                                                                                     f'event logs from all channels.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                elif "voice" in str(reply.content.lower()):
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Logs Setup**",
                                                                 description="This will enable **voice** logs on this "
                                                                             "channel or disable **voice logs on "
                                                                             "all channels:\n\n"
                                                                             "__Voice Actions__\n"
                                                                             "Joined VC\n"
                                                                             "Left VC\n"
                                                                             "Moved VC\n\n"
                                                                 , color=0x08d5f7,

                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 fields=[('Respond with',
                                                                          "**enable**, **disable**, or **back**",
                                                                          True)])
                                    await pogsetupid.edit(embed=embededit)
                                    await reply.delete()

                                    reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                                    if reply:
                                        if "enable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, ctx.channel.id, "JoinVC")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "LeaveVC")
                                            set_log_item(ctx.guild.id, ctx.channel.id, "MovedVC")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Set voice '
                                                                                     f'event logs to this channel.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "disable" in str(reply.content.lower()):
                                            set_log_item(ctx.guild.id, "0", "JoinVC")
                                            set_log_item(ctx.guild.id, "0", "LeaveVC")
                                            set_log_item(ctx.guild.id, "0", "MovedVC")
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         description=f'<:Check:845178458426179605'
                                                                                     f'> **Removed voice '
                                                                                     f'event logs from all channels.**',
                                                                         color=0x08d5f7)
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                elif "back" in str(reply.content.lower()):
                                    # If it's found then form our embed.
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Pogbot Setup**",
                                                                 color=0x08d5f7,
                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 description="Respond with any menu option to proceed.",
                                                                 fields=[('Settings', 'Basic server settings.', True),
                                                                         ('Moderator', "Moderator settings.", True),
                                                                         ('Reactions', "Setup role reactions.", True),
                                                                         ('Commands', "Configure custom commands.",
                                                                          True),
                                                                         ('Logs', "Enable event logs.", True),
                                                                         ('Switcher', "Turn on/off commands.", True)])
                                    # Edit the original message.
                                    await pogsetupid.edit(embed=embededit)
                                    # Delete the message.
                                    await reply.delete()
                                    break
                        # Look for wel in lowercase message.
                        if "wel" in str(reply.content.lower()):
                            while True:
                                # If found, then form the embed.
                                embededit = await send_embed(ctx, send_option=2, title=f"**Welcome Message Setup**",
                                                             description="Select the type of welcome message or action "
                                                                         "you'd like to edit.", color=0x08d5f7,
                                                             thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                             fields=[('Respond with',
                                                                      "**channel**, **dm**, **role**, or **back**",
                                                                      True)])
                                # Edit the message.
                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()
                                reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                                if "channel" in str(reply.content.lower()):
                                    while True:
                                        # If found, then form the embed.
                                        embededit = await send_embed(ctx, send_option=2,
                                                                     title=f"**Channel Welcome Setup**",
                                                                     description=f"**{ctx.message.channel}** will be "
                                                                                 f"set to the welcome message channel. "
                                                                                 f"\n\n**Choose a type of"
                                                                                 f" welcome message to continue.**",
                                                                     color=0x08d5f7,
                                                                     thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                     fields=[('Respond with',
                                                                              "**image**, **text**, **both**, "
                                                                              "**disable**, or **back**", True)])
                                        # Edit the message.
                                        await pogsetupid.edit(embed=embededit)
                                        await reply.delete()
                                        reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                                        if "disable" in str(reply.content.lower()):
                                            # If found, then form the embed.
                                            set_welcome_card(0, reply.guild.id)
                                            set_welcome_channel(0, reply.guild.id)
                                            reset_welcome_message(reply.guild.id)
                                            embededit = discord.Embed(
                                                description=f'<:Check:845178458426179605> **Reset welcome '
                                                            f'messages for channels and disabled them.**',
                                                color=0x08d5f7)
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return

                                        elif "image" in str(reply.content.lower()):
                                            set_welcome_card(1, reply.guild.id)
                                            set_welcome_channel(reply.channel.id, reply.guild.id)
                                            embededit = discord.Embed(
                                                description=f'<:Check:845178458426179605> **{ctx.message.channel} set'
                                                            f' to welcome message channel.**',
                                                color=0x08d5f7)

                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "text" in str(reply.content.lower()):
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         title=f"**Welcome Message Setup**",
                                                                         description=f"**Respond with the text you'd "
                                                                                     f"like to use for the welcome "
                                                                                     f"message.**",
                                                                         color=0x08d5f7,
                                                                         thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                         fields=[
                                                                             ('Wildcards:', "%USER%, %SERVER%", True),
                                                                             ('Example:',
                                                                              "Hey %USER%, glad you're here, welcome to"
                                                                              " %SERVER%!", True)])
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            textreply = await self.bot.wait_for('message', timeout=60,
                                                                                check=checkAuthor)
                                            if textreply:
                                                set_welcome_channel(textreply.channel.id, textreply.guild.id)
                                                set_welcome_message(str(textreply.content), textreply.guild.id)
                                                embededit = await send_embed(ctx, send_option=2,
                                                                             title=f"**{textreply.guild}'s welcome "
                                                                                   f"message has been set.**",
                                                                             description=f"Channel: {textreply.channel}"
                                                                                         f"\nMessage: "
                                                                                         f"{textreply.content}",
                                                                             color=0x08d5f7)
                                                await pogsetupid.edit(embed=embededit)
                                                set_welcome_card(0, reply.guild.id)
                                                await textreply.delete()
                                                await self.bot.wait_for('message', timeout=5, check=checkAuthor)
                                                current_users.remove(ctx.guild.id)
                                                return
                                        elif "both" in str(reply.content.lower()):
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         title=f"**Welcome Message Setup**",
                                                                         description=f"**Respond with the text you'd "
                                                                                     f"like to use for "
                                                                                     f"the welcome message.**",
                                                                         color=0x08d5f7,
                                                                         thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                         fields=[
                                                                             ('Wildcards:', "%USER%, %SERVER%", True),
                                                                             ('Example:',
                                                                              "Hey %USER%, glad you're here, welcome to"
                                                                              " %SERVER%!", True)])
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            bothreply = await self.bot.wait_for('message', timeout=60,
                                                                                check=checkAuthor)
                                            if bothreply:
                                                set_welcome_message(str(bothreply.content), bothreply.guild.id)
                                                set_welcome_card(1, bothreply.guild.id)
                                                set_welcome_channel(bothreply.channel.id, bothreply.guild.id)
                                                embededit = await send_embed(ctx, send_option=2,
                                                                             title=f"**{bothreply.guild}'s welcome "
                                                                                   f"message has been set.**",
                                                                             description=f"Channel: {bothreply.channel}"
                                                                                         f"\nMessage: "
                                                                                         f"{bothreply.content}",
                                                                             color=0x08d5f7)
                                                await pogsetupid.edit(embed=embededit)
                                                await bothreply.delete()
                                                await self.bot.wait_for('message', timeout=5, check=checkAuthor)
                                                current_users.remove(ctx.guild.id)
                                                return
                                        elif "back" in str(reply.content.lower()):
                                            break

                                elif "role" in str(reply.content.lower()):
                                    while True:
                                        # If found, then form the embed.
                                        embededit = await send_embed(ctx, send_option=2,
                                                                     title=f"**Welcome Role Setup**",
                                                                     description=f"Choose an option to hand out roles "
                                                                                 f"when members join the server.\n\n"
                                                                                 f"**Respond with an option to continue"
                                                                                 f".**",
                                                                     color=0x08d5f7,
                                                                     thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                     fields=[
                                                                         ('Respond with',
                                                                          "**set**, **remove**, or **back**", True)])
                                        # Edit the message.
                                        await pogsetupid.edit(embed=embededit)
                                        await reply.delete()
                                        reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                                        if "set" in str(reply.content.lower()):
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         title=f"**Welcome Role Setup**",
                                                                         description=f"**Respond with the name or ID "
                                                                                     f"for the role you'd like to hand "
                                                                                     f"out to users on join.**",
                                                                         color=0x08d5f7,
                                                                         thumbnail='https://i.imgur.com/rYKYpDw.png')
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            reply = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                                            if reply:
                                                g_role = discord.utils.get(ctx.guild.roles, name=reply.content)
                                                if not g_role and self.is_int(reply.content):
                                                    g_role = discord.utils.get(ctx.guild.roles, id=int(reply.content))
                                                if not g_role and "@&" in reply.content:
                                                    extra, role_id = reply.content.split("&")
                                                    if ">" in role_id:
                                                        role_id, end = role_id.split(">")
                                                        if self.is_int(role_id):
                                                            g_role = discord.utils.get(ctx.guild.roles, id=int(role_id))
                                                if not g_role:
                                                    embededit = await send_embed(ctx, send_option=2,
                                                                                 description=f"<:Pogbot_X:850089728018874368> "
                                                                                             f"**Cannot find that role.**",
                                                                                 color=0x08d5f7)
                                                    await pogsetupid.edit(embed=embededit)
                                                    await reply.delete()
                                                    current_users.remove(ctx.guild.id)
                                                    return

                                                set_welcome_role(g_role.id, reply.guild.id)
                                                embededit = await send_embed(ctx, send_option=2,
                                                                             title=f"**{reply.guild}'s welcome "
                                                                                   f"role setting has been set."
                                                                                   f"**",
                                                                             description=f"Role: {g_role.name}"
                                                                                         f"\nID: {g_role.id}",
                                                                             color=0x08d5f7)
                                                await pogsetupid.edit(embed=embededit)
                                                await reply.delete()

                                                current_users.remove(ctx.guild.id)
                                                return

                                        elif "remove" in str(reply.content.lower()):
                                            set_welcome_role("None", reply.guild.id)
                                            embededit = discord.Embed(
                                                description=f'<:Check:845178458426179605> **Removed welcome role '
                                                            f'settings and disabled them.**',
                                                color=0x08d5f7)
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "back" in str(reply.content.lower()):
                                            break
                                elif "dm" in str(reply.content.lower()):
                                    while True:
                                        # If found, then form the embed.
                                        embededit = await send_embed(ctx, send_option=2,
                                                                     title=f"**Direct Message Welcome Setup**",
                                                                     description=f"**Send a custom message to "
                                                                                 "members when they join.\n\n"
                                                                                 "**Respond with an option to continue.",
                                                                     color=0x08d5f7,
                                                                     thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                     fields=[
                                                                         ('Respond with',
                                                                          "**set**, **remove**, or **back**", True)])
                                        # Edit the message.
                                        await pogsetupid.edit(embed=embededit)
                                        await reply.delete()
                                        reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                                        if "set" in str(reply.content.lower()):
                                            embededit = await send_embed(ctx, send_option=2,
                                                                         title=f"**Direct Message Welcome Setup**",
                                                                         description=f"**Respond with the text you'd like to "
                                                                                     f"use for the welcome message.**",
                                                                         color=0x08d5f7,
                                                                         thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                         fields=[
                                                                             ('Wildcards:', "%USER%, %SERVER%", True),
                                                                             ('Example:',
                                                                              "Hey %USER%, thanks for joining "
                                                                              "%SERVER%! Have a look around, we hop"
                                                                              "e you enjoy your stay with us!",
                                                                              True)])
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            reply = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                                            if reply:
                                                set_welcome_dm_message(reply.content, reply.guild.id)
                                                embededit = await send_embed(ctx, send_option=2,
                                                                             title=f"**{reply.guild}'s direct message "
                                                                                   f"setting has been set.**",
                                                                             description=f"Message:{reply.content}",
                                                                             color=0x08d5f7)
                                                await pogsetupid.edit(embed=embededit)
                                                await reply.delete()
                                                current_users.remove(ctx.guild.id)
                                                return

                                        if "remove" in str(reply.content.lower()):
                                            set_welcome_dm_message("None", reply.guild.id)
                                            embededit = discord.Embed(
                                                description=f'<:Check:845178458426179605> **Removed direct welcome '
                                                            f'messages for new members and disabled them.**',
                                                color=0x08d5f7)
                                            # Edit the message.
                                            await pogsetupid.edit(embed=embededit)
                                            await reply.delete()
                                            current_users.remove(ctx.guild.id)
                                            return
                                        elif "back" in str(reply.content.lower()):
                                            break
                                elif "back" in str(reply.content.lower()):
                                    embededit = await send_embed(ctx, send_option=2, title=f"**Pogbot Setup**",
                                                                 color=0x08d5f7,
                                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                                 description="Respond with any menu option to proceed.",
                                                                 fields=[('Settings', 'Basic server settings.', True),
                                                                         ('Moderator', "Moderator settings.", True),
                                                                         ('Reactions', "Setup role reactions.", True),
                                                                         ('Commands', "Configure custom commands.",
                                                                          True),
                                                                         ('Logs', "Enable event logs.", True),
                                                                         ('Switcher', "Turn on/off commands.", True)
                                                                         ])
                                    await pogsetupid.edit(embed=embededit)
                                    await reply.delete()
                                    break

                        # Look for pre in lowercase message
                        if "pre" in str(reply.content.lower()):
                            # If it's found then form the embed.
                            trueprefix = await get_prefix(self.bot, ctx)
                            embededit = await send_embed(ctx, send_option=2, title=f"**Prefix Setting**",
                                                         description="Respond with a new prefix for the bot.",
                                                         color=0x08d5f7, thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                         fields=[('Current Prefix', f"{trueprefix[2]}", True)])
                            # Edit the message.
                            await pogsetupid.edit(embed=embededit)
                            # Delete the user message.
                            await reply.delete()
                            # Set setup to false.
                            pogsetup = False
                            # Set prefix setup to true.
                            prefixsetup = True
                            reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                            # Set the prefix var to the message.
                            prefix = reply.content
                            # connect to db.
                            conn = sqlite3.connect('prefs.db')
                            # Str for connection type.
                            conn.text_factory = str
                            # Define cursor.
                            cur = conn.cursor()
                            # Update the servers table, set prefix to new prefix where the server ID matches this one.
                            cur.execute(f"UPDATE servers SET Prefix = '{prefix}' WHERE ServerID = '{ctx.guild.id}'")
                            # Commit the changes.
                            conn.commit()
                            # Close the database.
                            conn.close()
                            # Setup the embed.
                            embededit = discord.Embed(color=0x08d5f7,
                                                      description=f'<:Check:845178458426179605> **Bot prefix changed to {prefix}**')
                            # Edit the original message
                            await pogsetupid.edit(embed=embededit)
                            # Turn off Prefix setup.
                            prefixsetup = False
                            # Delete the message sent by user.
                            await reply.delete()
                            break
                    except asyncio.TimeoutError:
                        embedexpire = discord.Embed(description='<:Check:845178458426179605> **Exiting setup...**',
                                                    color=0x08d5f7)
                        # Edit the Original Message.
                        await pogsetupid.edit(embed=embedexpire)
                        await asyncio.sleep(0.4)
                        await pogsetupid.delete()
                        inwelcomesetup = False
                        break
            else:
                # Sending a message saying the user has to be admin to run the command, keeping the message ID as a var.
                denymessage = await send_embed(ctx,
                                               description=f'<:Check:845178458426179605> **You must have ADMINISTRATOR '
                                                           f'to run setup.**',
                                               color=0x08d5f7)
            current_users.remove(ctx.guild.id)


def setup(bot):
    bot.add_cog(Config(bot))
