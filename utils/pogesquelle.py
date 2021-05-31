import sqlite3
import base64
from discord.ext import commands


# Get Prefix Function
async def get_prefix(client, message):
    try:
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
    except:
        prefixed = "!"
        return


def get_or_request_token():
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
    return BotToken


def reset_token():
    # Pull up the database again
    conn = sqlite3.connect('prefs.db')
    # Create our SQL cursor.
    cur = conn.cursor()
    # Reset our Token to "None"
    cur.execute(f"UPDATE configs SET BotToken = 'None' WHERE ID = '1'")
    # Commit Database
    conn.commit()
    # Close Database
    conn.close()
