import discord
from discord.ext import commands
from utils.pogfunctions import send_embed
import os


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Check to see if bot is ready.
    async def on_ready(self):
        # Print status to terminal
        print('Status: Ready.')
        # Change bot playing status to information about how to add the bot.
        await self.bot.change_presence(
            activity=discord.Game(name='Message "add" to add me to your server.'))

    @commands.Cog.listener()
    # Look for members joining.
    async def on_member_join(self, member):
        print(f'{member} joined.')

    @commands.Cog.listener()
    # Look for members leaving.
    async def on_member_remove(self, member):
        print(f'{member} left.')

    @commands.Cog.listener()
    # Look for members joining.
    async def on_message_edit(self, before, after):
        print(f'Message Edited: Author: {before.author} Original: {before.clean_content} New: {after.clean_content}.')

    @commands.Cog.listener()
    # Look for members joining.
    async def on_message_delete(self, message):
        print(f'Message Deleted: Author: {message.author} Message: {message.clean_content}.')

    @commands.Cog.listener()
    # Look for incoming messages in DMs and in Chat.
    async def on_message(self, msg):

        # Check if the message author is a bot.
        if msg.author.bot:
            # if it is a bot then return the code from here without going further.
            return

        # Check if the message channel contains the word direct message
        if "Direct Message" in str(msg.channel):
            # If any of the IDs match Mag, Cheetah, or Jonny then
            if "add" in msg.content:
                # https://discord.com/api/oauth2/authorize?client_id=843272975771631616&permissions=0&scope=bot
                await send_embed(msg.channel, send_option=0, title=f"**Click here to add Pogbot to your server**",
                                 url="https://discord.com/api/oauth2/authorize?client_id=843272975771631616"
                                     "&permissions=0&scope=bot",
                                 description="The default prefix is ! \n Run the command !setup once added to "
                                             "get started.", color=0x08d5f7)
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


def setup(bot):
    bot.add_cog(Events(bot))
