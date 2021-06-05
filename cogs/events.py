import discord
from discord.ext import commands
from utils.pogfunctions import send_embed, create_welcome_card
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
                                 author_pfp=member.avatar_url, color=0x6eff90,
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
    # Look for members leaving.
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
                                 author_pfp=member.avatar_url, color=0xff6e6e,
                                 description=f"**Leave event by** {member.mention}",
                                 fields=[('User', f"{member}", False),
                                         ('User ID', f"{member.id}", False),
                                         ('Roles', f"{str(g_roles_str)}", False),
                                         ('Account Created', f"{membercreated}", True)],
                                 timestamp=(datetime.utcnow()),
                                 footer=f"Left")
        print(f'{member} left.')

    @commands.Cog.listener()
    # Look for members editing messages.
    async def on_message_edit(self, before, after):
        if "Direct Message" in str(before.channel):
            print("Direct Message Detected..")
        else:
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
                                     author_pfp=before.author.avatar_url, color=0xfff56e,
                                     description=f"Message by {before.author.mention}\n**Edited** "
                                                 f"in {before.channel.mention} [Jump to message]({after.jump_url})",
                                     fields=[('Before', f"{msgbefore}", True),
                                             ('After', f"{msgafter}", True),
                                             ('Author ID', f"{after.author.id}", False),
                                             ('Message ID', f"{after.id}", True)],
                                     timestamp=after.edited_at,
                                     footer=f"Edited")

        print(f'Message Edited: Author: {before.author} Original: {before.clean_content} New: {after.clean_content}.')

    @commands.Cog.listener()
    # Look for members deleting messages.
    async def on_message_delete(self, message):
        DeleteChannelID = get_log_item(message.author.guild.id, "Delete")
        if DeleteChannelID != 0:
            if message.content != "":
                channel = self.bot.get_channel(DeleteChannelID)

                MessageFormatted = message.clean_content
                if len(str(MessageFormatted)) > 1300:
                    MessageFormatted = MessageFormatted[1300]

                await send_embed(channel, send_option=0, author=message.author,
                                 author_pfp=message.author.avatar_url, color=0xff6e6e,
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

        # Check if the message author is a bot.
        if msg.author.bot:
            # if it is a bot then return the code from here without going further.
            return
        check_global_user(msg.author.id)
        check_log_item(msg.author.guild.id)
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
        # Print the server name and channel of the message followed by author name and the message content.
        print(f'Server Message in {msg.guild} [{msg.channel}] {msg.author} : {msg.content}')
        # image = requests.get(msg.author.avatar_url, stream=True)
        # welcomecardfolder = Path("img/card_welcomes/")
        # avatar = welcomecardfolder / "avatar.png"
        # file = open(avatar, "wb")
        # file.write(image.content)
        # file.close()


def setup(bot):
    bot.add_cog(Events(bot))
