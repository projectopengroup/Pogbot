# Importing requirements
import sqlite3
import discord
import base64
import os
from discord.ext import commands

# Print the bot logo to terminal on start
print('''
      ___           ___           ___           ___           ___           ___     
     /\  \         /\  \         /\  \         /\  \         /\  \         /\  \    
    /::\  \       /::\  \       /::\  \       /::\  \       /::\  \        \:\  \   
   /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \        \:\  \  
  /::\~\:\  \   /:/  \:\  \   /:/  \:\  \   /::\~\:\__\   /:/  \:\  \       /::\  \ 
 /:/\:\ \:\__\ /:/__/ \:\__\ /:/__/_\:\__\ /:/\:\ \:|__| /:/__/ \:\__\     /:/\:\__\\
 \/__\:\/:/  / \:\  \ /:/  / \:\  /\ \/__/ \:\~\:\/:/  / \:\  \ /:/  /    /:/  \/__/
      \::/  /   \:\  /:/  /   \:\ \:\__\    \:\ \::/  /   \:\  /:/  /    /:/  /     
       \/__/     \:\/:/  /     \:\/:/  /     \:\/:/  /     \:\/:/  /     \/__/      
                  \::/  /       \::/  /       \::/__/       \::/  /                 
                   \/__/         \/__/         ~~            \/__/                                                                                            
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

# Define bot and it's commands prefix.
bot = commands.Bot(command_prefix="!")


# Function to create one line embeds. So far it takes most of the possible arguments that you can set to an embed. Not
# all args need to be filled out, but a title or description is required. One of them has to be filled
# out to create an embed, or both. To create an embed, just type ' await send_embed(ctx, arg=value) ' with the arg being
# one of the args that it takes and the appropriate value. Any image, thumbnail, pfp, etc. takes a url in the form of a
# string. The fields argument takes an array of tuples. So for example:
#                                                           [(name1, value1, inline1), (name2, value2, inline2)]
async def send_embed(ctx, title=None, description=None, author=None, author_pfp=None,
                     color=discord.Colour.default(), footer=None, thumbnail=None, image=None, fields=None):
    if title is None and description is None:
        print("[Error]: Error creating embed. No title or description specified.")
    else:
        # Initializes new_embed variable
        new_embed = None

        # Checks if title and description are 'None'. If None, that element isn't added to the embed
        if title is not None and description is not None:
            new_embed = discord.Embed(title=title, description=description, color=color)
        elif title is not None and description is None:
            new_embed = discord.Embed(title=title, color=color)
        elif title is None and description is not None:
            new_embed = discord.Embed(description=description, color=color)

        # Checks if each argument is 'None'. If None, the argument is ignored. But if not None, then the element is
        # added to the embed.
        if image is not None:
            new_embed.set_image(url=image)
        if footer is not None:
            new_embed.set_footer(text=footer)
        if thumbnail is not None:
            new_embed.set_thumbnail(url=thumbnail)
        if author is not None and author_pfp is not None:
            new_embed.set_author(name=author, icon_url=author_pfp)
        elif author is not None and author_pfp is None:
            new_embed.set_author(name=author)

        if fields is not None:
            for field in fields:
                new_embed.add_field(name=field[0], value=field[1], inline=field[2])

        await ctx.send(embed=new_embed)


@bot.event
# Look for incoming messages in DMs and in Chat.
async def on_message(msg):
    # Check if the message author is a bot.
    if msg.author.bot:
        # if it is a bot then return the code from here without going further.
        return

    # Check if the message channel contains the word direct message
    if "Direct Message" in str(msg.channel):
        # If it does, then print it as such and return without going further.
        print(str(msg.author.id))
        if str(msg.author.id) == "421781675727388672":
            print(msg.content)
            if "reboot" in msg.content:
                print("Reboot Command Accepted.")
                os.system('bash run.sh')
                quit()

        print(f'{msg.channel} - {msg.author} : {msg.content}')
        await bot.process_commands(msg)
        return
    # Print the server name and channel of the message followed by author name and the message content.
    print(f'Server Message in {msg.guild} [{msg.channel}] {msg.author} : {msg.content}')
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


@bot.command()
# Look for a command called codeck.
async def codeck(ctx):
    # Sends the link to the bot codeck page when the codeck command is used.
    await ctx.send("https://open.codecks.io/pog")


@bot.command()
# Look for a command called echo
async def echo(ctx, *, arg):
    # Send an echo of the keyword-only argument.
    await ctx.send(arg)


@bot.command()
# Look for a command called icon.
async def icon(ctx):
    # Send pogbot icon
    await ctx.send(bot.user.avatar_url)


@bot.command(name='avatar', aliases=['av', 'pfp'])
# Look for a command called avatar and collects optional user parameter, so if no user given, user = None.
async def avatar(ctx, user: discord.Member = None):
    # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
    # command author.
    if user is None:
        user = ctx.author
    # Defining pfp from user's avatar_url.
    pfp = user.avatar_url
    # Creating an embed response using an f string to insert the author long name by using our variable 'user', setting
    # the description to '**Avatar**', the color to match the bot, and the image to the specified user's pfp.
    await send_embed(ctx, title=f'**{user}**', description='**Avatar**', color=0x08d5f7, image=pfp)


@bot.command(name='userid', aliases=['id', 'uid'])
# Look for a command called userid and collects optional user parameter, so if no user given, user = None.
async def userid(ctx, user: discord.Member = None):
    # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
    # command author.
    if user is None:
        user = ctx.author
    # Creates a discord embed with the elements: title (Which gets the user's tag),
    # description (Which gets the user's id), and color (which is the bot's color).
    await send_embed(ctx, author=f"{user}'s ID", author_pfp=user.avatar_url, description=f'**{user.id}**',
                     color=0x08d5f7)


@bot.command()
# Look for a command called userid and collects optional user parameter, so if no user given, user = None.
async def whois(ctx, user: discord.Member = None):
    # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
    # command author.
    if user is None:
        user = ctx.author

    # Checks if the user is a bot and stores it in a variable
    isBot = "No"
    if user.bot:
        isBot = "Yes"

    # Checks if the user has a nickname set by taking the username, removing the # and numbers, and comparing it with
    # the display name.
    usernameFull = str(user)
    username, usertag = usernameFull.split("#")
    nickname = user.display_name
    if username == nickname:
        nickname = "None"

    # Creates and sends an embed with various user info by adding them as fields. When getting dates, the format as to
    # be converted so that it is easier to read.
    await send_embed(ctx, title=f"**{username}**", thumbnail=user.avatar_url,
                     fields=[(f'**Username:**', usernameFull, True), (f'**Nickname:**', nickname, True),
                             (f'**User ID:**', str(user.id), True),
                             (f'**Registered:**', str(user.created_at.strftime("%b %d, %Y")), True),
                             (f'**Joined Server:**', str(user.joined_at.strftime("%b %d, %Y")), True),
                             (f'**Is Bot:**', isBot, True)],
                     color=0x08d5f7)


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


@bot.event
# Look for members joining.
async def on_message_edit(before, after):
    print(f'Message Edited: Author: {before.author} Original: {before.clean_content} New: {after.clean_content}.')


@bot.event
# Look for members joining.
async def on_message_delete(message):
    print(f'Message Deleted: Author: {message.author} Message: {message.clean_content}.')


# Run the bot using its token if running from main.
if __name__ == "__main__":
    # Try to login with the bot token
    try:
        bot.run(BotToken)
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
