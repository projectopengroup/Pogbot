# Importing requirements
import discord
from discord.ext import commands

# Request bot token from user input.
BotToken = input("Enter bot token: ")

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
async def ping(ctx):
    # Send a message "Pong" when ping has been used.
    await ctx.send("Pong")


@bot.command()
# Look for a command called github.
async def github(ctx):
    # Sends the link to the bot github page when the github command is used.
    await ctx.send("https://github.com/projectopengroup/Pogbot")


# DJ's code for finding an avatar
# Assigning command aliases to look for.
@bot.command(name='avatar', aliases=['av', 'pfp'])
# Look for a command called avatar.
async def avatar(ctx):
    # Defining 'user' from command origin(ctx)'s author(person who sent the command).
    user = ctx.author
    # Defining 'userid' from command origin(ctx)'s author's ID(identification number).
    # userid = user.id
    # Defining pfp from ctx.author(user)'s avatar_url.
    pfp = user.avatar_url
    # Creating an embed response using an f string to insert the author long name by using our variable 'user'.
    embed = discord.Embed(
        title=f'**{user}**',
        description='**Avatar**',
        color=0x08d5f7
    )
    # Setting the embed's image url property to the one we defined from user(ctx.author).avatar_url
    embed.set_image(url=pfp)
    # Sending the embed message response back.
    await ctx.send(embed=embed)


# DJ's code for finding an avatar
# Assigning command aliases to look for.
@bot.command(name='avatar', aliases=['av', 'pfp'])
# Look for a command called avatar.
async def avatar(ctx):
    # Defining 'user' from command origin(ctx)'s author(person who sent the command).
    user = ctx.author
    # Defining 'userid' from command origin(ctx)'s author's ID(identification number).
    userid = ctx.message.author.id
    # Defining pfp from ctx.author(user)'s avatar_url.
    pfp = user.avatar_url
    # Creating an embed response using an f string to insert the author long name by using our variable 'user'.
    embed = discord.Embed(
        title=f'**{user}**',
        description='**Avatar**',
        color=0x08d5f7
    )
    # Setting the embed's image url property to the one we defined from user(ctx.author).avatar_url
    embed.set_image(url=pfp)
    # Sending the embed message response back.
    await ctx.send(embed=embed)


@bot.event
# Check to see if bot is ready.
async def on_ready():
    # Print status to terminal.
    print('Status: Ready.')
    await bot.change_presence(
        activity=discord.Game(name='with discord API'))


@bot.event
# Look for members joining.
async def on_member_join(member):
    print(f'{member} joined.')


@bot.event
# Look for members leaving.
async def on_member_remove(member):
    print(f'{member} left.')


# Run the bot using its token.
bot.run(BotToken)
