# Importing requirements
import sqlite3
import discord
import base64
import os
import asyncio
from discord.ext import commands
from utils.pogfunctions import get_prefix, send_embed

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

# Making our connection to the sqllite3 database.
conn = sqlite3.connect('prefs.db')
# Setting this connection to strings/
conn.text_factory = str
# Creating our SQL cursor.
cur = conn.cursor()
# Executing a query that selects everything from the table called configs.
cur.execute('SELECT * FROM configs')
# Pulling data from the cursor by fetching everything.
data = cur.fetchall()
# Setting the bot token variable by looking for the second columns value in the data.
BotToken = (data[0][1])
# If the BotToken is it's default value of "None" then do this stuff.
if "None" not in BotToken:
    print("Status: Bot token found! Loading bot...'")
    # Convert base64 string to bytes
    base64_bytes = BotToken.encode("ascii")
    # Decode base64 bytes to bytes
    fromBytes = base64.b64decode(base64_bytes)
    # Convert to string
    BotToken = fromBytes.decode("ascii")
else:
    print("Status: No bot token found!, prompting user for input")
    # Request bot token from user input.
    BotToken = input("Enter bot token: ")
    # Change string to bytes
    toBytes = BotToken.encode("ascii")
    # Make bytes base64
    base64_bytes = base64.b64encode(toBytes)
    # Change bytes back to a base64 encoded string
    base64_token = base64_bytes.decode("ascii")
    # Update the database with the provided BotToken in Base64.
    cur.execute(f"UPDATE configs SET BotToken = '{base64_token}' WHERE BotToken = 'None'")
    # Commit the database changes.
    conn.commit()

# Close the database connection
conn.close()

# set a global var called prefix
prefix = "!"

# Define bot and it's commands prefix, calling the get_prefix function, where it returns the server specific prefix.
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)

if __name__ == "__main__":
    for files in os.listdir("./cogs"):
        if files.endswith(".py"):
            extension = files[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Status: Extension '{extension}' loaded.")
            except Exception as exp:
                exception = f"{type(exp).__name__}: {exp}"
                print(f"Status: Failed loading extension {extension}\n{exception}")


@bot.event
# Check to see if bot is ready.
async def on_ready():
    # Print status to terminal
    print('Status: Ready.')
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


class HelpFormatted(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embedhelp = discord.Embed(title="**Pogbot's Help Menu**", description=page, color=0x08d5f7)
            embedhelp = embedhelp.set_thumbnail(url="https://i.imgur.com/a9dzSlL.png")
            await destination.send(embed=embedhelp)


# Run the bot using its token if running from main.
if __name__ == "__main__":
    # Try to login with the bot token
    try:
        bot.help_command = HelpFormatted(no_category='documentation')
        bot.run(BotToken)

        # bot = commands.Bot(command_prefix=get_prefix)
    # On login error do this
    except discord.errors.LoginFailure as e:
        print("Status: Login unsuccessful.")
        # Pull up the database again
        conn = sqlite3.connect('prefs.db')
        # Create our SQL cursor.
        cur = conn.cursor()
        # Reset our Token to "None"
        cur.execute(f"UPDATE configs SET BotToken = 'None' WHERE BotToken = '{BotToken}'")
        # Commit Database
        conn.commit()
        # Close Database
        conn.close()
