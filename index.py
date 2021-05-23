# Importing requirements
import discord
from discord.ext import commands

# Define bot and it's commands prefix.
bot = commands.Bot(command_prefix="!")

@bot.event
# Look for incoming messages in DMs and in Chat.
async def on_message(msg):
    # Check if the message author is a bot.
    if msg.author.bot:
        # if it is a bot then return the code from here, not going any further.
        return
    # Print the server name and channel of the message followed by author name and the message content.
    print(f'(Server: {msg.guild}) [{msg.channel}] {msg.author} : {msg.content}')
    # Ensure that we process our commands, as on_message overrides and stops command execution.
    await bot.process_commands(msg)


@bot.command()
# Look for a command called ping.
async def ping(msg):
    # Send a message "Pong" when ping has been used.
    await msg.send("Pong")


@bot.event
# Check to see if bot is ready.
async def on_ready():
    # Print status to terminal.
    print('Status: Ready.')

@bot.event
# Look for members joining.
async def on_member_join(member):
    print(f'{member} joined.')


@bot.event
# Look for members leaving.
async def on_member_remove(member):
    print(f'{member} left.')


# Run the bot using it's token.
bot.run('TOKEN HERE')
