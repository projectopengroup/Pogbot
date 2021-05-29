# Importing requirements
import sqlite3
import discord
import base64
import os
import asyncio
from discord.ext import commands

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
global prefix
prefix = "!"
# set a global var called prefixsetup
global prefixsetup
prefixsetup = False
# set a global var called pogsetup
global pogsetup
pogsetup = False
# set a global var called pogsetupID
global pogsetupid
pogsetupid = "0"

global orginchannel
orginchannel = "0"


# Function to expire setup.
async def revert_setup():
    # Sleep the thread 15 seconds.
    await asyncio.sleep(15)
    global pogsetup
    # Set setup to False.
    pogsetup = False
    # Build and Embed.
    embedexpire = discord.Embed(description='<:Check:845178458426179605> **Setup Session Expired...**',
                                color=0x08d5f7)
    # Edit the Original Message.
    await pogsetupid.edit(embed=embedexpire)


# Get Prefix Function, this gets the prefix for every message sent on the bot client.
async def get_prefix(client, message):
    global prefix
    # Connect to the SQL DB.
    conn = sqlite3.connect('prefs.db')
    # Set type to string.
    conn.text_factory = str
    # Set the cursor for the connection.
    cur = conn.cursor()
    # Execute command on the db that looks for the prefix field where serverID matches the incoming messages server ID.
    cur.execute(f'SELECT Prefix FROM servers WHERE ServerID={message.guild.id}')
    # Fetch the response.
    data = cur.fetchone()
    # Set a var named prefixer to the response from the query.
    prefixer = data
    # if the response is nothing
    if str(prefixer) == "None":
        # Explain what we're doing to the terminal.
        print("Prefix was none, executing SQL")
        # Format new empty values for the row, with the exception of the server ID. This is default setup for a server.
        # It will only run this once, because only once will it not find the prefix, because we set it here.
        prefs_query = f"""INSERT INTO servers
                                 (ServerID, Prefix, MutedRole, ModRoles, EditLogs, DeleteLogs, JoinLogs, LeaveLogs, 
                                 WarnLogs, KickLogs, BanLogs, MuteLogs)
                                  VALUES 
                                 ('{message.guild.id}', '!', 'None', 'None', 0, 0, 0, 0, 0, 0, 0, 0)"""
        # Execute our query
        cur.execute(prefs_query)
        # Commit the changes.
        conn.commit()
        # Set prefixer to the default prefix.
        prefixer = "!"
    # Close the connection.
    conn.close()
    # Set Global Prefix to Prefixer
    prefix = prefixer
    # Return prefixer to our function entry point
    return prefixer


# Function to create one line embeds. So far it takes most of the possible arguments that you can set to an embed. Not
# all args need to be filled out, but a title or description is required. One of them has to be filled
# out to create an embed, or both. To create an embed, just type ' await send_embed(ctx, send_option=option, arg=value)'
# with the arg being one of the args that it takes and the appropriate value. Any image, thumbnail, pfp, etc. takes a
# url in the form of a string. The fields argument takes an array of tuples. So for example:
#                                                           [(name1, value1, inline1), (name2, value2, inline2)]

# send_option = 0 means create then send the embed
# send_option = 1 means create and send the embed, but also return the embed so that it can be stored in a variable and
# the sent embed can be edited later
# send_option = 2 create the embed, but only return the embed, not send it, so the embed object is stored in a variable
# that can be used later.
async def send_embed(ctx, send_option=0, title=None, description=None, author=None, author_pfp=None,
                     color=discord.Colour.default(), footer=None, thumbnail=None, image=None, url=None, fields=None):
    if title is None and description is None:
        print("[Error]: Error creating embed. No title or description specified.")
    else:
        # Initializes new_embed variable
        new_embed = discord.Embed(colour=color)

        # Checks if title, description, and url are 'None'. If None, that element isn't added to the embed
        if title is not None:
            new_embed.title = title
        if description is not None:
            new_embed.description = description
        if url is not None:
            new_embed.url = url

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

        if send_option == 0:
            await ctx.send(embed=new_embed)
        elif send_option == 1:
            return await ctx.send(embed=new_embed)
        elif send_option == 2:
            return new_embed


