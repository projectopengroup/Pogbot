import discord
from discord.ext import commands
from utils.pogfunctions import send_embed, create_welcome_card, diff_lists
from utils.pogesquelle import get_welcome_card, get_welcome_role, \
    get_welcome_channel, get_welcome_message, get_welcome_dm_message, check_global_user, get_welcome_dm_message, \
    get_welcome_role, check_log_item, get_log_item
import os
import requests
from discord.utils import get
from math import sqrt
from pathlib import Path
from datetime import datetime


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Check to see if bot is ready.
    async def on_ready(self):
        # Print status to terminal
        print('Status: Ready.')
        # Don't make any API calls from here, can cause disconnects and errors.
        # Change bot playing status to information about how to add the bot.
        # await self.bot.change_presence(
        #   activity=discord.Game(name='Message "add" to add me to your server.'))

    @commands.Cog.listener()
    # Look for members joining.
    async def on_member_join(self, member):
        check_log_item(member.guild.id)
        JoinChannelID = get_log_item(member.guild.id, "Join")
        if JoinChannelID != 0:
            if member != "":
                channel = self.bot.get_channel(JoinChannelID)
                membercreated = str(member.created_at.strftime("%b %d, %Y"))

                await send_embed(channel, send_option=0, author=f"{member} joined.",
                                 author_pfp=member.avatar_url_as(format="png"), color=0x6eff90,
                                 description=f"**Join event by** {member.mention}",
                                 fields=[('User', f"{member}", False),
                                         ('User ID', f"{member.id}", False),
                                         ('Account Created', f"{membercreated}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Joined")
        # Print to terminal when a member joins.
        print(f'{member} joined.')
        check_global_user(member.id)
        # Get the welcome message from our SQL database by using our function.
        welcomemessage = get_welcome_message(member.guild.id)
        # Make a new var called welcomecardon and set the value to 0.
        welcomecardon = 0
        # Get the welcome card setting(either 0 or 1) from the SQL database
        welcomecardon = get_welcome_card(member.guild.id)

        # Get the dm welcome message from our SQL database by using our function.
        dm_welcomemessage = get_welcome_dm_message(member.guild.id)

        welcomerole = get_welcome_role(member.guild.id)

        if welcomerole != "None":
            for g_role in member.guild.roles:
                if str(welcomerole) in str(g_role.id):
                    await member.add_roles(g_role)

        # If the message isn't "None" then
        if dm_welcomemessage != "None":
            # Replace our wildcards with the appropriate objects.
            dm_welcomemessage = dm_welcomemessage.replace("%USER%", f"{member.mention}")
            dm_welcomemessage = dm_welcomemessage.replace("%SERVER%", f"{member.guild}")
            # Send the welcome message.
            await member.send(dm_welcomemessage)

        if welcomecardon == 1 and welcomemessage != "None":
            # Get the welcome channel from the database and set it to a var named channel.
            channel = self.bot.get_channel(get_welcome_channel(member.guild.id))
            # Make a new var called avatarRequest and send a request to download and get the users avatar to it.
            avatarRequest = (requests.get(member.avatar_url)).content
            welcomemessage = welcomemessage.replace("%USER%", f"{member.mention}")
            welcomemessage = welcomemessage.replace("%SERVER%", f"{member.guild}")
            # Send a message with the file that our create welcome card function returns.
            await channel.send(file=create_welcome_card(avatarRequest, member, member.guild), content=welcomemessage)
            return

        # If the message isn't "None" then
        if welcomemessage != "None":
            # Set our channel var to the channel specified in our SQL database.
            channel = self.bot.get_channel(get_welcome_channel(member.guild.id))
            # Replace our wildcards with the appropriate objects.
            welcomemessage = welcomemessage.replace("%USER%", f"{member.mention}")
            welcomemessage = welcomemessage.replace("%SERVER%", f"{member.guild}")
            # Send the welcome message.
            await channel.send(welcomemessage)
            return

        # if the welcome card setting is set to ON(or 1) then
        if welcomecardon == 1:
            # Get the welcome channel from the database and set it to a var named channel.
            channel = self.bot.get_channel(get_welcome_channel(member.guild.id))
            # Make a new var called avatarRequest and send a request to download and get the users avatar to it.
            avatarRequest = (requests.get(member.avatar_url)).content
            # Send a message with the file that our create welcome card function returns.
            await channel.send(file=create_welcome_card(avatarRequest, member, member.guild))
            return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        check_log_item(role.guild.id)
        RolesCreateChannelID = get_log_item(role.guild.id, "RoleMade")
        if RolesCreateChannelID != 0:
            if role != "":
                channel = self.bot.get_channel(RolesCreateChannelID)
                rolecreated = str(role.created_at.strftime("%b %d, %Y"))
                await send_embed(channel, send_option=0, author=f"{role.guild} role created.",
                                 author_pfp=role.guild.icon_url_as(format="png"), color=0x5c7aff,
                                 description=f"**Role** {role.mention} was created.",
                                 fields=[('Role', f"{role}", True),
                                         ('ID', f"{role.id}", True),
                                         ('Color', f"{role.color}", True),
                                         ('Managed', f"{role.managed}", True),
                                         ('Position', f"{role.position}", True),
                                         ('Tags', f"{role.tags}", True),
                                         ('Mentionable', f"{role.mentionable}", True),
                                         ('Permissions Wrap', f"{role.permissions}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Role created")
        print(f'{role} was created.')

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if after.position == before.position:
            print(f'{after} was updated.')
            check_log_item(before.guild.id)
            RolesUpdateChannelID = get_log_item(before.guild.id, "RoleUpdated")
            if RolesUpdateChannelID != 0:
                if before != "":
                    channel = self.bot.get_channel(RolesUpdateChannelID)
                    await send_embed(channel, send_option=0, author=f"{before.guild} role updated.",
                                     author_pfp=before.guild.icon_url_as(format="png"), color=0xfff959,
                                     description=f"**Role** {after.mention} was updated.",
                                     fields=[('Role', f"{after}", True),
                                             ('ID', f"{after.id}", True),
                                             ('Color', f"{after.color}", True),
                                             ('Managed', f"{after.managed}", True),
                                             ('Position', f"{after.position}", True),
                                             ('Tags', f"{after.tags}", True),
                                             ('Mentionable', f"{after.mentionable}", True),
                                             ('Permissions Wrap', f"{after.permissions}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Role updated")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        print(f'{role} was deleted.')
        check_log_item(role.guild.id)
        RolesDeleteChannelID = get_log_item(role.guild.id, "RoleDelete")
        if RolesDeleteChannelID != 0:
            if role != "":
                channel = self.bot.get_channel(RolesDeleteChannelID)
                rolecreated = str(role.created_at.strftime("%b %d, %Y"))
                await send_embed(channel, send_option=0, author=f"{role.guild} role deleted.",
                                 author_pfp=role.guild.icon_url_as(format="png"), color=0xff5c5c,
                                 description=f"**Role** **{role}** was deleted.",
                                 fields=[('Role', f"{role}", True),
                                         ('ID', f"{role.id}", True),
                                         ('Color', f"{role.color}", True),
                                         ('Managed', f"{role.managed}", True),
                                         ('Position', f"{role.position}", True),
                                         ('Tags', f"{role.tags}", True),
                                         ('Mentionable', f"{role.mentionable}", True),
                                         ('Permissions', f"{role.permissions}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Role deleted")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f'{member} {before.channel} - {after.channel}')
        if str(before.channel) == "None":
            print(f"Joined VC to {after.channel}")
            JoinVCChannelID = get_log_item(member.guild.id, "JoinVC")
            if JoinVCChannelID != 0:
                if member != "":
                    channel = self.bot.get_channel(JoinVCChannelID)
                    await send_embed(channel, send_option=0, author=f"{member} joined a voice channel.",
                                     author_pfp=member.avatar_url_as(format="png"), color=0x42f595,
                                     description=f"**{member.mention}** joined voice channel {after.channel.mention}.",
                                     fields=[('Channel', f"{after.channel}", True),
                                             ('ID', f"{after.channel.id}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Joined voice")
            return
        if str(after.channel) == "None":
            print(f"{member} left VC")
            LeftVCChannelID = get_log_item(member.guild.id, "LeaveVC")
            if LeftVCChannelID != 0:
                if member != "":
                    channel = self.bot.get_channel(LeftVCChannelID)
                    await send_embed(channel, send_option=0, author=f"{member} left voice.",
                                     author_pfp=member.avatar_url_as(format="png"), color=0xf54242,
                                     description=f"**{member.mention}** left voice channel {before.channel.mention}.",
                                     fields=[('Channel', f"{before.channel}", True),
                                             ('ID', f"{before.channel.id}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Left voice")
            return
        if after.channel != before.channel:
            print(f"User Moved Channels to {after.channel}")
            MovedVCChannelID = get_log_item(member.guild.id, "MovedVC")
            if MovedVCChannelID != 0:
                if member != "":
                    channel = self.bot.get_channel(MovedVCChannelID)
                    await send_embed(channel, send_option=0, author=f"{member} moved in voice.",
                                     author_pfp=member.avatar_url_as(format="png"), color=0xffd64f,
                                     description=f"**{member.mention}** moved from voice "
                                                 f"channel {before.channel.mention} to {after.channel.mention}.",
                                     fields=[('Came from', f"{before.channel}", False),
                                             ('ID', f"{before.channel.id}", True),
                                             ('Went to', f"{after.channel}", False),
                                             ('ID', f"{after.channel.id}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Moved voice")
            return


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        check_log_item(member.guild.id)
        LeaveChannelID = get_log_item(member.guild.id, "Leave")
        if LeaveChannelID != 0:
            if member != "":
                channel = self.bot.get_channel(LeaveChannelID)
                membercreated = str(member.created_at.strftime("%b %d, %Y"))
                g_roles = member.roles
                g_roles = [f"{role.mention}\n" for role in g_roles]
                g_roles_str = ''.join(g_roles)
                await send_embed(channel, send_option=0, author=f"{member} left.",
                                 author_pfp=member.avatar_url_as(format="png"), color=0xff6e6e,
                                 description=f"**Leave event by** {member.mention}",
                                 fields=[('User', f"{member}", False),
                                         ('User ID', f"{member.id}", False),
                                         ('Roles', f"{str(g_roles_str)}", False),
                                         ('Account Created', f"{membercreated}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Left")
        print(f'{member} left.')

    @commands.Cog.listener()
    # Look for members leaving.
    async def on_member_update(self, before, after):
        user = before
        if before.nick != after.nick:
            check_log_item(before.guild.id)
            NickChannelID = get_log_item(before.guild.id, "NickChanged")
            if NickChannelID != 0:
                if before != "":
                    channel = self.bot.get_channel(NickChannelID)
                    membercreated = str(before.created_at.strftime("%b %d, %Y"))
                    nickname = after.nick
                    if "None" in str(nickname):
                        nickname = "None"
                    await send_embed(channel, send_option=0, author=f"{before} changed nickname.",
                                     author_pfp=before.avatar_url_as(format="png"), color=0xb9ff6e,
                                     description=f"**Nickname event for** {before.mention}",
                                     fields=[('User', f"{before}", False),
                                             ('**Nickname**', f"**{nickname}**", False),
                                             ('User ID', f"{before.id}", False),
                                             ('Account Created', f"{membercreated}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Changed Nickname")
            print(f"[{before.guild}]{user} changed nickname from {before.nick} to {after.nick}")
        if before.roles != after.roles:
            ldiff = diff_lists(before.roles, after.roles)
            if ldiff[0]:
                RolesAddedID = get_log_item(before.guild.id, "RoleGiven")
                if RolesAddedID != 0:
                    if before != "":
                        channel = self.bot.get_channel(RolesAddedID)
                        RoleName = str(ldiff[0])
                        RoleID = str(ldiff[0])
                        RoleName = RoleName.split("name='")[1].split("'>")[0]
                        RoleID = RoleID.split("Role id=")[1].split(" name=")[0]
                        RoleMention = discord.utils.get(before.guild.roles, name=RoleName)
                        await send_embed(channel, send_option=0, author=f"{before} received a role.",
                                         author_pfp=before.avatar_url_as(format="png"), color=0x7aff97,
                                         description=f"**Role** {RoleMention.mention} was given.",
                                         fields=[('Role', f"{RoleName}", True),
                                                 ('ID', f"{RoleID}", True),
                                                 ('User', f"{before}", False),
                                                 ('UserID', f"{before.id}", True)],
                                         timestamp=(datetime.utcnow()),
                                         footer=f"Role received")
                print(f"{user} role was added: {ldiff[0]}")
            if ldiff[1]:
                RolesRemovedID = get_log_item(before.guild.id, "RoleRemoved")
                if RolesRemovedID != 0:
                    if before != "":
                        channel = self.bot.get_channel(RolesRemovedID)
                        RoleName = str(ldiff[1])
                        RoleID = str(ldiff[1])
                        RoleName = RoleName.split("name='")[1].split("'>")[0]
                        RoleID = RoleID.split("Role id=")[1].split(" name=")[0]
                        RoleMention = discord.utils.get(before.guild.roles, name=RoleName)
                        await send_embed(channel, send_option=0, author=f"{before} lost a role.",
                                         author_pfp=before.avatar_url_as(format="png"), color=0xffce7a,
                                         description=f"**Role** {RoleMention.mention} was removed.",
                                         fields=[('Role', f"{RoleName}", True),
                                                 ('ID', f"{RoleID}", True),
                                                 ('User', f"{before}", False),
                                                 ('UserID', f"{before.id}", True)],
                                         timestamp=(datetime.utcnow()),
                                         footer=f"Role removed")
                print(f"{user} role was removed: {ldiff[1]}")
        if before.activity != after.activity:
            return
        if before.status != after.status:
            return

    @commands.Cog.listener()
    # Look for members leaving.
    async def on_user_update(self, before, after):
        if before.name != after.name:
            for g_guild in before.mutual_guilds:
                if g_guild.id != 0:
                    NickChannelID = get_log_item(g_guild.id, "NickChanged")
                    if NickChannelID != 0:
                        if before != "":
                            channel = self.bot.get_channel(NickChannelID)
                            membercreated = str(before.created_at.strftime("%b %d, %Y"))
                            await send_embed(channel, send_option=0, author=f"{before} changed username.",
                                             author_pfp=before.avatar_url_as(format="png"), color=0xfa7a2f,
                                             description=f"**Username event for** {before.mention}",
                                             fields=[('User before', f"{before}", True),
                                                     ('User now', f"**{after}**", True),
                                                     ('User ID', f"{before.id}", False),
                                                     ('Account Created', f"{membercreated}", True)],
                                             timestamp=(datetime.utcnow()),
                                             footer=f"Changed Username")
                print(f"[{before} changed username to {after}")
            if before.avatar != after.avatar:
                return

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        check_log_item(channel.guild.id)
        ChanCreateID = get_log_item(channel.guild.id, "ChanMade")
        if ChanCreateID != 0:
            if channel != "":
                sendchannel = self.bot.get_channel(ChanCreateID)
                await send_embed(sendchannel, send_option=0, author=f"{channel.guild} channel created.",
                                 author_pfp=channel.guild.icon_url_as(format="png"), color=0x976eff,
                                 description=f"**Channel** {channel.mention} was created.",
                                 fields=[('Name', f"{channel}", True),
                                         ('ID', f"{channel.id}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Channel created")
        print(f'{channel} created.')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        check_log_item(channel.guild.id)
        ChanDeleteID = get_log_item(channel.guild.id, "ChanDelete")
        if ChanDeleteID != 0:
            if channel != "":
                sendchannel = self.bot.get_channel(ChanDeleteID)

                await send_embed(sendchannel, send_option=0, author=f"{channel.guild} channel deleted.",
                                 author_pfp=channel.guild.icon_url_as(format="png"), color=0xfc4128,
                                 description=f"Channel **{channel.mention}** was deleted.",
                                 fields=[('Name', f"{channel}", True),
                                         ('ID', f"{channel.id}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Channel deleted")
        print(f'{channel} deleted.')

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        check_log_item(invite.guild.id)
        INVCreateID = get_log_item(invite.guild.id, "Invites")
        if INVCreateID != 0:
            if invite != "":
                sendchannel = self.bot.get_channel(INVCreateID)
                await send_embed(sendchannel, send_option=0, author=f"{invite.guild} invite created.",
                                 author_pfp=invite.guild.icon_url_as(format="png"), color=0xf5f547,
                                 description=f"**Invite** {invite.code} was created.",
                                 fields=[('Created by', f"{invite.inviter}", True),
                                         ('Max Uses', f"{invite.max_uses}", True),
                                         ('Channel', f"{invite.channel.mention}", True),
                                         ('Max Age', f"{invite.max_age}", True),
                                         ('Temporary', f"{invite.temporary}", True),
                                         ('Invite Code', f"{invite.code}", True)],
                                 timestamp=invite.created_at,
                                 footer=f"Invite created")
        print(f'invite {invite.code} created.')

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        check_log_item(invite.guild.id)
        INVDeleteID = get_log_item(invite.guild.id, "Invites")
        if INVDeleteID != 0:
            if invite != "":
                sendchannel = self.bot.get_channel(INVDeleteID)
                await send_embed(sendchannel, send_option=0, author=f"{invite.guild} invite deleted.",
                                 author_pfp=invite.guild.icon_url_as(format="png"), color=0xfc4128,
                                 description=f"**Invite** {invite.code} was deleted.",
                                 fields=[('Channel', f"{invite.channel.mention}", True),
                                         ('Invite Code', f"{invite.code}", True)],
                                 timestamp=datetime.utcnow(),
                                 footer=f"Invite deleted")
        print(f'invite {invite.code} created.')

    @commands.Cog.listener()
    # Look for members editing messages.
    async def on_message_edit(self, before, after):
        if before.clean_content != after.clean_content:
            if isinstance(before.author, discord.member.User):
                print(f"Non-Member Event Detected: {before.author}")
                return
            if isinstance(before.channel, discord.channel.DMChannel):
                print("Direct Message Detected..")
            if isinstance(before.author, discord.member.Member):
                EditChannelID = get_log_item(before.author.guild.id, "Edit")
                if EditChannelID != 0:
                    if before.content != "":
                        channel = self.bot.get_channel(EditChannelID)
                        msgbefore = before.clean_content
                        msgafter = after.clean_content

                        if len(str(msgbefore)) > 450:
                            msgbefore = f"**Truncated**:{before.clean_content[0:450]}..."

                        if len(str(msgafter)) > 450:
                            msgafter = f"**Truncated**:{after.clean_content[0:450]}..."

                        await send_embed(channel, send_option=0, author=before.author,
                                         author_pfp=before.author.avatar_url_as(format="png"), color=0xfff56e,
                                         description=f"Message by {before.author.mention}\n**Edited** "
                                                     f"in {before.channel.mention} [Jump to message]({after.jump_url})",
                                         fields=[('Before', f"{msgbefore}", True),
                                                 ('After', f"{msgafter}", True),
                                                 ('Author ID', f"{after.author.id}", False),
                                                 ('Message ID', f"{after.id}", True)],
                                         timestamp=after.edited_at,
                                         footer=f"Edited")

            print(
                f'Message Edited: Author: {before.author} Original: {before.clean_content} New: {after.clean_content}.')

    @commands.Cog.listener()
    # Look for members deleting messages.
    async def on_message_delete(self, message):
        if isinstance(message.author, discord.member.User):
            print(f"Non-Member Event Detected: {message.author}")
            return
        if isinstance(message.channel, discord.channel.DMChannel):
            print("Direct Message Detected..")
        if isinstance(message.author, discord.member.Member):
            DeleteChannelID = get_log_item(message.author.guild.id, "Delete")
            if DeleteChannelID != 0:
                if message.content != "":
                    channel = self.bot.get_channel(DeleteChannelID)

                    MessageFormatted = message.clean_content
                    if len(str(MessageFormatted)) > 1300:
                        MessageFormatted = MessageFormatted[1300]

                    await send_embed(channel, send_option=0, author=message.author,
                                     author_pfp=message.author.avatar_url_as(format="png"), color=0xff6e6e,
                                     description=f"Message by {message.author.mention}\n**Deleted** "
                                                 f"in {message.channel.mention}",
                                     fields=[('Message', f"{MessageFormatted}", True),
                                             ('Author ID', f"{message.author.id}", False),
                                             ('Message ID', f"{message.id}", True)],
                                     timestamp=(datetime.utcnow()),
                                     footer=f"Deleted")

        print(f'Message Deleted: Author: {message.author} Message: {message.clean_content}.')

    @commands.Cog.listener()
    # Look for incoming messages in DMs and in Chat.
    async def on_message(self, msg):
        if isinstance(msg.author, discord.member.User):
            print(f"Non-Member Event Detected: {msg.author}")
            # Check if the message channel contains the word direct message
            if "Direct Message" in str(msg.channel):

                if "add" in msg.content:
                    # https://discord.com/api/oauth2/authorize?client_id=843272975771631616&permissions=0&scope=bot
                    await send_embed(msg.channel, send_option=0, title=f"**Click here to add Pogbot to your server**",
                                     url="https://discord.com/api/oauth2/authorize?client_id=843272975771631616"
                                         "&permissions=4294967287&scope=bot",
                                     description="The default prefix is ! \n Run the command !setup once added to "
                                                 "get started.", color=0x08d5f7)
                # If any of the IDs match Mag, Cheetah, or Jonny then
                if str(msg.author.id) == "421781675727388672" or "171238557417996289" or "293362579709886465":
                    # Look for the text "reboot" in the message
                    if "reboot" in msg.content:
                        # reboot has been found so go ahead and run the update command, and then quit the script.
                        print("Reboot Command Accepted.")
                        # go back a dir.
                        os.system('cd ..')
                        os.system('bash run.sh')
                        quit()
                # Print incoming direct messages to terminal.
                print(f'{msg.channel} - {msg.author} : {msg.content}')

                # Ensure that we process our commands, as on_message overrides and stops command execution.
                # await bot.process_commands(msg)
                return
            return
        # Check if the message author is a bot.
        if msg.author.bot:
            # if it is a bot then return the code from here without going further.
            return
        check_global_user(msg.author.id)
        # Print the server name and channel of the message followed by author name and the message content.
        print(f'Server Message in {msg.guild} [{msg.channel}] {msg.author} : {msg.content}')
        check_log_item(msg.author.guild.id)
        # image = requests.get(msg.author.avatar_url, stream=True)
        # welcomecardfolder = Path("img/card_welcomes/")
        # avatar = welcomecardfolder / "avatar.png"
        # file = open(avatar, "wb")
        # file.write(image.content)
        # file.close()


def setup(bot):
    bot.add_cog(Events(bot))
