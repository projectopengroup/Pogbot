import sqlite3
import base64
from discord.ext import commands


def encodebase64(string):
    toBytes = string.encode("ascii")
    base64_bytes = base64.b64encode(toBytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def decodebase64(base64str):
    base64_bytes = base64str.encode("ascii")
    fromBytes = base64.b64decode(base64_bytes)
    string = fromBytes.decode("ascii")
    return string


# Get Prefix Function
async def get_prefix(client, message):
    try:
        # Connect to the SQL DB.
        conn = sqlite3.connect('prefs.db')
        # Set type to string.
        conn.text_factory = str
        # Set the cursor for the connection.
        cur = conn.cursor()
        # Execute command on the db that looks for the prefix field where serverID match the incoming msg server ID.
        cur.execute(f'SELECT Prefix FROM servers WHERE ServerID={message.guild.id}')
        # Fetch the response.
        data = cur.fetchone()
        # Set a var named prefixer to the response from the query.
        prefixer = data
        # if the response is nothing
        if str(prefixer) == "None":
            # Explain what we're doing to the terminal.
            print("Prefix was none, executing SQL")
            # Format new empty values for the row, with the exception of the server ID. This is default for a server.
            # It will only run this once, because only once will it not find the prefix, because we set it here.
            prefs_query = f"""INSERT INTO servers
                                     (ServerID, Prefix, MutedRole, ModRoles, 
                                     Welcome, WelcomeDM, WelcomeRole, WelcomeCard, WelcomeChannel)
                                      VALUES 
                                     ('{message.guild.id}', '!', 'None', 'None', 'None', 
                                     'None', 'None', 0, 0) """
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
        return prefixed


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


def set_welcome_message(message, serverid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    message = encodebase64(message)
    cur.execute(f"UPDATE servers SET Welcome = '{message}' WHERE ServerID = '{serverid}'")
    # Commit the database changes.
    conn.commit()
    conn.close()


def reset_welcome_message(serverid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE servers SET Welcome = 'None' WHERE ServerID = '{serverid}'")
    # Commit the database changes.
    conn.commit()
    conn.close()


def get_welcome_message(serverid):
    # 0 is false 1 is true
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT Welcome FROM servers WHERE ServerID={serverid}')
    data = cur.fetchone()
    data = data[0]
    if data != "None":
        data = decodebase64(data)
    # Commit the database changes.
    conn.commit()
    conn.close()
    return data


def set_welcome_dm_message(message, serverid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    message = encodebase64(message)
    cur.execute(f"UPDATE servers SET WelcomeDM = '{message}' WHERE ServerID = '{serverid}'")
    # Commit the database changes.
    conn.commit()
    conn.close()


def get_welcome_dm_message(serverid):
    # 0 is false 1 is true
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT WelcomeDM FROM servers WHERE ServerID={serverid}')
    data = cur.fetchone()
    data = data[0]
    if data != "None":
        data = decodebase64(data)
    # Commit the database changes.
    conn.commit()
    conn.close()
    return data


def set_welcome_role(role, serverid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE servers SET WelcomeRole = '{role}' WHERE ServerID = '{serverid}'")
    # Commit the database changes.
    conn.commit()
    conn.close()


def get_welcome_role(serverid):
    # 0 is false 1 is true
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT WelcomeRole FROM servers WHERE ServerID={serverid}')
    data = cur.fetchone()
    data = data[0]
    # Commit the database changes.
    conn.commit()
    conn.close()
    return data


def set_welcome_card(integer, serverid):
    # 0 is false 1 is true
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE servers SET WelcomeCard = '{integer}' WHERE ServerID = '{serverid}'")
    # Commit the database changes.
    conn.commit()
    conn.close()


def get_welcome_card(serverid):
    # 0 is false 1 is true
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT WelcomeCard FROM servers WHERE ServerID={serverid}')
    data = cur.fetchone()
    data = data[0]
    # Commit the database changes.
    conn.commit()
    conn.close()
    return data


def set_welcome_channel(channelid, serverid):
    # 0 is false 1 is true
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE servers SET WelcomeChannel = '{channelid}' WHERE ServerID = '{serverid}'")
    # Commit the database changes.
    conn.commit()
    conn.close()


def get_welcome_channel(serverid):
    # 0 is false 1 is true
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT WelcomeChannel FROM servers WHERE ServerID={serverid}')
    data = cur.fetchone()
    data = data[0]
    # Commit the database changes.
    conn.commit()
    conn.close()
    return data


def check_log_item(serverid):
    conn = sqlite3.connect('prefs.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute(f'SELECT ServerID FROM logs WHERE ServerID={serverid}')
    data = cur.fetchone()
    Serverd = data
    if str(Serverd) == "None":
        prefs_query = f"""INSERT INTO logs
                                 (ServerID, 'Join', Leave, Ban, Unban, Edit, 'Delete', BulkDelete, ChanMade, ChanDelete, 
                                 RoleMade, RoleDelete, RoleUpdated, RoleGiven, RoleRemoved, NickChanged, ModCmdUsed, 
                                 JoinVC, LeaveVC, MovedVC, Invites, Mute, Kick, Warn)
                                  VALUES 
                                 ('{serverid}', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) """
        cur.execute(prefs_query)
        conn.commit()
    conn.close()


def get_log_item(serverid, logitem):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    # Join Leave Ban Unban Edit Delete BulkDelete ChanMade ChanDelete RoleMade RoleDelete RoleUpdated RoleGiven
    # RoleRemoved NickChanged JoinVC LeaveVC MovedVC Invites Mute Kick Warn
    cur.execute(f"SELECT `{logitem}` FROM logs WHERE ServerID={serverid}")
    data = cur.fetchone()
    if data:
        data = data[0]
    else:
        data = 0
    conn.commit()
    conn.close()
    return data


def set_log_item(serverid, channelid, logitem):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    # Join Leave Ban Unban Edit Delete BulkDelete ChanMade ChanDelete RoleMade RoleDelete RoleUpdated RoleGiven
    # RoleRemoved NickChanged JoinVC LeaveVC MovedVC Invites Mute Kick Warn
    cur.execute(f"UPDATE logs SET '{logitem}' = '{channelid}' WHERE ServerID = '{serverid}'")
    conn.commit()
    conn.close()


def set_all_log_items(serverid, channelid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    # Join Leave Ban Unban Edit Delete BulkDelete ChanMade ChanDelete RoleMade RoleDelete RoleUpdated RoleGiven
    # RoleRemoved NickChanged JoinVC LeaveVC MovedVC Invites Mute Kick Warn
    cur.execute(f"UPDATE logs SET 'Join' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Leave' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Ban' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Unban' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Edit' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Delete' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'BulkDelete' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'ChanMade' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'ChanDelete' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'RoleMade' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'RoleDelete' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'RoleUpdated' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'RoleGiven' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'RoleRemoved' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'NickChanged' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'JoinVC' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'LeaveVC' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'MovedVC' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Invites' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Mute' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Kick' = '{channelid}' WHERE ServerID = '{serverid}'")
    cur.execute(f"UPDATE logs SET 'Warn' = '{channelid}' WHERE ServerID = '{serverid}'")

    conn.commit()
    conn.close()


def check_snipes(serverid):
    conn = sqlite3.connect('prefs.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute(f'SELECT ServerID FROM snipes WHERE ServerID={serverid}')
    data = cur.fetchone()
    Serverd = data
    if str(Serverd) == "None":
        prefs_query = f"""INSERT INTO snipes
                                 (ServerID, 'Message', 'MessageID', 'Author', 'AuthorAvatar', 'Timestamp')
                                  VALUES 
                                 ('{serverid}', 0, 0, 0, 0, 0) """
        cur.execute(prefs_query)
        conn.commit()
    conn.close()


def check_rolereactions(messageid):
    conn = sqlite3.connect('prefs.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute(f'SELECT MessageID FROM rolereactions WHERE MessageID={messageid}')
    data = cur.fetchone()
    Serverd = data
    if str(Serverd) == "None":
        prefs_query = f"""INSERT INTO rolereactions
                                 (MessageID, 'RoleList', 'EmojiList')
                                  VALUES 
                                 ('{messageid}', 'None', 'None') """
        cur.execute(prefs_query)
        conn.commit()
    conn.close()


def get_rolelist(messageid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"SELECT `RoleList` FROM rolereactions WHERE MessageID={messageid}")
    data = cur.fetchone()
    if data:
        data = data[0]
    else:
        data = 0
    conn.commit()
    conn.close()
    return data


def set_rolelist(messageid, rolelist):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE rolereactions SET 'RoleList' = '{rolelist}' WHERE MessageID = '{messageid}'")
    conn.commit()
    conn.close()


def get_emojilist(messageid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"SELECT `EmojiList` FROM rolereactions WHERE MessageID={messageid}")
    data = cur.fetchone()
    if data:
        data = data[0]
    else:
        data = 0
    conn.commit()
    conn.close()
    return data


def set_emojilist(messageid, emojilist):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE rolereactions SET 'EmojiList' = '{emojilist}' WHERE MessageID = '{messageid}'")
    conn.commit()
    conn.close()

def check_user(serverid, userid):
    conn = sqlite3.connect('prefs.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute(f'SELECT UserID FROM users WHERE ServerID={serverid} and UserID={userid}')
    data = cur.fetchone()
    Usered = data
    if str(Usered) == "None":
        prefs_query = f"""INSERT INTO users
                                     (ServerID, UserID, XP, Level, Warnings, XPLockedUntil, 
                                     MutedUntil)
                                      VALUES 
                                     ('{serverid}', '{userid}', 0, 0, 0, '0', '0') """
        cur.execute(prefs_query)
        conn.commit()
        conn.close()

def get_db_user_item(serverid, userid, itemname):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"SELECT `{itemname}` FROM users WHERE ServerID={serverid} and UserID={userid}")
    data = cur.fetchone()
    if data:
        data = data[0]
    else:
        data = 0
    conn.commit()
    conn.close()
    return data

def set_db_user_item(serverid, userid, itemname, string):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET '{itemname}'='{string}' WHERE ServerID='{serverid}' and UserID='{userid}'")
    conn.commit()
    conn.close()

def get_db_item(serverid, tablename, itemname):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"SELECT `{itemname}` FROM {tablename} WHERE ServerID={serverid}")
    data = cur.fetchone()
    if data:
        data = data[0]
    else:
        data = 0
    conn.commit()
    conn.close()
    return data


def set_db_item(serverid, tablename, string, itemname):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE {tablename} SET '{itemname}' = '{string}' WHERE ServerID = '{serverid}'")
    conn.commit()
    conn.close()


# Global user settings start here, please keep the other settings out of this half of the file ###########
# GLOBAL USER SETTINGS ###################################################################################
def check_global_user(userid):
    conn = sqlite3.connect('prefs.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute(f'SELECT UserID FROM globalusers WHERE UserID={userid}')
    data = cur.fetchone()
    Usered = data
    if str(Usered) == "None":
        prefs_query = f"""INSERT INTO globalusers
                                 (UserID, WelcomeImage, UserDarkColor, UserLightColor, ProfileImage, NicknameHistory, 
                                 Currency, Blacklisted)
                                  VALUES 
                                 ('{userid}', 'None', 'None', 'None', 'None', 'None', 0, 0) """
        cur.execute(prefs_query)
        conn.commit()
        conn.close()


def set_global_bgcolor(userid, htmlcolor):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE globalusers SET UserLightColor = '{htmlcolor}' WHERE UserID = '{userid}'")
    conn.commit()
    conn.close()


def get_global_bgcolor(userid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT UserlightColor FROM globalusers WHERE UserID={userid}')
    data = cur.fetchone()
    data = data[0]
    conn.commit()
    conn.close()
    return data


def set_global_bannercolor(userid, htmlcolor):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE globalusers SET UserDarkColor = '{htmlcolor}' WHERE UserID = '{userid}'")
    conn.commit()
    conn.close()


def get_global_bannercolor(userid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT UserDarkColor FROM globalusers WHERE UserID={userid}')
    data = cur.fetchone()
    data = data[0]
    conn.commit()
    conn.close()
    return data


def set_global_welcomeimg(userid, imageurl):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE globalusers SET WelcomeImage = '{imageurl}' WHERE UserID = '{userid}'")
    conn.commit()
    conn.close()


def get_global_welcomeimg(userid):
    conn = sqlite3.connect('prefs.db')
    cur = conn.cursor()
    cur.execute(f'SELECT WelcomeImage FROM globalusers WHERE UserID={userid}')
    data = cur.fetchone()
    data = data[0]
    conn.commit()
    conn.close()
    return data
# Global user settings end here, please keep the other settings out of this half of the file ###########
# GLOBAL USER SETTINGS ###################################################################################