# Define bot and it's commands prefix, calling the get_prefix function, where it returns the server specific prefix.
bot = commands.Bot(command_prefix=get_prefix)


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


@bot.command()
# Look for a command called setup
async def setup(ctx):
    global pogsetupid
    global pogsetup
    global orginchannel
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
                                             ('Switcher', "Turn on/off commands.", True)
                                             ])
        # Setting our global pogsetup var to true.
        pogsetup = True
        orginchannel = ctx.message.channel
        # Editing our original message into our new embed.
        await pogsetupid.edit(embed=embededit)
        # Delete the orignal message.
        await ctx.message.delete()
        # Run our task to expire setup.
        asyncio.run(await revert_setup())

    else:
        # Sending a message saying the user has to be admin to run the command, keeping the message ID as a var.
        denymessage = await send_embed(ctx, description=f'<:Check:845178458426179605> **You must have ADMINISTRATOR '
                                                        f'to run setup.**',
                                       color=0x08d5f7)


@bot.event
# Check to see if bot is ready.
async def on_ready():
    # Print status to terminal
    print('Status: Ready.')
    await bot.change_presence(
        activity=discord.Game(name='Message me "join."'))


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
    global prefixsetup
    global prefix
    global pogsetup

    # Check if the message author is a bot.
    if msg.author.bot:
        # if it is a bot then return the code from here without going further.
        return

    # Check if the message channel contains the word direct message
    if "Direct Message" in str(msg.channel):
        # If any of the IDs match Mag, Cheetah, or Jonny then
        if "join" in msg.content:
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
    # If we're in prefix setup then
    if msg.channel == orginchannel:
        if msg.author.guild_permissions.administrator:
            if prefixsetup is True:
                # Set the prefix var to the message.
                prefix = msg.content
                # connect to db.
                conn = sqlite3.connect('prefs.db')
                # Str for connection type.
                conn.text_factory = str
                # Define cursor.
                cur = conn.cursor()
                # Update the servers table, set prefix to new prefix where the server ID matches this one.
                cur.execute(f"UPDATE servers SET Prefix = '{prefix}' WHERE ServerID = '{msg.guild.id}'")
                # Commit the changes.
                conn.commit()
                # Close the database.
                conn.close()
                # Setup the embed.
                embededit = discord.Embed(description=f'<:Check:845178458426179605> **Bot prefix changed to {prefix}**',
                                          color=0x08d5f7)
                # Edit the original message
                await pogsetupid.edit(embed=embededit)
                # Turn off Prefix setup.
                prefixsetup = False
                # Delete the message sent by user.
                await msg.delete()
    # If the bot is in setup mode then
    if msg.channel == orginchannel:
        if pogsetup is True:
            # Make sure the user is admin.
            if msg.author.guild_permissions.administrator:
                # Look for the word set in the message that has been converted into lower case.
                if "set" in str(msg.content.lower()):
                    # If it's found then form our embed.
                    embededit = await send_embed(msg.channel, send_option=2, title=f"**Basic Settings**",
                                                 thumbnail='https://i.imgur.com/rYKYpDw.png', color=0x08d5f7,
                                                 description="Respond with any menu option to proceed.",
                                                 fields=[('Prefix', "Set the bots prefix.", True),
                                                         ('Welcomes', "Setup a channel for welcome messages.", True)])
                    # Edit the original message.
                    await pogsetupid.edit(embed=embededit)
                    # Delete the message.
                    await msg.delete()
                # Look for pre in lowercase message
                if "pre" in str(msg.content.lower()):
                    # If it's found then form the embed.
                    embededit = await send_embed(msg.channel, send_option=2, title=f"**Prefix Setting**",
                                                 description="Respond with a new prefix for the bot.", color=0x08d5f7,
                                                 thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                 fields=[('Current Prefix', f"{prefix[0]}", True)])
                    # Edit the message.

                    await pogsetupid.edit(embed=embededit)
                    # Delete the user message.
                    await msg.delete()
                    # Set setup to false.
                    pogsetup = False
                    # Set prefix setup to true.
                    prefixsetup = True

    # Ensure that we process our commands, as on_message overrides and stops command execution.
    await bot.process_commands(msg)


# Run the bot using its token if running from main.
if __name__ == "__main__":
    # Try to login with the bot token
    try:
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
