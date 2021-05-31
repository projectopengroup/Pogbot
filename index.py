# Importing requirements
import sqlite3
import discord
import base64
import os
import asyncio
from discord.ext import commands
from utils.pogfunctions import get_prefix, send_embed
from utils.pogesquelle import get_or_request_token, reset_token

# Print the bot logo to terminal on start
print('''
    ___       ___       ___       ___       ___       ___   
   /\  \     /\  \     /\  \     /\  \     /\  \     /\  \  
  /::\  \   /::\  \   /::\  \   /::\  \   /::\  \    \:\  \ 
 /::\:\__\ /:/\:\__\ /:/\:\__\ /::\:\__\ /:/\:\__\   /::\__\\
 \/\::/  / \:\/:/  / \:\:\/__/ \:\::/  / \:\/:/  /  /:/\/__/
    \/__/   \::/  /   \::/  /   \::/  /   \::/  /   \/__/   
             \/__/     \/__/     \/__/     \/__/                                                                                      
''')

# set a var called prefix to the bots default prefix
prefix = "!"

# Define bot and it's commands prefix, calling the get_prefix function, where it returns the server specific prefix.
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)

# This is our entry point for loading the bots commands. Cogs are necessary in discord.py for a couple of reasons.
# 1. In order to display the proper category information in the built in help menu, we're required to do it.
# 2. As we add more and more commands and features, the main thread of the bot will become bloated otherwise.
# If we're in the main process.
if __name__ == "__main__":
    # Find all the files in the folder named cogs.
    for files in os.listdir("./cogs"):
        # If in those files we see one that has a .py extension.
        if files.endswith(".py"):
            # Save the name of the extension into the var without its .py extension.
            extension = files[:-3]
            # Try this
            try:
                # Load the scripts as cogs.
                bot.load_extension(f"cogs.{extension}")
                # Print if we loaded it.
                print(f"Status: Extension '{extension}' loaded.")
                # If it errors then pull the information of the error(exception) and name it "exp" for short.
            except Exception as exp:
                # Set the var exception by type, name and exception reason.
                exception = f"{type(exp).__name__}: {exp}"
                # Print the error to terminal.
                print(f"Status: Failed loading extension {extension}\n{exception}")


@bot.event
# Check to see if bot is ready.
async def on_ready():
    # Print status to terminal
    print('Status: Ready.')
    # Change bot playing status to information about how to add the bot.
    await bot.change_presence(
        activity=discord.Game(name='Message "add" to add me to your server.'))


@bot.event
# Look for members joining.
async def on_member_join(member):
    print(f'{member} joined.')


@bot.event
# Look for members leaving.
async def on_member_remove(member):
    print(f'{member} left.')


@bot.event
# Look for members joining.
async def on_message_edit(before, after):
    print(f'Message Edited: Author: {before.author} Original: {before.clean_content} New: {after.clean_content}.')


@bot.event
# Look for members joining.
async def on_message_delete(message):
    print(f'Message Deleted: Author: {message.author} Message: {message.clean_content}.')


@bot.event
# Look for incoming messages in DMs and in Chat.
async def on_message(msg):
    global prefix

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
                os.system('bash run.sh')
                quit()
        # Print incoming direct messages to terminal.
        print(f'{msg.channel} - {msg.author} : {msg.content}')
        # Ensure that we process our commands, as on_message overrides and stops command execution.
        # await bot.process_commands(msg)
        return
    # Print the server name and channel of the message followed by author name and the message content.
    print(f'Server Message in {msg.guild} [{msg.channel}] {msg.author} : {msg.content}')

    # Ensure that we process our commands, as on_message overrides and stops command execution.
    await bot.process_commands(msg)


# Name a new class and call it HelpFormatted passing commands.MinimalHelpCommand as base.
class HelpFormatted(commands.MinimalHelpCommand):
    # Make a new function inside of this class called send_pages
    async def send_pages(self):
        # Name a new var "destination" and use get_destination to get it from the send_pages function that inherited it
        # from commands.MinimalHelpCommand
        destination = self.get_destination()
        # For the page send_pages paginator wrap it in a embed and send it back to the destination.
        # We're doing this to better format the help command responses. This makes them look more EmBeDy.
        for page in self.paginator.pages:
            embedhelp = discord.Embed(title="**Pogbot's Help Menu**", description=page, color=0x08d5f7)
            embedhelp = embedhelp.set_thumbnail(url="https://i.imgur.com/a9dzSlL.png")
            await destination.send(embed=embedhelp)


# If we're running from main.
if __name__ == "__main__":
    # Try to do this
    try:
        # Set the bots help command to our own formatting, pass the field no category renamed to documentation.
        bot.help_command = HelpFormatted(no_category='documentation')
        # Get the bots token and name it in a var called BotToken
        BotToken = get_or_request_token()
        # Login with our BotToken
        bot.run(BotToken)
        # bot = commands.Bot(command_prefix=get_prefix)
    # On login error do this
    except discord.errors.LoginFailure as exp:
        print("Status: Login unsuccessful.")
        # If the login fails then, reset the token but send the token that was bad with it as an ID.
        print(BotToken)
        reset_token()
