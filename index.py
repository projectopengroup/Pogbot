import discord
import os
from discord.ext import commands
from utils.pogfunctions import send_embed
from utils.pogesquelle import get_or_request_token, reset_token, get_prefix
from utils.pogfunctions import create_welcome_card

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

# Define bot and it's commands prefix, calling the get_prefix function, where it returns the server specific prefix.
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=discord.Intents.all(),
                   activity=discord.Game(name='Message "add" to add me to your server.'))
# Allow case insensitive categories.
bot._BotBase__cogs = commands.core._CaseInsensitiveDict()

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
        bot.help_command = HelpFormatted(no_category='Help Command')
        # Get the bots token and name it in a var called BotToken
        BotToken = get_or_request_token()
        # Login with our BotToken
        bot.run(BotToken)

    # On login error do this
    except discord.errors.LoginFailure as exp:
        # Print to terminal that login failed.
        print("Status: Login unsuccessful.")
        # If the login fails then reset the token.
        reset_token()
