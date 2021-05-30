import sqlite3
import discord
import base64
import os
import asyncio
from discord.ext import commands


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
    prefix = prefixer[0]
    prefixer = prefixer[0]
    prefixed = commands.when_mentioned(client, message)
    prefixed.append(prefixer)
    return prefixed


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
